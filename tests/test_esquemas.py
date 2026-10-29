from politik.esquemas import erros_diario, erros_ficha, erros_tema
from tests.helpers import FICHA_OK, TEMA_OK


def test_ficha_ok():
    assert erros_ficha(FICHA_OK) == []


def test_ficha_sem_fonte_invalida():
    assert any("fontes" in e for e in erros_ficha({**FICHA_OK, "fontes": []}))


def test_ficha_texto_vazio_e_nivel_errado():
    erros = erros_ficha({**FICHA_OK, "o_que_muda": " ", "nivel": "mundial"})
    assert any("o_que_muda" in e for e in erros) and any("nivel" in e for e in erros)


def test_ficha_url_sem_http():
    assert erros_ficha({**FICHA_OK, "fontes": [{"nome": "x", "url": "www.x"}]})


def test_tema_ok_e_linha_fora_de_ordem():
    assert erros_tema(TEMA_OK) == []
    lt = [{**TEMA_OK["linha_do_tempo"][0], "data": "2026-01-02"}, TEMA_OK["linha_do_tempo"][0]]
    assert any("ordem" in e for e in erros_tema({**TEMA_OK, "linha_do_tempo": lt}))


def test_tema_fato_sem_fonte():
    lt = [{**TEMA_OK["linha_do_tempo"][0], "fontes": []}]
    assert erros_tema({**TEMA_OK, "linha_do_tempo": lt})


def test_diario():
    assert erros_diario({"data": "2026-10-28", "temas": [{"slug": "a", "novo_hoje": "x", "aviso_fonte_unica": None}],
                         "fichas": ["camara:1"]}) == []
    assert erros_diario({"data": "2026-10-28", "temas": [{"slug": "a"}], "fichas": []})
