from politik.carrossel.legenda import legenda, LIMITE_INSTAGRAM


def _modelo(temas, mais=3, niveis=("Federal",)):
    return {
        "data_extenso": "quarta-feira, 28 de outubro de 2026",
        "capa": {"temas": temas, "mais": mais, "niveis": list(niveis)},
    }


def test_legenda_dia_normal():
    t = legenda(_modelo([{"nome": "Caso Master", "linha": "Fachin mantém o caso no STF"}, {"nome": "B", "linha": "x"}]))
    assert t.startswith("Politik · quarta-feira, 28 de outubro de 2026\n")
    assert "• Caso Master: Fachin mantém o caso no STF" in t
    assert "• Mais 3 movimentações oficiais" in t
    assert t.rstrip().endswith("#politik")


def test_legenda_sem_linha_e_caracteres_especiais():
    t = legenda(_modelo([{"nome": "A & B <C>", "linha": None}], mais=0))
    assert "\n• A & B <C>\n" in t and "&amp;" not in t
    assert "movimentações" not in t


def test_legenda_dia_sem_temas():
    t = legenda(_modelo([], mais=2, niveis=("Federal", "Amazonas")))
    assert "• 2 movimentações oficiais (Federal · Amazonas)" in t


def test_legenda_respeita_limite():
    t = legenda(_modelo([{"nome": f"T{i}", "linha": "x" * 1000} for i in range(5)]))
    assert len(t) <= LIMITE_INSTAGRAM
    assert t.rstrip().endswith("#politik") and "• T0: " in t and "• Mais 3" in t


def test_legenda_singular():
    assert "• Mais 1 movimentação oficial\n" in legenda(_modelo([{"nome": "A", "linha": None}], mais=1))
    assert "• 1 movimentação oficial (Federal)" in legenda(_modelo([], mais=1))


def test_legenda_com_mundo():
    m = _modelo([{"nome": "A", "linha": None}], mais=2)
    assert "• 1 fato do mundo" in legenda({**m, "capa": {**m["capa"], "mundo": 1}})
    t = legenda({**m, "capa": {**m["capa"], "mundo": 3}})
    assert t.index("• Mais 2 movimentações oficiais") < t.index("• 3 fatos do mundo")


def test_legenda_so_mundo_sem_movimentacoes():
    t = legenda(
        _modelo([], mais=0, niveis=("Mundo",)) | {"capa": {"temas": [], "mais": 0, "niveis": ["Mundo"], "mundo": 3}}
    )
    assert "• 3 fatos do mundo" in t and "movimentaç" not in t
