# Perfil das Fontes — SUPRIMENTOS

Gerado em: `2026-06-01T15:10` — amostras de 5 linhas por fonte.

Cobre apenas **Tables** e **QueryTables** do workspace SUPRIMENTOS.
Pivots, AnalysisViews e Dashboards são camada visual — não incluídos.

---

- Fontes analisadas: `53`
- Com amostra OK: `51`
- Com erro ou vazia: `2`

---

## ADIANTAMENTO_NFE

_Amostra indisponível._

## AD_v1

**Colunas:** 11  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `MES_PGTO` | texto | 2024/08 |
| `E.CDFILIAL` | inteiro | 8813 |
| `E.NMPRODUTO_OFICIAL` | texto | PAPEL SULFITE BRANCO A4 500FL - PC |
| `E.QTDE_EST` | inteiro | 15 |
| `MES_ENTRADA` | texto | 2024/08 |
| `E.CDPRODESTO` | texto | D202102000 |
| `VALOR_CONCILIADO` | decimal | 344.85 |
| `ANO_ENTRADA` | inteiro | 2024 |
| `E.NMEMP` | texto | RC |
| `E.CDFORNECED` | texto | J13328409000183 |
| `E.FANTASIA_OFICIAL` | texto | SIXPEL (SP) |

## AD_v2

**Colunas:** 11  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `ANO_ENTRADA` | inteiro | 2024 |
| `MES_ENTRADA` | texto | 2024/08 |
| `MES_PGTO` | texto | 2024/08 |
| `E.NMEMP` | texto | RC |
| `E.CDFILIAL` | inteiro | 8813 |
| `E.CDFORNECED` | texto | J13328409000183 |
| `E.FANTASIA_OFICIAL` | texto | SIXPEL (SP) |
| `E.CDPRODESTO` | texto | D202102000 |
| `E.NMPRODUTO_OFICIAL` | texto | PAPEL SULFITE BRANCO A4 500FL - PC |
| `E.QTDE_EST` | inteiro | 15 |
| `VALOR_CONCILIADO` | decimal | 344.85 |

## AD_v3

**Colunas:** 16  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `ANO` | inteiro | 2024 |
| `MES_ENTRADA` | texto | 2024/08 |
| `MES_PGTO` | texto | 2024/08 |
| `NMEMP` | texto | RC |
| `UF` | texto | SP |
| `CDFILIAL` | inteiro | 8813 |
| `NMFILIAL` | texto | HOSP. MARIO DEGNI |
| `CDFORNECED` | texto | J13328409000183 |
| `FANTASIA_OFICIAL` | texto | SIXPEL (SP) |
| `CAT1` | texto | D - DESPESAS |
| `CAT2` | texto | D2 - ESCRITORIO |
| `CDPRODESTO` | texto | D202102000 |
| `NMPRODUTO_OFICIAL` | texto | PAPEL SULFITE BRANCO A4 500FL - PC |
| `E.QTDE_EST` | inteiro | 15 |
| `VALOR_FINAL` | decimal | 344.85 |
| `STATUS_CONCILIACAO` | texto | CONCILIADO |

## COT

**Colunas:** 32  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | RC |
| `ID` | texto | RCMAI108105060 |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I1 - ESTOCAVEIS |
| `CAT3` | texto | I108 - SOBREMESA |
| `CAT4` | texto | I1081 - DOCES |
| `CAT5` | texto | I108105 - FRUTAS SECAS |
| `MARCA` | texto | 00001 - FORNECEDOR |
| `REGIAO` | texto | 003 - REGIONAL - MARANHAO |
| `UF` | texto | MA |
| `CDFORNECED` | texto | J51142623000130 |
| `NMRAZSOCFORN` | texto | FONTE VIVA ALIMENTOS LTDA |
| `NMFANTFORN` | texto | FONTE VIVA |
| `MESANO` | texto | 2026/03 |
| `MES` | inteiro | 3 |
| `SGMES` | texto | MAR |
| `ANO` | inteiro | 2026 |
| `CDFORMPGTO` | inteiro |  |
| `NMFORMPGTO` | texto |  |
| `CDPRODUTO` | texto | I108105060 |
| `NMPRODUTO` | texto | UVA PASSA PRETA - KG |
| `CDPRODUTO_EST` | texto | I108105060 |
| `NMPRODUTO_EST` | texto | UVA PASSA PRETA - KG |
| `PRECOUNIT` | decimal | 49.65 |
| `PRECOUNIT_EST` | decimal | 49.65 |
| `NMPRODUTO_OFICIAL` | texto | UVA PASSA PRETA - KG |
| `CURVA_PROD` | texto | CC |
| `POS_PROD` | inteiro | 961 |
| `CURVA_FORN` | texto | AAA |
| `POS_FORN` | inteiro | 1 |
| `CURVA_ID` | texto | CCC |
| `POS_ID` | inteiro | 12259 |

## COT  - IDEAL

**Colunas:** 25  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | RC |
| `ID` | texto | RCSPI302117000 |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I3 - HORTIFRUTI |
| `CAT3` | texto | I302 - PROCESSADOS |
| `CAT4` | texto | I3021 - VERDURAS |
| `CAT5` | texto | I302117 - MOYASHI |
| `MARCA` | texto | 00001 - FORNECEDOR |
| `REGIAO` | texto | 001 - REGIONAL - SAO PAULO |
| `UF` | texto | SP |
| `CDFORNECED` | texto | J65941775000107 |
| `NMRAZSOCFORN` | texto | HORTCLEAN DIST. PROD. ALIM. LTDA |
| `NMFANTFORN` | texto | HORTCLEAN (NOVA) |
| `MESANO` | texto | 2025/06 |
| `MES` | inteiro | 6 |
| `SGMES` | texto | JUN |
| `ANO` | inteiro | 2025 |
| `CDFORMPGTO` | inteiro | 1 |
| `NMFORMPGTO` | texto | Da Data de Emissao (Inclusive) |
| `CDPRODUTO` | texto | I302117000 |
| `NMPRODUTO` | texto | MOYASHI PROCESSADO INTEIRO - KG |
| `CDPRODUTO_EST` | texto | I302117000 |
| `NMPRODUTO_EST` | texto | MOYASHI PROCESSADO INTEIRO - KG |
| `PRECOUNIT` | decimal | 23 |
| `PRECOUNIT_EST` | decimal | 23 |

## COT - MELHOR

**Colunas:** 25  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | ME |
| `ID` | texto | MEESI101203020 |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I1 - ESTOCAVEIS |
| `CAT3` | texto | I101 - NUTRICIONAIS |
| `CAT4` | texto | I1012 - MATINAIS INFANTIS |
| `CAT5` | texto | I101203 - CREMOGEMA TRADICIONAL |
| `MARCA` | texto | 00001 - FORNECEDOR |
| `REGIAO` | texto | 007 - BAIXO GUANDU |
| `UF` | texto | ES |
| `CDFORNECED` | texto | J05880726000180 |
| `NMRAZSOCFORN` | texto | SUDESTE INDUSTRIA E COMERCIO LTDA |
| `NMFANTFORN` | texto | SUDESTE |
| `MESANO` | texto | 2025/02 |
| `MES` | inteiro | 2 |
| `SGMES` | texto | FEB |
| `ANO` | inteiro | 2025 |
| `CDFORMPGTO` | inteiro | 1 |
| `NMFORMPGTO` | texto | Data Emissao NF (Inclusive) |
| `CDPRODUTO` | texto | I101203028 |
| `NMPRODUTO` | texto | CREMOGEMA TRADICIONAL - 180GR- PC |
| `CDPRODUTO_EST` | texto | I101203020 |
| `NMPRODUTO_EST` | texto | CREMOGEMA TRADICIONAL - KG |
| `PRECOUNIT` | decimal | 9.25 |
| `PRECOUNIT_EST` | decimal | 51.38889 |

## COT - SUPERA

**Colunas:** 25  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | SU |
| `ID` | texto | SUSPI503113000 |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I5 - LIMPEZA |
| `CAT3` | texto | I503 - LIQUIDOS |
| `CAT4` | texto | I5031 - DOMESTICO |
| `CAT5` | texto | I503113 - LUSTRA MOVEIS |
| `MARCA` | texto | 00001 - FORNECEDOR |
| `REGIAO` | texto | 001 - REGIAO SAO PAULO |
| `UF` | texto | SP |
| `CDFORNECED` | texto | J28278839000105 |
| `NMRAZSOCFORN` | texto | DUMOPP COMERCIO PRODUTOS HIGIENE LIMPEZA LTDA ME |
| `NMFANTFORN` | texto | DUMOPP |
| `MESANO` | texto | 2026/06 |
| `MES` | inteiro | 6 |
| `SGMES` | texto | JUN |
| `ANO` | inteiro | 2026 |
| `CDFORMPGTO` | inteiro | 2 |
| `NMFORMPGTO` | texto | VINTE E OITO DIAS (INCLUSIVE) |
| `CDPRODUTO` | texto | I503113000 |
| `NMPRODUTO` | texto | LUSTRA MOVEIS 500ML - UN |
| `CDPRODUTO_EST` | texto | I503113000 |
| `NMPRODUTO_EST` | texto | LUSTRA MOVEIS 500ML - UN |
| `PRECOUNIT` | decimal | 23.9 |
| `PRECOUNIT_EST` | decimal | 23.9 |

## COT_MIN_FORN

**Colunas:** 7  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `ID` | texto | MEESI102101000 |
| `MESANO` | texto | 2025/06 |
| `POS_FORN` | inteiro | 19 |
| `CURVA_FORN` | texto | AAA |
| `FORNE_FANTASIA` | texto | J05880726000180 - SUDESTE |
| `PRECOUNIT_COT` | decimal | 4.6 |
| `PRIORIDADE` | inteiro | 1 |

## CP

**Colunas:** 49  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDAGENCIA` | inteiro | 3394 |
| `CDFILIAL` | inteiro | 9999 |
| `CDFORNECED` | texto | J44407989000128 |
| `CDSERIEENTR` | texto | OP |
| `CDTPCTPAGAR` | inteiro | 80 |
| `DIAS` | decimal | -8.874699074074075 |
| `DSCONTAPAG` | texto | PARC 5 DE 5 |
| `DSCONTCORR` | texto | BANCO BRADESCO |
| `DSTPCTPAGAR` | texto | TAXAS DIVERSAS |
| `IDHABIBPAG` | texto | N |
| `IDSTATBPAG` | texto | B |
| `IDSTATUS` | texto | A |
| `IDTPIJURFORN` | texto | J |
| `IDTPIJURNF` | texto | J |
| `LIBERADO` | decimal | 83307 |
| `NMAGENCIA` | texto | BANCO BRADESCO |
| `NMBANCO` | texto | BANCO BRADESCO S/A |
| `NMEMPRESA` | texto | SUPERA ALIMENTACAO |
| `NMFANTFORN` | texto | CONSELHO REGIONAL DE NUTRICIONISTAS - 3º |
| `CDFILIAL_CP` | inteiro | 9999 |
| `NMFILIAL_CP` | texto | SUPERA  ALIMENT  SERVICOS LTDA |
| `NMRAZSOCFORN` | texto | CONSELHO REGIONAL DE NUTRICIONISTAS - 3º |
| `NRBAIXAPAG` | inteiro | 56080 |
| `NRCHEQUE` | vazio |  |
| `NRLANBOLPAG` | inteiro | 90190 |
| `NRNOTAFISC` | inteiro | 7019046 |
| `PENDENTE` | inteiro | 0 |
| `REDUZIDO` | texto | 237 / 237 / 3394 |
| `SGESTADO` | texto | SP |
| `STATUSPAG` | texto | Baixado |
| `VRBAIXAPAG` | decimal | 11760.54 |
| `CDBANCO` | inteiro | 237 |
| `CDCONTCORR` | inteiro | 341 |
| `CDEMPRESA` | inteiro | 1 |
| `CDPICTCONT` | inteiro | 9 |
| `CDREDUCONT` | inteiro | 237 |
| `CDTPBAIXAPAG` | inteiro | 7 |
| `DTATUAVENPAG` | texto | 10/06/2026 |
| `DTBAIXAPAG` | texto | 29/04/2026 |
| `DTEMISSAO` | texto | 01/06/2026 |
| `DTENTRSAID` | texto | 01/06/2026 |
| `DTORIGVENPAG` | texto | 10/06/2026 |
| `NRINSJURNF` | inteiro | 44407989000128 |
| `NRLANCTONF` | inteiro | 72062 |
| `VRATUAPAG` | decimal | 833.07 |
| `VRORIGPAG` | decimal | 833.07 |
| `RAZAO_OFICIAL` | texto | CONSELHO REGIONAL DE NUTRICIONISTAS - 3º |
| `FAIXA_DIAS` | texto | AV 7 |
| `STATUS_VENC` | texto | A Vencer |

## CP_MOV

**Colunas:** 12  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J56642960000100 |
| `NMFANTFORN` | texto | LOJAS CEM |
| `NMRAZSOCFORN` | texto | LOJAS CEM |
| `ANO` | inteiro | 2026 |
| `SEMANA_ANO` | inteiro | 10 |
| `INI_SEMANA` | texto | 02 Mar, 2026 00:00:00 |
| `FIM_SEMANA` | texto | 08 Mar, 2026 00:00:00 |
| `ENTRA_DIVIDA_SEMANA` | decimal | 0 |
| `SAI_DIVIDA_SEMANA` | inteiro | 11588 |
| `VAR_LIQ_SEMANA` | decimal | -11588 |
| `SALDO_DIVIDA_SEMANA` | decimal | 0 |
| `CDTPCTPAGAR` | inteiro | 98 |

## CP_SALDO_2025

**Colunas:** 13  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J61116828000102 |
| `CDTPCTPAGAR` | inteiro | 1 |
| `NMFANTFORN` | texto | CALVO (SP) |
| `NMRAZSOCFORN` | texto | CALVO COMERCIO IMPORTACAO LTDA |
| `TIPO_LINHA` | texto | SALDO_INICIAL_2025 |
| `ANO` | inteiro | 2025 |
| `SEMANA_ANO` | inteiro | 0 |
| `INI_SEMANA` | vazio |  |
| `FIM_SEMANA` | vazio |  |
| `ENTRA_DIVIDA_SEMANA` | decimal | 0 |
| `SAI_DIVIDA_SEMANA` | inteiro | 0 |
| `VAR_LIQ_SEMANA` | decimal | 0 |
| `SALDO_DIVIDA_SEMANA` | decimal | 0 |

## CP_SALDO_2026

**Colunas:** 13  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J29732766000142 |
| `CDTPCTPAGAR` | inteiro | 4 |
| `NMFANTFORN` | texto | JSL DISTRIBUIDORA |
| `NMRAZSOCFORN` | texto | JSL DISTRIBUIDORA ALIMENTOS EIRELI |
| `TIPO_LINHA` | texto | SEMANA_2026 |
| `ANO` | inteiro | 2026 |
| `SEMANA_ANO` | inteiro | 13 |
| `INI_SEMANA` | texto | 23 Mar, 2026 00:00:00 |
| `FIM_SEMANA` | texto | 29 Mar, 2026 00:00:00 |
| `ENTRA_DIVIDA_SEMANA` | inteiro | 0 |
| `SAI_DIVIDA_SEMANA` | decimal | 1.997 |
| `VAR_LIQ_SEMANA` | decimal | -1.997 |
| `SALDO_DIVIDA_SEMANA` | decimal | 2.111 |

## CP_SALDO_2026_v2

**Colunas:** 12  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J18461001000107 |
| `NMFANTFORN` | texto | ARBOCLEAN INDUSTRIA |
| `NMRAZSOCFORN` | texto | ARBOCLEAN INDUSTRIA E COMERCIO DE PRODUTOS DE HIGIENE E LIMPEZA LTDA |
| `TIPO_LINHA` | texto | SEMANA_2026 |
| `ANO` | inteiro | 2026 |
| `SEMANA_ANO` | inteiro | 17 |
| `INI_SEMANA` | texto | 20 Apr, 2026 00:00:00 |
| `FIM_SEMANA` | texto | 26 Apr, 2026 00:00:00 |
| `ENTRA_DIVIDA_SEMANA` | decimal | 222981.12000000017 |
| `SAI_DIVIDA_SEMANA` | decimal | 0 |
| `VAR_LIQ_SEMANA` | decimal | 222981.12000000017 |
| `SALDO_DIVIDA_SEMANA` | decimal | -7603.750000000007 |

## CP_SEMANA

**Colunas:** 13  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `T.FORNECEDOR` | texto | J44407989000128 |
| `T.NMFANTFORN` | texto | CONSELHO REGIONAL DE NUTRICIONISTAS - 3º |
| `T.NMRAZSOCFORN` | texto | CONSELHO REGIONAL DE NUTRICIONISTAS - 3º |
| `T.ANO` | inteiro | 2026 |
| `T.SEMANA_ANO` | inteiro | 18 |
| `T.INI_SEMANA` | texto | 27 Apr, 2026 00:00:00 |
| `T.FIM_SEMANA` | texto | 03 May, 2026 00:00:00 |
| `VALOR_PAGO_SEMANA` | decimal | 23521.08 |
| `QTD_PAGAMENTOS_SEMANA` | inteiro | 2 |
| `VALOR_VENCIMENTOS_SEMANA` | inteiro | 0 |
| `QTD_VENCIMENTOS_SEMANA` | inteiro | 0 |
| `VALOR_VENCIDO_SEMANA` | inteiro | 0 |
| `QTD_VENCIDOS_SEMANA` | inteiro | 0 |

## CURVA ABC FORN - TOTAL

**Colunas:** 7  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J04249153000128 |
| `RAZAO_SOCIAL` | texto | MM SECURITIZADORA S.A. |
| `TOT_FORN` | decimal | 64791928 |
| `PERC` | decimal | 6.245433189893888 |
| `TOT_ACUM` | decimal | 6.245433189893888 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 1 |

## CURVA FORN - TODAS

**Colunas:** 6  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J19780714000198 |
| `TOT_FORN` | decimal | 23549645.277159113 |
| `PERC` | decimal | 4.56124287262019 |
| `TOT_ACUM` | decimal | 15.52588042139735 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 2 |

## CURVA ID - TODAS

**Colunas:** 6  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `TE.ID` | texto | RCPEI201203000 |
| `TE.TOT_ITEM` | decimal | 17274232.86999952 |
| `TE.PERC` | decimal | 3.4330448428624547 |
| `TOT_ACUM` | decimal | 3.4330448428624547 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 1 |

## CURVA PROD - IDEAL

**Colunas:** 6  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `TE.ID` | texto | RCPEI201203000 |
| `TE.TOT_ITEM` | decimal | 17274232.86999952 |
| `TE.PERC` | decimal | 3.7532209448848595 |
| `TOT_ACUM` | decimal | 3.7532209448848595 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 1 |

## CURVA PROD - MELHOR

**Colunas:** 6  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `TE.ID` | texto | MEESI601101001 |
| `TE.TOT_ITEM` | decimal | 831016.0290999995 |
| `TE.PERC` | decimal | 4.019358275159196 |
| `TOT_ACUM` | decimal | 4.019358275159196 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 1 |

## CURVA PROD - SUPERA

**Colunas:** 6  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `TE.ID` | texto | SUSPI201104049 |
| `TE.TOT_ITEM` | decimal | 842651.52 |
| `TE.PERC` | decimal | 2.382213076257399 |
| `TOT_ACUM` | decimal | 2.382213076257399 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 1 |

## CURVA PROD - TODAS

**Colunas:** 7  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDPRODESTO` | texto | I201203000 |
| `NMPRODUTO_OFICIAL` | texto | FILE PEITO FRANGO - KG |
| `TOT_ITEM` | decimal | 34458318.75300962 |
| `PERC` | decimal | 6.674103111314447 |
| `TOT_ACUM` | decimal | 6.674103111314447 |
| `CURVA` | texto | AAA |
| `POS` | inteiro | 1 |

## ENTRADA DE NOTAS - [TODAS]

**Colunas:** 42  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | RC |
| `UF` | texto | SP |
| `ID` | texto | RCSPA101107035 |
| `CDFILIAL` | inteiro | 8888 |
| `NMFILIAL` | texto | RC NUTRY ALIMENTACAO LTDA |
| `CDFORNECED` | texto | J71052559000537 |
| `NMRAZSOCFORN` | texto | BELMICRO TECNOLOGIA S/A |
| `NMFANTFORN` | texto | BELMICRO TECNOLOGIA S/A |
| `CAT1` | texto | A - ATIVOS |
| `CAT2` | texto | A1 - ATIVOS DIRETOS |
| `CAT3` | texto | A101 - EQUIPAMENTOS PARA COZINHA |
| `CAT4` | texto | A1011 - COCCAO |
| `CAT5` | texto | A101107 - FORNO |
| `CDPRODUTO` | texto | A101107035 |
| `NMPRODUTO` | texto | FORNO MICROONDAS 21LT - UN |
| `CDPRODESTO` | texto | A101107035 |
| `NMPRODUTO_EST` | texto | FORNO MICROONDAS 21LT - UN |
| `MESANO` | texto | 2025/07 |
| `MES` | inteiro | 7 |
| `SGMES` | texto | JUL |
| `ANO` | inteiro | 2025 |
| `VLRUNITPOND` | decimal | 598.8900146484 |
| `QTDE_EST` | inteiro | 1 |
| `VLRUNITPOND_EST` | decimal | 598.8900146484 |
| `TOTAL` | decimal | 598.8900146484 |
| `NMPRODUTO_OFICIAL` | texto | FORNO MICROONDAS 21LT - UN |
| `CDPRODUTO_OFICIAL` | texto | A101107035 |
| `CDFORNECED_OFICIAL` | texto | J71052559000537 |
| `FANTASIA_OFICIAL` | texto | BELMICRO TECNOLOGIA S/A |
| `RAZAO_OFICIAL` | texto | BELMICRO TECNOLOGIA S/A |
| `AREA` | texto | ALIMENTAÇÃO |
| `ATIVA` | texto | Yes |
| `CODFILIAL` | inteiro | 8888 |
| `CLIENTE` | texto | MATRIZ |
| `CONTROLE` | texto | S |
| `EMPRESA` | texto | IDEAL |
| `LOCAL` | texto | MATRIZ |
| `NEGOCIO` | texto | _MATRIZ |
| `NOME` | texto | RC NUTRY ALIMENTACAO LTDA |
| `REGIAO` | texto | SP |
| `SIGLA` | texto | MATRIZ_RC |
| `S_EMP` | texto | RC |

## FAT_SUP

**Colunas:** 9  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `TF.MESANO` | texto | 2024/09 |
| `TF.NMEMP` | texto | RC |
| `TF.CDFILIAL` | inteiro | 8833 |
| `TF.NMFILIAL` | texto | HOSPITAL STA CASA MISERICORDIA |
| `SUP` | texto | 592.001 |
| `CMV` | decimal | 553.299 |
| `FAT` | texto | 1.129.989,91 |
| `TF.UF` | texto | PA |
| `TF.FI.NEGOCIO` | texto | HOSPITAL |

## FILIAIS

**Colunas:** 12  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `EMPRESA` | texto | POMME VITA |
| `S_EMP` | texto | PV |
| `CDFILIAL` | inteiro | 0 |
| `LOCAL` | texto | ENCERRADAS |
| `CLIENTE` | texto | OFF |
| `SIGLA` | texto | OFF |
| `NOME` | texto | ENCERRADAS |
| `ATIVA` | texto | No |
| `NEGOCIO` | texto | ENCERRADA |
| `REGIAO` | texto |  |
| `AREA` | texto | ALIMENTAÇÃO |
| `CONTROLE` | texto | S |

## FILIAIS_DRO

**Colunas:** 19  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `EMPRESA` | texto | IDEAL |
| `S_EMP` | texto | RC |
| `CDFILIAL` | inteiro | 3047 |
| `LOCAL` | texto | CAPAAC |
| `CLIENTE` | texto | SESA |
| `SIGLA` | texto | CAPAAC |
| `NOME` | texto | ARISTIDES A. CAMPOS |
| `ATIVA` | texto | No |
| `NEGOCIO` | texto | HOSPITAL |
| `REGIAO` | texto | ES |
| `AREA` | texto | ALIMENTAÇÃO |
| `ENDEREÇO` | texto | AV. LEOPOLDINO SMARZARO 17 29310370 CACHOEIRO DE ITAPEMIRIM ES |
| `LATITUDE` | decimal | -20.84631072 |
| `LAT` | decimal | -20.84631072 |
| `LONGITUDE` | decimal | -41.15475558 |
| `LON` | decimal | -41.15475558 |
| `CONTROLE` | texto | S |
| `LAT2` | decimal | -20.84631072 |
| `LON2` | decimal | -41.15475558 |

## FILIAIS_NEW

**Colunas:** 19  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `EMPRESA` | texto | IDEAL |
| `S_EMP` | texto | RC |
| `CDFILIAL` | inteiro | 3047 |
| `LOCAL` | texto | CAPAAC |
| `CLIENTE` | texto | SESA |
| `SIGLA` | texto | CAPAAC |
| `NOME` | texto | ARISTIDES A. CAMPOS |
| `ATIVA` | texto | No |
| `NEGOCIO` | texto | HOSPITAL |
| `REGIAO` | texto | ES |
| `AREA` | texto | ALIMENTAÇÃO |
| `ENDEREÇO` | texto | AV. LEOPOLDINO SMARZARO 17 29310370 CACHOEIRO DE ITAPEMIRIM ES |
| `LATITUDE` | decimal | -20.84631072 |
| `LAT` | decimal | -20.84631072 |
| `LONGITUDE` | decimal | -41.15475558 |
| `LON` | decimal | -41.15475558 |
| `CONTROLE` | texto | S |
| `LAT2` | decimal | -20.84631072 |
| `LON2` | decimal | -41.15475558 |

## FILIAIS_SUPPLY

**Colunas:** 12  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `EMPRESA` | texto | IDEAL |
| `S_EMP` | texto | RC |
| `CDFILIAL` | inteiro | 3047 |
| `LOCAL` | texto | CAPAAC |
| `CLIENTE` | texto | SESA |
| `SIGLA` | texto | CAPAAC |
| `NOME` | texto | ARISTIDES A. CAMPOS |
| `ATIVA` | texto | No |
| `NEGOCIO` | texto | HOSPITAL |
| `REGIAO` | texto | ES |
| `AREA` | texto | ALIMENTAÇÃO |
| `CONTROLE` | texto | S |

## FORN_CP_25_26

**Colunas:** 1  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDFORNECED` | texto | J07456600000108 |

## INFLAÇÃO

**Colunas:** 27  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `ID` | texto | RCMAI102303000 |
| `MESANO` | texto | 2024/08 |
| `UF` | texto | MA |
| `NMEMP` | texto | RC |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I1 - ESTOCAVEIS |
| `CAT3` | texto | I102 - CEREAIS |
| `CAT4` | texto | I1023 - GRAOS |
| `CAT5` | texto | I102303 - GRAO DE BICO |
| `NMPRODUTO_EST` | texto | GRAO DE BICO - KG |
| `CDPRODUTO_OFICIAL` | texto | I102303000 |
| `CURVA_ID` | texto | CCC |
| `POS_ID` | inteiro | 7079 |
| `TOTAL` | decimal | 283.880001 |
| `PMP_ID` | decimal | 94.626667 |
| `PMP_ID_1` | decimal |  |
| `PMP_PROD` | decimal | 14.630984466321241 |
| `PMP_PROD_1` | decimal | 13.546842105263158 |
| `SOMA_INF_ID_1` | decimal |  |
| `SOMA_INF_ID_PMP` | decimal |  |
| `SOMA_INF_PROD_1` | decimal | -243.23947468421053 |
| `SOMA_INF_PROD_PMP` | decimal | -3.252427083174249 |
| `PERC_INF_ID_1` | decimal |  |
| `PERC_INF_ID_PMP` | decimal |  |
| `PERC_INF_PROD_1` | decimal | -598.514578266444 |
| `PERC_INF_PROD_PMP` | decimal | -8.00291575434305 |
| `ANO` | inteiro | 2024 |

## NF ADT - IDEAL

**Colunas:** 30  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | RC |
| `UF` | texto | SP |
| `ID` | texto | RCSPI301201060 |
| `CDFILIAL` | inteiro | 8808 |
| `NMFILIAL` | texto | HOSP. ALIPIO CORREA NETO |
| `CDFORNECED` | texto | J65941775000107 |
| `NMRAZSOCFORN` | texto | HORTCLEAN DIST. PROD. ALIM. LTDA |
| `NMFANTFORN` | texto | HORTCLEAN (NOVA) |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I3 - HORTIFRUTI |
| `CAT3` | texto | I301 - IN NATURA |
| `CAT4` | texto | I3012 - LEGUMES |
| `CAT5` | texto | I301201 - ABOBORA |
| `CDPRODUTO` | texto | I301201060 |
| `NMPRODUTO` | texto | ABOBORA SECA - KG |
| `CDPRODESTO` | texto | I301201060 |
| `NMPRODUTO_EST` | texto | ABOBORA SECA - KG |
| `NRONOTA_NF` | inteiro | 285410 |
| `NRONOTA_AD` | vazio |  |
| `STATUS_CONC` | texto | Normal |
| `MESANO` | texto | 2026/04 |
| `MES` | inteiro | 4 |
| `SGMES` | texto | APR |
| `ANO` | inteiro | 2026 |
| `VLRUNITPOND` | decimal | 4.59 |
| `QTDE_EST` | decimal | 4 |
| `VLRUNITPOND_EST` | decimal | 4.59 |
| `TOTAL` | decimal | 18.36 |
| `DTENTRADA` | texto | 06 Apr, 2026 00:00:00 |
| `DTEMISSAO` | texto | 04 Apr, 2026 00:00:00 |

## NF ADT - MELHOR

**Colunas:** 30  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | ME |
| `UF` | texto | ES |
| `ID` | texto | MEESI301204020 |
| `CDFILIAL` | inteiro | 3027 |
| `NMFILIAL` | texto | HOSP. JOAO SANTOS NEVES |
| `CDFORNECED` | texto | J63562389000189 |
| `NMRAZSOCFORN` | texto | TEIXEIRA HORTO MERCADO LTDA |
| `NMFANTFORN` | texto | TEIXEIRA HORTO MERCADO |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I3 - HORTIFRUTI |
| `CAT3` | texto | I301 - IN NATURA |
| `CAT4` | texto | I3012 - LEGUMES |
| `CAT5` | texto | I301204 - BATATA |
| `CDPRODUTO` | texto | I301204020 |
| `NMPRODUTO` | texto | BATATA COMUM - KG |
| `CDPRODESTO` | texto | I301204020 |
| `NMPRODUTO_EST` | texto | BATATA COMUM - KG |
| `DTENTRADA` | texto | 10/01/2026 00:00:00 |
| `DTEMISSAO` | texto | 08/01/2026 00:00:00 |
| `NRONOTA_NF` | inteiro | 109 |
| `NRONOTA_AD` | vazio |  |
| `STATUS_CONC` | texto | Normal |
| `MESANO` | texto | 2026/01 |
| `MES` | inteiro | 1 |
| `SGMES` | texto | JAN |
| `ANO` | inteiro | 2026 |
| `VLRUNITPOND` | decimal | 4 |
| `QTDE_EST` | inteiro | 25 |
| `VLRUNITPOND_EST` | decimal | 4 |
| `TOTAL` | decimal | 100 |

## NF ADT - POMME VITA

**Colunas:** 30  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | SU |
| `UF` | texto | PI |
| `ID` | texto | SUPII502206010 |
| `CDFILIAL` | inteiro | 9911 |
| `NMFILIAL` | texto | COZINHA CENTRAL PICOS |
| `CDFORNECED` | texto | J34251013000155 |
| `NMRAZSOCFORN` | texto | JACYANNE LORRANE ALMEIDA DE OLIVEIRA ROCHA LTDA |
| `NMFANTFORN` | texto | PICOS PLAST (JACYANNE) |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I5 - LIMPEZA |
| `CAT3` | texto | I502 - HIGIENE |
| `CAT4` | texto | I5022 - HIGIENE PROFISSIONAL |
| `CAT5` | texto | I502206 - TOALHA PAPEL |
| `CDPRODUTO` | texto | I502206011 |
| `NMPRODUTO` | texto | PAPEL TOALHA INTERFOLHA BCO 20X21 1000UN - (FD) |
| `CDPRODESTO` | texto | I502206010 |
| `NMPRODUTO_EST` | texto | PAPEL TOALHA INTERFOLHA BCO  20X21- UN |
| `DTENTRADA` | texto | 09/01/2026 00:00:00 |
| `DTEMISSAO` | texto | 07/01/2026 00:00:00 |
| `NRONOTA_NF` | inteiro | 8929 |
| `NRONOTA_AD` | vazio |  |
| `STATUS_CONC` | texto | Normal |
| `MESANO` | texto | 2026/01 |
| `MES` | inteiro | 1 |
| `SGMES` | texto | JAN |
| `ANO` | inteiro | 2026 |
| `VLRUNITPOND` | decimal | 10.22 |
| `QTDE_EST` | decimal | 21000 |
| `VLRUNITPOND_EST` | decimal | 0.01022 |
| `TOTAL` | decimal | 214.62 |

## NF COM ITENS - CONSOLIDADO

**Colunas:** 47  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `FILIAL` | texto | 3053 - HOSPITAL GERAL DE LINHARES |
| `SGESTADO` | texto | ES |
| `NMREGIAO` | texto | REGIONAL - ESPIRITO SANTO |
| `OPERAC` | texto | 48 - NF - Aquisicao de Insumos |
| `CDFORNECED` | texto | J42675575000154 |
| `NMRAZSOCFORN` | texto | COMERCIO LANCHERO EMPORIO LTDA |
| `NMFANTFORN` | texto | LANCHEIRO EMPORIO |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I2 - PERECIVEIS |
| `CAT3` | texto | I202 - FRIOS/EMBUTIDOS |
| `CAT4` | texto | I2021 - FRIOS |
| `CAT5` | texto | I202101 - APRESUNTADO |
| `CDPRODUTO` | texto | I202101010 |
| `NMPRODUTO` | texto | APRESUNTADO FATIADO - KG |
| `CDPRODESTO` | texto | I202101010 |
| `NMPRODUTO_EST` | texto | APRESUNTADO FATIADO - KG |
| `DTENTRADA` | texto | 09/01/2026 00:00:00 |
| `DTEMISSAO` | texto | 07/01/2026 00:00:00 |
| `NRNOTA` | texto | 000000136/1 |
| `CHAVE` | inteiro | 9223372036854775807 |
| `MESANO` | texto | 2026/01 |
| `MES` | inteiro | 1 |
| `ANO` | inteiro | 2026 |
| `NMEMP` | texto | RC |
| `SGMES` | texto | JAN |
| `VLRUNIT` | decimal | 22.99 |
| `TOTAL` | decimal | 142.3081 |
| `QTDE_EST` | decimal | 6.19 |
| `VLRUNIT_EST` | decimal | 22.99 |
| `CDFILIAL` | inteiro | 3053 |
| `ID` | texto | RCESI202101010 |
| `NMPRODUTO_OFICIAL` | texto | APRESUNTADO FATIADO - KG |
| `CDPRODUTO_OFICIAL` | texto | I202101010 |
| `CDFORNECED_OFICIAL` | texto | J42675575000154 |
| `FANTASIA_OFICIAL` | texto | LANCHEIRO EMPORIO |
| `RAZAO_OFICIAL` | texto | COMERCIO LANCHERO EMPORIO LTDA |
| `CURVA_PROD` | texto | BB |
| `POS_PROD` | inteiro | 330 |
| `CURVA_FORN` | texto | CCC |
| `POS_FORN` | inteiro | 509 |
| `CURVA_ID` | texto | BB |
| `POS_ID` | inteiro | 661 |
| `CODFILIAL` | inteiro | 3053 |
| `CLIENTE` | texto | ES |
| `LOCAL` | texto | HOSP_GERAL_LINHARES |
| `NEGOCIO` | texto | HOSPITAL |
| `SIGLA` | texto | HRL |

## NF COM ITENS - IDEAL

**Colunas:** 29  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `FILIAL` | texto | 8808 - HOSP. ALIPIO CORREA NETO |
| `SGESTADO` | texto | SP |
| `NMREGIAO` | texto | REGIONAL - SAO PAULO |
| `OPERAC` | texto | 48 - NF - Aquisicao de Insumos |
| `CDFORNECED` | texto | J65941775000107 |
| `NMRAZSOCFORN` | texto | HORTCLEAN DIST. PROD. ALIM. LTDA |
| `NMFANTFORN` | texto | HORTCLEAN (NOVA) |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I3 - HORTIFRUTI |
| `CAT3` | texto | I301 - IN NATURA |
| `CAT4` | texto | I3012 - LEGUMES |
| `CAT5` | texto | I301223 - PIMENTAO |
| `CDPRODUTO` | texto | I301223020 |
| `NMPRODUTO` | texto | PIMENTAO VERDE - KG |
| `CDPRODESTO` | texto | I301223020 |
| `NMPRODUTO_EST` | texto | PIMENTAO VERDE - KG |
| `DTENTRADA` | texto | 04/02/2026 00:00:00 |
| `DTEMISSAO` | texto | 03/02/2026 00:00:00 |
| `NRNOTA` | texto | 000284202/1 |
| `CHAVE` | inteiro | 9223372036854775807 |
| `MESANO` | texto | 2026/02 |
| `MES` | inteiro | 2 |
| `ANO` | inteiro | 2026 |
| `NMEMP` | texto | RC |
| `SGMES` | texto | FEB |
| `VLRUNIT` | decimal | 5.5 |
| `TOTAL` | decimal | 8.25 |
| `QTDE_EST` | decimal | 1.5 |
| `VLRUNIT_EST` | decimal | 5.5 |

## NF COM ITENS - ME

**Colunas:** 29  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `FILIAL` | texto | 3027 - HOSP. JOAO SANTOS NEVES |
| `SGESTADO` | texto | ES |
| `NMREGIAO` | texto | BAIXO GUANDU |
| `OPERAC` | texto | 01 - NF Compra |
| `CDFORNECED` | texto | J63562389000189 |
| `NMRAZSOCFORN` | texto | TEIXEIRA HORTO MERCADO LTDA |
| `NMFANTFORN` | texto | TEIXEIRA HORTO MERCADO |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I3 - HORTIFRUTI |
| `CAT3` | texto | I301 - IN NATURA |
| `CAT4` | texto | I3012 - LEGUMES |
| `CAT5` | texto | I301202 - ABOBRINHA |
| `CDPRODUTO` | texto | I301202000 |
| `NMPRODUTO` | texto | ABOBRINHA BRASILEIRA - KG |
| `CDPRODESTO` | texto | I301202000 |
| `NMPRODUTO_EST` | texto | ABOBRINHA BRASILEIRA - KG |
| `DTENTRADA` | texto | 10/01/2026 00:00:00 |
| `DTEMISSAO` | texto | 08/01/2026 00:00:00 |
| `NRNOTA` | texto | 000000109/1 |
| `CHAVE` | inteiro | 9223372036854775807 |
| `MESANO` | texto | 2026/01 |
| `MES` | inteiro | 1 |
| `ANO` | inteiro | 2026 |
| `NMEMP` | texto | ME |
| `SGMES` | texto | JAN |
| `VLRUNIT` | decimal | 4 |
| `TOTAL` | decimal | 12 |
| `QTDE_EST` | inteiro | 3 |
| `VLRUNIT_EST` | decimal | 4 |

## NF COM ITENS - SU

**Colunas:** 29  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `FILIAL` | texto | 9911 - COZINHA CENTRAL PICOS |
| `SGESTADO` | texto | PI |
| `NMREGIAO` | texto | PIAUI |
| `OPERAC` | texto | 01 - NF Compras |
| `CDFORNECED` | texto | J36672309000175 |
| `NMRAZSOCFORN` | texto | LUCAS RAFAEL DE SOUSA BARROS |
| `NMFANTFORN` | texto | LUCAS RAFAEL DE SOUSA BARROS |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I3 - HORTIFRUTI |
| `CAT3` | texto | I301 - IN NATURA |
| `CAT4` | texto | I3013 - FRUTAS |
| `CAT5` | texto | I301302 - ABACAXI |
| `CDPRODUTO` | texto | I301302030 |
| `NMPRODUTO` | texto | ABACAXI - KG |
| `CDPRODESTO` | texto | I301302030 |
| `NMPRODUTO_EST` | texto | ABACAXI - KG |
| `DTENTRADA` | texto | 27/01/2026 00:00:00 |
| `DTEMISSAO` | texto | 27/01/2026 00:00:00 |
| `NRNOTA` | texto | 000000467/1 |
| `CHAVE` | inteiro | 9223372036854775807 |
| `MESANO` | texto | 2026/01 |
| `MES` | inteiro | 1 |
| `ANO` | inteiro | 2026 |
| `NMEMP` | texto | SU |
| `SGMES` | texto | JAN |
| `VLRUNIT` | decimal | 8 |
| `TOTAL` | decimal | 24 |
| `QTDE_EST` | decimal | 3 |
| `VLRUNIT_EST` | decimal | 8 |

## NFE

**Colunas:** 63  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | RC |
| `UF` | texto | SP |
| `ID` | texto | RCSPI105303000 |
| `CDFILIAL` | inteiro | 8862 |
| `NMFILIAL` | texto | HOSP. OURO VERDE |
| `CDFORNECED` | texto | J36850123000169 |
| `NMRAZSOCFORN` | texto | PLATINA ESTOQUE ONLINE ALIMENTOS LTDA |
| `NMFANTFORN` | texto | PLATINA (NOVA) |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I1 - ESTOCAVEIS |
| `CAT3` | texto | I105 - FORMULADOS |
| `CAT4` | texto | I1053 - SOBREMESAS |
| `CAT5` | texto | I105303 - CURAU |
| `CDPRODUTO` | texto | I105303001 |
| `NMPRODUTO` | texto | CURAU C/ LEITE EM PO - 1 KG - PC |
| `CDPRODESTO` | texto | I105303000 |
| `NMPRODUTO_EST` | texto | CURAU C/ LEITE EM PO - KG |
| `MESANO` | texto | 2024/11 |
| `MES` | inteiro | 11 |
| `SGMES` | texto | NOV |
| `ANO` | inteiro | 2024 |
| `VLRUNITPOND` | decimal | 11.1 |
| `QTDE_EST` | inteiro | 10 |
| `VLRUNITPOND_EST` | decimal | 11.1 |
| `TOTAL` | decimal | 111 |
| `NMPRODUTO_OFICIAL` | texto | CURAU C/ LEITE EM PO - KG |
| `CDPRODUTO_OFICIAL` | texto | I105303000 |
| `CDFORNECED_OFICIAL` | texto | J36850123000169 |
| `FANTASIA_OFICIAL` | texto | PLATINA (NOVA) |
| `RAZAO_OFICIAL` | texto | PLATINA ESTOQUE ONLINE ALIMENTOS LTDA |
| `CURVA_PROD` | texto | B |
| `POS_PROD` | inteiro | 189 |
| `CURVA_FORN` | texto | B |
| `POS_FORN` | inteiro | 105 |
| `CURVA_ID` | texto | CC |
| `POS_ID` | inteiro | 2802 |
| `PMP_PROD` | decimal | 11.375 |
| `PMP_PROD_1` | decimal | 14.234802955665025 |
| `PMP_PROD_3` | decimal | 13.224915062287657 |
| `PMP_PROD_6` | decimal | 13.882659799260432 |
| `PMP_PROD_12` | decimal |  |
| `PMP_PROD_PID` | texto | I1053030002024/11 |
| `PMP_PROD_NM` | texto | CURAU C/ LEITE EM PO - KG |
| `IMP_PRODT` | decimal | 2.7500000000000036 |
| `PMP_PROD_ID` | decimal | 11.1 |
| `PMP_ID_1` | decimal | 11.1 |
| `PMP_ID_3` | decimal | 15.95 |
| `PMP_ID_6` | decimal | 10.332 |
| `PMP_ID_12` | decimal |  |
| `PMP_ID_NM` | texto | CURAU C/ LEITE EM PO - KG |
| `IMP_ID` | decimal | 0 |
| `PRE_MIN_COT` | vazio |  |
| `FORN_MIN_COT` | vazio |  |
| `IMP_COT` | vazio |  |
| `INF_ID_1` | decimal | 0 |
| `INF_ID_PMP` | decimal | 0 |
| `INF_PROD_1` | decimal | 31.34802955665025 |
| `INF_PROD_PMP` | decimal | 28.598029556650246 |
| `FI.CODFILIAL` | inteiro | 8862 |
| `FI.CLIENTE` | texto | H.MARIO GATTI |
| `FI.LOCAL` | texto | H.MARIO_GATTI |
| `FI.NEGOCIO` | texto | HOSPITAL |
| `FI.SIGLA` | texto | HMG |

## NFE - IDEAL

**Colunas:** 25  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | RC |
| `UF` | texto | SP |
| `ID` | texto | RCSPI403103005 |
| `CDFILIAL` | inteiro | 8867 |
| `NMFILIAL` | texto | HOSP. ALEXANDRE ZAIO |
| `CDFORNECED` | texto | J28278839000105 |
| `NMRAZSOCFORN` | texto | DUMOPP COMERCIO DE PRODUTOS DE HIGIENE E LIMPEZA LTDA |
| `NMFANTFORN` | texto | LILOLIMP DESCARTAVEIS E LIMPEZA |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I4 - DESCARTAVEIS |
| `CAT3` | texto | I403 - PLASTICO |
| `CAT4` | texto | I4031 - BEBIDAS |
| `CAT5` | texto | I403103 - COPO DESCARTAVEL |
| `CDPRODUTO` | texto | I403103006 |
| `NMPRODUTO` | texto | COPO DESC 050ML PS 5000UN - (CX) |
| `CDPRODESTO` | texto | I403103005 |
| `NMPRODUTO_EST` | texto | COPO DESC 050ML PS - UN |
| `MESANO` | texto | 2024/12 |
| `MES` | inteiro | 12 |
| `SGMES` | texto | DEC |
| `ANO` | inteiro | 2024 |
| `VLRUNITPOND` | decimal | 130.85 |
| `QTDE_EST` | decimal | 20000 |
| `VLRUNITPOND_EST` | decimal | 0.02617 |
| `TOTAL` | decimal | 523.4 |

## NFE - MELHOR

**Colunas:** 25  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | ME |
| `UF` | texto | ES |
| `ID` | texto | MEESI502202060 |
| `CDFILIAL` | inteiro | 3026 |
| `NMFILIAL` | texto | HOSP. SILVIO AVIDOS |
| `CDFORNECED` | texto | J05880726000180 |
| `NMRAZSOCFORN` | texto | SUDESTE INDUSTRIA E COMERCIO LTDA |
| `NMFANTFORN` | texto | SUDESTE |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I5 - LIMPEZA |
| `CAT3` | texto | I502 - HIGIENE |
| `CAT4` | texto | I5022 - HIGIENE PROFISSIONAL/EPI |
| `CAT5` | texto | I502202 - PANOS |
| `CDPRODUTO` | texto | I502202060 |
| `NMPRODUTO` | texto | PANO MULTIUSO NEUTRO ROLO 22X300MT - RL |
| `CDPRODESTO` | texto | I502202060 |
| `NMPRODUTO_EST` | texto | PANO MULTIUSO NEUTRO ROLO 22X300MT - RL |
| `MESANO` | texto | 2024/02 |
| `MES` | inteiro | 2 |
| `SGMES` | texto | FEB |
| `ANO` | inteiro | 2024 |
| `VLRUNITPOND` | decimal | 83.02 |
| `QTDE_EST` | inteiro | 5 |
| `VLRUNITPOND_EST` | decimal | 83.02 |
| `TOTAL` | decimal | 415.1 |

## NFE - SUPERA

**Colunas:** 25  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `NMEMP` | texto | SU |
| `UF` | texto | SP |
| `ID` | texto | SUSPI503108005 |
| `CDFILIAL` | inteiro | 9999 |
| `NMFILIAL` | texto | SUPERA  ALIMENT  SERVICOS LTDA |
| `CDFORNECED` | texto | J45159945000199 |
| `NMRAZSOCFORN` | texto | LILOLIMP COMERCIO DE PRODUTOS DESCARTAVEIS E LIMPEZA LTDA |
| `NMFANTFORN` | texto | LILOLIMP DESCARTAVEIS E LIMPEZA |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I5 - LIMPEZA |
| `CAT3` | texto | I503 - LIQUIDOS |
| `CAT4` | texto | I5031 - DOMESTICO |
| `CAT5` | texto | I503108 - DETERGENTE |
| `CDPRODUTO` | texto | I503108000 |
| `NMPRODUTO` | texto | DETERGENTE NEUTRO 24X500ML - (CX) |
| `CDPRODESTO` | texto | I503108005 |
| `NMPRODUTO_EST` | texto | DETERGENTE NEUTRO 500ML - UN |
| `MESANO` | texto | 2024/01 |
| `MES` | inteiro | 1 |
| `SGMES` | texto | JAN |
| `ANO` | inteiro | 2024 |
| `VLRUNITPOND` | decimal | 65 |
| `QTDE_EST` | decimal | 24 |
| `VLRUNITPOND_EST` | decimal | 2.7083333333333335 |
| `TOTAL` | decimal | 65 |

## NUM_COT

**Colunas:** 18  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `POS_ID` | inteiro | 2261 |
| `CURVA_ID` | texto | CC |
| `POS_PROD` | inteiro | 1089 |
| `CURVA_PROD` | texto | CC |
| `ID` | texto | RCPEI205201360 |
| `NMPRODUTO_EST` | texto | POLPA DE FRUTA TAMARINDO - KG |
| `CAT2` | texto | I2 - PERECIVEIS |
| `MESANO` | texto | 2026/02 |
| `UF` | texto | PE |
| `NMEMP` | texto | RC |
| `QTD_COT` | inteiro | 3 |
| `MIN_COT` | decimal | 4.9 |
| `MED_COT` | decimal | 5 |
| `MAX_COT` | decimal | 5.2 |
| `FORN_MENOR_PRECO` | texto | CANAA POLPAS |
| `CNPJ_MENOR_PRECO` | texto | J06015530000190 |
| `POS_FORN` | inteiro | 454 |
| `CURVA_FORN` | texto | CCC |

## PMP_ID

**Colunas:** 4  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `ID` | texto | RCPEI103105020 |
| `NMPRODUTO_EST` | texto | FARINHA DE MANDIOCA TORRADA - KG |
| `MESANO` | texto | 2025/09 |
| `PMP_ID` | decimal | 3.49 |

## PMP_ID_INF

**Colunas:** 8  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `PMP_ID_0` | decimal | 182 |
| `PMP_ID_1` | decimal | 182 |
| `PMP_ID_3` | decimal | 182 |
| `PMP_ID_6` | decimal | 182 |
| `PMP_ID_12` | decimal | 174 |
| `PI_ID` | texto | RCESI105306030 |
| `PI_NMPRODUTO` | texto | GELATINA ZERO AMORA EM PO - KG |
| `PI_MESANO` | texto | 2026/03 |

## PMP_ID_INF_12

**Colunas:** 22  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `ID` | texto | RCDFI103402030 |
| `POS_ID` | inteiro | 3744 |
| `CDPRODUTO_OFICIAL` | texto | I103402030 |
| `NMPRODUTO_OFICIAL` | texto | BISCOITO AGUA E SAL - KG |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I1 - ESTOCAVEIS |
| `CAT3` | texto | I103 - FARINACEOS |
| `CURVA_ID` | texto | CCC |
| `MESANO` | texto | 2026/06 |
| `PMP_0` | vazio |  |
| `PMP_1` | decimal | 8.417508417508417 |
| `PMP_2` | decimal | 8.333333333333332 |
| `PMP_3` | decimal | 8.353535353535353 |
| `PMP_4` | decimal | 8.333333333333332 |
| `PMP_5` | decimal | 8.333333333333332 |
| `PMP_6` | decimal | 8.33939393939394 |
| `PMP_7` | decimal | 8.33939393939394 |
| `PMP_8` | decimal | 8.33939393939394 |
| `PMP_9` | decimal | 8.33939393939394 |
| `PMP_10` | decimal | 8.33939393939394 |
| `PMP_11` | decimal | 8.33939393939394 |
| `PMP_12` | decimal | 8.503703703703703 |

## PMP_PROD

**Colunas:** 5  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `PID` | texto | D6011020002025/04 |
| `CDPRODUTO_OFICIAL` | texto | D601102000 |
| `MESANO` | texto | 2025/04 |
| `PMP_PROD` | decimal | 4763.778366013073 |
| `NMPRODUTO_OFICIAL` | texto | ADIANTAMENTO COMPRA A VISTA |

## PMP_PROD_INF

**Colunas:** 9  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `PMP_PROD_0` | decimal | 16.486886075949368 |
| `PMP_PROD_1` | decimal | 15.116829004329006 |
| `PMP_PROD_3` | decimal | 14.817192982456142 |
| `PMP_PROD_6` | decimal | 13.707990196078432 |
| `PMP_PROD_12` | decimal | 12.760099440646362 |
| `PP_PID` | texto | I3011330002025/12 |
| `PP_CDPROFICIAL` | texto | I301133000 |
| `PP_NMPROFICIAL` | texto | RUCULA - KG |
| `PP_MESANO` | texto | 2025/12 |

## PMP_PROD_INF_12

**Colunas:** 21  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDPRODUTO_OFICIAL` | texto | I107105010 |
| `NMPRODUTO_OFICIAL` | texto | MEL PURO - LT |
| `CAT1` | texto | I - INSUMOS |
| `CAT2` | texto | I1 - ESTOCAVEIS |
| `CAT3` | texto | I107 - MATINAIS |
| `CURVA_PROD` | texto | CCC |
| `MESANO` | texto | 2026/06 |
| `PMP_0` | vazio |  |
| `PMP_1` | decimal | 41.60857142857143 |
| `PMP_2` | decimal | 43.614285714285714 |
| `PMP_3` | decimal | 42.871428571428574 |
| `PMP_4` | decimal | 43.36666666666667 |
| `PMP_5` | decimal | 42.16 |
| `PMP_6` | decimal | 41.32 |
| `PMP_7` | decimal | 41.7925 |
| `PMP_8` | decimal | 40.69 |
| `PMP_9` | decimal | 50.52 |
| `PMP_10` | decimal | 53.32857142857142 |
| `PMP_11` | decimal | 61.75428571428571 |
| `PMP_12` | decimal | 54.094545454545454 |
| `POS_PROD` | inteiro | 2140 |

## TAB_PROD

**Colunas:** 4  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDPRODESTO` | texto | D202102000 |
| `NMPRODUTO_EST` | texto | PAPEL SULFITE BRANCO A4 500FL - PC |
| `TOTAL_PROD` | decimal | 331891.1555999998 |
| `QTDE_PROD` | decimal | 22132 |

## TIPOCONTA

**Colunas:** 4  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `CDCLASSFINANC` | inteiro | 1 |
| `NMCLASSFINANC` | texto | FORNECEDOR |
| `CDTPCTPAGAR` | inteiro | 1 |
| `NMTPCTPAGAR` | texto | ESTOCÁVEIS |

## TODAS - CONTAS A PAGAR

_Amostra indisponível._

## TODAS - DRO SUM

**Colunas:** 21  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `MESANO` | texto | 2024/02 |
| `ANO` | inteiro | 2024 |
| `CDFILIAL` | inteiro | 8888 |
| `NMFILIAL` | texto | 8888 - RC NUTRY ALIMENTACAO LTDA |
| `EMPRESA` | texto | IDEAL |
| `REGIAO` | texto | SP |
| `NEGOCIO` | texto | _MATRIZ |
| `VALOR_REAL` | texto | -5.861.395,22 |
| `FAT_` | texto | 0,00 |
| `CMV_` | texto | 0,00 |
| `MDO_` | texto | -941.670,62 |
| `ADM_` | texto | -645.278,87 |
| `NOP_` | texto | -1.343.748,12 |
| `INV_` | texto | 0,00 |
| `RES_` | texto | -2.930.697,61 |
| `_cmv` | decimal |  |
| `_mdo` | texto |  |
| `_adm` | decimal |  |
| `_nop` | decimal |  |
| `_inv` | decimal |  |
| `_res` | texto |  |

## [RC] COTAÇÃO DE PREÇOS - OLD

**Colunas:** 20  |  **Linhas na amostra:** 5

| Coluna | Tipo inferido | Exemplo |
|---|---|---|
| `SG` | vazio |  |
| `CDFILIAL` | inteiro | 8862 |
| `NMFILIAL` | texto | HOSP. OURO VERDE |
| `NMREGIAO` | texto | REGIONAL - SAO PAULO |
| `NV1` | texto | I - INSUMOS |
| `NV2` | texto | I5 - LIMPEZA |
| `NV3` | texto | I503 - LIQUIDOS |
| `NV4` | texto | I5031 - DOMESTICO |
| `NV5` | texto | I503101 - AGUA SANITARIA |
| `CDPRODUTO` | texto | I503101000 |
| `NMPRODUTO` | texto | AGUA SANITARIA - LT |
| `QTSOLI` | inteiro | 216 |
| `VLRPRECO` | decimal | 2.69917 |
| `TOTALPROD` | decimal | 583.02 |
| `CDFORNECED` | texto | J02184384000337 |
| `RAZAOFORN` | texto | MULTIPACK COMERCIAL EMBALAGENS LTDA |
| `FANTASIAFORN` | texto | MULTIPACK COMERCIAL |
| `MES` | texto | (06) - JUN |
| `ANO` | inteiro | 2026 |
| `MES/ANO` | texto | JUN/2026 |
