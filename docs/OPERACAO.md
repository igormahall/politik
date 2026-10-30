# Politik — operação

Detalhes técnicos: como o robô funciona, como configurar e como calibrar.
O que é o Politik e seus critérios estão no [README](../README.md).

- Design: `docs/superpowers/specs/2026-10-29-politik-design.md`
- Regras editoriais (o que o Claude segue): `editorial/GUIA.md`

## Como funciona

Todo dia às 10:13 UTC (6h13 em Manaus), com repescagem às 12:13 UTC se a primeira não rodar, o GitHub Actions roda `.github/workflows/diario.yml`:

1. `coletar`: Câmara, Senado, Assembleia do AM, Câmara de Manaus, Diário Oficial da União, 16 feeds de imprensa
   e as tramitações de projetos já acompanhados → `data/brutos/<dia>/` (temporário, fora do git).
   As votações da Câmara são agrupadas pelo projeto votado.
2. `filtrar`: separa destaques (até 25), notícias (até 60) e itens menores → `data/selecionados/<dia>.json`
   (guarda todos os itens do dia; é o registro bruto que fica no histórico)
3. **Claude Code** (sua assinatura) roda `/traduzir <dia>` → fichas (com `importancia` 1–3), temas e diário
   em `data/`. Ele só pode ler `data/` e `editorial/` e só pode escrever em `data/`.
4. `validar`: confere o que o Claude escreveu; o que estiver errado volta para a fila
5. `site`: gera o site → GitHub Pages
6. `enviar`: manda o resumo no Telegram
7. salva `data/` no repositório (é o histórico)

Se uma fonte cai ou a cota do Claude acaba, o resumo sai do mesmo jeito, com um aviso.

Outros workflows: **Carga de tema** (`carga-tema.yml`, manual: monta o passado de um tema com pesquisa na web)
e **Testes** (`testes.yml`, a cada push de código: `ruff` + `pytest`).

## Configuração (uma vez só)

1. **Repositório público no GitHub.** Crie o repositório `politik` (público) e envie este código:
   ```bash
   git remote add origin git@github.com:<seu-usuario>/politik.git
   git push -u origin main
   ```
2. **GitHub Pages.** No repositório: *Settings → Pages → Source: GitHub Actions*.
3. **Claude GitHub App.** Instale em https://github.com/apps/claude, só para este repositório.
4. **Bot do Telegram.**
   - No Telegram, fale com **@BotFather** → `/newbot` → guarde o token.
   - Mande qualquer mensagem para o seu bot novo.
   - Abra `https://api.telegram.org/bot<TOKEN>/getUpdates` no navegador e pegue o número em `"chat":{"id": ...}`.
5. **INLABS (Diário Oficial da União).** Faça o cadastro grátis em https://inlabs.in.gov.br.
6. **Token do Claude.** No laptop, com o Claude Code logado na sua conta Pro:
   ```bash
   claude setup-token
   ```
   O token aparece **uma vez só**. Copie na hora e anote a validade que o comando informar, para lembrar de renovar.
7. **Segredos.** Em *Settings → Secrets and variables → Actions → New repository secret*, cadastre:

   | Nome | Valor |
   |---|---|
   | `CLAUDE_CODE_OAUTH_TOKEN` | o token do passo 6 |
   | `TELEGRAM_BOT_TOKEN` | o token do @BotFather |
   | `TELEGRAM_CHAT_ID` | o número do passo 4 |
   | `INLABS_EMAIL` | seu e-mail do INLABS |
   | `INLABS_SENHA` | sua senha do INLABS |

8. **Primeiro teste.** *Actions → Politik diário → Run workflow*. Em ~10 minutos o resumo chega no Telegram.
9. **Carga do caso Master.** *Actions → Carga de tema → Run workflow* com
   `slug=caso-master`, `nome=Caso Master`, `descricao=Banco Master e Daniel Vorcaro`.
   Confira o tema no site. Se faltar parte da história, rode de novo: ele continua de onde parou
   (primeiro confirma fatos de fonte única, depois preenche lacunas, depois busca fatos novos).

## Calibrando

- **Cota do Claude:** cada execução registra turnos e duração em `data/uso.jsonl`.
  Referência: um dia com ~21 destaques e 60 notícias levou **37–41 turnos e 3–5 minutos**.
  Se a cota apertar, baixe `teto_destaques` / `teto_noticias` em `config/filtro.toml`.
- **O que vira destaque:** `config/filtro.toml` (siglas, tipos do DOU, termos de homenagem que vão para os menores).
- **Veículos de imprensa:** `config/imprensa.toml`.
- **Tom e regras dos textos:** `editorial/GUIA.md`.

## Segurança

- **Segredos** só existem em *GitHub Secrets*; nada sensível é gravado em `data/` ou no site.
  O histórico do git foi auditado em 30/10/2026 sem nenhuma credencial encontrada.
- Cada segredo só entra no passo que precisa dele: INLABS no `coletar`, Telegram no `enviar`,
  token de push só no commit (`persist-credentials: false` no checkout).
- Erros de envio ao Telegram nunca carregam a URL (que contém o token).
- O **Claude** lê conteúdo de terceiros (notícias, páginas): por isso só escreve em `data/`, e o código é
  restaurado do git logo depois do passo dele.
- Links no site só aceitam `http(s)`; textos são escapados.
- Actions fixadas por commit (SHA); o Dependabot abre PRs semanais para atualizá-las.

## Rodando no laptop

```bash
python -m venv .venv && .venv/bin/pip install -e .[dev]
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest
.venv/bin/python -m politik coletar --data 2026-10-28
.venv/bin/python -m politik filtrar --data 2026-10-28
claude -p "/traduzir 2026-10-28" --allowedTools "Read(data/**),Read(editorial/**),Edit(data/**),Glob" --max-turns 60
.venv/bin/python -m politik validar --data 2026-10-28
.venv/bin/python -m politik site --saida site_build --base-url "file://$PWD/site_build"
```

## Avisos

- O token do Claude é **pessoal**. Ele serve para o Politik rodar para você. Antes de abrir para outras
  pessoas (Instagram, canal público), reavalie os termos de uso: pode ser preciso usar a API paga.
- Workflows agendados em repositório público param após 60 dias sem commits. Os commits diários do próprio robô evitam isso.
