from datetime import date
from typing import Literal

from politik.modelos import Item
from politik.temas import casa_tema, normalizar

FEDERAL = {"camara", "senado"}
LOCAL = {"aleam", "cmm"}


def classificar(item: Item, cfg: dict, temas: list[dict]) -> Literal["destaque", "menor", "noticia"]:
    if item.categoria == "noticia":
        return "noticia"
    if item.categoria == "votacao" and item.extra.get("proposicao", True) is None and not casa_tema(item, temas):
        return "menor"  # votação sem projeto identificado não diz nada ao leitor
    if casa_tema(item, temas) or item.categoria in cfg["destaque_categorias"]:
        return "destaque"
    ementa = normalizar(item.ementa)
    if any(t in ementa for t in cfg.get("menores_termos_ementa", [])):
        return "menor"
    if item.fonte == "dou":
        return "destaque" if item.sigla_tipo in cfg["dou_destaque_tipos"] else "menor"
    if item.categoria == "norma" and item.fonte in LOCAL:
        return "destaque" if cfg["norma_sapl_destaque"] else "menor"
    if item.fonte in FEDERAL and item.sigla_tipo in cfg["destaque_siglas_federal"]:
        return "destaque"
    if item.fonte in LOCAL and item.sigla_tipo in cfg["destaque_siglas_local"]:
        return "destaque"
    return "menor"


def prioridade(item: Item, temas: list[dict]) -> int:
    if casa_tema(item, temas):
        return 1
    if item.categoria == "norma":
        return 2
    if item.categoria in ("votacao", "tramitacao"):
        return 3
    return {"federal": 4, "estadual": 5, "municipal": 6}[item.nivel]


def _idade(data: str, primeira_vez: str) -> int:
    return (date.fromisoformat(data) - date.fromisoformat(primeira_vez)).days


def filtrar(data: str, itens: list[Item], pendentes: list[dict], cfg: dict,
            temas: list[dict]) -> tuple[dict, list[dict]]:
    menores: list[Item] = []
    noticias: list[Item] = []
    candidatos: list[tuple[Item, str]] = []  # (item, primeira_vez)

    for p in pendentes:
        it = Item.from_dict(p["item"])
        if _idade(data, p["primeira_vez"]) > cfg["pendente_max_dias"]:
            menores.append(it)
        else:
            candidatos.append((it, p["primeira_vez"]))

    ja = {it.id for it, _ in candidatos}
    for it in itens:
        if it.id in ja:
            continue
        tipo = classificar(it, cfg, temas)
        if tipo == "destaque":
            candidatos.append((it, data))
        elif tipo == "noticia":
            noticias.append(it)
        else:
            menores.append(it)

    # sort é estável: pendentes (que vêm antes) ganham empates
    candidatos.sort(key=lambda c: prioridade(c[0], temas))
    teto = cfg["teto_destaques"]
    destaques = [it for it, _ in candidatos[:teto]]
    novos_pendentes = [{"item": it.to_dict(), "primeira_vez": pv} for it, pv in candidatos[teto:]]

    noticias.sort(key=lambda it: 0 if casa_tema(it, temas) else 1)
    menores += noticias[cfg["teto_noticias"]:]
    noticias = noticias[:cfg["teto_noticias"]]

    selecionados = {"data": data, "destaques": destaques, "noticias": noticias,
                    "menores": menores, "fontes_indisponiveis": [],
                    "primeira_vez": {it.id: pv for it, pv in candidatos[:teto]}}
    return selecionados, novos_pendentes
