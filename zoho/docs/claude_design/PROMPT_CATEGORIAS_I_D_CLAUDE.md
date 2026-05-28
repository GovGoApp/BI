# Prompt para Claude - filtros CAT1 a CAT5 somente I e D

Atualize o mock `BI Suprimentos v2.html` para corrigir os filtros de categoria.

Use SOMENTE estas duas categorias de `CAT1`, exatamente nesta ordem:

1. `I - INSUMOS`
2. `D - DESPESAS`

Nao inclua `A - ATIVOS`, `F - FATURAMENTO` nem `V - VENDA BALCAO` nos filtros principais.

A ordenacao dos codigos deve ser crescente dentro de cada nivel:

- Para insumos: `I0`, `I1`, `I2`, `I3`, `I4`, `I5`, `I6`.
- Para despesas: `D1`, `D2`, `D3`, `D4`, `D5`, `D6`, `D7`, `D8`.
- Nos niveis seguintes, tambem ordenar pelo codigo: `I001`, `I003`, `I101`, `I102`... / `D101`, `D102`, `D201`...

Implemente filtro em cascata:

`CAT1 -> CAT2 -> CAT3 -> CAT4 -> CAT5`

Regras:

- Selecionou `CAT1`, mostrar apenas `CAT2` filhos.
- Selecionou `CAT2`, mostrar apenas `CAT3` filhos.
- Selecionou `CAT3`, mostrar apenas `CAT4` filhos.
- Selecionou `CAT4`, mostrar apenas `CAT5` filhos.
- Cada nivel deve ter opcao `Todos`.
- A UI deve deixar claro que `CAT1` e o nivel mais amplo e `CAT5` e o mais especifico.
- A selecao deve atualizar visualmente KPIs, rankings e tabelas, mesmo que os dados sejam ficticios.

Use a arvore completa de categorias do arquivo `CATEGORIAS_I_D_ORDENADAS.md` como fonte para montar os filtros.

Resumo de `CAT2`, na ordem correta:

`I - INSUMOS`:

- `I0 - NUTRICIONAIS`
- `I1 - ESTOCAVEIS`
- `I2 - PERECIVEIS`
- `I3 - HORTIFRUTI`
- `I4 - DESCARTAVEIS`
- `I5 - LIMPEZA`
- `I6 - GAS`

`D - DESPESAS`:

- `D1 - VESTUARIOS/EPIS`
- `D2 - ESCRITORIO`
- `D3 - MANUTENCAO`
- `D4 - CONSTRUCAO`
- `D5 - SERVICOS`
- `D6 - COMPRA A VISTA`
- `D7 - CESTA BASICA`
- `D7 - COMODATO`
- `D8 - UTENSILIOS`

Na aba `Categorias`, priorize a navegacao por arvore e rankings. O usuario deve conseguir clicar em `I - INSUMOS > I2 - PERECIVEIS > I201 - CARNES > I2011 - BOVINOS` e ver os `CAT5` correspondentes.
