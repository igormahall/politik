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


def test_um_processo_com_erro_nao_derruba_as_tramitacoes(tmp_data, monkeypatch):
    # 10/11: um 502 em um único processo do Senado apagou todas as tramitações do dia
    import httpx

    from politik.coletores import tramitacao

    _ficha(tmp_data, "senado:1", "2026-10-28")
    _ficha(tmp_data, "senado:2", "2026-10-28")
    proc = load("senado_processo.json")[0]

    def responder(req):
        if req.url.path.endswith("/1"):
            return httpx.Response(502)
        return httpx.Response(200, json=proc)

    transporte = httpx.MockTransport(responder)
    real = httpx.Client
    monkeypatch.setattr(tramitacao.httpx, "Client", lambda **kw: real(transport=transporte, **kw))
    itens = tramitacao.coletar("2026-10-28")
    assert [it.id for it in itens] == ["senado:2:sit:2026-10-28"]


def test_tramitacao_falha_se_todos_os_processos_falham(tmp_data, monkeypatch):
    import httpx
    import pytest

    from politik.coletores import tramitacao

    _ficha(tmp_data, "senado:1", "2026-10-28")
    transporte = httpx.MockTransport(lambda req: httpx.Response(502))
    real = httpx.Client
    monkeypatch.setattr(tramitacao.httpx, "Client", lambda **kw: real(transport=transporte, **kw))
    with pytest.raises(httpx.HTTPStatusError):
        tramitacao.coletar("2026-10-28")
