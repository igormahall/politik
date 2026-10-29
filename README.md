# Politik

Um robô que, todo dia de manhã, lê o que o poder público publicou (federal, Amazonas e Manaus) e a imprensa,
traduz para linguagem simples **sem opinião** e manda um resumo no Telegram, com um site de fichas e histórico.

- Design: `docs/superpowers/specs/2026-10-29-politik-design.md`
- Regras editoriais (o que o Claude segue): `editorial/GUIA.md`

## Como funciona

Todo dia às 10:00 UTC (6h em Manaus) o GitHub Actions roda `.github/workflows/diario.yml`:

1. `coletar`: Câmara, Senado, Assembleia do AM, Câmara de Manaus, Diário Oficial da União, 16 feeds de imprensa
   e as tramitações de projetos já acompanhados → `data/brutos/<dia>/`
2. `filtrar`: separa destaques (até 25), notícias (até 60) e itens menores → `data/selecionados/<dia>.json`
3. **Claude Code** (sua assinatura) roda `/traduzir <dia>` → fichas, temas e diário em `data/`
4. `validar`: confere o que o Claude escreveu; o que estiver errado volta para a fila
5. `site`: gera o site → GitHub Pages
6. `enviar`: manda o resumo no Telegram
7. salva `data/` no repositório (é o histórico)

Se uma fonte cai ou a cota do Claude acaba, o resumo sai do mesmo jeito, com um aviso.

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
   Confira o tema no site. Se faltar parte da história, rode de novo: ele continua de onde parou.

## Calibrando

- **Cota do Claude:** cada execução registra turnos e duração em `data/uso.jsonl`.
  No teste de 28/10/2026, um dia com 23 destaques e 60 notícias levou **41 turnos e ~5 minutos**.
  Se a cota apertar, baixe `teto_destaques` / `teto_noticias` em `config/filtro.toml`.
- **O que vira destaque:** `config/filtro.toml` (siglas, tipos do DOU, termos de homenagem que vão para os menores).
- **Veículos de imprensa:** `config/imprensa.toml`.
- **Tom e regras dos textos:** `editorial/GUIA.md`.

## Rodando no laptop

```bash
python -m venv .venv && .venv/bin/pip install -e .[dev]
.venv/bin/pytest
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
