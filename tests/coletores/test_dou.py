import io
import zipfile

import httpx
import pytest

from politik.coletores import FonteIndisponivel
from politik.coletores.dou import coletar, parse_artigo
from tests.conftest import load_bytes


def test_parse_artigo_lei():
    it = parse_artigo(load_bytes("dou_artigo.xml"))
    assert it.id == "dou:12345678" and it.categoria == "norma" and it.nivel == "federal"
    assert it.sigla_tipo == "LEI"
    assert it.titulo == "LEI Nº 15.999, DE 27 DE OUTUBRO DE 2026"
    assert it.ementa.startswith("Altera a Lei nº 8.036")
    assert it.data == "2026-10-28"
    assert it.extra["orgao"] == "Atos do Poder Legislativo"


def test_parse_sem_ementa_usa_texto_sem_tags():
    it = parse_artigo(load_bytes("dou_portaria_sem_ementa.xml"))
    assert it.sigla_tipo == "PORTARIA"
    assert it.ementa.startswith("O MINISTRO DE ESTADO resolve: Art. 1º")
    assert "<" not in it.ementa


def test_tipo_normalizado_sem_acento():
    xml = load_bytes("dou_artigo.xml").replace(b'artType="Lei"', 'artType="Medida Provisória"'.encode())
    assert parse_artigo(xml).sigla_tipo == "MEDIDA PROVISORIA"


def test_sem_id_materia_retorna_none():
    assert parse_artigo(load_bytes("dou_artigo.xml").replace(b'idMateria="12345678"', b"")) is None


ZIP_DO_MES = "https://www.in.gov.br/documents/1/2/S01102026_Atualizado175048.zip/abc?version=1.0&download=true"


def _zip_do_mes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("20261028/DO1/lei.xml", load_bytes("dou_artigo.xml"))
        z.writestr("20261028/DO1E/mp.xml", load_bytes("dou_artigo.xml").replace(b"12345678", b"87654321"))
        z.writestr("20261027/DO1/outro_dia.xml", load_bytes("dou_artigo.xml").replace(b"12345678", b"11111111"))
    return buf.getvalue()


def _base_aberta(listagem: str | None = None, pedidos: list | None = None) -> httpx.Client:
    if listagem is None:
        listagem = f'<a href="{ZIP_DO_MES.replace("&", "&amp;")}">S01102026</a>'

    def h(r: httpx.Request) -> httpx.Response:
        if pedidos is not None:
            pedidos.append(r)
        if r.url.path.endswith("/base-de-dados"):
            return httpx.Response(200, text=listagem)
        if r.url.path.startswith("/documents/"):
            return httpx.Response(200, content=_zip_do_mes())
        return httpx.Response(404)

    return httpx.Client(transport=httpx.MockTransport(h))


@pytest.fixture
def sem_inlabs(monkeypatch):
    monkeypatch.delenv("INLABS_EMAIL", raising=False)
    monkeypatch.delenv("INLABS_SENHA", raising=False)


def test_sem_inlabs_usa_a_base_aberta_so_com_o_dia(sem_inlabs):
    pedidos = []
    itens = coletar("2026-10-28", base_aberta=_base_aberta(pedidos=pedidos))
    assert sorted(i.id for i in itens) == ["dou:12345678", "dou:87654321"]  # edição normal e extra; 27/10 fica fora
    assert pedidos[0].url.params["ano"] == "2026" and pedidos[0].url.params["mes"] == "Outubro"
    assert str(pedidos[1].url) == ZIP_DO_MES


def _legislacao(por_dia: dict | None = None, status: int = 200, pedidos: list | None = None) -> httpx.Client:
    """Imita a API de legislação do Senado: {"AAAAMMDD": [documentos]}."""

    def h(r: httpx.Request) -> httpx.Response:
        if pedidos is not None:
            pedidos.append(r)
        if status != 200:
            return httpx.Response(status)
        if r.url.path.endswith("/lista"):
            docs = (por_dia or {}).get(r.url.params["data"], [])
            return httpx.Response(200, json={"ListaDocumento": {"documentos": {"documento": docs} if docs else ""}})
        cod = r.url.path.rsplit("/", 1)[1]
        ident = {"urlDocumento": f"https://normas.leg.br/?urn=x;{cod}"}
        return httpx.Response(200, json={"DetalheDocumento": {"documentos": {"documento": [{"identificacao": ident}]}}})

    return httpx.Client(transport=httpx.MockTransport(h))


def _norma(cod, tipo="LEI-n", nome="Lei nº 15.555 de 26/11/2026", ementa="Altera o Estatuto da Criança."):
    return {
        "id": cod,
        "tipo": tipo,
        "descricao": "Lei Numerada",
        "normaNome": nome,
        "ementa": ementa,
        "dataassinatura": "26/11/2026",
    }


def test_base_aberta_ainda_sem_o_dia(sem_inlabs):
    with pytest.raises(FonteIndisponivel, match="2026-10-29"):
        coletar("2026-10-29", base_aberta=_base_aberta(), legislacao=_legislacao(status=502))


def test_base_aberta_sem_o_arquivo_do_mes(sem_inlabs):
    with pytest.raises(FonteIndisponivel, match="INLABS sem credenciais"):
        coletar("2026-10-28", base_aberta=_base_aberta(listagem="<p>nada</p>"), legislacao=_legislacao(status=502))


def test_sem_inlabs_e_sem_base_aberta_usa_a_legislacao_do_senado(sem_inlabs, tmp_data):
    # 20–27/11/2026: INLABS em manutenção e base aberta com 502; o DOU sumiu do boletim por uma semana
    por_dia = {
        "20261126": [_norma("1"), _norma("2", tipo="DEC-n", nome="Decreto nº 13.175 de 26/11/2026")],
        "20261124": [_norma("3", tipo="LCP", nome="Lei Complementar nº 239 de 24/11/2026")],
    }
    itens = coletar("2026-11-26", base_aberta=_base_aberta(listagem="<p>nada</p>"), legislacao=_legislacao(por_dia))
    assert [i.id for i in itens] == ["dou:leg:1", "dou:leg:2", "dou:leg:3"]  # a janela pega o que entrou atrasado
    assert [i.sigla_tipo for i in itens] == ["LEI", "DECRETO", "LEI COMPLEMENTAR"]
    assert all(i.fonte == "dou" and i.categoria == "norma" and i.data == "2026-11-26" for i in itens)
    assert itens[0].url == "https://normas.leg.br/?urn=x;1"


def test_legislacao_nao_repete_norma_de_boletim_anterior(sem_inlabs, tmp_data):
    from politik.armazenamento import escrever_json

    escrever_json(tmp_data / "selecionados" / "2026-11-25.json", {"destaques": [{"id": "dou:leg:3"}], "menores": []})
    por_dia = {"20261126": [_norma("1")], "20261124": [_norma("3", tipo="LCP")]}
    itens = coletar("2026-11-26", base_aberta=_base_aberta(listagem="<p>nada</p>"), legislacao=_legislacao(por_dia))
    assert [i.id for i in itens] == ["dou:leg:1"]


def test_legislacao_sem_normas_no_periodo_nao_e_falha(sem_inlabs, tmp_data):
    assert coletar("2026-11-22", base_aberta=_base_aberta(listagem="<p>nada</p>"), legislacao=_legislacao({})) == []
