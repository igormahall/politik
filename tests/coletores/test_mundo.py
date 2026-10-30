from pathlib import Path

import httpx
import pytest

from politik.coletores import FonteIndisponivel
from politik.coletores.imprensa import carregar_feeds
from politik.coletores.mundo import coletar
from tests.conftest import load_bytes

DIA = "2026-10-28"
FEEDS = [
    {"organizacao": "BBC", "veiculo": "bbc-brasil", "url": "https://bbc/1"},
    {"organizacao": "DW", "veiculo": "dw-world", "url": "https://dw/2"},
]


def _cliente(status):
    return httpx.Client(
        transport=httpx.MockTransport(lambda r: httpx.Response(status(r), content=load_bytes("feed.xml")))
    )


def test_coleta_marca_organizacao_e_categoria():
    itens = coletar(DIA, feeds=FEEDS, cliente=_cliente(lambda r: 200))
    assert len(itens) == 8  # o feed de exemplo tem 4 itens do dia
    assert {i.categoria for i in itens} == {"mundo"} and {i.nivel for i in itens} == {"mundo"}
    assert {i.extra["organizacao"] for i in itens} == {"BBC", "DW"}
    assert all(i.id.startswith("mundo:") and i.fonte == "mundo" for i in itens)


def test_um_feed_fora_nao_derruba():
    itens = coletar(DIA, feeds=FEEDS, cliente=_cliente(lambda r: 500 if "dw" in str(r.url) else 200))
    assert len(itens) == 4 and {i.extra["organizacao"] for i in itens} == {"BBC"}


def test_todos_fora_levanta_indisponivel():
    with pytest.raises(FonteIndisponivel):
        coletar(DIA, feeds=FEEDS, cliente=_cliente(lambda r: 500))


def test_config_tem_as_tres_organizacoes():
    feeds = carregar_feeds(Path("config/mundo.toml"))
    assert {f["organizacao"] for f in feeds} == {"BBC", "DW", "Agência Brasil"} and len(feeds) == 5
