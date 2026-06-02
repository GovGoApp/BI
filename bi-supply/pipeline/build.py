"""Constrói dist/index.html a partir de data/processed/ + dashboard/static/.

Uso:
    python pipeline/build.py
    python pipeline/build.py --tab resumo
"""
from __future__ import annotations
import argparse, csv, json, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[1]
PROC   = ROOT / "data" / "processed"
STATIC = ROOT / "dashboard" / "static"
DIST   = ROOT / "dist"

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

# ── I/O ───────────────────────────────────────────────────────────────────────

def rc(path):
    if not path.exists(): return []
    with path.open(encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))

def rj(path):
    if not path.exists(): return {}
    return json.loads(path.read_text(encoding="utf-8"))

def load(folder):
    d = {}
    p = PROC / folder
    if not p.exists(): return d
    for f in sorted(p.iterdir()):
        d[f.stem] = rc(f) if f.suffix==".csv" else rj(f)
    return d

def flt(v):
    try: return float(str(v).replace(",","."))
    except: return 0.0

def fmtBRL(v):
    n = flt(v)
    if abs(n)>=1e6: return f"R$ {n/1e6:.1f}M"
    if abs(n)>=1e3: return f"R$ {n/1e3:.0f}K"
    return f"R$ {n:,.0f}".replace(",",".")

def fmtNum(v):
    n = flt(v)
    if n>=1e6: return f"{n/1e6:.1f}M"
    if n>=1e3: return f"{n/1e3:.0f}K"
    return f"{n:,.0f}".replace(",",".")

def fmtPct(v): return f"{flt(v):+.1f}%"

# ── Helpers de componente ─────────────────────────────────────────────────────

def zoho_badge(name):
    return (f'<span style="font-size:10px;font-weight:700;color:var(--blue);'
            f'background:var(--blue-soft);border:1px solid #bfdbfe;border-radius:4px;'
            f'padding:1px 6px;letter-spacing:.3px;white-space:nowrap">ZOHO · {name}</span>')

def sec(title, content, subtitle="", zoho="", meta_extra=""):
    meta = ""
    if zoho or meta_extra:
        meta = f'<div class="meta">{zoho_badge(zoho) if zoho else ""}{meta_extra}</div>'
    sub = f'<div class="sub">{subtitle}</div>' if subtitle else ""
    return (f'<div class="card section"><div class="card-h">'
            f'<div><h3>{title}</h3>{sub}</div>{meta}</div>'
            f'<div class="card-b">{content}</div></div>')

def row2(a, b, ratio="1fr 1fr"):
    return f'<div style="display:grid;grid-template-columns:{ratio};gap:10px;margin-top:10px">{a}{b}</div>'

def row3(a, b, c):
    return f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:10px">{a}{b}{c}</div>'

def kpi(label, val_str, state="", delta_html=""):
    s = f" {state}" if state else ""
    return (f'<div class="kpi{s}"><div class="lab">{label}</div>'
            f'<div class="val">{val_str}</div>{delta_html}</div>')

def delta(val_str, ctx, direction=""):
    d = f" {direction}" if direction else ""
    return f'<div class="delta{d}"><b>{val_str}</b><span>{ctx}</span></div>'

def pill(text, color="k"):  return f'<span class="pill {color}">{text}</span>'
def badge(text, cls="rc"):  return f'<span class="badge {cls}">{text}</span>'
def curva(c):               return f'<span class="curva {c}">{c}</span>'

def hbar_item(label, val, max_val, sub="", color=""):
    pct = max(0, min(100, flt(val)/max_val*100)) if max_val else 0
    col = f" {color}" if color else ""
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    return (f'<div class="hbar"><div class="lab">{label}{sub_html}</div>'
            f'<div class="bar{col}"><span style="width:{pct:.1f}%"></span></div>'
            f'<div class="v">{fmtBRL(val)}</div></div>')

def hbar_list(rows, label_key, val_key, max_rows=10, sub_key="", color=""):
    if not rows: return ""
    max_v = max((flt(r.get(val_key,0)) for r in rows), default=1) or 1
    return "".join(
        hbar_item(r.get(label_key,""), r.get(val_key,0), max_v,
                  sub=r.get(sub_key,"") if sub_key else "", color=color)
        for r in rows[:max_rows]
    )

def table(rows, cols, max_rows=15):
    if not rows: return '<p class="muted" style="padding:10px">Sem dados</p>'
    ths = "".join(f'<th>{c["label"]}</th>' for c in cols)
    trs = ""
    for r in rows[:max_rows]:
        tds = ""
        for c in cols:
            v   = r.get(c["key"], "")
            cls = c.get("cls","")
            tds += f'<td class="{cls}">{v}</td>'
        trs += f"<tr>{tds}</tr>"
    return (f'<div style="overflow-x:auto"><table class="table">'
            f'<thead><tr>{ths}</tr></thead><tbody>{trs}</tbody></table></div>')

def heatmap(rows, row_key, col_key, val_key, fmt_fn=None):
    """Gera matriz com células s1-s5."""
    if not rows: return ""
    fmt = fmt_fn or (lambda v: f"{flt(v)/1e6:.1f}" if flt(v)>=1e6 else f"{flt(v)/1e3:.0f}K")
    row_vals = list(dict.fromkeys(r[row_key] for r in rows if r[row_key]))
    col_vals = list(dict.fromkeys(r[col_key] for r in rows if r[col_key]))
    lookup = {(r[row_key],r[col_key]):flt(r[val_key]) for r in rows}
    max_v  = max(lookup.values(), default=1) or 1

    def intensity(v):
        p = v/max_v
        if p<0.2:  return "s1"
        if p<0.4:  return "s2"
        if p<0.6:  return "s3"
        if p<0.8:  return "s4"
        return "s5"

    cols_css = f"160px repeat({len(col_vals)},1fr)"
    head = '<div class="cell head"></div>' + "".join(
        f'<div class="cell head">{c}</div>' for c in col_vals)
    body = ""
    for rv in row_vals:
        body += f'<div class="cell head" style="justify-content:flex-start;font-size:11px;font-weight:600;color:var(--ink);text-transform:none">{rv}</div>'
        for cv in col_vals:
            v  = lookup.get((rv,cv),0)
            si = intensity(v) if v>0 else "s1"
            body += f'<div class="cell {si}" title="{fmtBRL(v)}">{fmt(v) if v>0 else "—"}</div>'

    return (f'<div class="matrix" style="display:grid;grid-template-columns:{cols_css};gap:4px">'
            f'{head}{body}</div>')

def chart_container(chart_id, chart_type, data, height=160, color="#2563eb"):
    """Div que o dashboard.js vai renderizar como SVG."""
    data_json = json.dumps(data, ensure_ascii=False)
    return (f'<div id="{chart_id}" data-chart="{chart_type}" '
            f'data-color="{color}" data-height="{height}" '
            f'style="width:100%;height:{height}px" '
            f'data-series=\'{data_json}\'></div>')

def alerts_html(alert_list):
    rows = ""
    for a in alert_list:
        dot_cls = a.get("cls","")
        rows += (f'<div class="alert-row {dot_cls}">'
                 f'<span class="dot"></span>'
                 f'<div><div class="nm">{a["title"]}</div>'
                 f'<div class="who">{a.get("who","")}</div></div>'
                 f'<div class="num">{a.get("impact","")}</div>'
                 f'{pill(a.get("area",""), "ghost")}'
                 f'</div>')
    return f'<div class="alerts">{rows}</div>' if rows else ""


# ── Regras de alerta (Resumo) ─────────────────────────────────────────────────

def compute_alerts(kpis, top_cat, top_forn):
    alerts = []
    pct_cot = flt(kpis.get("pct_com_cotacao",100))
    if pct_cot < 50:
        alerts.append({"cls":"r","title":f"{pct_cot:.1f}% das compras sem cotação",
                        "who":"Abaixo do mínimo aceitável (meta: 80%)","impact":"Alto","area":"Compras"})
    cp120 = flt(kpis.get("cp_critico_120d",0))
    if cp120 > 0:
        alerts.append({"cls":"r","title":f"R$ {cp120/1e6:.1f}M em CP com +120 dias",
                        "who":"Títulos vencidos há mais de 120 dias","impact":fmtBRL(cp120),"area":"Financeiro"})
    imp = flt(kpis.get("imp_cot_total",0))
    if imp > 0:
        alerts.append({"cls":"y","title":f"R$ {imp/1e6:.1f}M de oportunidade de cotação",
                        "who":"Compras realizadas acima do menor preço disponível","impact":fmtBRL(imp),"area":"Compras"})
    ad = flt(kpis.get("ad_pendente",0))
    if ad > 1e6:
        alerts.append({"cls":"y","title":f"R$ {ad/1e6:.1f}M em adiantamentos pendentes",
                        "who":"Status indefinido — necessita conciliação","impact":fmtBRL(ad),"area":"Financeiro"})
    return alerts


# ── Builder: RESUMO ───────────────────────────────────────────────────────────

def build_resumo(d):
    kpis     = d.get("01_resumo_k00_kpis", {})
    por_mes  = d.get("01_resumo_r01_por_mes", [])
    neg      = d.get("01_resumo_r02_por_negocio", [])
    top_cat  = d.get("01_resumo_r03_top_categoria", [])
    top_forn = d.get("01_resumo_r04_top_fornecedor", [])
    por_uf   = d.get("01_resumo_r05_por_uf", [])
    geo_nne  = d.get("01_resumo_r06_geo_nne", [])
    geo_sse  = d.get("01_resumo_r07_geo_sse", [])
    por_fil  = d.get("01_resumo_r08_por_filial", [])
    cat_uf   = d.get("01_resumo_r09_cat2_por_uf", [])

    # ── KPIs ────────────────────────────────────────────────────
    yoy  = flt(kpis.get("crescimento_yoy_pct",0))
    cards = [
        kpi("Total Comprado",   fmtBRL(kpis.get("total_comprado_operacional",0)),
            state="ok",
            delta_html=delta(fmtPct(yoy), "vs. 2024", "up" if yoy>0 else "down")),
        kpi("Fornecedores",     fmtNum(kpis.get("fornecedores_ativos",0)),
            delta_html=delta(fmtNum(kpis.get("ids_unicos",0)), "IDs únicos")),
        kpi("Produtos / IDs",   fmtNum(kpis.get("produtos_unicos",0)),
            delta_html=delta(fmtNum(kpis.get("ids_unicos",0)), "IDs analíticos")),
        kpi("% com Cotação",    f'{flt(kpis.get("pct_com_cotacao",0)):.1f}%',
            state="warn" if flt(kpis.get("pct_com_cotacao",100))<60 else "",
            delta_html=delta("meta: 80%", "cobertura de cotação", "warn")),
        kpi("Oportunidade IMP", fmtBRL(kpis.get("imp_cot_total",0)),
            state="warn",
            delta_html=delta("16,3%", "linhas acima do mínimo", "warn")),
        kpi("CP em Aberto",     fmtBRL(kpis.get("cp_aberto",0)),
            delta_html=delta(fmtNum(kpis.get("cp_titulos",0)), "títulos")),
        kpi("AD Pendente",      fmtBRL(kpis.get("ad_pendente",0)),
            state="warn" if flt(kpis.get("ad_pendente",0))>1e6 else "",
            delta_html=delta("sem conciliação", "status indefinido")),
        kpi("Risco Fiscal 2027","—",
            state="warn",
            delta_html=delta("—", "dados cadastrais pendentes")),
    ]
    kpis_html = f'<div class="kpis">{"".join(cards)}</div>'

    # ── Gráfico tendência mensal ─────────────────────────────────
    mes_data = [{"x": r.get("mesano",""), "y": flt(r.get("spend",0))} for r in por_mes]
    chart_mes = chart_container("chart-resumo-mes", "GL", mes_data, height=140)

    # ── Compras por negócio ──────────────────────────────────────
    neg_html = hbar_list(neg, "negocio", "spend", max_rows=8)

    # ── Top categorias ───────────────────────────────────────────
    def fmt_inf(row):
        v = flt(row.get("inflacao_media_pct",0))
        if abs(v)<0.1: return "—"
        return f'<span class="pill {"r" if v>20 else "y" if v>5 else "g"}">{v:+.1f}%</span>'
    def fmt_imp(row):
        v = flt(row.get("imp_cot",0))
        return fmtBRL(v) if v>0 else "—"

    cat_rows = []
    for r in top_cat[:12]:
        cat_rows.append({**r,
            "pct_fmt":    f'{flt(r.get("pct",0)):.1f}%',
            "spend_fmt":  fmtBRL(r.get("spend",0)),
            "inf_fmt":    fmt_inf(r),
            "imp_fmt":    fmt_imp(r),
        })
    cat_html = table(cat_rows, [
        {"key":"cat2",      "label":"Categoria",   "cls":"nm"},
        {"key":"spend_fmt", "label":"Spend",        "cls":"num"},
        {"key":"pct_fmt",   "label":"%",            "cls":"num"},
        {"key":"inf_fmt",   "label":"Inflação",     "cls":"num"},
        {"key":"imp_fmt",   "label":"IMP_COT",      "cls":"num"},
    ])

    # ── Top fornecedores ─────────────────────────────────────────
    forn_rows = []
    for r in top_forn[:15]:
        c = r.get("curva","")
        forn_rows.append({**r,
            "curva_html":    curva(c) if c else "—",
            "spend_fmt":     fmtBRL(r.get("spend",0)),
            "pct_fmt":       f'{flt(r.get("pct",0)):.1f}%',
            "pct_acum_fmt":  f'{flt(r.get("pct_acum",0)):.1f}%',
            "imp_fmt":       fmtBRL(r.get("imp_cot",0)) if flt(r.get("imp_cot",0))>0 else "—",
            "cp_fmt":        fmtBRL(r.get("cp_aberto",0)) if flt(r.get("cp_aberto",0))>0 else "—",
        })
    forn_html = table(forn_rows, [
        {"key":"fornecedor",   "label":"Fornecedor",   "cls":"nm"},
        {"key":"curva_html",   "label":"Curva",        "cls":""},
        {"key":"spend_fmt",    "label":"Spend",        "cls":"num"},
        {"key":"pct_fmt",      "label":"%",            "cls":"num"},
        {"key":"pct_acum_fmt", "label":"Acum.",        "cls":"num"},
        {"key":"imp_fmt",      "label":"IMP_COT",      "cls":"num"},
        {"key":"cp_fmt",       "label":"CP Aberto",    "cls":"num"},
    ])

    # ── Por filial ───────────────────────────────────────────────
    fil_rows = [{**r,
        "spend_fmt": fmtBRL(r.get("spend",0)),
        "pct_fmt":   f'{flt(r.get("pct",0)):.1f}%',
        "cot_fmt":   f'{flt(r.get("pct_com_cotacao",0)):.0f}%',
        "imp_fmt":   fmtBRL(r.get("imp_cot",0)) if flt(r.get("imp_cot",0))>0 else "—",
    } for r in por_fil[:8]]
    fil_html = table(fil_rows, [
        {"key":"nome",      "label":"Filial",    "cls":"nm"},
        {"key":"negocio",   "label":"Negócio",   "cls":"sm"},
        {"key":"uf",        "label":"UF",        "cls":""},
        {"key":"spend_fmt", "label":"Spend",     "cls":"num"},
        {"key":"pct_fmt",   "label":"%",         "cls":"num"},
        {"key":"cot_fmt",   "label":"% Cot.",    "cls":"num"},
        {"key":"imp_fmt",   "label":"IMP_COT",   "cls":"num"},
    ])

    # ── Alertas ──────────────────────────────────────────────────
    al = compute_alerts(kpis, top_cat, top_forn)
    al_html = alerts_html(al) if al else '<p class="muted" style="padding:10px;font-size:12px">Nenhum alerta crítico.</p>'

    # ── Heatmap CAT2 × UF ────────────────────────────────────────
    hm_html = heatmap(cat_uf, "cat2", "uf", "spend")

    # ── Montagem ─────────────────────────────────────────────────
    return f"""
{kpis_html}

{row2(
    sec("Evolução Mensal", chart_mes, subtitle="Spend total · últimos 12 meses", zoho="NFE"),
    sec("Por Tipo de Negócio", neg_html, zoho="NFE"),
    ratio="1.5fr 1fr"
)}

{row2(
    sec("Top Categorias (CAT2)", cat_html, zoho="NFE"),
    sec("Top Fornecedores", forn_html, zoho="CURVA ABC FORN - TOTAL · NFE")
)}

{row3(
    sec("Geo — N e NE", hbar_list(geo_nne, "uf", "spend"), zoho="NFE"),
    sec("Geo — S e SE", hbar_list(geo_sse, "uf", "spend"), zoho="NFE"),
    sec("Por Filial (top 8)", fil_html, zoho="NFE")
)}

<div style="margin-top:10px">
{sec("Alertas Executivos", al_html)}
</div>

<div style="margin-top:10px">
{sec("Categoria × UF (Heatmap)", hm_html, subtitle="Spend por CAT2 e estado", zoho="NFE")}
</div>
"""


# ── Builder genérico (abas sem builder específico) ────────────────────────────

def build_generica(d, page_key, folder):
    index  = d.get(f"{folder}_00_index", {})
    kpis   = d.get(f"{folder}_k00_kpis", {})

    kpis_cards = []
    for kd in index.get("kpis", [])[:8]:
        key = kd.get("chave",""); val = kpis.get(key,"—")
        kpis_cards.append(kpi(kd.get("titulo",key), _auto_fmt(key, val)))
    kpis_html = f'<div class="kpis">{"".join(kpis_cards)}</div>' if kpis_cards else ""

    secs = []
    for rel in index.get("relatorios", []):
        stem  = rel.get("arquivo","").replace(".csv","").replace(".json","")
        rows  = d.get(stem)
        if not rows: continue
        tipo  = rel.get("tipo","T")
        title = rel.get("titulo","")
        zoho  = _extract_zoho(rel.get("sql",""))

        if isinstance(rows, list) and rows:
            if tipo == "HL":
                cols = list(rows[0].keys())
                content = hbar_list(rows, cols[0], cols[-1] if len(cols)>1 else cols[0])
            elif tipo == "GL":
                data = [{"x":r.get(list(rows[0].keys())[0],""), "y":flt(r.get(list(rows[0].keys())[-1],0))} for r in rows]
                content = chart_container(f"chart-{stem}", "GL", data, height=120)
            elif tipo == "GB":
                data = [{"x":r.get(list(rows[0].keys())[0],""), "y":flt(r.get(list(rows[0].keys())[-1],0))} for r in rows]
                content = chart_container(f"chart-{stem}", "GB", data, height=120)
            else:
                cs = [{"key":k,"label":k,"cls":"num" if i>0 else "nm"} for i,k in enumerate(list(rows[0].keys())[:7])]
                content = table(rows, cs, max_rows=20)
        elif isinstance(rows, dict):
            items = "".join(f"<tr><td class='nm'>{k}</td><td class='num'>{v}</td></tr>"
                            for k,v in rows.items() if k not in ("aba","data_page","label","kpis_arquivo","kpis","relatorios","status","nota"))
            content = f'<table class="table"><tbody>{items}</tbody></table>' if items else ""
        else:
            continue

        if content:
            secs.append(sec(title, content, zoho=zoho))

    body = "".join(secs) or '<p class="muted" style="padding:16px">Dados em processamento.</p>'
    return f"{kpis_html}<div style='margin-top:10px;display:flex;flex-direction:column;gap:10px'>{body}</div>"


def _auto_fmt(key, val):
    if any(x in key for x in ("total","spend","cp_","ad_","imp_","valor","aberto","pendente")):
        return fmtBRL(val)
    if "pct" in key or "media" in key:
        return f"{flt(val):.1f}%"
    if any(x in key for x in ("qtd","ids","forn","linhas","count","n_","total_id")):
        return fmtNum(val)
    return str(val)

def _extract_zoho(sql):
    import re
    m = re.search(r'FROM\s+"([^"]+)"', sql or "")
    return m.group(1) if m else ""


BUILDERS = {"resumo": build_resumo}


# ── Shell HTML ────────────────────────────────────────────────────────────────

def build_html(pages, static, now):
    tabs = "".join(
        f'<button class="tab{" active" if i==0 else ""}" data-page="{p}">{lb}</button>'
        for i,(p,_,lb) in enumerate(ABAS))

    chart_init = """
// Renderizar charts após DOMContentLoaded
document.addEventListener('DOMContentLoaded',()=>{
  document.querySelectorAll('[data-chart]').forEach(el=>{
    const type  = el.dataset.chart;
    const color = el.dataset.color||'#2563eb';
    const h     = parseInt(el.dataset.height)||160;
    try{
      const series = JSON.parse(el.dataset.series||'[]');
      let svg='';
      if(type==='GL'){
        const s=[{label:'',data:series,color}];
        svg=svgLineChart(s,{height:h});
      }else if(type==='GB'){
        svg=svgBarChart(series,'x','y',{height:h,color});
      }else if(type==='GE'){
        const keys=Object.keys(series[0]||{}).filter(k=>k!=='x');
        svg=svgStackedChart(series,'x',keys,null,{height:h});
      }
      if(svg) el.innerHTML=svg;
    }catch(e){console.warn('chart',el.id,e);}
  });
  renderBars(document);
});"""

    return f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8"/>
<title>BI de Suprimentos</title>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
{static['css']}
canvas{{display:block;width:100%}}
</style>
</head>
<body>
<div class="app">
  <div class="topbar">
    <div class="brand">
      <div class="mark">BI</div>
      <div>
        <h1>BI de Suprimentos</h1>
        <div class="sub">Gerado em {now}</div>
      </div>
    </div>
    <div class="search">
      <svg width="14" height="14" viewBox="0 0 20 20" fill="none">
        <circle cx="8" cy="8" r="5.5" stroke="#94a3b8" stroke-width="1.5"/>
        <path d="m13 13 3.5 3.5" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <input type="text" placeholder="Buscar…"/>
      <kbd>⌘K</kbd>
    </div>
  </div>
  <nav class="tabs" id="tabs">{tabs}</nav>
  <div id="pages">{pages}</div>
</div>
<script>
{static['js']}
{chart_init}
</script>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--tab", help="Só uma aba (debug)")
    args = p.parse_args(argv)

    DIST.mkdir(parents=True, exist_ok=True)
    static = {
        "css": (STATIC/"style.css").read_text(encoding="utf-8") if (STATIC/"style.css").exists() else "",
        "js":  (STATIC/"dashboard.js").read_text(encoding="utf-8") if (STATIC/"dashboard.js").exists() else "",
    }
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("Construindo dashboard...")
    pages = ""
    for page_key, folder, label in ABAS:
        if args.tab and page_key != args.tab: continue
        print(f"  {folder}/")
        d       = load(folder)
        builder = BUILDERS.get(page_key)
        body    = builder(d) if builder else build_generica(d, page_key, folder)
        first   = (ABAS[0][0] == page_key) and not args.tab
        pages  += f'<div class="page{"  active" if first else ""}" data-page="{page_key}">{body}</div>\n'

    html = build_html(pages, static, now)
    out  = DIST / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"\nGerado: {out}  ({out.stat().st_size//1024} KB)")

if __name__ == "__main__":
    main()
