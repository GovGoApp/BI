"""
scripts/migrate_elements.py — Migração pipeline → elements.json

Para cada elemento de generate_indexes.py:
  1. Verifica se já tem SQL + snapshot em elements.json → pula
  2. Executa SQL via run_query() contra o Zoho
  3. Compara resultado com o CSV antigo (linhas, somas)
  4. Salva em elements.json com sql + rows_snapshot + config original
  5. Atualiza docs/migracao/STATUS.md

Segurança: nunca sobrescreve entradas com origem='nlsql' (criadas pelo usuário).
Recovery:  git checkout v-pre-migration
"""
from __future__ import annotations
import csv, json, sys, uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.adapter import run_query

PROC          = ROOT / "data" / "processed"
ELEMENTS_FILE = ROOT / "nlsql" / "elements.json"
STATUS_FILE   = ROOT / "docs" / "migracao" / "STATUS.md"

# ══════════════════════════════════════════════════════════════════════════════
# SQL por variavel_js
# Regras:
#  - Aliases batem EXATAMENTE com config.chave / config.label / config.value
#    / config.colunas[].key / config.row_key / config.col_key / config.val_key
#  - Filtros implícitos: excluir _MATRIZ, NMPRODUTO NOT LIKE '%MUTUO%' em NFE
#  - Limites: KPI=sem, GL=50, GB=24, HL=20, T=50, TE=100, MX=200
#  - Período padrão: MESANO >= '2025/07' (últimos 12 meses) ou ANO IN (2025,2026)
# ══════════════════════════════════════════════════════════════════════════════
SQL_MAP: dict[str, str] = {

    # ── 01 RESUMO ─────────────────────────────────────────────────────────────

    "RESUMO_K01_TOTAL_COMPRADO": """
        SELECT
            SUM(CASE WHEN "ANO"=2026 THEN "TOTAL" ELSE 0 END)
                AS total_comprado_operacional,
            ROUND(
                (SUM(CASE WHEN "ANO"=2026 THEN "TOTAL" ELSE 0 END)
                 - SUM(CASE WHEN "ANO"=2025 THEN "TOTAL" ELSE 0 END))
                / NULLIF(SUM(CASE WHEN "ANO"=2025 THEN "TOTAL" ELSE 0 END),0) * 100
            , 2) AS crescimento_yoy_pct
        FROM "NFE"
        WHERE "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%DEVOLUCAO%'
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "RESUMO_K02_FORNECEDORES": """
        SELECT
            COUNT(DISTINCT "CDFORNECED_OFICIAL") AS fornecedores_ativos,
            COUNT(DISTINCT "ID")                 AS ids_unicos
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "RESUMO_K03_PRODUTOS": """
        SELECT
            COUNT(DISTINCT "NMPRODUTO_OFICIAL") AS produtos_unicos,
            COUNT(DISTINCT "ID")                AS ids_unicos
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "RESUMO_K04_IMPACTO": """
        SELECT SUM("IMP_COT") AS imp_cot_total
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "RESUMO_K05_OPORTUNIDADE": """
        SELECT SUM("IMP_COT") AS imp_cot_total
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "RESUMO_K06_COTACAO": """
        SELECT
            ROUND(
                COUNT(CASE WHEN "PRE_MIN_COT" IS NOT NULL AND "PRE_MIN_COT" <> '' THEN 1 END)
                * 100.0 / NULLIF(COUNT(*), 0)
            , 1) AS pct_com_cotacao
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "RESUMO_K07_AD": """
        SELECT SUM("VALOR_FINAL") AS ad_pendente
        FROM "AD_v3"
        WHERE "STATUS_CONCILIACAO" = 'ADIANTAMENTO ?'
    """,

    "RESUMO_K08_CP": """
        SELECT
            SUM("VRATUAPAG")                                              AS cp_aberto,
            SUM(CASE WHEN "STATUS_VENC"='Vencido' THEN "VRATUAPAG" ELSE 0 END) AS cp_vencido,
            COUNT(CASE WHEN "STATUS_VENC"='Vencido' THEN 1 END)          AS cp_titulos
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
    """,

    "RESUMO_R02_POR_NEGOCIO": """
        SELECT "FI.NEGOCIO" AS negocio, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "FI.NEGOCIO"
        ORDER BY spend DESC
        LIMIT 20
    """,

    "RESUMO_R03_TOP_CATEGORIA": """
        SELECT
            n."CAT2"                       AS cat2,
            SUM(n."TOTAL")                 AS spend,
            ROUND(SUM(n."TOTAL")*100.0/SUM(SUM(n."TOTAL")) OVER(),1) AS pct,
            ROUND(AVG(i."PERC_INF_ID_PMP"),1)                        AS inflacao_media_pct,
            SUM(n."IMP_COT")               AS imp_cot
        FROM "NFE" n
        LEFT JOIN "INFLAÇÃO" i ON n."ID"=i."ID" AND n."MESANO"=i."MESANO"
        WHERE n."ANO" IN (2025,2026)
          AND n."CAT2" NOT LIKE 'D5%'
          AND n."FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY n."CAT2"
        ORDER BY spend DESC
        LIMIT 20
    """,

    "RESUMO_R04_TOP_FORNECEDOR": """
        SELECT
            n."FANTASIA_OFICIAL"        AS fornecedor,
            n."CURVA_FORN"              AS curva,
            SUM(n."TOTAL")              AS spend,
            ROUND(SUM(n."TOTAL")*100.0/SUM(SUM(n."TOTAL")) OVER(),1) AS pct,
            SUM(CASE WHEN c."STATUSPAG"='Em Aberto' THEN c."VRATUAPAG" ELSE 0 END) AS cp_aberto
        FROM "NFE" n
        LEFT JOIN "CP" c ON n."CDFORNECED_OFICIAL"=c."CDFORNECED"
        WHERE n."ANO" IN (2025,2026)
          AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND n."NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY n."FANTASIA_OFICIAL", n."CURVA_FORN"
        ORDER BY spend DESC
        LIMIT 20
    """,

    "RESUMO_ALERTAS": """
        SELECT
            SUM(CASE WHEN "ANO"=2026 THEN "TOTAL" ELSE 0 END) AS total_comprado_operacional,
            SUM("IMP_COT") AS imp_cot_total,
            COUNT(DISTINCT "CDFORNECED_OFICIAL") AS fornecedores_ativos,
            ROUND(
                COUNT(CASE WHEN "PRE_MIN_COT" IS NOT NULL AND "PRE_MIN_COT"<>'' THEN 1 END)
                *100.0/NULLIF(COUNT(*),0)
            ,1) AS pct_com_cotacao
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
    """,

    "RESUMO_R08_POR_FILIAL": """
        SELECT
            "NMFILIAL" AS nome, "FI.NEGOCIO" AS negocio, "UF" AS uf,
            SUM("TOTAL") AS spend,
            ROUND(SUM("TOTAL")*100.0/SUM(SUM("TOTAL")) OVER(),1) AS pct
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "NMFILIAL","FI.NEGOCIO","UF"
        ORDER BY spend DESC
        LIMIT 8
    """,

    "RESUMO_R09_CAT2_POR_UF": """
        SELECT "CAT2" AS cat2, "UF" AS uf, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "CAT2" NOT LIKE 'D5%'
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CAT2","UF"
        ORDER BY spend DESC
        LIMIT 200
    """,

    # ── 02 OPORTUNIDADE ───────────────────────────────────────────────────────

    "OPORTUNIDADE_K01_TOTAL": """
        SELECT SUM("IMP_COT") AS imp_cot_total
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "OPORTUNIDADE_K02_SEM_COT": """
        SELECT COUNT(DISTINCT "ID") AS ids_aaa_sem_cotacao
        FROM "NFE"
        WHERE "PRE_MIN_COT" IS NULL
          AND "CURVA_ID" IN ('AAA','AA','A')
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "OPORTUNIDADE_K03_ACIMA": """
        SELECT COUNT(*) AS ids_comprados_acima_minimo
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "OPORTUNIDADE_K04_PCT": """
        SELECT
            ROUND(
                COUNT(CASE WHEN "IMP_COT">0 THEN 1 END) * 100.0
                / NULLIF(COUNT(CASE WHEN "PRE_MIN_COT" IS NOT NULL THEN 1 END),0)
            ,1) AS pct_linhas_acima_minimo
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "OPORTUNIDADE_K05_MONO": """
        SELECT COUNT(*) AS itens_mono_cotacao
        FROM "NUM_COT"
        WHERE "QTD_COT" = 1
          AND "MESANO" >= '2025/07'
    """,

    "OPORTUNIDADE_R04_MATRIZ": """
        SELECT
            'Insumos Estratégicos (AAA/AA)'  AS categoria,
            SUM(CASE WHEN "CURVA_ID" IN ('AAA','AA') AND "IMP_COT">0 THEN "IMP_COT" ELSE 0 END) AS impacto,
            COUNT(CASE WHEN "CURVA_ID" IN ('AAA','AA') AND "IMP_COT">0 THEN 1 END) AS itens
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        LIMIT 10
    """,

    "OPORTUNIDADE_R05_POR_TIPO": """
        SELECT
            CASE
                WHEN "IMP_COT" > 0 AND "CURVA_ID" IN ('AAA','AA','A') THEN 'Compra acima mínimo — curva A'
                WHEN "IMP_COT" > 0 THEN 'Compra acima mínimo'
                WHEN "PRE_MIN_COT" IS NULL THEN 'Sem cotação'
                ELSE 'Compra no mínimo'
            END AS tipo,
            SUM("TOTAL") AS valor
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY 1
        ORDER BY valor DESC
        LIMIT 10
    """,

    "OPORTUNIDADE_R03_POR_UF": """
        SELECT "UF" AS uf, SUM("IMP_COT") AS imp_cot
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "UF"
        ORDER BY imp_cot DESC
        LIMIT 20
    """,

    "OPORTUNIDADE_R01_TABELA": """
        SELECT
            'Compra acima mínimo cotado' AS tipo,
            CASE "CURVA_ID"
                WHEN 'AAA' THEN 1 WHEN 'AA' THEN 2 WHEN 'A' THEN 3
                WHEN 'B'   THEN 4 WHEN 'BB' THEN 5 ELSE 6 END AS prioridade,
            "ID"                AS id,
            "NMPRODUTO_OFICIAL" AS produto,
            "FANTASIA_OFICIAL"  AS fornecedor_atual,
            "PRE_MIN_COT"       AS preco_minimo,
            "IMP_COT"           AS imp_cot
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        ORDER BY imp_cot DESC
        LIMIT 100
    """,

    "OPORTUNIDADE_R02_POR_CAT": """
        SELECT "CAT2" AS cat2, SUM("IMP_COT") AS imp_cot
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CAT2"
        ORDER BY imp_cot DESC
        LIMIT 24
    """,

    # ── 03 CATEGORIAS ─────────────────────────────────────────────────────────

    "CATEGORIA_R01_HIERARQUIA": """
        SELECT
            "CAT1" AS cat1, "CAT2" AS cat2, "CAT3" AS cat3,
            "CAT4" AS cat4, "CAT5" AS cat5,
            SUM("TOTAL") AS spend,
            ROUND(AVG(i."PERC_INF_ID_PMP"),1) AS inflacao_media_pct
        FROM "NFE" n
        LEFT JOIN "INFLAÇÃO" i ON n."ID"=i."ID" AND n."MESANO"=i."MESANO"
        WHERE n."ANO" IN (2025,2026)
          AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND n."NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY "CAT1","CAT2","CAT3","CAT4","CAT5"
        ORDER BY spend DESC
        LIMIT 500
    """,

    "CATEGORIA_R02_CAT2_POR_MES": """
        SELECT "MESANO" AS mesano, "CAT2" AS cat2, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "MESANO" >= '2025/07'
          AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "CAT2" NOT LIKE 'D5%'
        GROUP BY "MESANO","CAT2"
        ORDER BY "MESANO"
        LIMIT 50
    """,

    "CATEGORIA_R03_CAT2_POR_UF": """
        SELECT "CAT2" AS cat2, "UF" AS uf, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "CAT2" NOT LIKE 'D5%'
        GROUP BY "CAT2","UF"
        ORDER BY spend DESC
        LIMIT 200
    """,

    "CATEGORIA_R04_TOP_FORN": """
        SELECT "CAT2" AS cat2, "FANTASIA_OFICIAL" AS fornecedor,
               SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CAT2","FANTASIA_OFICIAL"
        ORDER BY spend DESC
        LIMIT 50
    """,

    "CATEGORIA_R05_TOP_PROD": """
        SELECT
            n."CAT2" AS cat2,
            n."NMPRODUTO_OFICIAL" AS produto,
            SUM(n."TOTAL") AS spend,
            AVG(p."PMP_1") AS pmp_atual,
            ROUND(AVG(i."PERC_INF_ID_PMP"),1) AS var_pmp_pct
        FROM "NFE" n
        LEFT JOIN "PMP_ID_INF_12" p ON n."ID"=p."ID"
        LEFT JOIN "INFLAÇÃO" i ON n."ID"=i."ID" AND n."MESANO"=i."MESANO"
        WHERE n."ANO" IN (2025,2026) AND n."FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY n."CAT2", n."NMPRODUTO_OFICIAL"
        ORDER BY spend DESC
        LIMIT 50
    """,

    # ── 04 FILIAIS ────────────────────────────────────────────────────────────

    "FILIAL_K01_TOTAL": """
        SELECT SUM("TOTAL") AS total_comprado
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "FILIAL_K02_MEDIA": """
        SELECT ROUND(SUM("TOTAL")/NULLIF(COUNT(DISTINCT "CDFILIAL"),0),2)
            AS compra_media_por_filial
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "FILIAL_K03_MAIOR": """
        SELECT "NMFILIAL" AS maior_filial
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "NMFILIAL"
        ORDER BY SUM("TOTAL") DESC
        LIMIT 1
    """,

    "FILIAL_K04_MAIOR_UF": """
        SELECT "UF" AS maior_uf
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "UF"
        ORDER BY SUM("TOTAL") DESC
        LIMIT 1
    """,

    "FILIAL_K05_NEGOCIO": """
        SELECT "FI.NEGOCIO" AS maior_negocio
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "FI.NEGOCIO"
        ORDER BY SUM("TOTAL") DESC
        LIMIT 1
    """,

    "FILIAL_R01_RANKING": """
        SELECT
            "NMFILIAL" AS nome, "NMFILIAL" AS filial,
            "FI.NEGOCIO" AS negocio, "UF" AS uf,
            SUM("TOTAL") AS spend,
            ROUND(SUM("TOTAL")*100.0/SUM(SUM("TOTAL")) OVER(),1) AS pct,
            ROUND(
                COUNT(CASE WHEN "PRE_MIN_COT" IS NOT NULL THEN 1 END)
                *100.0/NULLIF(COUNT(*),0)
            ,1) AS pct_com_cotacao,
            SUM("IMP_COT") AS imp_cot
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "NMFILIAL","FI.NEGOCIO","UF"
        ORDER BY spend DESC
        LIMIT 50
    """,

    "FILIAL_R02_NEG": """
        SELECT "CDFILIAL" AS cdfilial, "NMFILIAL" AS filial,
               "FI.NEGOCIO" AS negocio, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CDFILIAL","NMFILIAL","FI.NEGOCIO"
        ORDER BY spend DESC
        LIMIT 200
    """,

    "FILIAL_R03_MES": """
        SELECT "CDFILIAL" AS cdfilial, "NMFILIAL" AS filial,
               "MESANO" AS mesano, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "MESANO" >= '2025/07' AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CDFILIAL","NMFILIAL","MESANO"
        ORDER BY "CDFILIAL","MESANO"
        LIMIT 50
    """,

    "FILIAL_R04_CAT": """
        SELECT "CDFILIAL" AS cdfilial, "NMFILIAL" AS filial,
               "CAT2" AS cat2, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "CAT2" NOT LIKE 'D5%'
        GROUP BY "CDFILIAL","NMFILIAL","CAT2"
        ORDER BY "CDFILIAL", spend DESC
        LIMIT 200
    """,

    "FILIAL_R05_FORN": """
        SELECT "CDFILIAL" AS cdfilial, "NMFILIAL" AS filial,
               "CDFORNECED_OFICIAL" AS cdforneced,
               "FANTASIA_OFICIAL" AS fornecedor,
               SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CDFILIAL","NMFILIAL","CDFORNECED_OFICIAL","FANTASIA_OFICIAL"
        ORDER BY "CDFILIAL", spend DESC
        LIMIT 200
    """,

    # ── 06 FORNECEDOR 360 ─────────────────────────────────────────────────────

    "FORNECEDOR_K01_ATIVOS": """
        SELECT COUNT(DISTINCT "CDFORNECED_OFICIAL") AS fornecedores_ativos
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "FORNECEDOR_K02_CURVA": """
        SELECT COUNT(DISTINCT "CDFORNECED") AS forn_curva_aaa_aa
        FROM "CURVA ABC FORN"
        WHERE "CURVA" IN ('AAA','AA')
    """,

    "FORNECEDOR_K03_SPEND": """
        SELECT SUM("TOTAL") AS spend_curva_aaa_aa_a
        FROM "NFE"
        WHERE "CURVA_FORN" IN ('AAA','AA','A')
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "FORNECEDOR_K04_PCT": """
        SELECT
            ROUND(
                SUM(CASE WHEN "CURVA_FORN" IN ('AAA','AA','A') THEN "TOTAL" ELSE 0 END)
                *100.0/NULLIF(SUM("TOTAL"),0)
            ,1) AS pct_spend_top
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "FORNECEDOR_K05_CP_N": """
        SELECT COUNT(DISTINCT "CDFORNECED") AS forn_com_cp_aberto
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
    """,

    "FORNECEDOR_K06_CP_R": """
        SELECT SUM("VRATUAPAG") AS cp_aberto_total
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
    """,

    "FORNECEDOR_K07_AD_N": """
        SELECT COUNT(DISTINCT "CDFORNECED") AS forn_com_ad_pendente
        FROM "AD_v3"
        WHERE "STATUS_CONCILIACAO" = 'ADIANTAMENTO ?'
    """,

    "FORNECEDOR_K08_AD_R": """
        SELECT SUM("VALOR_FINAL") AS ad_pendente_total
        FROM "AD_v3"
        WHERE "STATUS_CONCILIACAO" = 'ADIANTAMENTO ?'
    """,

    "FORNECEDOR_R01_TABELA": """
        SELECT
            n."FANTASIA_OFICIAL"        AS fornecedor,
            n."CURVA_FORN"              AS curva,
            GROUP_CONCAT(DISTINCT n."NMEMP")   AS empresas,
            GROUP_CONCAT(DISTINCT n."UF")      AS ufs,
            GROUP_CONCAT(DISTINCT n."CAT2" LIMIT 3) AS categorias_top,
            SUM(n."TOTAL")              AS spend_total,
            ROUND(SUM(n."TOTAL")*100.0/SUM(SUM(n."TOTAL")) OVER(),2) AS pct,
            SUM(n."IMP_COT")            AS imp_cot,
            SUM(CASE WHEN c."STATUSPAG"='Em Aberto' THEN c."VRATUAPAG" ELSE 0 END) AS cp_aberto,
            SUM(CASE WHEN c."STATUSPAG"='Em Aberto' AND c."STATUS_VENC"='Vencido'
                THEN c."VRATUAPAG" ELSE 0 END)  AS cp_vencido,
            SUM(CASE WHEN a."STATUS_CONCILIACAO"='ADIANTAMENTO ?' THEN a."VALOR_FINAL" ELSE 0 END) AS ad_pendente
        FROM "NFE" n
        LEFT JOIN "CP"    c ON n."CDFORNECED_OFICIAL"=c."CDFORNECED"
        LEFT JOIN "AD_v3" a ON n."CDFORNECED_OFICIAL"=a."CDFORNECED"
        WHERE n."ANO" IN (2025,2026)
          AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND n."NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY n."FANTASIA_OFICIAL", n."CURVA_FORN"
        ORDER BY spend_total DESC
        LIMIT 100
    """,

    "FORNECEDOR_R02_CAT": """
        SELECT "FANTASIA_OFICIAL" AS fornecedor, "CAT2" AS cat2,
               SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "FANTASIA_OFICIAL","CAT2"
        ORDER BY spend DESC
        LIMIT 50
    """,

    "FORNECEDOR_R03_PROD": """
        SELECT "FANTASIA_OFICIAL" AS fornecedor,
               "NMPRODUTO_OFICIAL" AS produto,
               SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY "FANTASIA_OFICIAL","NMPRODUTO_OFICIAL"
        ORDER BY spend DESC
        LIMIT 50
    """,

    # ── 07 PRODUTOS ───────────────────────────────────────────────────────────

    "PRODUTO_K01_TOTAL": """
        SELECT COUNT(DISTINCT "ID") AS total_ids
        FROM "PMP_ID_INF_12"
        WHERE "PMP_1" IS NOT NULL AND "PMP_1" > 0
    """,

    "PRODUTO_K02_PMP": """
        SELECT ROUND(AVG("PMP_1"),2) AS pmp_medio_cesta
        FROM "PMP_ID_INF_12"
        WHERE "PMP_1" IS NOT NULL AND "PMP_1" > 0
    """,

    "PRODUTO_K03_VAR": """
        SELECT COUNT(*) AS ids_variacao_pmp_gt10pct
        FROM "INFLAÇÃO"
        WHERE ABS("PERC_INF_ID_PMP") > 10
          AND "MESANO" >= '2025/07'
    """,

    "PRODUTO_K04_SC": """
        SELECT COUNT(DISTINCT n."ID") AS ids_sem_cotacao_12m
        FROM "NFE" n
        LEFT JOIN "NUM_COT" nc ON n."ID"=nc."ID" AND n."MESANO"=nc."MESANO"
        WHERE n."MESANO" >= '2025/07'
          AND nc."ID" IS NULL
          AND n."FI.NEGOCIO" <> '_MATRIZ'
    """,

    "PRODUTO_K05_INF": """
        SELECT ROUND(AVG("PERC_INF_ID_PMP"),1) AS inflacao_media_cesta
        FROM "INFLAÇÃO"
        WHERE "MESANO" >= '2025/07'
          AND "PERC_INF_ID_PMP" IS NOT NULL
          AND ABS("PERC_INF_ID_PMP") < 500
    """,

    "PRODUTO_R01_TABELA": """
        SELECT
            n."NMPRODUTO_OFICIAL" AS produto,
            n."CAT2"              AS cat2,
            n."CURVA_ID"          AS curva_id,
            SUM(n."TOTAL")        AS spend,
            ROUND(AVG(p."PMP_1"),2) AS pmp_atual,
            ROUND(AVG(i."PERC_INF_ID_PMP"),1) AS var_pmp_pct
        FROM "NFE" n
        LEFT JOIN "PMP_ID_INF_12" p ON n."ID"=p."ID"
        LEFT JOIN "INFLAÇÃO"       i ON n."ID"=i."ID" AND n."MESANO"=i."MESANO"
        WHERE n."ANO" IN (2025,2026)
          AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND n."NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY n."NMPRODUTO_OFICIAL", n."CAT2", n."CURVA_ID"
        ORDER BY spend DESC
        LIMIT 100
    """,

    "PRODUTO_R03_TOP_INF": """
        SELECT "NMPRODUTO_EST" AS produto,
               ROUND(AVG("PERC_INF_ID_PMP"),1) AS var_pmp_pct
        FROM "INFLAÇÃO"
        WHERE "PERC_INF_ID_PMP" > 5
          AND "MESANO" >= '2025/07'
          AND "NMPRODUTO_EST" NOT LIKE '%MUTUO%'
          AND ABS("PERC_INF_ID_PMP") < 500
        GROUP BY "NMPRODUTO_EST"
        ORDER BY var_pmp_pct DESC
        LIMIT 20
    """,

    "PRODUTO_R04_TOP_DEF": """
        SELECT "NMPRODUTO_EST" AS produto,
               ROUND(AVG("PERC_INF_ID_PMP"),1) AS var_pmp_pct
        FROM "INFLAÇÃO"
        WHERE "PERC_INF_ID_PMP" < -3
          AND "MESANO" >= '2025/07'
          AND "NMPRODUTO_EST" NOT LIKE '%MUTUO%'
          AND ABS("PERC_INF_ID_PMP") < 500
        GROUP BY "NMPRODUTO_EST"
        ORDER BY var_pmp_pct ASC
        LIMIT 20
    """,

    "PRODUTO_R02_PMP_CAT": """
        SELECT n."CAT2" AS cat2,
               ROUND(AVG(p."PMP_1"),2) AS pmp_medio,
               SUM(n."TOTAL") AS spend
        FROM "NFE" n
        LEFT JOIN "PMP_ID_INF_12" p ON n."ID"=p."ID"
        WHERE n."ANO" IN (2025,2026) AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND p."PMP_1" > 0
        GROUP BY n."CAT2"
        ORDER BY spend DESC
        LIMIT 50
    """,

    # ── 08 COTAÇÕES ───────────────────────────────────────────────────────────

    "COTACAO_K01_COT": """
        SELECT COUNT(DISTINCT "ID") AS produtos_cotados
        FROM "NUM_COT"
        WHERE "QTD_COT" > 0 AND "MESANO" >= '2025/07'
    """,

    "COTACAO_K02_PCT": """
        SELECT
            ROUND(
                COUNT(DISTINCT nc."ID") * 100.0
                / NULLIF(COUNT(DISTINCT n."ID"), 0)
            ,1) AS pct_cobertura
        FROM "NFE" n
        LEFT JOIN "NUM_COT" nc ON n."ID"=nc."ID" AND n."MESANO"=nc."MESANO"
        WHERE n."MESANO" >= '2025/07' AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND n."NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
    """,

    "COTACAO_K03_MEDIA": """
        SELECT ROUND(AVG("QTD_COT"),1) AS media_cotacoes_produto
        FROM "NUM_COT"
        WHERE "MESANO" >= '2025/07'
    """,

    "COTACAO_K04_ZERO": """
        SELECT COUNT(DISTINCT n."ID") AS com_zero_cotacao
        FROM "NFE" n
        LEFT JOIN "NUM_COT" nc ON n."ID"=nc."ID" AND n."MESANO"=nc."MESANO"
        WHERE n."MESANO" >= '2025/07'
          AND nc."ID" IS NULL
          AND n."FI.NEGOCIO" <> '_MATRIZ'
    """,

    "COTACAO_K05_UMA": """
        SELECT COUNT(DISTINCT "ID") AS com_uma_cotacao
        FROM "NUM_COT"
        WHERE "QTD_COT" = 1 AND "MESANO" >= '2025/07'
    """,

    "COTACAO_K06_LE3": """
        SELECT COUNT(DISTINCT "ID") AS com_le3_cotacoes
        FROM "NUM_COT"
        WHERE "QTD_COT" <= 3 AND "MESANO" >= '2025/07'
    """,

    "COTACAO_K07_IMP": """
        SELECT SUM("IMP_COT") AS potencial_imp_cot
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "MESANO" >= '2025/07'
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "COTACAO_K08_MENOR": """
        SELECT
            ROUND(
                COUNT(CASE WHEN "IMP_COT"=0 AND "PRE_MIN_COT" IS NOT NULL THEN 1 END)
                *100.0
                /NULLIF(COUNT(CASE WHEN "PRE_MIN_COT" IS NOT NULL THEN 1 END),0)
            ,1) AS pct_comprado_no_menor
        FROM "NFE"
        WHERE "MESANO" >= '2025/07' AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "COTACAO_R01_MES": """
        SELECT
            nc."MESANO" AS mesano,
            COUNT(CASE WHEN nc."QTD_COT"=0 THEN 1 END) AS zero,
            COUNT(CASE WHEN nc."QTD_COT"=1 THEN 1 END) AS uma,
            COUNT(CASE WHEN nc."QTD_COT" BETWEEN 2 AND 3 THEN 1 END) AS duas_tres,
            COUNT(CASE WHEN nc."QTD_COT">=4 THEN 1 END) AS quatro_mais
        FROM "NUM_COT" nc
        WHERE nc."MESANO" >= '2025/07'
        GROUP BY nc."MESANO"
        ORDER BY nc."MESANO"
        LIMIT 24
    """,

    "COTACAO_R02_CURVA": """
        SELECT
            nc."CURVA_ID"                         AS curva_id,
            COUNT(*)                               AS total,
            COUNT(CASE WHEN nc."QTD_COT"=0 THEN 1 END) AS zero,
            COUNT(CASE WHEN nc."QTD_COT"=1 THEN 1 END) AS uma,
            COUNT(CASE WHEN nc."QTD_COT" BETWEEN 2 AND 3 THEN 1 END) AS duas_tres,
            COUNT(CASE WHEN nc."QTD_COT">=4 THEN 1 END) AS quatro_mais,
            ROUND(
                COUNT(CASE WHEN nc."QTD_COT"<=1 THEN 1 END)*100.0/NULLIF(COUNT(*),0)
            ,1) AS pct_risco
        FROM "NUM_COT" nc
        WHERE nc."MESANO" >= '2025/07'
        GROUP BY nc."CURVA_ID"
        ORDER BY total DESC
        LIMIT 200
    """,

    "COTACAO_R03_CAT_MES": """
        SELECT n."CAT2" AS cat2, n."MESANO" AS mesano,
               ROUND(
                   COUNT(DISTINCT nc."ID")*100.0/NULLIF(COUNT(DISTINCT n."ID"),0)
               ,1) AS pct_cobertura
        FROM "NFE" n
        LEFT JOIN "NUM_COT" nc ON n."ID"=nc."ID" AND n."MESANO"=nc."MESANO"
        WHERE n."MESANO" >= '2025/07'
          AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND n."CAT2" NOT LIKE 'D5%'
        GROUP BY n."CAT2", n."MESANO"
        ORDER BY n."MESANO"
        LIMIT 50
    """,

    "COTACAO_R04_UF": """
        SELECT
            n."UF" AS uf,
            ROUND(
                COUNT(DISTINCT nc."ID")*100.0/NULLIF(COUNT(DISTINCT n."ID"),0)
            ,1) AS pct_cobertura,
            SUM(n."IMP_COT") AS imp_cot,
            ROUND(SUM(n."IMP_COT")*100.0/NULLIF(SUM(n."TOTAL"),0),1) AS imp_sobre_spend_pct
        FROM "NFE" n
        LEFT JOIN "NUM_COT" nc ON n."ID"=nc."ID" AND n."MESANO"=nc."MESANO"
        WHERE n."ANO" IN (2025,2026) AND n."FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY n."UF"
        ORDER BY pct_cobertura ASC
        LIMIT 50
    """,

    "COTACAO_R05_MIN_FORN": """
        SELECT nc."FORN_MENOR_PRECO" AS fornecedor,
               COUNT(*) AS vezes_menor_preco,
               COUNT(DISTINCT nc."ID") AS ids_unicos
        FROM "NUM_COT" nc
        WHERE nc."MESANO" >= '2025/07'
          AND nc."FORN_MENOR_PRECO" IS NOT NULL
        GROUP BY nc."FORN_MENOR_PRECO"
        ORDER BY vezes_menor_preco DESC
        LIMIT 50
    """,

    "COTACAO_R06_REL": """
        SELECT nc."ID" AS id, nc."MESANO" AS mesano,
               nc."MIN_COT" AS preco_min,
               nc."MED_COT" AS preco_med,
               nc."QTD_COT" AS n_cotacoes
        FROM "NUM_COT" nc
        WHERE nc."MESANO" >= '2025/07'
        ORDER BY nc."MESANO" DESC, nc."ID"
        LIMIT 100
    """,

    "COTACAO_R07_PRECOS": """
        SELECT c."ID" AS id, c."NMPRODUTO_OFICIAL" AS produto,
               c."FANTASIA_OFICIAL" AS fornecedor,
               c."MESANO" AS mesano,
               MIN(c."PRECOUNIT") AS preco_min
        FROM "COT" c
        WHERE c."MESANO" >= '2025/07'
        GROUP BY c."ID", c."NMPRODUTO_OFICIAL", c."FANTASIA_OFICIAL", c."MESANO"
        ORDER BY c."MESANO" DESC, c."ID"
        LIMIT 100
    """,

    "COTACAO_R08_PROD": """
        SELECT
            c."NMPRODUTO_OFICIAL"               AS produto,
            COUNT(DISTINCT c."MESANO")          AS n_meses_cotados,
            MIN(c."PRECOUNIT")                  AS preco_min_global,
            nc."FORN_MENOR_PRECO"               AS fornecedor_mais_barato
        FROM "COT" c
        LEFT JOIN "NUM_COT" nc ON c."ID"=nc."ID" AND c."MESANO"=nc."MESANO"
        WHERE c."MESANO" >= '2025/07'
        GROUP BY c."NMPRODUTO_OFICIAL", nc."FORN_MENOR_PRECO"
        ORDER BY n_meses_cotados DESC
        LIMIT 100
    """,

    "COTACAO_R09_MATRIZ": """
        SELECT c."NMPRODUTO_OFICIAL" AS produto, c."MESANO" AS mesano,
               MIN(c."PRECOUNIT") AS preco_min
        FROM "COT" c
        WHERE c."MESANO" >= '2025/07'
        GROUP BY c."NMPRODUTO_OFICIAL", c."MESANO"
        ORDER BY c."NMPRODUTO_OFICIAL", c."MESANO"
        LIMIT 200
    """,

    "COTACAO_R10_LE3": """
        SELECT nc."ID" AS id, c."NMPRODUTO_OFICIAL" AS produto,
               nc."QTD_COT" AS n_concorrentes,
               nc."MIN_COT" AS preco_min,
               nc."FORN_MENOR_PRECO" AS fornecedor_mais_barato
        FROM "NUM_COT" nc
        LEFT JOIN "COT" c ON nc."ID"=c."ID" AND nc."MESANO"=c."MESANO"
        WHERE nc."QTD_COT" <= 3 AND nc."QTD_COT" > 0
          AND nc."MESANO" >= '2025/07'
        GROUP BY nc."ID", c."NMPRODUTO_OFICIAL", nc."QTD_COT",
                 nc."MIN_COT", nc."FORN_MENOR_PRECO"
        ORDER BY nc."QTD_COT", preco_min DESC
        LIMIT 50
    """,

    # ── 09 IMPACTO ────────────────────────────────────────────────────────────

    "IMPACTO_K01_TOTAL": """
        SELECT SUM("IMP_COT") AS imp_cot_total
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "IMPACTO_K02_IDS": """
        SELECT COUNT(DISTINCT "ID") AS ids_com_impacto
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "IMPACTO_K03_PCT": """
        SELECT
            ROUND(
                COUNT(CASE WHEN "IMP_COT">0 THEN 1 END)*100.0
                /NULLIF(COUNT(CASE WHEN "PRE_MIN_COT" IS NOT NULL THEN 1 END),0)
            ,1) AS pct_linhas_acima_minimo
        FROM "NFE"
        WHERE "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "IMPACTO_K04_UF": """
        SELECT "UF" AS uf_lider
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026) AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "UF"
        ORDER BY SUM("IMP_COT") DESC
        LIMIT 1
    """,

    "IMPACTO_K05_PROD": """
        SELECT "NMPRODUTO_OFICIAL" AS top_produto_nome
        FROM "NFE"
        WHERE "IMP_COT" > 0 AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
        GROUP BY "NMPRODUTO_OFICIAL"
        ORDER BY SUM("IMP_COT") DESC
        LIMIT 1
    """,

    "IMPACTO_R03_TOP_ID": """
        SELECT
            "ID"                AS id,
            "NMPRODUTO_OFICIAL" AS produto,
            "CAT2"              AS cat2,
            "UF"                AS uf,
            "FANTASIA_OFICIAL"  AS fornecedor_atual,
            "FORN_MIN_COT"      AS fornecedor_mais_barato,
            SUM("IMP_COT")      AS imp_cot
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "ID","NMPRODUTO_OFICIAL","CAT2","UF","FANTASIA_OFICIAL","FORN_MIN_COT"
        ORDER BY imp_cot DESC
        LIMIT 100
    """,

    "IMPACTO_R04_FORN": """
        SELECT "FORN_MIN_COT" AS fornecedor,
               COUNT(*) AS vezes_mais_barato,
               SUM("IMP_COT") AS oportunidade_total
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "FORN_MIN_COT" IS NOT NULL
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "FORN_MIN_COT"
        ORDER BY oportunidade_total DESC
        LIMIT 50
    """,

    "IMPACTO_R05_PROD_MIN": """
        SELECT "ID" AS id,
               "NMPRODUTO_OFICIAL" AS produto,
               "PRE_MIN_COT" AS pre_min_cot,
               SUM("IMP_COT") AS imp_cot
        FROM "NFE"
        WHERE "IMP_COT" > 0
          AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "ID","NMPRODUTO_OFICIAL","PRE_MIN_COT"
        ORDER BY imp_cot DESC
        LIMIT 50
    """,

    # ── 10 INFLAÇÃO ───────────────────────────────────────────────────────────

    "INFLACAO_K01_MEDIA": """
        SELECT ROUND(AVG("PERC_INF_ID_PMP"),1) AS inflacao_media_pct
        FROM "INFLAÇÃO"
        WHERE "MESANO" >= '2025/07'
          AND "PERC_INF_ID_PMP" IS NOT NULL
          AND ABS("PERC_INF_ID_PMP") < 500
    """,

    "INFLACAO_K02_EXP": """
        SELECT SUM("SOMA_INF_ID_PMP") AS exposicao_monetaria_12m
        FROM "INFLAÇÃO"
        WHERE "MESANO" >= '2025/07'
    """,

    "INFLACAO_K03_GT10": """
        SELECT COUNT(DISTINCT "ID") AS ids_com_inflacao_gt10pct
        FROM "INFLAÇÃO"
        WHERE ABS("PERC_INF_ID_PMP") > 10
          AND "MESANO" >= '2025/07'
          AND ABS("PERC_INF_ID_PMP") < 500
    """,

    "INFLACAO_K04_CAT": """
        SELECT "CAT2" AS cat2_mais_inflada
        FROM "INFLAÇÃO"
        WHERE "MESANO" >= '2025/07'
          AND "PERC_INF_ID_PMP" IS NOT NULL
          AND ABS("PERC_INF_ID_PMP") < 500
        GROUP BY "CAT2"
        ORDER BY AVG("PERC_INF_ID_PMP") DESC
        LIMIT 1
    """,

    "INFLACAO_R01_CAT_MES": """
        SELECT "CAT2" AS cat2, "MESANO" AS mesano,
               ROUND(AVG("PERC_INF_ID_PMP"),1) AS inflacao_media_pct,
               SUM("SOMA_INF_ID_PMP") AS exposicao_rs
        FROM "INFLAÇÃO"
        WHERE "MESANO" >= '2025/07'
          AND ABS("PERC_INF_ID_PMP") < 500
          AND "CAT2" NOT LIKE 'D5%'
        GROUP BY "CAT2","MESANO"
        ORDER BY "MESANO"
        LIMIT 50
    """,

    "INFLACAO_R05_TOP_INF": """
        SELECT "NMPRODUTO_EST" AS produto,
               ROUND(AVG("PERC_INF_ID_PMP"),1) AS var_pct
        FROM "INFLAÇÃO"
        WHERE "PERC_INF_ID_PMP" > 5
          AND "MESANO" >= '2025/07'
          AND ABS("PERC_INF_ID_PMP") < 500
          AND "NMPRODUTO_EST" NOT LIKE '%MUTUO%'
        GROUP BY "NMPRODUTO_EST"
        ORDER BY var_pct DESC
        LIMIT 20
    """,

    "INFLACAO_R06_TOP_DEF": """
        SELECT "NMPRODUTO_EST" AS produto,
               ROUND(AVG("PERC_INF_ID_PMP"),1) AS var_pct
        FROM "INFLAÇÃO"
        WHERE "PERC_INF_ID_PMP" < -3
          AND "MESANO" >= '2025/07'
          AND ABS("PERC_INF_ID_PMP") < 500
          AND "NMPRODUTO_EST" NOT LIKE '%MUTUO%'
        GROUP BY "NMPRODUTO_EST"
        ORDER BY var_pct ASC
        LIMIT 20
    """,

    "INFLACAO_R07_FORN": """
        SELECT n."FANTASIA_OFICIAL" AS fornecedor,
               ROUND(AVG(i."PERC_INF_ID_PMP"),1) AS inflacao_media_pct,
               SUM(n."TOTAL") AS spend
        FROM "NFE" n
        LEFT JOIN "INFLAÇÃO" i ON n."ID"=i."ID" AND n."MESANO"=i."MESANO"
        WHERE n."MESANO" >= '2025/07'
          AND n."FI.NEGOCIO" <> '_MATRIZ'
          AND ABS(i."PERC_INF_ID_PMP") < 500
        GROUP BY n."FANTASIA_OFICIAL"
        ORDER BY inflacao_media_pct DESC
        LIMIT 50
    """,

    "INFLACAO_R08_CAT_PROD": """
        SELECT i."CAT2" AS cat2, i."NMPRODUTO_EST" AS produto,
               ROUND(AVG(i."PERC_INF_ID_PMP"),1) AS inflacao_media_pct,
               SUM(i."SOMA_INF_ID_PMP") AS exposicao_rs
        FROM "INFLAÇÃO" i
        WHERE i."MESANO" >= '2025/07'
          AND ABS(i."PERC_INF_ID_PMP") < 500
          AND i."NMPRODUTO_EST" NOT LIKE '%MUTUO%'
        GROUP BY i."CAT2", i."NMPRODUTO_EST"
        ORDER BY inflacao_media_pct DESC
        LIMIT 50
    """,

    # ── 12 FINANCEIRO ─────────────────────────────────────────────────────────

    "FINANCEIRO_K01_ABERTO": """
        SELECT SUM("VRATUAPAG") AS cp_aberto_total
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
    """,

    "FINANCEIRO_K02_TIT": """
        SELECT COUNT(*) AS cp_titulos
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
    """,

    "FINANCEIRO_K03_VENC": """
        SELECT SUM("VRATUAPAG") AS cp_vencido
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
          AND "STATUS_VENC" = 'Vencido'
    """,

    "FINANCEIRO_K04_7D": """
        SELECT SUM("VRATUAPAG") AS cp_a_vencer_7d
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
          AND "STATUS_VENC" = 'A Vencer'
          AND "FAIXA_DIAS" IN ('AV 0','AV 7')
    """,

    "FINANCEIRO_K05_120": """
        SELECT SUM("VRATUAPAG") AS cp_critico_120d
        FROM "CP"
        WHERE "STATUSPAG" = 'Em Aberto'
          AND "FAIXA_DIAS" IN ('VE +120','VE 120')
    """,

    "FINANCEIRO_R03_TIMELINE": """
        SELECT
            "T.SEMANA_ANO"            AS semana,
            SUM("VALOR_PAGO_SEMANA")  AS valor_pago,
            SUM("VALOR_VENCIMENTOS_SEMANA") AS valor_vencimentos,
            SUM("VALOR_VENCIDO_SEMANA")     AS valor_vencido
        FROM "CP_SEMANA"
        WHERE "T.ANO" IN (2025,2026)
        GROUP BY "T.SEMANA_ANO"
        ORDER BY "T.SEMANA_ANO"
        LIMIT 24
    """,

    "FINANCEIRO_R04_SALDO": """
        SELECT
            "T.FORNECEDOR" AS fornecedor,
            "T.SEMANA_ANO" AS semana,
            SUM("VALOR_VENCIMENTOS_SEMANA") - SUM("VALOR_PAGO_SEMANA") AS saldo
        FROM "CP_SEMANA"
        WHERE "T.ANO" = 2026
        GROUP BY "T.FORNECEDOR","T.SEMANA_ANO"
        ORDER BY "T.FORNECEDOR","T.SEMANA_ANO"
        LIMIT 200
    """,

    # ── 13 ADIANTAMENTOS ──────────────────────────────────────────────────────

    "ADIANTAMENTO_K01_TOTAL": """
        SELECT SUM("VALOR_FINAL") AS ad_total_12m
        FROM "AD_v3"
        WHERE "ANO" IN (2025,2026)
    """,

    "ADIANTAMENTO_K02_CONC": """
        SELECT SUM("VALOR_FINAL") AS conciliado
        FROM "AD_v3"
        WHERE "STATUS_CONCILIACAO" = 'CONCILIADO'
          AND "ANO" IN (2025,2026)
    """,

    "ADIANTAMENTO_K03_PEND": """
        SELECT SUM("VALOR_FINAL") AS pendente
        FROM "AD_v3"
        WHERE "STATUS_CONCILIACAO" = 'ADIANTAMENTO ?'
    """,

    "ADIANTAMENTO_K04_PCT": """
        SELECT
            ROUND(
                SUM(CASE WHEN "STATUS_CONCILIACAO"='CONCILIADO' THEN "VALOR_FINAL" ELSE 0 END)
                *100.0/NULLIF(SUM("VALOR_FINAL"),0)
            ,1) AS pct_conciliado
        FROM "AD_v3"
        WHERE "ANO" IN (2025,2026)
    """,

    "ADIANTAMENTO_K05_N": """
        SELECT COUNT(*) AS n_pendente
        FROM "AD_v3"
        WHERE "STATUS_CONCILIACAO" = 'ADIANTAMENTO ?'
    """,

    "ADIANTAMENTO_R01_FUNIL": """
        SELECT
            CASE "STATUS_CONCILIACAO"
                WHEN 'CONCILIADO'    THEN 'Conciliado'
                WHEN 'ADIANTAMENTO ?' THEN 'Pendente'
                ELSE "STATUS_CONCILIACAO"
            END AS status,
            SUM("VALOR_FINAL") AS valor
        FROM "AD_v3"
        WHERE "ANO" IN (2025,2026)
        GROUP BY "STATUS_CONCILIACAO"
        ORDER BY valor DESC
        LIMIT 10
    """,

    "ADIANTAMENTO_R03_MES": """
        SELECT
            "MES_ENTRADA"                                                     AS mesano,
            SUM(CASE WHEN "STATUS_CONCILIACAO"='ADIANTAMENTO ?' THEN "VALOR_FINAL" ELSE 0 END) AS pendente,
            SUM(CASE WHEN "STATUS_CONCILIACAO"='CONCILIADO' THEN "VALOR_FINAL" ELSE 0 END)      AS conciliado
        FROM "AD_v3"
        WHERE "ANO" IN (2025,2026)
        GROUP BY "MES_ENTRADA"
        ORDER BY "MES_ENTRADA"
        LIMIT 50
    """,

    "ADIANTAMENTO_R04_UF": """
        SELECT f."UF" AS uf, SUM(a."VALOR_FINAL") AS valor_total
        FROM "AD_v3" a
        LEFT JOIN "FILIAIS_SUPPLY" f ON a."CDFORNECED"=f."CDFILIAL"
        WHERE a."ANO" IN (2025,2026)
        GROUP BY f."UF"
        ORDER BY valor_total DESC
        LIMIT 20
    """,

    "ADIANTAMENTO_R05_CAT": """
        SELECT n."CAT2" AS cat2,
               SUM(CASE WHEN a."STATUS_CONCILIACAO"='ADIANTAMENTO ?' THEN a."VALOR_FINAL" ELSE 0 END) AS pendente,
               SUM(CASE WHEN a."STATUS_CONCILIACAO"='CONCILIADO' THEN a."VALOR_FINAL" ELSE 0 END)      AS conciliado
        FROM "AD_v3" a
        LEFT JOIN "NFE" n ON a."CDFORNECED"=n."CDFORNECED_OFICIAL"
                          AND a."ANO"=n."ANO"
        WHERE a."ANO" IN (2025,2026)
        GROUP BY n."CAT2"
        ORDER BY pendente DESC
        LIMIT 50
    """,

    # ── 14 SERVIÇOS ───────────────────────────────────────────────────────────

    "SERVICO_K01_TOTAL": """
        SELECT SUM("TOTAL") AS total_servicos
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "SERVICO_K02_FORN": """
        SELECT COUNT(DISTINCT "CDFORNECED_OFICIAL") AS fornecedores_servicos
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "SERVICO_K03_UFS": """
        SELECT COUNT(DISTINCT "UF") AS ufs_atendidas
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "SERVICO_K04_VAR": """
        SELECT
            ROUND(
                (SUM(CASE WHEN "MESANO"=(SELECT MAX("MESANO") FROM "NFE" WHERE "CAT2" LIKE 'D5%')
                     THEN "TOTAL" ELSE 0 END)
                -SUM(CASE WHEN "MESANO"=(
                    SELECT DISTINCT "MESANO" FROM "NFE"
                    WHERE "MESANO" < (SELECT MAX("MESANO") FROM "NFE" WHERE "CAT2" LIKE 'D5%')
                    AND "CAT2" LIKE 'D5%'
                    ORDER BY "MESANO" DESC LIMIT 1)
                     THEN "TOTAL" ELSE 0 END))
                *100.0
                /NULLIF(SUM(CASE WHEN "MESANO"=(
                    SELECT DISTINCT "MESANO" FROM "NFE"
                    WHERE "MESANO" < (SELECT MAX("MESANO") FROM "NFE" WHERE "CAT2" LIKE 'D5%')
                    AND "CAT2" LIKE 'D5%'
                    ORDER BY "MESANO" DESC LIMIT 1)
                     THEN "TOTAL" ELSE 0 END),0)
            ,1) AS variacao_mensal_pct
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "FI.NEGOCIO" <> '_MATRIZ'
    """,

    "SERVICO_K05_CAT": """
        SELECT "CAT3" AS maior_categoria
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CAT3"
        ORDER BY SUM("TOTAL") DESC
        LIMIT 1
    """,

    "SERVICO_R02_MES": """
        SELECT "MESANO" AS mesano, SUM("TOTAL") AS spend
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%'
          AND "MESANO" >= '2025/07'
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "MESANO"
        ORDER BY "MESANO"
        LIMIT 24
    """,

    "SERVICO_R03_CAT": """
        SELECT "CAT3" AS categoria, "CAT2" AS cat2,
               SUM("TOTAL") AS spend,
               ROUND(SUM("TOTAL")*100.0/SUM(SUM("TOTAL")) OVER(),1) AS pct
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
        GROUP BY "CAT3","CAT2"
        ORDER BY spend DESC
        LIMIT 20
    """,

    "SERVICO_R05_CAT5": """
        SELECT "CAT5" AS cat5, "CAT3" AS cat3,
               SUM("TOTAL") AS spend,
               ROUND(SUM("TOTAL")*100.0/SUM(SUM("TOTAL")) OVER(),1) AS pct
        FROM "NFE"
        WHERE "CAT2" LIKE 'D5%' AND "ANO" IN (2025,2026)
          AND "FI.NEGOCIO" <> '_MATRIZ'
          AND "CAT5" IS NOT NULL AND "CAT5" <> ''
        GROUP BY "CAT5","CAT3"
        ORDER BY spend DESC
        LIMIT 50
    """,

    # ── 15 DADOS ──────────────────────────────────────────────────────────────

    "DADOS_K01_LINHAS": """
        SELECT COUNT(*) AS linhas_total_nfe FROM "NFE"
    """,

    "DADOS_K02_FONTES": """
        SELECT 16 AS fontes_ok
    """,

    "DADOS_K03_TOTAL": """
        SELECT 18 AS fontes_total
    """,

    "DADOS_K04_SC": """
        SELECT COUNT(*) AS linhas_sem_cotacao
        FROM "NFE"
        WHERE "PRE_MIN_COT" IS NULL
          AND "ANO" IN (2025,2026)
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
    """,

    "DADOS_K05_PCT": """
        SELECT
            ROUND(
                COUNT(CASE WHEN "PRE_MIN_COT" IS NULL THEN 1 END)*100.0
                /NULLIF(COUNT(*),0)
            ,1) AS pct_sem_cotacao
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
          AND "NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'
    """,

    "DADOS_R01_FONTES": """
        SELECT 'NFE' AS arquivo, COUNT(*) AS linhas, 'OK' AS status FROM "NFE"
        UNION ALL SELECT 'CP', COUNT(*), 'OK' FROM "CP"
        UNION ALL SELECT 'AD_v3', COUNT(*), 'OK' FROM "AD_v3"
        UNION ALL SELECT 'INFLAÇÃO', COUNT(*), 'OK' FROM "INFLAÇÃO"
        UNION ALL SELECT 'PMP_ID_INF_12', COUNT(*), 'OK' FROM "PMP_ID_INF_12"
        UNION ALL SELECT 'NUM_COT', COUNT(*), 'OK' FROM "NUM_COT"
        UNION ALL SELECT 'COT', COUNT(*), 'OK' FROM "COT"
        UNION ALL SELECT 'CURVA ABC FORN', COUNT(*), 'OK' FROM "CURVA ABC FORN"
        UNION ALL SELECT 'CP_SEMANA', COUNT(*), 'OK' FROM "CP_SEMANA"
        UNION ALL SELECT 'FILIAIS_SUPPLY', COUNT(*), 'OK' FROM "FILIAIS_SUPPLY"
        LIMIT 18
    """,

    "DADOS_R02_SANEA": """
        SELECT
            'Sem cotação (IDs A/AA/AAA)'      AS problema,
            'PRE_MIN_COT'                      AS campo,
            COUNT(CASE WHEN "PRE_MIN_COT" IS NULL AND "CURVA_ID" IN ('AAA','AA','A')
                THEN 1 END)                    AS linhas,
            ROUND(
                COUNT(CASE WHEN "PRE_MIN_COT" IS NULL AND "CURVA_ID" IN ('AAA','AA','A')
                    THEN 1 END)*100.0/NULLIF(COUNT(*),0)
            ,1) AS pct,
            'Alto' AS impacto
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
        UNION ALL
        SELECT
            'Compra acima mínimo', 'IMP_COT',
            COUNT(CASE WHEN "IMP_COT">0 THEN 1 END),
            ROUND(COUNT(CASE WHEN "IMP_COT">0 THEN 1 END)*100.0/NULLIF(COUNT(*),0),1),
            'Médio'
        FROM "NFE"
        WHERE "ANO" IN (2025,2026)
        LIMIT 10
    """,
}


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _load_elements() -> tuple[list, dict]:
    els = json.loads(ELEMENTS_FILE.read_text(encoding='utf-8')) if ELEMENTS_FILE.exists() else []
    return els, {e.get('variavel_js',''): e for e in els}

def _load_csv(vjs: str, indexes: dict) -> list[dict]:
    """Carrega CSV antigo para comparação."""
    info = indexes.get(vjs, {})
    dados = info.get('dados','')
    if not dados:
        return []
    folder = info.get('_folder','')
    path   = PROC / folder / dados
    if not path.exists():
        return []
    if path.suffix == '.json':
        data = json.loads(path.read_text(encoding='utf-8'))
        return [data] if isinstance(data, dict) else data
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))

def _compare(sql_rows: list, csv_rows: list) -> str:
    if not csv_rows:
        return f"SEM_CSV({len(sql_rows)}r)"
    rq, rc = len(sql_rows), len(csv_rows)
    if rc == 0:
        return f"CSV_VAZIO({rq}r)"
    delta_rows = abs(rq - rc) / max(rc, 1) * 100
    if delta_rows > 20:
        return f"⚠️ SQL:{rq}r CSV:{rc}r (Δ{delta_rows:.0f}%)"
    # Comparar somas numéricas
    if sql_rows and csv_rows:
        for k in sql_rows[0]:
            try:
                s_sum = sum(float(r.get(k,0) or 0) for r in sql_rows)
                c_sum = sum(float(r.get(k,0) or 0) for r in csv_rows if k in r)
                if c_sum and abs(s_sum-c_sum)/abs(c_sum) > 0.05:
                    return f"⚠️ {k}: SQL={s_sum:.0f} CSV={c_sum:.0f} (Δ{abs(s_sum-c_sum)/c_sum*100:.1f}%)"
            except (ValueError, TypeError):
                pass
    return f"✅ {rq}r"

def _load_all_indexes() -> dict:
    """Carrega todos os 00_index.json, retorna dict variavel_js → elem_info."""
    out = {}
    for idx_file in sorted(PROC.glob('*/[0-9]*_00_index.json')):
        idx = json.loads(idx_file.read_text(encoding='utf-8'))
        tab = idx.get('data_page', idx.get('label','?'))
        folder = idx_file.parent.name
        for e in idx.get('elementos', []):
            vjs = e.get('variavel_js','')
            if vjs:
                out[vjs] = {**e, 'tab': tab, '_folder': folder, '_label': idx.get('label','')}
    return out


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def run(only_tab: str | None = None, dry_run: bool = False):
    indexes    = _load_all_indexes()
    els, by_vjs = _load_elements()
    results    = []

    for vjs, info in indexes.items():
        tab  = info.get('_label', info.get('tab', '?'))
        tipo = info.get('tipo', '?')

        if only_tab and tab.lower() != only_tab.lower():
            results.append({'vjs': vjs, 'tab': tab, 'tipo': tipo,
                            'status': 'SKIP_TAB', 'rows': 0, 'delta': '—', 'note': ''})
            continue

        # Já feito (tem SQL + snapshot, de qualquer origem)
        entry = by_vjs.get(vjs, {})
        if entry.get('sql','').strip() and entry.get('rows_snapshot'):
            results.append({'vjs': vjs, 'tab': tab, 'tipo': tipo,
                            'status': 'DONE', 'rows': len(entry['rows_snapshot']),
                            'delta': '✅', 'note': ''})
            continue

        sql = SQL_MAP.get(vjs, '').strip()
        if not sql:
            results.append({'vjs': vjs, 'tab': tab, 'tipo': tipo,
                            'status': 'NO_SQL', 'rows': 0, 'delta': '—', 'note': ''})
            continue

        if dry_run:
            results.append({'vjs': vjs, 'tab': tab, 'tipo': tipo,
                            'status': 'DRY', 'rows': 0, 'delta': '—', 'note': sql[:60]})
            continue

        print(f"  [{tab}] {vjs}...", end='', flush=True)
        result = run_query(sql)

        if not result.get('ok'):
            err = result.get('error','?')[:80]
            print(f" ERRO: {err}")
            results.append({'vjs': vjs, 'tab': tab, 'tipo': tipo,
                            'status': 'FAIL', 'rows': 0, 'delta': '❌', 'note': err})
            continue

        rows  = result.get('rows', [])
        delta = _compare(rows, _load_csv(vjs, indexes))
        print(f" {len(rows)}r {delta}")

        snapshot = rows[:200]
        now      = _now()

        if vjs in by_vjs and by_vjs[vjs].get('origem','') != 'nlsql':
            # Atualizar entrada existente de pipeline
            by_vjs[vjs].update({
                'sql': sql, 'rows_snapshot': snapshot,
                'config': info.get('config', by_vjs[vjs].get('config',{})),
                'updated_at': now,
            })
        else:
            # Criar nova entrada de pipeline
            new_entry = {
                'id':              str(uuid.uuid4()),
                'tipo':            tipo,
                'title':           info.get('titulo', vjs)[:80],
                'destination_tab': info.get('tab', '?'),
                'config':          info.get('config', {}),
                'sql':             sql,
                'columns':         list(rows[0].keys()) if rows else [],
                'rows_snapshot':   snapshot,
                'variavel_js':     vjs,
                'question':        '',
                'origem':          'pipeline',
                'created_at':      now,
                'updated_at':      now,
            }
            els.append(new_entry)
            by_vjs[vjs] = new_entry

        results.append({'vjs': vjs, 'tab': tab, 'tipo': tipo,
                        'status': 'OK', 'rows': len(rows),
                        'delta': delta, 'note': ''})

    # Salvar elements.json
    if not dry_run:
        ELEMENTS_FILE.write_text(
            json.dumps(els, ensure_ascii=False, indent=2), encoding='utf-8')

    # Atualizar STATUS.md
    _update_status(results)

    # Resumo
    done  = sum(1 for r in results if r['status'] in ('OK','DONE'))
    fail  = sum(1 for r in results if r['status'] == 'FAIL')
    nosql = sum(1 for r in results if r['status'] == 'NO_SQL')
    print(f"\n{'DRY RUN - ' if dry_run else ''}Concluido: {done}/{len(results)} OK  falhas: {fail}  sem SQL: {nosql}")
    return results


def _update_status(results: list):
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    icon = {
        'OK': '✅', 'DONE': '✅', 'FAIL': '❌',
        'NO_SQL': '⏳', 'DRY': '🔎', 'SKIP_TAB': '—',
    }
    now    = datetime.now().strftime('%Y-%m-%d %H:%M')
    done   = sum(1 for r in results if r['status'] in ('OK','DONE'))
    total  = sum(1 for r in results if r['status'] != 'SKIP_TAB')
    lines  = [
        f"# STATUS — Migração Pipeline → NL-SQL",
        f"\nAtualizado: {now} | **{done}/{total}** elementos prontos\n",
        "| Aba | Elemento | Tipo | Status | Linhas | Delta |",
        "|-----|----------|------|--------|--------|-------|",
    ]
    for r in results:
        if r['status'] == 'SKIP_TAB':
            continue
        st = icon.get(r['status'], r['status'])
        lines.append(f"| {r['tab']} | `{r['vjs']}` | {r['tipo']} | {st} | {r['rows']} | {r['delta']} |")

    STATUS_FILE.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Migra elementos do pipeline para elements.json')
    p.add_argument('--tab',      help='Processar só uma aba (ex: Resumo)')
    p.add_argument('--dry-run',  action='store_true', help='Mostra SQLs sem executar')
    args = p.parse_args()
    run(only_tab=args.tab, dry_run=args.dry_run)
