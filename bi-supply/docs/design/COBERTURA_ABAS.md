# Cobertura das Abas — Auditoria Zoho x Mock

Auditoria comparando o mock `BI Suprimentos v4` contra os dashboards reais do Zoho Analytics (workspace `SUPRIMENTOS`).

Usado como referência para garantir que o dashboard implementado cubra os componentes reais do Zoho.

---

## Resumo da auditoria

Os dashboards do Zoho existentes:
- `PAINEL RESUMO`
- `PAINEL FORNECEDOR`
- `PAINEL COTAÇÃO`
- `PAINEL INFLAÇÃO`
- `PAINEL ADIANTAMENTO`
- `PAINEL CP`
- `PAINEL SERVIÇOS`
- `PAINEL PRODUTOS`

---

## PAINEL RESUMO

| Componente Zoho | Status | Ação |
|---|---|---|
| `SUP por GEO - N e NE` | Falta | Criar gráfico geográfico/por regional |
| `SUP por GEO - S e SE` | Falta | Criar gráfico geográfico/por regional |
| `CAT por MES` | Falta | Criar gráfico temporal de categorias |
| `CAT por UF` | Falta | Criar gráfico categoria × UF |
| `CAT_UF` | Parcial | Manter e deixar como tabela/pivot oficial |
| `RESUMO NEGOCIOS` | Parcial | Manter e fortalecer |
| `RESUMO_FILIAL` | Parcial | Manter e cruzar com aba Filiais |
| `RESUMO - FORN` | Parcial | Manter e cruzar com Fornecedor 360 |

---

## PAINEL FORNECEDOR

| Componente Zoho | Status | Ação |
|---|---|---|
| `FORNECEDORES IMPACTO sobre COTACAO` | Falta | Criar bloco dedicado |
| `FORNECEDORES e PRODUTOS - IMPACTO` | Falta | Criar tabela fornecedor × produto × impacto |
| `FORNECEDORES INFLACAO` | Falta | Criar ranking separado de inflação |
| `FORNECEDORES e PRODUTOS - INFLACAO` | Falta | Criar detalhe fornecedor × produto × inflação |
| `FORNECEDORES TOTAL` | Falta | Criar ranking total |
| `FORNECEDORES por CAT` | Falta | Criar distribuição por categoria |
| `FORNECEDORES por CAT 2` | Falta | Criar distribuição por CAT2 |
| `CP_STATUS` | Presente | Manter |

---

## PAINEL COTAÇÃO

| View Zoho | O que representa | Status |
|---|---|---|
| `CONTAGEM de COTACOES` | Distribuição mensal por quantidade de cotações | Falta |
| `CONTAGEM de COTACOES por ABC` | Cobertura por curva ABC do ID | Falta |
| `CONTAGEM DE COTACOES por CAT` | Cobertura por categoria | Falta |
| `CONTAGEM de COTACOES por UF` | Cobertura por UF | Falta |
| `COTACOES DE PRECOS - TODOS` | Consulta ampla de preços cotados | Falta |
| `COTACOES por PRODUTO` | Histórico de cotações por produto | Falta |
| `RELATORIO DE COTACOES` | Relatório produto × fornecedor × meses | Falta |
| `MIN COTACAO por FORN` | Fornecedor com menor preço | Falta |
| `MIN COTACAO por FORN - COTACOES <= 3` | Menor preço com baixa concorrência | Falta |
| `NUMERO de COTACOES por PRODUTO` | Matriz produto × mês × quantidade/mínimo | Falta |
| `IMPACTO de COTACAO NACIONAL` | Impacto consolidado nacional | Falta |
| `IMPACTO de COTACAO por UF` | Impacto por UF | Falta |
| `IMP_COT_ID` | Impacto por ID | Falta |

---

## PAINEL INFLAÇÃO

| Componente Zoho | Status | Ação |
|---|---|---|
| `INFLACAO por MES por CAT - %` | Falta | Criar linha/área por CAT |
| `INFLACAO por MES por CAT - R$` | Falta | Criar gráfico R$ separado |
| `TOP INFLACAO` | Parcial | Manter |
| `TOP DEFLACAO` | Parcial | Manter |
| `INFLACAO por PRODUTO e CAT` | Falta | Criar tabela produto × categoria |
| `INFLACAO NACIONAL` | Falta | Criar painel nacional |
| `INFLACAO por UF` | Falta | Criar painel por UF |

---

## PAINEL ADIANTAMENTO

| Componente Zoho | Status | Ação |
|---|---|---|
| `Adiantamento %` | Falta | Criar card/gráfico |
| `Adiantamento por Mes` | Falta | Criar gráfico temporal |
| `Adiantamento por UF` | Falta | Criar por UF |
| `AD por UF` | Falta | Criar gráfico/tabela |
| `AD por CAT` | Falta | Criar gráfico/tabela |
| `AD por PRODUTO %` | Falta | Criar tabela |
| `AD por PRODUTO e UF` | Falta | Criar tabela |
| `AD por FORNECEDOR` | Falta | Criar tabela |
| `AD por FORNECEDOR e UF` | Falta | Criar tabela |

---

## PAINEL CP

| Componente Zoho | Status | Ação |
|---|---|---|
| `CP_STATUS` | Presente | Manter |
| `CP_STATUS-TOTAL` | Falta | Adicionar |
| `CP_SALDO_26` | Falta | Adicionar |
| `CP_SALDO_DIVIDA_2026` | Falta | Adicionar |
| `CP_SEMANA` | Falta | Adicionar |

---

## PAINEL SERVIÇOS

| Componente Zoho | Status | Ação |
|---|---|---|
| `DESPESAS por UF` | Presente | Manter |
| `DESPESAS por UF e CAT` | Presente | Manter |
| `SERVICOS` | Presente | Manter |
| `SERVICOS por MES` | Presente | Manter |

---

## PAINEL PRODUTOS

| Componente Zoho | Status | Ação |
|---|---|---|
| `PRODUTOS por CAT` | Falta | Criar |
| `PRODUTOS por ID` | Falta | Criar |
| `PRODUTOS por ID - MIN COT` | Falta | Criar |
| `PRODUTOS por ID e FORN` | Falta | Criar |
| `PRODUTOS por PROD` | Falta | Criar |
| `PRODUTOS por UF` | Falta | Criar |
| `PADRONIZACAO PRODUTOS` | Falta | Criar |
| `PMP_PROD_ABC` | Falta | Criar |
| `PMP_PROD_ID` | Falta | Criar |
| `PMP_PROD_INF_12_x` | Falta | Criar |
| `PMP_ID_INF_12_x` | Falta | Criar |
| `PMP_UF` | Falta | Criar |

---

## Correção conceitual: IMP ≠ INF

### IMP — Impacto de cotação

```
IMP_COT = (VLRUNITPOND_EST - PRE_MIN_COT) × QTDE_EST
```

Pertence às abas: **Cotações**, **Impacto**, **Oportunidades**, **Fornecedor 360**

### INF — Inflação / variação de PMP

Variação do PMP ao longo do tempo com base em séries mensais.

Pertence às abas: **Inflação**, **Categorias**, **Produtos**

**Regra:** nunca usar IMP como sinônimo de inflação. Nunca misturar `IMPACTO de COTACAO` com `INFLACAO por MES` no mesmo gráfico sem identificação clara.

---

## Evidências dos exports de cotação

| Arquivo | Linhas | Colunas principais |
|---|---:|---|
| `contagem_cotacoes.csv` | 280 | `MESANO`, `QTD_COT` |
| `contagem_cotacoes_abc.csv` | 81 | `CURVA_ID`, `QTD_COT` |
| `contagem_cotacoes_cat.csv` | 126 | `MESANO`, `CAT2` |
| `contagem_cotacoes_uf.csv` | 61 | `UF`, `QTD_COT` |
| `min_cotacao_forn.csv` | 8.851 | `POS_FORN`, `CNPJ_MENOR_PRECO`, `FORN_MENOR_PRECO`, `POS_ID` |
| `numero_cotacoes_produto.csv` | 5.808 | `POS_ID`, `CURVA_ID`, `ID`, meses, `#`, `MIN` |
| `relatorio_cotacoes.csv` | 12.722 | `POS_PROD`, `UF`, `NMPRODUTO_OFICIAL`, `NMRAZSOCFORN`, meses |
