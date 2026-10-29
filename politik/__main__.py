import argparse
import sys
import tomllib
from pathlib import Path

from politik import coletores
from politik.armazenamento import carregar_itens, data_dir, escrever_json, ler_json, salvar_itens
from politik.datas import dia_de_referencia
from politik.filtro import filtrar
from politik.temas import carregar_temas

CONFIG_FILTRO = Path("config/filtro.toml")


def carregar_cfg() -> dict:
    return tomllib.loads(CONFIG_FILTRO.read_text(encoding="utf-8"))


def cmd_coletar(args) -> int:
    pasta = data_dir() / "brutos" / args.data
    cols = coletores.carregar_todos()
    falhas = {}
    for nome, fn in cols.items():
        try:
            itens = fn(args.data)
            salvar_itens(pasta / f"{nome}.json", itens)
            print(f"{nome}: {len(itens)} itens")
        except Exception as e:  # uma fonte ruim não derruba as outras
            falhas[nome] = f"{type(e).__name__}: {e}"
            print(f"{nome}: FALHOU ({falhas[nome]})", file=sys.stderr)
    escrever_json(pasta / "_falhas.json", falhas)
    return 1 if cols and len(falhas) == len(cols) else 0


def cmd_filtrar(args) -> int:
    pasta = data_dir() / "brutos" / args.data
    itens = []
    for f in sorted(pasta.glob("*.json")):
        if not f.name.startswith("_"):
            itens += carregar_itens(f)
    falhas = ler_json(pasta / "_falhas.json", {})
    sel, pend = filtrar(args.data, itens, ler_json(data_dir() / "pendentes.json", []),
                        carregar_cfg(), carregar_temas())
    sel["fontes_indisponiveis"] = sorted(falhas)
    for chave in ("destaques", "noticias", "menores"):
        sel[chave] = [i.to_dict() for i in sel[chave]]
    escrever_json(data_dir() / "selecionados" / f"{args.data}.json", sel)
    escrever_json(data_dir() / "pendentes.json", pend)
    print(f"destaques={len(sel['destaques'])} noticias={len(sel['noticias'])} "
          f"menores={len(sel['menores'])} pendentes={len(pend)}")
    return 0


def cmd_validar(args) -> int:
    from politik.temas import marcar_inativos
    from politik.validar import validar

    diario = validar(args.data)
    inativos = marcar_inativos(args.data, carregar_cfg()["inatividade_tema_dias"])
    print(f"fichas válidas={len(diario['fichas'])} temas={len(diario['temas'])} "
          f"sem_traducao={diario.get('sem_traducao', False)} inativados={inativos}")
    return 0


def cmd_site(args) -> int:
    import os

    from politik.site.gerador import gerar

    gerar(Path(args.saida), args.base_url or os.environ.get("POLITIK_BASE_URL", ""))
    return 0


# nome -> (função, argumentos extras além de --data)
COMANDOS = {
    "coletar": (cmd_coletar, []),
    "filtrar": (cmd_filtrar, []),
    "validar": (cmd_validar, []),
    "site": (cmd_site, [("--saida", {"default": "site_build"}), ("--base-url", {"default": None})]),
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="politik")
    sub = p.add_subparsers(dest="comando", required=True)
    for nome, (_, extras) in COMANDOS.items():
        s = sub.add_parser(nome)
        s.add_argument("--data", default=None)
        for flag, opcoes in extras:
            s.add_argument(flag, **opcoes)
    args = p.parse_args(argv)
    args.data = args.data or dia_de_referencia()
    return COMANDOS[args.comando][0](args)


if __name__ == "__main__":
    sys.exit(main())
