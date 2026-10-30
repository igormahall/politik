import subprocess
import sys
from pathlib import Path

from politik.armazenamento import data_dir, escrever_json, id_seguro, ler_json
from politik.esquemas import erros_diario, erros_ficha, erros_tema, limpar_capa


def _restaurar_ou_remover(caminho: Path) -> None:
    """Arquivo inválido: volta para a versão commitada; se não houver, remove."""
    r = subprocess.run(["git", "show", f"HEAD:{caminho}"], capture_output=True)
    if r.returncode == 0:
        caminho.write_bytes(r.stdout)
    else:
        caminho.unlink(missing_ok=True)


def _limpar_invalidos(pasta: Path, erros_fn, acao) -> set[str]:
    """Confere todo arquivo da pasta; devolve os nomes (stem) que eram inválidos."""
    invalidos = set()
    for p in sorted(pasta.glob("*.json")):
        conteudo = ler_json(p)
        erros = erros_fn(conteudo) if conteudo is not None else ["JSON inválido"]
        if erros:
            print(f"{p.name} inválido: {erros}", file=sys.stderr)
            acao(p)
            invalidos.add(p.stem)
    return invalidos


def validar(data: str) -> dict:
    base = data_dir()
    sel = ler_json(base / "selecionados" / f"{data}.json", {"destaques": []})
    destaques = {d["id"]: d for d in sel.get("destaques", [])}
    pendentes = ler_json(base / "pendentes.json", [])
    primeira = {**sel.get("primeira_vez", {}), **{p["item"]["id"]: p["primeira_vez"] for p in pendentes}}

    # 1. todo tema e toda ficha precisam estar válidos (inclusive os fora do diário)
    _limpar_invalidos(base / "temas", erros_tema, _restaurar_ou_remover)
    _limpar_invalidos(base / "fichas", erros_ficha, lambda p: p.unlink())

    def ficha_valida(iid: str) -> bool:
        return (base / "fichas" / f"{id_seguro(iid)}.json").exists()

    # 2. diário
    caminho_diario = base / "diario" / f"{data}.json"
    diario = ler_json(caminho_diario)
    for aviso in limpar_capa(diario) if isinstance(diario, dict) else []:
        print(f"diário: {aviso}", file=sys.stderr)
    if diario is None or erros_diario(diario):
        if diario is not None:
            print(f"diário inválido: {erros_diario(diario)}", file=sys.stderr)
        # aproveita fichas válidas de hoje escritas antes de o Claude parar
        feitas = [
            i
            for i in destaques
            if ficha_valida(i) and ler_json(base / "fichas" / f"{id_seguro(i)}.json", {}).get("data") == data
        ]
        diario = {"data": data, "temas": [], "fichas": feitas}
        diario["parcial" if feitas else "sem_traducao"] = True

    diario["fichas"] = [i for i in diario["fichas"] if ficha_valida(i)]
    diario["temas"] = [t for t in diario["temas"] if (base / "temas" / f"{t['slug']}.json").exists()]
    escrever_json(caminho_diario, diario)

    # 3. destaque sem ficha válida volta para a fila, mantendo a data da primeira vez
    ja = {p["item"]["id"] for p in pendentes}
    for iid, d in destaques.items():
        if iid not in diario["fichas"] and iid not in ja:
            pendentes.append({"item": d, "primeira_vez": primeira.get(iid, data)})
    escrever_json(base / "pendentes.json", pendentes)
    return diario
