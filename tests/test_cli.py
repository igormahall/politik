from unittest.mock import ANY

from politik import coletores
from politik.__main__ import main
from politik.armazenamento import carregar_itens, ler_json
from politik.modelos import Item

D = "2026-10-28"


def _item(id="camara:1", **kw):
    return Item(**{**dict(id=id, fonte="camara", nivel="federal", categoria="proposicao", sigla_tipo="PL",
                          titulo="t", ementa="", data=D, url="u"), **kw})


def boom(data):
    raise RuntimeError("fora do ar")


def _fake(monkeypatch, cols):
    monkeypatch.setattr(coletores, "carregar_todos", lambda: cols)


def test_coletar_fonte_falha_continua(tmp_data, monkeypatch):
    _fake(monkeypatch, {"ok": lambda d: [_item()], "ruim": boom})
    assert main(["coletar", "--data", D]) == 0
    assert ler_json(tmp_data / f"brutos/{D}/_falhas.json") == {"ruim": ANY}
    assert carregar_itens(tmp_data / f"brutos/{D}/ok.json")


def test_coletar_todas_falham(tmp_data, monkeypatch):
    _fake(monkeypatch, {"a": boom, "b": boom})
    assert main(["coletar", "--data", D]) == 1


def test_filtrar_marca_indisponiveis_e_serializa(tmp_data, monkeypatch):
    _fake(monkeypatch, {"ok": lambda d: [_item(), _item("camara:2", sigla_tipo="REQ")], "ruim": boom})
    main(["coletar", "--data", D])
    assert main(["filtrar", "--data", D]) == 0
    sel = ler_json(tmp_data / f"selecionados/{D}.json")
    assert sel["fontes_indisponiveis"] == ["ruim"]
    assert [i["id"] for i in sel["destaques"]] == ["camara:1"]
    assert [i["id"] for i in sel["menores"]] == ["camara:2"]
    assert ler_json(tmp_data / "pendentes.json") == []
