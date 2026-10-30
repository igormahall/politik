from politik.esquemas import erros_diario, erros_ficha, erros_mundo, erros_tema, limpar_capa
from tests.helpers import FICHA_OK, MUNDO_OK, TEMA_OK


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
    assert (
        erros_diario(
            {
                "data": "2026-10-28",
                "temas": [{"slug": "a", "novo_hoje": "x", "aviso_fonte_unica": None}],
                "fichas": ["camara:1"],
            }
        )
        == []
    )
    assert erros_diario({"data": "2026-10-28", "temas": [{"slug": "a"}], "fichas": []})


def test_limpar_capa_remove_so_campos_ruins():
    d = {
        "data": "2026-10-29",
        "fichas": [],
        "temas": [
            {"slug": "a", "novo_hoje": "x", "nome_curto": "Caso Master", "linha_capa": "Fachin mantém o caso no STF"},
            {"slug": "b", "novo_hoje": "x", "nome_curto": "", "linha_capa": "y" * 81},
            {"slug": "c", "novo_hoje": "x", "nome_curto": 3},
        ],
    }
    avisos = limpar_capa(d)
    assert d["temas"][0]["nome_curto"] == "Caso Master" and "linha_capa" in d["temas"][0]
    assert "nome_curto" not in d["temas"][1] and "linha_capa" not in d["temas"][1]
    assert "nome_curto" not in d["temas"][2]
    assert len(avisos) == 3
    assert erros_diario(d) == []


def test_mundo_ok():
    assert erros_mundo(MUNDO_OK) == []


def test_mundo_mesma_organizacao_duas_vezes_e_invalida():
    fontes = [
        {"nome": "BBC", "url": "https://www.bbc.com/news/a"},
        {"nome": "BBC Brasil", "url": "https://www.bbc.com/portuguese/b"},
    ]
    assert any("duas organizações" in e for e in erros_mundo({**MUNDO_OK, "fontes": fontes}))


def test_mundo_url_nao_coletada_e_invalida():
    erros = erros_mundo(MUNDO_OK, urls_mundo={"https://outra"}, urls_impacto=set())
    assert any("não coletada" in e for e in erros)
    urls = {f["url"] for f in MUNDO_OK["fontes"]}
    impacto = {MUNDO_OK["fontes_impacto"][0]["url"]}
    assert erros_mundo(MUNDO_OK, urls_mundo=urls, urls_impacto=urls | impacto) == []


def test_mundo_agencia_brasil_nacional_nao_confirma_fato():
    # mesma organização por domínio, mas a URL veio da imprensa nacional, não do feed internacional
    fontes = [MUNDO_OK["fontes"][0], {"nome": "Agência Brasil", "url": "https://agenciabrasil.ebc.com.br/politica/y"}]
    urls_mundo = {MUNDO_OK["fontes"][0]["url"]}
    erros = erros_mundo({**MUNDO_OK, "fontes": fontes}, urls_mundo=urls_mundo, urls_impacto=set())
    assert any("não coletada" in e for e in erros)


def test_mundo_impacto_sem_fonte_e_invalido():
    assert erros_mundo({k: v for k, v in MUNDO_OK.items() if k != "fontes_impacto"})


def test_tema_internacional_exige_duas_organizacoes():
    assert erros_tema({**TEMA_OK, "internacional": True})
    assert erros_tema(TEMA_OK) == []
