"""
audit_elements.py — mapeia todos os elementos do v4 vs data/processed/

Para cada aba:
  - Lista elementos hardcoded no pages.XXX() do v4
  - Lista arquivos existentes em data/processed/{aba}/
  - Identifica o que falta, o que está só no v4, só no processed ou nos dois

Uso: python pipeline/audit_elements.py
"""
import re, json
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[1]
V4      = ROOT / "design" / "BI Suprimentos v4.html"
PROC    = ROOT / "data" / "processed"

ABAS = [
    ("resumo",        "01_resumo"),
    ("oportunidades", "02_oportunidade"),
    ("categorias",    "03_categoria"),
    ("filiais",       "04_filial"),
    ("estoque",       "05_estoque"),
    ("forn360",       "06_fornecedor"),
    ("produtos",      "07_produto"),
    ("cotacoes",      "08_cotacao"),
    ("impacto",       "09_impacto"),
    ("inflacao",      "10_inflacao"),
    ("fiscal",        "11_fiscal"),
    ("financeiro",    "12_financeiro"),
    ("adiantamentos", "13_adiantamento"),
    ("servicos",      "14_servico"),
    ("qualidade",     "15_dados"),
]

# Mapeamento manual: quais variáveis JS o v4 usa em cada página
# Extraído da leitura do v4 (arrays JS substituíveis)
V4_JS_VARS = {
    "resumo":        ["FORN"],          # pages.resumo usa FORN para top fornecedores
    "oportunidades": ["OPP"],
    "categorias":    ["CAT_VAL","CAT_INF","CAT_TAX"],
    "filiais":       ["FILIAIS"],
    "estoque":       ["ESTOQUE"],
    "forn360":       ["FORN"],
    "produtos":      ["PRODS"],
    "cotacoes":      ["COTACOES"],
    "impacto":       [],
    "inflacao":      [],
    "fiscal":        ["FORN"],
    "financeiro":    [],
    "adiantamentos": [],
    "servicos":      [],
    "qualidade":     [],
}

# Elementos hardcoded por página (identificados na leitura do v4)
V4_HARDCODED = {
    "resumo": [
        ("kpis",              "KPI",  "8 KPI cards com valores monetários/percentuais"),
        ("tendencia_mensal",  "GL",   "SVG polyline com 12 pontos mensais"),
        ("por_negocio",       "HL",   "Hbar: Cozinha/Escola/Hospital/Presídio/Merenda/CD"),
        ("top_categorias",    "T",    "Tabela: Proteínas/Alimentos/Laticínios/Hortifruti..."),
        ("top_fornecedores",  "T",    "Tabela lê de FORN (já substituído)"),
        ("alertas",           "AL",   "Lista de alertas (regras — sem arquivo de dados)"),
        ("geo_nne",           "HL",   "Hbar UFs Norte/Nordeste"),
        ("geo_sse",           "HL",   "Hbar UFs Sul/Sudeste"),
        ("resumo_negocios",   "T",    "Tabela por negócio com CP e impacto"),
        ("resumo_filial",     "T",    "Tabela top 8 filiais"),
        ("cat_uf",            "MX",   "Heatmap CAT2 × UF"),
    ],
    "oportunidades": [
        ("kpis",             "KPI", "6 KPI cards"),
        ("matriz_prioridade","MX",  "Matriz 3×3 impacto × esforço"),
        ("por_tipo",         "HL",  "Hbar 6 tipos de oportunidade"),
        ("por_uf",           "HL",  "Hbar por UF"),
        ("tabela_principal", "TE",  "Tabela lê de OPP (já substituído)"),
    ],
    "categorias": [
        ("kpis",         "KPI", "6 KPI cards contextuais"),
        ("cascata",      "TB",  "5 colunas de drilldown leem CAT_VAL/CAT_INF/CAT_TAX"),
        ("cat2_por_mes", "GL",  "Gráfico 4 séries CAT2 × mês"),
        ("cat2_por_uf",  "MX",  "Heatmap CAT2 × UF"),
        ("top_forn_cat", "T",   "Top fornecedores na categoria"),
        ("top_prod_cat", "T",   "Top produtos na categoria"),
    ],
    "filiais": [
        ("kpis",           "KPI","8 KPI cards"),
        ("ranking",        "HL", "Hbar ranking filiais, lê FILIAIS"),
        ("filial_negocio", "MX", "Heatmap filial × negócio"),
        ("tabela_filiais", "T",  "Tabela completa, lê FILIAIS"),
        ("filial_cat",     "T",  "Filial × categoria"),
        ("filial_mes",     "GL", "Gráfico top 3 filiais × mês"),
    ],
    "estoque": [
        ("kpis",           "KPI","8 KPI cards"),
        ("dias_por_filial", "HL","Hbar dias de estoque, lê ESTOQUE"),
        ("entradas_saidas", "GB","Barras agrupadas, lê ESTOQUE"),
        ("tabela_estoque",  "T", "Tabela movimentação, lê ESTOQUE"),
        ("por_grupo",       "T", "Estoque por grupo produto"),
        ("compras_cmv",     "T", "Compras × CMV por filial"),
    ],
    "forn360": [
        ("kpis",         "KPI","6 KPI cards"),
        ("tagbar",       "TB", "Filtros rápidos"),
        ("tabela_forn",  "TE", "Tabela expansível, lê FORN"),
    ],
    "produtos": [
        ("kpis",         "KPI","6 KPI cards"),
        ("tagbar",       "TB", "Filtros rápidos"),
        ("tabela_prods", "TE", "Tabela expansível com spark, lê PRODS"),
    ],
    "cotacoes": [
        ("kpis",               "KPI","8 KPI cards"),
        ("cobertura_mes",      "GE", "Barras empilhadas 0/1/2/3/4+ cotações"),
        ("cobertura_curva",    "MX", "Matriz curva × faixas cotação"),
        ("cobertura_cat_mes",  "GL", "Gráfico 4 séries categoria × mês"),
        ("cobertura_uf",       "T",  "Tabela UF com cobertura %"),
        ("consulta_precos",    "T",  "Tabela consulta preços, lê COTACOES"),
        ("cotacoes_produto",   "T",  "Tabela cotações por produto, lê COTACOES"),
        ("matriz_produto_mes", "T",  "Matriz produto × mês # e MIN"),
        ("min_forn",           "T",  "MIN cotação por fornecedor"),
        ("min_le3",            "T",  "MIN cotação ≤ 3 concorrentes"),
        ("relatorio",          "T",  "Relatório completo de cotações"),
    ],
    "impacto": [
        ("kpis",         "KPI","6 KPI cards"),
        ("nacional_mes", "GB", "Barras impacto por mês"),
        ("por_uf",       "HL", "Hbar impacto por UF"),
        ("top_ids",      "T",  "Tabela top IDs por IMP_COT"),
        ("forn_nao_esc", "T",  "Fornecedores mais baratos não escolhidos"),
        ("prod_min_cot", "T",  "Produtos × MIN COT"),
    ],
    "inflacao": [
        ("kpis",         "KPI","6 KPI cards"),
        ("cat_mes_pct",  "GL", "Gráfico % por CAT × mês"),
        ("mes_rs",       "GB", "Barras R$ por mês"),
        ("top_inflacao", "HL", "Hbar top produtos inflação"),
        ("top_deflacao", "HL", "Hbar top produtos deflação"),
        ("nacional_cat", "T",  "Tabela nacional por categoria"),
        ("por_uf",       "T",  "Tabela por UF"),
        ("prod_cat",     "T",  "Produto × categoria"),
        ("por_forn",     "T",  "Por fornecedor"),
    ],
    "fiscal": [
        ("kpis",        "KPI","5 KPI cards"),
        ("matriz",      "MX", "Matriz valor × regime fiscal"),
        ("fila",        "T",  "Fila fiscal priorizada"),
        ("tabela_forn", "T",  "Fornecedores detalhe fiscal, lê FORN"),
    ],
    "financeiro": [
        ("kpis",         "KPI","5 KPI cards"),
        ("timeline",     "GB", "Timeline semanal 8 semanas"),
        ("por_forn",     "T",  "CP por fornecedor"),
    ],
    "adiantamentos": [
        ("kpis",        "KPI","5 KPI cards"),
        ("funil",       "FU", "Funil de conciliação"),
        ("por_empresa", "HL", "Hbar por empresa"),
        ("tabela_ad",   "T",  "Tabela detalhada adiantamentos"),
    ],
    "servicos": [
        ("kpis",       "KPI","6 KPI cards"),
        ("por_uf",     "HL", "Hbar por UF"),
        ("por_mes",    "GB", "Barras por mês"),
        ("por_cat",    "T",  "Tabela por categoria"),
        ("por_forn",   "T",  "Tabela fornecedores"),
        ("por_cat5",   "T",  "Detalhe por CAT5"),
    ],
    "qualidade": [
        ("kpis",         "KPI","6 KPI cards"),
        ("status_fontes","T",  "Tabela status das 18 fontes"),
        ("saneamento",   "T",  "Fila de saneamento"),
    ],
}

def get_processed_files(folder):
    p = PROC / folder
    if not p.exists(): return []
    return sorted(f.stem for f in p.iterdir() if f.suffix in (".csv",".json") and f.stem != "manifest")

def load_index(folder):
    p = PROC / folder / f"{folder}_00_index.json"
    if not p.exists(): return {}
    import json
    return json.loads(p.read_text(encoding="utf-8"))

def main():
    print("=" * 80)
    print("AUDITORIA DE ELEMENTOS: v4.html vs data/processed/")
    print("=" * 80)

    total_v4_only   = 0
    total_proc_only = 0
    total_both      = 0
    total_rule_based = 0

    rows_report = []

    for page_key, folder in ABAS:
        hardcoded     = V4_HARDCODED.get(page_key, [])
        js_vars       = V4_JS_VARS.get(page_key, [])
        proc_files    = get_processed_files(folder)
        index         = load_index(folder)
        index_rels    = {r.get("id",""):r for r in index.get("relatorios",[])}

        # Arquivos processed sem elemento no v4
        hc_ids = {hc[0] for hc in hardcoded}
        # Mapear proc_files para identificadores de elemento
        # Remover kpis e index da lista
        data_files = [f for f in proc_files
                      if not f.endswith("_k00_kpis") and not f.endswith("_00_index")]

        print(f"\n{'─'*70}")
        print(f"  {folder}  [{page_key}]")
        print(f"{'─'*70}")
        print(f"  {'ELEMENTO':<35} {'TIPO':<6} {'V4':<10} {'PROCESSED':<12} {'AÇÃO'}")
        print(f"  {'─'*35} {'─'*6} {'─'*10} {'─'*12} {'─'*20}")

        # 1. Elementos hardcoded no v4
        for elem_id, tipo, desc in hardcoded:
            if elem_id in ("alertas","cascata","tagbar"):
                # Rule-based ou estrutural — sem arquivo de dados
                status_v4   = "✓ hardcoded"
                status_proc = "rule-based"
                acao        = "sem arquivo"
                total_rule_based += 1
            elif elem_id in ("tabela_prods","tabela_forn","tabela_ad","tabela_filiais","ranking"):
                # Já lê de array JS substituível
                status_v4   = "✓ usa array JS"
                # Procurar arquivo correspondente em processed
                candidates = [f for f in data_files if elem_id.split("_")[-1] in f or tipo.lower() in f]
                status_proc = "✓ " + candidates[0] if candidates else "⚠ verificar"
                acao        = "ARRAY→JS ok" if candidates else "criar arquivo"
                total_both += 1
            else:
                # Hardcoded mas tem/deveria ter arquivo
                full_id = f"{folder}_{tipo.lower()}_{elem_id}" if tipo != "KPI" else f"{folder}_k00_kpis"
                # Procurar correspondente em data_files
                match = next((f for f in data_files
                               if elem_id in f or f.endswith(elem_id)
                               or any(p in f for p in elem_id.split("_"))), None)
                status_v4   = "✓ hardcoded"
                if match:
                    status_proc = f"✓ {match}"
                    acao        = "CONECTAR"
                    total_both  += 1
                else:
                    status_proc = "✗ falta"
                    acao        = "CRIAR+CONECTAR"
                    total_v4_only += 1

            rows_report.append((folder, elem_id, tipo, status_v4, status_proc, acao))
            print(f"  {elem_id:<35} {tipo:<6} {status_v4:<10} {status_proc:<30} {acao}")

        # 2. Arquivos em processed sem elemento no v4
        v4_elem_names = {hc[0] for hc in hardcoded}
        for fname in data_files:
            # Verificar se há correspondência com algum elemento do v4
            has_match = any(
                hc[0] in fname or fname.endswith(hc[0]) or
                any(p in fname for p in hc[0].split("_"))
                for hc in hardcoded
            )
            if not has_match and "kpis" not in fname and "index" not in fname:
                rows_report.append((folder, fname, "?", "✗ não tem", f"✓ {fname}", "ADICIONAR AO V4"))
                print(f"  {fname:<35} {'?':<6} {'✗ não tem':<10} {'✓ '+fname:<30} {'ADICIONAR AO V4'}")
                total_proc_only += 1

    print(f"\n{'='*80}")
    print(f"RESUMO GERAL")
    print(f"{'='*80}")
    print(f"  Nos dois (conectar):          {total_both:>4}")
    print(f"  Só no v4 (criar+conectar):    {total_v4_only:>4}")
    print(f"  Só em processed (adicionar):  {total_proc_only:>4}")
    print(f"  Rule-based (sem arquivo):     {total_rule_based:>4}")
    print(f"  TOTAL de ações:               {total_both+total_v4_only+total_proc_only:>4}")

    # Salvar relatório
    out = Path(__file__).parent / "audit_report.json"
    import json
    with out.open("w", encoding="utf-8") as f:
        json.dump(rows_report, f, ensure_ascii=False, indent=2)
    print(f"\nRelatório salvo em: {out}")

if __name__ == "__main__":
    main()
