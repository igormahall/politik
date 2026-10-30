import json

from politik.__main__ import main

D = "2026-10-28"


def _ultima(tmp_data):
    return json.loads((tmp_data / "uso.jsonl").read_text().splitlines()[-1])


def test_registrar_uso(tmp_data, tmp_path):
    f = tmp_path / "exec.json"
    f.write_text(
        json.dumps([{"type": "system"}, {"type": "result", "num_turns": 12, "duration_ms": 9000, "is_error": False}])
    )
    assert main(["registrar-uso", "--arquivo", str(f), "--data", D]) == 0
    assert _ultima(tmp_data) == {"data": D, "num_turns": 12, "duration_ms": 9000, "sucesso": True}


def test_registrar_uso_sem_arquivo(tmp_data):
    main(["registrar-uso", "--arquivo", "/nao/existe", "--data", D])
    assert _ultima(tmp_data)["sucesso"] is False


def test_registrar_uso_arquivo_vazio_string(tmp_data):
    main(["registrar-uso", "--arquivo", "", "--data", D])
    assert _ultima(tmp_data)["sucesso"] is False
