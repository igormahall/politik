from politik.modelos import Autor, Item


def test_item_roundtrip():
    it = Item(id="camara:1", fonte="camara", nivel="federal", categoria="proposicao",
              sigla_tipo="PL", titulo="PL 1/2026", ementa="x", data="2026-10-28",
              url="u", autores=[Autor("Ana", "PT", "AM")])
    assert Item.from_dict(it.to_dict()) == it


def test_autor_rotulo():
    assert Autor("Ana", "PT", "AM").rotulo() == "Ana (PT–AM)"
    assert Autor("Ana").rotulo() == "Ana"
