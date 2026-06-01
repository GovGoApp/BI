# Estudo dos Domínios — BI de Suprimentos

Análise do workspace `SUPRIMENTOS` do Zoho Analytics: estrutura de dados, domínios identificados e recomendações para o BI.

Gerado originalmente em 2026-05-27.

---

## Diagnóstico central

O workspace `SUPRIMENTOS` já tem uma camada de dados estruturada:

| Tipo | Quantidade |
|---|---:|
| Table | 21 |
| QueryTable | 32 |
| Pivot | 72 |
| AnalysisView | 31 |
| Dashboard | 8 |
| SummaryView | 1 |
| **Total** | **165** |

As `QueryTable` do Zoho funcionam como **camada semântica intermediária**: consolidam empresas, enriquecem compras com curvas ABC, PMP, inflação, cotações, fornecedores e filiais. O melhor caminho é usar essas query tables como fonte inicial.

**Oportunidade:** unir a profundidade operacional/econômica do Zoho com a camada cadastral/fiscal enriquecida do projeto de fornecedores.

---

## Fontes principais por domínio

### 1. Compras / Notas fiscais

| Fonte | Tipo | Linhas |
|---|---|---:|
| `NFE` | QueryTable | 239.694 |
| `ENTRADA DE NOTAS - [TODAS]` | QueryTable | 238.866 |
| `NF COM ITENS - CONSOLIDADO` | QueryTable | 118.176 |
| `NFE - IDEAL` | Table | 163.759 |

Campos recorrentes: `NMEMP`, `UF`, `CDFILIAL`, `NMFILIAL`, `FI.NEGOCIO`, fornecedor, produto, categoria, tempo, valor/quantidade, enriquecimento analítico (PMP, IMP, INF, cotação mínima).

**Distinção:** `NFE` é o fato principal de compras (agregado por item-mês). `NF COM ITENS - CONSOLIDADO` preserva dados de nota, chave, número e datas.

### 2. Cotações

| Fonte | Tipo | Linhas |
|---|---|---:|
| `COT` | QueryTable | 159.886 |
| `COT_MIN_FORN` | QueryTable | 66.311 |
| `NUM_COT` | QueryTable | 66.491 |

Campos importantes: `QTD_COT`, `MIN_COT`, `MED_COT`, `MAX_COT`, `PRE_MIN_COT`, `FORN_MENOR_PRECO`, `CNPJ_MENOR_PRECO`.

**Potencial:** comparar preço comprado × menor cotação × PMP histórico × fornecedor atual.

### 3. Curva ABC e consumo

| Fonte | Tipo | Linhas |
|---|---|---:|
| `CURVA FORN - TODAS` | QueryTable | 1.642 |
| `CURVA ABC FORN - TOTAL` | QueryTable | — |
| `CURVA ID - TODAS` | QueryTable | — |
| `CURVA PROD - TODAS` | QueryTable | — |

Campos: fornecedor/produto/ID, valor total, percentual, acumulado, curva (AAA→CCC), posição.

**Papel:** espinha dorsal de priorização — define o que é material para compras, fornecedor, produto e ID.

### 4. Preço médio, inflação e impacto

| Fonte | Tipo | Linhas |
|---|---|---:|
| `INFLAÇÃO` | QueryTable | 115.190 |
| `PMP_ID` | QueryTable | 115.190 |
| `PMP_ID_INF` | QueryTable | 115.190 |
| `PMP_ID_INF_12` | QueryTable | — |
| `PMP_PROD_INF_12` | QueryTable | — |

Campos: `PMP_0` a `PMP_12`, `SOMA_INF_*`, `PERC_INF_*`, `IMP_ID`, `IMP_COT`, `IMP_PRODT`.

**Uso:** detectar alta de preço por produto/ID/categoria e diferenciar aumento real de mix, fornecedor ou falta de cotação.

### 5. Contas a pagar

| Fonte | Tipo | Linhas |
|---|---|---:|
| `CP` | Table | 116.933 |
| `CP_MOV` | QueryTable | — |
| `CP_SEMANA` | QueryTable | — |
| `CP_SALDO_2026` | QueryTable | — |

Campos: datas (emissão, vencimento, baixa), valores, status, faixa de dias.

**Uso:** unir desempenho de suprimentos com pressão de caixa, risco de vencimento e negociação de prazo.

### 6. Adiantamentos

Fontes: `AD_v3`, `ADIANTAMENTO_NFE`, `NF ADT - IDEAL`, `NF ADT - MELHOR`, `NF ADT - POMME VITA`.

Campos: `STATUS_CONC`, `VALOR_CONCILIADO`, `NRONOTA_NF`, `NRONOTA_AD`.

**Uso:** reconciliar nota × adiantamento, identificar valores pendentes, concentração por fornecedor/produto/filial.

### 7. Filiais e geografia

Fontes: `FILIAIS_SUPPLY`, `FILIAIS`, `FILIAIS_DRO`, `FILIAIS_NEW`.

Campos: `EMPRESA`, `S_EMP`, `CDFILIAL`, `LOCAL`, `SIGLA`, `NEGOCIO`, `REGIAO`, `AREA`.

### 8. Resultado gerencial / SUP × CMV

Fontes: `FAT_SUP`, `TODAS - DRO SUM`.

**Uso:** conecta suprimentos com resultado econômico, margem e participação no CMV/faturamento.

---

## Camadas de dados recomendadas

### Bronze — extração direta do Zoho
Fontes a extrair sem transformação:
`NFE`, `NF COM ITENS - CONSOLIDADO`, `COT`, `COT_MIN_FORN`, `NUM_COT`, `CURVA ABC FORN - TOTAL`, `CURVA FORN - TODAS`, `CURVA PROD - TODAS`, `CURVA ID - TODAS`, `INFLAÇÃO`, `PMP_ID_INF_12`, `PMP_PROD_INF_12`, `CP`, `CP_MOV`, `CP_SEMANA`, `AD_v3`, `FILIAIS_SUPPLY`, `TAB_PROD`, `FAT_SUP`

### Silver — normalização
- Chaves de fornecedor, produto, filial, tempo, categoria
- Métricas: quantidade, total, preço unitário, PMP, inflação, impacto, cotação mínima

### Gold — tabelas de consumo para o dashboard
- `fato_compras_item_mes`
- `fato_cotacoes`
- `fato_contas_pagar`
- `fato_adiantamentos`
- `dim_fornecedor`, `dim_produto`, `dim_filial`, `dim_tempo`, `dim_categoria`

---

## O que a camada Zoho adiciona vs. dados locais

| Dimensão | Local (NFE.csv) | Zoho (NFE) |
|---|---|---|
| Linhas | 237.931 | 239.694 |
| Colunas | 37 | 63 |
| Curva fornecedor | 1.621 | 1.642 |

O Zoho traz a camada econômica/operacional que faltava: cotações, PMP, inflação, contas a pagar, adiantamentos, filial/geo e SUP × CMV.

A **tabela ponte** crítica para integração:
```
bridge_fornecedor_zoho_cadastro
  empresa · CDFORNECED · documento(CNPJ) · codigo_interno · nome_zoho · nome_cadastro · status_match
```

---

## Observações de arquitetura

O Zoho usa muitas QueryTables. Isso cria dependência opaca. Recomendações:

1. Usar as QueryTables consolidadas como fonte inicial.
2. Exportar e testar localmente.
3. Criar uma camada própria documentada.
4. Evitar depender da estrutura visual dos dashboards do Zoho.
5. Preservar linhagem: qual tabela originou cada indicador.
