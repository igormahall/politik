from dataclasses import asdict, dataclass, field
from typing import Literal

Nivel = Literal["federal", "estadual", "municipal", "mundo"]
Categoria = Literal["proposicao", "norma", "votacao", "tramitacao", "noticia", "mundo"]


@dataclass
class Autor:
    nome: str
    partido: str | None = None
    uf: str | None = None

    def rotulo(self) -> str:
        if self.partido and self.uf:
            return f"{self.nome} ({self.partido}–{self.uf})"
        if self.partido:
            return f"{self.nome} ({self.partido})"
        return self.nome


@dataclass
class Item:
    id: str
    fonte: str
    nivel: Nivel
    categoria: Categoria
    sigla_tipo: str
    titulo: str
    ementa: str
    data: str
    url: str
    autores: list[Autor] = field(default_factory=list)
    url_documento: str | None = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Item":
        d = dict(d)
        d["autores"] = [Autor(**a) for a in d.get("autores", [])]
        return cls(**d)
