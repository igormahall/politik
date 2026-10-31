import io
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from html import unescape
from urllib.parse import urljoin

import httpx

from politik.coletores import FonteIndisponivel, registrar
from politik.modelos import Item

URL_LOGIN = "https://inlabs.in.gov.br/logar.php"
URL_DOWNLOAD = "https://inlabs.in.gov.br/index.php?p={data}&dl={data}-DO1.zip"
# reserva: a base aberta da Imprensa Nacional (um zip por mês e seção; durante a manutenção do INLABS
# em outubro de 2026, atualizado todo dia)
URL_BASE_ABERTA = "https://www.in.gov.br/acesso-a-informacao/dados-abertos/base-de-dados"
MESES = "Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro".split()


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


def _ler_zip(conteudo: bytes, pasta: str = "") -> list[Item]:
    itens = []
    with zipfile.ZipFile(io.BytesIO(conteudo)) as z:
        for nome in z.namelist():
            if nome.startswith(pasta) and nome.lower().endswith(".xml"):
                it = parse_artigo(z.read(nome))
                if it:
                    itens.append(it)
    return itens


def _do_inlabs(data: str) -> list[Item]:
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
    return _ler_zip(r.content)


def _da_base_aberta(data: str, cliente: httpx.Client) -> list[Item]:
    ano, mes, dia = data.split("-")
    with cliente:
        pagina = cliente.get(URL_BASE_ABERTA, params={"ano": ano, "mes": MESES[int(mes) - 1]})
        pagina.raise_for_status()
        links = re.findall(rf'href="([^"]*/S01{mes}{ano}[^"/]*\.zip[^"]*)"', pagina.text)
        if not links:
            raise FonteIndisponivel(f"base aberta sem o arquivo de {mes}/{ano}")
        r = cliente.get(urljoin(URL_BASE_ABERTA, unescape(links[0])))
        r.raise_for_status()
    # a seção 1 do mês inteiro vem num zip só, com uma pasta por dia (edição normal e extras)
    itens = _ler_zip(r.content, pasta=f"{ano}{mes}{dia}/")
    if not itens:
        raise FonteIndisponivel(f"base aberta ainda sem {data}")
    return itens


@registrar("dou")
def coletar(data: str, base_aberta: httpx.Client | None = None) -> list[Item]:
    try:
        return _do_inlabs(data)
    except (FonteIndisponivel, httpx.HTTPError, zipfile.BadZipFile) as e:
        falha_inlabs = e
    cliente = base_aberta or httpx.Client(timeout=300, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
    try:
        return _da_base_aberta(data, cliente)
    except (FonteIndisponivel, httpx.HTTPError, zipfile.BadZipFile) as e:
        raise FonteIndisponivel(f"{falha_inlabs}; {e}") from e
