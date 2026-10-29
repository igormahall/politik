# Politik — documento de design (v1)

Data: 2026-10-29 · Autor: Igor (com Claude)

## 1. Por que existe

Igor se envolveu com as eleições de 2026, quis entender propostas e o rumo do país, e esbarrou em três problemas:

1. **Não sabe onde se informar.** Não tem hábito de consumir política, e quase toda fonte já chega com a leitura de alguém (jornalista, comentarista, lado).
2. **A fonte original é ilegível.** O que a União, a Assembleia e a Câmara Municipal publicam vem em juridiquês.
3. **Falta contexto.** Uma lei solta não diz quem propôs, de qual partido, em que pé está, o que muda na prática.

Ele não tem lado político definido. O objetivo final é **exercer a cidadania**: entender, cobrar e, mais tarde, ajudar outras pessoas com a mesma dificuldade.

O exemplo que ele deu do que quer receber: o **caso Banco Master / Daniel Vorcaro**, do qual ele não sabia nada. Isso não é uma lei, é uma história que se desenrola ao longo de meses, espalhada por Banco Central, PF, Justiça, Congresso e imprensa. O Politik precisa cobrir isso também.

## 2. O que é (v1)

Um robô que roda **uma vez por dia, sem servidor**, e:

1. **Coleta** o que foi publicado no dia anterior em fontes oficiais (federal, Amazonas, Manaus) e em vários veículos de imprensa de linhas diferentes.
2. **Filtra por código** o que é ruído burocrático, sem descartar nada em silêncio.
3. **Traduz e organiza com o Claude Code** (assinatura Pro do Igor): explica em linguagem simples, classifica, e agrupa em **temas em andamento**.
4. **Guarda tudo** num histórico versionado no repositório.
5. **Publica um site estático** (GitHub Pages) com as fichas, temas e arquivo.
6. **Envia um resumo diário no Telegram** só para o Igor, com botões que abrem as páginas do site.

Público da v1: **só o Igor**. A ideia é calibrar a qualidade por algumas semanas antes de abrir para outras pessoas.

## 3. Metas, não-metas e anti-metas

**Metas**
- Resumo diário confiável, lido em poucos minutos de manhã.
- Cada item compreensível por quem não é da área do direito.
- Cobertura dos três níveis: federal, estadual (AM), municipal (Manaus).
- Temas em andamento com "resumo até aqui" e linha do tempo.
- Histórico consultável.
- **Custo extra zero**: só GitHub grátis, Telegram grátis e a assinatura Claude Pro que ele já paga.

**Não-metas da v1 (ficam para depois)**
- Instagram (perfil público com carrossel diário). Vai exigir reavaliar a autenticação, ver §9.
- Diário Oficial de Manaus e Diário Oficial do Amazonas (sem API, sites difíceis de ler).
- Busca por pergunta livre ("me explica X agora").
- Detalhe de voto por parlamentar, se a fonte complicar. Se sair fácil, entra.
- Abrir para outras pessoas (canal, Discord, etc.).

**Anti-metas (o que faria o Igor desistir, nas palavras dele)**
- **Trazer pouca informação**: assuntos relevantes que não aparecem.
- **Informação vaga**: resumo que não diz o que muda de fato.
- **Classificação errada**: nível, tipo ou situação incorretos.
- E, pelo pedido original: **opinião ou viés** no texto.

## 4. Decisões já tomadas

### 4.1 Fontes

**Oficiais (v1)**. Verificadas em 2026-10-29: todas responderam com dados reais.

| Fonte | Acesso | Observação |
|---|---|---|
| Câmara dos Deputados | `https://dadosabertos.camara.leg.br/api/v2/` (JSON, aberto) | Proposições, autores/partidos, tramitações, votações. ~100+ proposições/dia, a maioria requerimentos e pareceres. |
| Senado Federal | `https://legis.senado.leg.br/dadosabertos/processo` (JSON, aberto) | **Não usar** `/materia/pesquisa/lista`: está descontinuado (desativação anunciada para 2026-02-01, ainda responde). |
| ALEAM (Assembleia do Amazonas) | `https://sapl.al.am.leg.br/api/` (SAPL, JSON aberto) | `materia/materialegislativa`, `norma/normajuridica` (com PDF). ~12 itens/dia, maioria requerimentos/moções. |
| Câmara Municipal de Manaus | `https://sapl.cmm.am.gov.br/api/` (SAPL, JSON aberto) | Matérias e normas, inclusive decretos do executivo municipal com PDF. |
| Diário Oficial da União | INLABS (`inlabs.in.gov.br`), XML grátis, exige cadastro gratuito | A Imprensa Nacional mantém um script Python oficial (`github.com/Imprensa-Nacional/inlabs`). Ler só Seção 1 (atos normativos) na v1. |

**Imprensa**: o Igor aceitou incluir explicitamente ("o que vale mesmo é a informação"). Serve para (a) **detectar temas em andamento** que as fontes oficiais não mostram ou mostram tarde, e (b) **confirmar fatos**. Mínimo: vários veículos nacionais de **linhas editoriais diferentes** e alguns do Amazonas, via RSS quando houver.

Decisões minhas sobre a imprensa:
- **Escopo:** política e governo em sentido amplo. Entra tudo que envolve poder público ou agentes públicos, inclusive economia e regulação (ex.: Banco Central), operações policiais e decisões judiciais com figuras públicas. O caso Master toca todos esses pontos.
- **Pré-filtro por código:** seções/feeds de política, economia e do Amazonas, além de palavras-chave dos temas ativos. Feeds de esporte, entretenimento etc. ficam de fora.
- **Profundidade:** título + resumo do RSS para todos. O texto completo é baixado só de fontes abertas sem paywall, priorizando as agências públicas (Agência Brasil, Agência Câmara, Agência Senado). Nada de contornar paywall.

### 4.2 Neutralidade (regras editoriais)

- Relatar **o que aconteceu, quem fez, o que muda**. Sem adjetivos valorativos, opinião ou especulação.
- **Nunca** dizer se algo é bom ou ruim nem recomendar posição.
- Fato vindo de **uma única fonte** é sinalizado ("segundo apenas o veículo X").
- **Todo item tem link** para o original e, quando existir, para o documento oficial.
- Opinião dos veículos é descartada. Só entram fatos.
- Partido do autor sempre aparece (ex.: "Dep. Fulano (PARTIDO–UF)").

Essas regras vão num guia editorial versionado no repositório e lido pelo Claude em toda execução.

### 4.3 Formato do resumo no Telegram

Escolhido pelo Igor a partir de mockups: **formato C, com fichas do formato B ao tocar.**

Mensagem diária:
1. Cabeçalho: dia, contagem de itens.
2. **🔥 Temas em andamento**: para cada tema com novidade, o nome, há quantos dias está ativo, o "resumo até aqui" (2 a 3 linhas), o "novo hoje" e um aviso de fonte única, quando houver. Botões: **Linha do tempo**, **Me explica do zero**.
3. **📜 Novidades oficiais**: lista curta agrupada em 🇧🇷 Federal, 🌳 Amazonas, 🏙️ Manaus. Uma linha por item, com link para a ficha.
4. Rodapé: "+ N itens menores", com link para a página que lista todos.

**Ficha** (página no site, aberta pelo toque): etiquetas (nível, tipo, situação) · título simples · **O que é** · **Quem propôs** (nome, partido, UF, coautores) · **O que muda pra você** · **Próximo passo** · links: texto oficial, como votaram (quando houver).

### 4.4 Horário

Uma execução por dia, cobrindo **o dia anterior inteiro**. Execução às ~6h de Manaus (10:00 UTC, já que Manaus é UTC−4) e mensagem chegando por volta das 7h de Manaus. O cron do GitHub atrasa às vezes; tolerável.

### 4.5 Plataforma

- **GitHub Actions** (cron diário), **repositório público**. O Igor concordou. Público dá Actions ilimitado e GitHub Pages grátis. Os segredos ficam em GitHub Secrets.
- **Python** para coleta, filtro, armazenamento, geração do site e envio.
- **Claude Code via `anthropics/claude-code-action@v1`** em modo automação (com `prompt`), autenticado com `CLAUDE_CODE_OAUTH_TOKEN` gerado por `claude setup-token` na conta Pro do Igor. Isso está documentado oficialmente em `code.claude.com/docs/en/github-actions`, com exemplo de execução agendada.
- **Bot do Telegram** (Bot API, grátis) mandando para o chat privado do Igor.
- **GitHub Pages** para o site estático.
- O Igor programa ("vibe coding" no trabalho), mas não tem servidor. O laptop fica ligado só de vez em quando, então **nada pode depender dele**.

## 5. Como funciona (arquitetura proposta)

```
cron 10:00 UTC
  │
  ├─ 1. coletar   (Python)  → data/brutos/AAAA-MM-DD/<fonte>.json
  ├─ 2. filtrar   (Python)  → data/selecionados/AAAA-MM-DD.json  + menores (sem IA)
  ├─ 3. traduzir  (Claude Code) lê selecionados + temas + guia editorial
  │                         → data/fichas/<id>.json, data/temas/<slug>.json (atualiza)
  ├─ 4. validar   (Python)  checa o schema do que o Claude escreveu
  ├─ 5. site      (Python)  → gera HTML estático → GitHub Pages
  ├─ 6. enviar    (Python)  → mensagem no Telegram com botões de URL para o site
  └─ 7. commit    dados + site no repositório (o histórico)
```

**Por que o toque abre uma página, e não uma resposta do bot:** sem servidor, o bot não consegue responder a cliques na hora. Os botões do Telegram são **botões de URL** para o site. Bônus: o site já é o arquivo consultável e a base para o futuro Instagram.

**O que conta como "novidade" de um dia** (decisão minha):
- Proposições/matérias **apresentadas** no dia (filtradas por tipo).
- **Eventos de tramitação relevantes** de itens que já estão no histórico ou que passaram no filtro: aprovado/rejeitado em plenário, sancionado/vetado, virou lei/norma.
- **Votações em plenário** (Câmara/Senado).
- **Normas publicadas** (leis, decretos, MPs) no DOU Seção 1 e nas normas jurídicas do SAPL (ALEAM/CMM).
- Matérias de imprensa que alimentam ou criam um tema.

### 5.1 Filtro (o ponto mais delicado)

Ele protege duas coisas: a atenção do Igor e a cota do Pro. Regras por código, baseadas no **tipo** do documento, antes de qualquer IA:

- **Entra (destaque):** PL, PLP, PEC, MPV, PDL, projetos de lei estaduais/municipais, leis e decretos publicados, votações de plenário, mudanças de situação relevantes.
- **Fica nos menores (sem IA):** requerimentos, pedidos de informação, pareceres de relator, moções de aplauso/pesar, homenagens, títulos de cidadania, denominação de ruas e prédios, atos de pessoal no DOU.
- **Nada some em silêncio:** os menores aparecem no site numa página do dia com a ementa original e o link, e a mensagem mostra a contagem.

As listas de tipos ficam num arquivo de configuração editável, para o Igor ajustar durante a calibração.

**DOU Seção 1** (decisão minha): entram leis, decretos, medidas provisórias e emendas constitucionais. Portarias, resoluções e instruções normativas vão para os menores, **exceto** quando o órgão ou o texto bate com um tema ativo (ex.: resolução do Banco Central ligada ao caso Master). Esse cruzamento é por palavras-chave do tema, feito por código.

**Teto diário e prioridade** (decisão minha, ajustar com medição): no máximo **25 itens em destaque por dia** enviados ao Claude, mais as atualizações de temas. Quando passar disso, a ordem de prioridade é:
1. novidades de temas ativos;
2. normas publicadas (leis, decretos, MPs);
3. votações e mudanças de situação;
4. novas proposições (federal > estadual > municipal).

O que sobrar fica pendente **por no máximo 2 dias**. Depois vai para os menores com a ementa original. A primeira semana mede o consumo real da cota (registrar no log de cada execução), e o teto é ajustado a partir daí.

### 5.2 Temas em andamento

- Um tema (ex.: "Caso Master") tem: nome, data de início, "resumo até aqui", linha do tempo (data, fato, fontes), itens oficiais relacionados, estado (ativo/inativo).
- O Claude **cria** um tema quando um assunto aparece em vários veículos e/ou num evento oficial, e **atualiza** quando chega novidade. A cada atualização ele reescreve "resumo até aqui" e "me explica do zero".
- "Me explica do zero" é **pré-gerado** junto com o tema, não sob demanda (sem servidor).
- Um tema fica **inativo após 30 dias sem novidade** (decisão minha) e continua no arquivo.

### 5.2.1 Carga inicial de temas (decisão do Igor)

O Claude **não** usa conhecimento próprio sem fonte. Para que os temas já em andamento comecem com o passado explicado, a v1 tem uma **carga inicial** feita antes da primeira execução diária. Ela começa **só com o caso Master** (Banco Master / Daniel Vorcaro).

- Um processo avulso, disparado manualmente (`workflow_dispatch`), coleta o histórico do tema **desde o primeiro fato relevante** e monta a linha do tempo e o "resumo até aqui", **tudo com fonte**.
- O RSS só traz notícias recentes. Para o passado, usar buscas/arquivos de fontes abertas (agências públicas como Agência Brasil, Agência Câmara e Agência Senado; comunicados do Banco Central e da PF; atos no DOU) e o que os veículos abertos permitirem acessar sem contornar paywall (decisão minha).
- Pode ser dividida em várias execuções para caber na cota do Pro.
- Novos temas com passado para recuperar podem usar o mesmo processo depois, com o nome do tema como parâmetro.

### 5.3 Papel do Claude

O Claude Code recebe arquivos locais e escreve arquivos locais. Não navega nem coleta, porque isso é trabalho do Python: mais barato, mais previsível. Ferramentas permitidas: leitura e escrita dentro de `data/`. Ele:
- escreve as fichas (texto simples, sem juridiquês, mirando um leitor de ensino médio);
- classifica (nível, tipo em linguagem simples, situação);
- liga itens a temas, e cria ou atualiza temas;
- marca fatos de fonte única;
- segue o guia editorial (§4.2).

## 6. Restrições

- **Custo zero além do Pro.** Nada de API paga, servidor ou VPS.
- **Cota do Pro é compartilhada** com o uso diário do Igor (limites por janela de horas e semanais). O volume que chega ao Claude precisa ser pequeno e medido. Usar `--max-turns` e agrupar itens numa única execução.
- **Termos de uso:** os termos permitem o token OAuth para "uso comum e individual" do Claude Code. A v1 é pessoal e roda o Claude Code oficial, sem modificação, então está dentro. **Não** usar o token fora do Claude Code (ex.: chamar a API direto com ele).
- **Repositório público:** nada sensível nos dados. Segredos: `CLAUDE_CODE_OAUTH_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, credenciais do INLABS.
- **Workflows agendados em repositório público** são desativados após 60 dias sem atividade. Os commits diários do próprio robô mantêm o repositório ativo.
- **Telegram:** limite de 4096 caracteres por mensagem. Dividir se passar.
- Idioma de tudo: **português do Brasil**.

## 7. Falhas e degradação

- **Uma fonte fora do ar:** o resumo sai mesmo assim, com aviso "fonte X indisponível hoje". O dia seguinte tenta recuperar o que faltou.
- **Cota do Claude esgotada ou erro na etapa 3:** o resumo sai sem tradução (títulos/ementas originais), com aviso. Os itens ficam pendentes para a próxima execução.
- **Saída do Claude inválida** (falha na etapa 4): mesmo tratamento do item acima, só para os itens inválidos.
- **Execução inteira falhou:** o GitHub avisa o Igor por e-mail (padrão do Actions).

## 8. Como saber se está dando certo

Calibração nas primeiras semanas, com o Igor lendo todo dia e ajustando o filtro e o guia editorial. Sinais de sucesso:
- Ele lê o resumo na maior parte dos dias.
- Ele fica sabendo de assuntos como o caso Master **pelo Politik**.
- Raramente acha uma ficha vaga ou mal classificada.
- A execução cabe com folga na cota do Pro, sem atrapalhar o uso pessoal.

## 9. Futuro (registrado, fora da v1)

- **Instagram:** perfil público com carrossel diário (capa com os temas, um slide por ficha), link da bio para o site. Exige conta Business/Criador, Página do Facebook, app na Meta, token renovado a cada 60 dias e geração de imagens. **Publicar para outras pessoas usando a assinatura Pro provavelmente não se encaixa em "uso individual"**: reavaliar os termos antes. Pode exigir a API paga.
- Diários oficiais de Manaus e do Amazonas.
- Busca no histórico.
- Voto por parlamentar.

## 10. Deixado para quem for construir

- Estrutura exata de pastas, schemas JSON e nomes de arquivo.
- Escolha dos veículos de imprensa e seus feeds (respeitando o critério do §4.1: linhas diferentes, nacionais e do AM).
- Gerador do site (Jinja2 ou similar) e visual, desde que funcione bem no celular.
- Como dividir o trabalho do Claude em uma ou mais chamadas dentro da cota.
- Testes e como rodar localmente.
- Confirmar a validade do token do `claude setup-token` (há relatos de 1 ano) e documentar a renovação.
