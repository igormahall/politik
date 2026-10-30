"""Contratos dos workflows do GitHub Actions, das skills do Claude e do guia editorial."""

import re
from pathlib import Path

import yaml


def test_skill_traduzir_manda_substituir_entradas_do_dia():
    assert "substitua" in Path(".claude/skills/traduzir/SKILL.md").read_text()


def _wf(nome):
    return yaml.safe_load(Path(f".github/workflows/{nome}").read_text())


def _passo(wf, job, nome):
    return next(s for s in wf["jobs"][job]["steps"] if s.get("name") == nome or s.get("id") == nome)


def test_carga_salva_progresso_parcial():
    wf = _wf("carga-tema.yml")
    assert _passo(wf, "carga", "claude").get("continue-on-error") is True
    assert "always()" in _passo(wf, "carga", "Validar tema").get("if", "")
    assert "always()" in _passo(wf, "carga", "Salvar tema").get("if", "")


def test_diario_push_resiliente_e_telegram_independente_do_pages():
    wf = _wf("diario.yml")
    assert "pull --rebase" in _passo(wf, "diario", "Salvar histórico")["run"]
    assert "steps.validar.outcome == 'success'" in _passo(wf, "diario", "Enviar no Telegram")["if"]
    assert _passo(wf, "diario", "deploy").get("continue-on-error") is True
    assert "INLABS_EMAIL" not in wf["jobs"]["diario"].get("env", {})
    assert "INLABS_EMAIL" in _passo(wf, "diario", "Coletar")["env"]


def test_claude_so_escreve_em_data():
    for nome, job in [("diario.yml", "diario"), ("carga-tema.yml", "carga")]:
        wf = _wf(nome)
        args = _passo(wf, job, "claude")["with"]["claude_args"]
        assert "Write" not in args and "Edit(data/" in args  # Edit(path) cobre Write
        checkout = wf["jobs"][job]["steps"][0]
        assert checkout["with"]["persist-credentials"] is False
    for skill in ["traduzir", "carga-tema"]:
        fm = Path(f".claude/skills/{skill}/SKILL.md").read_text().split("---")[1]
        assert "Edit(data/" in fm and "Write" not in fm


def test_skill_e_workflow_de_carga():
    skill = Path(".claude/skills/carga-tema/SKILL.md").read_text()
    assert "Edit(data/temas/**)" in skill and "WebFetch" in skill
    wf = yaml.safe_load(Path(".github/workflows/carga-tema.yml").read_text())
    assert set(wf[True]["workflow_dispatch"]["inputs"]) == {"slug", "nome", "descricao"}


def test_actions_fixadas_por_commit_e_dependabot():
    for wf in Path(".github/workflows").glob("*.yml"):
        for uses in re.findall(r"uses:\s*(\S+)", wf.read_text()):
            assert re.search(r"@[0-9a-f]{40}$", uses), f"{wf.name}: {uses} não está fixada por SHA"
    dep = yaml.safe_load(Path(".github/dependabot.yml").read_text())
    assert dep["updates"][0]["package-ecosystem"] == "github-actions"


def test_brutos_nao_vao_para_o_repositorio():
    assert "data/brutos/" in Path(".gitignore").read_text().splitlines()


def test_guia_tem_regras_de_titulo_e_importancia():
    guia = Path("editorial/GUIA.md").read_text()
    assert "sem número" in guia and "importancia" in guia
    assert '"importancia"' in Path(".claude/skills/traduzir/SKILL.md").read_text()


def test_carga_confirma_e_preenche_lacunas():
    skill = Path(".claude/skills/carga-tema/SKILL.md").read_text()
    assert "segunda fonte" in skill and "lacuna" in skill


def test_skill_e_guia_existem():
    from pathlib import Path

    skill = Path(".claude/skills/traduzir/SKILL.md").read_text()
    assert "Edit(data/**)" in skill and "editorial/GUIA.md" in skill
    assert "segundo apenas" in Path("editorial/GUIA.md").read_text()


def test_diario_tem_repescagem_que_nao_duplica():
    wf = _wf("diario.yml")
    crons = [c["cron"] for c in wf[True]["schedule"]]
    assert len(crons) == 2 and not any(c.startswith("0 ") for c in crons)  # minuto :00 é descartado sob carga
    assert wf["jobs"]["diario"]["needs"] == "checar"
    assert "data/diario/$D.json" in wf["jobs"]["checar"]["steps"][1]["run"]


def test_skill_traduzir_pede_campos_da_capa():
    skill = Path(".claude/skills/traduzir/SKILL.md").read_text()
    assert '"nome_curto"' in skill and '"linha_capa"' in skill
