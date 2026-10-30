import base64
from functools import cache
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from politik.carrossel.conteudo import movimentacoes

PASTA = Path(__file__).parent
SIMBOLO = (PASTA.parent / "site" / "favicon.svg").read_text(encoding="utf-8")
LARGURA, ALTURA = 1080, 1350

_env = Environment(loader=PackageLoader("politik.carrossel", "templates"), autoescape=select_autoescape())
_env.globals["movimentacoes"] = movimentacoes


def _fonte(nome: str) -> str:
    # embutida: a página nasce de set_content (about:blank), que não pode ler file://
    return "data:font/ttf;base64," + base64.b64encode((PASTA / "fontes" / nome).read_bytes()).decode()


@cache
def _css() -> str:
    css = (PASTA / "estilo.css").read_text(encoding="utf-8")
    return css.replace("{{ fontes }}/BricolageGrotesque.ttf", _fonte("BricolageGrotesque.ttf")).replace(
        "{{ fontes }}/SourceSans3.ttf", _fonte("SourceSans3.ttf")
    )


def paginas_html(modelo: dict) -> list[str]:
    """Um documento HTML por slide: capa → temas → fichas → fecho."""
    slides = [("capa", None)] + [("tema", t) for t in modelo["temas"]]
    if modelo.get("fichas"):
        slides.append(("fichas", None))
    slides.append(("fecho", None))
    tpl = _env.get_template("slides.html")
    css = _css()
    return [
        tpl.render(css=css, simbolo=SIMBOLO, m=modelo, tipo=tipo, t=t, n=n) for n, (tipo, t) in enumerate(slides, 1)
    ]


def renderizar(modelo: dict, saida: Path) -> list[Path]:
    """Grava 01.png, 02.png… (1080×1350) em `saida` e devolve os caminhos em ordem."""
    from playwright.sync_api import sync_playwright

    saida.mkdir(parents=True, exist_ok=True)
    arquivos = []
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        try:
            pagina = navegador.new_page(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=1)
            for n, html in enumerate(paginas_html(modelo), 1):
                pagina.set_content(html)
                pagina.evaluate("document.fonts.ready.then(() => encaixar())")
                arquivo = saida / f"{n:02d}.png"
                pagina.screenshot(path=str(arquivo))
                arquivos.append(arquivo)
        finally:
            navegador.close()
    return arquivos
