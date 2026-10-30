import httpx

from politik.coletores import registrar
from politik.modelos import Autor, Item

CASAS = {
    "aleam": ("https://sapl.al.am.leg.br", "estadual"),
    "cmm": ("https://sapl.cmm.am.gov.br", "municipal"),
}
SIGLAS_COM_AUTORES = {"PL", "PLC", "PEC", "PDL", "PLO", "PLE"}


def parse_tipos(json: dict) -> dict[int, str]:
    return {t["id"]: t["sigla"] for t in json["results"]}


def parse_materias(casa: str, json: dict, tipos: dict[int, str]) -> list[Item]:
    base, nivel = CASAS[casa]
    return [
        Item(
            id=f"{casa}:materia:{m['id']}",
            fonte=casa,
            nivel=nivel,
            categoria="proposicao",
            sigla_tipo=tipos.get(m["tipo"], str(m["tipo"])),
            titulo=m["__str__"],
            ementa=(m.get("ementa") or "").strip(),
            data=m["data_apresentacao"],
            url=f"{base}/materia/{m['id']}",
            url_documento=m.get("texto_original"),
        )
        for m in json["results"]
    ]


def parse_normas(casa: str, json: dict) -> list[Item]:
    base, nivel = CASAS[casa]
    return [
        Item(
            id=f"{casa}:norma:{n['id']}",
            fonte=casa,
            nivel=nivel,
            categoria="norma",
            sigla_tipo="NORMA",
            titulo=n["__str__"],
            ementa=(n.get("ementa") or "").strip(),
            data=n["data"],
            url=f"{base}/norma/{n['id']}",
            url_documento=n.get("texto_integral"),
        )
        for n in json["results"]
    ]


def parse_filiacao(json: dict) -> str | None:
    atuais = [f for f in json["results"] if not f.get("data_desfiliacao")]
    if not atuais:
        return None
    partes = atuais[0]["__str__"].split(" - ")
    return partes[1] if len(partes) > 1 else None


def _resultados(cliente: httpx.Client, url: str) -> list[dict]:
    out = []
    while url:
        r = cliente.get(url)
        r.raise_for_status()
        j = r.json()
        out += j["results"]
        url = j["pagination"]["links"].get("next")
        if url:
            url = url.replace("http://", "https://", 1)
    return out


def _autores(cliente: httpx.Client, base: str, materia_id: str, cache: dict) -> list[Autor]:
    autores = []
    for a in _resultados(cliente, f"{base}/api/materia/autoria/?materia={materia_id}"):
        aid = a["autor"]
        if aid not in cache:
            r = cliente.get(f"{base}/api/base/autor/{aid}/")
            r.raise_for_status()
            autor = r.json()
            fil = cliente.get(f"{base}/api/parlamentares/filiacao/?parlamentar={autor['object_id']}")
            partido = parse_filiacao(fil.json()) if fil.status_code == 200 else None
            cache[aid] = Autor(autor["nome"], partido, "AM" if partido else None)
        autores.append(cache[aid])
    return autores


def coletar_casa(casa: str, data: str, cliente: httpx.Client | None = None) -> list[Item]:
    cliente = cliente or httpx.Client(timeout=30, headers={"Accept": "application/json"})
    base, _ = CASAS[casa]
    tipos = parse_tipos({"results": _resultados(cliente, f"{base}/api/materia/tipomaterialegislativa/?page_size=100")})
    materias = parse_materias(
        casa,
        {
            "results": _resultados(
                cliente, f"{base}/api/materia/materialegislativa/?data_apresentacao={data}&page_size=100"
            )
        },
        tipos,
    )
    cache: dict = {}
    for m in materias:
        if m.sigla_tipo in SIGLAS_COM_AUTORES:
            m.autores = _autores(cliente, base, m.id.split(":")[-1], cache)
    normas = parse_normas(
        casa, {"results": _resultados(cliente, f"{base}/api/norma/normajuridica/?data={data}&page_size=100")}
    )
    return materias + normas


registrar("aleam")(lambda data: coletar_casa("aleam", data))
registrar("cmm")(lambda data: coletar_casa("cmm", data))
