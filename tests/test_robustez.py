"""Robustez do pipeline: arquivos corrompidos, falhas do Claude, fila de pendentes, esquemas."""

from politik.__main__ import main
from politik.armazenamento import escrever_json, ler_json
from politik.coletores.tramitacao import acompanhados
from politik.esquemas import erros_diario, erros_ficha, erros_tema
from politik.filtro import filtrar
from politik.site.gerador import gerar
from politik.telegram import compor
from politik.temas import carregar_temas
from tests.helpers import CFG, D, escrever_ficha, escrever_selecionados, escrever_tema, FICHA_OK, item, TEMA_OK


# --- C1
def test_acompanhados_ignora_fichas_de_tramitacao(tmp_data):
    for iid in ["camara:1", "camara:1:tram:5", "senado:2", "senado:2:sit:2026-10-01"]:
        escrever_ficha(tmp_data, {**FICHA_OK, "item_id": iid, "data": "2026-10-20"})
    assert acompanhados("2026-10-28") == ["camara:1", "senado:2"]


# --- C2
def test_diario_corrompido_cai_no_modo_sem_traducao(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1")])
    (tmp_data / "diario").mkdir()
    (tmp_data / f"diario/{D}.json").write_text('{"data": "2026-10-28", "fichas": [')
    assert main(["validar", "--data", D]) == 0
    assert ler_json(tmp_data / f"diario/{D}.json")["sem_traducao"] is True


def test_tema_corrompido_fora_do_diario_e_removido_e_ignorado(tmp_data):
    escrever_selecionados(tmp_data, D)
    escrever_tema(tmp_data, TEMA_OK)
    (tmp_data / "temas/quebrado.json").write_text('{"slug": "quebrado",')
    assert [t["slug"] for t in carregar_temas()] == ["caso-master"]
    main(["validar", "--data", D])
    assert not (tmp_data / "temas/quebrado.json").exists()


def test_ficha_corrompida_fora_do_diario_e_removida(tmp_data):
    escrever_selecionados(tmp_data, D)
    (tmp_data / "fichas").mkdir()
    (tmp_data / "fichas/camara_7.json").write_text("{")
    escrever_ficha(tmp_data, {**FICHA_OK, "item_id": "camara:8", "explica": 1, "titulo": ""})
    main(["validar", "--data", D])
    assert not (tmp_data / "fichas/camara_7.json").exists()
    assert not (tmp_data / "fichas/camara_8.json").exists()


def test_site_nao_quebra_com_arquivo_corrompido(tmp_data, tmp_path):
    (tmp_data / "fichas").mkdir()
    (tmp_data / "fichas/x.json").write_text("{")
    gerar(tmp_path / "s", "https://x")
    assert (tmp_path / "s/arquivo.html").exists()


# --- I1
def test_primeira_vez_sobrevive_quando_traducao_falha(tmp_data):
    pend = [{"item": item("camara:x").to_dict(), "primeira_vez": "2026-10-25"}]
    sel, novos = filtrar("2026-10-26", [], pend, CFG, [])
    assert sel["primeira_vez"] == {"camara:x": "2026-10-25"}
    sel["destaques"] = [i.to_dict() for i in sel["destaques"]]
    escrever_json(tmp_data / "selecionados/2026-10-26.json", sel)
    escrever_json(tmp_data / "pendentes.json", novos)
    main(["validar", "--data", "2026-10-26"])
    assert ler_json(tmp_data / "pendentes.json")[0]["primeira_vez"] == "2026-10-25"


# --- I2
def test_sem_traducao_mostra_ementa_original(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1", ementa="Altera a Lei 8.036 sobre o <FGTS>")])
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": [], "sem_traducao": True})
    texto = "\n".join(m["text"] for m in compor(D, "https://x"))
    assert "Altera a Lei 8.036 sobre o &lt;FGTS&gt;" in texto


# --- I3
def test_sem_diario_aproveita_fichas_validas_do_dia(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1"), item("camara:2")])
    escrever_ficha(tmp_data, FICHA_OK)  # camara:1, data D
    main(["validar", "--data", D])
    diario = ler_json(tmp_data / f"diario/{D}.json")
    assert diario["fichas"] == ["camara:1"] and diario.get("parcial") is True
    assert [p["item"]["id"] for p in ler_json(tmp_data / "pendentes.json")] == ["camara:2"]
    texto = "\n".join(m["text"] for m in compor(D, "https://x"))
    assert "Tradução parcial hoje" in texto and "Muda o saque do FGTS" in texto


# --- I5
def test_tema_com_fato_repetido_e_invalido():
    lt = TEMA_OK["linha_do_tempo"] * 2
    assert any("repetido" in e for e in erros_tema({**TEMA_OK, "linha_do_tempo": lt}))


# --- I8
def test_esquema_datas_e_tipos():
    assert erros_tema({**TEMA_OK, "inicio": "18/11/2025"})
    assert erros_tema({**TEMA_OK, "linha_do_tempo": ["texto solto"]})
    assert erros_ficha({**FICHA_OK, "data": "ontem"})
    assert erros_diario(
        {"data": D, "fichas": [], "temas": [{"slug": "a", "novo_hoje": "x", "aviso_fonte_unica": True}]}
    )
    assert erros_diario({"data": D, "fichas": [], "temas": ["a"]})


# --- Workflows (I4, I6, I7)
