from politik.esquemas import erros_diario, erros_ficha, erros_tema
from tests.conftest import load


def test_exemplos_seguem_esquema():
    assert erros_ficha(load("exemplo_saida/ficha.json")) == []
    assert erros_tema(load("exemplo_saida/tema.json")) == []
    assert erros_diario(load("exemplo_saida/diario.json")) == []


def test_skill_e_guia_existem():
    from pathlib import Path
    skill = Path(".claude/skills/traduzir/SKILL.md").read_text()
    assert "allowed-tools: Read, Write, Edit, Glob" in skill and "editorial/GUIA.md" in skill
    assert "segundo apenas" in Path("editorial/GUIA.md").read_text()
