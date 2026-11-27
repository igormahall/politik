from datetime import date
from typing import Literal

from politik.modelos import Item
from politik.temas import casa_tema, normalizar

FEDERAL = {"camara", "senado"}
LOCAL = {"aleam", "cmm"}


def classificar(item: Item, cfg: dict, temas: list[dict]) -> Literal["destaque", "menor", "noticia", "mundo"]:
    if item.categoria in ("noticia", "mundo"):
        return item.categoria
    if item.categoria == "votacao" and item.extra.get("proposicao", True) is None and not casa_tema(item, temas):
        return "menor"  # votação sem projeto identificado não diz nada ao leitor
    if item.categoria == "tramitacao" and normalizar(item.titulo).startswith(tuple(cfg.get("tramitacao_rotina", []))):
        return "menor"  # etapa burocrática: não é notícia nem quando o projeto é de um tema
    if casa_tema(item, temas) or item.categoria in cfg["destaque_categorias"]:
        return "destaque"
    ementa = normalizar(item.ementa)
    if any(t in ementa for t in cfg.get("menores_termos_ementa", [])):
        return "menor"
    if item.fonte == "dou":
        # a base aberta acrescenta qualificadores ("DECRETO NUMERADO"): vale o tipo e suas variantes
        tipo = item.sigla_tipo
        return "destaque" if any(tipo == t or tipo.startswith(t + " ") for t in cfg["dou_destaque_tipos"]) else "menor"
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


def _rodizio(itens: list[Item], teto: int, chave=lambda it: it.extra.get("organizacao", "")) -> list[Item]:
    """Um de cada organização por vez, na ordem de chegada: nenhuma toma o teto sozinha."""
    filas: dict[str, list[Item]] = {}
    for it in itens:
        filas.setdefault(chave(it), []).append(it)
    saida = []
    while len(saida) < teto and any(filas.values()):
        for fila in filas.values():
            if fila and len(saida) < teto:
                saida.append(fila.pop(0))
    return saida


# atos que, por natureza, aparecem em mais de um lugar: a MP sai no DOU e tramita na Câmara e no Senado
REPLICADOS = ("MPV", "PLN", "MEDIDA PROVISORIA")


def _chave_ementa(it: Item) -> str:
    if not it.sigla_tipo.startswith(REPLICADOS):
        return ""  # PLs com o mesmo texto em casas diferentes podem ser de autores diferentes
    return " ".join(normalizar(it.ementa).split()).rstrip(".")


def _sem_repeticao(candidatos: list[tuple[Item, str]], temas: list[dict]) -> tuple[list, list[Item]]:
    """MP ou PLN com a mesma ementa em fontes diferentes é o mesmo ato; na mesma fonte são atos distintos."""
    fonte_da_vez: dict[str, str] = {}  # ementa -> fonte do candidato de maior prioridade
    for it, _ in sorted(candidatos, key=lambda c: prioridade(c[0], temas)):
        fonte_da_vez.setdefault(_chave_ementa(it), it.fonte)
    manter = [c for c in candidatos if not _chave_ementa(c[0]) or fonte_da_vez[_chave_ementa(c[0])] == c[0].fonte]
    return manter, [it for it, pv in candidatos if (it, pv) not in manter]


def _uma_tramitacao_por_projeto(candidatos: list[tuple[Item, str]]) -> tuple[list, list[Item]]:
    """Várias etapas do mesmo projeto no dia viram uma ficha só: fica a última (em 25/11, 15 etapas do PLP 299/2026)."""
    ultima: dict[str, Item] = {}
    for it, _ in candidatos:
        if it.categoria == "tramitacao":
            ultima[it.extra.get("item_origem") or it.id] = it  # a API devolve as etapas em ordem
    manter = [
        c
        for c in candidatos
        if c[0].categoria != "tramitacao" or ultima[c[0].extra.get("item_origem") or c[0].id] is c[0]
    ]
    return manter, [it for it, pv in candidatos if (it, pv) not in manter]


def _com_vagas_locais(candidatos: list[tuple[Item, str]], teto: int, vagas: int) -> list[tuple[Item, str]]:
    """Reserva até `vagas` lugares para ALEAM e CMM, alternando as casas; o resto segue a prioridade normal."""
    # a ALEAM (estadual) vem antes da CMM na prioridade: sem alternar, uma fila dela deixava a CMM sem vaga
    locais = _rodizio([c for c in candidatos if c[0].fonte in LOCAL], vagas, chave=lambda c: c[0].fonte)
    outros = [c for c in candidatos if c not in locais][: teto - len(locais)]
    escolhidos = {id(c) for c in locais + outros}
    return [c for c in candidatos if id(c) in escolhidos] + [c for c in candidatos if id(c) not in escolhidos]


def _idade(data: str, primeira_vez: str) -> int:
    return (date.fromisoformat(data) - date.fromisoformat(primeira_vez)).days


def filtrar(
    data: str, itens: list[Item], pendentes: list[dict], cfg: dict, temas: list[dict]
) -> tuple[dict, list[dict]]:
    menores: list[Item] = []
    noticias: list[Item] = []
    mundo: list[Item] = []
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
        elif tipo == "mundo":
            mundo.append(it)  # o excedente some: imprensa estrangeira não vai para os menores
        else:
            menores.append(it)

    # projeto apresentado hoje já ganha ficha própria: a tramitação dele no mesmo dia repetiria a notícia
    novos = {it.id for it, _ in candidatos}
    repetidas = [c for c in candidatos if c[0].categoria == "tramitacao" and c[0].extra.get("item_origem") in novos]
    candidatos = [c for c in candidatos if c not in repetidas]
    menores += [it for it, _ in repetidas]

    # o mesmo ato chega por mais de uma fonte (MP no DOU, na Câmara e no Senado): fica o de maior prioridade
    candidatos, repetidas = _sem_repeticao(candidatos, temas)
    menores += repetidas
    candidatos, repetidas = _uma_tramitacao_por_projeto(candidatos)
    menores += repetidas

    # sort é estável: pendentes (que vêm antes) ganham empates
    candidatos.sort(key=lambda c: prioridade(c[0], temas))
    teto = cfg["teto_destaques"]
    candidatos = _com_vagas_locais(candidatos, teto, cfg.get("vagas_locais", 0))
    destaques = [it for it, _ in candidatos[:teto]]
    novos_pendentes = [{"item": it.to_dict(), "primeira_vez": pv} for it, pv in candidatos[teto:]]

    # rodízio entre veículos, com as de tema primeiro dentro de cada um: cortar na ordem dos feeds (ou pôr todas
    # as de tema antes) deixava os do Amazonas, os últimos da lista e quase nunca de tema federal, sempre de fora
    noticias.sort(key=lambda it: 0 if casa_tema(it, temas) else 1)
    escolhidas = _rodizio(noticias, cfg["teto_noticias"], chave=lambda it: it.fonte)
    ids = {it.id for it in escolhidas}
    menores += [it for it in noticias if it.id not in ids]
    noticias = escolhidas

    selecionados = {
        "data": data,
        "destaques": destaques,
        "noticias": noticias,
        "mundo": _rodizio(mundo, cfg.get("teto_mundo", 80)),
        "menores": menores,
        "fontes_indisponiveis": [],
        "primeira_vez": {it.id: pv for it, pv in candidatos[:teto]},
    }
    return selecionados, novos_pendentes
