# Mapa de Abas e Elementos - BI Suprimentos v4

Fonte analisada: `zoho/design/BI Suprimentos v4.html`.

Regra de nomenclatura: doravante, manter os nomes das abas exatamente como aparecem no design v4.

## 1. Resumo

### KPIs

- Total comprado
- Fornecedores ativos
- Produtos / IDs
- Impacto R$
- Oportunidade R$
- Compras com cotacao
- Risco fiscal 2027
- CP em aberto

### Graficos, cards e relatorios

- Tendencia mensal de compras
- Compras por negocio
- Top categorias
- Top fornecedores
- Alertas executivos
- SUP por GEO - N e NE
- SUP por GEO - S e SE
- RESUMO NEGOCIOS
- RESUMO_FILIAL
- CAT_UF - categoria x UF
- RESUMO - FORN

### Tabelas

- Top categorias: Categoria, Valor 12m, % do total, Inflacao, Impacto R$
- Top fornecedores: Fornecedor, Empresas, Curva, Valor, Regime, Alerta
- RESUMO NEGOCIOS: Negocio, Valor 12m, % total, CP aberto, Impacto, Filiais
- RESUMO_FILIAL: Filial, Negocio, UF, Valor, Compra/CMV, CP aberto
- RESUMO - FORN: Fornecedor, Curva, Valor, CP, Impacto, Alerta

### Controles internos

- Valor
- Volume
- Impacto
- 12m
- 6m
- YTD

## 2. Oportunidades

### KPIs

- Oportunidade R$
- Prioridade alta
- Acima da menor cot.
- Inflacao curva A
- 1 cotacao
- Nao e menor preco

### Graficos, cards e relatorios

- Matriz de prioridade
- Oportunidade por tipo

### Tabelas

- Fila de oportunidades: Tipo, Prio., ID, Produto / Fornecedor, Forn. atual, Menor cot., Impacto R$, Evidencia, Acao sugerida, Status

### Controles internos

- Fila completa
- Economico
- Risco fiscal
- Risco financeiro
- Risco de estoque
- Saneamento
- Acima da menor cot.
- Cotacoes <= 3
- Inflacao curva A
- CP vencido
- AD pendente
- Estoque baixo
- Estoque excessivo

## 3. Categorias

### KPIs

- Total comprado
- Inflacao 12m
- Produtos / IDs
- Fornecedores
- Impacto R$
- Oportunidade R$

### Graficos, cards e relatorios

- Drilldown Nivel 1 -> Nivel 5
- Nivel 2 x UF
- Nivel 2 x Mes
- Categoria x Fornecedor
- Categoria x Produto
- Alertas da categoria

### Tabelas

- Categoria x Fornecedor: Fornecedor, Subcategoria, Valor, Curva, Regime
- Categoria x Produto: Produto, ID, PMP, Inflacao, Impacto

### Controles internos

- I - Insumos
- D - Despesas
- A - Ativos
- F - Faturamento
- V - Venda balcao
- Todos

## 4. Filiais

### KPIs

- Total comprado
- Compra media / filial
- Maior filial
- Maior UF
- Maior negocio
- Compra / CMV medio
- Impacto por filial
- Oportunidade

### Graficos, cards e relatorios

- Ranking de filiais
- Filial x Negocio
- Filiais - visao consolidada
- Filial x Categoria
- Filial x Fornecedor
- Filial x Mes

### Tabelas

- Filiais - visao consolidada: Filial, Negocio, UF, Empresa, FI.SIGLA, Total comprado, QTDE_EST, CMV, Compra/CMV, Dias estoque, CAT2 dominante, Forn., Status
- Filial x Categoria: Filial, CAT2, % do valor
- Filial x Fornecedor: Filial, Fornecedor, Valor

### Controles internos

- Valor
- Compra / CMV
- Impacto
- Estoque
- Todas
- Ruptura
- Atencao
- Saudavel
- Excesso

## 5. Estoque

### KPIs

- Estoque final
- Entradas 12m
- Saidas / CMV
- Consumo / dia
- Dias de estoque medio
- Estoque baixo menor que 15d
- Excesso maior que 60d
- Estoque negativo

### Graficos, cards e relatorios

- Dias de estoque por filial
- Entradas x Saidas x Ajustes
- Movimentacao por filial
- Estoque por grupo produto
- Compras x Consumo CMV por filial
- Alertas de estoque

### Tabelas

- Movimentacao por filial: Filial, UF, Empresa, Grupo produto, Estoque inicial, Entradas, Saidas, Ajustes, Estoque final, CMV, Consumo/dia, Dias estoque
- Estoque por grupo produto: Grupo, Estoque final, % do total, Dias medio, Risco
- Compras x Consumo CMV por filial: Filial, Compras, CMV, Razao, Leitura

### Controles internos

- Sintese
- Movimentacao
- Por grupo
- Analitico
- Todas
- Ruptura
- Atencao 7-15d
- Saudavel 15-45
- Excesso >60d
- Negativo

## 6. Fornecedor

### KPIs

- Fornecedores
- Valor 12m
- Sem CNPJ na base
- Risco fiscal x alto valor
- Lucro Real
- Simples Nacional

### Graficos, cards e relatorios

- Produtos comprados deste fornecedor
- Cotacoes e fornecedores alternativos
- Identidade e cadastro
- Compras 12m - categorias
- Impacto - cotacao vs. inflacao
- Fiscal 2027
- Financeiro - CP_STATUS
- Adiantamento - AD status
- Alertas e acao sugerida

### Tabelas

- Lista de fornecedores: Fornecedor, CNPJ, Empresas, Curva, Valor 12m, Regime, Credito 2027, Alertas
- Produtos comprados deste fornecedor: ID, Produto original / oficial, CAT2 - CAT3, Curva ID, Valor, PMP, Menor cot., Impacto, Status
- Cotacoes e fornecedores alternativos: ID, Produto, Comprado, Min cot., Med cot., Max cot., QTD_COT, Fornecedor menor preco, Decisao

### Controles internos

- Total
- Impacto cotacao
- Inflacao
- Categorias
- UF / CAT
- Por ano
- CP
- Fiscal
- Todos
- Curva AAA
- Curva AA
- Curva A
- Credito 2027 alto
- Credito condicionado
- Pendente
- Indeterminado
- Com adiantamento
- CP vencido

## 7. Produtos

### KPIs

- Produtos analisados
- IDs ativos 12m
- Variacao PMP > 10%
- Sem cotacao
- PMP medio cesta
- Inflacao cesta 12m

### Graficos, cards e relatorios

- Identificacao - original vs. oficial
- PMP_ID_INF_12
- Cotacoes 90d - FORN_MENOR_PRECO
- Compras por UF / filial

### Tabelas

- Produtos e precos: Produto, ID, Categoria, Curva ID, Curva Prod., PMP atual, Variacao 12m, Serie PMP, Impacto R$

### Controles internos

- Todos
- Curva ID AAA
- Curva ID AA
- Inflacao > 10%
- Deflacao
- Sem cotacao

## 8. Cotações

### KPIs

- Produtos cotados
- Cobertura cotacao
- Media / produto
- 0 cotacao
- 1 cotacao
- <= 3 cotacoes
- Potencial IMP_COT
- % no menor preco

### Graficos, cards e relatorios

- Distribuicao mensal de QTD_COT por ID
- Cotacoes por curva ABC do ID
- Cotacoes por categoria
- Cotacoes por UF
- Consulta de precos cotados
- Cotacoes por produto
- Matriz produto x mes - numero de cotacoes e minimo
- Fornecedor com menor preco
- Menor preco com baixa concorrencia
- Relatorio de cotacoes

### Origens Zoho explicitadas

- CONTAGEM de COTACOES
- CONTAGEM de COTACOES por ABC
- CONTAGEM DE COTACOES por CAT
- CONTAGEM de COTACOES por UF
- COTACOES DE PRECOS - TODOS
- COTACOES por PRODUTO
- NUMERO de COTACOES por PRODUTO
- MIN COTACAO por FORN
- MIN COTACAO por FORN - COTACOES <= 3
- RELATORIO DE COTACOES

### Tabelas

- Cotacoes por UF: UF, Total cot., 0/1 cot., <= 3 cot., Cobertura, Risco
- Consulta de precos cotados: ID, Produto, UF, Fornecedor, Mes, PRECOUNIT_EST, Curva forn., Curva ID
- Cotacoes por produto: ID, Produto, Categoria, UF, QTD_COT, MIN, MED, MAX, Forn. menor preco, Status
- Matriz produto x mes: POS_ID, Curva ID, ID, NMPRODUTO_EST, mes/ano, numero, MIN R$
- Fornecedor com menor preco: POS_FORN, Fornecedor menor preco, CNPJ, numero como menor, numero IDs unicos, Volume R$
- Menor preco com baixa concorrencia: ID, Produto, Forn. menor preco, UF, QTD_COT, Risco
- Relatorio de cotacoes: POS_PROD, UF, NMPRODUTO_OFICIAL, NMRAZSOCFORN, Min geral

### Controles internos

- Contagem
- Min. fornecedor
- Por produto
- Relatorio

## 9. Impacto

### KPIs

- Impacto total R$
- Impacto nacional
- UF lider em impacto
- % comprado acima do menor
- IDs com IMP_COT > 0
- Top IMP_COT item

### Graficos, cards e relatorios

- Impacto de cotacao nacional
- Impacto por UF
- Top IDs por IMP_COT
- Fornecedores menor preco nao escolhido
- PRODUTOS por ID - MIN COT

### Origens Zoho explicitadas

- IMPACTO de COTACAO NACIONAL
- IMPACTO de COTACAO por UF
- IMP_COT_ID
- IMP_ID
- IMP_PROD
- FORNECEDORES IMPACTO sobre COTACAO
- PRODUTOS por ID - MIN COT

### Tabelas

- Top IDs por IMP_COT: ID, Produto oficial, Categoria, UF, Forn. comprado, Forn. menor preco, PMP comprado, Menor cot., Qtde, IMP_COT, Curva ID, Status
- Fornecedores menor preco nao escolhido: Fornecedor menor, numero IDs, IMP_COT potencial, Curva forn.
- PRODUTOS por ID - MIN COT: ID, Curva, PRE_MIN_COT, FORN_MIN_COT, IMP_COT

### Controles internos

- Nacional
- Por UF
- Por ID
- Por fornecedor

## 10. Inflação

### KPIs

- Inflacao media cesta
- Exposicao R$ 12m
- Top inflacao
- Top deflacao
- IDs afetados
- CAT2 mais inflada

### Graficos, cards e relatorios

- Inflacao por mes por CAT - %
- Inflacao por mes por CAT - R$
- Top inflacao variacao %
- Top deflacao
- Inflacao nacional
- Inflacao por UF
- Inflacao por produto e categoria

### Origens Zoho explicitadas

- INFLACAO por MES por CAT - %
- INFLACAO por MES por CAT - R$
- TOP INFLACAO
- TOP DEFLACAO
- INFLACAO NACIONAL
- INFLACAO NACIONAL por CATEGORIA
- INFLACAO por UF
- INFLACAO por UF e por CAT
- INFLACAO por PRODUTO e CAT
- INF_ID_PMP
- INF_PROD_PMP

### Tabelas

- Inflacao nacional: Categoria, PERC_INF 12m, SOMA_INF R$, % sobre cesta
- Inflacao por UF: UF, PERC_INF, SOMA_INF R$, Leitura
- Inflacao por produto e categoria: ID, Produto, Categoria, PMP_0, PMP_6, PMP_12, INF_ID %, SOMA_INF R$, Curva

### Controles internos

- Variacao %
- Exposicao R$
- Nacional
- Por UF

## 11. Fiscal

### KPIs

- Compra com credito alto
- Compra condicionada
- Compra pendente
- Fornecedores indeterminados
- Valor em risco

### Graficos, cards e relatorios

- Matriz - valor comprado x regime fiscal
- Fila fiscal priorizada
- Fornecedores - detalhe fiscal

### Tabelas

- Fila fiscal priorizada: Fornecedor, Curva, Valor, Credito 2027, Acao
- Fornecedores - detalhe fiscal: Fornecedor, CNPJ, Valor comprado, Curva, Regime fiscal, Credito 2027, Evidencia, Acao fiscal

## 12. Financeiro

### KPIs

- CP em aberto
- CP vencido
- A vencer 7 dias
- Pressao de caixa
- Em negociacao

### Graficos, cards e relatorios

- Timeline semanal - proximas 8 semanas
- Contas a pagar por fornecedor

### Tabelas

- Contas a pagar por fornecedor: Fornecedor, CP aberto, Vencido, A vencer, Faixa de dias, Ultima compra, Curva, Acao

## 13. Adiantamentos

### KPIs

- AD total 12m
- Conciliado
- Pendente
- Parcial
- Notas vinculadas

### Graficos, cards e relatorios

- Funil de conciliacao
- AD por empresa
- Adiantamentos detalhados

### Tabelas

- Adiantamentos detalhados: Fornecedor, Nota fiscal, AD, Valor AD, Valor conciliado, Status, Mes entrada, Mes pagamento, Empresa

## 14. Serviços

### KPIs

- Total em servicos
- Fornecedores de servicos
- UFs atendidas
- Variacao mensal
- Maior categoria
- CP em aberto

### Graficos, cards e relatorios

- Servicos por UF
- Servicos por mes
- Servicos por categoria
- Fornecedores de servicos
- Servicos detalhados por CAT5

### Tabelas

- Servicos por categoria: Categoria, Valor, % do total, Variacao
- Fornecedores de servicos: Fornecedor, Categoria, Valor, Regime, Credito
- Servicos detalhados por CAT5: CAT5, CAT3 - CAT4, Valor, % sobre servicos, Variacao 12m, Fornecedor principal, Regime, CP aberto

## 15. Dados

### KPIs

- Linhas analisadas
- Fontes OK
- Forn. sem CNPJ
- Produtos sem codigo oficial
- Cotacoes incompletas
- Fiscal pendente

### Graficos, cards e relatorios

- Workspaces Zoho x fontes
- Cobertura por fonte
- Fila de saneamento
- Workspace SUPRIMENTOS
- Workspace APURACAO DE RESULTADOS

### Tabelas

- Cobertura por fonte: Fonte, Workspace, Linhas, Cobertura, %, Estado
- Fila de saneamento: Problema, Campo critico, Linhas, Impacto, Acao

