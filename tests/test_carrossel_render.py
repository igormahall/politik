import struct

import pytest

from politik.carrossel.render import paginas_html, renderizar

AVISO = "Só o veículo X divulgou o pedido de asilo."
MODELO = {
    "data_extenso": "quarta-feira, 28 de outubro de 2026",
    "capa": {"temas": [{"nome": "Caso Master", "linha": "Fachin mantém o caso no STF"}], "mais": 1, "niveis": []},
    "temas": [
        {
            "etiqueta": "Tema em andamento · dia 5",
            "nome": "Caso Master",
            "novo_hoje": "Fachin manteve o caso na Presidência do STF.",
            "aviso": AVISO,
            "para_entender": "O Banco Central liquidou o Banco Master.",
        },
        {
            "etiqueta": "Tema em andamento · dia 2",
            "nome": "Outro",
            "novo_hoje": "Algo novo.",
            "aviso": None,
            "para_entender": "Resumo.",
        },
    ],
    "fichas": {
        "grupos": [
            {
                "nivel": "Federal",
                "itens": [{"situacao": "Proposta apresentada", "titulo": "Muda o FGTS", "fonte_unica": True}],
            }
        ],
        "mais": 2,
    },
    "total": 5,
}


def _chromium():
    pw = pytest.importorskip("playwright.sync_api")
    try:
        p = pw.sync_playwright().start()
        navegador = p.chromium.launch()
    except Exception as e:  # Chromium não instalado nesta máquina
        pytest.skip(f"Chromium indisponível: {e}")
    return p, navegador


def test_paginas_html_ordem_e_textos():
    p = paginas_html(MODELO)
    assert len(p) == 5
    assert "O dia na política" in p[0] and "quarta-feira, 28 de outubro de 2026" in p[0]
    assert "Fachin mantém o caso no STF" in p[0] and "Mais 1 movimentação oficial" in p[0]
    assert AVISO in p[1] and "Também hoje" in p[3] and "e mais 2 no link da bio" in p[3] and "fonte única" in p[3]
    assert "Os fatos lado a lado" in p[-1] and "Link na bio · boletim diário grátis no Telegram" in p[-1]
    assert "5/5" in p[-1] and "1/5" in p[0]
    assert "fonts.googleapis" not in "".join(p)


def test_capa_dia_sem_temas():
    m = {**MODELO, "capa": {"temas": [], "mais": 3, "niveis": ["Federal", "Amazonas"]}, "temas": [], "total": 3}
    capa = paginas_html(m)[0]
    assert "Hoje: 3 movimentações oficiais" in capa and "Federal · Amazonas" in capa


def test_texto_escapado():
    m = {**MODELO, "capa": {**MODELO["capa"], "temas": [{"nome": "A & B <script>", "linha": None}]}}
    capa = paginas_html(m)[0]
    assert "A &amp; B &lt;script&gt;" in capa and "A & B <script>" not in capa


def test_renderiza_png_1080x1350(tmp_path):
    p, navegador = _chromium()
    navegador.close()
    p.stop()
    arqs = renderizar(MODELO, tmp_path)
    assert [a.name for a in arqs] == ["01.png", "02.png", "03.png", "04.png", "05.png"]
    for a in arqs:
        assert struct.unpack(">II", a.read_bytes()[16:24]) == (1080, 1350)


def test_texto_longo_cabe_e_aviso_fica_inteiro():
    longo = " ".join(
        f"Frase número {i} do novo hoje, com detalhes que ocupam bastante espaço no slide." for i in range(12)
    )
    m = {**MODELO, "temas": [{**MODELO["temas"][0], "novo_hoje": longo}, MODELO["temas"][1]]}
    p, navegador = _chromium()
    try:
        pagina = navegador.new_page(viewport={"width": 1080, "height": 1350})
        pagina.set_content(paginas_html(m)[1])
        pagina.evaluate("encaixar()")
        corpo = pagina.locator(".corpo")
        assert corpo.evaluate("e => e.scrollHeight <= e.clientHeight")
        assert pagina.locator(".aviso").inner_text().endswith(AVISO)
        assert pagina.locator(".novo-hoje").inner_text().startswith("Frase número 0")
    finally:
        navegador.close()
        p.stop()


def test_fontes_da_marca_carregam():
    p, navegador = _chromium()
    try:
        pagina = navegador.new_page()
        pagina.set_content(paginas_html(MODELO)[0])
        estados = pagina.evaluate("document.fonts.ready.then(() => [...document.fonts].map(f => f.status))")
        assert estados and set(estados) == {"loaded"}
    finally:
        navegador.close()
        p.stop()


def _encaixado(m, slide):
    p, navegador = _chromium()
    try:
        pagina = navegador.new_page(viewport={"width": 1080, "height": 1350})
        pagina.set_content(paginas_html(m)[slide])
        pagina.evaluate("encaixar()")
        return (
            pagina.locator(".corpo").evaluate("e => e.scrollHeight <= e.clientHeight"),
            pagina.locator(".novo-hoje").inner_text(),
            pagina.locator(".aviso").inner_text(),
        )
    finally:
        navegador.close()
        p.stop()


def test_corte_nao_quebra_numero_com_ponto():
    longo = " ".join(["O MPT informou 3.396 denúncias de assédio eleitoral e processou a Meta."] * 40)
    m = {**MODELO, "temas": [{**MODELO["temas"][0], "novo_hoje": longo}]}
    cabe, texto, aviso = _encaixado(m, 1)
    assert cabe and aviso.endswith(AVISO) and texto.endswith("…")
    assert "3. " not in texto and texto.count("3.396") >= 1


def test_frase_unica_gigante_corta_por_palavra_e_mantem_aviso():
    m = {**MODELO, "temas": [{**MODELO["temas"][0], "novo_hoje": "palavra " * 500}]}
    cabe, texto, aviso = _encaixado(m, 1)
    assert cabe and aviso.endswith(AVISO) and texto.endswith("…")


def test_singular_de_movimentacao_e_mais_fora_da_lista_numerada():
    um = {**MODELO, "capa": {**MODELO["capa"], "mais": 1}}
    capa = paginas_html(um)[0]
    assert "Mais 1 movimentação oficial" in capa and "<li>Mais" not in capa
    sem_temas = {**MODELO, "capa": {"temas": [], "mais": 1, "niveis": ["Federal"]}, "temas": [], "total": 3}
    assert "Hoje: 1 movimentação oficial" in paginas_html(sem_temas)[0]


def test_divisao_de_frases_respeita_numeros_brasileiros():
    p, navegador = _chromium()
    try:
        pagina = navegador.new_page()
        pagina.set_content(paginas_html(MODELO)[1])
        partes = pagina.evaluate("frases('O MPT informou 3.396 denúncias. Bloqueou R$ 1,5 mi. Fim')")
        assert partes == ["O MPT informou 3.396 denúncias. ", "Bloqueou R$ 1,5 mi. ", "Fim"]
    finally:
        navegador.close()
        p.stop()
