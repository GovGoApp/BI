# Especificação das Abas — BI de Suprimentos

Especificação detalhada de cada aba: componentes obrigatórios, views Zoho de origem, campos e estrutura.

Documento vivo — atualizar conforme as abas forem implementadas.

**Regra de rotulagem:** sempre que criar uma tabela, card ou gráfico com origem no Zoho, colocar no subtítulo:
```
Origem Zoho: NOME_DA_VIEW
```

---

## Aba: Resumo (`data-page="resumo"`)

### Cards de topo
- Total comprado R$
- Fornecedores ativos
- Produtos únicos
- IDs únicos
- Compras com cotação %
- Impacto de cotação total R$
- CP em aberto R$
- AD pendente R$

### Componentes obrigatórios

| Componente | View Zoho |
|---|---|
| Resumo por negócio | `RESUMO NEGOCIOS` |
| Resumo por filial | `RESUMO_FILIAL` |
| Resumo por fornecedor (top) | `RESUMO - FORN` |
| Compras por categoria e mês | `CAT por MES` |
| Compras por categoria e UF | `CAT por UF` / `CAT_UF` |
| Mapa geográfico N/NE | `SUP por GEO - N e NE` |
| Mapa geográfico S/SE | `SUP por GEO - S e SE` |

---

## Aba: Oportunidades (`data-page="oportunidades"`)

Foco em compras acima do menor preço cotado.

### Cards de topo
- Impacto de cotação total R$
- % comprado acima do menor preço
- IDs com impacto positivo
- Fornecedores com menor preço não aproveitado

### Componentes
| Componente | View Zoho |
|---|---|
| Ranking de IDs por impacto | `IMP_COT_ID` / `IMP_ID` |
| Impacto por UF | `IMPACTO de COTACAO por UF` |
| Impacto nacional consolidado | `IMPACTO de COTACAO NACIONAL` |
| Fornecedor × produto × impacto | `FORNECEDORES e PRODUTOS - IMPACTO` |
| Top fornecedores por impacto | `FORNECEDORES IMPACTO sobre COTACAO` |

---

## Aba: Categorias (`data-page="categorias"`)

Filtros em cascata CAT1→CAT5, ordem I→D→A.

### Componentes
- Filtro CAT1 → CAT2 → CAT3 → CAT4 → CAT5 em cascata
- Total comprado por categoria
- Evolução temporal por categoria
- Inflação por categoria
- Fornecedores por categoria

---

## Aba: Filiais (`data-page="filiais"`)

| Componente | View Zoho |
|---|---|
| Resumo por filial | `RESUMO_FILIAL` / `SUP por FILIAL` |
| Top categorias por filial | `CAT_UF` |
| Compras por negócio | `RESUMO NEGOCIOS` |

---

## Aba: Estoque (`data-page="estoque"`)

Dados do workspace `APURAÇÃO DE RESULTADOS` (workspace ID `2130260000006068011`).

| Componente | View Zoho |
|---|---|
| Estoque por filial | Pivots de estoque do workspace APURAÇÃO |

---

## Aba: Fornecedor 360 (`data-page="forn360"`)

Painel por CNPJ. Pesquisa por fornecedor com detalhe expansível.

### Componentes obrigatórios

| Componente | View Zoho |
|---|---|
| Volume total comprado | `FORNECEDORES TOTAL` |
| Volume por ano | `FORNECEDORES TOTAL - POR ANO` |
| Volume 2025/2026 | `FORNECEDORES_25_26` |
| Por categoria | `FORNECEDORES por CAT` / `FORNECEDORES por CAT 2` |
| Por UF e categoria | `FORNECEDORES por UF e CAT` |
| Impacto de cotação | `FORNECEDORES IMPACTO sobre COTACAO` |
| Fornecedor × produto × impacto | `FORNECEDORES e PRODUTOS - IMPACTO` |
| Inflação por fornecedor | `FORNECEDORES INFLACAO` |
| Fornecedor × produto × inflação | `FORNECEDORES e PRODUTOS - INFLACAO` |
| PMP por fornecedor | `PMP_FORN` |
| CP status | `CP_STATUS` |

### Campos a exibir no cabeçalho do fornecedor
- CNPJ, razão social, fantasia
- Curva fornecedor + posição
- UFs atendidas
- Regime fiscal + crédito 2027

---

## Aba: Produtos (`data-page="produtos"`)

| Componente | View Zoho |
|---|---|
| Por categoria | `PRODUTOS por CAT` |
| Por ID | `PRODUTOS por ID` |
| Por ID com menor cotação | `PRODUTOS por ID - MIN COT` |
| Por ID e fornecedor | `PRODUTOS por ID e FORN` |
| Por produto | `PRODUTOS por PROD` |
| Por UF | `PRODUTOS por UF` |
| Padronização | `PADRONIZACAO PRODUTOS` |
| PMP por ABC | `PMP_PROD_ABC` |
| PMP por ID | `PMP_PROD_ID` |
| PMP × inflação 12m (ID) | `PMP_ID_INF_12_x` |
| PMP × inflação 12m (prod) | `PMP_PROD_INF_12_x` |
| PMP por UF | `PMP_UF` |
| PMP por categoria | `PMP por CAT` |
| PMP por produto | `PMP por PROD` |

---

## Aba: Cotações (`data-page="cotacoes"`)

### Cards de topo
- Produtos cotados
- Cobertura de cotação %
- Média de cotações por produto
- Produtos com 0 cotação
- Produtos com 1 cotação
- Produtos com ≤ 3 cotações
- Potencial IMP_COT R$
- % comprado no menor preço

### Blocos obrigatórios

| Bloco | View Zoho | Descrição |
|---|---|---|
| 1. Contagem por mês | `CONTAGEM de COTACOES` | Distribuição 0,1,2,3,4,5+ por mês |
| 2. Cobertura por ABC | `CONTAGEM de COTACOES por ABC` | `CURVA_ID` × `QTD_COT` |
| 3. Cobertura por categoria | `CONTAGEM DE COTACOES por CAT` | `MESANO` × `CAT2` |
| 4. Cobertura por UF | `CONTAGEM de COTACOES por UF` | `UF` × `QTD_COT` |
| 5. Consulta de preços | `COTACOES DE PRECOS - TODOS` | Tabela ID × fornecedor × preço |
| 6. Cotações por produto | `COTACOES por PRODUTO` | Ranking produto/ID |
| 7. Número de cotações | `NUMERO de COTACOES por PRODUTO` | Matriz ID × mês × `#` e `MIN` |
| 8. MIN cotação por fornecedor | `MIN COTACAO por FORN` | Quem é o mais barato |
| 9. MIN cotação baixa concorrência | `MIN COTACAO por FORN - COTACOES <= 3` | Risco de baixa competição |
| 10. Relatório completo | `RELATORIO DE COTACOES` | `POS_PROD` × `UF` × fornecedor × meses |

---

## Aba: Impacto (`data-page="impacto"`)

Separada de Inflação. Foco em IMP_COT.

### Cards de topo
- Impacto de cotação total R$
- Impacto nacional R$
- UF líder em impacto
- IDs com maior IMP_COT
- Fornecedores mais frequentes como menor preço não escolhido
- % comprado acima do menor preço

### Tabela principal — colunas
ID · Produto oficial · Categoria · UF · Fornecedor comprado · Fornecedor menor preço · PMP · Menor cotação · Quantidade · IMP_COT · Curva ID · Status

Status: `Comprou no menor` · `Acima do menor` · `Sem cotação` · `Baixa concorrência`

### Views Zoho
`IMPACTO de COTACAO NACIONAL` · `IMPACTO de COTACAO por UF` · `IMPACTO por COTACAO` · `IMP_COT_ID` · `IMP_ID` · `IMP_PROD` · `IMP_PROD_2` · `PRODUTOS por ID - MIN COT`

---

## Aba: Inflação (`data-page="inflacao"`)

Separada de Impacto. Foco em variação do PMP ao longo do tempo.

Duas leituras separadas:
- Variação percentual de PMP
- Exposição monetária da inflação

### Componentes

| Componente | View Zoho |
|---|---|
| Inflação por mês e categoria % | `INFLACAO por MES por CAT - %` |
| Inflação por mês e categoria R$ | `INFLACAO por MES por CAT - R$` |
| Top inflação | `TOP INFLACAO` |
| Top deflação | `TOP DEFLACAO` |
| Inflação produto × categoria | `INFLACAO por PRODUTO e CAT` |
| Nacional | `INFLACAO NACIONAL` |
| Nacional por categoria | `INFLACAO NACIONAL por CATEGORIA` |
| Por UF | `INFLACAO por UF` |
| Por UF e categoria | `INFLACAO por UF e por CAT` |
| Por resumo de UF | `INFLACAO por RESUMO de UF` |
| Total | `INFLACAO total` |

---

## Aba: Fiscal (`data-page="fiscal"`)

Regime tributário e potencial de crédito CBS/IBS 2027.

Dados da base de fornecedores do projeto principal (não do Zoho).

### Componentes
- KPI: fornecedores com regime indeterminado
- KPI: volume comprado de fornecedores Simples/MEI
- Tabela: fornecedores por regime × volume × crédito estimado 2027
- Fila: alto valor + regime pendente

---

## Aba: Financeiro (`data-page="financeiro"`)

| Componente | View Zoho |
|---|---|
| Status de CP | `CP_STATUS` |
| CP total | `CP_STATUS-TOTAL` |
| Saldo 2026 | `CP_SALDO_26` / `CP_SALDO_DIVIDA_2026` |
| Por semana | `CP_SEMANA` |

### Cards de topo
- Total CP em aberto R$
- Vencidos R$
- A vencer próximos 7 dias
- Pago no mês

---

## Aba: Adiantamentos (`data-page="adiantamentos"`)

| Componente | View Zoho |
|---|---|
| KPI % conciliado | `Adiantamento %` |
| Evolução mensal | `Adiantamento por Mes` |
| Por UF | `Adiantamento por UF` / `AD por UF` |
| Por categoria | `AD por CAT` |
| Por produto % | `AD por PRODUTO %` |
| Por produto e UF | `AD por PRODUTO e UF` |
| Por fornecedor | `AD por FORNECEDOR` |
| Por fornecedor e UF | `AD por FORNECEDOR e UF` |
| Por mês e categoria | `AD por MES e CAT` |
| Conciliação | `CONCILIACAO_ AD` / `CONCILIACAO_UF` / `ADIANTAMENTO_CONC` |

---

## Aba: Serviços (`data-page="servicos"`)

| Componente | View Zoho |
|---|---|
| Por UF | `DESPESAS por UF` |
| Por UF e categoria | `DESPESAS por UF e CAT` |
| Serviços | `SERVICOS` |
| Evolução mensal | `SERVICOS por MES` |
| Despesas gerais | `DESPESAS` / `DESPESAS FIN` |

---

## Aba: Dados (`data-page="qualidade"`)

Monitor de qualidade dos dados.

### Verificações automáticas
- Fonte existe e exporta
- Colunas esperadas presentes
- Line count não caiu anormalmente
- Chaves nulas (fornecedor, produto, filial)
- Meses recentes presentes
- Duplicidades suspeitas por nota/item/produto
- Cobertura de fornecedor no cadastro enriquecido
