# Analise para v3 - Zoho x Claude BI de Suprimentos

Gerado para orientar a criacao do `BI Suprimentos v3.html`.

## Fontes analisadas

- Mock atual: `zoho/docs/claude_design/BI Suprimentos v2.html`.
- Inventario Zoho: `zoho/output/zoho_analytics_inventory/zoho_views_inventory.csv`.
- Dashboards exportados do Zoho:
  - `PAINEL RESUMO`
  - `PAINEL FORNECEDOR`
  - `PAINEL INFLACAO`
  - `PAINEL ADIANTAMENTO`
  - `PAINEL CP`
  - `PAINEL SERVICOS`
- Dashboards nao exportados pela API, mas cobertos pelo inventario:
  - `PAINEL COTACAO`
  - `PAINEL PRODUTOS`
- Categorias reais:
  - `zoho/docs/claude_design/CATEGORIAS_I_D_A_ORDENADAS.md`.
- Estoque fora do workspace SUPRIMENTOS:
  - workspace `APURACAO DE RESULTADOS`.

## Diagnostico geral

A v2 melhorou bastante a v1: trouxe `Categorias`, `Servicos`, filtros em duas linhas e uma primeira simulacao funcional.

Mas a v2 ainda nao esta suficientemente proxima do Zoho por tres motivos:

1. Algumas views reais do Zoho aparecem apenas de forma resumida, nao como cards/tabelas/pivots dedicados.
2. A categoria em cascata ainda esta errada na ordenacao e incompleta: precisa usar `I`, depois `D`, depois `A`, sempre ordenado por codigo.
3. Ainda falta uma area critica que nao esta no workspace SUPRIMENTOS: `Estoque por Filial`, localizado no workspace `APURACAO DE RESULTADOS`.

## Painel Resumo - Zoho

Componentes reais exportados:

| Componente Zoho | Tipo | Situacao na v2 | Acao v3 |
|---|---|---|---|
| `SUP por GEO - N e NE` | Grafico | Parcial | Criar bloco geografico explicito N/NE |
| `SUP por GEO - S e SE` | Grafico | Parcial | Criar bloco geografico explicito S/SE |
| `CAT por MES` | Grafico | Parcial | Criar serie categoria x mes |
| `CAT por UF` | Grafico | Parcial | Criar matriz categoria x UF |
| `CAT_UF` | Tabela/Pivot | Parcial | Criar tabela pivot CAT x UF |
| `RESUMO NEGOCIOS` | Tabela/Pivot | Parcial | Criar tabela por negocio |
| `RESUMO_FILIAL` | Tabela/Pivot | Parcial | Criar ranking por filial |
| `RESUMO - FORN` | Tabela/Pivot | Parcial | Criar ranking por fornecedor |

Melhoria v3:

- O resumo deve deixar de ser apenas executivo e virar um espelho organizado dos principais blocos do Zoho.
- Incluir cards/tabelas nomeadas por tema: `Geografia`, `Categorias`, `Negocios`, `Filiais`, `Fornecedores`.

## Painel Fornecedor - Zoho

Componentes reais exportados:

| Componente Zoho | Tipo | Situacao na v2 | Acao v3 |
|---|---|---|---|
| `FORNECEDORES IMPACTO sobre COTACAO` | Tabela/Pivot | Parcial | Criar tabela dedicada |
| `FORNECEDORES e PRODUTOS - IMPACTO` | Tabela/Pivot | Parcial | Criar detalhe fornecedor x produto x impacto |
| `FORNECEDORES INFLACAO` | Tabela/Pivot | Parcial | Criar ranking fornecedor x inflacao |
| `FORNECEDORES e PRODUTOS - INFLACAO` | Tabela/Pivot | Parcial | Criar detalhe fornecedor x produto x inflacao |
| `FORNECEDORES TOTAL` | Tabela/Pivot | Sim parcial | Melhorar como tabela principal |
| `FORNECEDORES por CAT` | Tabela/Pivot | Parcial | Criar fornecedor x categoria |
| `FORNECEDORES por CAT 2` | Tabela/Pivot | Parcial | Criar fornecedor x CAT2 |
| `CP_STATUS` | Tabela/Pivot | Parcial | Mostrar dentro do detalhe do fornecedor |

Views adicionais do inventario:

- `FORNECEDORES por UF e CAT`
- `FORNECEDORES TOTAL - POR ANO`
- `FORNECEDORES_25_26`
- `PMP_FORN`

Melhoria v3:

- A aba `Fornecedor 360` deve ter subtabs:
  - `Total`
  - `Impacto Cotacao`
  - `Inflacao`
  - `Categorias`
  - `UF/CAT`
  - `CP`
  - `Fiscal`

## Painel Produtos - Zoho

O dashboard nao exportou pela API, mas o inventario mostra as views principais:

| View Zoho | Situacao na v2 | Acao v3 |
|---|---|---|
| `PRODUTOS por CAT` | Parcial | Criar tabela produto x categoria |
| `PRODUTOS por ID` | Parcial | Criar tabela principal por ID |
| `PRODUTOS por ID - MIN COT` | Parcial | Criar comparativo ID x menor cotacao |
| `PRODUTOS por ID e FORN` | Parcial | Criar tabela ID x fornecedor |
| `PRODUTOS por PROD` | Parcial | Criar tabela por produto oficial |
| `PRODUTOS por UF` | Parcial | Criar matriz produto x UF |
| `PADRONIZACAO PRODUTOS` | Ausente | Criar card/tabela produto original x produto oficial |
| `PMP_PROD_ABC` | Ausente | Criar PMP por curva ABC |
| `PMP_PROD_ID` | Parcial | Criar relacao produto x ID |
| `PMP_PROD_INF_12_x` | Parcial | Melhorar serie 12 meses |
| `PMP_ID_INF_12_x` | Parcial | Melhorar serie por ID |
| `PMP_UF` | Ausente | Criar PMP por UF |
| `TOTAL por PROD` | Parcial | Criar ranking total por produto |
| `PMP por PROD` | Parcial | Criar ranking PMP por produto |
| `PMP por UF` | Ausente | Criar PMP por UF |

Melhoria v3:

- A aba `Produtos e Precos` deve ser mais tabular e menos somente investigativa.
- Incluir visual claro de padronizacao:
  - produto original;
  - produto oficial;
  - codigo original;
  - codigo oficial;
  - quantidade de aliases;
  - impacto da padronizacao.

## Painel Cotacao - Zoho

O dashboard nao exportou pela API, mas o inventario mostra as views principais:

| View Zoho | Situacao na v2 | Acao v3 |
|---|---|---|
| `CONTAGEM de COTACOES` | Parcial | Criar card/grafico dedicado |
| `CONTAGEM de COTACOES por ABC` | Ausente | Criar cotacao x curva ABC |
| `CONTAGEM DE COTACOES por CAT` | Ausente | Criar cotacao x categoria |
| `CONTAGEM de COTACOES por UF` | Ausente | Criar cotacao x UF |
| `COTACOES DE PRECOS - TODOS` | Parcial | Criar tabela de consulta de cotacoes |
| `COTACOES por PRODUTO` | Parcial | Criar tabela por produto |
| `RELATORIO DE COTACOES` | Ausente | Criar relatorio principal |
| `MIN COTACAO por FORN` | Parcial | Criar ranking fornecedor menor preco |
| `MIN COTACAO por FORN - COTACOES <= 3` | Ausente | Criar bloco baixa concorrencia |
| `NUMERO de COTACOES por PRODUTO` | Parcial | Melhorar distribuicao |
| `IMPACTO de COTACAO NACIONAL` | Ausente | Criar bloco nacional |
| `IMPACTO de COTACAO por UF` | Ausente | Criar bloco por UF |

Melhoria v3:

- A aba `Cotacoes` deve mostrar disciplina de cotacao por:
  - ABC;
  - categoria;
  - UF;
  - produto;
  - fornecedor menor preco;
  - itens com `<= 3` cotacoes.

## Painel Inflacao - Zoho

Componentes reais exportados:

| Componente Zoho | Tipo | Situacao na v2 | Acao v3 |
|---|---|---|---|
| `INFLACAO por MES por CAT - %` | Grafico | Parcial | Criar grafico dedicado |
| `INFLACAO por MES por CAT - R$` | Grafico | Parcial | Criar grafico dedicado |
| `TOP INFLACAO` | Tabela/Pivot | Sim parcial | Manter e melhorar |
| `TOP DEFLACAO` | Tabela/Pivot | Sim parcial | Manter e melhorar |
| `INFLACAO por PRODUTO e CAT` | Tabela/Pivot | Parcial | Criar tabela dedicada |
| `INFLACAO NACIONAL` | Tabela/Pivot | Parcial | Criar bloco nacional |
| `INFLACAO por UF` | Tabela/Pivot | Parcial | Criar bloco UF |

Views adicionais:

- `INFLACAO NACIONAL por CATEGORIA`
- `INFLACAO por RESUMO de UF`
- `INFLACAO por UF e por CAT`
- `INFLACAO total`
- `INF_ID`
- `INF_ID_PMP`
- `INF_PROD_PMP`
- `TOP DEFL`

Melhoria v3:

- Separar claramente:
  - variacao percentual;
  - impacto em reais;
  - produto;
  - categoria;
  - UF;
  - nacional.

## Painel Adiantamento - Zoho

Componentes reais exportados:

| Componente Zoho | Tipo | Situacao na v2 | Acao v3 |
|---|---|---|---|
| `Adiantamento %` | Grafico | Parcial | Criar composicao percentual |
| `Adiantamento por Mes` | Grafico | Parcial | Criar serie mensal |
| `Adiantamento por UF` | Grafico | Parcial | Criar grafico UF |
| `AD por UF` | Grafico | Parcial | Criar tabela/grafico UF |
| `AD por CAT` | Grafico | Parcial | Criar AD x categoria |
| `AD por PRODUTO %` | Tabela/Pivot | Ausente | Criar tabela percentual |
| `AD por PRODUTO e UF` | Tabela/Pivot | Ausente | Criar matriz produto x UF |
| `AD por FORNECEDOR` | Tabela/Pivot | Parcial | Melhorar tabela |
| `AD por FORNECEDOR e UF` | Tabela/Pivot | Ausente | Criar matriz fornecedor x UF |

Views adicionais:

- `AD por MES e CAT`
- `CONCILIACAO_ AD`
- `CONCILIACAO_UF`
- `ADIANTAMENTO_CONC`

Melhoria v3:

- A aba `Adiantamentos` deve ir alem de nota x AD:
  - incluir AD por produto;
  - AD por categoria;
  - AD por UF;
  - AD por fornecedor e UF;
  - conciliacao geral e por UF.

## Painel CP - Zoho

Componente real exportado:

| Componente Zoho | Tipo | Situacao na v2 | Acao v3 |
|---|---|---|---|
| `CP_STATUS` | Tabela/Pivot | Parcial | Criar pivot principal |

Views adicionais:

- `CP_STATUS-TOTAL`
- `CP_SALDO_26`
- `CP_SALDO_DIVIDA_2026`
- `CP_SEMANA`

Melhoria v3:

- A aba `Financeiro / CP` deve mostrar:
  - CP por status;
  - CP total;
  - saldo 2026;
  - saldo semanal;
  - fornecedor;
  - filial;
  - categoria;
  - curva fornecedor.

## Painel Servicos - Zoho

Componentes reais exportados:

| Componente Zoho | Tipo | Situacao na v2 | Acao v3 |
|---|---|---|---|
| `DESPESAS por UF` | Grafico | Sim parcial | Manter e aproximar |
| `DESPESAS por UF e CAT` | Grafico | Parcial | Criar matriz/tabela |
| `SERVICOS` | Grafico | Parcial | Criar grafico principal |
| `SERVICOS por MES` | Tabela/Pivot | Parcial | Criar pivot mensal |

Views adicionais:

- `DESPESAS`
- `DESPESAS FIN`
- `Despesas_2v2v2`

Melhoria v3:

- Servicos deve ser area propria, mas tambem deve conversar com categoria `D - DESPESAS`.

## Categorias - correcao obrigatoria

A v2 ainda ordena categorias errado.

Arquivo de referencia:

`zoho/docs/claude_design/CATEGORIAS_I_D_A_ORDENADAS.md`

Regra v3:

1. Primeiro `I - INSUMOS`.
2. Depois `D - DESPESAS`.
3. Depois `A - ATIVOS`.
4. Dentro de cada nivel, ordenar por codigo.
5. Nao usar `F - FATURAMENTO` nem `V - VENDA BALCAO` nos filtros principais.

Exemplos:

- `I0`, `I1`, `I2`, `I3`, `I4`, `I5`, `I6`.
- `D1`, `D2`, `D3`, `D4`, `D5`, `D6`, `D7`, `D8`.
- `A1`, `A2`.

## Compra por filial

Compra por filial existe em SUPRIMENTOS principalmente por:

- `RESUMO_FILIAL`
- `RESUMO FILIAL`
- `SUP por FILIAL`
- `SUP_x_CMV`
- campos de `NFE`:
  - `CDFILIAL`
  - `NMFILIAL`
  - `UF`
  - `FI.NEGOCIO`
  - `FI.SIGLA`
  - `CAT1` a `CAT5`
  - `TOTAL`
  - `QTDE_EST`
  - `VLRUNITPOND`

Acao v3:

- Criar aba `Filiais`.
- Mostrar compras por filial, negocio, UF, categoria e fornecedor.
- Incluir ranking de filiais e drilldown filial -> categoria -> produto -> fornecedor.

## Estoque por filial

Estoque nao esta no workspace `SUPRIMENTOS`.

Foi encontrado em:

Workspace: `APURACAO DE RESULTADOS`

Views de estoque:

| Tipo | View |
|---|---|
| Table | `MOV.ESTOQUE - SINTETICO (RC)` |
| Table | `MOV.ESTOQUE - SINTETICO (ME)` |
| Table | `MOV.ESTOQUE - SINTETICO (SU)` |
| Pivot | `ANALISE DE ESTOQUE - IDEAL` |
| Pivot | `ANALISE DE ESTOQUE - MELHOR` |
| Pivot | `ANALISE DE ESTOQUE - POMME VITA` |
| Pivot | `MOV. DE ESTOQUE ANALITICO - IDEAL` |
| Pivot | `MOV. DE ESTOQUE ANALITICO - MELHOR` |
| Pivot | `MOV. DE ESTOQUE SINTETICO - IDEAL` |

Volumes amostrados por `count(*)`:

| Fonte | Linhas |
|---|---:|
| `MOV.ESTOQUE - SINTETICO (RC)` | 3.174 |
| `MOV.ESTOQUE - SINTETICO (ME)` | 400 |
| `MOV.ESTOQUE - SINTETICO (SU)` | 1.119 |

Colunas de estoque:

- `FILIAL`
- `MES`
- `ANO`
- `GRUPO PRODUTO`
- `Estoque Inicial`
- `Entradas`
- `Saidas`
- `Ajustes`
- `Implantacao`
- `Estoque Final`
- `Total do Consumo (CMV)`
- `Consumo/Dia`
- `Dias de Estoque`

Acao v3:

- Criar aba `Estoque por Filial`.
- Cruzar visualmente com compras por filial.
- KPIs:
  - estoque final;
  - entradas;
  - saidas;
  - consumo/CMV;
  - consumo por dia;
  - dias de estoque;
  - filiais criticas;
  - estoque negativo;
  - excesso de estoque;
  - baixo estoque.
- Tabelas:
  - filial x grupo produto;
  - filial x mes;
  - grupo produto x dias de estoque;
  - compras x consumo;
  - entradas x saidas x ajustes;
  - ranking de filiais criticas.

## O que a v3 deve ser

A v3 deve ser menos "mock resumido" e mais "BI operacional inspirado nos paineis reais do Zoho".

Ela deve manter a camada acionavel criada pelo Claude, mas representar explicitamente os graficos, tabelas, cards e pivots reais do Zoho.

