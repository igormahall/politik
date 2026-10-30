"""Endurecimento de segurança: tokens fora de mensagens de erro, links seguros, actions fixadas."""

import httpx
import pytest

from politik.armazenamento import escrever_json
from politik.coletores import FonteIndisponivel, imprensa
from politik.site.gerador import gerar, link_seguro
from politik.telegram import enviar
from tests.helpers import D, escrever_ficha, escrever_selecionados, FICHA_OK, item


def test_erro_do_telegram_nao_expoe_o_token():
    cliente = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(400, json={"ok": False})))
    with pytest.raises(RuntimeError) as e:
        enviar([{"text": "oi", "reply_markup": None}], "123:SEGREDO", "42", cliente=cliente, espera=0)
    assert "SEGREDO" not in str(e.value) and "SEGREDO" not in repr(e.value.__cause__)
    assert "400" in str(e.value)


def test_link_seguro():
    assert link_seguro("https://a.b/c") == "https://a.b/c"
    assert link_seguro("http://a.b") == "http://a.b"
    assert link_seguro("javascript:alert(1)") == "#"
    assert link_seguro(" JavaScript:alert(1)") == "#"
    assert link_seguro("data:text/html,x") == "#"
    assert link_seguro(None) == "#"


def test_site_neutraliza_links_perigosos(tmp_data, tmp_path):
    escrever_selecionados(tmp_data, D, menores=[item("x:1", url="javascript:alert(document.cookie)")])
    escrever_ficha(tmp_data, {**FICHA_OK, "fontes": [{"nome": "x", "url": "https://ok"}]})
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": ["camara:1"]})
    gerar(tmp_path, "https://x")
    html = "".join(p.read_text() for p in tmp_path.rglob("*.html"))
    assert "javascript:" not in html


def test_site_usa_nome_amigavel_da_fonte(tmp_data, tmp_path):
    escrever_selecionados(tmp_data, D, indisponiveis=["dou"])
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": []})
    gerar(tmp_path, "https://x")
    assert "Diário Oficial da União indisponível hoje" in (tmp_path / f"dia/{D}.html").read_text()


def test_imprensa_todos_os_feeds_falham_vira_fonte_indisponivel(monkeypatch):
    monkeypatch.setattr(
        imprensa,
        "carregar_feeds",
        lambda: [{"veiculo": "a", "url": "https://a", "secao": "politica", "texto_completo": False}],
    )

    def falha(self, url, **kw):
        raise httpx.ConnectError("fora")

    monkeypatch.setattr(httpx.Client, "get", falha)
    with pytest.raises(FonteIndisponivel):
        imprensa.coletar(D)
