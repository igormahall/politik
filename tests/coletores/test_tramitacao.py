from politik.armazenamento import escrever_json
from politik.coletores.tramitacao import acompanhados, parse_situacao_senado, parse_tramitacoes_camara
from tests.conftest import load


def _ficha(tmp_data, item_id, data):
    escrever_json(tmp_data / "fichas" / f"{item_id.replace(':', '_')}.json", {"item_id": item_id, "data": data})


def test_tramitacao_so_do_dia():
    itens = parse_tramitacoes_camara("camara:2649124", load("camara_tramitacoes.json"), "2026-10-28")
    assert len(itens) == 1
    it = itens[0]
    assert it.id == "camara:2649124:tram:1" and it.categoria == "tramitacao"
    assert it.extra["item_origem"] == "camara:2649124" and it.titulo == "Apresentação de Proposição"
    assert parse_tramitacoes_camara("camara:2649124", load("camara_tramitacoes.json"), "2026-10-27") == []


def test_situacao_senado_do_dia():
    proc = load("senado_processo.json")[0]
    it = parse_situacao_senado(f"senado:{proc['id']}", proc, "2026-10-28")
    assert it.id == f"senado:{proc['id']}:sit:2026-10-28" and it.titulo == proc["situacaoAtual"]
    assert parse_situacao_senado("senado:1", proc, "2026-10-29") is None


def test_acompanhados_janela(tmp_data):
    _ficha(tmp_data, "camara:1", "2026-01-01")
    _ficha(tmp_data, "camara:2", "2026-10-01")
    _ficha(tmp_data, "aleam:materia:3", "2026-10-01")
    assert acompanhados("2026-10-28") == ["camara:2"]
