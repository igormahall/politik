import json
from collections.abc import Callable
from datetime import date, timedelta

from politik.modelos import Item


class FonteIndisponivel(Exception):
    pass


COLETORES: dict[str, Callable[[str], list[Item]]] = {}


def registrar(nome: str):
    def deco(fn):
        COLETORES[nome] = fn
        return fn

    return deco


def carregar_todos() -> dict[str, Callable[[str], list[Item]]]:
    # importa os módulos para que se registrem
    from politik.coletores import camara, dou, imprensa, mundo, sapl, senado, tramitacao  # noqa: F401

    return COLETORES


def ja_vistos(data: str, prefixos: tuple[str, ...], dias: int = 14) -> set[str]:
    """ids que já passaram por boletins anteriores ou estão na fila, para coletas com janela de vários dias."""
    from politik.armazenamento import data_dir

    ids: set[str] = set()
    hoje = date.fromisoformat(data)
    for n in range(1, dias + 1):
        p = data_dir() / "selecionados" / f"{(hoje - timedelta(days=n)).isoformat()}.json"
        if p.exists():
            sel = json.loads(p.read_text(encoding="utf-8"))
            ids |= {i["id"] for k in ("destaques", "noticias", "menores") for i in sel.get(k, [])}
    p = data_dir() / "pendentes.json"
    if p.exists():
        ids |= {x["item"]["id"] for x in json.loads(p.read_text(encoding="utf-8"))}
    return {i for i in ids if i.startswith(prefixos)}
