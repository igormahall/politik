import shutil
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from politik.armazenamento import data_dir, id_seguro, ler_json

NIVEIS = [("federal", "🇧🇷 Federal"), ("estadual", "🌳 Amazonas"), ("municipal", "🏙️ Manaus")]


def _b(base: str) -> str:
    return base.rstrip("/")


def url_ficha(item_id: str, base: str) -> str:
    return f"{_b(base)}/ficha/{id_seguro(item_id)}.html"


def url_tema(slug: str, ancora: str | None = None, base: str = "") -> str:
    return f"{_b(base)}/tema/{slug}.html" + (f"#{ancora}" if ancora else "")


def url_menores(data: str, base: str) -> str:
    return f"{_b(base)}/menores/{data}.html"


def url_dia(data: str, base: str) -> str:
    return f"{_b(base)}/dia/{data}.html"


def _carregar(pasta: Path) -> dict[str, dict]:
    lidos = {p.stem: ler_json(p) for p in sorted(pasta.glob("*.json"))}
    return {k: v for k, v in lidos.items() if isinstance(v, dict)}


def gerar(saida: Path, base_url: str) -> None:
    base = data_dir()
    fichas = {f["item_id"]: f for f in _carregar(base / "fichas").values() if "item_id" in f}
    temas = _carregar(base / "temas")
    diarios = _carregar(base / "diario")
    env = Environment(loader=PackageLoader("politik.site", "templates"), autoescape=select_autoescape(["html"]))
    env.globals.update(base=_b(base_url), url_ficha=lambda i: url_ficha(i, base_url),
                       url_tema=lambda s, a=None: url_tema(s, a, base_url),
                       url_menores=lambda d: url_menores(d, base_url), url_dia=lambda d: url_dia(d, base_url),
                       niveis=NIVEIS)

    def escrever(rel: str, tpl: str, **ctx):
        destino = saida / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(env.get_template(tpl).render(**ctx), encoding="utf-8")

    saida.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent / "estilo.css", saida / "estilo.css")

    for iid, f in fichas.items():
        escrever(f"ficha/{id_seguro(iid)}.html", "ficha.html", f=f, temas=temas)
    for slug, t in temas.items():
        escrever(f"tema/{slug}.html", "tema.html", t=t,
                 fichas=[f for f in fichas.values() if slug in f.get("temas", [])])

    dias = sorted(diarios, reverse=True)
    for d in dias:
        diario = diarios[d]
        sel = ler_json(base / "selecionados" / f"{d}.json", {"destaques": [], "menores": [], "fontes_indisponiveis": []})
        itens_dia = sorted((fichas[i] for i in diario.get("fichas", []) if i in fichas),
                           key=lambda f: f.get("importancia") or 2)
        ctx = dict(d=d, diario=diario, sel=sel, temas=temas, fichas=itens_dia)
        escrever(f"dia/{d}.html", "dia.html", **ctx)
        escrever(f"menores/{d}.html", "menores.html", d=d, menores=sel.get("menores", []))
        if d == dias[0]:
            escrever("index.html", "dia.html", **ctx)
    if not dias:
        escrever("index.html", "arquivo.html", dias=[], temas=temas)
    escrever("arquivo.html", "arquivo.html", dias=dias,
             temas=dict(sorted(temas.items(), key=lambda kv: (not kv[1].get("ativo"), kv[1].get("nome", "")))))
