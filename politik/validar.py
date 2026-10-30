import json
import subprocess
import sys
from pathlib import Path

from politik.armazenamento import data_dir, escrever_json, id_seguro, ler_json
from politik.esquemas import erros_diario, erros_ficha, erros_mundo, erros_tema, limpar_capa


def _versao_commitada(caminho: Path) -> bytes | None:
    r = subprocess.run(["git", "show", f"HEAD:{caminho}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _restaurar_ou_remover(caminho: Path) -> None:
    """Arquivo inválido: volta para a versão commitada; se não houver, remove."""
    commitado = _versao_commitada(caminho)
    if commitado is not None:
        caminho.write_bytes(commitado)
    else:
        caminho.unlink(missing_ok=True)


def _erros_tema(conteudo: dict, caminho: Path) -> list[str]:
    # tirar a marca "internacional" de um tema já gravado não pode ser um jeito de fugir das duas organizações
    commitado = _versao_commitada(caminho)
    if commitado and json.loads(commitado).get("internacional") is True and conteudo.get("internacional") is not True:
        return ["internacional: tema internacional não pode perder a marca"]
    return erros_tema(conteudo)


def _limpar_invalidos(pasta: Path, erros_fn, acao) -> set[str]:
    """Confere todo arquivo da pasta; devolve os nomes (stem) que eram inválidos."""
    invalidos = set()
    for p in sorted(pasta.glob("*.json")):
        conteudo = ler_json(p)
        erros = erros_fn(conteudo, p) if isinstance(conteudo, dict) else ["JSON inválido"]
        if erros:
            print(f"{p.name} inválido: {erros}", file=sys.stderr)
            acao(p)
            invalidos.add(p.stem)
    return invalidos


MAX_MUNDO = 5


def _validar_mundo(base: Path, data: str, sel: dict, ids) -> list[str]:
    """Fichas do Mundo do dia: só URLs coletadas hoje; as inválidas saem sem derrubar o diário."""
    urls_mundo = {i["url"] for i in sel.get("mundo", [])}
    urls_impacto = urls_mundo | {i["url"] for i in sel.get("noticias", [])}
    validos = []
    for p in sorted((base / "mundo").glob("*.json")):
        ficha = ler_json(p)
        if not isinstance(ficha, dict) or ficha.get("data") != data:
            # o Claude só escreve fichas de hoje: as de outro dia voltam à versão commitada ou saem
            _restaurar_ou_remover(p)
            continue
        erros = erros_mundo(ficha, urls_mundo, urls_impacto)
        if not erros and (not isinstance(ficha["item_id"], str) or p.stem != id_seguro(ficha["item_id"])):
            erros = ["item_id: não bate com o nome do arquivo"]
        if erros:
            print(f"{p.name} inválido: {erros}", file=sys.stderr)
            p.unlink()
        else:
            validos.append(ficha["item_id"])
    return [i for i in (ids if isinstance(ids, list) else []) if i in validos][:MAX_MUNDO]


def validar(data: str) -> dict:
    base = data_dir()
    sel = ler_json(base / "selecionados" / f"{data}.json", {"destaques": []})
    destaques = {d["id"]: d for d in sel.get("destaques", [])}
    pendentes = ler_json(base / "pendentes.json", [])
    primeira = {**sel.get("primeira_vez", {}), **{p["item"]["id"]: p["primeira_vez"] for p in pendentes}}

    # 1. todo tema e toda ficha precisam estar válidos (inclusive os fora do diário)
    _limpar_invalidos(base / "temas", _erros_tema, _restaurar_ou_remover)
    _limpar_invalidos(base / "fichas", lambda c, _: erros_ficha(c), lambda p: p.unlink())

    # o Claude só escreve o dia de hoje: diário de outro dia volta à versão commitada
    for p in (base / "diario").glob("*.json"):
        commitado = _versao_commitada(p) if p.stem != data else None
        if commitado is not None and commitado != p.read_bytes():
            print(f"{p.name}: diário de outro dia alterado; restaurado", file=sys.stderr)
            p.write_bytes(commitado)

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
    mundo = _validar_mundo(base, data, sel, diario.get("mundo"))  # sempre: ficha solta também é conferida
    if "mundo" in diario:
        diario["mundo"] = mundo
    diario["temas"] = [t for t in diario["temas"] if (base / "temas" / f"{t['slug']}.json").exists()]
    escrever_json(caminho_diario, diario)

    # 3. destaque sem ficha válida volta para a fila, mantendo a data da primeira vez
    ja = {p["item"]["id"] for p in pendentes}
    for iid, d in destaques.items():
        if iid not in diario["fichas"] and iid not in ja:
            pendentes.append({"item": d, "primeira_vez": primeira.get(iid, data)})
    escrever_json(base / "pendentes.json", pendentes)
    return diario
