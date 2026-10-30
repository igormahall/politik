from politik.esquemas import erros_diario, erros_ficha, erros_tema
from tests.conftest import load


def test_exemplos_seguem_esquema():
    assert erros_ficha(load("exemplo_saida/ficha.json")) == []
    assert erros_tema(load("exemplo_saida/tema.json")) == []
    assert erros_diario(load("exemplo_saida/diario.json")) == []
