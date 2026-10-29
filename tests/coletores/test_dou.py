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


def test_sem_credenciais(monkeypatch):
    monkeypatch.delenv("INLABS_EMAIL", raising=False)
    monkeypatch.delenv("INLABS_SENHA", raising=False)
    with pytest.raises(FonteIndisponivel):
        coletar("2026-10-28")
