"""
scripts/seed_pipeline_elements.py

Adiciona entradas de pipeline em elements.json para os elementos mais
importantes que já têm SQL simples (agregação direta do Zoho).

Execução única: só adiciona entradas que ainda não existem (por variavel_js).
Após rodar, execute o BAT para popular os snapshots via refresh_elements.py.

Uso: python scripts/seed_pipeline_elements.py
"""

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELEMENTS_FILE = ROOT / "nlsql" / "elements.json"

# ── Entradas a criar ───────────────────────────────────────────────────────────
# Cada dict: variavel_js, tipo, title, destination_tab, config, sql
# Apenas elementos com SQL simples (1 tabela, sem joins complexos).
# Elementos com joins multi-fonte ou cálculos Python permanecem no pipeline.

SEED: list[dict] = [
    # ── Resumo ────────────────────────────────────────────────────────────────
    {
        "variavel_js":     "RESUMO_R01_POR_MES",
        "tipo":            "GL",
        "title":           "Tendência Mensal de Compras",
        "destination_tab": "resumo",
        "config":          {"x": "mesano", "y": "spend", "color": "#2563eb"},
        "sql": 'SELECT "MESANO" AS mesano, SUM("TOTAL") AS spend FROM "NFE" GROUP BY "MESANO" ORDER BY "MESANO"',
    },
    {
        "variavel_js":     "RESUMO_R06_GEO_NNE",
        "tipo":            "HL",
        "title":           "SUP por GEO — Norte e Nordeste",
        "destination_tab": "resumo",
        "config":          {"label": "uf", "value": "spend"},
        "sql": (
            'SELECT "UF" AS uf, SUM("TOTAL") AS spend FROM "NFE" '
            "WHERE \"UF\" IN ('AC','AM','AP','PA','RO','RR','TO',"
            "'AL','BA','CE','MA','PB','PE','PI','RN','SE') "
            'GROUP BY "UF" ORDER BY spend DESC'
        ),
    },
    {
        "variavel_js":     "RESUMO_R07_GEO_SSE",
        "tipo":            "HL",
        "title":           "SUP por GEO — Sul e Sudeste",
        "destination_tab": "resumo",
        "config":          {"label": "uf", "value": "spend"},
        "sql": (
            'SELECT "UF" AS uf, SUM("TOTAL") AS spend FROM "NFE" '
            "WHERE \"UF\" IN ('ES','MG','RJ','SP','PR','RS','SC','DF','GO','MS','MT') "
            'GROUP BY "UF" ORDER BY spend DESC'
        ),
    },
    # ── Impacto ───────────────────────────────────────────────────────────────
    {
        "variavel_js":     "IMPACTO_R01_MES",
        "tipo":            "GB",
        "title":           "Impacto Nacional por Mês",
        "destination_tab": "impacto",
        "config":          {"x": "mesano", "y": "imp_cot", "color": "#b91c1c"},
        "sql": (
            'SELECT "MESANO" AS mesano, SUM("IMP_COT") AS imp_cot FROM "NFE" '
            'WHERE "IMP_COT" > 0 GROUP BY "MESANO" ORDER BY "MESANO"'
        ),
    },
    {
        "variavel_js":     "IMPACTO_R02_UF",
        "tipo":            "HL",
        "title":           "Impacto por UF",
        "destination_tab": "impacto",
        "config":          {"label": "uf", "value": "imp_cot", "color": "r"},
        "sql": (
            'SELECT "UF" AS uf, SUM("IMP_COT") AS imp_cot FROM "NFE" '
            'WHERE "IMP_COT" > 0 GROUP BY "UF" ORDER BY imp_cot DESC'
        ),
    },
    # ── Inflação ──────────────────────────────────────────────────────────────
    {
        "variavel_js":     "INFLACAO_R02_MES_RS",
        "tipo":            "GB",
        "title":           "Exposição R$ por Mês",
        "destination_tab": "inflacao",
        "config":          {"x": "mesano", "y": "exposicao_rs", "color": "#a16207"},
        "sql": (
            'SELECT "MESANO" AS mesano, SUM("SOMA_INF_ID_PMP") AS exposicao_rs '
            'FROM "INFLAÇÃO" GROUP BY "MESANO" ORDER BY "MESANO"'
        ),
    },
    {
        "variavel_js":     "INFLACAO_R04_POR_CAT",
        "tipo":            "T",
        "title":           "Inflação Nacional por Categoria",
        "destination_tab": "inflacao",
        "config":          {"colunas": [{"key": "cat2", "cls": "nm"},
                                         {"key": "inflacao_media_pct", "cls": "num", "fmt": "pct"},
                                         {"key": "exposicao_rs", "cls": "num", "fmt": "brl"}]},
        "sql": (
            'SELECT "CAT2" AS cat2, '
            'AVG("PERC_INF_ID_PMP") AS inflacao_media_pct, '
            'SUM("SOMA_INF_ID_PMP") AS exposicao_rs '
            'FROM "INFLAÇÃO" GROUP BY "CAT2" ORDER BY inflacao_media_pct DESC'
        ),
    },
    {
        "variavel_js":     "INFLACAO_R03_POR_UF",
        "tipo":            "T",
        "title":           "Inflação por UF",
        "destination_tab": "inflacao",
        "config":          {"colunas": [{"key": "uf"},
                                         {"key": "inflacao_media_pct", "cls": "num", "fmt": "pct"},
                                         {"key": "exposicao_rs", "cls": "num", "fmt": "brl"}]},
        "sql": (
            'SELECT "UF" AS uf, '
            'AVG("PERC_INF_ID_PMP") AS inflacao_media_pct, '
            'SUM("SOMA_INF_ID_PMP") AS exposicao_rs '
            'FROM "INFLAÇÃO" GROUP BY "UF" ORDER BY inflacao_media_pct DESC'
        ),
    },
    # ── Financeiro ────────────────────────────────────────────────────────────
    {
        "variavel_js":     "FINANCEIRO_R01_AGING",
        "tipo":            "T",
        "title":           "Aging de CP",
        "destination_tab": "financeiro",
        "config":          {"colunas": [{"key": "faixa_dias", "cls": "nm"},
                                         {"key": "valor", "cls": "num", "fmt": "brl"},
                                         {"key": "titulos", "cls": "num"}]},
        "sql": (
            'SELECT "FAIXA_DIAS" AS faixa_dias, '
            'SUM("VRATUAPAG") AS valor, COUNT(*) AS titulos '
            'FROM "CP" WHERE "STATUSPAG" = \'Em Aberto\' '
            'GROUP BY "FAIXA_DIAS" ORDER BY valor DESC'
        ),
    },
    {
        "variavel_js":     "FINANCEIRO_R02_FORN",
        "tipo":            "T",
        "title":           "CP por Fornecedor",
        "destination_tab": "financeiro",
        "config":          {"colunas": [{"key": "fornecedor", "cls": "nm"},
                                         {"key": "curva"},
                                         {"key": "cp_aberto", "cls": "num", "fmt": "brl"},
                                         {"key": "cp_vencido", "cls": "num", "fmt": "brl"},
                                         {"key": "titulos", "cls": "num"}]},
        "sql": (
            'SELECT "NMFANTFORN" AS fornecedor, '
            'SUM("VRATUAPAG") AS cp_aberto, '
            'SUM(CASE WHEN "STATUS_VENC" = \'Vencido\' THEN "VRATUAPAG" ELSE 0 END) AS cp_vencido, '
            'COUNT(*) AS titulos '
            'FROM "CP" WHERE "STATUSPAG" = \'Em Aberto\' '
            'GROUP BY "NMFANTFORN" ORDER BY cp_aberto DESC LIMIT 200'
        ),
    },
    # ── Adiantamentos ─────────────────────────────────────────────────────────
    {
        "variavel_js":     "ADIANTAMENTO_R02_EMP",
        "tipo":            "HL",
        "title":           "AD por Empresa",
        "destination_tab": "adiantamentos",
        "config":          {"label": "empresa", "value": "pendente", "sub": "conciliado"},
        "sql": (
            'SELECT "NMEMP" AS empresa, '
            'SUM(CASE WHEN "STATUS_CONCILIACAO" != \'CONCILIADO\' THEN "VALOR_FINAL" ELSE 0 END) AS pendente, '
            'SUM(CASE WHEN "STATUS_CONCILIACAO" = \'CONCILIADO\' THEN "VALOR_FINAL" ELSE 0 END) AS conciliado '
            'FROM "AD_v3" GROUP BY "NMEMP" ORDER BY pendente DESC'
        ),
    },
    {
        "variavel_js":     "ADIANTAMENTO_R06_FORN",
        "tipo":            "T",
        "title":           "AD por Fornecedor",
        "destination_tab": "adiantamentos",
        "config":          {"colunas": [{"key": "fornecedor", "cls": "nm"},
                                         {"key": "pendente", "cls": "num", "fmt": "brl"},
                                         {"key": "conciliado", "cls": "num", "fmt": "brl"},
                                         {"key": "registros", "cls": "num"}]},
        "sql": (
            'SELECT "NMFANTFORN" AS fornecedor, '
            'SUM(CASE WHEN "STATUS_CONCILIACAO" != \'CONCILIADO\' THEN "VALOR_FINAL" ELSE 0 END) AS pendente, '
            'SUM(CASE WHEN "STATUS_CONCILIACAO" = \'CONCILIADO\' THEN "VALOR_FINAL" ELSE 0 END) AS conciliado, '
            'COUNT(*) AS registros '
            'FROM "AD_v3" GROUP BY "NMFANTFORN" ORDER BY pendente DESC LIMIT 200'
        ),
    },
    # ── Serviços ──────────────────────────────────────────────────────────────
    {
        "variavel_js":     "SERVICO_R01_UF",
        "tipo":            "HL",
        "title":           "Serviços por UF",
        "destination_tab": "servicos",
        "config":          {"label": "uf", "value": "spend"},
        "sql": (
            'SELECT "UF" AS uf, SUM("TOTAL") AS spend FROM "NFE" '
            'WHERE "CAT2" LIKE \'D5%\' GROUP BY "UF" ORDER BY spend DESC'
        ),
    },
    {
        "variavel_js":     "SERVICO_R04_FORN",
        "tipo":            "T",
        "title":           "Fornecedores de Serviços",
        "destination_tab": "servicos",
        "config":          {"colunas": [{"key": "fornecedor", "cls": "nm"},
                                         {"key": "categoria"},
                                         {"key": "spend", "cls": "num", "fmt": "brl"},
                                         {"key": "pct", "cls": "num"}]},
        "sql": (
            'SELECT "FANTASIA_OFICIAL" AS fornecedor, "CAT3" AS categoria, '
            'SUM("TOTAL") AS spend FROM "NFE" '
            'WHERE "CAT2" LIKE \'D5%\' '
            'GROUP BY "FANTASIA_OFICIAL", "CAT3" ORDER BY spend DESC LIMIT 200'
        ),
    },
]


# ── Script ────────────────────────────────────────────────────────────────────

def main() -> None:
    existing = json.loads(ELEMENTS_FILE.read_text(encoding="utf-8")) if ELEMENTS_FILE.exists() else []
    existing_vjs = {e.get("variavel_js", "") for e in existing}

    now = datetime.now(timezone.utc).isoformat()
    added = 0

    for seed in SEED:
        vjs = seed["variavel_js"]
        if vjs in existing_vjs:
            print(f"  [skip] {vjs} (já existe)")
            continue

        entry = {
            "id":              str(uuid.uuid4()),
            "tipo":            seed["tipo"],
            "title":           seed["title"],
            "destination_tab": seed["destination_tab"],
            "config":          seed.get("config", {}),
            "sql":             seed["sql"],
            "columns":         [],
            "rows_snapshot":   [],
            "variavel_js":     vjs,
            "question":        "",
            "origem":          "pipeline",
            "created_at":      now,
            "updated_at":      now,
        }
        existing.append(entry)
        existing_vjs.add(vjs)
        print(f"  [add]  {vjs}")
        added += 1

    ELEMENTS_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nConcluido: {added} entradas adicionadas de {len(SEED)} definidas.")
    print("Proximos passos:")
    print("  1. python nlsql/refresh_elements.py   (popula snapshots via Zoho)")
    print("  2. python pipeline/build.py            (embute no HTML)")


if __name__ == "__main__":
    main()
