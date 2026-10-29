import json
import re
import time
from datetime import date
from html import escape

import httpx

from politik.armazenamento import data_dir, id_seguro, ler_json
from politik.site.gerador import NIVEIS, url_ficha, url_menores, url_tema

LIMITE = 4096
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
NOMES_FONTES = {"camara": "Câmara", "senado": "Senado", "aleam": "Assembleia do AM", "cmm": "Câmara de Manaus",
                "dou": "Diário Oficial da União", "imprensa": "Imprensa", "tramitacao": "Tramitações"}


def _frases(texto: str, n: int) -> str:
    return " ".join(re.split(r"(?<=[.!?])\s+", texto.strip())[:n])


def _dividir(texto: str) -> list[str]:
    partes, atual = [], ""
    for linha in texto.split("\n"):
        while len(linha) > LIMITE:  # linha sozinha maior que o limite (raro)
            partes.append(linha[:LIMITE])
            linha = linha[LIMITE:]
        if len(atual) + len(linha) + 1 > LIMITE:
            partes.append(atual.rstrip("\n"))
            atual = ""
        atual += linha + "\n"
    if atual.strip():
        partes.append(atual.rstrip("\n"))
    return partes


def compor(data: str, base_url: str) -> list[dict]:
    base = data_dir()
    sel = ler_json(base / "selecionados" / f"{data}.json",
                   {"destaques": [], "noticias": [], "menores": [], "fontes_indisponiveis": []})
    diario = ler_json(base / "diario" / f"{data}.json", {"temas": [], "fichas": [], "sem_traducao": True})
    d = date.fromisoformat(data)
    n_total = len(sel["destaques"]) + len(sel.get("noticias", [])) + len(sel["menores"])

    blocos: list[tuple[str, dict | None]] = []
    cab = [f"📋 <b>Politik — {DIAS[d.weekday()]}, {d.day:02d}/{MESES[d.month - 1]}</b>",
           f"{n_total} itens · {len(sel['destaques'])} em destaque"]
    for f in sel.get("fontes_indisponiveis", []):
        cab.append(f"⚠️ {escape(NOMES_FONTES.get(f, f))} indisponível hoje.")
    if diario.get("sem_traducao"):
        cab.append("⚠️ Tradução indisponível hoje — mostrando textos originais.")
    blocos.append(("\n".join(cab), None))

    temas = [(t, ler_json(base / "temas" / f"{t['slug']}.json")) for t in diario.get("temas", [])]
    temas = [(t, tema) for t, tema in temas if tema]
    if temas:
        blocos.append(("\n<b>🔥 Temas em andamento</b>", None))
    for t, tema in temas:
        dias = (d - date.fromisoformat(tema["inicio"])).days + 1
        linhas = [f"<b>{escape(tema['nome'])}</b> · dia {dias}",
                  f"<i>Resumo até aqui:</i> {escape(_frases(tema['resumo_ate_aqui'], 3))}",
                  f"<i>Novo hoje:</i> {escape(t['novo_hoje'])}"]
        if t.get("aviso_fonte_unica"):
            linhas.append(f"⚠️ {escape(t['aviso_fonte_unica'])}")
        botoes = {"inline_keyboard": [[
            {"text": "🕒 Linha do tempo", "url": url_tema(t["slug"], "linha-do-tempo", base_url)},
            {"text": "❓ Me explica do zero", "url": url_tema(t["slug"], "do-zero", base_url)}]]}
        blocos.append(("\n".join(linhas), botoes))

    nov = ["\n<b>📜 Novidades oficiais</b>"]
    if diario.get("sem_traducao"):
        itens = [(i["nivel"], i["url"], i["titulo"]) for i in sel["destaques"]]
    else:
        fichas = [ler_json(base / "fichas" / f"{id_seguro(i)}.json") for i in diario.get("fichas", [])]
        itens = [(f["nivel"], url_ficha(f["item_id"], base_url), f["titulo"]) for f in fichas if f]
    if not itens:
        nov.append("Nenhuma novidade oficial ontem.")
    for nivel, rotulo in NIVEIS:
        grupo = [(u, t) for n, u, t in itens if n == nivel]
        if grupo:
            nov.append(f"\n{rotulo}")
            nov += [f'• <a href="{escape(u)}">{escape(t)}</a>' for u, t in grupo]
    nov.append(f'\n<a href="{url_menores(data, base_url)}">+ {len(sel["menores"])} itens menores</a>')
    blocos.append(("\n".join(nov), None))

    # junta blocos sem botões em mensagens, respeitando o limite
    msgs: list[dict] = []
    for texto, markup in blocos:
        if markup is None and msgs and msgs[-1]["reply_markup"] is None \
                and len(msgs[-1]["text"]) + len(texto) + 1 <= LIMITE:
            msgs[-1]["text"] += "\n" + texto
            continue
        for parte in _dividir(texto):
            msgs.append({"text": parte, "reply_markup": markup})
    return msgs


def enviar(mensagens: list[dict], token: str, chat_id: str, cliente: httpx.Client | None = None) -> None:
    cliente = cliente or httpx.Client(timeout=30)
    for m in mensagens:
        corpo = {"chat_id": chat_id, "text": m["text"], "parse_mode": "HTML", "disable_web_page_preview": True}
        if m.get("reply_markup"):
            corpo["reply_markup"] = json.dumps(m["reply_markup"])
        for tentativa in range(2):
            r = cliente.post(f"https://api.telegram.org/bot{token}/sendMessage", data=corpo)
            if r.status_code == 429 or r.status_code >= 500:
                if tentativa == 0:
                    time.sleep(float(r.json().get("parameters", {}).get("retry_after", 1)) if r.status_code == 429 else 1)
                    continue
            r.raise_for_status()
            break
