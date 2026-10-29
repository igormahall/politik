import tomllib
from pathlib import Path

from politik.filtro import classificar, filtrar
from politik.modelos import Item

CFG = tomllib.loads(Path("config/filtro.toml").read_text())
D = "2026-10-28"


def item(**kw):
    base = dict(id="camara:1", fonte="camara", nivel="federal", categoria="proposicao", sigla_tipo="PL",
                titulo="t", ementa="", data=D, url="u")
    return Item(**{**base, **kw})


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
    mistura = ([item(id=f"p{k}") for k in range(30)] + [item(id=f"r{k}", sigla_tipo="REQ") for k in range(5)]
               + [item(id=f"n{k}", categoria="noticia", sigla_tipo="NOTICIA", fonte="imprensa:x") for k in range(5)])
    sel, pend = filtrar(D, mistura, [], CFG, [])
    assert len(sel["destaques"]) + len(sel["noticias"]) + len(sel["menores"]) + len(pend) == 40
