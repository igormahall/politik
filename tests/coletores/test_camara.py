import re

from politik.coletores.camara import parse_deputado, parse_proposicoes, parse_votacoes
from politik.modelos import Autor
from tests.conftest import load


def test_parse_proposicoes_campos():
    itens = parse_proposicoes(load("camara_proposicoes.json"))
    pl = next(i for i in itens if i.sigla_tipo == "PL")
    assert pl.id.startswith("camara:") and pl.nivel == "federal"
    assert re.fullmatch(r"PL \d+/2026", pl.titulo)
    assert pl.data == "2026-10-28"
    assert pl.url == f"https://www.camara.leg.br/propostas-legislativas/{pl.id.split(':')[1]}"


def test_parse_votacoes_so_plenario_do_dia():
    itens = parse_votacoes(load("camara_votacoes.json"), "2026-10-27")
    assert itens
    assert all(i.categoria == "votacao" and i.extra["siglaOrgao"] == "PLEN" for i in itens)
    assert all(i.data == "2026-10-27" for i in itens)


def test_parse_deputado():
    assert parse_deputado(load("camara_deputado.json")) == Autor("Rubens Pereira Júnior", "PT", "MA")
