import io
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from html import unescape

import httpx

from politik.coletores import FonteIndisponivel, registrar
from politik.modelos import Item

URL_LOGIN = "https://inlabs.in.gov.br/logar.php"
URL_DOWNLOAD = "https://inlabs.in.gov.br/index.php?p={data}&dl={data}-DO1.zip"


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _sem_tags(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def parse_artigo(xml: bytes) -> Item | None:
    raiz = ET.fromstring(xml)
    art = raiz if raiz.tag == "article" else raiz.find("article")
    if art is None or not art.get("idMateria"):
        return None
    corpo = art.find("body")

    def texto(tag: str) -> str:
        return (corpo.findtext(tag) or "").strip() if corpo is not None else ""

    dia, mes, ano = art.get("pubDate", "").split("/")
    ementa = texto("Ementa") or _sem_tags(texto("Texto"))[:300]
    return Item(
        id=f"dou:{art.get('idMateria')}",
        fonte="dou",
        nivel="federal",
        categoria="norma",
        sigla_tipo=_sem_acento(art.get("artType", "")).upper(),
        titulo=texto("Identifica") or art.get("name", ""),
        ementa=ementa,
        data=f"{ano}-{mes}-{dia}",
        url=art.get("pdfPage") or "https://www.in.gov.br/leiturajornal",
        extra={"orgao": art.get("artCategory", "")},
    )


@registrar("dou")
def coletar(data: str) -> list[Item]:
    email, senha = os.environ.get("INLABS_EMAIL"), os.environ.get("INLABS_SENHA")
    if not email or not senha:
        raise FonteIndisponivel("INLABS sem credenciais")
    with httpx.Client(timeout=120, follow_redirects=True) as s:
        s.post(URL_LOGIN, data={"email": email, "password": senha})
        cookie = s.cookies.get("inlabs_session_cookie")
        if not cookie:
            raise FonteIndisponivel("INLABS: login falhou")
        r = s.get(URL_DOWNLOAD.format(data=data), headers={"origem": "736372697074"})
        if r.status_code == 404:
            return []
        r.raise_for_status()
    itens = []
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for nome in z.namelist():
            if nome.lower().endswith(".xml"):
                it = parse_artigo(z.read(nome))
                if it:
                    itens.append(it)
    return itens
