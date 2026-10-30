from datetime import datetime, UTC

from politik.armazenamento import carregar_itens, id_seguro, salvar_itens
from politik.datas import dia_de_referencia
from tests.helpers import item as _item


def test_salvar_itens_idempotente(tmp_path):
    p = tmp_path / "x.json"
    a, b = _item("camara:a"), _item("camara:b")
    salvar_itens(p, [a, b])
    salvar_itens(p, [a])
    assert [i.id for i in carregar_itens(p)] == [a.id, b.id]


def test_dia_de_referencia():
    assert dia_de_referencia(datetime(2026, 10, 29, 10, 0, tzinfo=UTC)) == "2026-10-28"
    assert dia_de_referencia(datetime(2026, 10, 29, 2, 0, tzinfo=UTC)) == "2026-10-27"


def test_id_seguro():
    assert id_seguro("imprensa:g1/abc") == "imprensa_g1_abc"
