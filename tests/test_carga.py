from politik.__main__ import main
from tests.helpers import escrever_tema, TEMA_OK


def test_validar_tema_cli_sem_fonte(tmp_data):
    lt = [{"data": "2025-11-18", "fato": "x", "fontes": [], "fonte_unica": True}]
    escrever_tema(tmp_data, {**TEMA_OK, "linha_do_tempo": lt})
    assert main(["validar-tema", "--slug", "caso-master"]) == 1


def test_validar_tema_cli_ok(tmp_data):
    escrever_tema(tmp_data, TEMA_OK)
    assert main(["validar-tema", "--slug", "caso-master"]) == 0


def test_validar_tema_inexistente(tmp_data):
    assert main(["validar-tema", "--slug", "nao-existe"]) == 1
