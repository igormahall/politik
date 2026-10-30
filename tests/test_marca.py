"""Identidade visual (direção B, Encontro das Águas) aplicada ao site e aos arquivos da marca."""

from pathlib import Path

from politik.armazenamento import escrever_json
from politik.site.gerador import gerar
from tests.helpers import D

SLOGAN = "Os fatos lado a lado."


def test_arquivos_da_marca_existem():
    for nome in ["simbolo.svg", "logo.svg", "marca-dagua.svg", "avatar-512.png", "README.md"]:
        assert (Path("marca") / nome).exists(), nome


def test_favicon_do_site_e_o_simbolo_oficial():
    assert Path("politik/site/favicon.svg").read_text() == Path("marca/simbolo.svg").read_text()


def test_site_usa_a_marca(tmp_data, tmp_path):
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": []})
    gerar(tmp_path, "https://x")
    html = (tmp_path / "index.html").read_text()
    assert 'rel="icon"' in html and "favicon.svg" in html
    assert SLOGAN in html
    assert (tmp_path / "favicon.svg").exists()
    css = (tmp_path / "estilo.css").read_text()
    assert "--rio-negro: #2a1f1a" in css and "--solimoes: #c9a266" in css
    assert "Bricolage Grotesque" in css and "Source Sans 3" in css


def test_simbolo_para_fundo_escuro_tem_contorno_claro():
    svg = Path("marca/simbolo-contorno.svg").read_text()
    assert 'stroke="#f4efe7"' in svg
    assert Path("politik/site/simbolo-contorno.svg").read_text() == svg


def test_topo_escuro_usa_simbolo_com_contorno(tmp_data, tmp_path):
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": []})
    gerar(tmp_path, "https://x")
    assert 'src="https://x/simbolo-contorno.svg"' in (tmp_path / "index.html").read_text()
    assert (tmp_path / "simbolo-contorno.svg").exists()


def test_datas_por_extenso(tmp_data, tmp_path):
    from politik.site.gerador import data_br

    assert data_br("2026-10-28") == "quarta-feira, 28 de outubro de 2026"
    assert data_br("2026-10-28", curta=True) == "28/10/2026"
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": []})
    gerar(tmp_path, "https://x")
    assert "quarta-feira, 28 de outubro de 2026" in (tmp_path / "index.html").read_text()
