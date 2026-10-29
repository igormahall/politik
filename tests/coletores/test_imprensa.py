from politik.coletores.imprensa import carregar_feeds, parse_feed
from tests.conftest import load_bytes

DIA = "2026-10-28"


def test_parse_feed_filtra_por_dia():
    itens = parse_feed("agenciabrasil", "politica", load_bytes("feed.xml"), DIA)
    assert len(itens) == 4
    assert all(i.data == DIA and i.categoria == "noticia" for i in itens)
    assert all("<" not in i.ementa and len(i.ementa) <= 500 for i in itens)
    assert itens[0].fonte == "imprensa:agenciabrasil" and itens[0].nivel == "federal"


def test_secao_amazonas_e_estadual():
    itens = parse_feed("acritica", "amazonas", load_bytes("feed.xml"), DIA)
    assert all(i.nivel == "estadual" for i in itens)


def test_id_estavel():
    a = parse_feed("x", "politica", load_bytes("feed.xml"), DIA)
    b = parse_feed("x", "politica", load_bytes("feed.xml"), DIA)
    assert [i.id for i in a] == [i.id for i in b] and len({i.id for i in a}) == len(a)


def test_config_tem_linhas_diferentes_e_amazonas():
    feeds = carregar_feeds()
    assert len({f["veiculo"] for f in feeds}) >= 9
    assert sum(f["secao"] == "amazonas" for f in feeds) >= 2
    assert all(f["texto_completo"] is False or f["veiculo"].startswith("agencia") for f in feeds)
