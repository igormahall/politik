import re

import httpx

from politik.coletores import registrar
from politik.modelos import Autor, Item

BASE = "https://legis.senado.leg.br/dadosabertos/processo"
_AUTOR = re.compile(r"^(?:Senador[a]?\s+)?(.+?)\s*\(([^/]+)/(\w{2})\)$")


def parse_autoria(autoria: str) -> list[Autor]:
    autores = []
    for parte in re.split(r"(?<=\)),\s*", autoria or ""):
        m = _AUTOR.match(parte.strip())
        autores.append(Autor(*m.groups()) if m else Autor(parte.strip()))
    return [a for a in autores if a.nome]


def parse_processos(lista: list[dict]) -> list[Item]:
    return [
        Item(
            id=f"senado:{p['id']}",
            fonte="senado",
            nivel="federal",
            categoria="proposicao",
            sigla_tipo=p["identificacao"].split()[0],
            titulo=p["identificacao"],
            ementa=p.get("ementa") or "",
            data=p["dataApresentacao"][:10],
            url=f"https://www25.senado.leg.br/web/atividade/materias/-/materia/{p['codigoMateria']}",
            url_documento=p.get("urlDocumento"),
            autores=parse_autoria(p.get("autoria", "")),
            extra={"tipoDocumento": p.get("tipoDocumento"), "situacaoAtual": p.get("situacaoAtual"),
                   "codigoMateria": p.get("codigoMateria")},
        )
        for p in lista
    ]


@registrar("senado")
def coletar(data: str, cliente: httpx.Client | None = None) -> list[Item]:
    cliente = cliente or httpx.Client(timeout=30, headers={"Accept": "application/json"})
    r = cliente.get(BASE, params={"dataInicioApresentacao": data, "dataFimApresentacao": data})
    r.raise_for_status()
    return parse_processos(r.json())
