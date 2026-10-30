from datetime import date

from politik.armazenamento import data_dir, id_seguro, ler_json
from politik.site.gerador import data_br, NIVEIS
from politik.telegram import _frases, MESES

MAX_TEMAS = 5
MAX_FICHAS = 5
DIAS_ATE_DESDE = 60  # tema mais antigo que isso: "desde mmm/aaaa" em vez de "dia N"


def movimentacoes(n: int) -> str:
    return "1 movimentação oficial" if n == 1 else f"{n} movimentações oficiais"


def _etiqueta(inicio: str, dia: date) -> str:
    i = date.fromisoformat(inicio)
    n = (dia - i).days + 1
    if n > DIAS_ATE_DESDE:
        return f"Tema em andamento · desde {MESES[i.month - 1]}/{i.year}"
    return f"Tema em andamento · dia {n}"


def montar(data: str) -> dict | None:
    """Modelo dos slides do dia (só dados, sem HTML). None quando não há carrossel."""
    base = data_dir()
    diario = ler_json(base / "diario" / f"{data}.json")
    if not diario or diario.get("sem_traducao"):
        return None
    dia = date.fromisoformat(data)

    temas, capa_temas = [], []
    for t in diario.get("temas", []):
        tema = ler_json(base / "temas" / f"{t['slug']}.json")
        if not tema:
            continue
        temas.append(
            {
                "etiqueta": _etiqueta(tema["inicio"], dia),
                "nome": tema["nome"],
                "novo_hoje": t["novo_hoje"],
                "aviso": t.get("aviso_fonte_unica"),
                "para_entender": _frases(tema["resumo_ate_aqui"], 1),
            }
        )
        capa_temas.append({"nome": t.get("nome_curto") or tema["nome"], "linha": t.get("linha_capa")})
        if len(temas) == MAX_TEMAS:
            break

    fichas = [ler_json(base / "fichas" / f"{id_seguro(i)}.json") for i in diario.get("fichas", [])]
    fichas = [f for f in fichas if f and (f.get("importancia") or 2) in (1, 2)]
    if not temas and not fichas:
        return None
    mostradas = fichas[:MAX_FICHAS]
    grupos = []
    for nivel, rotulo in NIVEIS:
        itens = [
            {"situacao": f["situacao"], "titulo": f["titulo"], "fonte_unica": bool(f.get("fonte_unica"))}
            for f in mostradas
            if f["nivel"] == nivel
        ]
        if itens:
            grupos.append({"nivel": rotulo.split(" ", 1)[1], "itens": itens})

    return {
        "data_extenso": data_br(data),
        "capa": {"temas": capa_temas, "mais": len(mostradas), "niveis": [g["nivel"] for g in grupos]},
        "temas": temas,
        "fichas": {"grupos": grupos, "mais": len(fichas) - len(mostradas)} if mostradas else None,
        "total": 1 + len(temas) + (1 if mostradas else 0) + 1,
    }
