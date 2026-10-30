import sys
from dataclasses import replace
from pathlib import Path

import httpx

from politik.coletores import FonteIndisponivel, registrar
from politik.coletores.imprensa import carregar_feeds, parse_feed, UA
from politik.modelos import Item

CONFIG = Path("config/mundo.toml")


@registrar("mundo")
def coletar(data: str, feeds: list[dict] | None = None, cliente: httpx.Client | None = None) -> list[Item]:
    feeds = carregar_feeds(CONFIG) if feeds is None else feeds
    cliente = cliente or httpx.Client(timeout=30, follow_redirects=True, headers=UA)
    itens, falhas = [], 0
    with cliente:
        for f in feeds:
            try:
                r = cliente.get(f["url"])
                r.raise_for_status()
                for it in parse_feed(f["veiculo"], "mundo", r.content, data):
                    itens.append(
                        replace(
                            it,
                            id=it.id.replace("imprensa:", "mundo:", 1),
                            fonte="mundo",
                            nivel="mundo",
                            categoria="mundo",
                            extra={"veiculo": f["veiculo"], "organizacao": f["organizacao"]},
                        )
                    )
            except Exception as e:  # um feed ruim não derruba os outros
                falhas += 1
                print(f"mundo: feed {f['veiculo']} falhou: {e}", file=sys.stderr)
    if feeds and falhas == len(feeds):
        raise FonteIndisponivel("todos os feeds internacionais falharam")
    return itens
