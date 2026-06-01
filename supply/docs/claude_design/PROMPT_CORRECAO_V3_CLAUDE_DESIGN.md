# Prompt para Claude - Correcao da v3 do BI Suprimentos

Use este prompt para revisar o mock `BI Suprimentos v3.html`.

Gere um novo arquivo:

```text
BI Suprimentos v3.1.html
```

Nao sobrescreva `BI Suprimentos v3.html`.

## Objetivo

Corrigir a v3 para ficar mais fiel aos paineis reais do Zoho Analytics, especialmente:

1. Painel de cotacoes.
2. Painel de fornecedor.
3. Painel de produtos.
4. Painel de adiantamento.
5. Separacao correta entre `IMP` e `INF`.

Mantenha a identidade visual atual da v3, mas melhore a estrutura analitica.

## Correcao principal: IMP nao e INF

Na v3 atual houve confusao entre impacto e inflacao.

Trate os conceitos assim:

### IMP / Impacto de cotacao

Impacto e a perda/oportunidade economica de comprar acima da menor cotacao disponivel.

Use a formula de negocio:

```text
Impacto de cotacao = (PMP/preco medio comprado - menor cotacao) * quantidade comprada
```

Nos dados, os campos principais sao:

- `PRE_MIN_COT`
- `FORN_MIN_COT`
- `IMP_COT`
- `IMP_COT_ID`
- `IMP_ID`
- `IMP_PROD`
- `IMP_PROD_2`
- `IMPACTO de COTACAO NACIONAL`
- `IMPACTO de COTACAO por UF`
- `IMPACTO por COTACAO`

Nao explique impacto como inflacao.

### INF / Inflacao

Inflacao e variacao de PMP no tempo.

Use campos como:

- `PMP_ID`
- `PMP_ID_1`
- `PMP_ID_12`
- `PMP_0` a `PMP_12`
- `SOMA_INF_ID_1`
- `SOMA_INF_ID_PMP`
- `PERC_INF_ID_1`
- `PERC_INF_ID_PMP`
- `INF_ID`
- `INF_ID_PMP`
- `INF_PROD_PMP`
- `PMP_ID_INF_12`
- `PMP_PROD_INF_12`

Inflacao pode ter efeito em reais, mas nao e a mesma coisa que impacto de cotacao.

## Mudanca de abas

Na v3.1, ajuste a navegacao assim:

1. Resumo Executivo
2. Oportunidades
3. Categorias
4. Filiais
5. Estoque por Filial
6. Fornecedor 360
7. Produtos e Precos
8. Cotacoes
9. Impacto de Cotacao
10. Inflacao
11. Fiscal 2027
12. Financeiro / CP
13. Adiantamentos
14. Servicos
15. Qualidade dos Dados

Se preferir reduzir abas, `Impacto de Cotacao` pode ser uma subaba forte dentro de `Cotacoes`, mas visualmente precisa ficar separado de `Inflacao`.

## Refazer a aba Cotacoes

A aba atual de cotacoes esta simplificada demais. Ela precisa representar os blocos reais do Zoho.

### Cards de topo

Inclua cards para:

- Produtos cotados.
- Cobertura de cotacao.
- Media de cotacoes por produto.
- Produtos com `0 cotacao`.
- Produtos com `1 cotacao`.
- Produtos com `<= 3 cotacoes`.
- Potencial `IMP_COT`.
- Percentual comprado no menor preco.

### Bloco 1 - CONTAGEM de COTACOES

Criar grafico temporal/empilhado com origem:

```text
CONTAGEM de COTACOES
```

Campos:

- `MESANO`
- `QTD_COT`
- contagem de produtos/IDs

Mostrar a distribuicao de 0, 1, 2, 3, 4, 5+ cotacoes ao longo dos meses.

### Bloco 2 - CONTAGEM de COTACOES por ABC

Criar matriz ou grafico empilhado com origem:

```text
CONTAGEM de COTACOES por ABC
```

Campos:

- `CURVA_ID`
- `QTD_COT`
- contagem

O usuario precisa ver rapidamente se os itens curva A/AA/AAA estao com baixa concorrencia.

### Bloco 3 - CONTAGEM DE COTACOES por CAT

Criar grafico categoria x mes com origem:

```text
CONTAGEM DE COTACOES por CAT
```

Campos:

- `MESANO`
- `CAT2`
- contagem

Dar destaque para categorias relevantes como pereciveis, estocaveis, hortifruti, descartaveis, servicos, EPIs, manutencao e ativos.

### Bloco 4 - CONTAGEM de COTACOES por UF

Criar mapa/tabela/matriz com origem:

```text
CONTAGEM de COTACOES por UF
```

Campos:

- `UF`
- `QTD_COT`
- contagem

Mostrar UFs com maior risco de baixa cotacao.

### Bloco 5 - Consulta de precos

Criar tabela de consulta com origem:

```text
COTACOES DE PRECOS - TODOS (CONSULTA PRECO COTACAO)
```

Use colunas como:

- ID
- produto
- UF
- fornecedor
- mes
- preco cotado
- curva fornecedor
- curva ID

### Bloco 6 - COTACOES por PRODUTO

Criar uma tabela/ranking com origem:

```text
COTACOES por PRODUTO
```

Mostrar produto, ID, categoria, UF, fornecedores cotados, minimo, medio, maximo e status.

### Bloco 7 - NUMERO de COTACOES por PRODUTO

Criar matriz ampla com origem:

```text
NUMERO de COTACOES por PRODUTO
```

Estrutura observada no CSV:

- `POS_ID`
- `CURVA_ID`
- `ID`
- `NMPRODUTO_EST`
- meses em colunas
- pares `#` e `MIN`
- `Summary`

Essa matriz e importante porque mostra a disciplina de cotacao por produto ao longo dos meses.

### Bloco 8 - MIN COTACAO por FORN

Criar matriz/tabela com origem:

```text
MIN COTACAO por FORN
```

Estrutura observada:

- `POS_FORN`
- `CNPJ_MENOR_PRECO`
- `FORN_MENOR_PRECO`
- `POS_ID`
- `NMPRODUTO_EST`
- meses em colunas

Mostrar quais fornecedores aparecem mais vezes como menor preco.

### Bloco 9 - MIN COTACAO por FORN - COTACOES <= 3

Criar bloco especifico de risco com origem:

```text
MIN COTACAO por FORN - COTACOES <= 3
```

Objetivo: mostrar produtos em que a menor cotacao existe, mas a competicao foi baixa.

### Bloco 10 - RELATORIO DE COTACOES

Criar tabela ampla com origem:

```text
RELATORIO DE COTACOES
```

Estrutura observada:

- `POS_PROD`
- `UF`
- `NMPRODUTO_OFICIAL`
- `NMRAZSOCFORN`
- meses em colunas
- `Min PRECOUNIT_EST`

Este deve ser o relatorio operacional principal.

## Criar aba/subaba Impacto de Cotacao

Esta area nao pode ficar misturada com inflacao.

Componentes obrigatorios:

- `IMPACTO de COTACAO NACIONAL`
- `IMPACTO de COTACAO por UF`
- `IMPACTO por COTACAO`
- `IMP_COT_ID`
- `IMP_ID`
- `IMP_PROD`
- `IMP_PROD_2`
- `PRODUTOS por ID - MIN COT`

### Cards de topo

Inclua:

- Impacto de cotacao total R$.
- Impacto nacional R$.
- Impacto por UF lider.
- Produtos/IDs com maior `IMP_COT`.
- Fornecedores mais frequentes como menor preco nao escolhido.
- Percentual comprado acima do menor preco.

### Tabela principal

Colunas:

- ID
- Produto oficial
- Categoria
- UF
- Fornecedor comprado
- Fornecedor menor preco
- PMP/preco medio comprado
- Menor cotacao
- Quantidade
- `IMP_COT`
- Curva ID
- Status

Use status como:

- Comprou no menor
- Acima do menor
- Sem cotacao
- Baixa concorrencia

## Refazer Inflacao

Renomeie a aba `Inflacao e impacto` para `Inflacao`.

Inclua os componentes reais:

- `INFLACAO por MES por CAT - %`
- `INFLACAO por MES por CAT - R$`
- `TOP INFLACAO`
- `TOP DEFLACAO`
- `INFLACAO por PRODUTO e CAT`
- `INFLACAO NACIONAL`
- `INFLACAO NACIONAL por CATEGORIA`
- `INFLACAO por UF`
- `INFLACAO por UF e por CAT`
- `INFLACAO por RESUMO de UF`
- `INFLACAO total`
- `INF_ID`
- `INF_ID_PMP`
- `INF_PROD_PMP`

Mostrar duas leituras separadas:

- variacao percentual de PMP;
- exposicao monetaria da inflacao.

Nao chamar `IMP_COT` de inflacao.

## Completar Fornecedor 360

Incluir blocos/tabelas com estes nomes de view do Zoho:

- `FORNECEDORES IMPACTO sobre COTACAO`
- `FORNECEDORES e PRODUTOS - IMPACTO`
- `FORNECEDORES INFLACAO`
- `FORNECEDORES e PRODUTOS - INFLACAO`
- `FORNECEDORES TOTAL`
- `FORNECEDORES por CAT`
- `FORNECEDORES por CAT 2`
- `FORNECEDORES por UF e CAT`
- `FORNECEDORES TOTAL - POR ANO`
- `FORNECEDORES_25_26`
- `PMP_FORN`
- `CP_STATUS`

Separar visualmente:

- impacto de cotacao por fornecedor;
- inflacao por fornecedor;
- volume total comprado;
- categorias atendidas;
- risco financeiro/CP.

## Completar Produtos e Precos

Incluir blocos/tabelas com estes nomes:

- `PRODUTOS por CAT`
- `PRODUTOS por ID`
- `PRODUTOS por ID - MIN COT`
- `PRODUTOS por ID e FORN`
- `PRODUTOS por PROD`
- `PRODUTOS por UF`
- `PADRONIZACAO PRODUTOS`
- `PMP_PROD_ABC`
- `PMP_PROD_ID`
- `PMP_PROD_INF_12_x`
- `PMP_ID_INF_12_x`
- `PMP_UF`
- `PMP por CAT`
- `PMP por PROD`
- `PMP por UF`

## Completar Resumo Executivo

Incluir estes componentes do Zoho:

- `SUP por GEO - N e NE`
- `SUP por GEO - S e SE`
- `CAT por MES`
- `CAT por UF`
- `CAT_UF`
- `RESUMO NEGOCIOS`
- `RESUMO_FILIAL`
- `RESUMO - FORN`

## Completar Adiantamentos

Incluir estes componentes:

- `Adiantamento %`
- `Adiantamento por Mes`
- `Adiantamento por UF`
- `AD por UF`
- `AD por CAT`
- `AD por PRODUTO %`
- `AD por PRODUTO e UF`
- `AD por FORNECEDOR`
- `AD por FORNECEDOR e UF`
- `AD por MES e CAT`
- `CONCILIACAO_ AD`
- `CONCILIACAO_UF`
- `ADIANTAMENTO_CONC`

## Completar Financeiro / CP

Incluir:

- `CP_STATUS`
- `CP_STATUS-TOTAL`
- `CP_SALDO_26`
- `CP_SALDO_DIVIDA_2026`
- `CP_SEMANA`

## Servicos

Manter e melhorar:

- `DESPESAS por UF`
- `DESPESAS por UF e CAT`
- `SERVICOS`
- `SERVICOS por MES`
- `DESPESAS`
- `DESPESAS FIN`
- `Despesas_2v2v2`

## Regra de rotulagem

Sempre que criar uma tabela, card ou grafico inspirado diretamente no Zoho, coloque no subtitulo:

```text
Origem Zoho: NOME_DA_VIEW
```

Exemplo:

```text
Menor preco por fornecedor
Origem Zoho: MIN COTACAO por FORN
```

Isso e essencial para a fase seguinte de ligacao com dados reais.

## Regras de design

- Mantenha o visual denso, executivo e operacional.
- Nao transformar em landing page.
- Usar tabelas compactas, cards objetivos e graficos de leitura rapida.
- Nao misturar cards dentro de cards.
- Nao esconder os paineis importantes atras de texto explicativo.
- Priorizar leitura por compra, filial, fornecedor, produto, categoria, UF e mes.
- Garantir que a pagina rode como HTML unico.

