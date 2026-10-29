import unicodedata

from politik.armazenamento import data_dir, ler_json
from politik.modelos import Item


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").casefold()


def carregar_temas(ativos: bool = True) -> list[dict]:
    temas = [ler_json(p) for p in sorted((data_dir() / "temas").glob("*.json"))]
    return [t for t in temas if isinstance(t, dict) and "slug" in t and (t.get("ativo", True) or not ativos)]


def casa_tema(item: Item, temas: list[dict]) -> list[str]:
    texto = normalizar(" ".join([item.titulo, item.ementa, item.extra.get("orgao", "")]))
    return [t["slug"] for t in temas if any(normalizar(p) in texto for p in t.get("palavras_chave", []) if p)]


def marcar_inativos(hoje: str, dias: int) -> list[str]:
    from datetime import date, timedelta

    from politik.armazenamento import escrever_json

    limite = (date.fromisoformat(hoje) - timedelta(days=dias)).isoformat()
    alterados = []
    for p in sorted((data_dir() / "temas").glob("*.json")):
        t = ler_json(p)
        if isinstance(t, dict) and t.get("ativo") and t.get("ultima_novidade", hoje) < limite:
            t["ativo"] = False
            escrever_json(p, t)
            alterados.append(t["slug"])
    return alterados
