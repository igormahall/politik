from datetime import date

NIVEIS = {"federal", "estadual", "municipal"}


def _datas(d: dict, campos: list[str]) -> list[str]:
    erros = []
    for c in campos:
        try:
            date.fromisoformat(d.get(c))
        except (TypeError, ValueError):
            erros.append(f"{c}: data inválida {d.get(c)!r} (use AAAA-MM-DD)")
    return erros

TEXTOS_FICHA = ["item_id", "tipo_simples", "situacao", "titulo", "o_que_e", "quem_propos",
                "o_que_muda", "proximo_passo", "data"]
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
