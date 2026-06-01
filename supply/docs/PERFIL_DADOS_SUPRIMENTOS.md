# Perfil de dados - SUPRIMENTOS

Gerado em: `2026-05-27T13:30:29`.

Este perfil foi criado a partir de amostras pequenas (`limit 5`) das fontes `Table` e `QueryTable` do workspace `SUPRIMENTOS`.

Arquivos tecnicos:

- `output\suprimentos_profile\suprimentos_sources_profile.json`
- `output\suprimentos_profile\suprimentos_sources_profile.csv`
- `output\suprimentos_profile\samples/`

## Resumo

- Fontes analisadas: `53`.
- Fontes com amostra OK: `53`.
- Fontes com erro de amostra: `0`.

## Fontes por dominio inferido

### Adiantamentos

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | ADIANTAMENTO_NFE | 16 | 5 | ok |
| QueryTable | AD_v1 | 11 | 5 | ok |
| QueryTable | AD_v2 | 11 | 5 | ok |
| QueryTable | AD_v3 | 16 | 5 | ok |
| Table | NF ADT - IDEAL | 30 | 5 | ok |
| Table | NF ADT - MELHOR | 30 | 5 | ok |
| Table | NF ADT - POMME VITA | 30 | 5 | ok |

### Contas a pagar

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | CP_MOV | 12 | 5 | ok |
| QueryTable | CP_SALDO_2025 | 13 | 5 | ok |
| QueryTable | CP_SALDO_2026 | 13 | 5 | ok |
| QueryTable | CP_SALDO_2026_v2 | 12 | 5 | ok |
| QueryTable | CP_SEMANA | 13 | 5 | ok |
| Table | CP | 49 | 5 | ok |
| Table | TODAS - CONTAS A PAGAR | 46 | 0 | ok |

### Cotacoes

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | COT | 32 | 5 | ok |
| QueryTable | COT_MIN_FORN | 7 | 5 | ok |
| QueryTable | NUM_COT | 18 | 5 | ok |
| Table | COT - IDEAL | 25 | 5 | ok |
| Table | COT - MELHOR | 25 | 5 | ok |
| Table | COT - SUPERA | 25 | 5 | ok |
| Table | [RC] COTAÇÃO DE PREÇOS - OLD | 20 | 5 | ok |

### Curva ABC e consumo

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | CURVA ABC FORN - TOTAL | 7 | 5 | ok |
| QueryTable | CURVA FORN - TODAS | 6 | 5 | ok |
| QueryTable | CURVA ID - TODAS | 6 | 5 | ok |
| QueryTable | CURVA PROD - IDEAL | 6 | 5 | ok |
| QueryTable | CURVA PROD - MELHOR | 6 | 5 | ok |
| QueryTable | CURVA PROD - SUPERA | 6 | 5 | ok |
| QueryTable | CURVA PROD - TODAS | 7 | 5 | ok |

### Filiais e organizacao

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| Table | FILIAIS | 12 | 5 | ok |
| Table | FILIAIS_DRO | 19 | 5 | ok |
| Table | FILIAIS_NEW | 19 | 5 | ok |
| Table | FILIAIS_SUPPLY | 12 | 5 | ok |

### Fornecedores

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | FORN_CP_25_26 | 1 | 5 | ok |

### Notas fiscais e itens

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | ENTRADA DE NOTAS - [TODAS] | 42 | 5 | ok |
| QueryTable | NF COM ITENS - CONSOLIDADO | 47 | 5 | ok |
| QueryTable | NFE | 63 | 5 | ok |
| Table | NF COM ITENS - IDEAL | 29 | 5 | ok |
| Table | NF COM ITENS - ME | 29 | 5 | ok |
| Table | NF COM ITENS - SU | 29 | 5 | ok |
| Table | NFE - IDEAL | 25 | 5 | ok |
| Table | NFE - MELHOR | 25 | 5 | ok |
| Table | NFE - SUPERA | 25 | 5 | ok |

### Preco medio e inflacao

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | INFLAÇÃO | 27 | 5 | ok |
| QueryTable | PMP_ID | 4 | 5 | ok |
| QueryTable | PMP_ID_INF | 8 | 5 | ok |
| QueryTable | PMP_ID_INF_12 | 22 | 5 | ok |
| QueryTable | PMP_PROD | 5 | 5 | ok |
| QueryTable | PMP_PROD_INF | 9 | 5 | ok |
| QueryTable | PMP_PROD_INF_12 | 21 | 5 | ok |

### Produtos

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | TAB_PROD | 4 | 5 | ok |

### Resultado/financeiro gerencial

| Tipo | Fonte | Colunas | Amostra | Status |
|---|---|---:|---:|---|
| QueryTable | FAT_SUP | 9 | 5 | ok |
| Table | TIPOCONTA | 4 | 5 | ok |
| Table | TODAS - DRO SUM | 21 | 5 | ok |

## Dicionario preliminar por fonte

### ADIANTAMENTO_NFE

- Tipo: `QueryTable`.
- View ID: `2130260000026349219`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\01_querytable_adiantamento_nfe.csv`.

| # | Coluna |
|---:|---|
| 1 | ANO |
| 2 | MESANO |
| 3 | NMEMP |
| 4 | FI.NEGOCIO |
| 5 | ID |
| 6 | CDFILIAL |
| 7 | NMFILIAL |
| 8 | CAT2 |
| 9 | CDPRODESTO |
| 10 | CDFORNECED |
| 11 | FANTASIA_OFICIAL |
| 12 | RAZAO_OFICIAL |
| 13 | VLRUNITPOND |
| 14 | VLRUNITPOND_EST |
| 15 | QTDE_EST |
| 16 | TOTAL |

### AD_v1

- Tipo: `QueryTable`.
- View ID: `2130260000026354443`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\02_querytable_ad_v1.csv`.

| # | Coluna |
|---:|---|
| 1 | MES_PGTO |
| 2 | E.CDFILIAL |
| 3 | E.NMPRODUTO_OFICIAL |
| 4 | E.QTDE_EST |
| 5 | MES_ENTRADA |
| 6 | E.CDPRODESTO |
| 7 | VALOR_CONCILIADO |
| 8 | ANO_ENTRADA |
| 9 | E.NMEMP |
| 10 | E.CDFORNECED |
| 11 | E.FANTASIA_OFICIAL |

### AD_v2

- Tipo: `QueryTable`.
- View ID: `2130260000026354707`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\03_querytable_ad_v2.csv`.

| # | Coluna |
|---:|---|
| 1 | ANO_ENTRADA |
| 2 | MES_ENTRADA |
| 3 | MES_PGTO |
| 4 | E.NMEMP |
| 5 | E.CDFILIAL |
| 6 | E.CDFORNECED |
| 7 | E.FANTASIA_OFICIAL |
| 8 | E.CDPRODESTO |
| 9 | E.NMPRODUTO_OFICIAL |
| 10 | E.QTDE_EST |
| 11 | VALOR_CONCILIADO |

### AD_v3

- Tipo: `QueryTable`.
- View ID: `2130260000026362009`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\04_querytable_ad_v3.csv`.

| # | Coluna |
|---:|---|
| 1 | ANO |
| 2 | MES_ENTRADA |
| 3 | MES_PGTO |
| 4 | NMEMP |
| 5 | UF |
| 6 | CDFILIAL |
| 7 | NMFILIAL |
| 8 | CDFORNECED |
| 9 | FANTASIA_OFICIAL |
| 10 | CAT1 |
| 11 | CAT2 |
| 12 | CDPRODESTO |
| 13 | NMPRODUTO_OFICIAL |
| 14 | E.QTDE_EST |
| 15 | VALOR_FINAL |
| 16 | STATUS_CONCILIACAO |

### NF ADT - IDEAL

- Tipo: `Table`.
- View ID: `2130260000026457002`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\41_table_nf_adt_ideal.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | NRONOTA_NF |
| 19 | NRONOTA_AD |
| 20 | STATUS_CONC |
| 21 | MESANO |
| 22 | MES |
| 23 | SGMES |
| 24 | ANO |
| 25 | VLRUNITPOND |
| 26 | QTDE_EST |
| 27 | VLRUNITPOND_EST |
| 28 | TOTAL |
| 29 | DTENTRADA |
| 30 | DTEMISSAO |

### NF ADT - MELHOR

- Tipo: `Table`.
- View ID: `2130260000026589027`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\42_table_nf_adt_melhor.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | DTENTRADA |
| 19 | DTEMISSAO |
| 20 | NRONOTA_NF |
| 21 | NRONOTA_AD |
| 22 | STATUS_CONC |
| 23 | MESANO |
| 24 | MES |
| 25 | SGMES |
| 26 | ANO |
| 27 | VLRUNITPOND |
| 28 | QTDE_EST |
| 29 | VLRUNITPOND_EST |
| 30 | TOTAL |

### NF ADT - POMME VITA

- Tipo: `Table`.
- View ID: `2130260000026589359`.
- Dominio inferido: `Adiantamentos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\43_table_nf_adt_pomme_vita.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | DTENTRADA |
| 19 | DTEMISSAO |
| 20 | NRONOTA_NF |
| 21 | NRONOTA_AD |
| 22 | STATUS_CONC |
| 23 | MESANO |
| 24 | MES |
| 25 | SGMES |
| 26 | ANO |
| 27 | VLRUNITPOND |
| 28 | QTDE_EST |
| 29 | VLRUNITPOND_EST |
| 30 | TOTAL |

### CP_MOV

- Tipo: `QueryTable`.
- View ID: `2130260000026747005`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\07_querytable_cp_mov.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |
| 2 | NMFANTFORN |
| 3 | NMRAZSOCFORN |
| 4 | ANO |
| 5 | SEMANA_ANO |
| 6 | INI_SEMANA |
| 7 | FIM_SEMANA |
| 8 | ENTRA_DIVIDA_SEMANA |
| 9 | SAI_DIVIDA_SEMANA |
| 10 | VAR_LIQ_SEMANA |
| 11 | SALDO_DIVIDA_SEMANA |
| 12 | CDTPCTPAGAR |

### CP_SALDO_2025

- Tipo: `QueryTable`.
- View ID: `2130260000026756002`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\08_querytable_cp_saldo_2025.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |
| 2 | CDTPCTPAGAR |
| 3 | NMFANTFORN |
| 4 | NMRAZSOCFORN |
| 5 | TIPO_LINHA |
| 6 | ANO |
| 7 | SEMANA_ANO |
| 8 | INI_SEMANA |
| 9 | FIM_SEMANA |
| 10 | ENTRA_DIVIDA_SEMANA |
| 11 | SAI_DIVIDA_SEMANA |
| 12 | VAR_LIQ_SEMANA |
| 13 | SALDO_DIVIDA_SEMANA |

### CP_SALDO_2026

- Tipo: `QueryTable`.
- View ID: `2130260000026747561`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\09_querytable_cp_saldo_2026.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |
| 2 | CDTPCTPAGAR |
| 3 | NMFANTFORN |
| 4 | NMRAZSOCFORN |
| 5 | TIPO_LINHA |
| 6 | ANO |
| 7 | SEMANA_ANO |
| 8 | INI_SEMANA |
| 9 | FIM_SEMANA |
| 10 | ENTRA_DIVIDA_SEMANA |
| 11 | SAI_DIVIDA_SEMANA |
| 12 | VAR_LIQ_SEMANA |
| 13 | SALDO_DIVIDA_SEMANA |

### CP_SALDO_2026_v2

- Tipo: `QueryTable`.
- View ID: `2130260000026805633`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\10_querytable_cp_saldo_2026_v2.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |
| 2 | NMFANTFORN |
| 3 | NMRAZSOCFORN |
| 4 | TIPO_LINHA |
| 5 | ANO |
| 6 | SEMANA_ANO |
| 7 | INI_SEMANA |
| 8 | FIM_SEMANA |
| 9 | ENTRA_DIVIDA_SEMANA |
| 10 | SAI_DIVIDA_SEMANA |
| 11 | VAR_LIQ_SEMANA |
| 12 | SALDO_DIVIDA_SEMANA |

### CP_SEMANA

- Tipo: `QueryTable`.
- View ID: `2130260000026727012`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\11_querytable_cp_semana.csv`.

| # | Coluna |
|---:|---|
| 1 | T.FORNECEDOR |
| 2 | T.NMFANTFORN |
| 3 | T.NMRAZSOCFORN |
| 4 | T.ANO |
| 5 | T.SEMANA_ANO |
| 6 | T.INI_SEMANA |
| 7 | T.FIM_SEMANA |
| 8 | VALOR_PAGO_SEMANA |
| 9 | QTD_PAGAMENTOS_SEMANA |
| 10 | VALOR_VENCIMENTOS_SEMANA |
| 11 | QTD_VENCIMENTOS_SEMANA |
| 12 | VALOR_VENCIDO_SEMANA |
| 13 | QTD_VENCIDOS_SEMANA |

### CP

- Tipo: `Table`.
- View ID: `2130260000026616007`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\36_table_cp.csv`.

| # | Coluna |
|---:|---|
| 1 | CDAGENCIA |
| 2 | CDFILIAL |
| 3 | CDFORNECED |
| 4 | CDSERIEENTR |
| 5 | CDTPCTPAGAR |
| 6 | DIAS |
| 7 | DSCONTAPAG |
| 8 | DSCONTCORR |
| 9 | DSTPCTPAGAR |
| 10 | IDHABIBPAG |
| 11 | IDSTATBPAG |
| 12 | IDSTATUS |
| 13 | IDTPIJURFORN |
| 14 | IDTPIJURNF |
| 15 | LIBERADO |
| 16 | NMAGENCIA |
| 17 | NMBANCO |
| 18 | NMEMPRESA |
| 19 | NMFANTFORN |
| 20 | CDFILIAL_CP |
| 21 | NMFILIAL_CP |
| 22 | NMRAZSOCFORN |
| 23 | NRBAIXAPAG |
| 24 | NRCHEQUE |
| 25 | NRLANBOLPAG |
| 26 | NRNOTAFISC |
| 27 | PENDENTE |
| 28 | REDUZIDO |
| 29 | SGESTADO |
| 30 | STATUSPAG |
| 31 | VRBAIXAPAG |
| 32 | CDBANCO |
| 33 | CDCONTCORR |
| 34 | CDEMPRESA |
| 35 | CDPICTCONT |
| 36 | CDREDUCONT |
| 37 | CDTPBAIXAPAG |
| 38 | DTATUAVENPAG |
| 39 | DTBAIXAPAG |
| 40 | DTEMISSAO |
| 41 | DTENTRSAID |
| 42 | DTORIGVENPAG |
| 43 | NRINSJURNF |
| 44 | NRLANCTONF |
| 45 | VRATUAPAG |
| 46 | VRORIGPAG |
| 47 | RAZAO_OFICIAL |
| 48 | FAIXA_DIAS |
| 49 | STATUS_VENC |

### TODAS - CONTAS A PAGAR

- Tipo: `Table`.
- View ID: `2130260000026610007`.
- Dominio inferido: `Contas a pagar`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\51_table_todas_contas_a_pagar.csv`.

| # | Coluna |
|---:|---|
| 1 | CDAGENCIA |
| 2 | CDBANCO |
| 3 | CDCONTCORR |
| 4 | CDEMPRESA |
| 5 | CDFILIAL |
| 6 | CDFORNECED |
| 7 | CDPICTCONT |
| 8 | CDREDUCONT |
| 9 | CDSERIEENTR |
| 10 | CDTPBAIXAPAG |
| 11 | CDTPCTPAGAR |
| 12 | DIAS |
| 13 | DSCONTAPAG |
| 14 | DSCONTCORR |
| 15 | DSTPCTPAGAR |
| 16 | DTATUAVENPAG |
| 17 | DTBAIXAPAG |
| 18 | DTEMISSAO |
| 19 | DTENTRSAID |
| 20 | DTORIGVENPAG |
| 21 | IDHABIBPAG |
| 22 | IDSTATBPAG |
| 23 | IDSTATUS |
| 24 | IDTPIJURFORN |
| 25 | IDTPIJURNF |
| 26 | LIBERADO |
| 27 | NMAGENCIA |
| 28 | NMBANCO |
| 29 | NMEMPRESA |
| 30 | NMFANTFORN |
| 31 | CDFILIAL_CP |
| 32 | NMFILIAL_CP |
| 33 | NMRAZSOCFORN |
| 34 | NRBAIXAPAG |
| 35 | NRCHEQUE |
| 36 | NRINSJURNF |
| 37 | NRLANBOLPAG |
| 38 | NRLANCTONF |
| 39 | NRNOTAFISC |
| 40 | PENDENTE |
| 41 | REDUZIDO |
| 42 | SGESTADO |
| 43 | STATUSPAG |
| 44 | VRATUAPAG |
| 45 | VRBAIXAPAG |
| 46 | VRORIGPAG |

### COT

- Tipo: `QueryTable`.
- View ID: `2130260000025185218`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\05_querytable_cot.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | ID |
| 3 | CAT1 |
| 4 | CAT2 |
| 5 | CAT3 |
| 6 | CAT4 |
| 7 | CAT5 |
| 8 | MARCA |
| 9 | REGIAO |
| 10 | UF |
| 11 | CDFORNECED |
| 12 | NMRAZSOCFORN |
| 13 | NMFANTFORN |
| 14 | MESANO |
| 15 | MES |
| 16 | SGMES |
| 17 | ANO |
| 18 | CDFORMPGTO |
| 19 | NMFORMPGTO |
| 20 | CDPRODUTO |
| 21 | NMPRODUTO |
| 22 | CDPRODUTO_EST |
| 23 | NMPRODUTO_EST |
| 24 | PRECOUNIT |
| 25 | PRECOUNIT_EST |
| 26 | NMPRODUTO_OFICIAL |
| 27 | CURVA_PROD |
| 28 | POS_PROD |
| 29 | CURVA_FORN |
| 30 | POS_FORN |
| 31 | CURVA_ID |
| 32 | POS_ID |

### COT_MIN_FORN

- Tipo: `QueryTable`.
- View ID: `2130260000025675146`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\06_querytable_cot_min_forn.csv`.

| # | Coluna |
|---:|---|
| 1 | ID |
| 2 | MESANO |
| 3 | POS_FORN |
| 4 | CURVA_FORN |
| 5 | FORNE_FANTASIA |
| 6 | PRECOUNIT_COT |
| 7 | PRIORIDADE |

### NUM_COT

- Tipo: `QueryTable`.
- View ID: `2130260000026094963`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\25_querytable_num_cot.csv`.

| # | Coluna |
|---:|---|
| 1 | POS_ID |
| 2 | CURVA_ID |
| 3 | POS_PROD |
| 4 | CURVA_PROD |
| 5 | ID |
| 6 | NMPRODUTO_EST |
| 7 | CAT2 |
| 8 | MESANO |
| 9 | UF |
| 10 | NMEMP |
| 11 | QTD_COT |
| 12 | MIN_COT |
| 13 | MED_COT |
| 14 | MAX_COT |
| 15 | FORN_MENOR_PRECO |
| 16 | CNPJ_MENOR_PRECO |
| 17 | POS_FORN |
| 18 | CURVA_FORN |

### COT - IDEAL

- Tipo: `Table`.
- View ID: `2130260000025183360`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\33_table_cot_ideal.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | ID |
| 3 | CAT1 |
| 4 | CAT2 |
| 5 | CAT3 |
| 6 | CAT4 |
| 7 | CAT5 |
| 8 | MARCA |
| 9 | REGIAO |
| 10 | UF |
| 11 | CDFORNECED |
| 12 | NMRAZSOCFORN |
| 13 | NMFANTFORN |
| 14 | MESANO |
| 15 | MES |
| 16 | SGMES |
| 17 | ANO |
| 18 | CDFORMPGTO |
| 19 | NMFORMPGTO |
| 20 | CDPRODUTO |
| 21 | NMPRODUTO |
| 22 | CDPRODUTO_EST |
| 23 | NMPRODUTO_EST |
| 24 | PRECOUNIT |
| 25 | PRECOUNIT_EST |

### COT - MELHOR

- Tipo: `Table`.
- View ID: `2130260000025183646`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\34_table_cot_melhor.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | ID |
| 3 | CAT1 |
| 4 | CAT2 |
| 5 | CAT3 |
| 6 | CAT4 |
| 7 | CAT5 |
| 8 | MARCA |
| 9 | REGIAO |
| 10 | UF |
| 11 | CDFORNECED |
| 12 | NMRAZSOCFORN |
| 13 | NMFANTFORN |
| 14 | MESANO |
| 15 | MES |
| 16 | SGMES |
| 17 | ANO |
| 18 | CDFORMPGTO |
| 19 | NMFORMPGTO |
| 20 | CDPRODUTO |
| 21 | NMPRODUTO |
| 22 | CDPRODUTO_EST |
| 23 | NMPRODUTO_EST |
| 24 | PRECOUNIT |
| 25 | PRECOUNIT_EST |

### COT - SUPERA

- Tipo: `Table`.
- View ID: `2130260000025183932`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\35_table_cot_supera.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | ID |
| 3 | CAT1 |
| 4 | CAT2 |
| 5 | CAT3 |
| 6 | CAT4 |
| 7 | CAT5 |
| 8 | MARCA |
| 9 | REGIAO |
| 10 | UF |
| 11 | CDFORNECED |
| 12 | NMRAZSOCFORN |
| 13 | NMFANTFORN |
| 14 | MESANO |
| 15 | MES |
| 16 | SGMES |
| 17 | ANO |
| 18 | CDFORMPGTO |
| 19 | NMFORMPGTO |
| 20 | CDPRODUTO |
| 21 | NMPRODUTO |
| 22 | CDPRODUTO_EST |
| 23 | NMPRODUTO_EST |
| 24 | PRECOUNIT |
| 25 | PRECOUNIT_EST |

### [RC] COTAÇÃO DE PREÇOS - OLD

- Tipo: `Table`.
- View ID: `2130260000001512585`.
- Dominio inferido: `Cotacoes`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\53_table_rc_cota_o_de_pre_os_old.csv`.

| # | Coluna |
|---:|---|
| 1 | SG |
| 2 | CDFILIAL |
| 3 | NMFILIAL |
| 4 | NMREGIAO |
| 5 | NV1 |
| 6 | NV2 |
| 7 | NV3 |
| 8 | NV4 |
| 9 | NV5 |
| 10 | CDPRODUTO |
| 11 | NMPRODUTO |
| 12 | QTSOLI |
| 13 | VLRPRECO |
| 14 | TOTALPROD |
| 15 | CDFORNECED |
| 16 | RAZAOFORN |
| 17 | FANTASIAFORN |
| 18 | MES |
| 19 | ANO |
| 20 | MES/ANO |

### CURVA ABC FORN - TOTAL

- Tipo: `QueryTable`.
- View ID: `2130260000028973002`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\12_querytable_curva_abc_forn_total.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |
| 2 | RAZAO_SOCIAL |
| 3 | TOT_FORN |
| 4 | PERC |
| 5 | TOT_ACUM |
| 6 | CURVA |
| 7 | POS |

### CURVA FORN - TODAS

- Tipo: `QueryTable`.
- View ID: `2130260000025494002`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\13_querytable_curva_forn_todas.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |
| 2 | TOT_FORN |
| 3 | PERC |
| 4 | TOT_ACUM |
| 5 | CURVA |
| 6 | POS |

### CURVA ID - TODAS

- Tipo: `QueryTable`.
- View ID: `2130260000025185715`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\14_querytable_curva_id_todas.csv`.

| # | Coluna |
|---:|---|
| 1 | TE.ID |
| 2 | TE.TOT_ITEM |
| 3 | TE.PERC |
| 4 | TOT_ACUM |
| 5 | CURVA |
| 6 | POS |

### CURVA PROD - IDEAL

- Tipo: `QueryTable`.
- View ID: `2130260000025209012`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\15_querytable_curva_prod_ideal.csv`.

| # | Coluna |
|---:|---|
| 1 | TE.ID |
| 2 | TE.TOT_ITEM |
| 3 | TE.PERC |
| 4 | TOT_ACUM |
| 5 | CURVA |
| 6 | POS |

### CURVA PROD - MELHOR

- Tipo: `QueryTable`.
- View ID: `2130260000025209286`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\16_querytable_curva_prod_melhor.csv`.

| # | Coluna |
|---:|---|
| 1 | TE.ID |
| 2 | TE.TOT_ITEM |
| 3 | TE.PERC |
| 4 | TOT_ACUM |
| 5 | CURVA |
| 6 | POS |

### CURVA PROD - SUPERA

- Tipo: `QueryTable`.
- View ID: `2130260000025209149`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\17_querytable_curva_prod_supera.csv`.

| # | Coluna |
|---:|---|
| 1 | TE.ID |
| 2 | TE.TOT_ITEM |
| 3 | TE.PERC |
| 4 | TOT_ACUM |
| 5 | CURVA |
| 6 | POS |

### CURVA PROD - TODAS

- Tipo: `QueryTable`.
- View ID: `2130260000025423006`.
- Dominio inferido: `Curva ABC e consumo`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\18_querytable_curva_prod_todas.csv`.

| # | Coluna |
|---:|---|
| 1 | CDPRODESTO |
| 2 | NMPRODUTO_OFICIAL |
| 3 | TOT_ITEM |
| 4 | PERC |
| 5 | TOT_ACUM |
| 6 | CURVA |
| 7 | POS |

### FILIAIS

- Tipo: `Table`.
- View ID: `2130260000025580155`.
- Dominio inferido: `Filiais e organizacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\37_table_filiais.csv`.

| # | Coluna |
|---:|---|
| 1 | EMPRESA |
| 2 | S_EMP |
| 3 | CDFILIAL |
| 4 | LOCAL |
| 5 | CLIENTE |
| 6 | SIGLA |
| 7 | NOME |
| 8 | ATIVA |
| 9 | NEGOCIO |
| 10 | REGIAO |
| 11 | AREA |
| 12 | CONTROLE |

### FILIAIS_DRO

- Tipo: `Table`.
- View ID: `2130260000026003056`.
- Dominio inferido: `Filiais e organizacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\38_table_filiais_dro.csv`.

| # | Coluna |
|---:|---|
| 1 | EMPRESA |
| 2 | S_EMP |
| 3 | CDFILIAL |
| 4 | LOCAL |
| 5 | CLIENTE |
| 6 | SIGLA |
| 7 | NOME |
| 8 | ATIVA |
| 9 | NEGOCIO |
| 10 | REGIAO |
| 11 | AREA |
| 12 | ENDEREÇO |
| 13 | LATITUDE |
| 14 | LAT |
| 15 | LONGITUDE |
| 16 | LON |
| 17 | CONTROLE |
| 18 | LAT2 |
| 19 | LON2 |

### FILIAIS_NEW

- Tipo: `Table`.
- View ID: `2130260000026003474`.
- Dominio inferido: `Filiais e organizacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\39_table_filiais_new.csv`.

| # | Coluna |
|---:|---|
| 1 | EMPRESA |
| 2 | S_EMP |
| 3 | CDFILIAL |
| 4 | LOCAL |
| 5 | CLIENTE |
| 6 | SIGLA |
| 7 | NOME |
| 8 | ATIVA |
| 9 | NEGOCIO |
| 10 | REGIAO |
| 11 | AREA |
| 12 | ENDEREÇO |
| 13 | LATITUDE |
| 14 | LAT |
| 15 | LONGITUDE |
| 16 | LON |
| 17 | CONTROLE |
| 18 | LAT2 |
| 19 | LON2 |

### FILIAIS_SUPPLY

- Tipo: `Table`.
- View ID: `2130260000025580003`.
- Dominio inferido: `Filiais e organizacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\40_table_filiais_supply.csv`.

| # | Coluna |
|---:|---|
| 1 | EMPRESA |
| 2 | S_EMP |
| 3 | CDFILIAL |
| 4 | LOCAL |
| 5 | CLIENTE |
| 6 | SIGLA |
| 7 | NOME |
| 8 | ATIVA |
| 9 | NEGOCIO |
| 10 | REGIAO |
| 11 | AREA |
| 12 | CONTROLE |

### FORN_CP_25_26

- Tipo: `QueryTable`.
- View ID: `2130260000026805532`.
- Dominio inferido: `Fornecedores`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\21_querytable_forn_cp_25_26.csv`.

| # | Coluna |
|---:|---|
| 1 | CDFORNECED |

### ENTRADA DE NOTAS - [TODAS]

- Tipo: `QueryTable`.
- View ID: `2130260000025494206`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\19_querytable_entrada_de_notas_todas.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | MESANO |
| 19 | MES |
| 20 | SGMES |
| 21 | ANO |
| 22 | VLRUNITPOND |
| 23 | QTDE_EST |
| 24 | VLRUNITPOND_EST |
| 25 | TOTAL |
| 26 | NMPRODUTO_OFICIAL |
| 27 | CDPRODUTO_OFICIAL |
| 28 | CDFORNECED_OFICIAL |
| 29 | FANTASIA_OFICIAL |
| 30 | RAZAO_OFICIAL |
| 31 | AREA |
| 32 | ATIVA |
| 33 | CODFILIAL |
| 34 | CLIENTE |
| 35 | CONTROLE |
| 36 | EMPRESA |
| 37 | LOCAL |
| 38 | NEGOCIO |
| 39 | NOME |
| 40 | REGIAO |
| 41 | SIGLA |
| 42 | S_EMP |

### NF COM ITENS - CONSOLIDADO

- Tipo: `QueryTable`.
- View ID: `2130260000027214968`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\23_querytable_nf_com_itens_consolidado.csv`.

| # | Coluna |
|---:|---|
| 1 | FILIAL |
| 2 | SGESTADO |
| 3 | NMREGIAO |
| 4 | OPERAC |
| 5 | CDFORNECED |
| 6 | NMRAZSOCFORN |
| 7 | NMFANTFORN |
| 8 | CAT1 |
| 9 | CAT2 |
| 10 | CAT3 |
| 11 | CAT4 |
| 12 | CAT5 |
| 13 | CDPRODUTO |
| 14 | NMPRODUTO |
| 15 | CDPRODESTO |
| 16 | NMPRODUTO_EST |
| 17 | DTENTRADA |
| 18 | DTEMISSAO |
| 19 | NRNOTA |
| 20 | CHAVE |
| 21 | MESANO |
| 22 | MES |
| 23 | ANO |
| 24 | NMEMP |
| 25 | SGMES |
| 26 | VLRUNIT |
| 27 | TOTAL |
| 28 | QTDE_EST |
| 29 | VLRUNIT_EST |
| 30 | CDFILIAL |
| 31 | ID |
| 32 | NMPRODUTO_OFICIAL |
| 33 | CDPRODUTO_OFICIAL |
| 34 | CDFORNECED_OFICIAL |
| 35 | FANTASIA_OFICIAL |
| 36 | RAZAO_OFICIAL |
| 37 | CURVA_PROD |
| 38 | POS_PROD |
| 39 | CURVA_FORN |
| 40 | POS_FORN |
| 41 | CURVA_ID |
| 42 | POS_ID |
| 43 | CODFILIAL |
| 44 | CLIENTE |
| 45 | LOCAL |
| 46 | NEGOCIO |
| 47 | SIGLA |

### NFE

- Tipo: `QueryTable`.
- View ID: `2130260000025181862`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\24_querytable_nfe.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | MESANO |
| 19 | MES |
| 20 | SGMES |
| 21 | ANO |
| 22 | VLRUNITPOND |
| 23 | QTDE_EST |
| 24 | VLRUNITPOND_EST |
| 25 | TOTAL |
| 26 | NMPRODUTO_OFICIAL |
| 27 | CDPRODUTO_OFICIAL |
| 28 | CDFORNECED_OFICIAL |
| 29 | FANTASIA_OFICIAL |
| 30 | RAZAO_OFICIAL |
| 31 | CURVA_PROD |
| 32 | POS_PROD |
| 33 | CURVA_FORN |
| 34 | POS_FORN |
| 35 | CURVA_ID |
| 36 | POS_ID |
| 37 | PMP_PROD |
| 38 | PMP_PROD_1 |
| 39 | PMP_PROD_3 |
| 40 | PMP_PROD_6 |
| 41 | PMP_PROD_12 |
| 42 | PMP_PROD_PID |
| 43 | PMP_PROD_NM |
| 44 | IMP_PRODT |
| 45 | PMP_PROD_ID |
| 46 | PMP_ID_1 |
| 47 | PMP_ID_3 |
| 48 | PMP_ID_6 |
| 49 | PMP_ID_12 |
| 50 | PMP_ID_NM |
| 51 | IMP_ID |
| 52 | PRE_MIN_COT |
| 53 | FORN_MIN_COT |
| 54 | IMP_COT |
| 55 | INF_ID_1 |
| 56 | INF_ID_PMP |
| 57 | INF_PROD_1 |
| 58 | INF_PROD_PMP |
| 59 | FI.CODFILIAL |
| 60 | FI.CLIENTE |
| 61 | FI.LOCAL |
| 62 | FI.NEGOCIO |
| 63 | FI.SIGLA |

### NF COM ITENS - IDEAL

- Tipo: `Table`.
- View ID: `2130260000027214002`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\44_table_nf_com_itens_ideal.csv`.

| # | Coluna |
|---:|---|
| 1 | FILIAL |
| 2 | SGESTADO |
| 3 | NMREGIAO |
| 4 | OPERAC |
| 5 | CDFORNECED |
| 6 | NMRAZSOCFORN |
| 7 | NMFANTFORN |
| 8 | CAT1 |
| 9 | CAT2 |
| 10 | CAT3 |
| 11 | CAT4 |
| 12 | CAT5 |
| 13 | CDPRODUTO |
| 14 | NMPRODUTO |
| 15 | CDPRODESTO |
| 16 | NMPRODUTO_EST |
| 17 | DTENTRADA |
| 18 | DTEMISSAO |
| 19 | NRNOTA |
| 20 | CHAVE |
| 21 | MESANO |
| 22 | MES |
| 23 | ANO |
| 24 | NMEMP |
| 25 | SGMES |
| 26 | VLRUNIT |
| 27 | TOTAL |
| 28 | QTDE_EST |
| 29 | VLRUNIT_EST |

### NF COM ITENS - ME

- Tipo: `Table`.
- View ID: `2130260000027214646`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\45_table_nf_com_itens_me.csv`.

| # | Coluna |
|---:|---|
| 1 | FILIAL |
| 2 | SGESTADO |
| 3 | NMREGIAO |
| 4 | OPERAC |
| 5 | CDFORNECED |
| 6 | NMRAZSOCFORN |
| 7 | NMFANTFORN |
| 8 | CAT1 |
| 9 | CAT2 |
| 10 | CAT3 |
| 11 | CAT4 |
| 12 | CAT5 |
| 13 | CDPRODUTO |
| 14 | NMPRODUTO |
| 15 | CDPRODESTO |
| 16 | NMPRODUTO_EST |
| 17 | DTENTRADA |
| 18 | DTEMISSAO |
| 19 | NRNOTA |
| 20 | CHAVE |
| 21 | MESANO |
| 22 | MES |
| 23 | ANO |
| 24 | NMEMP |
| 25 | SGMES |
| 26 | VLRUNIT |
| 27 | TOTAL |
| 28 | QTDE_EST |
| 29 | VLRUNIT_EST |

### NF COM ITENS - SU

- Tipo: `Table`.
- View ID: `2130260000027214324`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\46_table_nf_com_itens_su.csv`.

| # | Coluna |
|---:|---|
| 1 | FILIAL |
| 2 | SGESTADO |
| 3 | NMREGIAO |
| 4 | OPERAC |
| 5 | CDFORNECED |
| 6 | NMRAZSOCFORN |
| 7 | NMFANTFORN |
| 8 | CAT1 |
| 9 | CAT2 |
| 10 | CAT3 |
| 11 | CAT4 |
| 12 | CAT5 |
| 13 | CDPRODUTO |
| 14 | NMPRODUTO |
| 15 | CDPRODESTO |
| 16 | NMPRODUTO_EST |
| 17 | DTENTRADA |
| 18 | DTEMISSAO |
| 19 | NRNOTA |
| 20 | CHAVE |
| 21 | MESANO |
| 22 | MES |
| 23 | ANO |
| 24 | NMEMP |
| 25 | SGMES |
| 26 | VLRUNIT |
| 27 | TOTAL |
| 28 | QTDE_EST |
| 29 | VLRUNIT_EST |

### NFE - IDEAL

- Tipo: `Table`.
- View ID: `2130260000025181004`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\47_table_nfe_ideal.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | MESANO |
| 19 | MES |
| 20 | SGMES |
| 21 | ANO |
| 22 | VLRUNITPOND |
| 23 | QTDE_EST |
| 24 | VLRUNITPOND_EST |
| 25 | TOTAL |

### NFE - MELHOR

- Tipo: `Table`.
- View ID: `2130260000025181290`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\48_table_nfe_melhor.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | MESANO |
| 19 | MES |
| 20 | SGMES |
| 21 | ANO |
| 22 | VLRUNITPOND |
| 23 | QTDE_EST |
| 24 | VLRUNITPOND_EST |
| 25 | TOTAL |

### NFE - SUPERA

- Tipo: `Table`.
- View ID: `2130260000025181576`.
- Dominio inferido: `Notas fiscais e itens`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\49_table_nfe_supera.csv`.

| # | Coluna |
|---:|---|
| 1 | NMEMP |
| 2 | UF |
| 3 | ID |
| 4 | CDFILIAL |
| 5 | NMFILIAL |
| 6 | CDFORNECED |
| 7 | NMRAZSOCFORN |
| 8 | NMFANTFORN |
| 9 | CAT1 |
| 10 | CAT2 |
| 11 | CAT3 |
| 12 | CAT4 |
| 13 | CAT5 |
| 14 | CDPRODUTO |
| 15 | NMPRODUTO |
| 16 | CDPRODESTO |
| 17 | NMPRODUTO_EST |
| 18 | MESANO |
| 19 | MES |
| 20 | SGMES |
| 21 | ANO |
| 22 | VLRUNITPOND |
| 23 | QTDE_EST |
| 24 | VLRUNITPOND_EST |
| 25 | TOTAL |

### INFLAÇÃO

- Tipo: `QueryTable`.
- View ID: `2130260000026132374`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\22_querytable_infla_o.csv`.

| # | Coluna |
|---:|---|
| 1 | ID |
| 2 | MESANO |
| 3 | UF |
| 4 | NMEMP |
| 5 | CAT1 |
| 6 | CAT2 |
| 7 | CAT3 |
| 8 | CAT4 |
| 9 | CAT5 |
| 10 | NMPRODUTO_EST |
| 11 | CDPRODUTO_OFICIAL |
| 12 | CURVA_ID |
| 13 | POS_ID |
| 14 | TOTAL |
| 15 | PMP_ID |
| 16 | PMP_ID_1 |
| 17 | PMP_PROD |
| 18 | PMP_PROD_1 |
| 19 | SOMA_INF_ID_1 |
| 20 | SOMA_INF_ID_PMP |
| 21 | SOMA_INF_PROD_1 |
| 22 | SOMA_INF_PROD_PMP |
| 23 | PERC_INF_ID_1 |
| 24 | PERC_INF_ID_PMP |
| 25 | PERC_INF_PROD_1 |
| 26 | PERC_INF_PROD_PMP |
| 27 | ANO |

### PMP_ID

- Tipo: `QueryTable`.
- View ID: `2130260000025577131`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\26_querytable_pmp_id.csv`.

| # | Coluna |
|---:|---|
| 1 | ID |
| 2 | NMPRODUTO_EST |
| 3 | MESANO |
| 4 | PMP_ID |

### PMP_ID_INF

- Tipo: `QueryTable`.
- View ID: `2130260000025808066`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\27_querytable_pmp_id_inf.csv`.

| # | Coluna |
|---:|---|
| 1 | PMP_ID_0 |
| 2 | PMP_ID_1 |
| 3 | PMP_ID_3 |
| 4 | PMP_ID_6 |
| 5 | PMP_ID_12 |
| 6 | PI_ID |
| 7 | PI_NMPRODUTO |
| 8 | PI_MESANO |

### PMP_ID_INF_12

- Tipo: `QueryTable`.
- View ID: `2130260000025859008`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\28_querytable_pmp_id_inf_12.csv`.

| # | Coluna |
|---:|---|
| 1 | ID |
| 2 | POS_ID |
| 3 | CDPRODUTO_OFICIAL |
| 4 | NMPRODUTO_OFICIAL |
| 5 | CAT1 |
| 6 | CAT2 |
| 7 | CAT3 |
| 8 | CURVA_ID |
| 9 | MESANO |
| 10 | PMP_0 |
| 11 | PMP_1 |
| 12 | PMP_2 |
| 13 | PMP_3 |
| 14 | PMP_4 |
| 15 | PMP_5 |
| 16 | PMP_6 |
| 17 | PMP_7 |
| 18 | PMP_8 |
| 19 | PMP_9 |
| 20 | PMP_10 |
| 21 | PMP_11 |
| 22 | PMP_12 |

### PMP_PROD

- Tipo: `QueryTable`.
- View ID: `2130260000025577012`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\29_querytable_pmp_prod.csv`.

| # | Coluna |
|---:|---|
| 1 | PID |
| 2 | CDPRODUTO_OFICIAL |
| 3 | MESANO |
| 4 | PMP_PROD |
| 5 | NMPRODUTO_OFICIAL |

### PMP_PROD_INF

- Tipo: `QueryTable`.
- View ID: `2130260000025808259`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\30_querytable_pmp_prod_inf.csv`.

| # | Coluna |
|---:|---|
| 1 | PMP_PROD_0 |
| 2 | PMP_PROD_1 |
| 3 | PMP_PROD_3 |
| 4 | PMP_PROD_6 |
| 5 | PMP_PROD_12 |
| 6 | PP_PID |
| 7 | PP_CDPROFICIAL |
| 8 | PP_NMPROFICIAL |
| 9 | PP_MESANO |

### PMP_PROD_INF_12

- Tipo: `QueryTable`.
- View ID: `2130260000025859434`.
- Dominio inferido: `Preco medio e inflacao`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\31_querytable_pmp_prod_inf_12.csv`.

| # | Coluna |
|---:|---|
| 1 | CDPRODUTO_OFICIAL |
| 2 | NMPRODUTO_OFICIAL |
| 3 | CAT1 |
| 4 | CAT2 |
| 5 | CAT3 |
| 6 | CURVA_PROD |
| 7 | MESANO |
| 8 | PMP_0 |
| 9 | PMP_1 |
| 10 | PMP_2 |
| 11 | PMP_3 |
| 12 | PMP_4 |
| 13 | PMP_5 |
| 14 | PMP_6 |
| 15 | PMP_7 |
| 16 | PMP_8 |
| 17 | PMP_9 |
| 18 | PMP_10 |
| 19 | PMP_11 |
| 20 | PMP_12 |
| 21 | POS_PROD |

### TAB_PROD

- Tipo: `QueryTable`.
- View ID: `2130260000025330341`.
- Dominio inferido: `Produtos`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\32_querytable_tab_prod.csv`.

| # | Coluna |
|---:|---|
| 1 | CDPRODESTO |
| 2 | NMPRODUTO_EST |
| 3 | TOTAL_PROD |
| 4 | QTDE_PROD |

### FAT_SUP

- Tipo: `QueryTable`.
- View ID: `2130260000025890015`.
- Dominio inferido: `Resultado/financeiro gerencial`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\20_querytable_fat_sup.csv`.

| # | Coluna |
|---:|---|
| 1 | TF.MESANO |
| 2 | TF.NMEMP |
| 3 | TF.CDFILIAL |
| 4 | TF.NMFILIAL |
| 5 | SUP |
| 6 | CMV |
| 7 | FAT |
| 8 | TF.UF |
| 9 | TF.FI.NEGOCIO |

### TIPOCONTA

- Tipo: `Table`.
- View ID: `2130260000026620092`.
- Dominio inferido: `Resultado/financeiro gerencial`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\50_table_tipoconta.csv`.

| # | Coluna |
|---:|---|
| 1 | CDCLASSFINANC |
| 2 | NMCLASSFINANC |
| 3 | CDTPCTPAGAR |
| 4 | NMTPCTPAGAR |

### TODAS - DRO SUM

- Tipo: `Table`.
- View ID: `2130260000025889773`.
- Dominio inferido: `Resultado/financeiro gerencial`.
- Status da amostra: `ok`.
- Amostra: `output\suprimentos_profile\samples\52_table_todas_dro_sum.csv`.

| # | Coluna |
|---:|---|
| 1 | MESANO |
| 2 | ANO |
| 3 | CDFILIAL |
| 4 | NMFILIAL |
| 5 | EMPRESA |
| 6 | REGIAO |
| 7 | NEGOCIO |
| 8 | VALOR_REAL |
| 9 | FAT_ |
| 10 | CMV_ |
| 11 | MDO_ |
| 12 | ADM_ |
| 13 | NOP_ |
| 14 | INV_ |
| 15 | RES_ |
| 16 | _cmv |
| 17 | _mdo |
| 18 | _adm |
| 19 | _nop |
| 20 | _inv |
| 21 | _res |
