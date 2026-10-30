from politik.carrossel.conteudo import fatos_do_mundo, movimentacoes

LIMITE_INSTAGRAM = 2200
FECHO = "Os fatos lado a lado. Cada item explicado do zero, com fontes, no link da bio."
HASHTAGS = "#política #congresso #brasil #amazonas #manaus #politik"


def legenda(modelo: dict) -> str:
    """Texto puro para colar no Instagram; corta temas do fim se passar do limite."""
    capa = modelo["capa"]
    temas = [f"• {t['nome']}: {t['linha']}" if t["linha"] else f"• {t['nome']}" for t in capa["temas"]]
    nacionais = [n for n in capa["niveis"] if n != "Mundo"]
    if not capa["mais"]:
        extra = []
    elif not capa["temas"]:
        extra = [f"• {movimentacoes(capa['mais'])} ({' · '.join(nacionais)})"]
    else:
        extra = [f"• Mais {movimentacoes(capa['mais'])}"]
    if capa.get("mundo"):
        extra.append(f"• {fatos_do_mundo(capa['mundo'])}")

    def compor(linhas):
        corpo = "\n".join(linhas + extra)
        return f"Politik · {modelo['data_extenso']}\n\nO dia na política:\n{corpo}\n\n{FECHO}\n\n{HASHTAGS}"

    texto = compor(temas)
    while len(texto) > LIMITE_INSTAGRAM and temas:
        temas.pop()
        texto = compor(temas)
    return texto
