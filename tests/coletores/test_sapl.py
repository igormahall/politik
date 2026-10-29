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
