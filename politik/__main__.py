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
    sel, pend = filtrar(args.data, itens, ler_json(data_dir() / "pendentes.json", []), carregar_cfg(), carregar_temas())
    sel["fontes_indisponiveis"] = sorted(falhas)
    for chave in ("destaques", "noticias", "menores"):
        sel[chave] = [i.to_dict() for i in sel[chave]]
    escrever_json(data_dir() / "selecionados" / f"{args.data}.json", sel)
    escrever_json(data_dir() / "pendentes.json", pend)
    print(
        f"destaques={len(sel['destaques'])} noticias={len(sel['noticias'])} "
        f"menores={len(sel['menores'])} pendentes={len(pend)}"
    )
    return 0


def cmd_validar(args) -> int:
    from politik.temas import marcar_inativos
    from politik.validar import validar

    diario = validar(args.data)
    inativos = marcar_inativos(args.data, carregar_cfg()["inatividade_tema_dias"])
    print(
        f"fichas válidas={len(diario['fichas'])} temas={len(diario['temas'])} "
        f"sem_traducao={diario.get('sem_traducao', False)} inativados={inativos}"
    )
    return 0


def cmd_site(args) -> int:
    import os

    from politik.site.gerador import gerar

    gerar(Path(args.saida), args.base_url or os.environ.get("POLITIK_BASE_URL", ""))
    return 0


def cmd_enviar(args) -> int:
    import os

    from politik.telegram import compor, enviar

    msgs = compor(args.data, os.environ.get("POLITIK_BASE_URL", ""))
    enviar(msgs, os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"])
    print(f"{len(msgs)} mensagens enviadas")
    return 0


def cmd_carrossel(args) -> int:
    import os
    from html import escape

    from politik import telegram
    from politik.carrossel import render
    from politik.carrossel.conteudo import montar
    from politik.carrossel.legenda import legenda

    token, chat = os.environ["TELEGRAM_BOT_TOKEN"], os.environ["TELEGRAM_CHAT_ID"]
    modelo = montar(args.data)
    if modelo is None:
        telegram.enviar([{"text": "🖼️ Sem carrossel hoje.", "reply_markup": None}], token, chat)
        print("carrossel: nada hoje")
        return 0
    imagens = render.renderizar(modelo, Path(args.saida))
    telegram.enviar_album(imagens, token, chat)
    telegram.enviar([{"text": escape(legenda(modelo)), "reply_markup": None}], token, chat)
    print(f"carrossel: {len(imagens)} slides enviados")
    return 0


def cmd_registrar_uso(args) -> int:
    import json

    reg = {"data": args.data, "num_turns": None, "duration_ms": None, "sucesso": False}
    try:
        eventos = json.loads(Path(args.arquivo).read_text(encoding="utf-8"))
        res = next(e for e in reversed(eventos) if e.get("type") == "result")
        reg.update(
            num_turns=res.get("num_turns"), duration_ms=res.get("duration_ms"), sucesso=not res.get("is_error", True)
        )
    except (OSError, ValueError, StopIteration, AttributeError, TypeError):
        pass
    caminho = data_dir() / "uso.jsonl"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8") as f:
        f.write(json.dumps(reg, ensure_ascii=False) + "\n")
    print(reg)
    return 0


def cmd_validar_tema(args) -> int:
    from politik.esquemas import erros_tema

    tema = ler_json(data_dir() / "temas" / f"{args.slug}.json")
    erros = erros_tema(tema) if isinstance(tema, dict) else ["tema não encontrado"]
    for e in erros:
        print(f"tema {args.slug}: {e}", file=sys.stderr)
    return 1 if erros else 0


# nome -> (função, argumentos extras além de --data)
COMANDOS = {
    "coletar": (cmd_coletar, []),
    "filtrar": (cmd_filtrar, []),
    "validar": (cmd_validar, []),
    "enviar": (cmd_enviar, []),
    "carrossel": (cmd_carrossel, [("--saida", {"default": "carrossel_build"})]),
    "validar-tema": (cmd_validar_tema, [("--slug", {"required": True})]),
    "registrar-uso": (cmd_registrar_uso, [("--arquivo", {"default": ""})]),
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
