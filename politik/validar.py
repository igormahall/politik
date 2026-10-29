import subprocess
import sys

from politik.armazenamento import data_dir, escrever_json, id_seguro, ler_json
from politik.esquemas import erros_diario, erros_ficha, erros_tema


def _restaurar_ou_remover(caminho) -> None:
    """Tema inválido: volta para a versão commitada; se não houver, remove."""
    r = subprocess.run(["git", "show", f"HEAD:{caminho}"], capture_output=True)
    if r.returncode == 0:
        caminho.write_bytes(r.stdout)
    else:
        caminho.unlink(missing_ok=True)


def validar(data: str) -> dict:
    base = data_dir()
    sel = ler_json(base / "selecionados" / f"{data}.json", {"destaques": []})
    destaques = {d["id"]: d for d in sel.get("destaques", [])}
    pendentes = ler_json(base / "pendentes.json", [])
    primeira = {p["item"]["id"]: p["primeira_vez"] for p in pendentes}

    caminho_diario = base / "diario" / f"{data}.json"
    diario = ler_json(caminho_diario)
    if not isinstance(diario, dict) or erros_diario(diario):
        if diario is not None:
            print(f"diário inválido: {erros_diario(diario) if isinstance(diario, dict) else 'formato'}", file=sys.stderr)
        diario = {"data": data, "temas": [], "fichas": [], "sem_traducao": True}

    fichas_ok = []
    for iid in diario["fichas"]:
        caminho = base / "fichas" / f"{id_seguro(iid)}.json"
        ficha = ler_json(caminho)
        erros = erros_ficha(ficha) if isinstance(ficha, dict) else ["ficha ausente"]
        if erros:
            print(f"ficha {iid} inválida: {erros}", file=sys.stderr)
            caminho.unlink(missing_ok=True)
        else:
            fichas_ok.append(iid)
    diario["fichas"] = fichas_ok

    temas_ok = []
    for t in diario["temas"]:
        caminho = base / "temas" / f"{t['slug']}.json"
        tema = ler_json(caminho)
        erros = erros_tema(tema) if isinstance(tema, dict) else ["tema ausente"]
        if erros:
            print(f"tema {t['slug']} inválido: {erros}", file=sys.stderr)
            if caminho.exists():
                _restaurar_ou_remover(caminho)
        else:
            temas_ok.append(t)
    diario["temas"] = temas_ok
    escrever_json(caminho_diario, diario)

    # destaque sem ficha válida volta para a fila
    ja = {p["item"]["id"] for p in pendentes}
    for iid, d in destaques.items():
        if iid not in fichas_ok and iid not in ja:
            pendentes.append({"item": d, "primeira_vez": primeira.get(iid, data)})
    escrever_json(base / "pendentes.json", pendentes)
    return diario
