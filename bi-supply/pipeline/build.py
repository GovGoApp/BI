"""Constrói o dashboard HTML final em dist/index.html.

Lê data/processed/{aba}/*.csv|json + dashboard/static/ + dashboard/tabs/*.yml
e gera dist/index.html auto-contido (dados embutidos como JSON).

Uso:
    python pipeline/build.py
    python pipeline/build.py --tab resumo   # só uma aba (debug)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT     = Path(__file__).resolve().parents[1]
PROC     = ROOT / "data" / "processed"
STATIC   = ROOT / "dashboard" / "static"
TABS_DIR = ROOT / "dashboard" / "tabs"
DIST     = ROOT / "dist"
DESIGN   = ROOT / "design" / "BI Suprimentos v4.html"


# ── Leitores ──────────────────────────────────────────────────────────────────

def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))


def read_json(path: Path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_processed(aba_folder: str) -> dict:
    """Carrega todos os arquivos CSV/JSON de uma pasta de aba."""
    folder = PROC / aba_folder
    data   = {}
    if not folder.exists():
        return data
    for p in sorted(folder.iterdir()):
        if p.suffix == ".csv":
            data[p.stem] = read_csv(p)
        elif p.suffix == ".json":
            data[p.stem] = read_json(p)
    return data


# ── CSS / JS ──────────────────────────────────────────────────────────────────

def load_static() -> dict[str, str]:
    css = (STATIC / "style.css").read_text(encoding="utf-8") if (STATIC / "style.css").exists() else ""
    js  = (STATIC / "dashboard.js").read_text(encoding="utf-8") if (STATIC / "dashboard.js").exists() else ""
    return {"css": css, "js": js}


# ── ABAS ──────────────────────────────────────────────────────────────────────

ABAS = [
    ("resumo",        "01_resumo",       "Resumo"),
    ("oportunidades", "02_oportunidade",  "Oportunidades"),
    ("categorias",    "03_categoria",     "Categorias"),
    ("filiais",       "04_filial",        "Filiais"),
    ("estoque",       "05_estoque",       "Estoque"),
    ("forn360",       "06_fornecedor",    "Fornecedor"),
    ("produtos",      "07_produto",       "Produtos"),
    ("cotacoes",      "08_cotacao",       "Cotações"),
    ("impacto",       "09_impacto",       "Impacto"),
    ("inflacao",      "10_inflacao",      "Inflação"),
    ("fiscal",        "11_fiscal",        "Fiscal"),
    ("financeiro",    "12_financeiro",    "Financeiro"),
    ("adiantamentos", "13_adiantamento",  "Adiantamentos"),
    ("servicos",      "14_servico",       "Serviços"),
    ("qualidade",     "15_dados",         "Dados"),
]

# Mapa de formatação por chave de KPI
KPI_FMT = {
    "total_comprado_operacional": "brl",
    "total_comprado_periodo": "brl",
    "crescimento_yoy_pct": "pct",
    "fornecedores_ativos": "num",
    "pct_com_cotacao": "pct",
    "imp_cot_total": "brl",
    "cp_aberto": "brl",
    "cp_titulos": "num",
    "ad_pendente": "brl",
    "ids_unicos": "num",
    "produtos_unicos": "num",
}


# ── Renderizadores de elemento ────────────────────────────────────────────────

def render_kpi_card(key: str, val, label: str, state: str = "", delta: str = "") -> str:
    fmt = KPI_FMT.get(key, "auto")
    if fmt == "brl":    disp = f"R$ {_fmt_num(val)}"
    elif fmt == "pct":  disp = f"{float(val or 0):+.1f}%"
    elif fmt == "num":  disp = _fmt_num(val)
    else:               disp = _fmt_auto(val)

    state_cls = f" {state}" if state else ""
    delta_html = f'<div class="delta"><b>{delta}</b></div>' if delta else ""
    return f"""<div class="kpi{state_cls}">
  <div class="lab">{label}</div>
  <div class="val">{disp}</div>
  {delta_html}
</div>"""


def _fmt_num(v) -> str:
    try:
        n = float(v)
        if n >= 1e9:  return f"{n/1e9:.1f}B"
        if n >= 1e6:  return f"{n/1e6:.1f}M"
        if n >= 1e3:  return f"{n/1e3:.0f}K"
        return f"{n:,.0f}".replace(",", ".")
    except:
        return str(v)


def _fmt_auto(v) -> str:
    try:
        n = float(v)
        if abs(n) >= 1e6: return f"R$ {n/1e6:.1f}M"
        if abs(n) >= 1e3: return f"R$ {n/1e3:.0f}K"
        return f"R$ {n:,.0f}".replace(",", ".")
    except:
        return str(v)


def render_kpis_bar(kpis: dict, definitions: list[dict]) -> str:
    cards = []
    for d in definitions:
        key   = d.get("chave","")
        label = d.get("titulo","")
        val   = kpis.get(key, "—")
        state = d.get("state","")
        cards.append(render_kpi_card(key, val, label, state))
    return f'<div class="kpis">{" ".join(cards)}</div>'


def render_table(rows: list[dict], cols: list[dict] | None = None,
                 table_id: str = "", max_rows: int = 20) -> str:
    if not rows:
        return '<p class="muted" style="padding:12px">Sem dados</p>'

    display_cols = cols or [{"key": k, "label": k} for k in rows[0].keys()]
    header = "".join(f'<th>{c.get("label",c.get("key",""))}</th>' for c in display_cols)

    body_rows = []
    for r in rows[:max_rows]:
        cells = []
        for c in display_cols:
            k   = c.get("key","")
            v   = r.get(k, "")
            cls = c.get("cls","")
            cells.append(f'<td class="{cls}">{v}</td>')
        body_rows.append(f'<tr>{"".join(cells)}</tr>')

    tid = f' id="{table_id}"' if table_id else ""
    return f"""<div style="overflow-x:auto">
<table class="table"{tid}>
  <thead><tr>{header}</tr></thead>
  <tbody>{"".join(body_rows)}</tbody>
</table></div>"""


def render_hbar_list(rows: list[dict], label_key: str, value_key: str,
                     max_rows: int = 10, color: str = "") -> str:
    if not rows:
        return ""
    max_val = max(float(r.get(value_key, 0) or 0) for r in rows) or 1
    color_style = f"background:{color}" if color else ""
    items = []
    for r in rows[:max_rows]:
        lbl = r.get(label_key, "")
        val = float(r.get(value_key, 0) or 0)
        pct = val / max_val * 100
        disp = _fmt_auto(val)
        items.append(f"""<div class="hbar">
  <div class="lab">{lbl}</div>
  <div class="bar" data-pct="{pct:.1f}"><span style="{color_style}"></span></div>
  <div class="v">{disp}</div>
</div>""")
    return "".join(items)


def render_section(title: str, subtitle: str, content: str) -> str:
    return f"""<div class="card section">
  <div class="card-h"><h3>{title}</h3><span class="sub">{subtitle}</span></div>
  <div class="card-b">{content}</div>
</div>"""


# ── Construtores de aba ───────────────────────────────────────────────────────

def build_aba_resumo(data: dict) -> str:
    kpis = data.get("01_resumo_k00_kpis", {})
    defs = [
        {"chave":"total_comprado_operacional","titulo":"Total Comprado"},
        {"chave":"crescimento_yoy_pct","titulo":"Crescimento YoY","state":"ok"},
        {"chave":"fornecedores_ativos","titulo":"Fornecedores"},
        {"chave":"pct_com_cotacao","titulo":"% com Cotação","state":"warn"},
        {"chave":"imp_cot_total","titulo":"Oportunidade IMP_COT","state":"warn"},
        {"chave":"cp_aberto","titulo":"CP em Aberto"},
        {"chave":"ad_pendente","titulo":"AD Pendente","state":"warn"},
        {"chave":"ids_unicos","titulo":"IDs Únicos"},
    ]
    kpis_html = render_kpis_bar(kpis, defs)

    por_mes  = data.get("01_resumo_r01_por_mes", [])
    neg      = data.get("01_resumo_r02_por_negocio", [])
    top_cat  = data.get("01_resumo_r03_top_categoria", [])
    top_forn = data.get("01_resumo_r04_top_fornecedor", [])
    geo_nne  = data.get("01_resumo_r06_geo_nne", [])
    geo_sse  = data.get("01_resumo_r07_geo_sse", [])
    por_fil  = data.get("01_resumo_r08_por_filial", [])

    # Série mensal → sparkline data
    mes_data = json.dumps([{"x": r.get("mesano",""), "y": float(r.get("spend",0) or 0)} for r in por_mes])

    # Tabela top categorias
    top_cat_html = render_table(top_cat, [
        {"key":"cat2","label":"Categoria"},
        {"key":"spend","label":"Spend R$","cls":"num"},
        {"key":"pct","label":"%","cls":"num"},
        {"key":"imp_cot","label":"IMP_COT","cls":"num"},
        {"key":"inflacao_media_pct","label":"Inflação %","cls":"num"},
    ], max_rows=10)

    # Tabela top fornecedores
    top_forn_html = render_table(top_forn, [
        {"key":"fornecedor","label":"Fornecedor","cls":"nm"},
        {"key":"curva","label":"Curva"},
        {"key":"spend","label":"Spend R$","cls":"num"},
        {"key":"pct","label":"%","cls":"num"},
        {"key":"imp_cot","label":"IMP_COT","cls":"num"},
        {"key":"cp_aberto","label":"CP Aberto","cls":"num"},
    ], max_rows=15)

    # Por filial
    fil_html = render_table(por_fil, [
        {"key":"nome","label":"Filial","cls":"nm"},
        {"key":"negocio","label":"Negócio"},
        {"key":"uf","label":"UF"},
        {"key":"spend","label":"Spend","cls":"num"},
        {"key":"pct","label":"%","cls":"num"},
        {"key":"imp_cot","label":"IMP_COT","cls":"num"},
    ], max_rows=8)

    return f"""
{kpis_html}

<div class="grid" style="grid-template-columns:2fr 1fr;gap:10px;margin-top:10px">
  {render_section("Evolução Mensal","12 meses",
    f'<canvas id="chart-resumo-mes" class="spark" style="height:80px" data-series=\'{mes_data}\'></canvas>')}
  {render_section("Por Tipo de Negócio","spend",render_hbar_list(neg,"negocio","spend"))}
</div>

<div class="grid" style="grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
  {render_section("Top Categorias (CAT2)","spend + inflação + impacto",top_cat_html)}
  {render_section("Top Fornecedores","curva ABC + CP",top_forn_html)}
</div>

<div class="grid" style="grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px">
  {render_section("Geo — N e NE","",render_hbar_list(geo_nne,"uf","spend"))}
  {render_section("Geo — S e SE","",render_hbar_list(geo_sse,"uf","spend"))}
  {render_section("Por Filial (top 8)","",fil_html)}
</div>
"""


def build_aba_generica(data: dict, page_key: str, folder: str) -> str:
    """Aba genérica: mostra KPIs + lista todos os relatórios disponíveis."""
    index = data.get(f"{folder}_00_index", {})
    kpis  = data.get(f"{folder}_k00_kpis", {})
    label = index.get("label", page_key)

    # KPIs
    kpis_defs = index.get("kpis", [])
    kpis_html = ""
    if kpis_defs and kpis:
        cards = []
        for d in kpis_defs[:8]:
            key = d.get("chave",""); val = kpis.get(key,"—")
            cards.append(render_kpi_card(key, val, d.get("titulo",key)))
        kpis_html = f'<div class="kpis">{"".join(cards)}</div>'

    # Relatórios
    rels = index.get("relatorios", [])
    secs = []
    for rel in rels:
        stem = rel.get("arquivo","").replace(".csv","").replace(".json","")
        rows = data.get(stem)
        if not rows:
            continue
        tipo  = rel.get("tipo","T")
        title = rel.get("titulo","")
        desc  = rel.get("descricao","")

        if isinstance(rows, list) and len(rows) > 0:
            if tipo in ("HL",):
                cols = list(rows[0].keys())
                val_key = cols[-1] if len(cols)>1 else cols[0]
                lbl_key = cols[0]
                content = render_hbar_list(rows, lbl_key, val_key)
            else:
                cols_def = [{"key":k,"label":k} for k in list(rows[0].keys())[:8]]
                content  = render_table(rows, cols_def, max_rows=15)
        elif isinstance(rows, dict):
            items = [f"<tr><td><b>{k}</b></td><td class='num'>{v}</td></tr>"
                     for k,v in rows.items() if k not in ("aba","data_page","label")]
            content = f'<table class="table"><tbody>{"".join(items)}</tbody></table>'
        else:
            continue

        secs.append(render_section(title, desc[:80], content))

    return f"""
{kpis_html}
<div style="margin-top:10px;display:flex;flex-direction:column;gap:10px">
{"".join(secs) or '<p class="muted" style="padding:12px">Dados em processamento.</p>'}
</div>
"""


ABA_BUILDERS = {
    "resumo": build_aba_resumo,
}


def build_page(page_key: str, folder: str, label: str) -> str:
    data     = load_processed(folder)
    builder  = ABA_BUILDERS.get(page_key)
    if builder:
        body = builder(data)
    else:
        body = build_aba_generica(data, page_key, folder)
    return f'<div class="page" data-page="{page_key}">{body}</div>'


# ── Montagem do HTML ──────────────────────────────────────────────────────────

def build_html(pages_html: str, static: dict, generated_at: str) -> str:
    tabs_nav = "".join(
        f'<button class="tab{" active" if i==0 else ""}" data-page="{p}">{label}</button>'
        for i,(p,_,label) in enumerate(ABAS)
    )

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8"/>
<title>BI de Suprimentos</title>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
{static['css']}

/* chart canvas */
canvas{{display:block;width:100%}}

/* BC chart */
.bc-wrap{{display:flex;gap:3px;align-items:flex-end;width:100%}}
.bc-col{{display:flex;flex-direction:column;align-items:center;flex:1;gap:3px}}
.bc-bar-wrap{{display:flex;align-items:flex-end;width:100%}}
.bc-bar{{width:100%;border-radius:3px 3px 0 0;min-height:2px;transition:opacity .15s}}
.bc-bar:hover{{opacity:.8}}
.bc-label{{font-size:9px;color:var(--muted);text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}}
</style>
</head>
<body>
<div class="app">

  <div class="topbar">
    <div class="brand">
      <div class="mark">BI</div>
      <div>
        <h1>BI de Suprimentos</h1>
        <div class="sub">Gerado em {generated_at}</div>
      </div>
    </div>
    <div class="search">
      <svg width="14" height="14" viewBox="0 0 20 20" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#94a3b8" stroke-width="1.5"/><path d="m13 13 3.5 3.5" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round"/></svg>
      <input type="text" placeholder="Buscar… " />
      <kbd>⌘K</kbd>
    </div>
  </div>

  <nav class="tabs" id="tabs">{tabs_nav}</nav>

  <div id="pages">
{pages_html}
  </div>

</div>
<script>
{static['js']}

// Sparklines após carregamento
document.querySelectorAll('canvas[data-series]').forEach(c => {{
  try {{
    const s = JSON.parse(c.dataset.series || '[]');
    const vals = s.map(p => p.y||p||0);
    renderSparkline(c, vals, 'var(--blue)');
  }} catch(e) {{}}
}});

// Barras proporcionais
renderBars(document);
</script>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(description="Gera dist/index.html")
    parser.add_argument("--tab", help="Gerar só uma aba (debug)")
    args = parser.parse_args(argv)

    DIST.mkdir(parents=True, exist_ok=True)
    static = load_static()
    now    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("Construindo dashboard...")
    pages_html = ""
    for page_key, folder, label in ABAS:
        if args.tab and page_key != args.tab:
            continue
        print(f"  {folder}/ ({label})")
        pages_html += build_page(page_key, folder, label) + "\n"

    html = build_html(pages_html, static, now)
    out  = DIST / "index.html"
    out.write_text(html, encoding="utf-8")

    size_kb = out.stat().st_size / 1024
    print(f"\nGerado: {out}  ({size_kb:.0f} KB)")
    print("Abrir: start dist/index.html")


if __name__ == "__main__":
    main()
