from datetime import date, timedelta

import httpx

from politik.coletores import registrar
from politik.modelos import Autor, Item

BASE = "https://dadosabertos.camara.leg.br/api/v2"
SIGLAS_COM_AUTORES = {"PL", "PLP", "PEC", "MPV", "PDL"}


def parse_proposicoes(json: dict) -> list[Item]:
    return [
        Item(
            id=f"camara:{p['id']}",
            fonte="camara",
            nivel="federal",
            categoria="proposicao",
            sigla_tipo=p["siglaTipo"],
            titulo=f"{p['siglaTipo']} {p['numero']}/{p['ano']}",
            ementa=p.get("ementa") or "",
            data=p["dataApresentacao"][:10],
            url=f"https://www.camara.leg.br/propostas-legislativas/{p['id']}",
        )
        for p in json["dados"]
    ]


def parse_votacoes(json: dict, data: str) -> list[Item]:
    return [
        Item(
            id=f"camara:votacao:{v['id']}",
            fonte="camara",
            nivel="federal",
            categoria="votacao",
            sigla_tipo="VOTACAO",
            titulo=v.get("descricao") or "Votação em plenário",
            ementa=v.get("descricao") or "",
            data=v["data"],
            url=v["uri"],
            extra={"siglaOrgao": v["siglaOrgao"], "aprovacao": v.get("aprovacao"),
                   "uriProposicaoObjeto": v.get("uriProposicaoObjeto")},
        )
        for v in json["dados"]
        if v["siglaOrgao"] == "PLEN" and v["data"] == data
    ]


def parse_deputado(json: dict) -> Autor:
    s = json["dados"]["ultimoStatus"]
    return Autor(s["nome"], s.get("siglaPartido"), s.get("siglaUf"))


def _paginar(cliente: httpx.Client, url: str) -> list[dict]:
    dados = []
    while url:
        r = cliente.get(url)
        r.raise_for_status()
        j = r.json()
        dados += j["dados"]
        url = next((l["href"] for l in j.get("links", []) if l["rel"] == "next"), None)
    return dados


def _autores(cliente: httpx.Client, pid: str, cache: dict) -> list[Autor]:
    r = cliente.get(f"{BASE}/proposicoes/{pid}/autores")
    r.raise_for_status()
    autores = []
    for a in r.json()["dados"]:
        if a.get("tipo") == "Deputado(a)" and a.get("uri"):
            if a["uri"] not in cache:
                d = cliente.get(a["uri"])
                d.raise_for_status()
                cache[a["uri"]] = parse_deputado(d.json())
            autores.append(cache[a["uri"]])
        else:
            autores.append(Autor(a["nome"]))
    return autores


@registrar("camara")
def coletar(data: str, cliente: httpx.Client | None = None) -> list[Item]:
    cliente = cliente or httpx.Client(timeout=30, headers={"Accept": "application/json"})
    seguinte = (date.fromisoformat(data) + timedelta(days=1)).isoformat()
    props = _paginar(cliente, f"{BASE}/proposicoes?dataApresentacaoInicio={data}"
                              f"&dataApresentacaoFim={data}&itens=100")
    itens = parse_proposicoes({"dados": props})
    cache: dict = {}
    for it in itens:
        if it.sigla_tipo in SIGLAS_COM_AUTORES:
            it.autores = _autores(cliente, it.id.split(":")[1], cache)
    # a API trata dataFim como exclusiva para votações
    votos = _paginar(cliente, f"{BASE}/votacoes?dataInicio={data}&dataFim={seguinte}&itens=200")
    return itens + parse_votacoes({"dados": votos}, data)
