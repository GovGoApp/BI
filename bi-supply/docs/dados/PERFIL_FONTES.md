# Perfil das Fontes — SUPRIMENTOS

Perfil gerado a partir de amostras (`limit 5`) das 53 fontes `Table` e `QueryTable` do workspace `SUPRIMENTOS`.

Gerado originalmente em 2026-05-27.

- Fontes analisadas: **53**
- Fontes com amostra OK: **53**
- Fontes com erro: **0**

---

## Por domínio

### Adiantamentos

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | ADIANTAMENTO_NFE | 16 |
| QueryTable | AD_v1 | 11 |
| QueryTable | AD_v2 | 11 |
| QueryTable | AD_v3 | 16 |
| Table | NF ADT - IDEAL | 30 |
| Table | NF ADT - MELHOR | 30 |
| Table | NF ADT - POMME VITA | 30 |

### Contas a pagar

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | CP_MOV | 12 |
| QueryTable | CP_SALDO_2025 | 13 |
| QueryTable | CP_SALDO_2026 | 13 |
| QueryTable | CP_SALDO_2026_v2 | 12 |
| QueryTable | CP_SEMANA | 13 |
| Table | CP | 49 |
| Table | TODAS - CONTAS A PAGAR | 46 |

### Cotações

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | COT | 32 |
| QueryTable | COT_MIN_FORN | 7 |
| QueryTable | NUM_COT | 18 |
| Table | COT - IDEAL | 25 |
| Table | COT - MELHOR | 25 |
| Table | COT - SUPERA | 25 |
| Table | [RC] COTAÇÃO DE PREÇOS - OLD | 20 |

### Curva ABC e consumo

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | CURVA ABC FORN - TOTAL | 7 |
| QueryTable | CURVA FORN - TODAS | 6 |
| QueryTable | CURVA ID - TODAS | 6 |
| QueryTable | CURVA PROD - IDEAL | 6 |
| QueryTable | CURVA PROD - MELHOR | 6 |
| QueryTable | CURVA PROD - SUPERA | 6 |
| QueryTable | CURVA PROD - TODAS | 7 |

### Filiais e organização

| Tipo | Fonte | Colunas |
|---|---|---:|
| Table | FILIAIS | 12 |
| Table | FILIAIS_DRO | 19 |
| Table | FILIAIS_NEW | 19 |
| Table | FILIAIS_SUPPLY | 12 |

### Fornecedores e resultado

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | FAT_SUP | — |
| QueryTable | FORN_CP_25_26 | — |
| Table | TODAS - DRO SUM | — |
| Table | TIPOCONTA | — |

### Notas fiscais / compras

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | NFE | 63 |
| QueryTable | ENTRADA DE NOTAS - [TODAS] | — |
| QueryTable | NF COM ITENS - CONSOLIDADO | — |
| Table | NFE - IDEAL | — |
| Table | NFE - MELHOR | — |
| Table | NFE - SUPERA | — |
| Table | NF COM ITENS - IDEAL | — |
| Table | NF COM ITENS - ME | — |
| Table | NF COM ITENS - SU | — |

### Preço médio / inflação / impacto

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | INFLAÇÃO | — |
| QueryTable | PMP_ID | — |
| QueryTable | PMP_ID_INF | — |
| QueryTable | PMP_ID_INF_12 | — |
| QueryTable | PMP_PROD | — |
| QueryTable | PMP_PROD_INF | — |
| QueryTable | PMP_PROD_INF_12 | — |

### Produtos / referência

| Tipo | Fonte | Colunas |
|---|---|---:|
| QueryTable | TAB_PROD | — |

---

## Volumes por fonte (top 15)

| Fonte | Linhas |
|---|---:|
| NFE | 239.694 |
| ENTRADA DE NOTAS - [TODAS] | 238.866 |
| NFE - IDEAL | 163.759 |
| COT | 159.886 |
| NF COM ITENS - CONSOLIDADO | 118.176 |
| CP | 116.933 |
| PMP_ID | 115.190 |
| INFLAÇÃO | 115.190 |
| PMP_ID_INF | 115.190 |
| COT - IDEAL | 113.960 |
| NF ADT - IDEAL | 81.666 |
| PMP_PROD_INF | 79.844 |
| NF COM ITENS - IDEAL | 78.466 |
| NUM_COT | 66.491 |
| COT_MIN_FORN | 66.311 |

---

## Notas de uso

- **NFE** é a fonte principal de compras. Tem 63 colunas com enriquecimento analítico completo (curvas, PMP, IMP, INF, cotação mínima).
- **CP** tem 49 colunas com todo o detalhe de contas a pagar.
- **COT** tem 32 colunas com dados de cotação por produto/fornecedor/mês.
- **AD_v3** e **ADIANTAMENTO_NFE** são as fontes principais de adiantamentos.
- **FILIAIS_SUPPLY** é a dimensão de filiais recomendada para suprimentos.
- **TAB_PROD** é a tabela de referência de produtos (dicionário).
