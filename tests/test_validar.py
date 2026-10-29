from politik.__main__ import main
from politik.armazenamento import escrever_json, ler_json
from politik.temas import marcar_inativos
from tests.helpers import D, FICHA_OK, TEMA_OK, escrever_ficha, escrever_selecionados, escrever_tema, item


def test_validar_sem_diario_reenfileira(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1")])
    assert main(["validar", "--data", D]) == 0
    assert ler_json(tmp_data / f"diario/{D}.json")["sem_traducao"] is True
    pend = ler_json(tmp_data / "pendentes.json")
    assert [p["item"]["id"] for p in pend] == ["camara:1"] and pend[0]["primeira_vez"] == D


def test_validar_remove_ficha_invalida(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1"), item("camara:2")])
    escrever_ficha(tmp_data, FICHA_OK)
    escrever_ficha(tmp_data, {**FICHA_OK, "item_id": "camara:2", "fontes": []})
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": ["camara:1", "camara:2"]})
    main(["validar", "--data", D])
    assert not (tmp_data / "fichas/camara_2.json").exists()
    assert ler_json(tmp_data / f"diario/{D}.json")["fichas"] == ["camara:1"]
    assert [p["item"]["id"] for p in ler_json(tmp_data / "pendentes.json")] == ["camara:2"]


def test_validar_destaque_sem_ficha_volta_para_pendentes(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1"), item("camara:3")])
    escrever_ficha(tmp_data, FICHA_OK)
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": ["camara:1"]})
    main(["validar", "--data", D])
    assert [p["item"]["id"] for p in ler_json(tmp_data / "pendentes.json")] == ["camara:3"]


def test_validar_tema_invalido_sai_do_diario(tmp_data):
    escrever_selecionados(tmp_data, D)
    escrever_tema(tmp_data, {**TEMA_OK, "resumo_ate_aqui": ""})
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "fichas": [],
                  "temas": [{"slug": "caso-master", "novo_hoje": "x", "aviso_fonte_unica": None}]})
    main(["validar", "--data", D])
    assert ler_json(tmp_data / f"diario/{D}.json")["temas"] == []


def test_marcar_inativos(tmp_data):
    escrever_tema(tmp_data, {**TEMA_OK, "slug": "a", "ultima_novidade": "2026-09-01"})
    escrever_tema(tmp_data, {**TEMA_OK, "slug": "b", "ultima_novidade": "2026-10-20"})
    assert marcar_inativos("2026-10-28", 30) == ["a"]
    assert ler_json(tmp_data / "temas/a.json")["ativo"] is False
