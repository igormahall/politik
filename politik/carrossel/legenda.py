LIMITE_INSTAGRAM = 2200
FECHO = "Os fatos lado a lado. Cada item explicado do zero, com fontes, no link da bio."
HASHTAGS = "#política #congresso #brasil #amazonas #manaus #politik"


def legenda(modelo: dict) -> str:
    """Texto puro para colar no Instagram; corta temas do fim se passar do limite."""
    capa = modelo["capa"]
    temas = [f"• {t['nome']}: {t['linha']}" if t["linha"] else f"• {t['nome']}" for t in capa["temas"]]
    if not capa["temas"]:
        extra = [f"• {capa['mais']} movimentações oficiais ({' · '.join(capa['niveis'])})"]
    else:
        extra = [f"• Mais {capa['mais']} movimentações oficiais"] if capa["mais"] else []

    def compor(linhas):
        corpo = "\n".join(linhas + extra)
        return f"Politik · {modelo['data_extenso']}\n\nO dia na política:\n{corpo}\n\n{FECHO}\n\n{HASHTAGS}"

    texto = compor(temas)
    while len(texto) > LIMITE_INSTAGRAM and temas:
        temas.pop()
        texto = compor(temas)
    return texto
