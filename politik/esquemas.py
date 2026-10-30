from datetime import date
from urllib.parse import urlparse

NIVEIS = {"federal", "estadual", "municipal"}


def _datas(d: dict, campos: list[str]) -> list[str]:
    erros = []
    for c in campos:
        try:
            date.fromisoformat(d.get(c))
        except (TypeError, ValueError):
            erros.append(f"{c}: data inválida {d.get(c)!r} (use AAAA-MM-DD)")
    return erros


TEXTOS_FICHA = [
    "item_id",
    "tipo_simples",
    "situacao",
    "titulo",
    "o_que_e",
    "quem_propos",
    "o_que_muda",
    "proximo_passo",
    "data",
]
TEXTOS_TEMA = ["slug", "nome", "inicio", "ultima_novidade", "resumo_ate_aqui", "explica_do_zero"]


def _textos(d: dict, campos: list[str]) -> list[str]:
    return [f"{c}: texto obrigatório" for c in campos if not isinstance(d.get(c), str) or not d[c].strip()]


def _fontes(fontes, onde: str) -> list[str]:
    if not isinstance(fontes, list) or not fontes:
        return [f"{onde}fontes: precisa de pelo menos uma fonte"]
    erros = []
    for f in fontes:
        if not isinstance(f, dict) or not str(f.get("nome", "")).strip():
            erros.append(f"{onde}fontes: fonte sem nome")
        elif not str(f.get("url", "")).startswith("http"):
            erros.append(f"{onde}fontes: url inválida {f.get('url')!r}")
    return erros


def erros_ficha(d: dict) -> list[str]:
    if not isinstance(d, dict):
        return ["ficha: precisa ser objeto"]
    erros = _textos(d, TEXTOS_FICHA) + _datas(d, ["data"])
    if d.get("nivel") not in NIVEIS:
        erros.append(f"nivel: inválido {d.get('nivel')!r}")
    erros += _fontes(d.get("fontes"), "")
    if not isinstance(d.get("fonte_unica"), bool):
        erros.append("fonte_unica: precisa ser booleano")
    if not isinstance(d.get("temas"), list):
        erros.append("temas: precisa ser lista")
    imp = d.get("importancia")
    if imp is not None and (type(imp) is not int or imp not in (1, 2, 3)):
        erros.append("importancia: 1 (alta), 2 (média) ou 3 (baixa)")
    return erros


def erros_tema(d: dict) -> list[str]:
    if not isinstance(d, dict):
        return ["tema: precisa ser objeto"]
    erros = _textos(d, TEXTOS_TEMA) + _datas(d, ["inicio", "ultima_novidade"])
    if not isinstance(d.get("ativo"), bool):
        erros.append("ativo: precisa ser booleano")
    if not isinstance(d.get("palavras_chave"), list) or not d["palavras_chave"]:
        erros.append("palavras_chave: precisa de pelo menos uma")
    lt = d.get("linha_do_tempo")
    if not isinstance(lt, list) or not lt:
        return erros + ["linha_do_tempo: precisa de pelo menos um fato"]
    if not all(isinstance(f, dict) for f in lt):
        return erros + ["linha_do_tempo: toda entrada precisa ser objeto"]
    vistos = set()
    for i, f in enumerate(lt):
        erros += [f"linha_do_tempo[{i}].{e}" for e in _textos(f, ["data", "fato"]) + _datas(f, ["data"])]
        erros += _fontes(f.get("fontes"), f"linha_do_tempo[{i}].")
        chave = (f.get("data"), f.get("fato"))
        if chave in vistos:
            erros.append(f"linha_do_tempo[{i}]: fato repetido")
        vistos.add(chave)
        if d.get("internacional") is True and len(_organizacoes(f.get("fontes"))) < 2:
            erros.append(f"linha_do_tempo[{i}]: tema internacional precisa de duas organizações nas fontes")
    datas = [str(f.get("data", "")) for f in lt]
    if datas != sorted(datas):
        erros.append("linha_do_tempo: fora de ordem de data")
    return erros


def erros_diario(d: dict) -> list[str]:
    if not isinstance(d, dict):
        return ["diário: precisa ser objeto"]
    erros = _textos(d, ["data"])
    if not isinstance(d.get("fichas"), list):
        erros.append("fichas: precisa ser lista")
    temas = d.get("temas")
    if not isinstance(temas, list):
        return erros + ["temas: precisa ser lista"]
    for i, t in enumerate(temas):
        if not isinstance(t, dict):
            erros.append(f"temas[{i}]: precisa ser objeto")
            continue
        erros += [f"temas[{i}].{e}" for e in _textos(t, ["slug", "novo_hoje"])]
        if t.get("aviso_fonte_unica") is not None and not isinstance(t["aviso_fonte_unica"], str):
            erros.append(f"temas[{i}].aviso_fonte_unica: texto ou null")
    return erros


NOME_CURTO_MAX = 40
LINHA_CAPA_MAX = 80


def limpar_capa(d: dict) -> list[str]:
    """Campos da capa do carrossel são opcionais: o inválido sai sozinho, sem invalidar o diário."""
    avisos = []
    temas = d.get("temas") if isinstance(d, dict) else None
    for i, t in enumerate(temas if isinstance(temas, list) else []):
        if not isinstance(t, dict):
            continue
        for campo, limite in (("nome_curto", NOME_CURTO_MAX), ("linha_capa", LINHA_CAPA_MAX)):
            if campo in t and (not isinstance(t[campo], str) or not t[campo].strip() or len(t[campo]) > limite):
                del t[campo]
                avisos.append(f"temas[{i}].{campo}: removido (texto de 1 a {limite} caracteres)")
    return avisos


# Seção Mundo: as organizações que podem confirmar um fato, por domínio (BBC PT e EN contam como uma).
ORGANIZACOES = {"bbc.co.uk": "BBC", "bbc.com": "BBC", "dw.com": "DW", "agenciabrasil.ebc.com.br": "Agência Brasil"}
TEXTOS_MUNDO = ["item_id", "titulo", "o_que_aconteceu", "data"]


def organizacao(url: str) -> str | None:
    host = (urlparse(str(url)).hostname or "").lower()
    return next((org for dominio, org in ORGANIZACOES.items() if host == dominio or host.endswith("." + dominio)), None)


def _organizacoes(fontes) -> set[str]:
    return {organizacao(f.get("url")) for f in fontes or [] if isinstance(f, dict)} - {None}


def erros_mundo(d: dict, urls_mundo: set[str] | None = None, urls_impacto: set[str] | None = None) -> list[str]:
    """Ficha do Mundo. Com os conjuntos de URLs do dia, só vale fonte que o Politik coletou."""
    if not isinstance(d, dict):
        return ["ficha do mundo: precisa ser objeto"]
    erros = _textos(d, TEXTOS_MUNDO) + _datas(d, ["data"]) + _fontes(d.get("fontes"), "")
    if len(_organizacoes(d.get("fontes"))) < 2:
        erros.append("fontes: o fato precisa de duas organizações diferentes (BBC, DW, Agência Brasil)")
    imp = d.get("importancia")
    if type(imp) is not int or imp not in (1, 2, 3):
        erros.append("importancia: 1 (alta), 2 (média) ou 3 (baixa)")
    tem_impacto = d.get("importa_para_o_brasil") is not None
    if tem_impacto != (d.get("fontes_impacto") is not None):
        erros.append("importa_para_o_brasil e fontes_impacto: um não existe sem o outro")
    if tem_impacto:
        erros += _textos(d, ["importa_para_o_brasil"]) + _fontes(d.get("fontes_impacto"), "impacto.")
    for campo, urls in (("fontes", urls_mundo), ("fontes_impacto", urls_impacto)):
        if urls is None:
            continue
        for f in d.get(campo) or []:
            if isinstance(f, dict) and f.get("url") not in urls:
                erros.append(f"{campo}: url não coletada hoje {f.get('url')!r}")
    return erros
