# Politik

**O que o poder público fez ontem, explicado em linguagem simples e sem opinião.**

Todo dia de manhã, o Politik lê o que foi publicado oficialmente em três níveis (**federal**, **Amazonas**
e **Manaus**), cruza com a imprensa e entrega um resumo curto: o que aconteceu, quem fez, de qual partido
e o que muda na prática.

🌐 Site com as fichas e o histórico: **https://igormahall.github.io/politik**

## Por que existe

Acompanhar política é difícil para quem não é da área:

- **Não se sabe onde se informar.** Quase toda fonte já chega com a leitura de alguém: jornalista,
  comentarista, lado político.
- **A fonte original é ilegível.** Leis, decretos e projetos são escritos em linguagem jurídica.
- **Falta contexto.** Um documento solto não diz quem propôs, em que pé está nem o que muda para você.

O Politik nasceu depois das eleições de 2026, da vontade de entender o que é feito em nome do cidadão,
para poder **acompanhar, cobrar e explicar** a outras pessoas.

## O que você recebe

- **Um resumo diário** (por volta das 6h de Manaus), aberto pelos **⭐ mais importantes** do dia e depois organizado
  em 🇧🇷 Federal, 🌳 Amazonas e 🏙️ Manaus.
- **Fichas** para cada item: *o que é · quem propôs · o que muda pra você · próximo passo · fontes*.
- **Temas em andamento**: assuntos que se desenrolam por meses (como o caso Banco Master) ganham
  linha do tempo, "resumo até aqui" e "me explica do zero". O resumo diário avisa quando há novidade.
- **Histórico** consultável no site.

## Critérios

### Neutralidade

- Relata **o que aconteceu, quem fez e o que muda**. Sem adjetivos, opinião ou especulação.
- **Nunca** diz se algo é bom ou ruim, nem recomenda posição.
- Da imprensa, aproveita **só os fatos**. Declarações aparecem como declarações ("X disse que…").
- Todo item tem **link para a fonte**. Fato vindo de um único veículo é sinalizado: *"segundo apenas…"*.
- O partido aparece sempre junto do autor: "Dep. Fulano (PARTIDO–UF)".
- **Nenhum fato sem fonte.** O que não está num documento ou numa notícia citada não entra.

### O que entra no resumo

Por dia são publicadas centenas de itens, e a maioria é burocracia. O Politik separa:

- **Destaques:** projetos de lei e emendas à Constituição, leis, decretos e medidas provisórias
  publicadas, votações em plenário (agrupadas pelo projeto votado) e mudanças de situação de projetos já
  acompanhados. São no máximo 25 por dia.
- **Itens menores:** requerimentos, pareceres, homenagens, títulos de cidadão, nomes de rua e atos de
  rotina. **Nada é descartado em silêncio**: eles ficam listados no site, com o texto original.
- Qualquer item ligado a um **tema em andamento** sobe para os destaques, mesmo que seja de rotina.

### Importância (a ordem do resumo)

Cada item recebe um nível de importância. O critério é **impacto**, nunca mérito ou lado político:

| Nível | Quando |
|---|---|
| ⭐ **Alta** | Já vale ou passou numa votação decisiva **e** afeta muita gente diretamente (dinheiro, impostos, preços, benefícios, saúde, educação, segurança, direitos, eleições), ou é um fato novo concreto num tema em andamento |
| **Média** | Avançou uma etapa relevante num assunto de alcance amplo, ou é uma proposta nova que mudaria algo para muita gente |
| **Baixa** | Proposta de alcance restrito, data comemorativa, homenagem ou ato de rotina |

Na dúvida, vale o nível mais baixo. São no máximo cerca de 5 itens de importância alta por dia.

### Como escreve

- **Títulos dizem sozinhos o essencial**: o que muda e para quem, sem número de lei, sem nome de autor e
  sem jargão de tramitação.
  *"Divórcio pode ser decidido logo no início do processo"*, e não *"Senado recebe PL 3.303/2025"*.
- Frases curtas, para quem não é do direito. Termo técnico só com explicação.
- "O que muda pra você" é sempre concreto. Se ainda é só uma proposta, diz isso.

As regras completas estão no [guia editorial](editorial/GUIA.md).

## Fontes

- **Oficiais:** Câmara dos Deputados, Senado Federal, Diário Oficial da União, Assembleia Legislativa do
  Amazonas e Câmara Municipal de Manaus.
- **Imprensa:** agências públicas (Agência Brasil, Agência Câmara, Agência Senado) e veículos nacionais de
  linhas editoriais diferentes, além de veículos do Amazonas. A lista completa está em
  [`config/imprensa.toml`](config/imprensa.toml).

## Limites

- Os textos são produzidos por inteligência artificial (Claude), seguindo o guia editorial e uma validação
  automática. **Erros podem acontecer: sempre confira a fonte original**, que está linkada em cada item.
- Ainda não cobre os diários oficiais do Amazonas e de Manaus.
- Hoje é um projeto pessoal, em calibração. A ideia é abrir para mais pessoas depois.

## Transparência

O código, os critérios e todo o histórico gerado são públicos neste repositório.
Detalhes técnicos, configuração e operação estão em [`docs/OPERACAO.md`](docs/OPERACAO.md).
