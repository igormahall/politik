import json
import os
from pathlib import Path

from politik.modelos import Item


def data_dir() -> Path:
    return Path(os.environ.get("POLITIK_DATA", "data"))


def ler_json(caminho: Path, padrao=None):
    caminho = Path(caminho)
    if not caminho.exists():
        return padrao
    return json.loads(caminho.read_text(encoding="utf-8"))


def escrever_json(caminho: Path, obj) -> None:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def carregar_itens(caminho: Path) -> list[Item]:
    return [Item.from_dict(d) for d in ler_json(caminho, [])]


def salvar_itens(caminho: Path, itens: list[Item]) -> None:
    por_id = {i.id: i for i in carregar_itens(caminho)}
    for i in itens:
        por_id[i.id] = i
    escrever_json(caminho, [i.to_dict() for i in por_id.values()])


def id_seguro(item_id: str) -> str:
    return item_id.replace(":", "_").replace("/", "_")
