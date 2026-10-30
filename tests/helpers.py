import tomllib
from pathlib import Path

from politik.armazenamento import escrever_json, id_seguro
from politik.modelos import Item

D = "2026-10-28"
CFG = tomllib.loads(Path("config/filtro.toml").read_text())

FICHA_OK = {
    "item_id": "camara:1",
    "nivel": "federal",
    "tipo_simples": "Projeto de lei",
    "situacao": "Proposta apresentada",
    "titulo": "Muda o saque do FGTS",
    "o_que_e": "Um projeto que muda o saque.",
    "quem_propos": "Dep. Ana (PT–AM)",
    "o_que_muda": "Ainda não muda nada: é só uma proposta.",
    "proximo_passo": "Vai para as comissões.",
    "fontes": [{"nome": "Câmara dos Deputados", "url": "https://www.camara.leg.br/x"}],
    "fonte_unica": False,
    "temas": [],
    "data": D,
}

TEMA_OK = {
    "slug": "caso-master",
    "nome": "Caso Master",
    "inicio": "2025-11-18",
    "ativo": True,
    "ultima_novidade": D,
    "palavras_chave": ["Banco Master"],
    "resumo_ate_aqui": "Resumo.",
    "explica_do_zero": "Do zero.",
    "linha_do_tempo": [
        {
            "data": "2025-11-18",
            "fato": "Fato.",
            "fontes": [{"nome": "Agência Brasil", "url": "https://a"}],
            "fonte_unica": True,
        }
    ],
}


def item(id="camara:1", **kw):
    return Item(
        **{
            **dict(
                id=id,
                fonte="camara",
                nivel="federal",
                categoria="proposicao",
                sigla_tipo="PL",
                titulo="PL 1/2026",
                ementa="Ementa original",
                data=D,
                url="https://u",
            ),
            **kw,
        }
    )


def escrever_selecionados(d, data, destaques=(), noticias=(), menores=(), indisponiveis=(), mundo=()):
    escrever_json(
        d / f"selecionados/{data}.json",
        {
            "data": data,
            "destaques": [i.to_dict() for i in destaques],
            "noticias": [i.to_dict() for i in noticias],
            "menores": [i.to_dict() for i in menores],
            "mundo": [i.to_dict() for i in mundo],
            "fontes_indisponiveis": list(indisponiveis),
        },
    )


def escrever_ficha(d, ficha):
    escrever_json(d / f"fichas/{id_seguro(ficha['item_id'])}.json", ficha)


def escrever_tema(d, tema):
    escrever_json(d / f"temas/{tema['slug']}.json", tema)


MUNDO_OK = {
    "item_id": "mundo:2026-10-28:1",
    "titulo": "EUA anunciam tarifa sobre o aço",
    "o_que_aconteceu": "O governo dos EUA anunciou uma tarifa sobre o aço importado.",
    "importa_para_o_brasil": "A CNI disse, segundo a Agência Brasil, que as exportações de aço podem cair.",
    "fontes": [
        {"nome": "BBC", "url": "https://www.bbc.com/portuguese/articles/a1"},
        {"nome": "DW", "url": "https://www.dw.com/pt-br/a-2"},
    ],
    "fontes_impacto": [{"nome": "Agência Brasil", "url": "https://agenciabrasil.ebc.com.br/economia/x"}],
    "importancia": 1,
    "data": D,
}


def escrever_mundo(d, ficha):
    escrever_json(d / "mundo" / f"{id_seguro(ficha['item_id'])}.json", ficha)
