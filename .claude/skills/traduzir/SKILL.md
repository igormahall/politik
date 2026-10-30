---
name: traduzir
description: Traduz os destaques de um dia do Politik em fichas em linguagem simples e atualiza os temas em andamento. Uso: /traduzir AAAA-MM-DD
allowed-tools: Read(data/**), Read(editorial/**), Edit(data/**), Glob
---

# Traduzir o dia

Argumento: a data `D` (AAAA-MM-DD).

Você só lê e escreve arquivos dentro de `data/` e lê `editorial/`. Não use outras ferramentas,
não acesse a internet, não use conhecimento próprio sem fonte.

## Passos

1. Leia `editorial/GUIA.md` inteiro. Ele manda em tudo abaixo.
2. Leia `data/selecionados/D.json`. Interessam `destaques` (itens oficiais) e `noticias` (imprensa).
3. Liste e leia os temas ativos em `data/temas/*.json` (`"ativo": true`).
4. Para **cada** item de `destaques`, escreva uma ficha em `data/fichas/<id_seguro>.json`
   (`id_seguro` = `id` trocando `:` e `/` por `_`). Use `titulo`, `ementa`, `autores`, `extra`
   e `url`/`url_documento` do item. Itens de `tramitacao` com `extra.item_origem`: a ficha explica
   a mudança daquele projeto. Se um destaque não tiver informação suficiente para uma ficha honesta,
   escreva a ficha com o que há, dizendo claramente o que a fonte não informa.
   Siga à risca as regras de **titulo** (§3) e dê a **importancia** pelos critérios da §5 do guia (`"importancia"`: 1, 2 ou 3).
5. Temas: usando destaques **e** notícias,
   - atualize temas existentes que tenham novidade (acrescente na `linha_do_tempo`; se já houver entradas
     com data D — o dia está sendo refeito —, substitua essas entradas em vez de acrescentar de novo; reescreva
     `resumo_ate_aqui` e `explica_do_zero`, `ultima_novidade = D`, inclua os ids em `temas` das fichas ligadas);
   - crie temas novos só pelas regras do guia (§4).
6. **Por último**, escreva `data/diario/D.json`, com `fichas` ordenadas da mais para a menos importante, listando todas as fichas escritas e os temas com novidade hoje.

Trabalhe em lotes: leia tudo uma vez, escreva os arquivos em sequência, sem reler o que já escreveu.

## Formatos

Ficha:
```json
{"item_id": "camara:123", "nivel": "federal|estadual|municipal", "tipo_simples": "Projeto de lei",
 "situacao": "Proposta apresentada", "titulo": "...", "o_que_e": "...", "quem_propos": "Dep. Fulano (PT–AM)",
 "o_que_muda": "...", "proximo_passo": "...", "fontes": [{"nome": "Câmara dos Deputados", "url": "https://..."}],
 "fonte_unica": false, "temas": ["slug"], "data": "D", "importancia": 2}
```

Tema:
```json
{"slug": "caso-master", "nome": "Caso Master", "inicio": "AAAA-MM-DD", "ativo": true, "ultima_novidade": "D",
 "palavras_chave": ["Banco Master", "Vorcaro"], "resumo_ate_aqui": "...", "explica_do_zero": "...",
 "linha_do_tempo": [{"data": "AAAA-MM-DD", "fato": "...", "fontes": [{"nome": "Agência Brasil", "url": "https://..."}],
                     "fonte_unica": false}]}
```

Diário:
```json
{"data": "D", "temas": [{"slug": "caso-master", "novo_hoje": "...", "aviso_fonte_unica": "Lista divulgada só pelo veículo X." }],
 "fichas": ["camara:123", "aleam:materia:9"]}
```
`aviso_fonte_unica` é `null` quando não houver.

Todos os campos de texto são obrigatórios e não podem ficar vazios. Toda `url` começa com `http`.
A `linha_do_tempo` fica em ordem crescente de data.
