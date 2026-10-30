from politik.filtro import classificar, filtrar
from tests.helpers import CFG, D, item


def test_requerimento_vai_para_menores():
    assert classificar(item(sigla_tipo="REQ"), CFG, []) == "menor"


def test_parecer_da_camara_vai_para_menores_mas_prl_da_aleam_e_destaque():
    assert classificar(item(sigla_tipo="PRL"), CFG, []) == "menor"
    assert classificar(item(fonte="aleam", nivel="estadual", sigla_tipo="PRL"), CFG, []) == "destaque"


def test_noticia():
    assert classificar(item(categoria="noticia", fonte="imprensa:g1", sigla_tipo="NOTICIA"), CFG, []) == "noticia"


def test_dou_lei_destaque_portaria_menor():
    assert classificar(item(fonte="dou", categoria="norma", sigla_tipo="LEI"), CFG, []) == "destaque"
    assert classificar(item(fonte="dou", categoria="norma", sigla_tipo="PORTARIA"), CFG, []) == "menor"


def test_portaria_vira_destaque_se_casa_tema():
    tema = {"slug": "caso-master", "palavras_chave": ["Banco Master"]}
    it = item(fonte="dou", categoria="norma", sigla_tipo="PORTARIA", ementa="... Banco Master S.A. ...")
    assert classificar(it, CFG, [tema]) == "destaque"


def test_teto_e_pendentes():
    itens = [item(id=f"camara:{n}") for n in range(30)]
    sel, pend = filtrar(D, itens, [], CFG, [])
    assert len(sel["destaques"]) == 25 and len(pend) == 5
    assert all(p["primeira_vez"] == D for p in pend)
    assert sel["data"] == D and sel["fontes_indisponiveis"] == []


def test_pendente_expira_para_menores():
    pend = [{"item": item(id="camara:x").to_dict(), "primeira_vez": "2026-10-25"}]
    sel, novos = filtrar(D, [], pend, CFG, [])
    assert [i.id for i in sel["menores"]] == ["camara:x"] and novos == []


def test_pendente_valido_volta_e_mantem_primeira_vez():
    pend = [{"item": item(id="camara:x").to_dict(), "primeira_vez": "2026-10-27"}]
    itens = [item(id=f"camara:{n}") for n in range(25)]
    sel, novos = filtrar(D, itens, pend, CFG, [])
    # pendentes entram antes dos novos de mesma prioridade
    assert "camara:x" in [i.id for i in sel["destaques"]]
    assert len(novos) == 1 and novos[0]["primeira_vez"] == D


def test_prioridade_norma_antes_de_proposicao():
    sel, _ = filtrar(D, [item(id="a"), item(id="b", categoria="norma", fonte="dou", sigla_tipo="LEI")], [], CFG, [])
    assert [i.id for i in sel["destaques"]] == ["b", "a"]


def test_prioridade_federal_estadual_municipal():
    itens = [item(id="m", fonte="cmm", nivel="municipal"), item(id="e", fonte="aleam", nivel="estadual"), item(id="f")]
    sel, _ = filtrar(D, itens, [], CFG, [])
    assert [i.id for i in sel["destaques"]] == ["f", "e", "m"]


def test_noticias_teto_e_tema_primeiro():
    tema = {"slug": "t", "palavras_chave": ["Master"]}
    nots = [item(id=f"n{k}", categoria="noticia", fonte="imprensa:g1", sigla_tipo="NOTICIA") for k in range(70)]
    nots.append(item(id="nm", categoria="noticia", fonte="imprensa:g1", sigla_tipo="NOTICIA", titulo="Caso Master"))
    sel, _ = filtrar(D, nots, [], CFG, [tema])
    assert len(sel["noticias"]) == 60 and sel["noticias"][0].id == "nm"
    assert len(sel["menores"]) == 11


def test_nada_some():
    mistura = (
        [item(id=f"p{k}") for k in range(30)]
        + [item(id=f"r{k}", sigla_tipo="REQ") for k in range(5)]
        + [item(id=f"n{k}", categoria="noticia", sigla_tipo="NOTICIA", fonte="imprensa:x") for k in range(5)]
    )
    sel, pend = filtrar(D, mistura, [], CFG, [])
    assert len(sel["destaques"]) + len(sel["noticias"]) + len(sel["menores"]) + len(pend) == 40


def test_homenagem_vai_para_menores_mesmo_sendo_pl():
    it = item(fonte="aleam", nivel="estadual", ementa="Concede o Título de Cidadão do Amazonas ao Senhor X.")
    assert classificar(it, CFG, []) == "menor"
    assert classificar(item(fonte="cmm", nivel="municipal", ementa="DENOMINA rua no bairro Y"), CFG, []) == "menor"


def test_homenagem_ligada_a_tema_continua_destaque():
    tema = {"slug": "t", "palavras_chave": ["Vorcaro"]}
    assert classificar(item(ementa="Concede medalha a Vorcaro"), CFG, [tema]) == "destaque"


def _mundo(i, org):
    return item(f"mundo:{org}:{i}", fonte="mundo", nivel="mundo", categoria="mundo", extra={"organizacao": org})


def test_mundo_vai_para_balde_proprio_com_rodizio():
    itens = [_mundo(i, "BBC") for i in range(100)] + [_mundo(i, "DW") for i in range(10)]
    itens += [_mundo(i, "Agência Brasil") for i in range(5)]
    sel, _ = filtrar(D, itens, [], CFG, [])
    assert len(sel["mundo"]) == 80
    orgs = [i.extra["organizacao"] for i in sel["mundo"]]
    assert orgs.count("DW") == 10 and orgs.count("Agência Brasil") == 5
    assert not sel["menores"] and not sel["noticias"] and not sel["destaques"]


def test_tramitacao_de_projeto_apresentado_no_mesmo_dia_nao_vira_ficha_repetida():
    novo = item("senado:1", fonte="senado", sigla_tipo="PL")
    tram_mesmo_dia = item("senado:1:sit:x", fonte="senado", categoria="tramitacao", extra={"item_origem": "senado:1"})
    tram_antigo = item("senado:2:sit:x", fonte="senado", categoria="tramitacao", extra={"item_origem": "senado:2"})
    sel, _ = filtrar(D, [novo, tram_mesmo_dia, tram_antigo], [], CFG, [])
    assert {i.id for i in sel["destaques"]} == {"senado:1", "senado:2:sit:x"}
    assert "senado:1:sit:x" in [i.id for i in sel["menores"]]
