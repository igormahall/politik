from politik.coletores.senado import parse_processos
from politik.modelos import Autor
from tests.conftest import load

BASE = load("senado_processo.json")[0]


def test_parse_autoria_com_partido():
    it = parse_processos([{**BASE, "autoria": "Senadora Damares Alves (REPUBLICANOS/DF)"}])[0]
    assert it.autores == [Autor("Damares Alves", "REPUBLICANOS", "DF")]


def test_parse_varios_autores():
    it = parse_processos([{**BASE, "autoria": "Senador Jorge Seif (PL/SC), Senadora Damares Alves (REPUBLICANOS/DF)"}])[
        0
    ]
    assert it.autores == [Autor("Jorge Seif", "PL", "SC"), Autor("Damares Alves", "REPUBLICANOS", "DF")]


def test_parse_autoria_sem_partido():
    it = parse_processos([{**BASE, "autoria": "Câmara dos Deputados"}])[0]
    assert it.autores == [Autor("Câmara dos Deputados")]


def test_sigla_tipo_e_campos():
    it = parse_processos([{**BASE, "identificacao": "PL 123/2026"}])[0]
    assert it.sigla_tipo == "PL" and it.titulo == "PL 123/2026"
    assert it.id == f"senado:{BASE['id']}" and it.nivel == "federal"
    assert it.url.endswith(f"/materia/{BASE['codigoMateria']}")
    assert it.extra["situacaoAtual"] == BASE["situacaoAtual"]
