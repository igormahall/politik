import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load(nome):
    return json.loads((FIXTURES / nome).read_text(encoding="utf-8"))


def load_bytes(nome):
    return (FIXTURES / nome).read_bytes()


@pytest.fixture
def tmp_data(tmp_path, monkeypatch):
    d = tmp_path / "data"
    d.mkdir()
    monkeypatch.setenv("POLITIK_DATA", str(d))
    return d
