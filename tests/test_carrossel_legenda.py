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
    assert "• Também hoje: Federal" in t and "movimentaç" not in t
    assert t.rstrip().endswith("#politik")


def test_legenda_sem_linha_e_caracteres_especiais():
    t = legenda(_modelo([{"nome": "A & B <C>", "linha": None}], mais=0))
    assert "\n• A & B <C>\n" in t and "&amp;" not in t
    assert "movimentações" not in t


def test_legenda_respeita_limite():
    t = legenda(_modelo([{"nome": f"T{i}", "linha": "x" * 1000} for i in range(5)]))
    assert len(t) <= LIMITE_INSTAGRAM
    assert t.rstrip().endswith("#politik") and "• T0: " in t and "• Também hoje: Federal" in t


def test_legenda_dia_sem_temas_lista_os_niveis():
    t = legenda(_modelo([], mais=2, niveis=("Federal", "Amazonas", "Mundo")))
    assert "• Hoje: Federal · Amazonas · Mundo" in t and "movimentaç" not in t
