from politik.armazenamento import escrever_json
from politik.carrossel.conteudo import montar
from tests.helpers import D, escrever_ficha, escrever_tema, FICHA_OK, TEMA_OK


def _diario(d, temas=(), fichas=(), **extra):
    escrever_json(d / f"diario/{D}.json", {"data": D, "temas": list(temas), "fichas": list(fichas), **extra})


def _tema_do_dia(slug, **extra):
    return {"slug": slug, "novo_hoje": f"Novidade de {slug}.", "aviso_fonte_unica": None, **extra}


def _ficha(d, iid, nivel="federal", importancia=2, **extra):
    escrever_ficha(d, {**FICHA_OK, "item_id": iid, "nivel": nivel, "importancia": importancia, **extra})
    return iid


def test_montar_dia_normal(tmp_data):
    escrever_tema(tmp_data, TEMA_OK)
    escrever_tema(tmp_data, {**TEMA_OK, "slug": "outro", "nome": "Outro tema"})
    fichas = [
        _ficha(tmp_data, "camara:1", importancia=1),
        _ficha(tmp_data, "aleam:materia:5", "estadual"),
        _ficha(tmp_data, "camara:3", importancia=3),
    ]
    _diario(
        tmp_data,
        [
            _tema_do_dia("caso-master", nome_curto="Caso Master", linha_capa="Fachin mantém o caso no STF"),
            _tema_do_dia("outro"),
        ],
        fichas,
    )
    m = montar(D)
    assert m["data_extenso"] == "quarta-feira, 28 de outubro de 2026"
    assert m["capa"]["temas"][0] == {"nome": "Caso Master", "linha": "Fachin mantém o caso no STF"}
    assert m["capa"]["temas"][1] == {"nome": "Outro tema", "linha": None}
    assert [g["nivel"] for g in m["fichas"]["grupos"]] == ["Federal", "Amazonas"]
    assert m["capa"]["mais"] == 2 and m["fichas"]["mais"] == 0
    assert m["temas"][1]["novo_hoje"] == "Novidade de outro." and m["temas"][0]["para_entender"] == "Resumo."
    assert m["total"] == 1 + 2 + 1 + 1


def test_etiqueta_conta_dias_e_vira_desde_depois_de_60(tmp_data):
    escrever_tema(tmp_data, {**TEMA_OK, "inicio": D})
    escrever_tema(tmp_data, {**TEMA_OK, "slug": "velho", "inicio": "2025-03-28"})
    _diario(tmp_data, [_tema_do_dia("caso-master"), _tema_do_dia("velho")])
    temas = montar(D)["temas"]
    assert temas[0]["etiqueta"] == "Tema em andamento · dia 1"
    assert temas[1]["etiqueta"] == "Tema em andamento · desde mar/2025"


def test_aviso_fonte_unica_vai_para_o_slide(tmp_data):
    escrever_tema(tmp_data, TEMA_OK)
    _diario(tmp_data, [_tema_do_dia("caso-master", aviso_fonte_unica="Só o veículo X.")])
    assert montar(D)["temas"][0]["aviso"] == "Só o veículo X."


def test_limites_de_temas_e_fichas(tmp_data):
    for i in range(7):
        escrever_tema(tmp_data, {**TEMA_OK, "slug": f"t{i}"})
    fichas = [_ficha(tmp_data, f"camara:{i}") for i in range(8)]
    _diario(tmp_data, [_tema_do_dia(f"t{i}") for i in range(7)], fichas)
    m = montar(D)
    assert len(m["temas"]) == 5 and len(m["capa"]["temas"]) == 5
    assert sum(len(g["itens"]) for g in m["fichas"]["grupos"]) == 5 and m["fichas"]["mais"] == 3
    assert m["total"] == 8


def test_dia_sem_temas(tmp_data):
    _diario(tmp_data, [], [_ficha(tmp_data, "camara:1", fonte_unica=True)], parcial=True)
    m = montar(D)
    assert m["capa"]["temas"] == [] and m["capa"]["niveis"] == ["Federal"] and m["temas"] == []
    assert m["fichas"]["grupos"][0]["itens"][0] == {
        "situacao": "Proposta apresentada",
        "titulo": "Muda o saque do FGTS",
        "fonte_unica": True,
    }
    assert m["total"] == 3


def test_sem_carrossel(tmp_data):
    assert montar(D) is None
    _diario(tmp_data, sem_traducao=True)
    assert montar(D) is None
    _diario(tmp_data, [], [_ficha(tmp_data, "camara:1", importancia=3)])
    assert montar(D) is None


def test_arquivos_faltando_sao_ignorados(tmp_data):
    escrever_tema(tmp_data, TEMA_OK)
    fichas = ["camara:404", _ficha(tmp_data, "camara:1")]
    _diario(tmp_data, [_tema_do_dia("sumiu"), _tema_do_dia("caso-master")], fichas)
    m = montar(D)
    assert [t["nome"] for t in m["temas"]] == ["Caso Master"]
    assert [i["titulo"] for g in m["fichas"]["grupos"] for i in g["itens"]] == ["Muda o saque do FGTS"]
