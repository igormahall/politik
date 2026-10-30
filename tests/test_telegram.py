import json
import re

import httpx
import pytest

from politik.armazenamento import escrever_json
from politik.telegram import compor, enviar, enviar_album
from tests.conftest import load
from tests.helpers import D, escrever_ficha, escrever_mundo, escrever_selecionados, FICHA_OK, item, MUNDO_OK

B = "https://x"


def _texto(msgs):
    return "\n".join(m["text"] for m in msgs)


def _diario(d, fichas, temas=(), sem=False):
    dd = {"data": D, "temas": list(temas), "fichas": fichas}
    if sem:
        dd["sem_traducao"] = True
    escrever_json(d / f"diario/{D}.json", dd)


def test_compor_formato_c(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1")], menores=[item("camara:9")] * 3)
    escrever_ficha(tmp_data, FICHA_OK)
    escrever_ficha(tmp_data, {**FICHA_OK, "item_id": "aleam:materia:5", "nivel": "estadual", "titulo": "Lei do AM"})
    escrever_json(tmp_data / "temas/caso-master.json", load("exemplo_saida/tema.json"))
    _diario(tmp_data, ["camara:1", "aleam:materia:5"], load("exemplo_saida/diario.json")["temas"])
    msgs = compor(D, B)
    assert msgs[0]["text"].startswith("📋 <b>Politik — quarta, 28/out</b>")
    assert "🔥 Temas em andamento" in _texto(msgs)
    botoes = [b for m in msgs if m["reply_markup"] for row in m["reply_markup"]["inline_keyboard"] for b in row]
    assert {"🕒 Linha do tempo", "❓ Me explica do zero"} <= {b["text"] for b in botoes}
    assert {b["url"] for b in botoes} == {
        f"{B}/tema/caso-master.html#linha-do-tempo",
        f"{B}/tema/caso-master.html#do-zero",
    }
    t = _texto(msgs)
    assert t.index("🔥 Temas") < t.index("📜 Novidades oficiais") < t.index("🇧🇷 Federal") < t.index("🌳 Amazonas")
    assert f'<a href="{B}/ficha/camara_1.html">Muda o saque do FGTS</a>' in t
    assert f'<a href="{B}/menores/{D}.html">+ 3 itens menores</a>' in t


def test_compor_sem_traducao(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1", ementa="Altera a Lei 8.036 sobre o FGTS")])
    _diario(tmp_data, [], sem=True)
    t = _texto(compor(D, B))
    assert "Tradução indisponível hoje" in t and "PL 1/2026" in t and '<a href="https://u">' in t


def test_compor_dia_vazio(tmp_data):
    escrever_selecionados(tmp_data, D)
    _diario(tmp_data, [])
    assert "Nenhuma novidade oficial ontem." in compor(D, B)[0]["text"]


def test_compor_escapa_html(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1")])
    escrever_ficha(tmp_data, {**FICHA_OK, "titulo": "A <b> & C"})
    _diario(tmp_data, ["camara:1"])
    assert "A &lt;b&gt; &amp; C" in _texto(compor(D, B))


def test_compor_divide_mensagem_longa(tmp_data):
    ids = [f"camara:{n}" for n in range(200)]
    escrever_selecionados(tmp_data, D, destaques=[item(i) for i in ids])
    for i in ids:
        escrever_ficha(tmp_data, {**FICHA_OK, "item_id": i, "titulo": "Um título razoavelmente longo " * 2})
    _diario(tmp_data, ids)
    msgs = compor(D, B)
    assert len(msgs) > 1 and all(len(m["text"]) <= 4096 for m in msgs)
    assert _texto(msgs).count("/ficha/camara_") == 200


def test_fonte_indisponivel_aparece(tmp_data):
    escrever_selecionados(tmp_data, D, indisponiveis=["dou"])
    _diario(tmp_data, [])
    assert "⚠️ Diário Oficial da União indisponível hoje." in compor(D, B)[0]["text"]


def test_enviar_tenta_de_novo_em_429():
    chamadas = []

    def h(req):
        chamadas.append(req)
        return httpx.Response(429 if len(chamadas) == 1 else 200, json={"ok": True})

    enviar(
        [{"text": "oi", "reply_markup": None}],
        "T",
        "42",
        cliente=httpx.Client(transport=httpx.MockTransport(h)),
        espera=0,
    )
    assert len(chamadas) == 2 and "/botT/sendMessage" in str(chamadas[0].url)


def _pngs(pasta, n):
    arqs = []
    for i in range(n):
        a = pasta / f"{i:02d}.png"
        a.write_bytes(b"\x89PNG falso")
        arqs.append(a)
    return arqs


def test_enviar_album_monta_media_group(tmp_path):
    chamadas = []

    def h(req):
        chamadas.append(req)
        return httpx.Response(200, json={"ok": True})

    enviar_album(_pngs(tmp_path, 3), "T", "42", cliente=httpx.Client(transport=httpx.MockTransport(h)), espera=0)
    assert len(chamadas) == 1 and "/botT/sendMediaGroup" in str(chamadas[0].url)
    corpo = chamadas[0].read().decode("latin-1")
    media = json.loads(re.search(r'name="media"\r\n\r\n(.*?)\r\n', corpo).group(1))
    assert [m["media"] for m in media] == ["attach://f0", "attach://f1", "attach://f2"]
    assert {m["type"] for m in media} == {"photo"}
    assert 'name="f2"' in corpo and 'name="chat_id"' in corpo


def test_enviar_album_erro_nao_vaza_token(tmp_path):
    def h(req):
        return httpx.Response(400, json={"ok": False, "description": "bad"})

    cliente = httpx.Client(transport=httpx.MockTransport(h))
    with pytest.raises(RuntimeError) as e:
        enviar_album(_pngs(tmp_path, 2), "SEGREDO", "42", cliente=cliente, espera=0)
    assert "400" in str(e.value) and "SEGREDO" not in str(e.value)


def test_enviar_album_rejeita_mais_de_10_ou_nenhuma(tmp_path):
    with pytest.raises(ValueError):
        enviar_album(_pngs(tmp_path, 11), "T", "42")
    with pytest.raises(ValueError):
        enviar_album([], "T", "42")


def test_compor_secao_mundo(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1")])
    escrever_ficha(tmp_data, FICHA_OK)
    escrever_mundo(tmp_data, {**MUNDO_OK, "titulo": "Tarifa & aço"})
    escrever_json(
        tmp_data / f"diario/{D}.json", {"data": D, "temas": [], "fichas": ["camara:1"], "mundo": [MUNDO_OK["item_id"]]}
    )
    t = _texto(compor(D, B))
    assert t.index("📜 Novidades oficiais") < t.index("🌍 Mundo") < t.index("itens menores")
    assert f'<a href="{B}/mundo/mundo_2026-10-28_1.html">Tarifa &amp; aço</a>' in t


def test_compor_sem_mundo_nao_tem_secao(tmp_data):
    escrever_selecionados(tmp_data, D, destaques=[item("camara:1")])
    escrever_ficha(tmp_data, FICHA_OK)
    _diario(tmp_data, ["camara:1"])
    assert "🌍 Mundo" not in _texto(compor(D, B))
