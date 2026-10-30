from unittest.mock import ANY

from politik import coletores
from politik.__main__ import main
from politik.armazenamento import carregar_itens, ler_json
from tests.helpers import D
from tests.helpers import item as _item


def boom(data):
    raise RuntimeError("fora do ar")


def _fake(monkeypatch, cols):
    monkeypatch.setattr(coletores, "carregar_todos", lambda: cols)


def test_coletar_fonte_falha_continua(tmp_data, monkeypatch):
    _fake(monkeypatch, {"ok": lambda d: [_item()], "ruim": boom})
    assert main(["coletar", "--data", D]) == 0
    assert ler_json(tmp_data / f"brutos/{D}/_falhas.json") == {"ruim": ANY}
    assert carregar_itens(tmp_data / f"brutos/{D}/ok.json")


def test_coletar_todas_falham(tmp_data, monkeypatch):
    _fake(monkeypatch, {"a": boom, "b": boom})
    assert main(["coletar", "--data", D]) == 1


def test_filtrar_marca_indisponiveis_e_serializa(tmp_data, monkeypatch):
    _fake(monkeypatch, {"ok": lambda d: [_item(), _item("camara:2", sigla_tipo="REQ")], "ruim": boom})
    main(["coletar", "--data", D])
    assert main(["filtrar", "--data", D]) == 0
    sel = ler_json(tmp_data / f"selecionados/{D}.json")
    assert sel["fontes_indisponiveis"] == ["ruim"]
    assert [i["id"] for i in sel["destaques"]] == ["camara:1"]
    assert [i["id"] for i in sel["menores"]] == ["camara:2"]
    assert ler_json(tmp_data / "pendentes.json") == []


def _telegram_falso(monkeypatch):
    from politik import telegram
    from politik.carrossel import render

    enviadas = {"mensagens": [], "album": None}
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "T")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    monkeypatch.setattr(telegram, "enviar", lambda msgs, token, chat: enviadas["mensagens"].extend(msgs))
    monkeypatch.setattr(telegram, "enviar_album", lambda imgs, token, chat: enviadas.__setitem__("album", imgs))
    monkeypatch.setattr(render, "renderizar", lambda modelo, saida: [saida / f"{n:02d}.png" for n in (1, 2, 3)])
    return enviadas


def test_carrossel_sem_conteudo_avisa(tmp_data, monkeypatch):
    enviadas = _telegram_falso(monkeypatch)
    assert main(["carrossel", "--data", D]) == 0
    assert enviadas["mensagens"] == [{"text": "🖼️ Sem carrossel hoje.", "reply_markup": None}]
    assert enviadas["album"] is None


def test_carrossel_renderiza_e_envia_album_e_legenda(tmp_data, monkeypatch, tmp_path):
    from politik.armazenamento import escrever_json
    from tests.helpers import escrever_ficha, FICHA_OK

    enviadas = _telegram_falso(monkeypatch)
    escrever_ficha(tmp_data, {**FICHA_OK, "titulo": "A & B"})
    escrever_json(tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": ["camara:1"]})
    assert main(["carrossel", "--data", D, "--saida", str(tmp_path / "c")]) == 0
    assert [a.name for a in enviadas["album"]] == ["01.png", "02.png", "03.png"]
    assert len(enviadas["mensagens"]) == 1 and enviadas["mensagens"][0]["text"].startswith("Politik · ")
