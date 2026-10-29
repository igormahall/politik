from politik.armazenamento import escrever_json
from politik.modelos import Item
from politik.temas import carregar_temas, casa_tema


def _it(**kw):
    base = dict(id="x", fonte="dou", nivel="federal", categoria="norma", sigla_tipo="PORTARIA",
                titulo="", ementa="", data="2026-10-28", url="u")
    return Item(**{**base, **kw})


def test_casa_tema_sem_acento_e_caixa():
    tema = {"slug": "caso-master", "palavras_chave": ["Banco Master", "Vorcaro"]}
    assert casa_tema(_it(ementa="liquidação do BANCO MASTER S.A."), [tema]) == ["caso-master"]
    assert casa_tema(_it(titulo="Daniel Vórcaro depõe"), [tema]) == ["caso-master"]
    assert casa_tema(_it(ementa="Banco do Brasil"), [tema]) == []


def test_casa_tema_usa_orgao():
    tema = {"slug": "t", "palavras_chave": ["Banco Central"]}
    assert casa_tema(_it(extra={"orgao": "Banco Central do Brasil/Diretoria"}), [tema]) == ["t"]


def test_carregar_temas_ativos(tmp_data):
    escrever_json(tmp_data / "temas/a.json", {"slug": "a", "ativo": True, "palavras_chave": []})
    escrever_json(tmp_data / "temas/b.json", {"slug": "b", "ativo": False, "palavras_chave": []})
    assert [t["slug"] for t in carregar_temas()] == ["a"]
    assert len(carregar_temas(ativos=False)) == 2
