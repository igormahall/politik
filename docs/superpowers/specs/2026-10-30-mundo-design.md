# Seção "Mundo" — design

Data: 30/10/2026.

## Intenção

O Igor quer que o Politik seja **o boletim diário do que aconteceu no país, no estado e no mundo**. Hoje ele
cobre o Congresso, o Diário Oficial, o Amazonas, Manaus e a imprensa brasileira. Falta o mundo: **os
principais fatos internacionais do dia, com ênfase no que afeta o Brasil**, no mesmo tom claro, direto e sem
viés. O Igor pediu, desde o início, **atenção e esmero para não propagar informação falsa ou enviesada**;
isso é a razão de ser das regras abaixo, mais rígidas que as da parte nacional.

## Metas

- Todo dia, de **3 a 5 fatos internacionais**, cada um numa ficha curta em linguagem simples.
- Entram: os fatos que **afetam o Brasil** e os **grandes acontecimentos** do dia, mesmo sem ligação com o
  Brasil (ex. um terremoto devastador, o início de uma guerra) — decidido pelo Igor.
- A seção aparece no boletim do Telegram, no site e no carrossel do Instagram.

## Não metas

- Órgãos oficiais estrangeiros (governos, parlamentos, ONU) como fonte: **só imprensa** (decidido pelo Igor).
- Cobertura completa do noticiário internacional, editorias de variedades, esporte, celebridades.
- Análise, previsão ou opinião do Politik.

## Antimetas (falhou mesmo que funcione)

- **Publicar um fato internacional confirmado por uma fonte só.**
- **O Politik prever consequências com a própria voz** ("isso vai encarecer o dólar"). Todo impacto é
  atribuído a quem o afirmou.
- Escolher fatos ou enquadrá-los pela posição política de quem está envolvido; os critérios do
  `editorial/GUIA.md` §1 (neutralidade) valem integralmente.
- A seção "Mundo" atrasar, encarecer demais ou derrubar o boletim nacional, que é o produto principal.

## Fontes (decidido pelo Igor, após verificação dos feeds em 30/10/2026)

Só feeds RSS gratuitos e oficiais dos próprios veículos, todos testados e respondendo:

| Organização | Feeds | Observação |
|---|---|---|
| BBC | `https://feeds.bbci.co.uk/portuguese/rss.xml` (BBC News Brasil), `https://feeds.bbci.co.uk/news/world/rss.xml` | ~35 itens/dia cada |
| DW | `https://rss.dw.com/rdf/rss-br-all` (DW Brasil), `https://rss.dw.com/rdf/rss-en-world` | o feed em português mistura temas (~60 itens) |
| Agência Brasil – Internacional | `https://agenciabrasil.ebc.com.br/rss/internacional/feed.xml` | republica material da **Reuters** e da **EFE**; é a porta de entrada da Reuters no Politik |

Reuters, AP e AFP diretas foram testadas e **não têm feed aberto** (401/403/404); ficam de fora. Atalhos
como o Google Notícias foram descartados (só manchete e termos de uso duvidosos). RFI Brasil e France 24
funcionam e podem entrar no futuro; não fazem parte desta versão.

O BBC News Brasil e a DW Brasil publicam também sobre o Brasil. **A fronteira (minha regra) é onde o fato
acontece ou quem age:** se o fato principal acontece no exterior ou é um ato de governo, organismo ou empresa
estrangeira — inclusive quando é sobre o Brasil (tarifa dos EUA sobre o Brasil, Lula discursando na ONU,
acordo Mercosul–UE) —, é Mundo. Se é um ato de instituição brasileira no Brasil (o Congresso votar a
ratificação do acordo), é nacional. Essa separação **é decisão do Claude**, seguindo o guia; o filtro em código
**não** filtra por assunto (só janela de tempo, organização da fonte e teto de itens). Um mesmo fato não vira
ficha nacional e do Mundo ao mesmo tempo: vale a regra acima.

## Regras editoriais (decididas pelo Igor)

1. **Duas fontes, sempre.** Um fato só entra se **pelo menos duas organizações diferentes** o relatam.
   A fonte conta pela **organização** (minha regra): BBC em português e BBC em inglês valem uma; a Agência
   Brasil vale como ela mesma, citando a agência original quando a matéria for da Reuters ou da EFE
   (ex. "Agência Brasil/Reuters"). Não existe "aviso de fonte única" no Mundo: o fato com uma fonte só
   simplesmente não entra. Detalhe do **fato** que só uma das fontes traz não entra no texto.
2. **Impacto atribuído.** O "por que importa para o Brasil" só existe quando alguma fonte disser isso, e
   sempre com o dono da afirmação: "O Itamaraty disse que…", "Analistas ouvidos pela Reuters preveem…".
   Exemplo aprovado pelo Igor (versão B):
   > O Itamaraty disse que vai buscar diálogo com o novo governo. Analistas ouvidos pela Reuters e pelo
   > Financial Times preveem pressão sobre o dólar; a Confederação Nacional da Indústria citou risco para
   > as exportações de aço.
   **Uma fonte basta para cada declaração de impacto (caminho B, decidido pelo Igor)**, sempre nomeando quem
   disse e onde foi publicado ("o Itamaraty disse, segundo a Agência Brasil, que…"). O impacto pode vir também
   da **imprensa brasileira que o Politik já coleta** (Agência Brasil, g1, Folha etc.), onde costuma aparecer
   a reação do governo e das entidades brasileiras. Essas fontes nacionais servem **só** ao impacto: não contam
   como segunda organização para confirmar o fato.
   Grande acontecimento sem ligação com o Brasil: a ficha não tem esse campo (nunca inventar uma ligação).
3. **Seleção:** 3 a 5 fatos. Primeiro os que afetam o Brasil (segundo as fontes), depois os grandes
   acontecimentos. Dia fraco pode ter menos de 3; nunca encher com fato menor para chegar a 3. "Grande
   acontecimento", na falta de critério melhor (minha regra): é destaque nas duas organizações ou em todas
   as três ao mesmo tempo e envolve vidas, guerra/paz, eleição ou decisão de chefe de Estado de país
   relevante, ou mercado global.
4. Linguagem e neutralidade: as mesmas do `editorial/GUIA.md` (§1 e §2). O guia ganha uma seção "Mundo"
   com as regras 1–3 acima.

## Ficha do Mundo

Campos (o construtor define nomes finais e o esquema, seguindo o padrão das fichas atuais):

- **titulo**: o fato, em linguagem simples, mesmas regras de título do guia (§3).
- **o_que_aconteceu**: 2–4 frases, só o que as duas (ou mais) fontes concordam.
- **importa_para_o_brasil** (opcional): só com afirmação atribuída, como na regra 2.
- **fontes**: pelo menos **duas organizações diferentes entre BBC, DW e Agência Brasil – Internacional**,
  cada uma com nome e URL da matéria — são elas que confirmam o fato.
- **fontes_impacto** (opcional): as matérias citadas no `importa_para_o_brasil` (qualquer veículo coletado),
  cada uma com nome e URL. Não contam para a regra das duas fontes.
- **importancia**: 1–3, como as fichas nacionais.

O código (não só o Claude) **verifica** a regra das duas fontes: ficha do Mundo com menos de duas
organizações distintas nas `fontes` é inválida e sai, do mesmo jeito que o `validar` já remove fichas ruins.
O mapeamento URL→organização (domínio `bbc.co.uk`/`bbc.com` → BBC, `dw.com` → DW,
`agenciabrasil.ebc.com.br` → Agência Brasil) fica no código.

Fatos do Mundo podem alimentar **temas em andamento** (ex. a eleição americana), seguindo as regras de temas
do guia (§6). Minha regra: o tema ganha o campo `internacional: true`; fatos do Mundo só entram em temas
internacionais, e temas internacionais só recebem fatos do Mundo. O `validar` exige duas organizações em cada
entrada da linha do tempo de um tema internacional. Temas nacionais não mudam.

## Onde aparece

- **Telegram:** uma seção "🌍 Mundo" depois das novidades oficiais, com o título de cada ficha e o link para
  a página dela no site (como as fichas nacionais).
- **Site:** uma página por ficha do Mundo, como as fichas nacionais, e a seção no resumo do dia.
- **Carrossel:** o slide "Também hoje" ganha o grupo "Mundo" (já previsto no design do carrossel), depois de
  Federal, Amazonas e Manaus. O limite de 5 itens do slide continua, mas **o Mundo tem até 2 lugares
  garantidos** quando houver fichas do Mundo (minha regra: o Igor quer um boletim de país, estado *e* mundo; num
  dia cheio, o Mundo não pode sumir). O total continua em **no máximo 8 slides**. Na capa, "Mais N
  movimentações oficiais" passa a contar só as nacionais, e o Mundo aparece como "N fatos do mundo".

## Restrições

- Custo zero: só feeds gratuitos; o Claude continua sendo o mesmo da tradução diária (sem chamada extra).
- O volume dos feeds (~200 itens/dia somando todos) **não pode** ir inteiro para o Claude: o código filtra
  antes (últimas 24h, fora a política brasileira, títulos e resumos curtos), com um teto de itens, como o
  `teto_noticias` atual. O valor do teto é escolha do construtor, medido para não estourar o `--max-turns`
  da tradução.
- Se os feeds internacionais falharem, o boletim sai sem a seção, com o aviso de fonte indisponível que o
  Politik já usa.
- Ações do GitHub fixadas por SHA; runner `ubuntu-24.04`; nomes e estilo do repositório.

## Decidido pelo Igor

- Haver a seção, com os principais fatos do mundo e ênfase no que afeta o Brasil.
- Só imprensa; fontes BBC, DW e a Reuters via Agência Brasil (AP e AFP sem acesso aberto).
- Impacto sempre atribuído (versão B), com uma fonte bastando para cada declaração de impacto, inclusive da
  imprensa brasileira (caminho B).
- Duas fontes confirmando, sem exceção.
- 3 a 5 fatos por dia, incluindo grandes acontecimentos sem ligação com o Brasil.

## Escolhas minhas (o Igor pode revisar)

- A fonte conta pela organização; BBC português + inglês = uma.
- Critério de "grande acontecimento" da regra 3.
- Validação das duas fontes também em código, não só no guia.
- Seção no fim do Telegram ("🌍 Mundo") e grupo "Mundo" no carrossel.
- Fronteira Mundo × nacional pelo lugar do fato e por quem age; decidida pelo Claude, não por filtro de assunto.
- Temas internacionais marcados com `internacional: true`, sem misturar com temas nacionais.
- Até 2 lugares garantidos para o Mundo no slide "Também hoje".

## Deixado para o construtor

- Novo coletor (provavelmente uma variante do coletor de imprensa, com uma categoria "mundo") e o filtro.
- Esquema da ficha do Mundo, mudanças no `validar`, na skill `/traduzir`, no `editorial/GUIA.md`, no site,
  no Telegram e no carrossel.
- Como o Claude agrupa matérias sobre o mesmo fato entre fontes diferentes.
- Testes, com dados de exemplo como o resto do projeto.

## Mudanças depois do design (30/10/2026)

- Carrossel: as contagens da capa saíram (ver o spec do carrossel). O Mundo aparece na linha "Também hoje" da
  capa e continua com até 2 lugares garantidos no slide de fichas.
