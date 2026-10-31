# Politik — operação

Detalhes técnicos: como o robô funciona, como configurar e como calibrar.
O que é o Politik e seus critérios estão no [README](../README.md).

- Design: `docs/superpowers/specs/2026-10-29-politik-design.md`, com o carrossel do Instagram
  (`2026-10-30-carrossel-instagram-design.md`) e a seção Mundo (`2026-10-30-mundo-design.md`) na mesma pasta
- Regras editoriais (o que o Claude segue): `editorial/GUIA.md`

## Como funciona

Todo dia às 6h13 de Manaus (10:13 UTC), com repescagem às 8h13, um agendador externo (cron-job.org) dispara
`.github/workflows/diario.yml` pela API do GitHub, com `agendado=true`. O agendamento do próprio GitHub (`schedule`,
nos mesmos horários) fica no arquivo só de reserva: ele nunca disparou neste repositório (veja
[Por que um agendador externo](#por-que-um-agendador-externo)). Uma execução automática que encontra o dia já
processado não faz nada, então os gatilhos podem se sobrepor sem repetir o resumo. O botão *Run workflow* sempre
processa. O GitHub Actions então roda:

1. `coletar`: Câmara, Senado, Assembleia do AM, Câmara de Manaus, Diário Oficial da União, 16 feeds de imprensa
   e as tramitações de projetos já acompanhados → `data/brutos/<dia>/` (temporário, fora do git).
   Para a seção Mundo, também os feeds internacionais de `config/mundo.toml` (BBC, DW e Agência Brasil –
   Internacional).
   As votações da Câmara são agrupadas pelo projeto votado.
2. `filtrar`: separa destaques (até 25), notícias (até 60), itens do Mundo (até 80, em rodízio entre as
   organizações) e itens menores → `data/selecionados/<dia>.json` (guarda todos os itens do dia; é o registro
   bruto que fica no histórico). A tramitação de um projeto apresentado no mesmo dia não vira uma segunda ficha.
3. **Claude Code** (sua assinatura, modelo Claude Haiku 5.5) roda `/traduzir <dia>` → fichas (com `importancia` 1–3), fichas do Mundo
   (`data/mundo/`, só fatos confirmados por duas organizações), temas e diário em `data/`. Ele só pode ler `data/` e `editorial/` e só pode escrever em `data/`.
4. `validar`: confere o que o Claude escreveu; o que estiver errado volta para a fila. Ficha do Mundo sem
   duas organizações, ou com link que não foi coletado no dia, sai.
5. `site`: gera o site → GitHub Pages
6. `enviar`: manda o resumo no Telegram
7. `carrossel`: desenha o carrossel do Instagram (1080×1350, até 8 slides) e manda no mesmo chat do Telegram,
   como álbum de fotos + legenda pronta para copiar. Se falhar, o resumo e o histórico não são afetados.
8. salva `data/` no repositório (é o histórico)

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
9. **Agendador (sem ele o resumo não sai sozinho).**
   - **Token só para disparar o workflow.** No GitHub: *Settings → Developer settings → Personal access tokens →
     Fine-grained tokens → Generate new token*. Nome `politik-agendador`; validade: a mais longa oferecida (anote a
     data); *Repository access → Only select repositories → politik*; *Permissions → Actions → Read and write*.
   - **cron-job.org** (grátis). Crie a conta e, em *Create cronjob*:

     | Campo | Valor |
     |---|---|
     | URL | `https://api.github.com/repos/<seu-usuario>/politik/actions/workflows/diario.yml/dispatches` |
     | Agenda | personalizada: minuto `13`, horas `6` e `8`, todos os dias; fuso `America/Manaus` |
     | Método (*Advanced*) | `POST` |
     | Cabeçalhos | `Authorization: Bearer <token>`, `Accept: application/vnd.github+json`, `Content-Type: application/json` |
     | Corpo | `{"ref":"main","inputs":{"agendado":"true"}}` |
     | Notificações | avisar em caso de falha e quando o job for desativado |

   - **Teste.** *Test run* deve responder HTTP 200 ou 204, e uma execução nova aparece em *Actions*. Se o dia já foi
     processado, ela termina em segundos sem fazer nada.
10. **Carga do caso Master.** *Actions → Carga de tema → Run workflow* com
   `slug=caso-master`, `nome=Caso Master`, `descricao=Banco Master e Daniel Vorcaro`.
   Confira o tema no site. Se faltar parte da história, rode de novo: ele continua de onde parou
   (primeiro confirma fatos de fonte única, depois preenche lacunas, depois busca fatos novos).

## Calibrando

- **Cota do Claude:** cada execução registra turnos e duração em `data/uso.jsonl`.
  Referência: um dia com ~21 destaques e 60 notícias levou **37–41 turnos e 3–5 minutos**; com o Mundo e o
  Haiku (29/10), **43 turnos e ~6 minutos**, cerca de 8% da sessão de 5 horas do Pro. O teto é `--max-turns 80`.
  Se a cota apertar, baixe `teto_destaques` / `teto_noticias` em `config/filtro.toml`.
- **O que vira destaque:** `config/filtro.toml` (siglas, tipos do DOU, termos de homenagem que vão para os menores).
- **Veículos de imprensa:** `config/imprensa.toml`; do Mundo, `config/mundo.toml` (cada feed diz a que
  organização pertence; a regra das duas fontes conta organizações, não feeds).
- **Tom e regras dos textos:** `editorial/GUIA.md`.

## Segurança

- **Segredos** só existem em *GitHub Secrets*; nada sensível é gravado em `data/` ou no site.
  O histórico do git foi auditado em 30/10/2026 sem nenhuma credencial encontrada.
- Cada segredo só entra no passo que precisa dele: INLABS no `coletar`, Telegram no `enviar`,
  token de push só no commit (`persist-credentials: false` no checkout).
- Erros de envio ao Telegram nunca carregam a URL (que contém o token).
- O **Claude** lê conteúdo de terceiros (notícias, páginas), que pode trazer instruções escondidas. As skills
  mandam tratar esse texto como dado, e o pipeline não confia no que ele escreve:
  - só escreve em `data/`, e o código é restaurado do git logo depois do passo dele;
  - `selecionados/<dia>.json`, `pendentes.json` e `uso.jsonl` são guardados antes e restaurados depois;
  - `validar` desfaz mudanças em diários, fichas e fichas do Mundo de outros dias, e um tema internacional
    não pode perder a marca;
  - se a validação falhar, nada do que o Claude escreveu é commitado (a repescagem das 8h13 tenta de novo).
- O **token do agendador** (guardado só no cron-job.org) tem apenas a permissão *Actions* deste repositório: dispara
  e cancela execuções, mas não lê segredos nem muda código. Se vazar, revogue em *Settings → Developer settings*.
- Links no site só aceitam `http(s)`; textos são escapados.
- Actions fixadas por commit (SHA); o Dependabot abre PRs semanais para atualizá-las.

## Por que um agendador externo

Em 30 e 31/10/2026 o `schedule` do GitHub não criou nenhuma execução, em nenhum horário (10:00, 10:13 e 12:13 UTC):
`gh api "repos/<seu-usuario>/politik/actions/runs?event=schedule"` respondia `total_count: 0`. Tudo do nosso lado
estava certo: workflow ativo, arquivo no branch padrão, repositório público com commits recentes, cron válido.
Não era atraso nem descarte no minuto :00 (mudar o horário não resolveu): o agendador do GitHub simplesmente não
disparava. Em 2026 há vários relatos iguais na comunidade do GitHub, sem resposta oficial nem solução, e a própria
documentação trata o `schedule` como melhor esforço (pode atrasar e pode ser descartado). Já o disparo pela API
(`workflow_dispatch`) sempre funcionou. Por isso o horário é responsabilidade do agendador externo.

**O resumo não chegou?** Veja primeiro o histórico do job no cron-job.org: 401, 403 ou 404 = token vencido, errado
ou sem a permissão *Actions*; 422 = corpo errado. Depois, *Actions → Politik diário*. Para processar o dia na hora:
*Run workflow*.

## Rodando no laptop

```bash
python -m venv .venv && .venv/bin/pip install -e .[dev,carrossel] && .venv/bin/playwright install chromium
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/pytest
.venv/bin/python -m politik coletar --data 2026-10-28
.venv/bin/python -m politik filtrar --data 2026-10-28
claude -p "/traduzir 2026-10-28" --allowedTools "Read(data/**),Read(editorial/**),Edit(data/**),Glob" --model claude-haiku-5-5 --max-turns 80
.venv/bin/python -m politik validar --data 2026-10-28
.venv/bin/python -m politik site --saida site_build --base-url "file://$PWD/site_build"
# carrossel (envia ao Telegram)
TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... .venv/bin/python -m politik carrossel --data 2026-10-28
```

## Avisos

- O token do Claude é **pessoal**. Ele serve para o Politik rodar para você. Antes de abrir para outras
  pessoas (Instagram, canal público), reavalie os termos de uso: pode ser preciso usar a API paga.
- Workflows agendados em repositório público param após 60 dias sem commits. Os commits diários do próprio robô evitam isso.
