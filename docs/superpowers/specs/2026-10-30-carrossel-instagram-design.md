# Carrossel diário para o Instagram — design

Data: 30/10/2026. Etapa 1 de 2 (a etapa 2, publicar sozinho pela Instagram Graph API, fica para depois).

## Intenção

O Igor quer levar o Politik para o Instagram. Quem parar no post precisa sentir que **recebeu um boletim
diário do que aconteceu**, com informação clara, direta e sem viés político. O nome continua **Politik**
(decidido depois de comparar alternativas: ele diz "política" na hora para o leitor comum e tem a origem
estrangeira e sóbria que o Igor queria).

Nesta etapa, o robô diário **gera as artes e a legenda** e as **manda para o Telegram do Igor**; ele salva
no celular e posta à mão. Postar à mão por algumas semanas serve para validar o formato antes de automatizar.

## Metas

- Todo dia, junto com o boletim, gerar um carrossel no formato do Instagram e uma legenda pronta para copiar.
- As artes chegam no Telegram do Igor, fáceis de salvar na galeria do celular.
- Zero custo e zero IA de imagem: as artes são desenhadas por código a partir dos dados do dia.

## Não metas

- Publicar no Instagram automaticamente (etapa 2).
- Cobertura do mundo (projeto à parte, combinado para depois). O formato só precisa deixar espaço para
  uma seção "Mundo" no futuro.

## Antimetas (falhou mesmo que funcione)

- Qualquer coisa que pareça viés: cores de partido (vermelho+verde+amarelo, azul forte), escolha de foto
  ou enquadramento opinativo. As regras de `marca/README.md` e de `editorial/GUIA.md` valem para as artes.
- Texto inventado ou "melhorado" na hora de desenhar. Fora a linha curta da capa (abaixo), **todo texto
  das artes vem literalmente dos dados do dia** já validados.
- Perder o aviso de fonte única: se um tema tem `aviso_fonte_unica`, ele aparece no slide do tema.
- O carrossel atrasar ou derrubar o boletim do Telegram, que é o produto principal.

## O carrossel (aprovado pelo Igor sobre a edição real de 29/10)

Formato: **4:5, 1080×1350 px**, PNG ou JPEG de alta qualidade.

Estilo **C, "As duas águas"** (escolhido entre três): em cada slide, faixa superior Rio Negro (`#2a1f1a`)
com etiqueta em Solimões (`#c9a266`) e título em Espuma (`#f4efe7`); um fio Solimões separa a faixa do
corpo; corpo em fundo Espuma com texto escuro. Rótulos pequenos em maiúsculas na cor `#7a5a2e`. Avisos em
`#8a5300` com fio Solimões à esquerda. Fontes da marca: Bricolage Grotesque 700 nos títulos, Source Sans 3
no texto. Rodapé de todo slide: marca d'água (símbolo pequeno + "politik · os fatos lado a lado", 85% de
opacidade, canto inferior esquerdo) e numeração "n/total" no canto inferior direito.

O modelo de referência visual está em `.superpowers/brainstorm/` (arquivo `carrossel.html`), fora do git;
este documento é a fonte da verdade.

Slides, nesta ordem:

1. **Capa.** Etiqueta com a data por extenso ("quinta-feira, 29 de outubro de 2026"), título "O dia na
   política". Corpo: lista numerada dos temas do dia, cada um com um **nome curto** em negrito e uma
   **linha curta** embaixo; por último, "Mais N movimentações oficiais" quando houver fichas no slide de
   fichas (N = quantas fichas aparecem nele, sem contar o "e mais").
2. **Um slide por tema** do `diario` (na ordem do diário). Etiqueta "Tema em andamento · dia N" (N contado
   desde `inicio`, como no Telegram; para temas muito longos, ex. mais de 60 dias, "desde mmm/aaaa"). Título:
   nome do tema. Corpo: rótulo "Novo hoje" + `novo_hoje`; se houver `aviso_fonte_unica`, o aviso com ⚠.
   Se sobrar espaço, rótulo "Para entender" + a 1ª frase de `resumo_ate_aqui`.
3. **Lista das fichas: um slide só, "Também hoje".** Fichas de importância 1 e 2 de **todos os níveis**
   (o Igor quer país e estado; no futuro, mundo), agrupadas por nível com um subtítulo pequeno
   ("Federal", "Amazonas", "Manaus", na ordem de `NIVEIS` do site) e, dentro do grupo, na ordem do diário.
   Cada item: a situação (em maiúsculas pequenas) e o título; ficha com `fonte_unica` ganha um "⚠ fonte
   única" discreto. Importância 3 fica de fora. Cabem até ~5 itens; o que passar vira
   "e mais N no link da bio".
4. **Fecho.** "Os fatos lado a lado"; "Cada item explicado do zero, com a linha do tempo e as fontes.";
   "Link na bio · boletim diário grátis no Telegram".

### A linha curta da capa (decidido: escrita pelo Claude)

A skill `/traduzir` passa a escrever, para cada tema em `data/diario/D.json`, dois campos novos:
um nome curto do tema para a capa e uma linha curta com o fato do dia (no exemplo: "Flávio Bolsonaro fora
do país" / "PL diz que ninguém aprovou a carta do senador"). Seguem o `editorial/GUIA.md` (sem viés, sem
adjetivo de juízo). O esquema do diário e o `validar` passam a conhecê-los; se faltarem ou forem inválidos,
a capa cai para o nome do tema sem a linha curta, e nada mais quebra.

## Legenda

Uma legenda de texto pronta para colar no Instagram, montada por código a partir dos mesmos dados (sem IA):
data, os temas do dia com a linha curta, a frase de neutralidade/slogan, convite para o link na bio e um
conjunto pequeno e fixo de hashtags neutras (ex. #política #congresso #brasil; a lista exata é escolha do
construtor, sem hashtags partidárias). Respeitar o limite do Instagram (2.200 caracteres).

## Entrega (decidido pelo Igor)

As artes vão para o **mesmo chat do Telegram** que já recebe o boletim (`TELEGRAM_CHAT_ID`, que é o chat
privado do Igor com o bot), **depois** das mensagens do boletim:

- um **álbum** com as imagens, na ordem dos slides (o Igor salva todas na galeria de uma vez);
- uma mensagem com a **legenda**, fácil de copiar.

Falhar ao gerar ou enviar o carrossel **não pode** impedir o envio do boletim nem o commit do histórico.

## Restrições

- Roda dentro do workflow `diario.yml` existente, no runner `ubuntu-24.04`, sem custo.
- Ações do GitHub fixadas por SHA (há teste que exige isso).
- Fontes empacotadas no repositório (licença OFL, permitida), para o resultado não depender da internet
  nem variar entre execuções.
- Datas para leitura sempre em português, nunca `2026-10-28` (regra da marca).

## Dias diferentes do normal

- **Sem tradução** (`sem_traducao`): não gerar carrossel; mandar ao Igor uma linha avisando que hoje não há
  carrossel. Publicar texto original sem tradução contraria o propósito.
- **Tradução parcial** (`parcial`): gerar normalmente com o que existir.
- **Sem temas no dia** (comum nos dias `parcial`): não há slides de tema, e a capa não repete os títulos do
  slide de fichas; ela mostra só "Hoje: N movimentações oficiais" e os níveis que tiveram novidade
  (ex. "Federal · Amazonas"). O carrossel fica capa → fichas → fecho.
- **Nada no dia** (sem temas e sem fichas de importância 1–2): não gerar carrossel; avisar em uma linha.
- **Muitos temas:** no máximo 5 slides de tema (o Instagram aceita até 20 imagens, mas carrossel longo
  ninguém passa); os demais entram só na capa se couberem, senão ficam de fora.
- **Tamanho máximo:** capa + até 5 temas + 1 slide de fichas + fecho = **8 slides**, o que cabe em um
  álbum só do Telegram (limite de 10 por álbum).
- **Texto que não cabe:** o construtor decide a estratégia (reduzir fonte até um mínimo legível, cortar em
  frase inteira com "…"), mas **nunca** cortar o aviso de fonte única.

## Decidido pelo Igor

- Etapa 1 primeiro (artes + postagem manual); automação depois.
- Nome: manter Politik.
- Estilo C; estrutura capa → temas → lista de fichas → fecho; capa com linha curta escrita pelo Claude.
- Entrega no Telegram, pelo celular.

## Escolhas minhas (o Igor pode revisar)

- Desenho por **HTML/CSS renderizado para PNG** com um navegador sem tela (ex. Playwright/Chromium) a
  partir de templates Jinja, como o site já faz. Dá tipografia e quebra de linha boas e reaproveita a
  identidade; custa ~1 minuto a mais no workflow.
- Álbum de **fotos** (não arquivos) no Telegram: o Telegram recomprime um pouco, mas 1080 px de largura
  passa quase intacto e salvar na galeria fica a um toque.
- Regras dos "dias diferentes" acima.
- Importância 3 fora do carrossel.
- Slide de fichas único, "Também hoje", com todos os níveis agrupados, e o marcador de fonte única nas fichas.
- No dia sem temas, a capa não repete os títulos das fichas.

## Deixado para o construtor

- Organização do código (ex. `politik/instagram/` com templates próprios ou reaproveitando `politik/site`),
  nomes de comandos (ex. `python -m politik carrossel --data D`) e onde as imagens ficam durante a execução
  (não precisam ir para o git).
- Estratégia exata de encaixe de texto e tamanhos de fonte, dentro do estilo acima.
- Como testar (com dados de exemplo, como o resto do projeto).

## Pendência antes de abrir ao público

`docs/OPERACAO.md` avisa: o token do Claude é pessoal, e antes de abrir o Politik para outras pessoas
(Instagram, canal público) é preciso reavaliar os termos de uso; pode ser necessário usar a API paga.
Isso não impede construir a etapa 1, mas precisa ser resolvido **antes do primeiro post público**.
