from politik.coletores.sapl import parse_filiacao, parse_materias, parse_normas, parse_tipos
from tests.conftest import load


def test_parse_tipos():
    tipos = parse_tipos(load("sapl_tipos.json"))
    assert tipos[1] == "PL" and tipos[3] == "REQ"


def test_parse_materias_nivel_e_sigla():
    tipos = parse_tipos(load("sapl_tipos.json"))
    itens = parse_materias("aleam", load("sapl_materias.json"), tipos)
    assert itens and all(i.nivel == "estadual" for i in itens)
    assert {i.sigla_tipo for i in itens} <= set(tipos.values())
    assert itens[0].id.startswith("aleam:materia:")
    assert itens[0].url == f"https://sapl.al.am.leg.br/materia/{itens[0].id.split(':')[-1]}"


def test_parse_normas_categoria():
    itens = parse_normas("cmm", load("sapl_normas.json"))
    assert itens[0].categoria == "norma" and itens[0].nivel == "municipal"
    assert itens[0].url_documento.endswith(".pdf")
    assert itens[0].data == "2026-09-28"


def test_parse_filiacao_atual():
    assert parse_filiacao(load("sapl_filiacao.json")) == "PV"


def test_parse_filiacao_vazia():
    assert parse_filiacao({"results": []}) is None


def test_janela_pega_materia_cadastrada_atrasada_sem_repetir_a_ja_vista(tmp_data):
    # 03–26/11: 14 matérias de cada casa foram cadastradas dias depois, com a data original, e nunca entraram
    import httpx

    from politik.armazenamento import escrever_json
    from politik.coletores.sapl import coletar_casa

    escrever_json(
        tmp_data / "selecionados" / "2026-11-25.json", {"destaques": [], "menores": [{"id": "aleam:materia:1"}]}
    )
    pedidos = []

    def materia(mid, dia):
        return {"id": mid, "tipo": 1, "__str__": f"PL {mid}/2026", "ementa": "Ementa", "data_apresentacao": dia}

    def responder(req):
        pedidos.append(req.url)
        vazio = {"next": None}
        if "tipomaterialegislativa" in req.url.path:
            return httpx.Response(200, json={"results": [{"id": 1, "sigla": "MSGOV"}], "pagination": {"links": vazio}})
        if "materialegislativa" in req.url.path:
            res = [materia(1, "2026-11-20"), materia(2, "2026-11-21"), materia(3, "2026-11-26")]
            return httpx.Response(200, json={"results": res, "pagination": {"links": vazio}})
        return httpx.Response(200, json={"results": [], "pagination": {"links": vazio}})

    itens = coletar_casa("aleam", "2026-11-26", httpx.Client(transport=httpx.MockTransport(responder)))
    assert [i.id for i in itens] == ["aleam:materia:2", "aleam:materia:3"]
    consulta = next(u for u in pedidos if "materialegislativa" in u.path and "tipo" not in u.path)
    assert consulta.params["data_apresentacao__gte"] == "2026-11-19"
    assert consulta.params["data_apresentacao__lte"] == "2026-11-26"
