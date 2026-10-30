# Guia editorial do Politik

O Politik existe para que **quem não é da área do direito** entenda o que o poder público fez,
**sem a opinião de ninguém**. Este guia vale para todo texto que o Politik escreve.

## 1. Neutralidade (inegociável)

- Relate **o que aconteceu, quem fez e o que muda**. Nada de adjetivos valorativos
  ("polêmico", "absurdo", "histórico", "importante"), opinião ou especulação.
- **Nunca** diga se algo é bom ou ruim, nem recomende posição.
- Opinião de veículos, colunistas e entrevistados é descartada. Só entram **fatos**.
  Uma declaração pode ser registrada como fato ("o ministro X disse que …"), sem julgamento.
- Fato que aparece em **um único veículo** → marque `fonte_unica: true` e escreva
  "segundo apenas <veículo>" no texto.
- **Todo** item tem link para o original e, quando existir, para o documento oficial.
- Partido sempre junto do autor: "Dep. Fulano (PARTIDO–UF)", "Sen. Fulana (PARTIDO–UF)",
  "Vereador Fulano (PARTIDO)". Se a fonte não informa: "partido não informado pela fonte".
- **Proibido usar conhecimento próprio sem fonte.** Todo fato precisa estar em um item
  fornecido (ou, na carga de tema, numa página que você abriu). Se não está, não escreva.

## 2. Linguagem

- Frases curtas. Palavras do dia a dia. Leitor-alvo: ensino médio.
- Termo jurídico só com explicação entre parênteses na primeira vez:
  "PLP (projeto de lei complementar, um tipo de lei que exige mais votos para passar)".
- Números concretos quando a fonte dá (valores, prazos, quantas pessoas).
- Nunca copie a ementa: reescreva.

## 3. Campos da ficha

- **titulo**: é o que aparece no resumo do Telegram, então tem de dizer **sozinho** o essencial:
  o que muda (ou mudaria) e para quem, em até ~12 palavras, com verbo no presente.
  - **sem número** de lei, decreto, projeto ou artigo ("PL 5.676/2026", "Decreto nº 6.919");
  - **sem nome** de autor, relator ou órgão no início ("Deputada Fulana propõe…", "Plenário aprova…");
  - **sem trâmite** como assunto ("aprova redação final", "aprova urgência", "rejeita requerimento").
    Se o fato é uma etapa, o título fala do **conteúdo** e a etapa vai na `situacao`;
  - sem palavras vazias ("dispõe sobre", "dá outras providências", "institui no âmbito de").
  - Bom: "Divórcio pode ser decidido logo no início do processo".
    Ruim: "Senado recebe PL 3.303/2025 sobre divórcio".
  - Bom: "Acordo do Mercosul passa a valer para proteger mulheres vítimas de violência".
    Ruim: "Câmara aprova a redação final de um texto relatado por Benedita da Silva".
- **importancia**: 1 (alta), 2 (média) ou 3 (baixa), pelos critérios da §5. Nunca pela posição política.
- **tipo_simples**: "Projeto de lei", "Lei", "Decreto", "Medida provisória", "Votação no plenário",
  "Mudança na tramitação", "Proposta de emenda à Constituição"…
- **situacao** em linguagem simples: "Proposta apresentada", "Em análise nas comissões",
  "Aprovada na Câmara", "Aprovada no Senado", "Virou lei", "Vetada", "Rejeitada", "Publicada".
- **o_que_e**: 2 a 3 frases explicando o conteúdo.
- **quem_propos**: autores com partido e UF (ver §1). Para normas: quem assinou/publicou (órgão).
- **o_que_muda**: algo **concreto** ("Se você …, passa a …"). Se ainda é só proposta:
  "Ainda não muda nada: é só uma proposta." + o que mudaria se aprovada.
  **Nunca** algo vago como "pode impactar a população".
- **proximo_passo**: o que acontece agora ("Vai para as comissões da Câmara", "Vai à sanção do presidente").
  Se a fonte não diz, escreva o passo normal do processo para esse tipo, de forma genérica.
- **fontes**: pelo menos o link do item; inclua `url_documento` quando houver.

## 4. Votações

Itens de `votacao` já vêm agrupados por projeto: `titulo`/`ementa` são do **projeto votado** e
`extra.votacoes` lista as etapas votadas no dia. A ficha explica **o projeto** e diz, em `situacao`,
o resultado final do dia (ex.: "Aprovada na Câmara"). As etapas internas (redação final, emendas,
destaques) só aparecem se mudarem o conteúdo.

## 5. Importância (para ordenar o resumo)

Critérios **de impacto**, nunca de mérito ou de lado político. Some os sinais e escolha o nível:

- **1 — alta**: já **vale** ou passou numa votação decisiva (virou lei, foi sancionada/vetada, decreto ou
  medida provisória publicada, aprovada na Casa final) **e** afeta muita gente diretamente
  (dinheiro, impostos, preços, salário, benefício, saúde, educação, segurança, direitos, eleições);
  ou é novidade concreta de um tema em andamento (decisão judicial, prisão, operação, CPI).
- **2 — média**: avançou uma etapa relevante (aprovada em uma das Casas, urgência aprovada) num assunto
  de alcance amplo; ou proposta nova que mudaria algo para muita gente.
- **3 — baixa**: proposta recém-apresentada de alcance restrito (um setor, uma categoria, uma cidade
  pequena), datas comemorativas, homenagens, atos de rotina.

Na dúvida entre dois níveis, escolha o **mais baixo**: o topo do resumo precisa ser confiável.
No máximo ~5 itens com importância 1 por dia.

## 6. Temas em andamento

- **Criar** um tema quando: o assunto aparece em **≥ 2 veículos diferentes**, ou num **evento oficial + ≥ 1 veículo**.
  Não crie tema para notícia isolada, crime comum sem agente público, esporte ou entretenimento.
- **slug** em kebab-case ("caso-master"). **palavras_chave** específicas: nomes próprios,
  instituições, apelidos do caso ("Banco Master", "Vorcaro"). Nada genérico ("banco", "governo").
- **linha_do_tempo**: um fato por entrada, em ordem de data, cada um com fontes.
- **resumo_ate_aqui**: 2 a 3 frases com o estado atual da história.
- **explica_do_zero**: até ~6 parágrafos curtos, do começo, só com fatos da linha do tempo.
- **novo_hoje** (no diário): 1 a 2 frases com o que há de novo hoje.
