"""Títulos objetivos, importância e votações agrupadas por projeto."""
import tomllib
from pathlib import Path

from politik.armazenamento import escrever_json
from politik.coletores.camara import agrupar_votacoes, parse_votacoes
from politik.esquemas import erros_ficha
from politik.filtro import classificar
from politik.telegram import compor
from tests.conftest import load
from tests.helpers import D, FICHA_OK, escrever_ficha, escrever_selecionados, item

CFG = tomllib.loads(Path("config/filtro.toml").read_text())


def test_votacoes_do_mesmo_projeto_viram_um_item():
    votos = parse_votacoes(load("camara_votacoes.json"), "2026-10-27")
    detalhe = load("camara_votacao_detalhe.json")["dados"]
    # todas apontando para o mesmo projeto
    grupos = agrupar_votacoes(votos, {v.id: detalhe for v in votos})
    assert len(grupos) == 1
    g = grupos[0]
    assert g.titulo == "PDL 274/2026" and g.ementa.startswith("Aprova o texto do Acordo")
    assert g.id == "camara:votacao:2620905:2026-10-27"
    assert len(g.extra["votacoes"]) == len(votos)
    assert g.url == "https://www.camara.leg.br/propostas-legislativas/2620905"


def test_votacao_sem_projeto_identificado_vira_menor():
    votos = parse_votacoes(load("camara_votacoes.json"), "2026-10-27")[:1]
    grupos = agrupar_votacoes(votos, {votos[0].id: {"proposicoesAfetadas": []}})
    assert grupos[0].extra["proposicao"] is None
    assert classificar(grupos[0], CFG, []) == "menor"


def test_importancia_opcional_mas_valida():
    assert erros_ficha({**FICHA_OK, "importancia": 1}) == []
    assert erros_ficha(FICHA_OK) == []  # fichas antigas continuam válidas
    assert erros_ficha({**FICHA_OK, "importancia": 5})
    assert erros_ficha({**FICHA_OK, "importancia": "alta"})


def _feed(tmp_data, fichas):
    escrever_selecionados(tmp_data, D, destaques=[item(f["item_id"]) for f in fichas])
    for f in fichas:
        escrever_ficha(tmp_data, f)
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": [f["item_id"] for f in fichas]})
    return "\n".join(m["text"] for m in compor(D, "https://x"))


def test_feed_abre_com_mais_importantes_e_ordena(tmp_data):
    t = _feed(tmp_data, [
        {**FICHA_OK, "item_id": "camara:1", "titulo": "Baixa federal", "importancia": 3},
        {**FICHA_OK, "item_id": "cmm:materia:2", "nivel": "municipal", "titulo": "Alta Manaus", "importancia": 1},
        {**FICHA_OK, "item_id": "camara:3", "titulo": "Média federal", "importancia": 2},
        {**FICHA_OK, "item_id": "camara:4", "titulo": "Sem nota"},
    ])
    assert t.index("⭐ Mais importantes") < t.index("Alta Manaus") < t.index("🇧🇷 Federal")
    assert t.index("Média federal") < t.index("Sem nota") < t.index("Baixa federal")
    assert t.count("Alta Manaus") == 1  # não repete no grupo do nível


def test_cabecalho_sem_contagem_protocolar(tmp_data):
    t = _feed(tmp_data, [FICHA_OK])
    assert "em destaque" not in t and "itens ·" not in t
    assert t.startswith("📋 <b>Politik — quarta, 28/out</b>")


def test_guia_tem_regras_de_titulo_e_importancia():
    guia = Path("editorial/GUIA.md").read_text()
    assert "sem número" in guia and "importancia" in guia
    assert '"importancia"' in Path(".claude/skills/traduzir/SKILL.md").read_text()


def test_carga_confirma_e_preenche_lacunas():
    skill = Path(".claude/skills/carga-tema/SKILL.md").read_text()
    assert "segunda fonte" in skill and "lacuna" in skill
