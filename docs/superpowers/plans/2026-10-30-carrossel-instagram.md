# Carrossel diário para o Instagram — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Todo dia, depois do boletim, o robô gera um carrossel 4:5 no estilo "As duas águas" e uma legenda a partir dos dados validados do dia e manda os dois para o Telegram do Igor.

**Architecture:** Três camadas isoladas em `politik/carrossel/`: `conteudo.py` transforma `data/` num modelo de slides (dados puros, sem HTML), `render.py` transforma o modelo em HTML por template Jinja e em PNG com Chromium sem tela (Playwright), e `legenda.py` monta o texto. `telegram.py` ganha o envio de álbum; o comando `python -m politik carrossel` costura tudo e roda num passo próprio do `diario.yml`, que nunca derruba o boletim.

**Tech Stack:** Python 3.12, Jinja2 (já usado), Playwright 1.63.0 + Chromium (extra opcional `carrossel`), httpx (já usado), pytest.

**Spec:** `docs/superpowers/specs/2026-10-30-carrossel-instagram-design.md`

## Global Constraints

- Imagens **1080×1350 px**, PNG.
- Cores: Rio Negro `#2a1f1a`, Solimões `#c9a266`, Espuma `#f4efe7`, texto `#241b16`, rótulos `#7a5a2e`, aviso `#8a5300`, linhas `#e2d9cb`, suave `#6b5f55`.
- Fontes empacotadas no repo (OFL): Bricolage Grotesque 700 nos títulos, Source Sans 3 400/600 no texto. Nenhuma requisição à internet durante a renderização.
- Todo slide: marca d'água (símbolo + "politik · os fatos lado a lado", opacidade 0.85, canto inferior esquerdo) e "n/total" no canto inferior direito.
- Datas para leitura sempre em português (`data_br` de `politik/site/gerador.py`), nunca `AAAA-MM-DD`.
- Fora `nome_curto`/`linha_capa`, todo texto das artes vem literalmente dos dados validados; nenhum texto é inventado por código.
- O aviso de fonte única de um tema **nunca** é cortado.
- Máximo de **8 slides** (capa + até 5 temas + 1 fichas + fecho). Importância 3 fica de fora.
- Falha no carrossel não pode impedir o boletim nem o commit do histórico.
- Actions fixadas por SHA; runner `ubuntu-24.04`.
- Estilo do código: o do repositório (nomes em português, ruff com linha de 120, testes com `tmp_data` e `tests/helpers.py`).

## Review Focus

1. Texto longo (um `novo_hoje` de ~600 caracteres com aviso de fonte única): o slide não pode transbordar e o aviso aparece inteiro → teste em Task 4.
2. O Claude escreve `nome_curto`/`linha_capa` vazios, longos demais ou com tipo errado: o diário **não** pode virar inválido (cairia em `sem_traducao`); só esses campos somem → teste em Task 1.
3. Diário cita ficha ou tema cujo arquivo não existe: o carrossel ignora o item, sem exceção → teste em Task 2.
4. Telegram recusa o álbum (400/500): erro sem o token na mensagem, o boletim já foi enviado antes e o passo do workflow tem `continue-on-error` → testes em Tasks 5 e 6.
5. Títulos com `<`, `&` ou aspas: aparecem literalmente na arte (autoescape) e na legenda → testes em Tasks 3 e 4.

---

### Task 1: Campos da capa no diário (`nome_curto`, `linha_capa`)

**Files:**
- Modify: `politik/esquemas.py` (perto de `erros_diario`)
- Modify: `politik/validar.py` (função `validar`, antes de `erros_diario`)
- Modify: `.claude/skills/traduzir/SKILL.md` (passo 6 e formato do Diário)
- Test: `tests/test_esquemas.py`, `tests/test_validar.py`, `tests/test_workflows.py`

**Interfaces:**
- Produces: `limpar_capa(diario: dict) -> list[str]` em `politik/esquemas.py`: remove, de cada tema do diário, `nome_curto` se não for texto não vazio de até `NOME_CURTO_MAX = 40` caracteres e `linha_capa` se não for texto não vazio de até `LINHA_CAPA_MAX = 80`; devolve a lista de avisos (um por campo removido). Muda o dicionário no lugar; ignora entradas de `temas` que não sejam dict.
- Produces: no diário validado, cada tema pode ter `nome_curto: str` e `linha_capa: str` (ambos opcionais).

- [ ] **Step 1: Testes que falham**

```python
# tests/test_esquemas.py
def test_limpar_capa_remove_so_campos_ruins():
    d = {"data": "2026-10-29", "fichas": [], "temas": [
        {"slug": "a", "novo_hoje": "x", "nome_curto": "Caso Master", "linha_capa": "Fachin mantém o caso no STF"},
        {"slug": "b", "novo_hoje": "x", "nome_curto": "", "linha_capa": "y" * 81},
        {"slug": "c", "novo_hoje": "x", "nome_curto": 3},
    ]}
    avisos = limpar_capa(d)
    assert d["temas"][0]["nome_curto"] == "Caso Master" and "linha_capa" in d["temas"][0]
    assert "nome_curto" not in d["temas"][1] and "linha_capa" not in d["temas"][1]
    assert "nome_curto" not in d["temas"][2]
    assert len(avisos) == 3
    assert erros_diario(d) == []

# tests/test_validar.py
def test_capa_invalida_nao_derruba_o_diario(tmp_data):
    # mesmo arranjo de test_validar_tema_invalido_sai_do_diario, com tema válido e
    # diário com "nome_curto": "" e "linha_capa": "ok"
    diario = validar(D)
    assert "sem_traducao" not in diario and "parcial" not in diario
    assert "nome_curto" not in diario["temas"][0] and diario["temas"][0]["linha_capa"] == "ok"

# tests/test_workflows.py
def test_skill_traduzir_pede_campos_da_capa():
    skill = Path(".claude/skills/traduzir/SKILL.md").read_text()
    assert '"nome_curto"' in skill and '"linha_capa"' in skill
```

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_esquemas.py tests/test_validar.py tests/test_workflows.py -q` → FAIL (`limpar_capa` não existe; a skill não cita os campos).

- [ ] **Step 3: Implementar.** `limpar_capa` em `esquemas.py`; em `validar.py`, chamar `limpar_capa(diario)` (imprimindo os avisos em stderr, como o resto do módulo) logo depois de ler o diário e antes de `erros_diario`, só se `diario` for dict. Na skill, no passo 6, acrescentar: para cada tema do diário, `nome_curto` (até 40 caracteres, o nome do tema como cabe numa capa) e `linha_capa` (até 80 caracteres, o fato do dia numa frase curta, sem adjetivo de juízo, seguindo o `editorial/GUIA.md`); e incluir os dois campos no exemplo de JSON do Diário, ex. `"nome_curto": "Caso Master", "linha_capa": "Fachin mantém o caso na Presidência do STF"`.

- [ ] **Step 4:** mesmo comando do Step 2 → PASS; depois `.venv/bin/python -m pytest -q` → tudo passa.

- [ ] **Step 5: Commit** `feat(diario): campos nome_curto e linha_capa para a capa do carrossel`

---

### Task 2: Modelo dos slides (`conteudo.py`)

**Files:**
- Create: `politik/carrossel/__init__.py` (vazio), `politik/carrossel/conteudo.py`
- Test: `tests/test_carrossel_conteudo.py`

**Interfaces:**
- Consumes: diário validado (Task 1), `ler_json`, `id_seguro`, `data_dir` (`politik/armazenamento.py`), `data_br`, `NIVEIS` (`politik/site/gerador.py`), `MESES` abreviados de `politik/telegram.py`.
- Produces: `montar(data: str) -> dict | None`. `None` quando o diário não existe, tem `sem_traducao`, ou não há temas nem fichas de importância 1–2. Senão:

```python
{
  "data_extenso": "quinta-feira, 29 de outubro de 2026",
  "capa": {
    "temas": [{"nome": str, "linha": str | None}],   # vazio no dia sem temas
    "mais": int,                                     # nº de fichas no slide de fichas
    "niveis": [str],                                 # ex. ["Federal", "Amazonas"]; usado no dia sem temas
  },
  "temas": [{"etiqueta": str, "nome": str, "novo_hoje": str, "aviso": str | None, "para_entender": str}],
  "fichas": {"grupos": [{"nivel": str, "itens": [{"situacao": str, "titulo": str, "fonte_unica": bool}]}],
             "mais": int} | None,
  "total": int,                                      # nº de slides: 1 + len(temas) + (1 se fichas) + 1
}
```

Regras (do spec): temas na ordem do diário, no máximo `MAX_TEMAS = 5`, pulando os cujo arquivo em `data/temas/` não existe. `capa.temas[i].nome` = `nome_curto` ou, sem ele, o `nome` do tema; `linha` = `linha_capa` ou `None`. Etiqueta: `"Tema em andamento · dia N"` com `N = (dia - inicio).days + 1`; se `N > 60`, `"Tema em andamento · desde mar/2025"` (mês abreviado minúsculo/ano). `para_entender` = 1ª frase de `resumo_ate_aqui` (o render decide se cabe). Fichas: as do diário com arquivo existente e `importancia` em (1, 2) (ausente conta como 2, como no Telegram), na ordem do diário; as primeiras `MAX_FICHAS = 5` vão para os grupos, o resto conta em `mais`; grupos na ordem de `NIVEIS`, rótulo sem o emoji ("Federal", "Amazonas", "Manaus"); sem fichas, `"fichas": None`.

- [ ] **Step 1: Testes que falham** (usar `tmp_data`, `escrever_ficha`, `FICHA_OK`, `TEMA_OK`, `D` de `tests/helpers.py`)

```python
def test_montar_dia_normal(tmp_data):
    # 2 temas (um com nome_curto/linha_capa, outro sem), 3 fichas: federal imp 1, estadual imp 2, federal imp 3
    m = montar(D)
    assert m["data_extenso"] == "quarta-feira, 28 de outubro de 2026"
    assert m["capa"]["temas"][0] == {"nome": "Caso Master", "linha": "Fachin mantém o caso no STF"}
    assert m["capa"]["temas"][1]["linha"] is None
    assert [g["nivel"] for g in m["fichas"]["grupos"]] == ["Federal", "Amazonas"]
    assert m["capa"]["mais"] == 2 and m["total"] == 1 + 2 + 1 + 1

def test_etiqueta_conta_dias_e_vira_desde_depois_de_60(tmp_data):
    # TEMA_OK com inicio = D → "dia 1"; inicio "2025-03-28" → "desde mar/2025"

def test_aviso_fonte_unica_vai_para_o_slide(tmp_data):
    assert montar(D)["temas"][0]["aviso"] == "Só o veículo X."

def test_limites_de_temas_e_fichas(tmp_data):
    # 7 temas e 8 fichas de importância 2
    m = montar(D)
    assert len(m["temas"]) == 5 and len(m["capa"]["temas"]) == 5
    assert sum(len(g["itens"]) for g in m["fichas"]["grupos"]) == 5 and m["fichas"]["mais"] == 3
    assert m["total"] == 8

def test_dia_sem_temas(tmp_data):
    m = montar(D)
    assert m["capa"]["temas"] == [] and m["capa"]["niveis"] == ["Federal"] and m["temas"] == []

def test_sem_carrossel(tmp_data):
    # sem diário; diário com sem_traducao; diário só com fichas de importância 3 → None nos três

def test_arquivos_faltando_sao_ignorados(tmp_data):
    # diário cita "camara:404" e tema "sumiu" sem arquivo → montar não levanta e não os inclui
```

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_carrossel_conteudo.py -q` → FAIL (módulo não existe).
- [ ] **Step 3:** Implementar `montar` em `politik/carrossel/conteudo.py` com `MAX_TEMAS = 5` e `MAX_FICHAS = 5` no topo do módulo.
- [ ] **Step 4:** mesmo comando → PASS.
- [ ] **Step 5: Commit** `feat(carrossel): modelo dos slides a partir do diário`

---

### Task 3: Legenda (`legenda.py`)

**Files:**
- Create: `politik/carrossel/legenda.py`
- Test: `tests/test_carrossel_legenda.py`

**Interfaces:**
- Consumes: o dict de `montar` (Task 2).
- Produces: `legenda(modelo: dict) -> str` (texto puro, sem HTML), no máximo `LIMITE_INSTAGRAM = 2200` caracteres.

Texto fixo (copiar exatamente):

```
Politik · {data_extenso}

O dia na política:
• {nome}: {linha}            ← uma por tema; sem linha, só "• {nome}"
• Mais {mais} movimentações oficiais   ← só se mais > 0 (no dia sem temas: "• {mais} movimentações oficiais ({niveis unidos por ' · '})")

Os fatos lado a lado. Cada item explicado do zero, com fontes, no link da bio.

#política #congresso #brasil #amazonas #manaus #politik
```

Se passar de 2200, remover linhas de tema do fim (nunca o cabeçalho, o fecho ou as hashtags).

- [ ] **Step 1: Testes que falham**

```python
def test_legenda_dia_normal():
    t = legenda(MODELO)  # MODELO: dict literal no formato da Task 2, 2 temas, mais=3
    assert t.startswith("Politik · quarta-feira, 28 de outubro de 2026\n")
    assert "• Caso Master: Fachin mantém o caso no STF" in t
    assert "• Mais 3 movimentações oficiais" in t
    assert t.rstrip().endswith("#politik")

def test_legenda_sem_linha_e_caracteres_especiais():
    # tema com nome "A & B <C>" e linha None → "• A & B <C>" literal, sem "&amp;"

def test_legenda_respeita_limite():
    # 5 temas com linha de 1000 caracteres → len(t) <= 2200 e hashtags preservadas
```

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_carrossel_legenda.py -q` → FAIL.
- [ ] **Step 3:** Implementar.
- [ ] **Step 4:** → PASS.
- [ ] **Step 5: Commit** `feat(carrossel): legenda pronta para o Instagram`

---

### Task 4: Desenho dos slides (template + Playwright)

**Files:**
- Create: `politik/carrossel/render.py`, `politik/carrossel/templates/slides.html`, `politik/carrossel/estilo.css`
- Create: `politik/carrossel/fontes/` com `BricolageGrotesque.ttf`, `SourceSans3.ttf` e `OFL.txt`
- Modify: `pyproject.toml` (extra `carrossel = ["playwright==1.63.0"]`; `package-data` para `politik.carrossel`: `templates/*.html`, `*.css`, `fontes/*`)
- Test: `tests/test_carrossel_render.py`

**Interfaces:**
- Consumes: o dict de `montar` (Task 2); `politik/site/simbolo-contorno.svg` e `politik/site/favicon.svg` (símbolo) como fonte do desenho do símbolo, embutidos inline.
- Produces: `paginas_html(modelo: dict) -> list[str]` (um documento HTML completo por slide, na ordem capa → temas → fichas → fecho) e `renderizar(modelo: dict, saida: Path) -> list[Path]` (grava `01.png`, `02.png`… em `saida`, 1080×1350, e devolve os caminhos em ordem).

Decisões:
- Fontes: baixar de `github.com/google/fonts` (`ofl/bricolagegrotesque/BricolageGrotesque[opsz,wdth,wght].ttf`, `ofl/sourcesans3/SourceSans3[wght].ttf` e o `OFL.txt` de cada pasta, juntos num `OFL.txt`), referenciadas por `@font-face` com URL `file://` absoluta do pacote. Nada de Google Fonts online.
- Layout em px reais (1080×1350), no estilo C do spec: faixa Rio Negro no topo com etiqueta Solimões e título Espuma; fio Solimões de 18 px sob a faixa; corpo Espuma. Tamanhos de partida: título 64 px (capa 84 px), texto 38 px, rótulos 26 px, etiqueta 28 px. Marca d'água e "n/total" a 48 px das bordas. Textos via Jinja com autoescape.
- Encaixe de texto, nesta ordem, até o corpo caber (checado no navegador com `scrollHeight > clientHeight` no contêiner do corpo): reduzir a escala do texto em passos de 0.05 até 0.75; no slide de tema, tirar o bloco "Para entender"; por fim, cortar `novo_hoje` na última frase inteira que caiba e terminar com "…". O aviso de fonte única nunca é reduzido abaixo da escala do texto nem cortado.
- Fecho com os textos exatos do spec: título "Os fatos lado a lado"; "Cada item explicado do zero, com a linha do tempo e as fontes."; "Link na bio · boletim diário grátis no Telegram". Capa: título "O dia na política"; no dia sem temas, "Hoje: N movimentações oficiais" e os níveis unidos por " · ". Slide de fichas: título "Também hoje", "e mais N no link da bio" quando `mais > 0`, "⚠ fonte única" nos itens marcados.
- Um único `chromium.launch()` por chamada de `renderizar`, uma página com viewport 1080×1350 e `device_scale_factor=1`.

- [ ] **Step 1: Testes que falham** (os de navegador com `pytest.importorskip("playwright")` e pulando se o Chromium não estiver instalado)

```python
def test_paginas_html_ordem_e_textos():
    p = paginas_html(MODELO)  # 2 temas, fichas presentes → 5 páginas
    assert len(p) == 5 and "O dia na política" in p[0] and "Também hoje" in p[3]
    assert "Os fatos lado a lado" in p[-1] and "5/5" in p[-1]
    assert "fonts.googleapis" not in "".join(p)

def test_texto_escapado():
    # tema com nome "A & B <script>" → "&lt;script&gt;" no HTML e nenhum "<script>" vindo do dado

def test_renderiza_png_1080x1350(tmp_path):
    arqs = renderizar(MODELO, tmp_path)
    assert [a.name for a in arqs] == ["01.png", "02.png", "03.png", "04.png", "05.png"]
    # ler o cabeçalho PNG (bytes 16–24) e conferir 1080×1350

def test_texto_longo_cabe_e_aviso_fica_inteiro(tmp_path):
    # tema com novo_hoje de ~600 caracteres e aviso "Só o veículo X divulgou o pedido de asilo."
    # abrir o HTML do slide no Playwright depois do encaixe: corpo sem transbordar
    # e o texto completo do aviso presente no DOM
```

- [ ] **Step 2:** instalar e rodar: `.venv/bin/pip install -e .[dev,carrossel] && .venv/bin/playwright install chromium && .venv/bin/python -m pytest tests/test_carrossel_render.py -q` → FAIL.
- [ ] **Step 3:** Implementar `render.py`, o template e o CSS; baixar as fontes.
- [ ] **Step 4:** mesmo pytest → PASS. Depois gerar o carrossel real de 29/10 (`python -c` com `montar("2026-10-29")` e `renderizar(..., Path("/tmp/claude-.../carrossel"))` no scratchpad) e **olhar as imagens** (ferramenta Read nos PNGs): conferir estilo C, legibilidade, nada cortado e nenhum texto sobre a marca d'água.
- [ ] **Step 5: Commit** `feat(carrossel): desenho dos slides em 1080×1350 com fontes da marca`

---

### Task 5: Envio do álbum no Telegram

**Files:**
- Modify: `politik/telegram.py` (nova função ao lado de `enviar`)
- Test: `tests/test_telegram.py`

**Interfaces:**
- Produces: `enviar_album(imagens: list[Path], token: str, chat_id: str, cliente: httpx.Client | None = None, espera: float = 1) -> None`: um `sendMediaGroup` com até 10 fotos (`type: "photo"`, `media: "attach://f{i}"`, arquivos em multipart). Mesma política de erro de `enviar`: uma nova tentativa em 429/5xx respeitando `retry_after`, `RuntimeError` sem o token na mensagem em erro de rede ou resposta não 200. Levanta `ValueError` se `imagens` estiver vazia ou tiver mais de 10.

- [ ] **Step 1: Testes que falham** (com `httpx.MockTransport`, como os testes existentes de `enviar`)

```python
def test_enviar_album_monta_media_group(tmp_path):
    # 3 PNGs falsos → 1 POST para .../sendMediaGroup; media JSON com 3 itens "attach://f0".."f2", type "photo"

def test_enviar_album_erro_nao_vaza_token(tmp_path):
    # transporte responde 400 {"description": "bad"} → RuntimeError com "400" e sem o token

def test_enviar_album_rejeita_mais_de_10(tmp_path):
    # 11 imagens → ValueError
```

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_telegram.py -q` → FAIL.
- [ ] **Step 3:** Implementar; reaproveitar o laço de tentativas de `enviar` extraindo um auxiliar privado se ficar repetido.
- [ ] **Step 4:** → PASS.
- [ ] **Step 5: Commit** `feat(telegram): envio de álbum de fotos`

---

### Task 6: Comando `carrossel` e workflow diário

**Files:**
- Modify: `politik/__main__.py` (`cmd_carrossel` e entrada em `COMANDOS`)
- Modify: `.github/workflows/diario.yml`, `.github/workflows/testes.yml`
- Modify: `docs/OPERACAO.md` (seção "Como funciona" e comando local)
- Test: `tests/test_cli.py`, `tests/test_workflows.py`

**Interfaces:**
- Consumes: `montar` (Task 2), `legenda` (Task 3), `renderizar` (Task 4), `enviar_album` (Task 5), `enviar` (existente).
- Produces: `python -m politik carrossel --data D [--saida carrossel_build]`. Com `montar(D) is None`: manda uma mensagem só, `"🖼️ Sem carrossel hoje."`, e sai com 0. Senão: renderiza em `--saida`, chama `enviar_album`, depois `enviar([{"text": escape(texto_da_legenda), "reply_markup": None}], ...)`, imprime `"carrossel: N slides enviados"` e sai com 0. Erros sobem (o passo do workflow é que os tolera).

Workflow `diario.yml`, novo passo **depois** de "Enviar no Telegram" e antes de "Salvar histórico":

```yaml
      - name: Carrossel do Instagram
        if: always() && steps.validar.outcome == 'success'
        continue-on-error: true
        timeout-minutes: 10
        run: |
          pip install -e .[carrossel]
          playwright install --with-deps chromium
          python -m politik carrossel --data "$D" --saida carrossel_build
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

`testes.yml`: trocar `pip install -e .[dev]` por `pip install -e .[dev,carrossel]` e acrescentar `- run: playwright install --with-deps chromium` antes do `pytest`. Acrescentar `carrossel_build/` ao `.gitignore`.

- [ ] **Step 1: Testes que falham**

```python
# tests/test_cli.py
def test_carrossel_sem_conteudo_avisa(tmp_data, monkeypatch):
    # sem diário; monkeypatch de politik.telegram.enviar capturando mensagens; env TELEGRAM_* falsos
    assert main(["carrossel", "--data", D]) == 0
    assert capturadas == [{"text": "🖼️ Sem carrossel hoje.", "reply_markup": None}]

def test_carrossel_renderiza_e_envia_album_e_legenda(tmp_data, monkeypatch, tmp_path):
    # diário mínimo válido; monkeypatch de renderizar (devolve 3 caminhos), enviar_album e enviar
    # → enviar_album recebe os 3 caminhos; enviar recebe 1 mensagem começando com "Politik · "

# tests/test_workflows.py
def test_carrossel_nao_derruba_o_diario():
    wf = _wf("diario.yml")
    p = _passo(wf, "diario", "Carrossel do Instagram")
    assert p["continue-on-error"] is True and "steps.validar.outcome == 'success'" in p["if"]
    nomes = [s.get("name") for s in wf["jobs"]["diario"]["steps"]]
    assert nomes.index("Enviar no Telegram") < nomes.index("Carrossel do Instagram") < nomes.index("Salvar histórico")
```

- [ ] **Step 2:** `.venv/bin/python -m pytest tests/test_cli.py tests/test_workflows.py -q` → FAIL.
- [ ] **Step 3:** Implementar o comando, editar os dois workflows, o `.gitignore` e o `docs/OPERACAO.md` (uma linha em "Como funciona" sobre o carrossel no Telegram e o comando local `python -m politik carrossel --data AAAA-MM-DD`).
- [ ] **Step 4:** `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/ruff format --check .` → tudo passa.
- [ ] **Step 5: Commit** `feat(carrossel): comando diário e passo no workflow`

---

### Task 7: Prova real

- [ ] **Step 1:** `git push`, esperar o workflow "Testes" passar (`gh run watch`).
- [ ] **Step 2:** A prova real é a próxima execução agendada (10:13 UTC). Não disparar o diário à mão para testar: isso refaria a tradução e reenviaria o boletim. Se o Igor quiser ver antes, pedir autorização a ele primeiro.
- [ ] **Step 3:** Depois da execução, conferir no log "carrossel: N slides enviados" (`gh run view --log`) e pedir ao Igor que confirme no celular que o álbum e a legenda chegaram e salvam na galeria. Os dados de amanhã ainda não terão `nome_curto`/`linha_capa` só se a skill falhar; nesse caso a capa usa o nome do tema (conferir).
