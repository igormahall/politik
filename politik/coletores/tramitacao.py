from datetime import date, timedelta

import httpx

from politik.armazenamento import data_dir, ler_json
from politik.coletores import registrar
from politik.modelos import Item

CAMARA = "https://dadosabertos.camara.leg.br/api/v2"
SENADO = "https://legis.senado.leg.br/dadosabertos/processo"


def acompanhados(hoje: str, janela_dias: int = 180) -> list[str]:
    limite = (date.fromisoformat(hoje) - timedelta(days=janela_dias)).isoformat()
    ids = []
    for f in sorted((data_dir() / "fichas").glob("*.json")):
        ficha = ler_json(f, {})
        if not isinstance(ficha, dict):
            continue
        iid = ficha.get("item_id", "")
        # só o projeto original: fichas de votação/tramitação não são acompanhadas
        if (iid.startswith(("camara:", "senado:")) and iid.count(":") == 1
                and ficha.get("data", "") >= limite and iid not in ids):
            ids.append(iid)
    return ids


def parse_tramitacoes_camara(item_id: str, json: dict, data: str) -> list[Item]:
    return [
        Item(
            id=f"{item_id}:tram:{t['sequencia']}",
            fonte="camara",
            nivel="federal",
            categoria="tramitacao",
            sigla_tipo="TRAMITACAO",
            titulo=t.get("descricaoSituacao") or t.get("descricaoTramitacao") or "Tramitação",
            ementa=t.get("despacho") or "",
            data=data,
            url=f"https://www.camara.leg.br/propostas-legislativas/{item_id.split(':')[1]}",
            url_documento=t.get("url"),
            extra={"item_origem": item_id},
        )
        for t in json["dados"]
        if t["dataHora"][:10] == data
    ]


def parse_situacao_senado(item_id: str, processo: dict, data: str) -> Item | None:
    if processo.get("dataSituacaoAtual") != data:
        return None
    return Item(
        id=f"{item_id}:sit:{data}",
        fonte="senado",
        nivel="federal",
        categoria="tramitacao",
        sigla_tipo="TRAMITACAO",
        titulo=processo.get("situacaoAtual") or "Mudança de situação",
        ementa=processo.get("ementa") or (processo.get("conteudo") or {}).get("ementa") or "",
        data=data,
        url=f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{processo['codigoMateria']}",
        extra={"item_origem": item_id},
    )


@registrar("tramitacao")
def coletar(data: str) -> list[Item]:
    itens = []
    with httpx.Client(timeout=30, headers={"Accept": "application/json"}) as c:
        for iid in acompanhados(data):
            casa, cod = iid.split(":")[:2]
            if casa == "camara":
                r = c.get(f"{CAMARA}/proposicoes/{cod}/tramitacoes", params={"dataInicio": data, "dataFim": data})
                r.raise_for_status()
                itens += parse_tramitacoes_camara(iid, r.json(), data)
            else:
                r = c.get(f"{SENADO}/{cod}")
                r.raise_for_status()
                if it := parse_situacao_senado(iid, r.json(), data):
                    itens.append(it)
    return itens
