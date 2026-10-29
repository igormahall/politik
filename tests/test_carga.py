from pathlib import Path

import yaml

from politik.__main__ import main
from tests.helpers import TEMA_OK, escrever_tema


def test_validar_tema_cli_sem_fonte(tmp_data):
    lt = [{"data": "2025-11-18", "fato": "x", "fontes": [], "fonte_unica": True}]
    escrever_tema(tmp_data, {**TEMA_OK, "linha_do_tempo": lt})
    assert main(["validar-tema", "--slug", "caso-master"]) == 1


def test_validar_tema_cli_ok(tmp_data):
    escrever_tema(tmp_data, TEMA_OK)
    assert main(["validar-tema", "--slug", "caso-master"]) == 0


def test_validar_tema_inexistente(tmp_data):
    assert main(["validar-tema", "--slug", "nao-existe"]) == 1


def test_skill_e_workflow_de_carga():
    skill = Path(".claude/skills/carga-tema/SKILL.md").read_text()
    assert "Edit(data/temas/**)" in skill and "WebFetch" in skill
    wf = yaml.safe_load(Path(".github/workflows/carga-tema.yml").read_text())
    assert set(wf[True]["workflow_dispatch"]["inputs"]) == {"slug", "nome", "descricao"}
