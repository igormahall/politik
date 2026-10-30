from politik.__main__ import main
from politik.armazenamento import escrever_json, ler_json
from politik.temas import marcar_inativos
from tests.helpers import (
    D,
    escrever_ficha,
    escrever_mundo,
    escrever_selecionados,
    escrever_tema,
    FICHA_OK,
    item,
    MUNDO_OK,
    TEMA_OK,
)


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
    escrever_json(
        tmp_data / f"diario/{D}.json",
        {"data": D, "fichas": [], "temas": [{"slug": "caso-master", "novo_hoje": "x", "aviso_fonte_unica": None}]},
    )
    main(["validar", "--data", D])
    assert ler_json(tmp_data / f"diario/{D}.json")["temas"] == []


def test_marcar_inativos(tmp_data):
    escrever_tema(tmp_data, {**TEMA_OK, "slug": "a", "ultima_novidade": "2026-09-01"})
    escrever_tema(tmp_data, {**TEMA_OK, "slug": "b", "ultima_novidade": "2026-10-20"})
    assert marcar_inativos("2026-10-28", 30) == ["a"]
    assert ler_json(tmp_data / "temas/a.json")["ativo"] is False


def test_capa_invalida_nao_derruba_o_diario(tmp_data):
    escrever_selecionados(tmp_data, D)
    escrever_tema(tmp_data, TEMA_OK)
    tema = {"slug": "caso-master", "novo_hoje": "x", "aviso_fonte_unica": None, "nome_curto": "", "linha_capa": "ok"}
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "fichas": [], "temas": [tema]})
    main(["validar", "--data", D])
    diario = ler_json(tmp_data / f"diario/{D}.json")
    assert "sem_traducao" not in diario and "parcial" not in diario
    assert "nome_curto" not in diario["temas"][0] and diario["temas"][0]["linha_capa"] == "ok"


def _coletados_do_mundo():
    mundo = [
        item(f"mundo:x:{i}", url=f["url"], categoria="mundo", nivel="mundo") for i, f in enumerate(MUNDO_OK["fontes"])
    ]
    noticias = [item("imprensa:ab:1", categoria="noticia", url=MUNDO_OK["fontes_impacto"][0]["url"])]
    return mundo, noticias


def test_validar_remove_mundo_invalido_e_mantem_diario(tmp_data):
    mundo, noticias = _coletados_do_mundo()
    escrever_selecionados(tmp_data, D, mundo=mundo, noticias=noticias)
    escrever_mundo(tmp_data, MUNDO_OK)
    ruim = {
        **MUNDO_OK,
        "item_id": "mundo:2026-10-28:2",
        "fontes": [*MUNDO_OK["fontes"][:1], {"nome": "DW", "url": "https://www.dw.com/inventada"}],
    }
    escrever_mundo(tmp_data, ruim)
    escrever_json(
        tmp_data / f"diario/{D}.json",
        {"data": D, "temas": [], "fichas": [], "mundo": [MUNDO_OK["item_id"], ruim["item_id"]]},
    )
    main(["validar", "--data", D])
    diario = ler_json(tmp_data / f"diario/{D}.json")
    assert diario["mundo"] == [MUNDO_OK["item_id"]]
    assert not (tmp_data / "mundo/mundo_2026-10-28_2.json").exists()
    assert "sem_traducao" not in diario


def test_validar_limita_mundo_a_cinco(tmp_data):
    mundo, noticias = _coletados_do_mundo()
    escrever_selecionados(tmp_data, D, mundo=mundo, noticias=noticias)
    ids = []
    for n in range(7):
        f = {**MUNDO_OK, "item_id": f"mundo:2026-10-28:{n}"}
        escrever_mundo(tmp_data, f)
        ids.append(f["item_id"])
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": [], "mundo": ids})
    main(["validar", "--data", D])
    assert ler_json(tmp_data / f"diario/{D}.json")["mundo"] == ids[:5]


def test_validar_diario_sem_mundo_continua_igual(tmp_data):
    escrever_selecionados(tmp_data, D)
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": []})
    main(["validar", "--data", D])
    assert "mundo" not in ler_json(tmp_data / f"diario/{D}.json")


def _sel_e_diario(tmp_data, diario_extra=None):
    mundo, noticias = _coletados_do_mundo()
    escrever_selecionados(tmp_data, D, mundo=mundo, noticias=noticias)
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": [], **(diario_extra or {})})


def test_validar_mundo_url_que_nao_e_texto_nao_derruba(tmp_data):
    _sel_e_diario(tmp_data, {"mundo": [MUNDO_OK["item_id"]]})
    ruim = {**MUNDO_OK, "fontes": [{"nome": "BBC", "url": ["https://www.bbc.com/a"]}, MUNDO_OK["fontes"][1]]}
    escrever_mundo(tmp_data, ruim)
    assert main(["validar", "--data", D]) == 0
    assert not (tmp_data / "mundo/mundo_2026-10-28_1.json").exists()


def test_validar_mundo_sem_chave_no_diario_ainda_confere(tmp_data):
    _sel_e_diario(tmp_data)  # o Claude escreveu a ficha e parou antes do diário
    inventada = {
        **MUNDO_OK,
        "fontes": [{"nome": "BBC", "url": "https://www.bbc.com/x"}, {"nome": "DW", "url": "https://www.dw.com/y"}],
    }
    escrever_mundo(tmp_data, inventada)
    main(["validar", "--data", D])
    assert not (tmp_data / "mundo/mundo_2026-10-28_1.json").exists()
    assert "mundo" not in ler_json(tmp_data / f"diario/{D}.json")


def test_validar_mundo_id_diferente_do_arquivo_sai(tmp_data):
    _sel_e_diario(tmp_data, {"mundo": [MUNDO_OK["item_id"]]})
    escrever_json(tmp_data / "mundo/outro_nome.json", MUNDO_OK)
    main(["validar", "--data", D])
    assert not (tmp_data / "mundo/outro_nome.json").exists()
    assert ler_json(tmp_data / f"diario/{D}.json")["mundo"] == []


def test_validar_mundo_de_outro_dia_nao_commitado_sai(tmp_data):
    _sel_e_diario(tmp_data)
    escrever_mundo(tmp_data, {**MUNDO_OK, "item_id": "mundo:2026-10-27:1", "data": "2026-10-27"})
    main(["validar", "--data", D])
    assert not (tmp_data / "mundo/mundo_2026-10-27_1.json").exists()


def test_validar_restaura_diario_de_outro_dia_e_tema_que_perdeu_a_marca(tmp_data, monkeypatch):
    import json

    from politik import validar as v

    antigo = {"data": "2026-10-27", "temas": [], "fichas": []}
    tema_commitado = {
        **TEMA_OK,
        "internacional": True,
        "linha_do_tempo": [
            {
                **TEMA_OK["linha_do_tempo"][0],
                "fontes": [
                    {"nome": "BBC", "url": "https://www.bbc.com/a"},
                    {"nome": "DW", "url": "https://www.dw.com/b"},
                ],
            }
        ],
    }
    commitados = {"diario/2026-10-27.json": antigo, "temas/caso-master.json": tema_commitado}

    def commitado(caminho):
        for fim, conteudo in commitados.items():
            if str(caminho).endswith(fim):
                return json.dumps(conteudo).encode()
        return None

    monkeypatch.setattr(v, "_versao_commitada", commitado)
    _sel_e_diario(tmp_data)
    escrever_json(tmp_data / "diario/2026-10-27.json", {**antigo, "mundo": ["mundo:2026-10-27:9"]})
    escrever_tema(tmp_data, TEMA_OK)  # o Claude tirou "internacional" e deixou uma fonte só
    main(["validar", "--data", D])
    assert ler_json(tmp_data / "diario/2026-10-27.json") == antigo
    assert ler_json(tmp_data / "temas/caso-master.json")["internacional"] is True
