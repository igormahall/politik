from collections.abc import Callable

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
    from politik.coletores import camara, sapl, senado  # noqa: F401
    return COLETORES
