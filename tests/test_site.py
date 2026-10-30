from politik.__main__ import main
from politik.armazenamento import escrever_json
from politik.site.gerador import url_ficha, url_menores, url_tema
from tests.conftest import load
from tests.helpers import D, escrever_selecionados, item

ID = "camara:2649124"


def popular_exemplo(d, titulo=None, sem_traducao=False):
    ficha = load("exemplo_saida/ficha.json")
    if titulo:
        ficha["titulo"] = titulo
    escrever_selecionados(
        d,
        D,
        destaques=[item(ID, ementa="Ementa <original>")],
        menores=[item("camara:9", sigla_tipo="REQ", titulo="REQ 9/2026", ementa="Requer algo")],
    )
    if sem_traducao:
        escrever_json(d / f"diario/{D}.json", {"data": D, "temas": [], "fichas": [], "sem_traducao": True})
        return
    escrever_json(d / "fichas/camara_2649124.json", ficha)
    escrever_json(d / "temas/caso-master.json", load("exemplo_saida/tema.json"))
    escrever_json(d / f"diario/{D}.json", load("exemplo_saida/diario.json"))


def test_site_gera_paginas(tmp_data, tmp_path):
    popular_exemplo(tmp_data)
    assert main(["site", "--saida", str(tmp_path), "--base-url", "https://x.github.io/politik"]) == 0
    for p in [
        "index.html",
        f"dia/{D}.html",
        "ficha/camara_2649124.html",
        "tema/caso-master.html",
        f"menores/{D}.html",
        "arquivo.html",
        "estilo.css",
    ]:
        assert (tmp_path / p).exists(), p
    ficha = (tmp_path / "ficha/camara_2649124.html").read_text()
    for trecho in ["O que é", "Quem propôs", "O que muda pra você", "Próximo passo", "Proposta apresentada"]:
        assert trecho in ficha
    tema = (tmp_path / "tema/caso-master.html").read_text()
    assert 'id="linha-do-tempo"' in tema and 'id="do-zero"' in tema
    assert "REQ 9/2026" in (tmp_path / f"menores/{D}.html").read_text()


def test_site_escapa(tmp_data, tmp_path):
    popular_exemplo(tmp_data, titulo="Lei <b>&</b>")
    main(["site", "--saida", str(tmp_path), "--base-url", "https://x"])
    assert "Lei &lt;b&gt;&amp;&lt;/b&gt;" in (tmp_path / "ficha/camara_2649124.html").read_text()


def test_site_dia_sem_traducao(tmp_data, tmp_path):
    popular_exemplo(tmp_data, sem_traducao=True)
    main(["site", "--saida", str(tmp_path), "--base-url", "https://x"])
    dia = (tmp_path / f"dia/{D}.html").read_text()
    assert "Tradução indisponível hoje" in dia and "Ementa &lt;original&gt;" in dia


def test_urls():
    assert url_tema("caso-master", "do-zero", base="https://x") == "https://x/tema/caso-master.html#do-zero"
    assert url_ficha("imprensa:g1/a", base="https://x/") == "https://x/ficha/imprensa_g1_a.html"
    assert url_menores(D, base="https://x") == f"https://x/menores/{D}.html"


def test_site_dia_ordena_por_importancia(tmp_data, tmp_path):
    from tests.helpers import escrever_ficha, FICHA_OK

    escrever_selecionados(tmp_data, D, destaques=[item("camara:1"), item("camara:2")])
    escrever_ficha(tmp_data, {**FICHA_OK, "item_id": "camara:1", "titulo": "Menos importante", "importancia": 3})
    escrever_ficha(tmp_data, {**FICHA_OK, "item_id": "camara:2", "titulo": "Mais importante", "importancia": 1})
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": ["camara:1", "camara:2"]})
    main(["site", "--saida", str(tmp_path), "--base-url", "https://x"])
    dia = (tmp_path / f"dia/{D}.html").read_text()
    assert dia.index("⭐ Mais importantes") < dia.index("Mais importante") < dia.index("Menos importante")
