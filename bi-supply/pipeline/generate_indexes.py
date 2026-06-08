"""
generate_indexes.py — gera/atualiza 00_index.json de todas as abas
com posições no grid 16 colunas × 40px.

Cada elemento tem:
  - id, variavel_js, tipo, titulo, subtitulo, zoho_origem
  - dados (arquivo em data/processed/{aba}/)
  - config (params de renderização)
  - layout: col, col_span, row, row_span, visivel, origem

origem='v4'        → já tem posição no mock
origem='processed' → existe só em data/processed/, sem posição ainda

Uso: python pipeline/generate_indexes.py
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

def e(id_, vjs, tipo, titulo, dados, config, col, col_span, row, row_span,
      subtitulo="", zoho="", visivel=True, origem="v4"):
    """Cria um elemento completo."""
    return {
        "id": id_,
        "variavel_js": vjs,
        "tipo": tipo,
        "titulo": titulo,
        "subtitulo": subtitulo,
        "zoho_origem": zoho,
        "dados": dados,
        "config": config,
        "layout": {
            "col": col, "col_span": col_span,
            "row": row, "row_span": row_span,
            "visivel": visivel,
            "origem": origem,
        }
    }

def ep(id_, vjs, tipo, titulo, dados, config, col=1, col_span=16, row=None, row_span=6,
       subtitulo="", zoho="", visivel=True):
    """Elemento de data/processed — posicionado abaixo dos elementos v4."""
    return {
        "id": id_,
        "variavel_js": vjs,
        "tipo": tipo,
        "titulo": titulo,
        "subtitulo": subtitulo,
        "zoho_origem": zoho,
        "dados": dados,
        "config": config,
        "layout": {
            "col": col, "col_span": col_span,
            "row": row, "row_span": row_span,
            "visivel": visivel if row is not None else False,
            "origem": "processed",
        }
    }

# ── 01_resumo ─────────────────────────────────────────────────────────────────
IDX_01 = {
    "aba": "01_resumo", "data_page": "resumo", "label": "Resumo",
    "grid": {"colunas": 16, "row_height_px": 40},
    "elementos": [
        # KPIs — row 1, cada KPI = 2 cols, row_span=3
        e("01_resumo_k01_total_comprado",   "RESUMO_K01_TOTAL_COMPRADO",   "KPI","Total Comprado",       "01_resumo_k00_kpis.json",{"chave":"total_comprado_operacional","fmt":"brl","delta_chave":"crescimento_yoy_pct","delta_ctx":"vs. 12m anteriores","delta_dir":"up"},   col=1,  col_span=2, row=1,row_span=2, zoho="NFE"),
        e("01_resumo_k02_fornecedores",     "RESUMO_K02_FORNECEDORES",     "KPI","Fornecedores Ativos",  "01_resumo_k00_kpis.json",{"chave":"fornecedores_ativos","fmt":"num","delta_chave":"ids_unicos","delta_ctx":"IDs analíticos"},                                         col=3,  col_span=2, row=1,row_span=2, zoho="NFE"),
        e("01_resumo_k03_produtos",         "RESUMO_K03_PRODUTOS",         "KPI","Produtos / IDs",       "01_resumo_k00_kpis.json",{"chave":"produtos_unicos","fmt":"num","delta_chave":"ids_unicos","delta_ctx":"IDs analíticos"},                                             col=5,  col_span=2, row=1,row_span=2, zoho="NFE"),
        e("01_resumo_k04_impacto",          "RESUMO_K04_IMPACTO",          "KPI","Impacto R$",           "01_resumo_k00_kpis.json",{"chave":"imp_cot_total","fmt":"brl","state":"alert"},                                                                                      col=7,  col_span=2, row=1,row_span=2, zoho="NFE"),
        e("01_resumo_k05_oportunidade",     "RESUMO_K05_OPORTUNIDADE",     "KPI","Oportunidade R$",      "01_resumo_k00_kpis.json",{"chave":"imp_cot_total","fmt":"brl","state":"ok"},                                                                                         col=9,  col_span=2, row=1,row_span=2, zoho="NFE"),
        e("01_resumo_k06_cotacao",          "RESUMO_K06_COTACAO",          "KPI","Compras com Cotação",  "01_resumo_k00_kpis.json",{"chave":"pct_com_cotacao","fmt":"pct","state":"warn","delta_ctx":"meta 80%","delta_dir":"warn"},                                            col=11, col_span=2, row=1,row_span=2, zoho="NFE"),
        e("01_resumo_k07_ad",               "RESUMO_K07_AD",               "KPI","AD Pendente",          "01_resumo_k00_kpis.json",{"chave":"ad_pendente","fmt":"brl","state":"warn","delta_ctx":"aguardando conciliação"},                                                  col=13, col_span=2, row=1,row_span=2, zoho="AD_v3"),
        e("01_resumo_k08_cp",               "RESUMO_K08_CP",               "KPI","CP em Aberto",         "01_resumo_k00_kpis.json",{"chave":"cp_aberto","fmt":"brl","state":"alert","delta_chave":"cp_vencido","delta_ctx":"vencido","delta_dir":"down"},                       col=15, col_span=2, row=1,row_span=2, zoho="CP"),

        # row 2: Tendência mensal (col 1-10) + Por negócio (col 11-16)
        e("01_resumo_r01_por_mes",      "RESUMO_R01_POR_MES",      "GL","Tendência Mensal de Compras","01_resumo_r01_por_mes.csv",{"x":"mesano","y":"spend","color":"#2563eb"}, col=1,  col_span=10, row=3,row_span=6, subtitulo="Valor comprado · últimos 12 meses", zoho="NFE"),
        e("01_resumo_r02_por_negocio",  "RESUMO_R02_POR_NEGOCIO",  "HL","Compras por Negócio",         "01_resumo_r02_por_negocio.csv",{"label":"negocio","value":"spend","sub":""},                             col=11, col_span=6, row=3,row_span=6, subtitulo="Valor 12m", zoho="NFE"),

        # row 3: Top categorias (col 1-8) + Top fornecedores (col 9-16)
        e("01_resumo_r03_top_categoria",   "RESUMO_R03_TOP_CATEGORIA",  "T","Top Categorias","01_resumo_r03_top_categoria.csv",{"colunas":[{"key":"cat2","label":"Categoria","cls":"nm"},{"key":"spend","label":"Valor 12m","cls":"num","fmt":"brl"},{"key":"pct","label":"%","cls":"num"},{"key":"inflacao_media_pct","label":"Inflação","cls":"num","fmt":"pct"},{"key":"imp_cot","label":"Impacto R$","cls":"num","fmt":"brl"}]},col=1,col_span=8,row=9,row_span=7,subtitulo="por valor comprado · inflação · impacto",zoho="NFE"),
        e("01_resumo_r04_top_fornecedor",  "RESUMO_R04_TOP_FORNECEDOR", "T","Top Fornecedores","01_resumo_r04_top_fornecedor.csv",{"colunas":[{"key":"fornecedor","label":"Fornecedor","cls":"nm"},{"key":"curva","label":"Curva"},{"key":"spend","label":"Valor","cls":"num","fmt":"brl"},{"key":"pct","label":"%","cls":"num"},{"key":"cp_aberto","label":"CP Aberto","cls":"num","fmt":"brl"}]},col=9,col_span=8,row=9,row_span=7,subtitulo="por valor · curva · CP",zoho="NFE"),

        # row 4: Alertas (full width)
        e("01_resumo_alertas",           "RESUMO_ALERTAS",           "AL","Alertas Executivos",    "01_resumo_k00_kpis.json",{"regras":True},                              col=1,  col_span=16, row=16,row_span=4, subtitulo="prioridades automáticas"),

        # row 5: Geo N/NE (col 1-8) + Geo S/SE (col 9-16)
        e("01_resumo_r06_geo_nne",       "RESUMO_R06_GEO_NNE",       "HL","SUP por GEO · N e NE", "01_resumo_r06_geo_nne.csv",{"label":"uf","value":"spend"},               col=1,  col_span=8,  row=20,row_span=5, subtitulo="Norte e Nordeste · R$ mi · 12m",zoho="NFE"),
        e("01_resumo_r07_geo_sse",       "RESUMO_R07_GEO_SSE",       "HL","SUP por GEO · S e SE", "01_resumo_r07_geo_sse.csv",{"label":"uf","value":"spend"},               col=9,  col_span=8,  row=20,row_span=5, subtitulo="Sul e Sudeste · R$ mi · 12m",zoho="NFE"),

        # row 6: Resumo negócios (col 1-8) + Resumo filial (col 9-16)
        e("01_resumo_r08_por_filial",    "RESUMO_R08_POR_FILIAL",    "T","RESUMO_FILIAL",          "01_resumo_r08_por_filial.csv",{"colunas":[{"key":"nome","label":"Filial","cls":"nm"},{"key":"negocio","label":"Negócio"},{"key":"uf","label":"UF"},{"key":"spend","label":"Valor","cls":"num","fmt":"brl"},{"key":"pct","label":"%","cls":"num"}]},col=9,col_span=8,row=25,row_span=6,subtitulo="top 8 · valor 12m · CP",zoho="NFE"),
        e("01_resumo_r09_cat2_por_uf",   "RESUMO_R09_CAT2_POR_UF",   "MX","Categoria × UF",       "01_resumo_r09_cat2_por_uf.csv",{"row_key":"cat2","col_key":"uf","val_key":"spend"},col=1,col_span=8,row=25,row_span=6,subtitulo="heatmap spend por categoria e estado",zoho="NFE"),
    ]
}

# ── 02_oportunidade ───────────────────────────────────────────────────────────
IDX_02 = {
    "aba":"02_oportunidade","data_page":"oportunidades","label":"Oportunidades",
    "grid":{"colunas":16,"row_height_px":40},
    "elementos":[
        e("02_oportunidade_k01_total",    "OPORTUNIDADE_K01_TOTAL",   "KPI","Oportunidade R$",    "02_oportunidade_k00_kpis.json",{"chave":"imp_cot_total","fmt":"brl","state":"warn"},          col=1,col_span=3,row=1,row_span=2,zoho="NFE"),
        e("02_oportunidade_k02_sem_cot",  "OPORTUNIDADE_K02_SEM_COT", "KPI","IDs AAA/A Sem Cot.", "02_oportunidade_k00_kpis.json",{"chave":"ids_aaa_sem_cotacao","fmt":"num","state":"alert"},    col=4,col_span=3,row=1,row_span=2,zoho="NFE"),
        e("02_oportunidade_k03_acima",    "OPORTUNIDADE_K03_ACIMA",   "KPI","IDs Acima do Mín.",  "02_oportunidade_k00_kpis.json",{"chave":"ids_comprados_acima_minimo","fmt":"num"},             col=7,col_span=3,row=1,row_span=2,zoho="NFE"),
        e("02_oportunidade_k04_pct",      "OPORTUNIDADE_K04_PCT",     "KPI","% Acima do Mínimo",  "02_oportunidade_k00_kpis.json",{"chave":"pct_linhas_acima_minimo","fmt":"pct","state":"warn"}, col=10,col_span=3,row=1,row_span=2,zoho="NFE"),
        e("02_oportunidade_k05_mono",     "OPORTUNIDADE_K05_MONO",    "KPI","≤1 Cotação (Risco)", "02_oportunidade_k00_kpis.json",{"chave":"itens_mono_cotacao","fmt":"num","state":"warn"},      col=13,col_span=4,row=1,row_span=3,zoho="NUM_COT"),
        e("02_oportunidade_r04_matriz",   "OPORTUNIDADE_R04_MATRIZ",  "MX","Matriz Prioridade",   "02_oportunidade_r04_matriz_prioridade.json",{"tipo":"matriz3x3"},                              col=1, col_span=5, row=3,row_span=7, subtitulo="Impacto × Esforço"),
        e("02_oportunidade_r05_por_tipo", "OPORTUNIDADE_R05_POR_TIPO","HL","Por Tipo de Oportunidade","02_oportunidade_r05_por_tipo.csv",{"label":"tipo","value":"valor"},                      col=6, col_span=5, row=3,row_span=7, zoho="NFE"),
        e("02_oportunidade_r03_por_uf",   "OPORTUNIDADE_R03_POR_UF",  "HL","Por UF",              "02_oportunidade_r03_por_uf.csv",{"label":"uf","value":"imp_cot"},                             col=11,col_span=6, row=3,row_span=7, zoho="NFE"),
        e("02_oportunidade_r01_tabela",   "OPORTUNIDADE_R01_TABELA",  "TE","Tabela de Oportunidades","02_oportunidade_r01_tabela_principal.csv",{"colunas":[{"key":"tipo","label":"Tipo"},{"key":"prioridade","label":"Prio","cls":"num"},{"key":"id","label":"ID","cls":"id"},{"key":"produto","label":"Produto","cls":"nm"},{"key":"fornecedor_atual","label":"Forn. Atual"},{"key":"preco_minimo","label":"Menor Cot.","cls":"num","fmt":"brl2"},{"key":"imp_cot","label":"Impacto","cls":"num","fmt":"brl"}]},col=1,col_span=16,row=10,row_span=8,subtitulo="fila priorizada por impacto",zoho="NFE"),
        # Tipo B (só processed)
        ep("02_oportunidade_r02_por_cat", "OPORTUNIDADE_R02_POR_CAT", "GB","Oportunidade por Categoria","02_oportunidade_r02_por_categoria.csv",{"x":"cat2","y":"imp_cot"},col_span=16,row_span=5,zoho="NFE"),
    ]
}

# ── 03_categoria ──────────────────────────────────────────────────────────────
IDX_03 = {
    "aba":"03_categoria","data_page":"categorias","label":"Categorias",
    "grid":{"colunas":16,"row_height_px":40},
    "nota":"KPIs são contextuais ao filtro ativo — calculados dinamicamente da hierarquia",
    "elementos":[
        e("03_categoria_r01_hierarquia",  "CATEGORIA_R01_HIERARQUIA",  "TB","Drilldown CAT1→CAT5",  "03_categoria_r01_hierarquia.csv",{"tipo":"cascata","niveis":["cat1","cat2","cat3","cat4","cat5"],"valor":"spend","inf":"inflacao_media_pct"},col=1,col_span=16,row=1,row_span=12,subtitulo="filtros em cascata · clique para navegar",zoho="NFE"),
        e("03_categoria_r02_cat2_por_mes","CATEGORIA_R02_CAT2_POR_MES","GL","CAT2 por Mês",          "03_categoria_r02_cat2_por_mes.csv",{"x":"mesano","y":"spend","serie_key":"cat2","color":"#2563eb"},col=1,col_span=10,row=12,row_span=5,subtitulo="top 5 categorias · séries 12m",zoho="NFE"),
        e("03_categoria_r03_cat2_por_uf", "CATEGORIA_R03_CAT2_POR_UF", "MX","CAT2 × UF",             "03_categoria_r03_cat2_por_uf.csv",{"row_key":"cat2","col_key":"uf","val_key":"spend"},              col=11,col_span=6,row=12,row_span=5,subtitulo="heatmap spend",zoho="NFE"),
        # Tipo B
        ep("03_categoria_r04_top_forn",   "CATEGORIA_R04_TOP_FORN",    "T","Top Fornecedores por Categoria","03_categoria_r04_top_fornecedor.csv",{"colunas":[{"key":"cat2"},{"key":"fornecedor","cls":"nm"},{"key":"spend","cls":"num","fmt":"brl"}]},col_span=8,row_span=6,zoho="NFE"),
        ep("03_categoria_r05_top_prod",   "CATEGORIA_R05_TOP_PROD",    "T","Top Produtos por Categoria","03_categoria_r05_top_produto.csv",{"colunas":[{"key":"cat2"},{"key":"produto","cls":"nm"},{"key":"spend","cls":"num","fmt":"brl"},{"key":"pmp_atual","cls":"num"},{"key":"var_pmp_pct","cls":"num","fmt":"pct"}]},col_span=8,row_span=6,zoho="NFE"),
    ]
}

# ── 04_filial ─────────────────────────────────────────────────────────────────
IDX_04 = {
    "aba":"04_filial","data_page":"filiais","label":"Filiais",
    "grid":{"colunas":16,"row_height_px":40},
    "elementos":[
        e("04_filial_k01_total",    "FILIAL_K01_TOTAL",    "KPI","Total Comprado",      "04_filial_k00_kpis.json",{"chave":"total_comprado","fmt":"brl"},           col=1, col_span=3,row=1,row_span=2,zoho="NFE"),
        e("04_filial_k02_media",    "FILIAL_K02_MEDIA",    "KPI","Compra Média/Filial", "04_filial_k00_kpis.json",{"chave":"compra_media_por_filial","fmt":"brl"},   col=4, col_span=3,row=1,row_span=2,zoho="NFE"),
        e("04_filial_k03_maior",    "FILIAL_K03_MAIOR",    "KPI","Maior Filial",        "04_filial_k00_kpis.json",{"chave":"maior_filial","fmt":"str"},              col=7, col_span=3,row=1,row_span=2,zoho="NFE"),
        e("04_filial_k04_maior_uf", "FILIAL_K04_MAIOR_UF", "KPI","Maior UF",           "04_filial_k00_kpis.json",{"chave":"maior_uf","fmt":"str"},                  col=10,col_span=3,row=1,row_span=2,zoho="NFE"),
        e("04_filial_k05_negocio",  "FILIAL_K05_NEGOCIO",  "KPI","Maior Negócio",      "04_filial_k00_kpis.json",{"chave":"maior_negocio","fmt":"str"},             col=13,col_span=4,row=1,row_span=2,zoho="NFE"),
        e("04_filial_r01_ranking",  "FILIAL_R01_RANKING",  "HL","Ranking de Filiais",  "04_filial_r01_ranking.csv",{"label":"nome","value":"spend","sub":"negocio"}, col=1, col_span=6,row=3,row_span=10,subtitulo="por valor comprado",zoho="NFE"),
        e("04_filial_r02_neg",      "FILIAL_R02_NEG",      "MX","Filial × Negócio",    "04_filial_r02_filial_negocio.csv",{"row_key":"cdfilial","col_key":"negocio","val_key":"spend"}, col=7,col_span=5,row=3,row_span=10,subtitulo="heatmap spend",zoho="NFE"),
        e("04_filial_r03_mes",      "FILIAL_R03_MES",      "GL","Top 3 Filiais × Mês", "04_filial_r03_top3_por_mes.csv",{"x":"mesano","y":"spend","serie_key":"cdfilial"}, col=12,col_span=5,row=3,row_span=5,zoho="NFE"),
        e("04_filial_r04_cat",      "FILIAL_R04_CAT",      "T","Filial × Categoria",   "04_filial_r04_por_categoria.csv",{"colunas":[{"key":"cdfilial"},{"key":"cat2","cls":"nm"},{"key":"spend","cls":"num","fmt":"brl"}]}, col=12,col_span=5,row=8,row_span=5,zoho="NFE"),
        # Tipo B
        ep("04_filial_r05_forn",    "FILIAL_R05_FORN",     "T","Filial × Fornecedor",  "04_filial_r05_por_fornecedor.csv",{"colunas":[{"key":"cdfilial"},{"key":"fornecedor","cls":"nm"},{"key":"spend","cls":"num","fmt":"brl"}]},col=1,col_span=16,row=13,row_span=6,zoho="NFE"),
    ]
}

# ── 05_estoque ────────────────────────────────────────────────────────────────
IDX_05 = {
    "aba":"05_estoque","data_page":"estoque","label":"Estoque",
    "grid":{"colunas":16,"row_height_px":40},
    "status":"PENDENTE",
    "nota":"Requer workspace APURAÇÃO DE RESULTADOS. Todos elementos Tipo B.",
    "elementos":[]
}

# ── 06_fornecedor ─────────────────────────────────────────────────────────────
IDX_06 = {
    "aba":"06_fornecedor","data_page":"forn360","label":"Fornecedor",
    "grid":{"colunas":16,"row_height_px":40},
    "elementos":[
        e("06_fornecedor_k01_ativos",  "FORNECEDOR_K01_ATIVOS",  "KPI","Fornecedores Ativos",   "06_fornecedor_k00_kpis.json",{"chave":"fornecedores_ativos","fmt":"num"},                                                                 col=1, col_span=2,row=1,row_span=2,zoho="NFE"),
        e("06_fornecedor_k02_curva",   "FORNECEDOR_K02_CURVA",   "KPI","Forn. AAA+AA",           "06_fornecedor_k00_kpis.json",{"chave":"forn_curva_aaa_aa","fmt":"num","state":"ok"},                                                            col=3, col_span=2,row=1,row_span=2,zoho="CURVA ABC FORN"),
        e("06_fornecedor_k03_spend",   "FORNECEDOR_K03_SPEND",   "KPI","Spend AAA/AA/A",          "06_fornecedor_k00_kpis.json",{"chave":"spend_curva_aaa_aa_a","fmt":"brl","state":"ok"},                                                        col=5, col_span=2,row=1,row_span=2,zoho="CURVA ABC FORN"),
        e("06_fornecedor_k04_pct",     "FORNECEDOR_K04_PCT",     "KPI","% Spend Top",             "06_fornecedor_k00_kpis.json",{"chave":"pct_spend_top","fmt":"pct","state":"ok"},                                                              col=7, col_span=2,row=1,row_span=2),
        e("06_fornecedor_k05_cp_n",    "FORNECEDOR_K05_CP_N",    "KPI","Forn. c/ CP Aberto",     "06_fornecedor_k00_kpis.json",{"chave":"forn_com_cp_aberto","fmt":"num","state":"warn"},                                                        col=9, col_span=2,row=1,row_span=2,zoho="CP"),
        e("06_fornecedor_k06_cp_r",    "FORNECEDOR_K06_CP_R",    "KPI","CP Aberto R$",            "06_fornecedor_k00_kpis.json",{"chave":"cp_aberto_total","fmt":"brl","state":"warn"},                                                          col=11,col_span=2,row=1,row_span=2,zoho="CP"),
        e("06_fornecedor_k07_ad_n",    "FORNECEDOR_K07_AD_N",    "KPI","Forn. c/ AD Pendente",   "06_fornecedor_k00_kpis.json",{"chave":"forn_com_ad_pendente","fmt":"num","state":"warn"},                                                      col=13,col_span=2,row=1,row_span=2,zoho="AD_v3"),
        e("06_fornecedor_k08_ad_r",    "FORNECEDOR_K08_AD_R",    "KPI","AD Pendente R$",          "06_fornecedor_k00_kpis.json",{"chave":"ad_pendente_total","fmt":"brl","state":"warn"},                                                        col=15,col_span=2,row=1,row_span=2,zoho="AD_v3"),
        e("06_fornecedor_r01_tabela",  "FORNECEDOR_R01_TABELA",  "TE","Tabela Fornecedor 360",   "06_fornecedor_r01_tabela_principal.csv",{"colunas":[{"key":"fornecedor","label":"Fornecedor","cls":"nm"},{"key":"curva","label":"Curva"},{"key":"empresas","label":"Empresas"},{"key":"ufs","label":"UFs"},{"key":"categorias_top","label":"Categorias"},{"key":"spend_total","label":"Spend","cls":"num","fmt":"brl"},{"key":"pct","label":"%","cls":"num"},{"key":"imp_cot","label":"IMP_COT","cls":"num","fmt":"brl"},{"key":"cp_aberto","label":"CP Aberto","cls":"num","fmt":"brl"},{"key":"cp_vencido","label":"CP Vencido","cls":"num","fmt":"brl"},{"key":"ad_pendente","label":"AD Pend.","cls":"num","fmt":"brl"}],"expandable":True},col=1,col_span=16,row=3,row_span=12,subtitulo="expandir para ver detalhe",zoho="NFE · CP · AD_v3"),
        # Tipo B
        ep("06_fornecedor_r02_cat",    "FORNECEDOR_R02_CAT",     "T","Fornecedor × Categoria",   "06_fornecedor_r02_por_categoria.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"cat2"},{"key":"spend","cls":"num","fmt":"brl"}]},col=1,col_span=16,row=15,row_span=6),
        ep("06_fornecedor_r03_prod",   "FORNECEDOR_R03_PROD",    "T","Produtos por Fornecedor",  "06_fornecedor_r03_produto_por_forn.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"produto","cls":"nm"},{"key":"spend","cls":"num","fmt":"brl"}]},col=1,col_span=16,row=22,row_span=6),
    ]
}

# ── 07_produto ────────────────────────────────────────────────────────────────
IDX_07 = {
    "aba":"07_produto","data_page":"produtos","label":"Produtos",
    "grid":{"colunas":16,"row_height_px":40},
    "elementos":[
        e("07_produto_k01_total",  "PRODUTO_K01_TOTAL",  "KPI","Total IDs",         "07_produto_k00_kpis.json",{"chave":"total_ids","fmt":"num"},                     col=1, col_span=3,row=1,row_span=2,zoho="PMP_ID_INF_12"),
        e("07_produto_k02_pmp",    "PRODUTO_K02_PMP",    "KPI","PMP Médio Cesta",   "07_produto_k00_kpis.json",{"chave":"pmp_medio_cesta","fmt":"brl2"},              col=4, col_span=3,row=1,row_span=2,zoho="PMP_ID_INF_12"),
        e("07_produto_k03_var",    "PRODUTO_K03_VAR",    "KPI","Var. PMP > 10%",    "07_produto_k00_kpis.json",{"chave":"ids_variacao_pmp_gt10pct","fmt":"num","state":"warn"}, col=7,col_span=3,row=1,row_span=2,zoho="PMP_ID_INF_12"),
        e("07_produto_k04_sc",     "PRODUTO_K04_SC",     "KPI","IDs Sem Cotação",   "07_produto_k00_kpis.json",{"chave":"ids_sem_cotacao_12m","fmt":"num","state":"warn"},     col=10,col_span=3,row=1,row_span=2,zoho="NUM_COT"),
        e("07_produto_k05_inf",    "PRODUTO_K05_INF",    "KPI","Inflação Média Cesta","07_produto_k00_kpis.json",{"chave":"inflacao_media_cesta","fmt":"pct","state":"warn"}, col=13,col_span=4,row=1,row_span=2,zoho="INFLAÇÃO"),
        e("07_produto_r01_tabela", "PRODUTO_R01_TABELA", "TE","Tabela de Produtos",   "07_produto_r01_tabela_principal.csv",{"colunas":[{"key":"produto","label":"Produto","cls":"nm"},{"key":"cat2","label":"Categoria"},{"key":"curva_id","label":"Curva ID"},{"key":"spend","label":"Spend","cls":"num","fmt":"brl"},{"key":"pmp_atual","label":"PMP","cls":"num","fmt":"brl2"},{"key":"var_pmp_pct","label":"Var. 12m","cls":"num","fmt":"pct"},{"key":"pmp_serie","label":"Série","cls":"spark"}],"expandable":True},col=1,col_span=16,row=3,row_span=10,subtitulo="com sparkline PMP 12m",zoho="NFE · PMP_ID_INF_12"),
        e("07_produto_r03_top_inf","PRODUTO_R03_TOP_INF","HL","Top Inflação",         "07_produto_r03_top_inflacao.csv",{"label":"produto","value":"var_pmp_pct","fmt":"pct"},col=1, col_span=8,row=13,row_span=5,zoho="PMP_PROD_INF_12"),
        e("07_produto_r04_top_def","PRODUTO_R04_TOP_DEF","HL","Top Deflação",         "07_produto_r04_top_deflacao.csv",{"label":"produto","value":"var_pmp_pct","fmt":"pct","color":"#16a34a"},col=9,col_span=8,row=13,row_span=5,zoho="PMP_PROD_INF_12"),
        # Tipo B
        ep("07_produto_r02_pmp_cat","PRODUTO_R02_PMP_CAT","T","PMP por Categoria",   "07_produto_r02_pmp_por_categoria.csv",{"colunas":[{"key":"cat2","cls":"nm"},{"key":"pmp_medio","cls":"num","fmt":"brl2"},{"key":"spend","cls":"num","fmt":"brl"}]},col_span=8,row_span=5),
    ]
}

# ── 08_cotacao ────────────────────────────────────────────────────────────────
IDX_08 = {
    "aba":"08_cotacao","data_page":"cotacoes","label":"Cotações",
    "grid":{"colunas":16,"row_height_px":40},
    "elementos":[
        e("08_cotacao_k01_cot",      "COTACAO_K01_COT",     "KPI","Produtos Cotados",       "08_cotacao_k00_kpis.json",{"chave":"produtos_cotados","fmt":"num"},                col=1, col_span=2,row=1,row_span=2,zoho="NUM_COT"),
        e("08_cotacao_k02_pct",      "COTACAO_K02_PCT",     "KPI","% Cobertura",             "08_cotacao_k00_kpis.json",{"chave":"pct_cobertura","fmt":"pct","state":"warn"},    col=3, col_span=2,row=1,row_span=2),
        e("08_cotacao_k03_media",    "COTACAO_K03_MEDIA",   "KPI","Média Cot./Produto",      "08_cotacao_k00_kpis.json",{"chave":"media_cotacoes_produto","fmt":"dec"},          col=5, col_span=2,row=1,row_span=2),
        e("08_cotacao_k04_zero",     "COTACAO_K04_ZERO",    "KPI","Com 0 Cotação",           "08_cotacao_k00_kpis.json",{"chave":"com_zero_cotacao","fmt":"num","state":"alert"},col=7, col_span=2,row=1,row_span=2),
        e("08_cotacao_k05_uma",      "COTACAO_K05_UMA",     "KPI","Com 1 Cotação",           "08_cotacao_k00_kpis.json",{"chave":"com_uma_cotacao","fmt":"num","state":"warn"},  col=9, col_span=2,row=1,row_span=2),
        e("08_cotacao_k06_le3",      "COTACAO_K06_LE3",     "KPI","Com ≤3 Cotações",         "08_cotacao_k00_kpis.json",{"chave":"com_le3_cotacoes","fmt":"num"},               col=11,col_span=2,row=1,row_span=2),
        e("08_cotacao_k07_imp",      "COTACAO_K07_IMP",     "KPI","Potencial IMP_COT",       "08_cotacao_k00_kpis.json",{"chave":"potencial_imp_cot","fmt":"brl","state":"warn"},col=13,col_span=2,row=1,row_span=2),
        e("08_cotacao_k08_menor",    "COTACAO_K08_MENOR",   "KPI","% Comprado no Mínimo",    "08_cotacao_k00_kpis.json",{"chave":"pct_comprado_no_menor","fmt":"pct"},           col=15,col_span=2,row=1,row_span=2),
        e("08_cotacao_r01_mes",      "COTACAO_R01_MES",     "GE","Distribuição QTD_COT/Mês", "08_cotacao_r01_cobertura_por_mes.csv",{"x":"mesano","stacks":["zero","uma","duas_tres","quatro_mais"]},col=1,col_span=10,row=3,row_span=6,subtitulo="0/1/2-3/4+ cotações por mês",zoho="NUM_COT"),
        e("08_cotacao_r02_curva",    "COTACAO_R02_CURVA",   "MX","Cobertura por Curva ABC",  "08_cotacao_r02_cobertura_por_curva.csv",{"row_key":"curva_id","col_key":"faixa","val_key":"total"},col=11,col_span=6,row=3,row_span=6,subtitulo="curva × faixas cotação",zoho="NUM_COT"),
        e("08_cotacao_r03_cat_mes",  "COTACAO_R03_CAT_MES", "GL","Cobertura por CAT × Mês",  "08_cotacao_r03_cobertura_por_cat_mes.csv",{"x":"mesano","y":"pct_cobertura","serie_key":"cat2"},col=1,col_span=8,row=9,row_span=5,subtitulo="top 5 categorias",zoho="NUM_COT"),
        e("08_cotacao_r04_uf",       "COTACAO_R04_UF",      "T","Cobertura por UF",          "08_cotacao_r04_cobertura_por_uf.csv",{"colunas":[{"key":"uf"},{"key":"pct_cobertura","cls":"num","fmt":"pct"},{"key":"imp_cot","cls":"num","fmt":"brl"},{"key":"imp_sobre_spend_pct","cls":"num","fmt":"pct"}]},col=9,col_span=8,row=9,row_span=5,zoho="NFE"),
        # Tipo B — blocos adicionais do v4 não conectados
        ep("08_cotacao_r05_min_forn","COTACAO_R05_MIN_FORN","T","MIN Cotação por Fornecedor","08_cotacao_r05_min_cotacao_fornecedor.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"vezes_menor_preco","cls":"num"},{"key":"ids_unicos","cls":"num"}]},col_span=8,row_span=5),
        ep("08_cotacao_r06_rel",     "COTACAO_R06_REL",     "T","Relatório de Cotações",     "08_cotacao_r06_relatorio.csv",{"colunas":[{"key":"id","cls":"id"},{"key":"uf"},{"key":"mesano"},{"key":"preco_min","cls":"num","fmt":"brl2"},{"key":"preco_med","cls":"num","fmt":"brl2"},{"key":"n_cotacoes","cls":"num"}]},col_span=16,row_span=7),
        ep("08_cotacao_r07_precos",  "COTACAO_R07_PRECOS",  "T","Consulta de Preços",        "08_cotacao_r07_consulta_precos.csv",{"colunas":[{"key":"id","cls":"id"},{"key":"produto","cls":"nm"},{"key":"fornecedor"},{"key":"mesano"},{"key":"preco_min","cls":"num","fmt":"brl2"}]},col_span=16,row_span=7),
        ep("08_cotacao_r08_prod",    "COTACAO_R08_PROD",    "T","Cotações por Produto",      "08_cotacao_r08_cotacao_por_produto.csv",{"colunas":[{"key":"produto","cls":"nm"},{"key":"n_meses_cotados","cls":"num"},{"key":"preco_min_global","cls":"num","fmt":"brl2"},{"key":"fornecedor_mais_barato"}]},col_span=16,row_span=7),
        ep("08_cotacao_r09_matriz",  "COTACAO_R09_MATRIZ",  "T","Matriz Produto × Mês",     "08_cotacao_r09_matriz_produto_mes.csv",{"tipo":"scroll_horiz"},col_span=16,row_span=8),
        ep("08_cotacao_r10_le3",     "COTACAO_R10_LE3",     "T","MIN Cot. ≤3 Concorrentes", "08_cotacao_r10_min_cot_baixa_concorrencia.csv",{"colunas":[{"key":"id","cls":"id"},{"key":"produto","cls":"nm"},{"key":"n_concorrentes","cls":"num"},{"key":"preco_min","cls":"num","fmt":"brl2"},{"key":"fornecedor_mais_barato"}]},col_span=16,row_span=5),
    ]
}

# ── 09_impacto ────────────────────────────────────────────────────────────────
IDX_09 = {
    "aba":"09_impacto","data_page":"impacto","label":"Impacto",
    "grid":{"colunas":16,"row_height_px":40},
    "nota":"IMP = impacto de cotação: diferença entre preço pago e menor preço cotado × quantidade",
    "elementos":[
        e("09_impacto_k01_total",  "IMPACTO_K01_TOTAL",  "KPI","Impacto Total",           "09_impacto_k00_kpis.json",{"chave":"imp_cot_total","fmt":"brl","state":"warn"},       col=1, col_span=3,row=1,row_span=2,zoho="NFE"),
        e("09_impacto_k02_ids",    "IMPACTO_K02_IDS",    "KPI","IDs com Impacto",          "09_impacto_k00_kpis.json",{"chave":"ids_com_impacto","fmt":"num"},                   col=4, col_span=3,row=1,row_span=2),
        e("09_impacto_k03_pct",    "IMPACTO_K03_PCT",    "KPI","% Acima do Mínimo",        "09_impacto_k00_kpis.json",{"chave":"pct_linhas_acima_minimo","fmt":"pct","state":"warn"},col=7,col_span=3,row=1,row_span=2),
        e("09_impacto_k04_uf",     "IMPACTO_K04_UF",     "KPI","UF Líder em Impacto",      "09_impacto_k00_kpis.json",{"chave":"uf_lider","fmt":"str"},                          col=10,col_span=3,row=1,row_span=2),
        e("09_impacto_k05_prod",   "IMPACTO_K05_PROD",   "KPI","Top Produto IMP",          "09_impacto_k00_kpis.json",{"chave":"top_produto_nome","fmt":"str"},                  col=13,col_span=4,row=1,row_span=2),
        e("09_impacto_r01_mes",    "IMPACTO_R01_MES",    "GB","Impacto Nacional por Mês",  "09_impacto_r01_por_mes.csv",{"x":"mesano","y":"imp_cot","color":"#b91c1c"},          col=1, col_span=10,row=3,row_span=5,subtitulo="IMP_COT acumulado",zoho="NFE"),
        e("09_impacto_r02_uf",     "IMPACTO_R02_UF",     "HL","Impacto por UF",            "09_impacto_r02_por_uf.csv",{"label":"uf","value":"imp_cot","color":"r"},             col=11,col_span=6,row=3,row_span=5,zoho="NFE"),
        e("09_impacto_r03_top_id", "IMPACTO_R03_TOP_ID", "T","Top IDs por IMP_COT",        "09_impacto_r03_top_id.csv",{"colunas":[{"key":"id","cls":"id"},{"key":"produto","cls":"nm"},{"key":"cat2"},{"key":"uf"},{"key":"fornecedor_atual"},{"key":"fornecedor_mais_barato"},{"key":"imp_cot","cls":"num","fmt":"brl"}]},col=1,col_span=16,row=8,row_span=8,subtitulo="fila de oportunidades de cotação",zoho="NFE"),
        # Tipo B
        ep("09_impacto_r04_forn",  "IMPACTO_R04_FORN",   "T","Forn. Mais Baratos Não Escolhidos","09_impacto_r04_forn_mais_barato_nao_escolhido.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"vezes_mais_barato","cls":"num"},{"key":"oportunidade_total","cls":"num","fmt":"brl"}]},col_span=8,row_span=5),
        ep("09_impacto_r05_prod_min","IMPACTO_R05_PROD_MIN","T","Produtos × MIN COT",       "09_impacto_r05_produto_min_cot.csv",{"colunas":[{"key":"id","cls":"id"},{"key":"produto","cls":"nm"},{"key":"pre_min_cot","cls":"num","fmt":"brl2"},{"key":"imp_cot","cls":"num","fmt":"brl"}]},col_span=8,row_span=5),
    ]
}

# ── 10_inflacao ───────────────────────────────────────────────────────────────
IDX_10 = {
    "aba":"10_inflacao","data_page":"inflacao","label":"Inflação",
    "grid":{"colunas":16,"row_height_px":40},
    "nota":"INF = variação do PMP ao longo do tempo. DIFERENTE de IMP_COT.",
    "elementos":[
        e("10_inflacao_k01_media",  "INFLACAO_K01_MEDIA",  "KPI","Inflação Média %",    "10_inflacao_k00_kpis.json",{"chave":"inflacao_media_pct","fmt":"pct","state":"warn"},      col=1, col_span=3,row=1,row_span=2,zoho="INFLAÇÃO"),
        e("10_inflacao_k02_exp",    "INFLACAO_K02_EXP",    "KPI","Exposição R$ 12m",    "10_inflacao_k00_kpis.json",{"chave":"exposicao_monetaria_12m","fmt":"brl"},               col=4, col_span=3,row=1,row_span=2,zoho="INFLAÇÃO"),
        e("10_inflacao_k03_gt10",   "INFLACAO_K03_GT10",   "KPI","IDs Inflação >10%",   "10_inflacao_k00_kpis.json",{"chave":"ids_com_inflacao_gt10pct","fmt":"num","state":"warn"},col=7, col_span=3,row=1,row_span=2),
        e("10_inflacao_k04_cat",    "INFLACAO_K04_CAT",    "KPI","CAT2 Mais Inflada",   "10_inflacao_k00_kpis.json",{"chave":"cat2_mais_inflada","fmt":"str"},                     col=10,col_span=7,row=1,row_span=2),
        e("10_inflacao_r01_cat_mes","INFLACAO_R01_CAT_MES","GL","Inflação % por CAT × Mês","10_inflacao_r01_por_cat_mes.csv",{"x":"mesano","y":"inflacao_media_pct","serie_key":"cat2"},col=1,col_span=10,row=3,row_span=6,subtitulo="top 5 categorias · séries 12m",zoho="INFLAÇÃO"),
        e("10_inflacao_r02_mes_rs", "INFLACAO_R02_MES_RS", "GB","Exposição R$ por Mês", "10_inflacao_r02_por_mes_rs.csv",{"x":"mesano","y":"exposicao_rs","color":"#a16207"},      col=11,col_span=6,row=3,row_span=6,zoho="INFLAÇÃO"),
        e("10_inflacao_r05_top_inf","INFLACAO_R05_TOP_INF","HL","Top Inflação (Produtos)","10_inflacao_r05_top_produto.csv",{"label":"produto","value":"var_pct","fmt":"pct"},     col=1, col_span=8,row=9,row_span=5,zoho="PMP_PROD_INF_12"),
        e("10_inflacao_r06_top_def","INFLACAO_R06_TOP_DEF","HL","Top Deflação (Produtos)","10_inflacao_r06_top_deflacao.csv",{"label":"produto","value":"var_pct","fmt":"pct","color":"g"},col=9,col_span=8,row=9,row_span=5,zoho="PMP_PROD_INF_12"),
        e("10_inflacao_r04_por_cat","INFLACAO_R04_POR_CAT","T","Nacional por Categoria", "10_inflacao_r04_por_categoria.csv",{"colunas":[{"key":"cat2","cls":"nm"},{"key":"inflacao_media_pct","cls":"num","fmt":"pct"},{"key":"exposicao_rs","cls":"num","fmt":"brl"}]},col=1,col_span=8,row=14,row_span=5,zoho="INFLAÇÃO"),
        e("10_inflacao_r03_por_uf", "INFLACAO_R03_POR_UF", "T","Por UF",               "10_inflacao_r03_por_uf.csv",{"colunas":[{"key":"uf"},{"key":"inflacao_media_pct","cls":"num","fmt":"pct"},{"key":"exposicao_rs","cls":"num","fmt":"brl"}]},col=9,col_span=8,row=14,row_span=5,zoho="INFLAÇÃO"),
        # Tipo B
        ep("10_inflacao_r07_forn",  "INFLACAO_R07_FORN",  "T","Por Fornecedor",        "10_inflacao_r07_por_fornecedor.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"inflacao_media_pct","cls":"num","fmt":"pct"},{"key":"spend","cls":"num","fmt":"brl"}]},col_span=8,row_span=5),
        ep("10_inflacao_r08_cat_prod","INFLACAO_R08_CAT_PROD","T","Produto × Categoria","10_inflacao_r08_produto_por_cat.csv",{"colunas":[{"key":"cat2"},{"key":"produto","cls":"nm"},{"key":"inflacao_media_pct","cls":"num","fmt":"pct"},{"key":"exposicao_rs","cls":"num","fmt":"brl"}]},col_span=8,row_span=5),
    ]
}

# ── 11_fiscal ─────────────────────────────────────────────────────────────────
IDX_11 = {
    "aba":"11_fiscal","data_page":"fiscal","label":"Fiscal",
    "grid":{"colunas":16,"row_height_px":40},
    "status":"PENDENTE",
    "nota":"Requer base cadastral de regime fiscal + crédito CBS/IBS 2027.",
    "elementos":[]
}

# ── 12_financeiro ─────────────────────────────────────────────────────────────
IDX_12 = {
    "aba":"12_financeiro","data_page":"financeiro","label":"Financeiro",
    "grid":{"colunas":16,"row_height_px":40},
    "nota":"STATUSPAG: 'Em Aberto' = pendente, 'Baixado' = pago.",
    "elementos":[
        e("12_financeiro_k01_aberto","FINANCEIRO_K01_ABERTO","KPI","CP em Aberto",    "12_financeiro_k00_kpis.json",{"chave":"cp_aberto_total","fmt":"brl","state":"warn"},  col=1, col_span=3,row=1,row_span=2,zoho="CP"),
        e("12_financeiro_k02_tit",   "FINANCEIRO_K02_TIT",   "KPI","Títulos Abertos", "12_financeiro_k00_kpis.json",{"chave":"cp_titulos","fmt":"num"},                    col=4, col_span=3,row=1,row_span=2),
        e("12_financeiro_k03_venc",  "FINANCEIRO_K03_VENC",  "KPI","CP Vencido",      "12_financeiro_k00_kpis.json",{"chave":"cp_vencido","fmt":"brl","state":"alert"},    col=7, col_span=3,row=1,row_span=2),
        e("12_financeiro_k04_7d",    "FINANCEIRO_K04_7D",    "KPI","A Vencer 7d",     "12_financeiro_k00_kpis.json",{"chave":"cp_a_vencer_7d","fmt":"brl"},                col=10,col_span=3,row=1,row_span=2),
        e("12_financeiro_k05_120",   "FINANCEIRO_K05_120",   "KPI","CP Crítico +120d","12_financeiro_k00_kpis.json",{"chave":"cp_critico_120d","fmt":"brl","state":"alert"},col=13,col_span=4,row=1,row_span=2),
        e("12_financeiro_r03_timeline","FINANCEIRO_R03_TIMELINE","GB","Timeline Semanal","12_financeiro_r03_timeline_semanal.csv",{"x":"semana","stacks":["valor_pago","valor_vencimentos","valor_vencido"]},col=1,col_span=16,row=3,row_span=5,subtitulo="próximas 8 semanas",zoho="CP_SEMANA"),
        e("12_financeiro_r01_aging", "FINANCEIRO_R01_AGING", "T","Aging de CP",       "12_financeiro_r01_aging.csv",{"colunas":[{"key":"faixa_dias","cls":"nm"},{"key":"valor","cls":"num","fmt":"brl"},{"key":"titulos","cls":"num"}]},col=1,col_span=8,row=8,row_span=6,zoho="CP"),
        e("12_financeiro_r02_forn",  "FINANCEIRO_R02_FORN",  "T","CP por Fornecedor", "12_financeiro_r02_por_fornecedor.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"curva"},{"key":"cp_aberto","cls":"num","fmt":"brl"},{"key":"cp_vencido","cls":"num","fmt":"brl"},{"key":"titulos","cls":"num"}]},col=9,col_span=8,row=8,row_span=6,zoho="CP"),
        # Tipo B
        ep("12_financeiro_r04_saldo","FINANCEIRO_R04_SALDO","T","Saldo Semanal 2026",  "12_financeiro_r04_saldo_semanal_2026.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"semana"},{"key":"saldo","cls":"num","fmt":"brl"}]},col=1,col_span=16,row=14,row_span=6),
    ]
}

# ── 13_adiantamento ───────────────────────────────────────────────────────────
IDX_13 = {
    "aba":"13_adiantamento","data_page":"adiantamentos","label":"Adiantamentos",
    "grid":{"colunas":16,"row_height_px":40},
    "nota":"STATUS_CONCILIACAO: 'CONCILIADO'=ok, 'ADIANTAMENTO ?'=pendente.",
    "elementos":[
        e("13_adiantamento_k01_total","ADIANTAMENTO_K01_TOTAL","KPI","AD Total 12m",     "13_adiantamento_k00_kpis.json",{"chave":"ad_total_12m","fmt":"brl"},                  col=1, col_span=3,row=1,row_span=2,zoho="AD_v3"),
        e("13_adiantamento_k02_conc", "ADIANTAMENTO_K02_CONC", "KPI","Conciliado",        "13_adiantamento_k00_kpis.json",{"chave":"conciliado","fmt":"brl","state":"ok"},      col=4, col_span=3,row=1,row_span=2),
        e("13_adiantamento_k03_pend", "ADIANTAMENTO_K03_PEND", "KPI","Pendente",           "13_adiantamento_k00_kpis.json",{"chave":"pendente","fmt":"brl","state":"alert"},    col=7, col_span=3,row=1,row_span=2),
        e("13_adiantamento_k04_pct",  "ADIANTAMENTO_K04_PCT",  "KPI","% Conciliado",       "13_adiantamento_k00_kpis.json",{"chave":"pct_conciliado","fmt":"pct","state":"ok"}, col=10,col_span=3,row=1,row_span=2),
        e("13_adiantamento_k05_n",    "ADIANTAMENTO_K05_N",    "KPI","Registros Pendentes","13_adiantamento_k00_kpis.json",{"chave":"n_pendente","fmt":"num","state":"warn"},    col=13,col_span=4,row=1,row_span=2),
        e("13_adiantamento_r01_funil","ADIANTAMENTO_R01_FUNIL","FU","Funil de Conciliação","13_adiantamento_r01_funil.csv",{"label":"status","value":"valor"},                   col=1, col_span=6,row=3,row_span=5,zoho="AD_v3"),
        e("13_adiantamento_r02_emp",  "ADIANTAMENTO_R02_EMP",  "HL","AD por Empresa",      "13_adiantamento_r02_por_empresa.csv",{"label":"empresa","value":"pendente","sub":"conciliado"},col=7,col_span=5,row=3,row_span=5,zoho="AD_v3"),
        e("13_adiantamento_r06_forn", "ADIANTAMENTO_R06_FORN", "T","AD por Fornecedor",   "13_adiantamento_r06_por_fornecedor.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"pendente","cls":"num","fmt":"brl"},{"key":"conciliado","cls":"num","fmt":"brl"},{"key":"registros","cls":"num"}]},col=12,col_span=5,row=3,row_span=5,zoho="AD_v3"),
        # Tipo B
        ep("13_adiantamento_r03_mes", "ADIANTAMENTO_R03_MES",  "GL","AD por Mês",          "13_adiantamento_r03_por_mes.csv",{"x":"mesano","stacks":["pendente","conciliado"]},col_span=8,row_span=5),
        ep("13_adiantamento_r04_uf",  "ADIANTAMENTO_R04_UF",   "HL","AD por UF",            "13_adiantamento_r04_por_uf.csv",{"label":"uf","value":"valor_total"},col=1,col_span=8,row=14,row_span=5),
        ep("13_adiantamento_r05_cat", "ADIANTAMENTO_R05_CAT",  "T","AD por Categoria",      "13_adiantamento_r05_por_categoria.csv",{"colunas":[{"key":"categoria","cls":"nm"},{"key":"pendente","cls":"num","fmt":"brl"},{"key":"conciliado","cls":"num","fmt":"brl"}]},col_span=8,row_span=5),
    ]
}

# ── 14_servico ────────────────────────────────────────────────────────────────
IDX_14 = {
    "aba":"14_servico","data_page":"servicos","label":"Serviços",
    "grid":{"colunas":16,"row_height_px":40},
    "nota":"Filtra CAT2=D5 excluindo lancamentos financeiros.",
    "elementos":[
        e("14_servico_k01_total", "SERVICO_K01_TOTAL", "KPI","Total Serviços",      "14_servico_k00_kpis.json",{"chave":"total_servicos","fmt":"brl"},          col=1, col_span=3,row=1,row_span=2,zoho="NFE"),
        e("14_servico_k02_forn",  "SERVICO_K02_FORN",  "KPI","Fornecedores",        "14_servico_k00_kpis.json",{"chave":"fornecedores_servicos","fmt":"num"},    col=4, col_span=3,row=1,row_span=2),
        e("14_servico_k03_ufs",   "SERVICO_K03_UFS",   "KPI","UFs Atendidas",       "14_servico_k00_kpis.json",{"chave":"ufs_atendidas","fmt":"num"},            col=7, col_span=3,row=1,row_span=2),
        e("14_servico_k04_var",   "SERVICO_K04_VAR",   "KPI","Variação Mensal",     "14_servico_k00_kpis.json",{"chave":"variacao_mensal_pct","fmt":"pct"},     col=10,col_span=3,row=1,row_span=2),
        e("14_servico_k05_cat",   "SERVICO_K05_CAT",   "KPI","Maior Categoria",     "14_servico_k00_kpis.json",{"chave":"maior_categoria","fmt":"str"},          col=13,col_span=4,row=1,row_span=2),
        e("14_servico_r01_uf",    "SERVICO_R01_UF",    "HL","Por UF",              "14_servico_r01_por_uf.csv",{"label":"uf","value":"spend"},                  col=1, col_span=6,row=3,row_span=7,zoho="NFE"),
        e("14_servico_r02_mes",   "SERVICO_R02_MES",   "GB","Por Mês",             "14_servico_r02_por_mes.csv",{"x":"mesano","y":"spend","color":"#2563eb"},   col=7, col_span=5,row=3,row_span=7,zoho="NFE"),
        e("14_servico_r03_cat",   "SERVICO_R03_CAT",   "T","Por Categoria",        "14_servico_r03_por_categoria.csv",{"colunas":[{"key":"categoria","cls":"nm"},{"key":"spend","cls":"num","fmt":"brl"},{"key":"pct","cls":"num"}]},col=12,col_span=5,row=3,row_span=7,zoho="NFE"),
        e("14_servico_r04_forn",  "SERVICO_R04_FORN",  "T","Fornecedores Serviços","14_servico_r04_por_fornecedor.csv",{"colunas":[{"key":"fornecedor","cls":"nm"},{"key":"categoria"},{"key":"spend","cls":"num","fmt":"brl"},{"key":"pct","cls":"num"}]},col=1,col_span=16,row=10,row_span=6,zoho="NFE"),
        # Tipo B
        ep("14_servico_r05_cat5", "SERVICO_R05_CAT5",  "T","Detalhe por CAT5",    "14_servico_r05_por_cat5.csv",{"colunas":[{"key":"cat5","cls":"nm"},{"key":"cat3"},{"key":"spend","cls":"num","fmt":"brl"},{"key":"pct","cls":"num"}]},col_span=16,row_span=7),
    ]
}

# ── 15_dados ──────────────────────────────────────────────────────────────────
IDX_15 = {
    "aba":"15_dados","data_page":"qualidade","label":"Dados",
    "grid":{"colunas":16,"row_height_px":40},
    "elementos":[
        e("15_dados_k01_linhas",  "DADOS_K01_LINHAS",  "KPI","Linhas Analisadas",    "15_dados_k00_kpis.json",{"chave":"linhas_total_nfe","fmt":"num"},                col=1, col_span=3,row=1,row_span=2,zoho="NFE"),
        e("15_dados_k02_fontes",  "DADOS_K02_FONTES",  "KPI","Fontes OK",            "15_dados_k00_kpis.json",{"chave":"fontes_ok","fmt":"num","state":"ok"},          col=4, col_span=3,row=1,row_span=2),
        e("15_dados_k03_total",   "DADOS_K03_TOTAL",   "KPI","Fontes Total",         "15_dados_k00_kpis.json",{"chave":"fontes_total","fmt":"num"},                    col=7, col_span=3,row=1,row_span=2),
        e("15_dados_k04_sc",      "DADOS_K04_SC",      "KPI","Linhas Sem Cotação",   "15_dados_k00_kpis.json",{"chave":"linhas_sem_cotacao","fmt":"num","state":"warn"},col=10,col_span=3,row=1,row_span=2),
        e("15_dados_k05_pct",     "DADOS_K05_PCT",     "KPI","% Sem Cotação",        "15_dados_k00_kpis.json",{"chave":"pct_sem_cotacao","fmt":"pct","state":"warn"},  col=13,col_span=4,row=1,row_span=2),
        e("15_dados_r01_fontes",  "DADOS_R01_FONTES",  "T","Status por Fonte",       "15_dados_r01_status_fontes.csv",{"colunas":[{"key":"arquivo","cls":"nm"},{"key":"linhas","cls":"num"},{"key":"status"}]},col=1,col_span=8,row=3,row_span=8,subtitulo="18 fontes · última extração"),
        e("15_dados_r02_sanea",   "DADOS_R02_SANEA",   "T","Fila de Saneamento",     "15_dados_r02_fila_saneamento.csv",{"colunas":[{"key":"problema","cls":"nm"},{"key":"campo","cls":"id"},{"key":"linhas","cls":"num"},{"key":"pct","cls":"num"},{"key":"impacto"}]},col=9,col_span=8,row=3,row_span=8,subtitulo="problemas de qualidade identificados"),
    ]
}

# ── Salvar todos ──────────────────────────────────────────────────────────────

INDEXES = {
    "01_resumo": IDX_01, "02_oportunidade": IDX_02, "03_categoria": IDX_03,
    "04_filial": IDX_04, "05_estoque": IDX_05, "06_fornecedor": IDX_06,
    "07_produto": IDX_07, "08_cotacao": IDX_08, "09_impacto": IDX_09,
    "10_inflacao": IDX_10, "11_fiscal": IDX_11, "12_financeiro": IDX_12,
    "13_adiantamento": IDX_13, "14_servico": IDX_14, "15_dados": IDX_15,
}


# Posições definitivas dos 22 elementos processed-only
# Formato: id -> (col, col_span, row, row_span)
PROCESSED_POSITIONS = {
    "02_oportunidade_r02_por_cat":  (1, 16, 18, 4),
    "03_categoria_r04_top_forn":    (1, 16, 17, 6),
    "03_categoria_r05_top_prod":    (1, 16, 24, 6),
    "04_filial_r05_forn":           (1, 16, 13, 6),
    "06_fornecedor_r02_cat":        (1, 16, 15, 6),
    "06_fornecedor_r03_prod":       (1, 16, 22, 6),
    "07_produto_r02_pmp_cat":       (1, 16, 18, 6),
    "08_cotacao_r05_min_forn":      (1, 16, 14, 6),
    "08_cotacao_r06_rel":           (1, 16, 21, 6),
    "08_cotacao_r07_precos":        (1, 16, 28, 6),
    "08_cotacao_r08_prod":          (1, 16, 35, 6),
    "08_cotacao_r09_matriz":        (1, 16, 42, 6),
    "08_cotacao_r10_le3":           (1, 16, 49, 6),
    "09_impacto_r04_forn":          (1, 16, 16, 6),
    "09_impacto_r05_prod_min":      (1, 16, 23, 6),
    "10_inflacao_r07_forn":         (1, 16, 19, 6),
    "10_inflacao_r08_cat_prod":     (1, 16, 26, 6),
    "12_financeiro_r04_saldo":      (1, 16, 14, 6),
    "13_adiantamento_r03_mes":      (1, 16, 8, 5),
    "13_adiantamento_r04_uf":       (1, 8, 14, 5),
    "13_adiantamento_r05_cat":      (1, 16, 20, 6),
    "14_servico_r05_cat5":          (1, 16, 16, 6),
}


def main():
    total_v4 = total_proc = 0
    for folder, idx in INDEXES.items():
        # Aplicar posições aos elementos processed
        for elem in idx.get("elementos", []):
            l = elem.get("layout", {})
            if l.get("origem") == "processed" and elem["id"] in PROCESSED_POSITIONS:
                col, col_span, row, row_span = PROCESSED_POSITIONS[elem["id"]]
                l["col"] = col; l["col_span"] = col_span
                l["row"] = row; l["row_span"] = row_span
                l["visivel"] = True

        path = PROC / folder / f"{folder}_00_index.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding="utf-8")
        n_v4   = sum(1 for e in idx.get("elementos",[]) if e.get("layout",{}).get("origem")=="v4")
        n_proc = sum(1 for e in idx.get("elementos",[]) if e.get("layout",{}).get("origem")=="processed")
        total_v4 += n_v4; total_proc += n_proc
        print(f"  {folder}: {n_v4} v4 + {n_proc} processed = {n_v4+n_proc} elementos")
    print(f"\nTotal: {total_v4} v4 + {total_proc} processed = {total_v4+total_proc} elementos")
    print(f"Indexes salvos em data/processed/{{aba}}/{{aba}}_00_index.json")

if __name__ == "__main__":
    main()
