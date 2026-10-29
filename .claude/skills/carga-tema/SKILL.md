---
name: carga-tema
description: Monta (ou completa) a linha do tempo de um tema do Politik desde o primeiro fato relevante, com fonte em tudo. Uso: /carga-tema <slug> "<nome>" "<descrição curta>"
allowed-tools: Read(data/**), Read(editorial/**), Edit(data/temas/**), Glob, WebSearch, WebFetch
---

# Carga inicial de tema

Argumentos: `slug`, `nome` e `descrição` do tema (ex.: `caso-master "Caso Master" "Banco Master e Daniel Vorcaro"`).

Leia `editorial/GUIA.md` antes de tudo. Ele manda em tudo abaixo, especialmente a neutralidade.

## Regras extras desta carga

- **Só entram fatos de páginas que você mesmo abriu com WebFetch nesta execução**, cada um com a URL da página.
  Um resultado de busca (WebSearch) não basta como fonte: abra a página.
- **Nada de conhecimento próprio.** Se você "sabe" algo mas não achou numa página aberta, não escreva.
- Priorize, nesta ordem: órgãos oficiais (Banco Central, Polícia Federal, STF, STJ, Câmara, Senado, TCU, DOU,
  Ministério Público), agências públicas (Agência Brasil, Agência Câmara, Agência Senado) e veículos de acesso aberto.
- **Nunca** tente contornar paywall. Página bloqueada = ignore.
- Fato encontrado em uma fonte só → `fonte_unica: true`.
- Busque fontes de linhas editoriais diferentes quando o fato for disputado. Registre declarações como declarações
  ("X disse que …"), sem tomar lado.

## Passos

1. Se `data/temas/<slug>.json` já existe, leia-o: você vai **continuar** de onde parou (preencher lacunas de período,
   acrescentar fatos que faltam), sem apagar o que já tem fonte.
2. Pesquise o tema do começo até hoje. Descubra o primeiro fato relevante e os marcos principais (decisões oficiais,
   operações, prisões, julgamentos, CPIs, normas publicadas).
3. Monte a `linha_do_tempo` em ordem crescente de data, um fato por entrada.
4. Escreva `resumo_ate_aqui` (2 a 3 frases) e `explica_do_zero` (até ~6 parágrafos curtos, separados por linha em
   branco, só com fatos da linha do tempo).
5. `palavras_chave`: nomes próprios e termos específicos que identificam o tema em documentos oficiais e notícias
   (ex.: "Banco Master", "Vorcaro", "BRB"). Nada genérico.
6. `inicio` = data do primeiro fato; `ultima_novidade` = data do fato mais recente; `ativo: true`.
7. Grave `data/temas/<slug>.json` no formato:

```json
{"slug": "caso-master", "nome": "Caso Master", "inicio": "AAAA-MM-DD", "ativo": true, "ultima_novidade": "AAAA-MM-DD",
 "palavras_chave": ["..."], "resumo_ate_aqui": "...", "explica_do_zero": "...",
 "linha_do_tempo": [{"data": "AAAA-MM-DD", "fato": "...", "fontes": [{"nome": "...", "url": "https://..."}],
                     "fonte_unica": false}]}
```

Se a cota ou os turnos estiverem acabando, **grave o que já tem** (válido e com fontes) antes de parar.
Uma próxima execução continua o trabalho.
