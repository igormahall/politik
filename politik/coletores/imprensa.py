import hashlib
import re
import sys
import tomllib
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import feedparser
import httpx

from politik.coletores import registrar
from politik.datas import FUSO
from politik.modelos import Item

CONFIG = Path("config/imprensa.toml")
UA = {"User-Agent": "Mozilla/5.0 (politik; +https://github.com)"}


def _sem_tags(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def carregar_feeds(caminho: Path = CONFIG) -> list[dict]:
    return tomllib.loads(caminho.read_text(encoding="utf-8"))["feed"]


def parse_feed(veiculo: str, secao: str, conteudo: bytes, data: str) -> list[Item]:
    itens = []
    for e in feedparser.parse(conteudo).entries:
        quando = e.get("published_parsed") or e.get("updated_parsed")
        if not quando or not e.get("link"):
            continue
        dia = datetime(*quando[:6], tzinfo=timezone.utc).astimezone(FUSO).date().isoformat()
        if dia != data:
            continue
        itens.append(Item(
            id=f"imprensa:{veiculo}:{hashlib.sha1(e.link.encode()).hexdigest()[:12]}",
            fonte=f"imprensa:{veiculo}",
            nivel="estadual" if secao == "amazonas" else "federal",
            categoria="noticia",
            sigla_tipo="NOTICIA",
            titulo=_sem_tags(e.get("title", "")),
            ementa=_sem_tags(e.get("summary", ""))[:500],
            data=dia,
            url=e.link,
            extra={"veiculo": veiculo, "secao": secao},
        ))
    return itens


def _texto_pagina(cliente: httpx.Client, url: str) -> str:
    r = cliente.get(url)
    r.raise_for_status()
    corpo = re.sub(r"(?is)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", r.text)
    paragrafos = re.findall(r"(?is)<p[^>]*>(.*?)</p>", corpo)
    return _sem_tags(" ".join(paragrafos))[:4000]


@registrar("imprensa")
def coletar(data: str) -> list[Item]:
    itens = []
    with httpx.Client(timeout=30, follow_redirects=True, headers=UA) as cliente:
        for f in carregar_feeds():
            try:
                r = cliente.get(f["url"])
                r.raise_for_status()
                novos = parse_feed(f["veiculo"], f["secao"], r.content, data)
                if f["texto_completo"]:
                    for it in novos:
                        try:
                            it.extra["texto"] = _texto_pagina(cliente, it.url)
                        except httpx.HTTPError:
                            pass
                itens += novos
            except Exception as e:  # um feed ruim não derruba os outros
                print(f"imprensa: feed {f['veiculo']} falhou: {e}", file=sys.stderr)
    return itens
