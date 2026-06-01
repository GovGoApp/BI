# Auditoria BI Suprimentos v3 - Zoho x Claude

Gerado para revisar o arquivo `BI Suprimentos v3.html` contra o inventario real do Zoho Analytics.

## O que foi verificado

- Pagina local: `zoho/docs/claude_design/BI Suprimentos v3.html`.
- Inventario completo do workspace Zoho `SUPRIMENTOS`.
- Dashboards exportados do Zoho:
  - `PAINEL RESUMO`
  - `PAINEL FORNECEDOR`
  - `PAINEL INFLACAO`
  - `PAINEL ADIANTAMENTO`
  - `PAINEL CP`
  - `PAINEL SERVICOS`
- Views de cotacao exportadas em CSV para auditoria:
  - `CONTAGEM de COTACOES`
  - `CONTAGEM de COTACOES por ABC`
  - `CONTAGEM DE COTACOES por CAT`
  - `CONTAGEM de COTACOES por UF`
  - `MIN COTACAO por FORN`
  - `MIN COTACAO por FORN - COTACOES <= 3`
  - `NUMERO de COTACOES por PRODUTO`
  - `RELATORIO DE COTACOES`
- Amostras locais ja perfiladas:
  - `COT`
  - `NUM_COT`
  - `COT_MIN_FORN`
  - `INFLACAO`
  - exemplos de impacto em `zoho/output/quiz_suprimentos`.

Observacao: novas consultas ao Zoho foram parcialmente limitadas por excesso de requisicoes consecutivas. Os exports de algumas views de impacto falharam por limite de valores distintos do Zoho, mas o erro retornou os campos relevantes: `MESANO`, `PRE_MIN_COT`, `PMP`, `VAR_COT`, `TOTAL` e `IMP_COT`.

## Resultado curto

1. A critica esta correta: a aba de cotacoes da v3 nao representa bem os principais graficos e tabelas do painel de cotacao do Zoho.
2. A v3 tambem nao traz varios componentes de outros paineis do workspace `SUPRIMENTOS`, especialmente Fornecedor, Adiantamento, Resumo, Produtos e Inflacao.
3. Houve confusao conceitual na v3 entre `IMP` e `INF`.
4. `IMP` deve ser tratado como impacto economico/oportunidade de compra, especialmente impacto de cotacao.
5. `INF` deve ser tratado como variacao de preco/PMP no tempo.

## Cobertura dos dashboards exportados

### PAINEL RESUMO

| Componente Zoho | Status na v3 | Acao |
|---|---|---|
| `SUP por GEO - N e NE` | Falta | Criar grafico geografico/por regional |
| `SUP por GEO - S e SE` | Falta | Criar grafico geografico/por regional |
| `CAT por MES` | Falta | Criar grafico temporal de categorias |
| `CAT por UF` | Falta | Criar grafico categoria x UF |
| `CAT_UF` | Existe parcialmente | Manter e deixar como tabela/pivot oficial |
| `RESUMO NEGOCIOS` | Existe parcialmente | Manter e fortalecer |
| `RESUMO_FILIAL` | Existe parcialmente | Manter e cruzar com aba Filiais |
| `RESUMO - FORN` | Existe parcialmente | Manter e cruzar com Fornecedor 360 |

### PAINEL FORNECEDOR

| Componente Zoho | Status na v3 | Acao |
|---|---|---|
| `FORNECEDORES IMPACTO sobre COTACAO` | Falta como tabela oficial | Criar bloco dedicado |
| `FORNECEDORES e PRODUTOS - IMPACTO` | Falta como tabela oficial | Criar tabela fornecedor x produto x impacto |
| `FORNECEDORES INFLACAO` | Falta como tabela oficial | Criar ranking separado de inflacao |
| `FORNECEDORES e PRODUTOS - INFLACAO` | Falta como tabela oficial | Criar detalhe fornecedor x produto x inflacao |
| `FORNECEDORES TOTAL` | Falta como tabela oficial | Criar ranking total |
| `FORNECEDORES por CAT` | Falta como tabela oficial | Criar distribuicao por categoria |
| `FORNECEDORES por CAT 2` | Falta como tabela oficial | Criar distribuicao por CAT2 |
| `CP_STATUS` | Existe | Manter |

### PAINEL INFLACAO

| Componente Zoho | Status na v3 | Acao |
|---|---|---|
| `INFLACAO por MES por CAT - %` | Falta como grafico oficial | Criar linha/area por CAT |
| `INFLACAO por MES por CAT - R$` | Falta como grafico oficial | Criar grafico R$ separado |
| `TOP INFLACAO` | Existe parcialmente | Manter |
| `TOP DEFLACAO` | Existe parcialmente | Manter |
| `INFLACAO por PRODUTO e CAT` | Falta | Criar tabela produto x categoria |
| `INFLACAO NACIONAL` | Falta | Criar painel nacional |
| `INFLACAO por UF` | Falta | Criar painel por UF |

### PAINEL ADIANTAMENTO

| Componente Zoho | Status na v3 | Acao |
|---|---|---|
| `Adiantamento %` | Falta como card/grafico oficial | Criar |
| `Adiantamento por Mes` | Falta como grafico oficial | Criar |
| `Adiantamento por UF` | Falta como grafico oficial | Criar |
| `AD por UF` | Falta como grafico/tabela oficial | Criar |
| `AD por CAT` | Falta como grafico/tabela oficial | Criar |
| `AD por PRODUTO %` | Falta como tabela oficial | Criar |
| `AD por PRODUTO e UF` | Falta como tabela oficial | Criar |
| `AD por FORNECEDOR` | Falta como tabela oficial | Criar |
| `AD por FORNECEDOR e UF` | Falta como tabela oficial | Criar |

### PAINEL CP

| Componente Zoho | Status na v3 | Acao |
|---|---|---|
| `CP_STATUS` | Existe | Manter |

Complementar com views do inventario:

- `CP_STATUS-TOTAL`
- `CP_SALDO_26`
- `CP_SALDO_DIVIDA_2026`
- `CP_SEMANA`

### PAINEL SERVICOS

| Componente Zoho | Status na v3 | Acao |
|---|---|---|
| `DESPESAS por UF` | Existe | Manter |
| `DESPESAS por UF e CAT` | Existe | Manter |
| `SERVICOS` | Existe | Manter |
| `SERVICOS por MES` | Existe | Manter |

## Painel COTACAO

O dashboard `PAINEL COTACAO` nao foi exportado com sucesso, mas o inventario e os exports das views mostram que ele deve ser muito mais completo do que a aba atual da v3.

### Views obrigatorias de cotacao

| View Zoho | O que representa | Status na v3 |
|---|---|---|
| `CONTAGEM de COTACOES` | Distribuicao mensal por quantidade de cotacoes | Falta como grafico oficial |
| `CONTAGEM de COTACOES por ABC` | Cobertura de cotacao por curva ABC do ID | Falta |
| `CONTAGEM DE COTACOES por CAT` | Cobertura de cotacao por categoria | Falta |
| `CONTAGEM de COTACOES por UF` | Cobertura de cotacao por UF | Falta |
| `COTACOES DE PRECOS - TODOS (CONSULTA PRECO COTACAO)` | Consulta ampla de precos cotados | Falta como tabela oficial |
| `COTACOES por PRODUTO` | Historico de cotacoes por produto | Falta |
| `RELATORIO DE COTACOES` | Relatorio amplo produto x fornecedor x meses | Falta |
| `MIN COTACAO por FORN` | Fornecedor com menor preco por produto/mes | Falta |
| `MIN COTACAO por FORN - COTACOES <= 3` | Mesma logica filtrada para baixa concorrencia | Falta |
| `NUMERO de COTACOES por PRODUTO` | Produto x mes com quantidade de cotacoes e minimo | Falta como matriz |
| `IMPACTO de COTACAO NACIONAL` | Impacto de cotacao consolidado nacional | Falta |
| `IMPACTO de COTACAO por UF` | Impacto de cotacao por UF | Falta |
| `IMPACTO por COTACAO` | Grafico de impacto por cotacao | Falta |
| `IMP_COT_ID` | Impacto de cotacao por ID | Falta |
| `IMP_PROD` | Impacto por produto | Falta |
| `IMP_PROD_2` | Impacto por produto, variante | Falta |

### Evidencias dos exports de cotacao

| Arquivo auditado | Linhas | Colunas principais |
|---|---:|---|
| `contagem_cotacoes.csv` | 280 | `MESANO`, `QTD_COT`, contagens |
| `contagem_cotacoes_abc.csv` | 81 | `CURVA_ID`, `QTD_COT`, contagens |
| `contagem_cotacoes_cat.csv` | 126 | `MESANO`, `CAT2`, contagens |
| `contagem_cotacoes_uf.csv` | 61 | `UF`, `QTD_COT`, contagens |
| `min_cotacao_forn.csv` | 8851 | `POS_FORN`, `CNPJ_MENOR_PRECO`, `FORN_MENOR_PRECO`, `POS_ID`, `NMPRODUTO_EST`, meses |
| `min_cotacao_forn_cot_le_3.csv` | 8851 | mesma estrutura, foco em baixa concorrencia |
| `numero_cotacoes_produto.csv` | 5808 | `POS_ID`, `CURVA_ID`, `ID`, `NMPRODUTO_EST`, meses, `#`, `MIN` |
| `relatorio_cotacoes.csv` | 12722 | `POS_PROD`, `UF`, `NMPRODUTO_OFICIAL`, `NMRAZSOCFORN`, meses, `Min PRECOUNIT_EST` |

## Painel PRODUTOS

O dashboard `PAINEL PRODUTOS` tambem nao foi exportado, mas o inventario mostra views que devem aparecer na v3:

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

A v3 tem uma pagina de produtos e precos, mas ainda nao replica essas visoes como componentes oficiais.

## Correcao conceitual: IMP nao e INF

### IMP

`IMP` deve ser lido como impacto economico em reais. No contexto de cotacao, o foco principal e o impacto de comprar acima da menor cotacao disponivel.

Formula operacional observada nas amostras:

```text
IMP_COT = (VLRUNITPOND_EST - PRE_MIN_COT) * QTDE_EST
```

Em linguagem de negocio, isso pode ser exibido como:

```text
Impacto de cotacao = (PMP/preco medio comprado - menor cotacao) * quantidade comprada
```

Campos relacionados:

- `PRE_MIN_COT`
- `FORN_MIN_COT`
- `IMP_COT`
- `IMP_COT_ID`
- `IMP_ID`
- `IMP_PROD`
- `IMP_PROD_2`
- `IMPACTO de COTACAO NACIONAL`
- `IMPACTO de COTACAO por UF`

Esse bloco pertence principalmente a:

- Cotações
- Oportunidades
- Fornecedor 360
- Produtos e Preços

### INF

`INF` deve ser lido como inflacao/variacao de preco no tempo, normalmente a partir de PMP e series mensais.

Campos relacionados:

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

Esse bloco pertence principalmente a:

- Inflacao
- Categoria
- Produtos e Precos

### Regra para o design

Nao usar `IMP` como sinonimo de inflacao.

Nao misturar `IMPACTO de COTACAO` com `INFLACAO por MES por CAT` no mesmo grafico sem deixar claro que sao duas metricas diferentes.

Pode existir uma visao cruzada, mas com nomes separados:

- `Impacto de cotacao R$`
- `Inflacao PMP %`
- `Exposicao inflacionaria R$`
- `Prioridade combinada: impacto de cotacao alto + inflacao alta`

## O que a v3 deve corrigir

1. Recriar a aba `Cotacoes` com os componentes reais do Zoho.
2. Criar uma subarea `Impacto de Cotacao` dentro de `Cotacoes` ou `Oportunidades`.
3. Renomear a aba `Inflacao e impacto` para `Inflacao` ou dividir em duas abas:
   - `Impacto de Cotacao`
   - `Inflacao`
4. Incluir todos os componentes de Fornecedor, Adiantamento, Resumo e Produtos que ficaram ausentes.
5. Mostrar os nomes das views Zoho nos subtitulos ou em etiquetas discretas, para facilitar o futuro binding de dados.

