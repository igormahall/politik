# Marca do Politik

**Direção: Encontro das Águas.** Em Manaus, o Rio Negro e o Solimões correm lado a lado por quilômetros
sem se misturar. O símbolo do Politik mostra exatamente isso: duas águas, cada uma com sua cor, lado a lado.
É a ideia do serviço: **mostrar os fatos lado a lado, sem escolher um lado**.

**Slogan:** *Os fatos lado a lado.*

## Arquivos

| Arquivo | Uso |
|---|---|
| `simbolo.svg` | Símbolo sozinho (círculo). Também é o favicon do site (`politik/site/favicon.svg`, cópia idêntica). |
| `simbolo-contorno.svg` | Símbolo com contorno Espuma, **obrigatório sobre fundo escuro** (topo do site, modo escuro, posts escuros): sem ele a metade Rio Negro some no fundo. |
| `logo.svg` | Símbolo + nome + slogan, na horizontal. Cabeçalhos, documentos, apresentações. |
| `marca-dagua.svg` | Marca d'água para posts e imagens: símbolo pequeno + "politik · os fatos lado a lado". Herda a cor do texto. |
| `avatar-512.png` | Foto do bot do Telegram e perfis (quadrado; as redes recortam em círculo). Já traz o contorno claro, para não sumir no tema escuro do app. |

## Cores

| Nome | Hex | Uso |
|---|---|---|
| Rio Negro | `#2a1f1a` | Texto forte, fundos escuros, topo do site |
| Solimões | `#c9a266` | Destaques, links no modo escuro, a outra metade do símbolo |
| Espuma | `#f4efe7` | Fundo claro |

As cores vêm do rio, de propósito: **nunca use vermelho, verde e amarelo juntos, ou azul forte** como cor de
marca. O público associa essas cores a partidos.

## Tipografia

- **Bricolage Grotesque** (500/700): nome e títulos.
- **Source Sans 3** (400/600): texto corrido.

Ambas gratuitas, no Google Fonts.

## Regras de uso

- O símbolo é sempre um **círculo**, com o Rio Negro à esquerda e o Solimões à direita. Não espelhe, não gire, não troque as cores.
- O nome é escrito **em minúsculas** na marca (`politik`); no texto corrido, "Politik".
- Marca d'água: canto inferior, pequena, com 85% de opacidade. Nunca sobre o rosto de uma pessoa ou sobre o texto principal.
- Espaço livre ao redor do símbolo: no mínimo metade do diâmetro dele.
- Tamanho mínimo do símbolo: 16 px (favicon).
- Datas para leitura sempre em português ("quarta-feira, 28 de outubro de 2026" ou "28/10/2026"), nunca no formato técnico 2026-10-28.

## Acessibilidade (auditada em 30/10/2026)

Todos os pares de texto e fundo do site passam no WCAG AA (≥ 4,5:1) nos temas claro e escuro;
o menor é o texto das etiquetas, com 4,8:1. O símbolo puro sobre fundo escuro tinha 1:1 na metade Rio Negro,
e por isso existe a versão com contorno.
