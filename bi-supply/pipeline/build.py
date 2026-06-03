"""
build.py — injeta dados reais no v4.html via sistema unificado.

Método:
  1. Lê design/BI Suprimentos v4.html
  2. Lê todos os 00_index.json de data/processed/{aba}/
  3. Para cada elemento com dados, carrega o arquivo CSV/JSON
  4. Injeta const {VARIAVEL_JS} = {dados}; para cada elemento
  5. Injeta const ABAS_INDEX = {...} com toda a config de layout
  6. Injeta CSS do grid 16 colunas × 40px
  7. Injeta o renderer unificado (substitui pages.XXX() do v4)
  8. Salva dist/index.html

Uso: python pipeline/build.py
"""
from __future__ import annotations
import csv, json, re, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT     = Path(__file__).resolve().parents[1]
PROC     = ROOT / "data" / "processed"
DESIGN   = ROOT / "design" / "BI Suprimentos v4.html"
DIST     = ROOT / "dist"
TABS_DIR = ROOT / "dashboard" / "tabs"

# ── Leitores ──────────────────────────────────────────────────────────────────

def rc(path):
    if not path.exists(): return []
    with path.open(encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))

def rj(path):
    if not path.exists(): return {}
    return json.loads(path.read_text(encoding="utf-8"))

MAX_ROWS = {
    "KPI": None,    # JSON — sem limite
    "GL":  50,      # série temporal
    "GB":  24,      # barras mensais
    "GE":  24,      # empilhado mensal
    "HL":  20,      # hbar list
    "T":   50,      # tabela simples
    "TE":  100,     # tabela expandível
    "MX":  200,     # heatmap (linhas × colunas)
    "AL":  None,    # JSON kpis
    "FU":  10,      # funil
    "TB":  150,     # cascata categorias
}
DEFAULT_MAX = 100

def load_elem_data(aba_folder, dados_file, tipo="T"):
    """Carrega dados de um elemento (CSV ou JSON) com limite por tipo."""
    path = PROC / aba_folder / dados_file
    if not path.exists(): return None
    if path.suffix == ".json": return rj(path)
    if path.suffix == ".csv":
        rows = rc(path)
        limit = MAX_ROWS.get(tipo, DEFAULT_MAX)
        return rows[:limit] if limit else rows
    return None

# ── Carrega todos os indexes ──────────────────────────────────────────────────

RAW = ROOT / "data" / "raw"

def load_dim_filiais():
    """Carrega todas as filiais com nome, negocio, uf, empresa — sem limite de linhas."""
    p = PROC / "04_filial" / "04_filial_r01_ranking.csv"
    if not p.exists():
        return []
    return [{"nome": r.get("nome",""), "negocio": r.get("negocio",""),
             "uf": r.get("uf",""), "empresa": r.get("empresa","")}
            for r in rc(p) if r.get("nome")]

def load_dim_fornecedores():
    """Carrega lista completa de fornecedores com curva ABC do raw Zoho."""
    p = RAW / "curva_forn.csv"
    if not p.exists():
        # fallback: usar processado sem limite
        pp = PROC / "06_fornecedor" / "06_fornecedor_r01_tabela_principal.csv"
        if not pp.exists():
            return []
        return [{"fornecedor": r.get("fornecedor",""), "curva": r.get("curva","")}
                for r in rc(pp) if r.get("fornecedor")]
    rows = rc(p)
    return [{"fornecedor": r.get("RAZAO_SOCIAL","").strip(),
             "curva":      r.get("CURVA","").strip()}
            for r in rows if r.get("RAZAO_SOCIAL","").strip()]

def load_dim_ids():
    """Carrega IDs únicos com nome produto e curva (apenas os com curva_id definida)."""
    p = RAW / "pmp_id_inf_12.csv"
    if not p.exists():
        return []
    rows = rc(p)
    seen = set(); result = []
    for r in rows:
        id_val  = (r.get("﻿ID","") or r.get("ID","")).strip()
        curva   = r.get("CURVA_ID","").strip()
        produto = r.get("NMPRODUTO_OFICIAL","").strip()
        cat2    = r.get("CAT2","").strip()
        if id_val and curva and id_val not in seen:
            seen.add(id_val)
            result.append({"id": id_val, "produto": produto, "cat2": cat2, "curva_id": curva})
    return result

def load_dim_categorias():
    """Carrega hierarquia completa de categorias sem limite de linhas."""
    p = PROC / "03_categoria" / "03_categoria_r01_hierarquia.csv"
    if not p.exists():
        return []
    rows = rc(p)
    # Somente colunas de categoria (exclui métricas)
    return [{k: r.get(k,"") for k in ("cat1","cat2","cat3","cat4","cat5")} for r in rows]

def load_dim_produtos():
    """Carrega lista completa de produtos com curva_prod de pmp_prod_inf_12."""
    p = RAW / "pmp_prod_inf_12.csv"
    if not p.exists():
        p = RAW / "pmp_id_inf_12.csv"   # fallback sem curva_prod
    if not p.exists():
        pp = PROC / "07_produto" / "07_produto_r01_tabela_principal.csv"
        if not pp.exists():
            return []
        return [{"cdproduto": r.get("cdproduto",""), "produto": r.get("produto",""),
                 "cat2": r.get("cat2",""), "curva_prod": r.get("curva_prod","")}
                for r in rc(pp) if r.get("cdproduto")]
    rows = rc(p)
    seen = set(); result = []
    for r in rows:
        cd = (r.get("﻿CDPRODUTO_OFICIAL","") or r.get("CDPRODUTO_OFICIAL","")).strip()
        nm = r.get("NMPRODUTO_OFICIAL","").strip()
        if cd and nm and cd not in seen:
            seen.add(cd)
            result.append({"cdproduto": cd, "produto": nm,
                           "cat2": r.get("CAT2",""), "curva_prod": r.get("CURVA_PROD","").strip()})
    return result

def load_all_indexes():
    indexes = {}
    for p in sorted(PROC.iterdir()):
        idx_file = p / f"{p.name}_00_index.json"
        if idx_file.exists():
            idx = rj(idx_file)
            indexes[p.name] = idx
    return indexes


def apply_layout_overrides(indexes):
    """Lê dashboard/tabs/{aba}.layout.json e aplica overrides nos indexes."""
    TABS_DIR.mkdir(parents=True, exist_ok=True)
    for _, idx in indexes.items():
        page_key = idx.get("data_page", "")
        layout_file = TABS_DIR / f"{page_key}.layout.json"
        if not layout_file.exists():
            continue
        overrides = rj(layout_file).get("overrides", {})
        for elem in idx.get("elementos", []):
            eid = elem.get("id", "")
            if eid not in overrides:
                continue
            ov = overrides[eid]
            # Posição
            for k in ("col", "col_span", "row", "row_span", "visivel"):
                if k in ov:
                    elem["layout"][k] = ov[k]
            # Texto
            if "texto" in ov:
                txt = ov["texto"]
                if "titulo"    in txt: elem["titulo"]    = txt["titulo"]
                if "subtitulo" in txt: elem["subtitulo"] = txt["subtitulo"]
                if "colunas"   in txt:
                    for col in elem.get("config", {}).get("colunas", []):
                        if col.get("key") in txt["colunas"]:
                            col["label"] = txt["colunas"][col["key"]]
    return indexes

# ── Gera JS de injeção ────────────────────────────────────────────────────────

def build_js_injection(indexes):
    lines = ["\n/* ========================================================"]
    lines.append("   DADOS REAIS — gerado por pipeline/build.py")
    lines.append("   " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    lines.append("   ======================================================== */")
    # Registry global — acessível como _BI_DATA[nome] pelo renderer
    lines.append("if (!window._BI_DATA) window._BI_DATA = {};\n")

    # 1. Dados por elemento → _BI_DATA[variavel_js]
    for folder, idx in indexes.items():
        for elem in idx.get("elementos", []):
            vjs   = elem.get("variavel_js", "")
            dados = elem.get("dados", "")
            if not vjs or not dados: continue
            data = load_elem_data(folder, dados, elem.get("tipo","T"))
            if data is None: continue
            data_js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            lines.append(f"window._BI_DATA['{vjs}'] = {data_js};")

    lines.append("")

    # 2. ABAS_INDEX com toda a config (sem os dados inline — dados já nas constantes)
    abas_index = {}
    for folder, idx in indexes.items():
        page_key = idx.get("data_page", folder.split("_",1)[-1] if "_" in folder else folder)
        abas_index[page_key] = {
            "label":    idx.get("label", ""),
            "nota":     idx.get("nota", ""),
            "status":   idx.get("status", ""),
            "grid":     idx.get("grid", {"colunas": 16, "row_height_px": 40}),
            "elementos": [
                {k: v for k, v in e.items() if k != "dados"}  # remove dados (já nas constantes)
                for e in idx.get("elementos", [])
            ]
        }

    abas_js = json.dumps(abas_index, ensure_ascii=False, separators=(",", ":"))
    lines.append(f"const ABAS_INDEX = {abas_js};")
    lines.append("")

    # Dimensões completas para os filtros (sem limite de linhas)
    dim_cats  = load_dim_categorias()
    dim_prods = load_dim_produtos()
    dim_filia = load_dim_filiais()
    dim_forns = load_dim_fornecedores()
    dim_ids   = load_dim_ids()
    lines.append(f"window._BI_DATA['DIM_CATEGORIAS']  = {json.dumps(dim_cats,  ensure_ascii=False, separators=(',',':'))};")
    lines.append(f"window._BI_DATA['DIM_PRODUTOS']    = {json.dumps(dim_prods, ensure_ascii=False, separators=(',',':'))};")
    lines.append(f"window._BI_DATA['DIM_FILIAIS']     = {json.dumps(dim_filia, ensure_ascii=False, separators=(',',':'))};")
    lines.append(f"window._BI_DATA['DIM_FORNECEDORES']= {json.dumps(dim_forns, ensure_ascii=False, separators=(',',':'))};")
    lines.append(f"window._BI_DATA['DIM_IDS']         = {json.dumps(dim_ids,   ensure_ascii=False, separators=(',',':'))};")
    lines.append("")
    print(f"  Dimensões: {len(dim_cats)} cat · {len(dim_prods)} prod · {len(dim_filia)} filiais · {len(dim_forns)} forn · {len(dim_ids)} IDs")

    return "\n".join(lines)

# ── CSS do grid ───────────────────────────────────────────────────────────────

GRID_CSS = """
/* ── Grid 16 colunas × 40px — gerado por build.py ── */
.page-grid {
  display: grid;
  grid-template-columns: repeat(16, 1fr);
  grid-auto-rows: 40px;
  gap: 10px;
  padding: 10px 0;
}
.grid-element {
  overflow: hidden;
  min-height: 0;
}
.grid-element .card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.grid-element .card-b {
  flex: 1;
  overflow: auto;
  min-height: 0;
}
.grid-element .kpi {
  height: 100%;
  box-sizing: border-box;
}
.grid-editor-handle {
  display: none;
  position: absolute;
  top: 4px; left: 4px;
  cursor: grab;
  z-index: 10;
  background: var(--blue-soft);
  border: 1px solid var(--blue);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 10px;
  color: var(--blue);
  font-weight: 700;
}
.edit-mode .grid-element {
  position: relative;
  outline: 1px dashed var(--line);
  outline-offset: -1px;
}
.edit-mode .grid-editor-handle { display: block; }
.edit-mode .grid-element:hover { outline-color: var(--blue); }
"""

# ── Renderer JS unificado ─────────────────────────────────────────────────────

RENDERER_JS = r"""
/* ── Renderer unificado — gerado por build.py ── */

function _fmtVal(v, fmt) {
  const n = parseFloat(v) || 0;
  if (!fmt || fmt === 'auto') return FMT.mi(n);
  if (fmt === 'brl')  return FMT.brl(n);
  if (fmt === 'brl2') return FMT.brl2(n);
  if (fmt === 'mi')   return FMT.mi(n);
  if (fmt === 'pct')  return (n > 0 ? '+' : '') + n.toFixed(1).replace('.', ',') + '%';
  if (fmt === 'num')  return FMT.num(n);
  if (fmt === 'dec')  return n.toFixed(2).replace('.', ',');
  if (fmt === 'str')  return String(v || '—');
  return FMT.mi(n);
}

function _zohoSrc(src) {
  return src ? `<span style="font-size:10px;font-weight:700;color:var(--blue);background:var(--blue-soft);border:1px solid #bfdbfe;border-radius:4px;padding:1px 6px;white-space:nowrap">${src}</span>` : '';
}

function _cardHeader(elem) {
  return `<div class="card-h" style="flex-shrink:0">
    <div><h3 style="margin:0;font-size:12px">${elem.titulo}</h3>${elem.subtitulo ? `<div class="sub" style="font-size:10.5px">${elem.subtitulo}</div>` : ''}</div>
    ${elem.zoho_origem ? `<div class="meta">${_zohoSrc(elem.zoho_origem)}</div>` : ''}
  </div>`;
}

// ── KPI ──────────────────────────────────────────────────────────────────────
function _renderKPI(elem, data) {
  const cfg = elem.config || {};
  const val = data ? data[cfg.chave] : null;
  const state = cfg.state || '';
  const valStr = _fmtVal(val, cfg.fmt);
  let deltaHtml = '';
  if (cfg.delta_chave && data) {
    const dval = data[cfg.delta_chave];
    const dir  = cfg.delta_dir || '';
    deltaHtml  = `<div class="delta ${dir}"><b>${_fmtVal(dval, cfg.fmt)}</b><span>${cfg.delta_ctx || ''}</span></div>`;
  } else if (cfg.delta_ctx) {
    deltaHtml = `<div class="delta"><span>${cfg.delta_ctx}</span></div>`;
  }
  return `<div class="kpi ${state}" style="height:100%">
    <div class="lab">${elem.titulo}</div>
    <div class="val">${valStr}</div>
    ${deltaHtml}
  </div>`;
}

// ── Hbar List ─────────────────────────────────────────────────────────────────
function _renderHL(elem, data) {
  if (!data || !data.length) return '<div class="muted" style="padding:10px;font-size:12px">Sem dados</div>';
  const cfg = elem.config || {};
  const lk = cfg.label, vk = cfg.value, sk = cfg.sub || '';
  const maxV = Math.max(...data.map(r => parseFloat(r[vk]) || 0)) || 1;
  const colorCls = cfg.color || '';
  return '<div style="overflow:auto;height:100%">' + data.map(r => {
    const v = parseFloat(r[vk]) || 0;
    const pct = (v / maxV * 100).toFixed(1);
    return `<div class="hbar">
      <div class="lab">${r[lk] || ''}${sk && r[sk] ? `<div class="sub">${r[sk]}</div>` : ''}</div>
      <div class="bar ${colorCls}"><span style="width:${pct}%"></span></div>
      <div class="v">${_fmtVal(v, cfg.fmt || 'brl')}</div>
    </div>`;
  }).join('') + '</div>';
}

// ── Tabela ────────────────────────────────────────────────────────────────────
function _renderT(elem, data) {
  if (!data || !data.length) return '<div class="muted" style="padding:10px;font-size:12px">Sem dados</div>';
  const cfg = elem.config || {};
  const cols = cfg.colunas || Object.keys(data[0]).slice(0, 6).map(k => ({key: k, label: k}));
  const ths = cols.map(c => `<th class="${c.cls || ''}" data-key="${c.key}">${c.label || c.key}</th>`).join('');
  const trs = data.slice(0, 25).map(r => {
    const tds = cols.map(c => {
      let v = r[c.key] != null ? r[c.key] : '';
      const fmt = c.fmt || '';
      if (fmt === 'brl')  v = FMT.brl(parseFloat(v) || 0);
      else if (fmt === 'brl2') v = FMT.brl2(parseFloat(v) || 0);
      else if (fmt === 'mi')   v = FMT.mi(parseFloat(v) || 0);
      else if (fmt === 'pct')  {
        const n = parseFloat(v) || 0;
        v = `<span class="pill ${n > 15 ? 'r' : n > 5 ? 'y' : n < -3 ? 'g' : 'k'}">${n > 0 ? '+' : ''}${n.toFixed(1).replace('.', ',')}%</span>`;
      }
      else if (c.cls === 'spark') {
        try { const pts = JSON.parse(v || '[]'); v = pts.length ? svgSpark(pts.map(Number)) : '—'; }
        catch(e) { v = '—'; }
      }
      return `<td class="${c.cls || ''}">${v}</td>`;
    }).join('');
    return `<tr>${tds}</tr>`;
  }).join('');
  return `<div style="overflow:auto;height:100%"><table class="table"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table></div>`;
}

// ── Gráfico de Linhas ─────────────────────────────────────────────────────────
function _renderGL(elem, data) {
  if (!data || !data.length) return '';
  const cfg = elem.config || {};
  const xk = cfg.x, yk = cfg.y, color = cfg.color || '#2563eb';
  const W=560, H=130, pL=36, pR=8, pT=10, pB=22;
  const iW = W - pL - pR, iH = H - pT - pB;
  const vals = data.map(r => parseFloat(r[yk]) || 0);
  const maxV = Math.max(...vals) || 1;
  const gid = 'g' + Math.random().toString(36).slice(2,7);

  const pts = data.map((r, i) => {
    const x = pL + (i / (data.length - 1)) * iW;
    const y = pT + iH - (vals[i] / maxV) * iH;
    return x.toFixed(1) + ',' + y.toFixed(1);
  }).join(' ');

  const lines = [0, 1, 2, 3].map(i => {
    const y = pT + (i / 3) * iH;
    return `<line x1="${pL}" x2="${W-pR}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#eef2f7"/>`;
  }).join('');

  const step = Math.max(1, Math.floor(data.length / 6));
  const xlabels = data.map((r, i) => {
    if (i % step !== 0 && i !== data.length - 1) return '';
    const x = pL + (i / (data.length - 1)) * iW;
    return `<text x="${x.toFixed(1)}" y="${H-3}" text-anchor="middle" font-size="9" fill="#64748b" font-family="'Segoe UI',Arial,sans-serif">${String(r[xk] || '').slice(-7)}</text>`;
  }).join('');

  const ptArr = pts.split(' ');
  const lastPt = ptArr[ptArr.length - 1].split(',');
  const pathD  = `M${pts.split(' ').join(' L')} L${lastPt[0]},${(pT+iH).toFixed(1)} L${pL},${(pT+iH).toFixed(1)} Z`;

  return `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">
    <defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${color}" stop-opacity=".18"/>
      <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
    </linearGradient></defs>
    ${lines}
    <path d="${pathD}" fill="url(#${gid})"/>
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.8" stroke-linejoin="round"/>
    ${xlabels}
  </svg>`;
}

// ── Gráfico de Barras ─────────────────────────────────────────────────────────
function _renderGB(elem, data) {
  if (!data || !data.length) return '';
  const cfg = elem.config || {};
  const xk = cfg.x, yk = cfg.y, color = cfg.color || '#2563eb';
  const W=560, H=110, pL=8, pR=8, pT=8, pB=22;
  const iW=W-pL-pR, iH=H-pT-pB;
  const vals = data.map(r => parseFloat(r[yk]) || 0);
  const maxV = Math.max(...vals) || 1;
  const bW = Math.floor(iW / data.length * 0.68);

  const bars = data.map((r, i) => {
    const x = pL + i * (iW / data.length) + (iW / data.length - bW) / 2;
    const v = vals[i], bH = (v / maxV) * iH, y = pT + iH - bH;
    return `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${bW}" height="${bH.toFixed(1)}" fill="${color}" rx="2" opacity="0.85"/>
      <text x="${(x+bW/2).toFixed(1)}" y="${H-4}" text-anchor="middle" font-size="8" fill="#64748b">${String(r[xk]||'').slice(-7)}</text>`;
  }).join('');

  return `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">
    <line x1="${pL}" x2="${W-pR}" y1="${(pT+iH/2).toFixed(1)}" y2="${(pT+iH/2).toFixed(1)}" stroke="#eef2f7"/>
    ${bars}
  </svg>`;
}

// ── Gráfico Empilhado ─────────────────────────────────────────────────────────
function _renderGE(elem, data) {
  if (!data || !data.length) return '';
  const cfg = elem.config || {};
  const xk = cfg.x, stacks = cfg.stacks || [];
  const colors = ['#b91c1c','#f59e0b','#2563eb','#16a34a','#6366f1'];
  const W=560, H=110, pL=8, pR=8, pT=8, pB=22;
  const iW=W-pL-pR, iH=H-pT-pB;
  const totals = data.map(r => stacks.reduce((s, k) => s + (parseFloat(r[k]) || 0), 0));
  const maxT = Math.max(...totals) || 1;
  const bW = Math.floor(iW / data.length * 0.7);

  const bars = data.map((r, i) => {
    const x = pL + i * (iW / data.length) + (iW / data.length - bW) / 2;
    let yOff = pT + iH, rects = '';
    stacks.forEach((k, ki) => {
      const v = parseFloat(r[k]) || 0, bH = (v / maxT) * iH;
      if (bH > 0) { rects += `<rect x="${x.toFixed(1)}" y="${(yOff-bH).toFixed(1)}" width="${bW}" height="${bH.toFixed(1)}" fill="${colors[ki%colors.length]}" opacity="0.85"/>`; yOff -= bH; }
    });
    return rects + `<text x="${(x+bW/2).toFixed(1)}" y="${H-4}" text-anchor="middle" font-size="8" fill="#64748b">${String(r[xk]||'').slice(-7)}</text>`;
  }).join('');

  return `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">${bars}</svg>`;
}

// ── Heatmap Matrix ────────────────────────────────────────────────────────────
function _renderMX(elem, data) {
  if (!data || !data.length) return '<div class="muted" style="padding:10px;font-size:12px">Sem dados</div>';
  const cfg = elem.config || {};
  const rk=cfg.row_key, ck=cfg.col_key, vk=cfg.val_key;
  const rows=[...new Set(data.map(r=>r[rk]).filter(Boolean))];
  const cols=[...new Set(data.map(r=>r[ck]).filter(Boolean))];
  const lookup={};
  data.forEach(r=>{lookup[`${r[rk]}|${r[ck]}`]=parseFloat(r[vk])||0;});
  const maxV=Math.max(...Object.values(lookup))||1;
  function si(v){const p=v/maxV;return p<.2?'s1':p<.4?'s2':p<.6?'s3':p<.8?'s4':'s5';}
  const head='<div class="cell head"></div>'+cols.map(c=>`<div class="cell head" style="font-size:9px;padding:2px">${String(c).slice(0,5)}</div>`).join('');
  const body=rows.map(rv=>`<div class="cell head" style="font-size:9px;text-align:left;justify-content:flex-start;padding:2px 4px;overflow:hidden;white-space:nowrap">${String(rv).slice(0,20)}</div>`+cols.map(cv=>{const v=lookup[`${rv}|${cv}`]||0;return `<div class="cell ${v>0?si(v):'s1'}" style="font-size:9px" title="${v?FMT.brl(v):''}">${v>0?(v/1e6).toFixed(1):'—'}</div>`;}).join('')).join('');
  const colW=`100px repeat(${cols.length},1fr)`;
  return `<div style="overflow:auto;height:100%"><div class="matrix" style="grid-template-columns:${colW}">${head}${body}</div></div>`;
}

// ── Alertas (rule-based) ──────────────────────────────────────────────────────
function _renderAL(elem, data) {
  if (!data) return '<div class="muted" style="padding:10px">—</div>';
  const alerts=[];
  const pct=parseFloat(data.pct_com_cotacao)||0;
  const imp=parseFloat(data.imp_cot_total)||0;
  const cp120=parseFloat(data.cp_critico_120d)||0;
  const adp=parseFloat(data.ad_pendente)||0;
  if(pct<50) alerts.push(['r',pct.toFixed(1)+'% das compras sem cotação','Abaixo do mínimo — meta: 80%','Alto','Compras']);
  if(cp120>0) alerts.push(['r','R$ '+FMT.mi(cp120)+' em CP com +120 dias','Títulos vencidos há mais de 120 dias',FMT.mi(cp120),'Financeiro']);
  if(imp>0) alerts.push(['y','R$ '+FMT.mi(imp)+' de oportunidade de cotação','Compras acima do menor preço disponível',FMT.mi(imp),'Compras']);
  if(adp>1e6) alerts.push(['y','R$ '+FMT.mi(adp)+' em adiantamentos pendentes','Status indefinido — necessita conciliação',FMT.mi(adp),'Financeiro']);
  if(!alerts.length) return '<div class="muted" style="padding:10px;font-size:12px">Nenhum alerta crítico no momento.</div>';
  return alerts.map(([t,tit,who,im,area])=>`<div class="alert-row ${t}"><span class="dot"></span><div><div class="nm">${tit}</div><div class="who">${who}</div></div><div class="num">${im}</div><span class="pill ghost">${area}</span><button class="act">Abrir</button></div>`).join('');
}

// ── Funil ─────────────────────────────────────────────────────────────────────
function _renderFU(elem, data) {
  if (!data || !data.length) return '';
  const cfg=elem.config||{};
  const lk=cfg.label||'status', vk=cfg.value||'valor';
  const maxV=parseFloat(data[0][vk])||1;
  return '<div class="funnel" style="padding:4px 0">' + data.map(r=>{
    const v=parseFloat(r[vk])||0, pct=(v/maxV*100).toFixed(1);
    return `<div class="funnel-step"><div class="fl">${r[lk]||''}</div><div class="fbar"><span style="width:${pct}%"></span></div><div class="fv">${FMT.brl(v)}</div></div>`;
  }).join('') + '</div>';
}

// ── Cascata Categorias ────────────────────────────────────────────────────────
function _renderTB(elem, data) {
  if (!data || !data.length) return '<div class="muted" style="padding:10px;font-size:12px">Hierarquia de categorias</div>';
  return _renderT({...elem, config:{colunas:[
    {key:'cat2',label:'CAT2',cls:'nm'},{key:'cat3',label:'CAT3',cls:'sm'},
    {key:'spend',label:'Spend',cls:'num',fmt:'brl'},{key:'pct',label:'%',cls:'num'},
    {key:'inflacao_media_pct',label:'Infl.',cls:'num',fmt:'pct'}
  ]}}, data.slice(0,30));
}

// ── Dispatcher ────────────────────────────────────────────────────────────────
function _renderElemento(elem, data) {
  if (elem.tipo === 'KPI') return _renderKPI(elem, data);

  const header = _cardHeader(elem);
  let body = '';

  switch(elem.tipo) {
    case 'GL': body = _renderGL(elem, data); break;
    case 'GB': body = _renderGB(elem, data); break;
    case 'GE': body = _renderGE(elem, data); break;
    case 'HL': body = _renderHL(elem, data); break;
    case 'T':  body = _renderT(elem, data);  break;
    case 'TE': body = _renderT(elem, data);  break;  // expandable como tabela por ora
    case 'MX': body = _renderMX(elem, data); break;
    case 'AL': body = _renderAL(elem, data); break;
    case 'FU': body = _renderFU(elem, data); break;
    case 'TB': body = _renderTB(elem, data); break;
    default:
      body = `<div class="muted" style="padding:10px;font-size:12px">${elem.tipo} · em implementação</div>`;
  }

  return `<div class="card" style="height:100%;display:flex;flex-direction:column;overflow:hidden">
    ${header}
    <div class="card-b" style="flex:1;overflow:auto;padding:8px 10px;min-height:0">${body}</div>
  </div>`;
}

// ── Renderiza uma página inteira ──────────────────────────────────────────────
function _renderPage(pageKey) {
  const idx = ABAS_INDEX[pageKey];
  if (!idx) return `<div class="muted" style="padding:20px">Aba: ${pageKey}</div>`;

  if (idx.status === 'PENDENTE') {
    return `<div style="display:flex;align-items:center;justify-content:center;height:200px;text-align:center;color:var(--muted)">
      <div><div style="font-size:15px;font-weight:700;margin-bottom:8px">${idx.label}</div>
      <div style="font-size:12px">${idx.nota || 'Pendente de implementação'}</div></div>
    </div>`;
  }

  const elems = (idx.elementos || []).filter(e => e.layout && e.layout.visivel);
  const cells = elems.map(e => {
    const {col, col_span, row, row_span} = e.layout;
    const data = window._BI_DATA ? window._BI_DATA[e.variavel_js] : undefined;
    const content = _renderElemento(e, data);
    const handle = `<div class="grid-editor-handle" data-id="${e.id}" title="${e.id}">⠿</div>`;
    return `<div class="grid-element" data-id="${e.id}"
         style="grid-column:${col}/span ${col_span};grid-row:${row}/span ${row_span};position:relative">
      ${handle}${content}
    </div>`;
  }).join('\n');

  return `<div class="page-grid">${cells}</div>`;
}

// ── Substituir pages.XXX() pelo renderer unificado ───────────────────────────
// 'categorias' e 'estoque' preservam a implementação original do v4
// (categorias usa cascata interativa CAT_VAL/CAT_INF/CAT_TAX que já foi populada)
const _ABAS_SKIP = new Set(['categorias','estoque']);
const _ABAS_KEYS = ['resumo','oportunidades','categorias','filiais','estoque',
  'forn360','produtos','cotacoes','impacto','inflacao',
  'fiscal','financeiro','adiantamentos','servicos','qualidade'];

_ABAS_KEYS.filter(pg => !_ABAS_SKIP.has(pg)).forEach(pg => {
  pages[pg] = () => _renderPage(pg);
});
"""

# ── CSS do editor ─────────────────────────────────────────────────────────────

EDITOR_CSS = """
/* ── Editor visual — gerado por build.py ── */
#ed-toggle.ed-active { background:var(--blue);color:#fff;border-color:var(--blue); }

body.edit-mode .grid-element {
  cursor: grab;
  position: relative;
}
/* borda via ::after para ficar ACIMA do conteúdo (KPI, card etc.) */
body.edit-mode .grid-element::after {
  content: '';
  position: absolute;
  inset: 0;
  border: 1px dashed var(--line);
  border-radius: 4px;
  pointer-events: none;
  z-index: 15;
}
body.edit-mode .grid-element:hover::after {
  border: 2px solid var(--blue);
}
body.edit-mode .grid-element.ed-over::after {
  border: 2px solid var(--blue);
  background: rgba(37,99,235,.07);
}
body.edit-mode .grid-element.ed-drag { opacity:.35; }
body.edit-mode .grid-element.ed-hidden { opacity:.18; }

/* ghost de posicionamento */
#ed-ghost {
  pointer-events: none;
  border: 2px dashed var(--blue);
  border-radius: 6px;
  background: rgba(37,99,235,.08);
  z-index: 50;
}

/* action bar */
.ed-bar {
  display: none;
  position: absolute; top:3px; right:3px;
  z-index: 30; gap:3px;
}
body.edit-mode .ed-bar { display:flex; }
.ed-icn {
  width:22px; height:22px;
  border:1px solid var(--border); border-radius:4px;
  background:var(--surface); color:var(--text);
  font-size:12px; cursor:pointer; padding:0;
  display:flex; align-items:center; justify-content:center;
}
.ed-icn:hover { background:var(--blue);color:#fff;border-color:var(--blue); }

/* resize handle */
.ed-rz {
  position: absolute; bottom:2px; right:2px;
  width:16px; height:16px;
  background:var(--blue); border-radius:3px;
  cursor:se-resize; z-index:30;
  color:#fff; font-size:12px; line-height:1;
  display:none; align-items:center; justify-content:center;
  user-select:none;
}
body.edit-mode .ed-rz { display:flex; }

/* editable text */
body.edit-mode [contenteditable="true"] {
  outline:1px dashed var(--blue); outline-offset:1px;
  cursor:text; border-radius:2px;
}
body.edit-mode [contenteditable="true"]:focus {
  outline:2px solid var(--blue);
  background:rgba(37,99,235,.04);
}
body.edit-mode svg text { cursor:text; }
"""

# ── JS do editor ──────────────────────────────────────────────────────────────

EDITOR_JS = r"""
/* ── Editor visual — gerado por build.py ── */
(function() {
'use strict';

const LS_PFX = 'bi_layout_';
const _st    = {};
let _undo    = null;
let _mode    = false;
let _src     = null;
let _gCol    = 1, _gRow = 1;
let _svgInp  = null, _svgTgt = null;

function _pk() { const a=document.querySelector('.tab.active[data-page]'); return a?a.dataset.page:''; }
function _ens(pk) { if (!_st[pk]) _st[pk]={overrides:{}}; return _st[pk]; }
function _ov(pk,id,p) { _ens(pk); if(!_st[pk].overrides[id]) _st[pk].overrides[id]={}; Object.assign(_st[pk].overrides[id],p); }
function _ovT(pk,id,tp) { _ens(pk); const ov=_st[pk].overrides; if(!ov[id]) ov[id]={}; if(!ov[id].texto) ov[id].texto={}; Object.assign(ov[id].texto,tp); }

function _getL(el) {
  const cm=(el.style.gridColumn||'').match(/(\d+)\s*\/\s*span\s*(\d+)/);
  const rm=(el.style.gridRow   ||'').match(/(\d+)\s*\/\s*span\s*(\d+)/);
  return {col:cm?+cm[1]:1,col_span:cm?+cm[2]:1,row:rm?+rm[1]:1,row_span:rm?+rm[2]:1};
}
function _setL(el,l) { el.style.gridColumn=`${l.col}/span ${l.col_span}`; el.style.gridRow=`${l.row}/span ${l.row_span}`; }

// ── localStorage: auto-save e load ───────────────────────────────────────────
function _autoSave(pk) {
  try {
    const ov=(_st[pk]||{}).overrides||{};
    localStorage.setItem(LS_PFX+pk, JSON.stringify(ov));
    _flashSaved();
  } catch(e) {}
}

function _loadAll() {
  for (let i=0;i<localStorage.length;i++) {
    const key=localStorage.key(i);
    if (!key||!key.startsWith(LS_PFX)) continue;
    const pk=key.slice(LS_PFX.length);
    try { const ov=JSON.parse(localStorage.getItem(key)||'{}'); _ens(pk); _st[pk].overrides=ov; } catch(e) {}
  }
}

// ── Aplicar overrides salvos ao DOM da aba atual ──────────────────────────────
function _applyLayout(pk) {
  const ov=(_st[pk]||{}).overrides||{};
  document.querySelectorAll('.grid-element').forEach(el=>{
    const id=el.dataset.id; if(!id||!ov[id]) return;
    const o=ov[id];
    if ('col' in o && 'col_span' in o) el.style.gridColumn=`${o.col}/span ${o.col_span}`;
    if ('row' in o && 'row_span' in o) el.style.gridRow   =`${o.row}/span ${o.row_span}`;
    if ('visivel' in o && !o.visivel) el.classList.add('ed-hidden');
    if (o.texto) {
      if (o.texto.titulo)    { const h=el.querySelector('.card-h h3')||el.querySelector('.kpi .lab'); if(h) h.textContent=o.texto.titulo; }
      if (o.texto.subtitulo) { const s=el.querySelector('.card-h .sub');if(s) s.textContent=o.texto.subtitulo; }
      if (o.texto.colunas)   {
        el.querySelectorAll('table th[data-key]').forEach(th=>{
          if(o.texto.colunas[th.dataset.key]) th.textContent=o.texto.colunas[th.dataset.key];
        });
      }
    }
  });
}

// ── Flash "salvo" no topbar ───────────────────────────────────────────────────
function _flashSaved() {
  let el=document.getElementById('ed-saved');
  if(!el){el=document.createElement('span');el.id='ed-saved';el.style.cssText='font-size:11px;color:var(--green,#16a34a);transition:opacity .5s';document.getElementById('ed-tb')?.appendChild(el);}
  el.textContent='✓ salvo';el.style.opacity='1';
  clearTimeout(el._t);el._t=setTimeout(()=>{el.style.opacity='0';},1500);
}

// ── Snapshot para undo ────────────────────────────────────────────────────────
function _snap(pk) {
  const dom={};
  document.querySelectorAll('.grid-element').forEach(el=>{
    const id=el.dataset.id; if(!id) return;
    dom[id]={gc:el.style.gridColumn,gr:el.style.gridRow,hid:el.classList.contains('ed-hidden')};
  });
  _undo={pk,overrides:JSON.parse(JSON.stringify((_st[pk]||{}).overrides||{})),dom};
}

// ── Ghost de posição ──────────────────────────────────────────────────────────
function _ghost(grid) {
  let g=document.getElementById('ed-ghost');
  if (!g){g=document.createElement('div');g.id='ed-ghost';grid.appendChild(g);}
  return g;
}
function _rmGhost() { const g=document.getElementById('ed-ghost');if(g)g.remove(); }

// ── Drag / drop ───────────────────────────────────────────────────────────────
function _initDnd() {
  document.addEventListener('dragstart', e=>{
    if(!_mode) return;
    const el=e.target.closest('.grid-element');if(!el) return;
    _src=el;el.classList.add('ed-drag');e.dataTransfer.effectAllowed='move';
    const grid=el.closest('.page-grid');if(!grid) return;
    const L=_getL(el);_gCol=L.col;_gRow=L.row;
    const g=_ghost(grid);
    g.style.gridColumn=`${L.col}/span ${L.col_span}`;
    g.style.gridRow   =`${L.row}/span ${L.row_span}`;
  });

  document.addEventListener('dragend', ()=>{
    if(_src)_src.classList.remove('ed-drag');_src=null;_rmGhost();
  });

  document.addEventListener('dragover', e=>{
    if(!_mode||!_src) return;
    const grid=_src.closest('.page-grid');if(!grid) return;
    const r=grid.getBoundingClientRect();
    if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) return;
    e.preventDefault();e.dataTransfer.dropEffect='move';
    const colW=r.width/16,rowH=50;
    const col=Math.max(1,Math.min(16,Math.floor((e.clientX-r.left)/colW)+1));
    const row=Math.max(1,Math.min(40,Math.floor((e.clientY-r.top )/rowH)+1));
    if(col===_gCol&&row===_gRow) return;
    _gCol=col;_gRow=row;
    const L=_getL(_src);const g=_ghost(grid);
    g.style.gridColumn=`${col}/span ${L.col_span}`;
    g.style.gridRow   =`${row}/span ${L.row_span}`;
  });

  document.addEventListener('drop', e=>{
    if(!_mode||!_src) return;
    const grid=_src.closest('.page-grid');if(!grid) return;
    const r=grid.getBoundingClientRect();
    if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) return;
    e.preventDefault();
    const pk=_pk();_snap(pk);
    const srcL=_getL(_src);const tc=_gCol,tr=_gRow;
    let tgt=null;
    document.querySelectorAll('.grid-element').forEach(el=>{
      if(el===_src) return;
      const l=_getL(el);
      if(tc<l.col+l.col_span&&tc+srcL.col_span>l.col&&tr<l.row+l.row_span&&tr+srcL.row_span>l.row) tgt=el;
    });
    if(tgt){
      const tL=_getL(tgt);
      _setL(_src,tL);_setL(tgt,srcL);
      _ov(pk,_src.dataset.id,{col:tL.col,col_span:tL.col_span,row:tL.row,row_span:tL.row_span});
      _ov(pk,tgt.dataset.id, {col:srcL.col,col_span:srcL.col_span,row:srcL.row,row_span:srcL.row_span});
    } else {
      _setL(_src,{...srcL,col:tc,row:tr});
      _ov(pk,_src.dataset.id,{col:tc,col_span:srcL.col_span,row:tr,row_span:srcL.row_span});
    }
    _rmGhost();
    _autoSave(pk);
  });
}

// ── Resize ────────────────────────────────────────────────────────────────────
function _attachRz(el,rz) {
  rz.addEventListener('mousedown', e=>{
    e.preventDefault();e.stopPropagation();
    const pk=_pk();_snap(pk);
    const gW=(el.closest('.page-grid')||{offsetWidth:640}).offsetWidth;
    const CP=Math.floor(gW/16),RP=50;
    const L0=_getL(el),sx=e.clientX,sy=e.clientY;
    const mv=ev=>{
      const nc=Math.max(1,Math.min(17-L0.col,L0.col_span+Math.round((ev.clientX-sx)/CP)));
      const nr=Math.max(1,Math.min(40,         L0.row_span+Math.round((ev.clientY-sy)/RP)));
      _setL(el,{...L0,col_span:nc,row_span:nr});
    };
    const up=()=>{
      document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up);
      const L=_getL(el);
      _ov(pk,el.dataset.id,{col:L.col,col_span:L.col_span,row:L.row,row_span:L.row_span});
      _autoSave(pk);
    };
    document.addEventListener('mousemove',mv);document.addEventListener('mouseup',up);
  });
}

// ── Inline text editing ───────────────────────────────────────────────────────
function _onBlur(e) {
  if(!_mode) return;
  const node=e.target,el=node.closest('.grid-element');if(!el) return;
  const pk=_pk(),id=el.dataset.id||'',txt=node.textContent.trim();
  if (node.matches('.card-h h3,.kpi .lab')) _ovT(pk,id,{titulo:txt});
  else if(node.matches('.card-h .sub'))  _ovT(pk,id,{subtitulo:txt});
  else if(node.tagName==='TH'){
    const k=node.dataset.key;
    if(k){const c={...(_st[pk]?.overrides[id]?.texto?.colunas||{}),[k]:txt};_ovT(pk,id,{colunas:c});}
  }
  _autoSave(pk);
  if(_mode) node.addEventListener('blur',_onBlur,{once:true});
}
function _enText(on) {
  document.querySelectorAll('.grid-element .card-h h3,.grid-element .card-h .sub,.grid-element table th,.grid-element .kpi .lab').forEach(n=>{
    n.contentEditable=on?'true':'false';
    if(on) n.addEventListener('blur',_onBlur,{once:true});
  });
}

// ── SVG floating input ────────────────────────────────────────────────────────
function _initSvgInp() {
  const inp=document.createElement('input');
  inp.id='ed-svg-inp';
  inp.style.cssText='position:fixed;z-index:9999;display:none;padding:2px 6px;border:2px solid var(--blue);border-radius:4px;font-size:11px;font-family:inherit;background:var(--surface);color:var(--text);min-width:80px';
  document.body.appendChild(inp);_svgInp=inp;
  inp.addEventListener('blur',_commitSvg);
  inp.addEventListener('keydown',e=>{if(e.key==='Enter'){_commitSvg();e.preventDefault();}if(e.key==='Escape'){inp.style.display='none';_svgTgt=null;}});
  document.addEventListener('click',e=>{if(_svgInp&&_svgInp.style.display!=='none'&&e.target!==_svgInp)_commitSvg();});
}
function _onSvgClick(e) {
  if(!_mode) return;
  const t=e.currentTarget,r=t.getBoundingClientRect();
  _svgTgt=t;_svgInp.value=t.textContent;
  _svgInp.style.left=r.left+'px';_svgInp.style.top=(r.top-4)+'px';
  _svgInp.style.display='block';_svgInp.focus();_svgInp.select();
  e.stopPropagation();
}
function _commitSvg() {
  if(!_svgTgt) return;
  const v=_svgInp.value.trim();if(v)_svgTgt.textContent=v;
  _svgInp.style.display='none';_svgTgt=null;
}
function _enSvg(on) {
  document.querySelectorAll('.grid-element svg text').forEach(t=>{
    if(on){t.style.cursor='text';t.addEventListener('click',_onSvgClick);}
    else{t.style.cursor='';t.removeEventListener('click',_onSvgClick);}
  });
}

// ── Decorar elementos ─────────────────────────────────────────────────────────
function _decorate() {
  document.querySelectorAll('.grid-element').forEach(el=>{
    if(el.querySelector('.ed-bar')) return;
    const id=el.dataset.id||'';
    const bar=document.createElement('div');bar.className='ed-bar';
    bar.innerHTML='<button class="ed-icn" title="Ocultar/Mostrar">👁</button>';
    el.appendChild(bar);
    bar.querySelector('.ed-icn').onclick=e=>{
      e.stopPropagation();const pk=_pk();_snap(pk);
      const hid=el.classList.toggle('ed-hidden');_ov(pk,id,{visivel:!hid});
      _autoSave(pk);
    };
    const rz=document.createElement('div');rz.className='ed-rz';rz.title='Redimensionar';rz.textContent='⇲';
    el.appendChild(rz);_attachRz(el,rz);
  });
}

// ── Toggle modo edição ────────────────────────────────────────────────────────
function _toggle() {
  _mode=!_mode;
  document.body.classList.toggle('edit-mode',_mode);
  const btn=document.getElementById('ed-toggle');
  if(btn){btn.textContent=_mode?'✕ Sair':'✎ Editar layout';btn.classList.toggle('ed-active',_mode);}
  const tb=document.getElementById('ed-tb');if(tb)tb.style.display=_mode?'flex':'none';
  document.querySelectorAll('.grid-element').forEach(el=>{el.draggable=_mode;});
  if(_mode) _decorate();
  _enText(_mode);_enSvg(_mode);
}

// ── Undo ──────────────────────────────────────────────────────────────────────
function _doUndo() {
  if(!_undo) return;
  const{pk,overrides,dom}=_undo;_undo=null;
  _st[pk]={overrides};
  document.querySelectorAll('.grid-element').forEach(el=>{
    const id=el.dataset.id;if(!id||!dom[id]) return;
    const s=dom[id];
    if(s.gc)el.style.gridColumn=s.gc;if(s.gr)el.style.gridRow=s.gr;
    el.classList.toggle('ed-hidden',!!s.hid);
  });
  _autoSave(pk);
}

// ── Download JSON (para build pipeline) ──────────────────────────────────────
function _export() {
  const pk=_pk();if(!pk){alert('Aba desconhecida.');return;}
  const ov=(_st[pk]||{}).overrides||{};
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([JSON.stringify({overrides:ov},null,2)],{type:'application/json'}));
  a.download=pk+'.layout.json';a.click();URL.revokeObjectURL(a.href);
}

// ── Observar troca de abas para re-aplicar layout ─────────────────────────────
function _watchTabs() {
  document.querySelectorAll('.tab[data-page]').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      // Aguarda o renderer terminar antes de aplicar overrides
      setTimeout(()=>{
        const pk=btn.dataset.page;if(!pk) return;
        _applyLayout(pk);
        if(_mode){_decorate();_enText(true);_enSvg(true);}
      }, 60);
    });
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
function _inject() {
  const topbar=document.querySelector('.topbar');if(!topbar) return;
  const par=topbar;
  const btn=document.createElement('button');
  btn.id='ed-toggle';btn.className='btn';btn.textContent='✎ Editar layout';
  btn.onclick=_toggle;
  par.appendChild(btn);
  const tb=document.createElement('div');
  tb.id='ed-tb';tb.style.cssText='display:none;gap:6px;align-items:center';
  tb.innerHTML='<button class="btn" id="ed-undo">↩ Desfazer</button><button class="btn" id="ed-exp" title="Exporta JSON para usar com build.py">⬇ Exportar JSON</button>';
  par.appendChild(tb);
  document.getElementById('ed-undo').onclick=_doUndo;
  document.getElementById('ed-exp').onclick=_export;
}

function _init() {
  _loadAll();
  _inject();
  _initDnd();
  _initSvgInp();
  _watchTabs();
  const pk=_pk(); if(pk) _applyLayout(pk);
  // Expõe funções para o módulo de filtros
  window._BI_EDITOR={applyLayout:_applyLayout,decorate:_decorate,enText:_enText,enSvg:_enSvg};
}

if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',_init);
else _init();
})();
"""

# ── CSS dos filtros ───────────────────────────────────────────────────────────

FILTER_CSS = """
/* ── Filtros BI — gerado por build.py ── */
.filters .row   { grid-template-columns: repeat(9,  minmax(0,1fr)) !important; }
.filters .row2  { grid-template-columns: repeat(9,  minmax(0,1fr)) !important; }
@media (max-width:1200px){
  .filters .row  { grid-template-columns: repeat(5, minmax(0,1fr)) !important; }
  .filters .row2 { grid-template-columns: repeat(7, minmax(0,1fr)) !important; }
}

/* Dropdown multi-select */
#flt-dd {
  position:fixed; z-index:1000;
  background:var(--surface); border:1px solid var(--border);
  border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,.14);
  display:flex; flex-direction:column; max-height:300px; min-width:160px;
  font-size:12.5px;
}
.flt-dd-srch { padding:7px 7px 5px; border-bottom:1px solid var(--line-soft); }
.flt-dd-srch input {
  width:100%; box-sizing:border-box; padding:4px 8px;
  border:1px solid var(--border); border-radius:5px;
  font-size:12px; font-family:inherit;
  background:var(--bg,#f8fafc); color:var(--text);
}
.flt-dd-opts { overflow-y:auto; flex:1; padding:3px 0; }
.flt-dd-all {
  display:flex; align-items:center; gap:7px;
  padding:5px 10px; cursor:pointer; font-weight:600;
  border-bottom:1px solid var(--line-soft); margin-bottom:3px;
}
#flt-list label {
  display:flex; align-items:center; gap:7px;
  padding:3px 10px; cursor:pointer; border-radius:4px; margin:0 3px;
}
#flt-list label:hover, .flt-dd-all:hover { background:var(--blue-soft); }
#flt-list input[type=checkbox], .flt-dd-all input[type=checkbox] {
  accent-color:var(--blue); width:13px; height:13px; flex-shrink:0; cursor:pointer;
}
#flt-list label span { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.flt-dd-foot {
  display:flex; align-items:center; justify-content:space-between;
  padding:5px 10px; border-top:1px solid var(--line-soft); gap:8px;
}
.flt-dd-cnt { font-size:11px; color:var(--muted); }
.flt-dd-clr { font-size:11px; font-weight:600; color:var(--blue); background:0; border:0; cursor:pointer; }
.flt-dd-clr:hover { color:#dc2626; }
"""

# ── JS dos filtros ────────────────────────────────────────────────────────────

FILTER_JS = r"""
/* ── Filtros BI — gerado por build.py ── */
(function(){
'use strict';

const _LS = 'bi_filters';
const _REGS = {
  N:  ['AC','AM','AP','PA','RO','RR','TO'],
  NE: ['AL','BA','CE','MA','PB','PE','PI','RN','SE'],
  CO: ['DF','GO','MS','MT'],
  SE: ['ES','MG','RJ','SP'],
  S:  ['PR','RS','SC'],
};
const _ABC  = ['AAA','AA','A','B','BB','C','CC','CCC'];
const _EMPS = ['RC','ME','PV']; // RC=Ideal, ME=Melhor, PV=Pomme Vita
const _SCP  = ['Em Aberto','Baixado'];
const _SAD  = ['ADIANTAMENTO CONCILIADO','ADIANTAMENTO PENDENTE','ADIANTAMENTO ?'];

// ── Estado ────────────────────────────────────────────────────────────────────
const _F0 = ()=>({
  empresa:[],negocio:[],regiao:[],uf:[],filial:[],
  ano:[],periodo:[],abc_forn:[],fornecedor:[],
  cat1:[],cat2:[],cat3:[],cat4:[],cat5:[],
  produto:[],id:[],abc_prod:[],abc_id:[],
  status_cot:[],status_cp:[],status_ad:[],alerta:[]
});
let _F=_F0();
let _vc2=null; // Set de cat2 válidos derivado da hierarquia (null = sem filtro de cat)

function _loadF(){ try{ const s=localStorage.getItem(_LS); if(s) _F=Object.assign(_F0(),JSON.parse(s)); }catch(e){} }

// Pré-computa cat2 válidos a partir da hierarquia completa, cruzando todos os níveis ativos
function _computeVC2(){
  const active=['cat1','cat2','cat3','cat4','cat5'].some(k=>_F[k].length>0);
  if(!active){ _vc2=null; return; }
  let h=_BD('DIM_CATEGORIAS')||_BD('CATEGORIA_R01_HIERARQUIA');
  ['cat1','cat2','cat3','cat4','cat5'].forEach(k=>{ if(_F[k].length) h=h.filter(r=>_F[k].includes(r[k])); });
  _vc2=new Set(h.map(r=>r.cat2).filter(Boolean));
}
function _saveF(){ try{ localStorage.setItem(_LS,JSON.stringify(_F)); }catch(e){} }

// ── Helpers ───────────────────────────────────────────────────────────────────
function _BD(k){ return ((window._BI_DATA_RAW)||{})[k]||[]; }
function _BDF(k){ return (window._BI_DATA||{})[k]||[]; }
function _sum(a,k){ return a.reduce((s,r)=>s+(parseFloat(r[k])||0),0); }
function _uniq(a,k){ return [...new Set(a.map(r=>r[k]).filter(Boolean))]; }
function _yr(s){ const m=String(s||'').match(/(\d{4})/); return m?m[1]:null; }
function _effUfs(){
  if (_F.uf.length) return _F.uf;
  if (_F.regiao.length) return _F.regiao.flatMap(r=>_REGS[r]||[]);
  return [];
}

// ── Predicado de filtro ───────────────────────────────────────────────────────
function _pred(r){
  if (!r) return false;
  const eu=_effUfs();
  if (_F.empresa.length){
    const e=r.empresa?[r.empresa]:(r.empresas||'').split('|').map(x=>x.trim()).filter(Boolean);
    if (!e.some(x=>_F.empresa.includes(x))) return false;
  }
  if (_F.negocio.length  && r.negocio     && !_F.negocio.includes(r.negocio))    return false;
  if (eu.length          && r.uf          && !eu.includes(r.uf))                  return false;
  if (_F.filial.length){ const f=r.filial||r.nome||''; if(f&&!_F.filial.includes(f)) return false; }
  // Filtro de categoria via cat2 derivado da hierarquia (funciona mesmo sem cat1-5 na linha)
  if (_vc2!==null && r.cat2 && !_vc2.has(r.cat2)) return false;
  if (_F.fornecedor.length && r.fornecedor && !_F.fornecedor.includes(r.fornecedor)) return false;
  if (_F.produto.length) {
    const sI=new Set(_F.produto.map(v=>v.split(' - ')[0]));
    const sN=new Set(_F.produto.map(v=>v.split(' - ').slice(1).join(' - ')));
    const ri=String(r.cdproduto||''), rn=String(r.produto||'');
    if ((ri||rn) && !sI.has(ri) && !sN.has(rn)) return false;
  }
  if (_F.id.length) {
    const sI=new Set(_F.id.map(v=>v.split(' - ')[0]));
    const ri=String(r.id||'');
    if (ri && !sI.has(ri)) return false;
  }
  if (_F.abc_forn.length  && r.curva      && !_F.abc_forn.includes(r.curva))      return false;
  if (_F.abc_prod.length  && r.curva_prod && !_F.abc_prod.includes(r.curva_prod)) return false;
  if (_F.abc_id.length    && r.curva_id   && !_F.abc_id.includes(r.curva_id))     return false;
  if (_F.periodo.length   && r.mesano     && !_F.periodo.includes(r.mesano))      return false;
  if (_F.ano.length       && r.mesano     && !_F.ano.includes(_yr(r.mesano)))     return false;
  if (_F.status_cp.length && r.statuspag  && !_F.status_cp.includes(r.statuspag)) return false;
  if (_F.status_ad.length && r.status_conciliacao && !_F.status_ad.includes(r.status_conciliacao)) return false;
  return true;
}

// ── Recálculo de KPIs ─────────────────────────────────────────────────────────
const _KC={
  RESUMO_K01_TOTAL_COMPRADO: ()=>({total_comprado_operacional:_sum(_BDF('RESUMO_R01_POR_MES'),'spend'),crescimento_yoy_pct:0}),
  RESUMO_K02_FORNECEDORES:   ()=>{const s=_BDF('RESUMO_R04_TOP_FORNECEDOR');return{fornecedores_ativos:s.length,ids_unicos:s.length};},
  RESUMO_K04_IMPACTO:        ()=>({imp_cot_total:_sum(_BDF('RESUMO_R03_TOP_CATEGORIA'),'imp_cot')}),
  RESUMO_K05_OPORTUNIDADE:   ()=>({imp_cot_total:_sum(_BDF('RESUMO_R03_TOP_CATEGORIA'),'imp_cot')}),
  RESUMO_K07_FISCAL:         ()=>({fornecedores_ativos:_BDF('RESUMO_R04_TOP_FORNECEDOR').length}),
  RESUMO_K08_CP:             ()=>({cp_aberto:_sum(_BDF('RESUMO_R04_TOP_FORNECEDOR'),'cp_aberto'),cp_titulos:_BDF('RESUMO_R04_TOP_FORNECEDOR').filter(r=>parseFloat(r.cp_aberto||0)>0).length}),
  OPORTUNIDADE_K01_TOTAL:    ()=>({imp_cot_total:_sum(_BDF('OPORTUNIDADE_R01_TABELA'),'imp_cot')}),
  OPORTUNIDADE_K03_ACIMA:    ()=>({ids_comprados_acima_minimo:_BDF('OPORTUNIDADE_R01_TABELA').filter(r=>parseFloat(r.imp_cot||0)>0).length}),
  OPORTUNIDADE_K04_PCT:      ()=>{const s=_BDF('OPORTUNIDADE_R01_TABELA');const t=s.length||1;return{pct_linhas_acima_minimo:(s.filter(r=>parseFloat(r.imp_cot||0)>0).length/t*100).toFixed(1)};},
  FILIAL_K01_TOTAL:          ()=>({total_comprado:_sum(_BDF('FILIAL_R01_RANKING'),'spend')}),
  FILIAL_K02_MEDIA:          ()=>{const s=_BDF('FILIAL_R01_RANKING');return{compra_media_por_filial:s.length?_sum(s,'spend')/s.length:0};},
  FILIAL_K03_MAIOR:          ()=>({maior_filial:(_BDF('FILIAL_R01_RANKING').slice().sort((a,b)=>(parseFloat(b.spend)||0)-(parseFloat(a.spend)||0))[0]||{}).nome||'—'}),
  FILIAL_K04_MAIOR_UF:       ()=>{const m={};_BDF('FILIAL_R01_RANKING').forEach(r=>{m[r.uf]=(m[r.uf]||0)+(parseFloat(r.spend)||0);});const t=Object.entries(m).sort((a,b)=>b[1]-a[1])[0]||[];return{maior_uf:t[0]||'—'};},
  FILIAL_K05_NEGOCIO:        ()=>{const m={};_BDF('FILIAL_R01_RANKING').forEach(r=>{m[r.negocio]=(m[r.negocio]||0)+(parseFloat(r.spend)||0);});const t=Object.entries(m).sort((a,b)=>b[1]-a[1])[0]||[];return{maior_negocio:t[0]||'—'};},
  FORNECEDOR_K01_ATIVOS:     ()=>({fornecedores_ativos:_BDF('FORNECEDOR_R01_TABELA').length}),
  FORNECEDOR_K02_SPEND:      ()=>({spend_curva_aaa_aa_a:_sum(_BDF('FORNECEDOR_R01_TABELA').filter(r=>['AAA','AA','A'].includes(r.curva)),'spend_total')}),
  FORNECEDOR_K03_PCT:        ()=>{const s=_BDF('FORNECEDOR_R01_TABELA');const t=_sum(s,'spend_total')||1;return{pct_spend_top:(_sum(s.filter(r=>['AAA','AA','A'].includes(r.curva)),'spend_total')/t*100).toFixed(1)};},
  FORNECEDOR_K04_CP:         ()=>({forn_com_cp_aberto:_BDF('FORNECEDOR_R01_TABELA').filter(r=>parseFloat(r.cp_aberto||0)>0).length}),
  FORNECEDOR_K05_AD:         ()=>({forn_com_ad_pendente:_BDF('FORNECEDOR_R01_TABELA').filter(r=>parseFloat(r.ad_pendente||0)>0).length}),
  PRODUTO_K01_TOTAL:         ()=>({total_ids:_BDF('PRODUTO_R01_TABELA').length}),
  PRODUTO_K02_PMP:           ()=>{const s=_BDF('PRODUTO_R01_TABELA');return{pmp_medio_cesta:s.length?_sum(s,'pmp_atual')/s.length:0};},
  PRODUTO_K03_VAR:           ()=>({ids_variacao_pmp_gt10pct:_BDF('PRODUTO_R01_TABELA').filter(r=>Math.abs(parseFloat(r.var_pmp_pct||0))>10).length}),
  PRODUTO_K05_INF:           ()=>{const s=_BDF('PRODUTO_R01_TABELA');return{inflacao_media_cesta:s.length?(_sum(s,'var_pmp_pct')/s.length).toFixed(1):0};},
  IMPACTO_K01_TOTAL:         ()=>({imp_cot_total:_sum(_BDF('IMPACTO_R03_TOP_ID'),'imp_cot')}),
  IMPACTO_K02_IDS:           ()=>({ids_com_impacto:_BDF('IMPACTO_R03_TOP_ID').filter(r=>parseFloat(r.imp_cot||0)>0).length}),
  IMPACTO_K03_PCT:           ()=>{const s=_BDF('IMPACTO_R03_TOP_ID');const t=s.length||1;return{pct_linhas_acima_minimo:(s.filter(r=>parseFloat(r.imp_cot||0)>0).length/t*100).toFixed(1)};},
  IMPACTO_K04_UF:            ()=>({uf_lider:(_BDF('IMPACTO_R02_UF').slice().sort((a,b)=>(parseFloat(b.imp_cot)||0)-(parseFloat(a.imp_cot)||0))[0]||{}).uf||'—'}),
  IMPACTO_K05_PROD:          ()=>({top_produto_nome:(_BDF('IMPACTO_R03_TOP_ID').slice().sort((a,b)=>(parseFloat(b.imp_cot)||0)-(parseFloat(a.imp_cot)||0))[0]||{}).produto||'—'}),
  INFLACAO_K01_MEDIA:        ()=>{const s=_BDF('INFLACAO_R04_POR_CAT');return{inflacao_media_pct:s.length?(_sum(s,'inflacao_media_pct')/s.length).toFixed(1):0};},
  INFLACAO_K02_EXP:          ()=>({exposicao_monetaria_12m:_sum(_BDF('INFLACAO_R02_MES_RS'),'exposicao_rs')}),
  INFLACAO_K04_CAT:          ()=>({cat2_mais_inflada:(_BDF('INFLACAO_R04_POR_CAT').slice().sort((a,b)=>(parseFloat(b.inflacao_media_pct)||0)-(parseFloat(a.inflacao_media_pct)||0))[0]||{}).cat2||'—'}),
  FINANCEIRO_K01_ABERTO:     ()=>({cp_aberto_total:_sum(_BDF('FINANCEIRO_R02_FORN'),'cp_aberto')}),
  FINANCEIRO_K02_TIT:        ()=>({cp_titulos:_sum(_BDF('FINANCEIRO_R02_FORN'),'titulos')}),
  FINANCEIRO_K03_VENC:       ()=>({cp_vencido:_sum(_BDF('FINANCEIRO_R02_FORN'),'cp_vencido')}),
  ADIANTAMENTO_K01_TOTAL:    ()=>{const s=_BDF('ADIANTAMENTO_R02_EMP');return{ad_total_12m:_sum(s,'pendente')+_sum(s,'conciliado')};},
  ADIANTAMENTO_K02_CONC:     ()=>({conciliado:_sum(_BDF('ADIANTAMENTO_R02_EMP'),'conciliado')}),
  ADIANTAMENTO_K03_PEND:     ()=>({pendente:_sum(_BDF('ADIANTAMENTO_R02_EMP'),'pendente')}),
  ADIANTAMENTO_K04_PCT:      ()=>{const s=_BDF('ADIANTAMENTO_R02_EMP');const t=(_sum(s,'pendente')+_sum(s,'conciliado'))||1;return{pct_conciliado:(_sum(s,'conciliado')/t*100).toFixed(1)};},
  ADIANTAMENTO_K05_N:        ()=>({n_pendente:_BDF('ADIANTAMENTO_R06_FORN').filter(r=>parseFloat(r.pendente||0)>0).length}),
  SERVICO_K01_TOTAL:         ()=>({total_servicos:_sum(_BDF('SERVICO_R01_UF'),'spend')}),
  SERVICO_K02_FORN:          ()=>({fornecedores_servicos:_BDF('SERVICO_R04_FORN').length}),
  SERVICO_K03_UFS:           ()=>({ufs_atendidas:_BDF('SERVICO_R01_UF').length}),
  SERVICO_K05_CAT:           ()=>({maior_categoria:(_BDF('SERVICO_R03_CAT').slice().sort((a,b)=>(parseFloat(b.spend)||0)-(parseFloat(a.spend)||0))[0]||{}).categoria||'—'}),
};

// ── Opções dos filtros ────────────────────────────────────────────────────────
const _OPTS={
  empresa:    ()=>_EMPS,
  negocio:    ()=>_uniq(_BD('DIM_FILIAIS'),'negocio').filter(Boolean).sort(),
  regiao:     ()=>Object.keys(_REGS),
  uf:         ()=>{
    let u=_F.regiao.length?_F.regiao.flatMap(r=>_REGS[r]||[]):_uniq(_BD('DIM_FILIAIS'),'uf');
    return [...new Set(u)].filter(Boolean).sort();
  },
  filial:     ()=>{
    let d=_BD('DIM_FILIAIS');
    const eu=_effUfs();
    if(eu.length) d=d.filter(r=>eu.includes(r.uf));
    if(_F.negocio.length) d=d.filter(r=>_F.negocio.includes(r.negocio));
    if(_F.empresa.length) d=d.filter(r=>_F.empresa.includes(r.empresa));
    return _uniq(d,'nome').filter(Boolean).sort();
  },
  ano:        ()=>['2024','2025','2026'],
  periodo:    ()=>{
    let a=_uniq(_BD('RESUMO_R01_POR_MES'),'mesano');
    if(_F.ano.length) a=a.filter(m=>_F.ano.includes(_yr(m)));
    return a;
  },
  abc_forn:   ()=>_ABC,
  fornecedor: ()=>{
    let d=_BD('DIM_FORNECEDORES');
    if(_F.abc_forn.length) d=d.filter(r=>_F.abc_forn.includes(r.curva));
    return _uniq(d,'fornecedor').filter(Boolean).sort().slice(0,500);
  },
  cat1:       ()=>_uniq(_BD('DIM_CATEGORIAS'),'cat1').filter(Boolean).sort(),
  cat2:       ()=>{let d=_BD('DIM_CATEGORIAS');if(_F.cat1.length)d=d.filter(r=>_F.cat1.includes(r.cat1));return _uniq(d,'cat2').filter(Boolean).sort();},
  cat3:       ()=>{let d=_BD('DIM_CATEGORIAS');if(_F.cat1.length)d=d.filter(r=>_F.cat1.includes(r.cat1));if(_F.cat2.length)d=d.filter(r=>_F.cat2.includes(r.cat2));return _uniq(d,'cat3').filter(Boolean).sort();},
  cat4:       ()=>{let d=_BD('DIM_CATEGORIAS');if(_F.cat1.length)d=d.filter(r=>_F.cat1.includes(r.cat1));if(_F.cat2.length)d=d.filter(r=>_F.cat2.includes(r.cat2));if(_F.cat3.length)d=d.filter(r=>_F.cat3.includes(r.cat3));return _uniq(d,'cat4').filter(Boolean).sort();},
  cat5:       ()=>{let d=_BD('DIM_CATEGORIAS');['cat1','cat2','cat3','cat4'].forEach(k=>{if(_F[k].length)d=d.filter(r=>_F[k].includes(r[k]));});return _uniq(d,'cat5').filter(Boolean).sort();},
  produto:    ()=>{
    let d=_BD('DIM_PRODUTOS');
    if(_F.abc_prod.length) d=d.filter(r=>_F.abc_prod.includes(r.curva_prod));
    if(_vc2!==null) d=d.filter(r=>_vc2.has(r.cat2));
    // Bidirecional com ID: se ID selecionado, restringe ao produto daquele ID
    if(_F.id.length){
      const sC=new Set(_F.id.map(v=>v.split(' - ')[0].slice(4))); // cdproduto = id[4:]
      d=d.filter(r=>sC.has(r.cdproduto));
    }
    return [...new Set(d.map(r=>`${r.cdproduto} - ${r.produto}`).filter(Boolean))].sort().slice(0,500);
  },
  id:         ()=>{
    let d=_BD('DIM_IDS');
    if(_vc2!==null) d=d.filter(r=>_vc2.has(r.cat2));
    if(_F.abc_id.length) d=d.filter(r=>_F.abc_id.includes(r.curva_id));
    // Filtrar por produto selecionado (nome)
    if(_F.produto.length){
      const sN=new Set(_F.produto.map(v=>v.split(' - ').slice(1).join(' - ')));
      d=d.filter(r=>sN.has(r.produto));
    }
    // Filtrar por empresa (2 primeiros chars do ID) e UF (chars 2-4)
    if(_F.empresa.length) d=d.filter(r=>_F.empresa.includes(r.id.slice(0,2)));
    const eu=_effUfs();
    if(eu.length) d=d.filter(r=>eu.includes(r.id.slice(2,4)));
    return [...new Set(d.map(r=>`${r.id} - ${r.produto}`).filter(Boolean))].sort().slice(0,500);
  },
  abc_prod:   ()=>_ABC,
  abc_id:     ()=>_ABC,
  status_cot: ()=>['Com cotação','Sem cotação','Mono-cotação'],
  status_cp:  ()=>_SCP,
  status_ad:  ()=>_SAD,
  alerta:     ()=>['OK','CP aberto','Sem cotação','Fiscal'],
};

// ── Cascatas: quando fk muda, limpa seleções inválidas downstream ─────────────
const _CASC={
  regiao:['uf','filial','id'], empresa:['filial','id'], negocio:['filial'], uf:['filial','id'],
  ano:['periodo'],
  cat1:['cat2','cat3','cat4','cat5','produto','id'],
  cat2:['cat3','cat4','cat5','produto','id'],
  cat3:['cat4','cat5','produto','id'],
  cat4:['cat5','produto','id'],
  cat5:['produto','id'],
  produto:['id'], id:['produto'],
  abc_forn:['fornecedor'], abc_prod:['produto','id'], abc_id:['id'],
};

function _cascade(fk){
  (_CASC[fk]||[]).forEach(dep=>{
    const opts=_OPTS[dep]();
    _F[dep]=_F[dep].filter(v=>opts.includes(v));
  });
}

// ── Aplicar filtros + re-render ───────────────────────────────────────────────
function _applyF(){
  if(!window._BI_DATA_RAW && window._BI_DATA)
    window._BI_DATA_RAW=Object.assign({},window._BI_DATA);

  // Pré-computa cat2 válidos (usado pelo _pred para todos os tipos de dado)
  _computeVC2();

  // Restaurar dados originais
  Object.keys(window._BI_DATA_RAW||{}).forEach(k=>{ window._BI_DATA[k]=window._BI_DATA_RAW[k]; });

  const active=Object.values(_F).some(v=>v.length>0);
  if(active){
    // Filtrar arrays
    Object.keys(window._BI_DATA).forEach(k=>{
      const d=window._BI_DATA[k];
      if(Array.isArray(d)) window._BI_DATA[k]=d.filter(_pred);
    });
    // Recalcular KPIs
    Object.keys(_KC).forEach(k=>{
      if(k in (window._BI_DATA_RAW||{}))
        try{ window._BI_DATA[k]=_KC[k](); }catch(e){}
    });
  }

  // Rebuild CAT_VAL/CAT_INF para a aba categorias (usa var, não const)
  if(typeof CAT_VAL!=='undefined'){
    const hier=_BDF('CATEGORIA_R01_HIERARQUIA')||[];
    const cv={};
    hier.forEach(r=>{
      ['cat1','cat2','cat3','cat4','cat5'].forEach(k=>{
        const v=r[k]; if(!v) return;
        const code=v.split(' - ')[0].trim().split(' ')[0];
        if(code) cv[code]=Math.round(((cv[code]||0)+(parseFloat(r.spend)||0)/1e6)*10)/10;
      });
    });
    CAT_VAL=cv;
  }
  if(typeof CAT_INF!=='undefined'){
    const inf=_BDF('INFLACAO_R04_POR_CAT')||[];
    const ci={};
    inf.forEach(r=>{
      const code=(r.cat2||'').split(' - ')[0].trim().split(' ')[0];
      if(code) ci[code]=parseFloat(r.inflacao_media_pct)||0;
    });
    CAT_INF=ci;
  }

  // Re-renderizar aba
  const pk=document.querySelector('.tab.active[data-page]')?.dataset.page;
  if(pk){
    const pg=document.getElementById('page');
    if(pg&&typeof pages!=='undefined'&&pages[pk]){
      pg.innerHTML=pages[pk]();
      if(window._BI_EDITOR){
        window._BI_EDITOR.applyLayout(pk);
        if(document.body.classList.contains('edit-mode')){
          window._BI_EDITOR.decorate();
          window._BI_EDITOR.enText(true);
          window._BI_EDITOR.enSvg(true);
        }
      }
    }
  }

  _refreshUI();
  _refreshChips();
}

// ── UI: botões de filtro ───────────────────────────────────────────────────────
const _LBL={
  empresa:'Todas',negocio:'Todos',regiao:'Todas',uf:'Todas',filial:'Todas',
  ano:'Todos',periodo:'Todos',abc_forn:'Todos',fornecedor:'Todos',
  cat1:'Todas',cat2:'Todas',cat3:'Todas',cat4:'Todas',cat5:'Todas',
  produto:'Todos',id:'Todos',abc_prod:'Todos',abc_id:'Todos',
  status_cot:'Todos',status_cp:'Todos',status_ad:'Todos',alerta:'Todos'
};

function _refreshUI(){
  document.querySelectorAll('[data-fk]').forEach(btn=>{
    const fk=btn.dataset.fk; const sel=_F[fk]||[];
    const v=btn.querySelector('.v'); if(!v) return;
    if(!sel.length){ v.textContent=_LBL[fk]||'Todos'; btn.classList.remove('active'); }
    else if(sel.length===1){ v.textContent=String(sel[0]).length>22?String(sel[0]).slice(0,20)+'…':sel[0]; btn.classList.add('active'); }
    else{ v.textContent=`${sel.length} sel.`; btn.classList.add('active'); }
  });
}

// ── UI: chips de filtros ativos ────────────────────────────────────────────────
const _CLBL={
  empresa:'Empresa',negocio:'Negócio',regiao:'Região',uf:'UF',filial:'Filial',
  ano:'Ano',periodo:'Período',abc_forn:'ABC forn.',fornecedor:'Fornecedor',
  cat1:'CAT1',cat2:'CAT2',cat3:'CAT3',cat4:'CAT4',cat5:'CAT5',
  produto:'Produto',id:'ID',abc_prod:'ABC prod.',abc_id:'ABC ID',
  status_cot:'Status cot.',status_cp:'Status CP',status_ad:'Status AD',alerta:'Alerta'
};

function _refreshChips(){
  const el=document.getElementById('appliedTags'); if(!el) return;
  el.innerHTML=Object.entries(_F)
    .filter(([,v])=>v.length>0)
    .map(([k,v])=>`<span class="pill" data-fk="${k}">${_CLBL[k]}: ${v.length>2?v.length+' sel.':v.join(', ')}<span class="x" style="margin-left:4px;opacity:.7;cursor:pointer">✕</span></span>`)
    .join('');
  el.querySelectorAll('.pill').forEach(p=>{
    p.addEventListener('click',()=>{ _F[p.dataset.fk]=[]; _cascade(p.dataset.fk); _saveF(); _applyF(); });
  });
}

// ── Dropdown multi-select ──────────────────────────────────────────────────────
let _ddFk=null;

function _openDD(btn,fk){
  if(_ddFk===fk){ _closeDD(); return; }
  _closeDD();
  _ddFk=fk;
  const opts=(_OPTS[fk]?_OPTS[fk]():[]);
  const sel=_F[fk]||[];
  const dd=document.getElementById('flt-dd');
  const allChk=opts.length>0&&opts.every(o=>sel.includes(o));

  dd.innerHTML=`
    <div class="flt-dd-srch"><input id="flt-q" placeholder="Buscar…" autocomplete="off"></div>
    <div class="flt-dd-opts">
      <label class="flt-dd-all"><input type="checkbox" id="flt-all" ${allChk?'checked':''}><span>Selecionar todos</span></label>
      <div id="flt-list">${opts.map(o=>`<label><input type="checkbox" value="${o}" ${sel.includes(String(o))?'checked':''}><span>${o}</span></label>`).join('')}</div>
    </div>
    <div class="flt-dd-foot"><span class="flt-dd-cnt">${sel.length} selecionado${sel.length!==1?'s':''}</span><button class="flt-dd-clr">Limpar</button></div>`;

  const r=btn.getBoundingClientRect();
  dd.style.cssText=`position:fixed;z-index:9999;background:#fff;border:1px solid var(--line,#e2e8f0);border-radius:8px;box-shadow:0 8px 24px rgba(15,23,42,.14);display:flex;flex-direction:column;left:${r.left}px;top:${r.bottom+3}px;min-width:${Math.max(r.width,180)}px;max-height:300px;font-size:12.5px`;

  requestAnimationFrame(()=>{
    const dr=dd.getBoundingClientRect();
    if(dr.right>window.innerWidth-8) dd.style.left=(window.innerWidth-dr.width-8)+'px';
    if(dr.bottom>window.innerHeight-8) dd.style.top=(r.top-dr.height-3)+'px';
  });

  document.getElementById('flt-q').addEventListener('input',e=>{
    const q=e.target.value.toLowerCase();
    document.querySelectorAll('#flt-list label').forEach(l=>{
      l.style.display=l.querySelector('span').textContent.toLowerCase().includes(q)?'':'none';
    });
  });

  document.getElementById('flt-all').addEventListener('change',e=>{
    const allInputs=[...document.querySelectorAll('#flt-list input')];
    if(e.target.checked){
      allInputs.forEach(cb=>{ cb.checked=true; if(!_F[fk].includes(cb.value)) _F[fk].push(cb.value); });
    } else {
      const vals=allInputs.map(cb=>cb.value);
      _F[fk]=_F[fk].filter(v=>!vals.includes(v));
      allInputs.forEach(cb=>cb.checked=false);
    }
    _updCnt();
  });

  document.getElementById('flt-list').addEventListener('change',e=>{
    if(e.target.type!=='checkbox') return;
    const v=e.target.value;
    if(e.target.checked){ if(!_F[fk].includes(v)) _F[fk].push(v); }
    else _F[fk]=_F[fk].filter(x=>x!==v);
    _updCnt();
  });

  dd.querySelector('.flt-dd-clr').addEventListener('click',()=>{
    _F[fk]=[];
    document.querySelectorAll('#flt-list input').forEach(cb=>cb.checked=false);
    document.getElementById('flt-all').checked=false;
    _updCnt();
  });

  function _updCnt(){
    const c=(_F[fk]||[]).length;
    dd.querySelector('.flt-dd-cnt').textContent=`${c} selecionado${c!==1?'s':''}`;
  }

  dd._onClose=()=>{ _cascade(fk); _saveF(); _applyF(); };
}

function _closeDD(){
  const dd=document.getElementById('flt-dd');
  if(_ddFk&&dd._onClose) dd._onClose();
  dd.style.display='none'; dd._onClose=null; _ddFk=null;
}

// ── Init ──────────────────────────────────────────────────────────────────────
function _init(){
  // Cria div do dropdown
  const dd=document.createElement('div'); dd.id='flt-dd'; dd.style.display='none';
  document.body.appendChild(dd);

  // Fecha dropdown ao clicar fora
  document.addEventListener('click',e=>{
    if(_ddFk&&!document.getElementById('flt-dd').contains(e.target)&&!e.target.closest('[data-fk]'))
      _closeDD();
  });

  // Wiring: botões de filtro
  document.querySelectorAll('[data-fk]').forEach(btn=>{
    btn.addEventListener('click',e=>{ e.stopPropagation(); _openDD(btn,btn.dataset.fk); });
  });

  // Limpar filtros
  const clr=document.getElementById('filtersClear');
  if(clr) clr.addEventListener('click',()=>{ _F=_F0(); _saveF(); _applyF(); });

  // Backup inicial dos dados
  if(window._BI_DATA&&!window._BI_DATA_RAW)
    window._BI_DATA_RAW=Object.assign({},window._BI_DATA);

  // Restaurar filtros salvos
  _loadF();
  _refreshUI();
  _refreshChips();

  // Se há filtros salvos, aplicar
  if(Object.values(_F).some(v=>v.length>0)) _applyF();

  // Integrar com troca de aba
  document.querySelectorAll('.tab[data-page]').forEach(btn=>{
    btn.addEventListener('click',()=>{
      setTimeout(()=>{
        if(Object.values(_F).some(v=>v.length>0)) _applyF();
      }, 90);
    });
  });
}

if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',_init);
else _init();
})();
"""

# ── Substituição do HTML dos filtros ──────────────────────────────────────────

# ── CSS da Aba Relatório ─────────────────────────────────────────────────────

RELATORIO_CSS = """
/* ── Aba Relatório — GovGo v2 layout + BI Design System ── */
.rel-wrap {
  display: grid;
  grid-template-columns: 360px minmax(0,1fr);
  height: calc(100vh - 140px);
  min-height: 480px;
  overflow: hidden;
  background: var(--card,#fff);
  border: 1px solid var(--line,#e2e8f0);
  border-radius: 10px;
}
.rel-side {
  border-right: 1px solid var(--line,#e2e8f0);
  background: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.rel-side-top {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 10px;
  border-bottom: 1px solid var(--line);
  background: var(--head,#f1f5f9);
  flex-shrink: 0;
}
.rel-mode-btn {
  flex: 1;
  padding: 6px 8px;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--muted,#64748b);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 7px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}
.rel-mode-btn.active {
  color: var(--blue,#2563eb);
  background: #fff;
  border-color: var(--line);
  box-shadow: 0 1px 2px rgba(0,0,0,.05);
}
#rel-side-body {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
/* Chat */
.rel-chat-section {
  position: relative; /* para position:absolute do msgs */
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.rel-chat-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-bottom: 1px solid rgba(226,232,240,.5);
  position: relative;
  z-index: 1;
  background: #fff;
  flex-shrink: 0;
}
.rel-chat-lbl {
  font-size: 10.5px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .06em;
}
.rel-msgs {
  position: absolute;
  top: 41px;   /* altura do rel-chat-hd */
  left: 0;
  right: 0;
  bottom: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 12px 10px;
}
.rel-msg { display: flex; margin-bottom: 8px; width: 100%; overflow: hidden; }
.rel-msg.user { justify-content: flex-end; }
.rel-msg.asst { justify-content: flex-start; }
.rel-bubble {
  padding: 8px 10px;
  font-size: 12.5px;
  line-height: 1.45;
  box-shadow: 0 1px 2px rgba(0,0,0,.05);
  overflow-wrap: anywhere;
}
.rel-msg.user .rel-bubble {
  max-width: 82%;
  background: var(--blue,#2563eb);
  color: #fff;
  border: 1px solid var(--blue);
  border-radius: 12px 12px 3px 12px;
}
.rel-msg.asst .rel-bubble {
  max-width: 92%;
  background: #eff6ff;
  color: var(--text);
  border: 1px solid #bfdbfe;
  border-radius: 12px 12px 12px 3px;
}
.rel-msg.asst .rel-bubble.err { background: #fee2e2; border-color: #fca5a5; color: #dc2626; }
.rel-msg-ref {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 5px;
  font-size: 11.5px;
  color: var(--blue);
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.rel-msg-meta { display: flex; align-items: center; gap: 5px; margin-top: 5px; }
.rel-icn-btn {
  width: 26px; height: 26px;
  border: 1px solid var(--line,#e2e8f0);
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--muted);
  padding: 0;
}
.rel-icn-btn:hover { background: #eff6ff; color: var(--blue); }
/* Input */
.rel-input-wrap { flex-shrink: 0; padding: 8px 10px; border-top: 1px solid var(--line); }
.rel-input-box {
  display: grid;
  grid-template-columns: auto minmax(0,1fr) auto;
  align-items: end;
  gap: 8px;
  padding: 7px 10px;
  background: #fff;
  border: 1px solid var(--border,#e2e8f0);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0,0,0,.05);
}
.rel-input-icon { color: var(--muted); font-size: 14px; padding-bottom: 3px; }
.rel-textarea {
  all: unset;
  min-width: 0;
  height: 58px;
  overflow-y: auto;
  font-family: inherit;
  font-size: 12.5px;
  line-height: 1.45;
  color: var(--text);
  white-space: pre-wrap;
}
.rel-textarea::placeholder { color: var(--muted); opacity: .7; }
.rel-send {
  height: 32px;
  padding: 0 14px;
  background: var(--blue);
  color: #fff;
  border: 0;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.rel-send:disabled { opacity: .5; cursor: default; }
.rel-hint { font-size: 10px; color: var(--muted); margin-top: 4px; padding: 0 2px; }
/* Histórico */
.rel-hist-tabs {
  display: grid;
  grid-template-columns: repeat(3,minmax(0,1fr));
  gap: 4px;
  padding: 8px 10px;
  border-bottom: 1px solid var(--line);
  flex-shrink: 0;
}
.rel-hist-tab {
  padding: 5px 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  background: var(--head,#f1f5f9);
  border: 1px solid var(--line);
  border-radius: 7px;
  cursor: pointer;
  text-align: center;
}
.rel-hist-tab.active { color: var(--blue); background: #eff6ff; border-color: #bfdbfe; }
.rel-hist-list { flex: 1; min-height: 0; overflow-y: auto; padding: 6px 10px 10px; }
.rel-hist-item { padding: 8px 10px; margin-bottom: 6px; background: #fff; border: 1px solid var(--line); border-radius: 8px; cursor: pointer; }
.rel-hist-item:hover,.rel-hist-item.active { background: #eff6ff; border-color: #bfdbfe; }
.rel-hi-title { font-size: 12px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rel-hi-sub   { font-size: 11px; color: var(--muted); margin-top: 1px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rel-hi-meta  { display: flex; align-items: center; gap: 6px; margin-top: 4px; font-size: 10.5px; color: var(--muted); }
.rel-hi-chip  { padding: 1px 6px; border-radius: 8px; font-size: 10px; font-weight: 700; }
.rel-hi-chip.ok    { background: #dcfce7; color: #16a34a; }
.rel-hi-chip.error { background: #fee2e2; color: #dc2626; }
/* Main direita */
.rel-main { display: flex; flex-direction: column; min-width: 0; overflow: hidden; background: var(--bg,#f8fafc); }
/* Barra de tabs */
.rel-tabs-bar {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  padding: 0 8px;
  background: var(--head,#f1f5f9);
  border-bottom: 1px solid var(--line);
  overflow-x: auto;
  overflow-y: hidden;
  flex-shrink: 0;
  scrollbar-width: thin;
  min-height: 44px;
}
.rel-rtab {
  flex: 0 0 auto;
  position: relative;
  padding: 8px 24px 8px 12px; /* padding-right extra para o × */
  margin-top: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px 8px 0 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 230px;
}
.rel-rtab:not(.has-x) { padding-right: 12px; }
.rel-rtab.active { color: var(--text); background: #fff; border-color: var(--line); border-bottom-color: #fff; }
.rel-rtab-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 150px; }
.rel-rtab-count {
  font-size: 10.5px; font-weight: 600;
  padding: 1px 5px; background: var(--line); border-radius: 8px;
  color: var(--muted); flex-shrink: 0;
}
.rel-rtab.active .rel-rtab-count { background: var(--blue); color: #fff; }
.rel-rtab-x {
  position: absolute;
  top: 4px; right: 4px;
  width: 14px; height: 14px;
  border: 0; background: transparent; color: var(--muted);
  cursor: pointer; font-size: 11px; padding: 0;
  display: flex; align-items: center; justify-content: center; border-radius: 3px;
  line-height: 1;
}
.rel-rtab-x:hover { background: var(--line); color: var(--text); }
.rel-sp {
  width: 10px; height: 10px;
  border: 2px solid var(--line); border-top-color: var(--blue);
  border-radius: 50%; animation: rl-spin .7s linear infinite; flex-shrink: 0;
}
@keyframes rl-spin { to { transform: rotate(360deg); } }
.rel-new-tab {
  flex-shrink: 0; width: 28px; height: 28px;
  margin: 6px 4px 0; border: 1px solid var(--border,#e2e8f0);
  border-radius: 6px; background: transparent; color: var(--blue);
  cursor: pointer; font-size: 18px;
  display: flex; align-items: center; justify-content: center;
}
.rel-new-tab:hover { background: #eff6ff; }
.rel-asst-tab {
  flex-shrink: 0; margin-left: auto; margin-top: 6px;
  padding: 6px 10px; font-size: 11px; font-weight: 600;
  color: var(--muted); background: transparent;
  border: 1px solid transparent;
  border-radius: 8px 8px 0 0; cursor: pointer;
}
.rel-asst-tab.active { color: var(--blue); background: #fff; border-color: var(--line); border-bottom-color: #fff; }
/* Conteúdo */
.rel-content { flex: 1; min-height: 0; overflow-y: auto; padding: 16px 24px 32px; }
.rel-intro { background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 20px 24px; color: var(--muted); font-size: 13.5px; line-height: 1.6; }
.rel-r-title { font-size: 20px; font-weight: 600; color: var(--text); margin: 0 0 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.rel-r-sub   { font-size: 13px; color: var(--muted); line-height: 1.4; margin-bottom: 14px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
/* SQL block */
.rel-sql-wrap { background: #0f172a; border-radius: 10px; overflow: hidden; margin-bottom: 14px; }
.rel-sql-head { display: flex; align-items: center; padding: 6px 12px; border-bottom: 1px solid rgba(255,255,255,.08); gap: 8px; }
.rel-sql-lbl  { font-size: 10.5px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; flex: 1; }
.rel-sql-copy { font-size: 11px; font-weight: 600; color: #94a3b8; background: transparent; border: 1px solid rgba(255,255,255,.1); border-radius: 5px; padding: 2px 8px; cursor: pointer; }
.rel-sql-copy:hover { color: #fff; }
.rel-sql-pre  { margin: 0; padding: 10px 14px; font-family: 'Cascadia Code','Consolas',monospace; font-size: 12px; line-height: 1.5; color: #e0eaf9; overflow: auto; max-height: 92px; scrollbar-width: thin; white-space: pre-wrap; word-break: break-all; }
/* Tabela */
.rel-tbl-wrap { background: #fff; border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.rel-tbl-hd   { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-bottom: 1px solid rgba(226,232,240,.5); flex-wrap: wrap; }
.rel-chip     { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700; }
.rel-chip.ok  { background: #dcfce7; color: #16a34a; }
.rel-chip.err { background: #fee2e2; color: #dc2626; }
.rel-chip.run { background: #eff6ff; color: var(--blue); }
.rel-rows-info { font-size: 12px; color: var(--muted); }
.rel-spacer   { flex: 1; }
.rel-pager    { display: inline-flex; align-items: center; gap: 3px; }
.rel-pg-btn   { width: 26px; height: 24px; border: 1px solid var(--border); border-radius: 5px; background: #fff; cursor: pointer; font-size: 11px; color: var(--text); display: flex; align-items: center; justify-content: center; }
.rel-pg-btn:disabled { opacity: .4; cursor: default; }
.rel-pg-num   { font-size: 11px; color: var(--muted); padding: 0 4px; }
.rel-act-btn  { padding: 3px 10px; border: 1px solid var(--border); border-radius: 6px; background: #fff; font-size: 11.5px; font-weight: 600; cursor: pointer; color: var(--text); }
.rel-act-btn:hover  { background: #eff6ff; color: var(--blue); border-color: #bfdbfe; }
.rel-act-btn.saved  { background: #eff6ff; color: var(--blue); border-color: #bfdbfe; }
.rel-tbl-scroll { overflow-x: auto; overflow-y: auto; height: 400px; scrollbar-width: thin; }
.rel-table { border-collapse: collapse; width: 100%; }
.rel-table thead { position: sticky; top: 0; z-index: 1; }
.rel-table th { background: var(--head,#f1f5f9); text-align: left; padding: 8px 12px; border-bottom: 1px solid rgba(226,232,240,.5); font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; font-weight: 600; white-space: nowrap; height: 36px; }
.rel-table td { padding: 9px 12px; border-bottom: 1px solid rgba(226,232,240,.5); font-size: 12.5px; color: var(--text); max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; height: 40px; }
.rel-table tbody tr:first-child td { background: #eff6ff; }
.rel-table tbody tr:hover td { background: rgba(37,99,235,.03); }
.rel-err { background: #fee2e2; border: 1px solid #fca5a5; border-radius: 8px; padding: 12px 14px; color: #dc2626; font-size: 13px; margin-bottom: 12px; }
/* Prompt editor */
.rel-prompt-section { display: flex; flex-direction: column; height: 100%; gap: 10px; }
.rel-prompt-hd { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.rel-prompt-info { font-size: 12px; color: var(--muted); flex: 1; }
.rel-prompt-ta { flex: 1; resize: none; font-family: 'Cascadia Code','Consolas',monospace; font-size: 12px; line-height: 1.5; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; background: #fff; color: var(--text); min-height: 200px; }
.rel-prompt-ta:focus { outline: none; border-color: var(--blue); }
/* Barra de progresso linear (durante atualização) */
.rel-lp {
  height: 3px;
  background: var(--blue-soft,#eff6ff);
  overflow: hidden;
  margin-bottom: 10px;
  flex-shrink: 0;
}
.rel-lp::after {
  content: '';
  display: block;
  height: 100%;
  width: 35%;
  background: var(--blue,#2563eb);
  animation: rel-lp-anim 1.4s ease-in-out infinite;
}
@keyframes rel-lp-anim {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}
"""

# ── JS da Aba Relatório ───────────────────────────────────────────────────────

RELATORIO_JS = r"""
/* ── Aba Relatório — gerado por build.py ── */
(function(){
'use strict';

const _RL = (window._BI_NLSQL_URL || 'http://localhost:5001');
const PAGE_SZ = 10;

// SVGs globais reutilizados nos botões
const _SVG_REFRESH = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M23 4v6h-6"/><path d="M20.5 15a9 9 0 1 1-2.1-9.4L23 10"/></svg>';
const _SVG_TRASH   = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"/><path d="m19 6-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>';
const _SVG_CODE    = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>';
const _SVG_SPIN    = '<span class="rel-sp" style="width:13px;height:13px;border-width:2px"></span>';

// ── Estado ─────────────────────────────────────────────────────────────────
const _S = {
  tabs: [],
  activeId: null,
  reports: {},
  chatId: null,
  msgs: [],
  sideMode: 'chat',
  histMode: 'chats',
  chats: [],
  history: [],
  running: false,
  pages: {},
  promptContent: '',
  promptUpdatedAt: '',
  inited: false,
};

// ── API ─────────────────────────────────────────────────────────────────────
async function _api(m, path, body) {
  try {
    const r = await fetch(_RL + path, {
      method: m,
      headers: {'Content-Type': 'application/json'},
      body: body ? JSON.stringify(body) : undefined,
    });
    return r.json();
  } catch(e) { return {ok:false, error:e.message}; }
}

// ── Formatação ──────────────────────────────────────────────────────────────
function _fv(v) {
  const n = parseFloat(v);
  if (isNaN(n)) return String(v ?? '—');
  if (Math.abs(n) >= 1e6) return 'R$ '+(n/1e6).toFixed(1).replace('.',',')+' mi';
  if (Math.abs(n) >= 1e3) return n.toLocaleString('pt-BR',{maximumFractionDigits:2});
  return n.toLocaleString('pt-BR',{maximumFractionDigits:4});
}
function _isN(v){ return v!==null&&v!==''&&v!==undefined&&!isNaN(parseFloat(v)); }
function _ts(s){ if(!s) return ''; try{ return new Date(s).toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'}); }catch(e){return '';} }
const $ = id => document.getElementById(id);
const _esc = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

// ── Tabs de resultado ───────────────────────────────────────────────────────
function _openTab(id){ _S.activeId=id; _renderTabs(); _renderContent(); }

function _closeTab(id){
  const i=_S.tabs.findIndex(t=>t.id===id);
  _S.tabs=_S.tabs.filter(t=>t.id!==id);
  delete _S.reports[id]; delete _S.pages[id];
  if(_S.activeId===id) _S.activeId=_S.tabs[Math.max(0,i-1)]?.id||'intro';
  _renderTabs(); _renderContent();
}

function _addTab(title, st){
  const id='t'+Date.now();
  _S.tabs.push({id, title:title||'…', st:st||'running', count:0, closable:true});
  _S.activeId=id; _S.pages[id]=0;
  _renderTabs(); _renderContent();
  return id;
}

function _patchTab(id, patch){
  const t=_S.tabs.find(t=>t.id===id); if(t) Object.assign(t,patch);
  _renderTabs();
}

// ── Enviar pergunta ─────────────────────────────────────────────────────────
async function _submit(){
  const ta=$('rel-q'); if(!ta) return;
  const q=ta.value.trim(); if(!q||_S.running) return;
  ta.value=''; ta.style.height='58px';
  _S.running=true; _updateSend();

  const uid='u'+Date.now();
  _S.msgs.push({id:uid, role:'user', text:q});
  const aid='a'+(Date.now()+1);
  _S.msgs.push({id:aid, role:'asst', text:'Gerando SQL…', st:'running'});
  _renderMsgs();

  const tabId=_addTab(q.slice(0,40),'running');

  const res=await _api('POST','/run',{question:q, chatId:_S.chatId||undefined});
  _S.running=false; _updateSend();

  const am=_S.msgs.find(m=>m.id===aid);

  // Falha de rede — servidor não está rodando
  if(!res.ok && (String(res.error||'').includes('fetch')||String(res.error||'').includes('Failed')||String(res.error||'').includes('Network'))) {
    _closeTab(tabId);
    if(am){ am.text='⚠️ Servidor NL-SQL não está respondendo.\n\nInicie com:\npython nlsql/server.py'; am.st='error'; }
    _renderMsgs(); return;
  }

  if(res.ok&&res.report){
    const r=res.report;
    _S.chatId=res.chat?.id||_S.chatId;
    _S.reports[tabId]=r;
    if(res.history) _S.history=res.history;
    if(res.chats)   _S.chats=res.chats;
    _patchTab(tabId,{title:r.title||q.slice(0,40), st:r.status, count:r.rowCount||0});
    if(am){ am.text=r.title||(r.status==='ok'?'Concluído':r.error||'Erro'); am.st=r.status; am.sql=r.sql; am.tabId=tabId; am.rid=r.id; am.refTitle=r.title; am.rowCount=r.rowCount; }
  } else {
    _patchTab(tabId,{title:'Erro',st:'error',count:0});
    if(am){ am.text=res.error||'Erro ao processar.'; am.st='error'; }
  }
  _renderMsgs(); _renderContent();
}

function _updateSend(){ const b=$('rel-send'); if(b) b.disabled=_S.running; }

// ── Render: mensagens ───────────────────────────────────────────────────────
function _renderMsgs(){
  const el=$('rel-msgs'); if(!el) return;
  if(!_S.msgs.length){
    el.innerHTML='<div style="text-align:center;color:var(--muted);font-size:12px;padding:20px 12px">Faça uma pergunta abaixo.<br>O resultado aparece nas abas à direita.</div>';
    return;
  }
  el.innerHTML=_S.msgs.map(m=>{
    const isU=m.role==='user';

    // Mensagem do usuário: bolha azul simples
    if(isU) return `<div class="rel-msg user"><div class="rel-bubble">${_esc(m.text)}</div></div>`;

    // Assistente rodando: bolha com spinner
    if(m.st==='running') return `<div class="rel-msg asst"><div class="rel-bubble"><span class="rel-sp" style="margin-right:6px;vertical-align:middle"></span>Gerando SQL…</div></div>`;

    // Assistente com erro: bolha de erro
    if(m.st==='error') return `<div class="rel-msg asst"><div class="rel-bubble err">${_esc(m.text)}</div></div>`;

    // Assistente com resultado ok: card igual aos boxes do histórico
    // Referência por m.id — evita SQL inline no onclick (aspas simples quebram o handler)
    const SVG_REF=_SVG_REFRESH, SVG_SQL=_SVG_CODE;
    return `<div class="rel-msg asst" style="width:95%">
      <div class="rel-hist-item" style="display:flex;align-items:flex-start;gap:8px;cursor:pointer;width:100%;box-sizing:border-box"
           onclick="window._RL.openOrLoad('${m.tabId||''}','${m.rid||''}')">
        <div style="flex:1;min-width:0">
          <div class="rel-hi-title">${_esc(m.refTitle||m.text||'Resultado')}</div>
          <div class="rel-hi-sub">${_ts(new Date().toISOString())}</div>
          <div class="rel-hi-meta">
            <span class="rel-hi-chip ok">ok</span>
            ${m.rowCount!=null?`<span>${m.rowCount.toLocaleString()} linha${m.rowCount!==1?'s':''}</span>`:''}
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:3px;flex-shrink:0">
          <button class="rel-icn-btn" data-mid="${m.id}" title="Atualizar resultado"
                  onclick="event.stopPropagation();window._RL.chatRefresh('${m.id}')">${SVG_REF}</button>
          ${m.sql?`<button class="rel-icn-btn" title="Copiar SQL"
                  onclick="event.stopPropagation();window._RL.copyMsgSQL('${m.id}')">${SVG_SQL}</button>`:''}
        </div>
      </div>
    </div>`;
  }).join('');
  requestAnimationFrame(()=>{ el.scrollTop=el.scrollHeight; });
}

// ── Render: barra de abas ───────────────────────────────────────────────────
function _renderTabs(){
  const el=$('rel-tabs-bar'); if(!el) return;
  const isPrompt=_S.activeId==='__prompt';
  const ts=_S.tabs.map(t=>{
    const act=t.id===_S.activeId;
    const spin=t.st==='running'?'<span class="rel-sp"></span>':'';
    const cnt=(t.st!=='running'&&t.count>0)?`<span class="rel-rtab-count">${t.count}</span>`:'';
    const cls=t.closable?`<button class="rel-rtab-x" onclick="event.stopPropagation();window._RL.closeTab('${t.id}')">×</button>`:'';
    return `<button class="rel-rtab${act?' active':''}${t.closable?' has-x':''}" onclick="window._RL.openTab('${t.id}')">${spin}<span class="rel-rtab-title">${_esc(t.title)}</span>${cnt}${cls}</button>`;
  }).join('');
  el.innerHTML=ts+
    '<button class="rel-new-tab" title="Nova consulta" onclick="window._RL.newQuery()">+</button>'+
    `<button class="rel-asst-tab${isPrompt?' active':''}" onclick="window._RL.showPrompt()">Assistente</button>`;
}

// ── Render: conteúdo direita ────────────────────────────────────────────────
function _renderContent(){
  const el=$('rel-content'); if(!el) return;
  if(_S.activeId==='__prompt'){ _renderPrompt(el); return; }
  if(!_S.activeId||!_S.reports[_S.activeId]){
    el.innerHTML='<div class="rel-intro"><strong>BI de Suprimentos · Relatório</strong><br><br>Use o chat à esquerda para fazer perguntas em português.<br>O SQL gerado e os resultados aparecem aqui, em abas.<br><br><em>Exemplos:</em><br>· "Top 10 fornecedores por gasto em SP"<br>· "Quantos IDs únicos comprados em 2025?"<br>· "Impacto de cotação por categoria no último trimestre"</div>';
    return;
  }
  const r=_S.reports[_S.activeId], tid=_S.activeId;
  if(r.status==='running'){
    el.innerHTML='<div style="display:flex;align-items:center;gap:12px;padding:20px;color:var(--muted)"><span class="rel-sp" style="width:18px;height:18px;border-width:3px"></span>Gerando SQL e consultando o Zoho…</div>';
    return;
  }
  let h=`<h2 class="rel-r-title">${_esc(r.title||r.question||'Resultado')}</h2>`;
  if(r.subtitle) h+=`<div class="rel-r-sub">${_esc(r.subtitle)}</div>`;
  else h+='<div style="margin-bottom:14px"></div>';
  if(r.status==='error') h+=`<div class="rel-err">${_esc(r.error||'Erro desconhecido')}</div>`;
  if(r.sql){
    const safe=r.sql.replace(/\\/g,'\\\\').replace(/`/g,"'");
    h+=`<div class="rel-sql-wrap"><div class="rel-sql-head"><span class="rel-sql-lbl">Comando SQL</span><button class="rel-sql-copy" onclick="navigator.clipboard.writeText(\`${safe}\`)">Copiar</button></div><pre class="rel-sql-pre">${_esc(r.sql)}</pre></div>`;
  }
  if(r.status==='ok'){
    const cols=r.columns||[], rows=r.rows||[];
    const total=r.rowCount||rows.length;
    const pg=_S.pages[tid]||0;
    const pgs=Math.ceil(rows.length/PAGE_SZ);
    const vis=rows.slice(pg*PAGE_SZ,(pg+1)*PAGE_SZ);
    const ths=cols.map(c=>`<th>${_esc(c)}</th>`).join('');
    const trs=vis.map(row=>'<tr>'+cols.map(c=>{
      const v=row[c]??'';
      const d=_isN(v)?_fv(v):_esc(String(v));
      const s=_isN(v)?' style="text-align:right;font-variant-numeric:tabular-nums"':'';
      return `<td${s}>${d}</td>`;
    }).join('')+'</tr>').join('');
    let pgr='';
    if(pgs>1) pgr=`<div class="rel-pager"><button class="rel-pg-btn" ${pg===0?'disabled':''} onclick="window._RL.page('${tid}',0)">«</button><button class="rel-pg-btn" ${pg===0?'disabled':''} onclick="window._RL.page('${tid}',${pg-1})">‹</button><span class="rel-pg-num">${pg+1}/${pgs}</span><button class="rel-pg-btn" ${pg>=pgs-1?'disabled':''} onclick="window._RL.page('${tid}',${pg+1})">›</button><button class="rel-pg-btn" ${pg>=pgs-1?'disabled':''} onclick="window._RL.page('${tid}',${pgs-1})">»</button></div>`;
    const sv=r.saved;
    h+=`<div class="rel-tbl-wrap"><div class="rel-tbl-hd"><span class="rel-chip ok">Executado</span><span class="rel-rows-info">${total.toLocaleString()} linha${total!==1?'s':''} · ${r.elapsedMs||0}ms</span><span class="rel-spacer"></span>${pgr}<button class="rel-act-btn" onclick="window._RL.export_('${tid}')">⬇ CSV</button><button class="rel-act-btn${sv?' saved':''}" onclick="window._RL.fav('${tid}')">${sv?'Salvo':'Salvar'}</button></div><div class="rel-tbl-scroll"><table class="rel-table"><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table></div></div>`;
  }
  el.innerHTML=h;
}

// ── Render: prompt editor ───────────────────────────────────────────────────
function _renderPrompt(c){
  const mt=_S.promptUpdatedAt?'Atualizado: '+_ts(_S.promptUpdatedAt):'';
  c.innerHTML=`<div class="rel-prompt-section"><div class="rel-prompt-hd"><span class="rel-prompt-info">nlsql/prompts/bi_suprimentos_sql.md &nbsp;·&nbsp; ${mt}</span><button class="rel-act-btn" id="rl-psave">Salvar</button><button class="rel-act-btn" id="rl-prst">↩ Restaurar</button></div><textarea class="rel-prompt-ta" id="rl-pta" spellcheck="false">${_esc(_S.promptContent)}</textarea></div>`;
  $('rl-psave').onclick=async()=>{ const v=$('rl-pta').value; const r=await _api('POST','/prompt',{content:v}); if(r.ok){_S.promptContent=v;alert('Prompt salvo! Próximas consultas usam o novo prompt.');}else alert('Erro: '+(r.error||'')); };
  $('rl-prst').onclick=async()=>{ if(!confirm('Restaurar backup?')) return; const r=await _api('POST','/prompt/reset'); if(r.ok){const g=await _api('GET','/prompt');if(g.ok){_S.promptContent=g.content;_S.promptUpdatedAt=g.updatedAt;}_renderPrompt(c);}else alert('Sem backup.'); };
}

// ── Render: sidebar histórico ───────────────────────────────────────────────
function _renderHist(){
  const el=$('rel-side-body'); if(!el) return;
  const m=_S.histMode;
  let items=[];
  if(m==='chats') items=_S.chats.map(c=>({id:c.id,title:c.title||'Chat',sub:_ts(c.updatedAt),type:'chat'}));
  else if(m==='reports') items=_S.history.map(r=>({id:r.id,title:r.title||r.question,sub:_ts(r.createdAt),type:'report',chip:r.status,rows:r.rowCount}));
  else items=_S.history.filter(r=>r.saved).map(r=>({id:r.id,title:r.title||r.question,sub:_ts(r.createdAt),type:'report',chip:r.status,rows:r.rowCount}));
  const list=items.length?items.map(it=>{
    const isReport=it.type==='report';
    const btns=isReport?`<div style="display:flex;flex-direction:column;gap:3px;flex-shrink:0">
      <button class="rel-icn-btn" data-hid="${it.id}" title="Atualizar resultado" onclick="event.stopPropagation();window._RL.histRefresh('${it.id}')">${_SVG_REFRESH}</button>
      <button class="rel-icn-btn" title="Apagar" onclick="event.stopPropagation();window._RL.histDel('${it.id}')">${_SVG_TRASH}</button>
    </div>`:'';
    return `<div class="rel-hist-item" style="display:flex;align-items:flex-start;gap:8px" onclick="window._RL.histOpen('${it.id}','${it.type}')">
      <div style="flex:1;min-width:0">
        <div class="rel-hi-title">${_esc(it.title)}</div>
        ${it.sub?`<div class="rel-hi-sub">${it.sub}</div>`:''}
        <div class="rel-hi-meta">
          ${it.chip?`<span class="rel-hi-chip ${it.chip}">${it.chip==='ok'?'✓':'✗'}</span>`:''}
          ${it.rows!=null?`<span>${it.rows.toLocaleString()} linhas</span>`:''}
        </div>
      </div>
      ${btns}
    </div>`;
  }).join(''):'<div style="padding:20px;text-align:center;color:var(--muted);font-size:12px">Vazio</div>';
  el.innerHTML=`<div style="display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden"><div class="rel-hist-tabs"><button class="rel-hist-tab${m==='chats'?' active':''}" onclick="window._RL.histMode('chats')">Chats</button><button class="rel-hist-tab${m==='reports'?' active':''}" onclick="window._RL.histMode('reports')">Relatórios</button><button class="rel-hist-tab${m==='saved'?' active':''}" onclick="window._RL.histMode('saved')">Favoritos</button></div><div class="rel-hist-list">${list}</div></div>`;
}

// ── Render: sidebar chat ────────────────────────────────────────────────────
function _renderChat(){
  const el=$('rel-side-body'); if(!el) return;
  el.innerHTML=`<div class="rel-chat-section"><div class="rel-chat-hd"><div class="rel-chat-lbl">Chat</div><button class="btn" onclick="window._RL.newChat()" style="padding:3px 10px;font-size:11px">+ Novo</button></div><div class="rel-msgs" id="rel-msgs"></div></div><div class="rel-input-wrap"><div class="rel-input-box"><span class="rel-input-icon"></span><textarea class="rel-textarea" id="rel-q" rows="3" placeholder="Faça uma pergunta em português… Ex: Top 10 fornecedores por gasto em SP"></textarea><button class="rel-send" id="rel-send">Enviar</button></div><div class="rel-hint">Enter para enviar · Shift+Enter nova linha · ${_RL}</div></div>`;
  const ta=$('rel-q'), btn=$('rel-send');
  if(ta) ta.addEventListener('keydown',e=>{ if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();_submit();} });
  if(btn) btn.addEventListener('click',_submit);
  _renderMsgs();
}

function _renderSide(){
  if(_S.sideMode==='chat') _renderChat();
  else _renderHist();
  document.querySelectorAll('.rel-mode-btn').forEach(b=>b.classList.toggle('active',b.dataset.mode===_S.sideMode));
}

// ── Globals ─────────────────────────────────────────────────────────────────
window._RL = {
  openTab:  id => _openTab(id),
  closeTab: id => _closeTab(id),
  newQuery: () => { _S.activeId=null; _renderTabs(); _renderContent(); setTimeout(()=>{ const t=$('rel-q');if(t)t.focus(); },60); },
  page:     (id,p) => { _S.pages[id]=Math.max(0,p); _renderContent(); },
  export_:  id => { const r=_S.reports[id]; if(r?.id) window.open(`${_RL}/export/${r.id}`,'_blank'); },
  fav:      async id => { const r=_S.reports[id]; if(!r) return; const res=await _api('POST',`/favorites/${r.id}`); if(res.ok){r.saved=res.saved;_renderContent();} },
  histMode: m => { _S.histMode=m; _renderHist(); },
  refreshHist: async () => { const r=await _api('GET','/history'); if(r.ok){_S.history=r.history||[];_S.chats=r.chats||[];_renderHist();} },
  histOpen: async (id,type) => {
    if(type==='chat'){ const c=_S.chats.find(c=>c.id===id); if(c){_S.chatId=c.id;_S.msgs=c.messages||[];_S.sideMode='chat';_renderSide();} return; }
    let r=_S.history.find(h=>h.id===id);
    if(!r||!r.columns){ const res=await _api('GET',`/history/${id}`); if(res.ok) r=res.report; }
    if(!r) return;
    const tid='th'+id.slice(0,8);
    if(!_S.tabs.find(t=>t.id===tid)) _S.tabs.push({id:tid,title:r.title||r.question||'Relatório',st:r.status,count:r.rowCount||0,closable:true});
    _S.reports[tid]=r; _S.pages[tid]=0; _S.activeId=tid;
    _renderTabs(); _renderContent();
  },
  newChat:    () => { _S.chatId=null; _S.msgs=[]; _renderMsgs(); },
  // Abre tab existente ou carrega do histórico se a tab foi fechada
  openOrLoad: (tabId, rid) => {
    if(tabId && _S.tabs.find(t=>t.id===tabId)) { _openTab(tabId); }
    else if(rid) { window._RL.histOpen(rid,'report'); }
  },

  // Copiar SQL de uma mensagem do chat (por msgId — evita SQL inline no onclick)
  copyMsgSQL: msgId => {
    const m=_S.msgs.find(m=>m.id===msgId); if(m?.sql) navigator.clipboard.writeText(m.sql);
  },

  // Re-executa SQL do card do chat via msgId (não SQL inline)
  chatRefresh: async msgId => {
    const m=_S.msgs.find(m=>m.id===msgId); if(!m?.sql) return;
    // Spinner no botão
    const btn=document.querySelector(`[data-mid="${msgId}"]`);
    if(btn){ btn.innerHTML=_SVG_SPIN; btn.disabled=true; }
    // Barra de progresso linear na área de resultado se tab ativa
    if(m.tabId && _S.activeId===m.tabId){ const c=$('rel-content'); if(c){ const p=document.createElement('div'); p.id='rel-lp'; p.className='rel-lp'; c.prepend(p); } }
    const res=await _api('POST','/execute',{sql:m.sql});
    document.getElementById('rel-lp')?.remove();
    if(btn){ btn.innerHTML=_SVG_REFRESH; btn.disabled=false; }
    if(res.ok && m.tabId){
      if(_S.reports[m.tabId]){ _S.reports[m.tabId].rows=res.rows; _S.reports[m.tabId].rowCount=res.rowCount; _S.reports[m.tabId].elapsedMs=res.elapsedMs; }
      const t=_S.tabs.find(t=>t.id===m.tabId); if(t){t.count=res.rowCount||0;}
      _renderTabs(); if(_S.activeId===m.tabId) _renderContent();
    }
  },

  histDel: async id => {
    const res=await _api('DELETE',`/history/${id}`);
    if(res.ok){ _S.history=_S.history.filter(h=>h.id!==id); _renderHist(); }
  },

  histRefresh: async id => {
    const r=_S.history.find(h=>h.id===id); if(!r?.sql) return;
    // Spinner no botão de refresh deste item
    const btn=document.querySelector(`[data-hid="${id}"]`);
    if(btn){ btn.innerHTML=_SVG_SPIN; btn.disabled=true; }
    // Barra de progresso se tab deste relatório estiver ativa
    const tid=Object.keys(_S.reports).find(k=>_S.reports[k]?.id===id);
    if(tid && _S.activeId===tid){ const c=$('rel-content'); if(c){ const p=document.createElement('div'); p.id='rel-lp'; p.className='rel-lp'; c.prepend(p); } }
    const res=await _api('POST','/execute',{sql:r.sql});
    document.getElementById('rel-lp')?.remove();
    if(btn){ btn.innerHTML=_SVG_REFRESH; btn.disabled=false; }
    if(res.ok){
      r.rows=res.rows; r.rowCount=res.rowCount; r.elapsedMs=res.elapsedMs; r.status='ok';
      if(tid){ _S.reports[tid]=Object.assign(_S.reports[tid],{rows:res.rows,rowCount:res.rowCount,elapsedMs:res.elapsedMs}); if(_S.activeId===tid) _renderContent(); }
      _renderHist();
    }
  },
  showPrompt: async () => {
    const r=await _api('GET','/prompt');
    if(r.ok){_S.promptContent=r.content;_S.promptUpdatedAt=r.updatedAt;}
    else _S.promptContent='# Servidor NL-SQL não está respondendo.\n# Inicie com: python nlsql/server.py\n\n# Quando o servidor estiver rodando, o prompt aparecerá aqui.';
    _S.activeId='__prompt'; _renderTabs(); _renderContent();
  },
};

// ── Init ────────────────────────────────────────────────────────────────────
async function _init(){
  const first=!_S.inited; _S.inited=true;
  // Esconder filtros + remover padding-bottom do .app (só na aba Relatório)
  const _flt=document.getElementById('filters'); if(_flt) _flt.style.display='none';
  const _app=document.querySelector('.app'); if(_app) _app.style.paddingBottom='0';
  if(first){ const r=await _api('GET','/history'); if(r.ok){_S.history=r.history||[];_S.chats=r.chats||[];} }
  document.querySelectorAll('.rel-mode-btn').forEach(b=>{
    b.addEventListener('click',()=>{
      _S.sideMode=b.dataset.mode;
      _renderSide();
      // Ao abrir Histórico, sempre tenta carregar do servidor
      if(b.dataset.mode==='history') window._RL.refreshHist();
    });
  });
  _renderSide(); _renderTabs(); _renderContent();
}

if(typeof pages!=='undefined'){
  pages['relatorio']=()=>`
<div class="rel-wrap">
  <aside class="rel-side">
    <div class="rel-side-top">
      <button class="rel-mode-btn active" data-mode="chat">Chat</button>
      <button class="rel-mode-btn" data-mode="history">Histórico</button>
    </div>
    <div id="rel-side-body" style="display:flex;flex-direction:column;flex:1;min-height:0;overflow:hidden"></div>
  </aside>
  <main class="rel-main">
    <div class="rel-tabs-bar" id="rel-tabs-bar"></div>
    <div class="rel-content" id="rel-content"></div>
  </main>
</div>`;
  // Esconder/mostrar filtros ao entrar/sair da aba Relatório
  document.addEventListener('click',e=>{
    const tab=e.target.closest('.tab[data-page]');
    if(!tab) return;
    const isRel = tab.dataset.page==='relatorio';
    const filters=document.getElementById('filters');
    if(filters) filters.style.display = isRel ? 'none' : '';
    const app=document.querySelector('.app');
    if(app) app.style.paddingBottom = isRel ? '0' : '';
    if(isRel) setTimeout(_init,60);
  });
}

})();
"""

def replace_filter_html(html):
    """Substitui o bloco .filters do v4 com as novas linhas de filtros."""
    new_filters = """<div class="filters" id="filters">
    <div class="row" id="filterRow1">
      <div class="f"><label>Empresa</label><button class="pick" data-fk="empresa"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Negócio</label><button class="pick" data-fk="negocio"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Região</label><button class="pick" data-fk="regiao"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>UF</label><button class="pick" data-fk="uf"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Filial</label><button class="pick" data-fk="filial"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Ano</label><button class="pick" data-fk="ano"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Período</label><button class="pick" data-fk="periodo"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>ABC fornecedor</label><button class="pick" data-fk="abc_forn"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Fornecedor</label><button class="pick" data-fk="fornecedor"><span class="v">Todos</span><span class="caret">▾</span></button></div>
    </div>
    <div class="row row2" id="filterRow2">
      <div class="f"><label>CAT 1</label><button class="pick" data-fk="cat1"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>CAT 2</label><button class="pick" data-fk="cat2"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>CAT 3</label><button class="pick" data-fk="cat3"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>CAT 4</label><button class="pick" data-fk="cat4"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>CAT 5</label><button class="pick" data-fk="cat5"><span class="v">Todas</span><span class="caret">▾</span></button></div>
      <div class="f"><label>Produto</label><button class="pick" data-fk="produto"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>ID</label><button class="pick" data-fk="id"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>ABC produto</label><button class="pick" data-fk="abc_prod"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f"><label>ABC ID</label><button class="pick" data-fk="abc_id"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f" style="display:none"><label>Status cotação</label><button class="pick" data-fk="status_cot"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f" style="display:none"><label>Status CP</label><button class="pick" data-fk="status_cp"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f" style="display:none"><label>Status AD</label><button class="pick" data-fk="status_ad"><span class="v">Todos</span><span class="caret">▾</span></button></div>
      <div class="f" style="display:none"><label>Tipo alerta</label><button class="pick" data-fk="alerta"><span class="v">Todos</span><span class="caret">▾</span></button></div>
    </div>
    <div class="filter-foot">
      <div><button class="filters-toggle open" id="advToggle"><span>Filtros avançados</span><span class="chev">▾</span></button></div>
      <div class="applied" id="appliedTags"></div>
      <button class="filters-clear" id="filtersClear">Limpar filtros</button>
    </div>
  </div>"""
    return re.sub(
        r'<div class="filters" id="filters">[\s\S]*?(?=\s*<!-- ===== Page)',
        new_filters + '\n\n  ',
        html, count=1
    )

# ── Injeção no HTML ───────────────────────────────────────────────────────────

def inject_css(html, css):
    """Injeta CSS antes do </style>."""
    return html.replace("</style>", css + "\n</style>", 1)

def inject_before_script_end(html, js):
    """Injeta JS antes do último </script>."""
    pos = html.rfind("</script>")
    if pos == -1: return html + f"\n<script>\n{js}\n</script>"
    return html[:pos] + "\n" + js + "\n" + html[pos:]

def inject_relatorio_tab(html):
    """Adiciona botão da aba Relatório no nav, URL do servidor e fix do topbar stamp."""
    # Aba Relatório no nav
    html = html.replace(
        '<button class="tab" data-page="qualidade">Dados</button>',
        '<button class="tab" data-page="qualidade">Dados</button>\n    <button class="tab" data-page="relatorio">Relatório</button>',
        1
    )
    # URL do servidor NL-SQL + stamp encostado ao título, 1 linha só
    topbar_fix = """<script>
window._BI_NLSQL_URL = "http://localhost:5001";
(function(){
  function _fixStamp(){
    var stamp  = document.querySelector('.topbar .stamp');
    var brand  = document.querySelector('.topbar .brand');
    var topbar = document.querySelector('.topbar');
    if(!stamp || !brand || !topbar) return;
    // Move stamp para logo após brand — encostado ao título
    stamp.remove();
    brand.insertAdjacentElement('afterend', stamp);
    // Grid: brand(auto) stamp(auto) search(1fr — preenche o espaço do meio) botões(auto)
    topbar.style.gridTemplateColumns = 'auto auto 1fr auto auto auto auto auto auto';
    stamp.style.cssText = 'font-size:11px;color:var(--muted,#64748b);white-space:nowrap;padding:0 2px 0 0;align-self:center';
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',_fixStamp);
  else _fixStamp();
})();
</script>"""
    html = html.replace("</head>", topbar_fix + "\n</head>", 1)
    return html

def update_timestamp(html):
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return re.sub(r"Atualizado em <b>[^<]*</b>",
                  f"Atualizado em <b>{now_str}</b>", html, count=1)

def replace_mock_arrays(html, indexes):
    """Substitui arrays de dados mockados do v4 pelos dados reais das fontes principais."""
    # FORN → fornecedor tabela principal
    forn_data = load_elem_data("06_fornecedor", "06_fornecedor_r01_tabela_principal.csv") or []
    forn_js = []
    for r in forn_data[:15]:
        emps = [e for e in r.get("empresas","").split("|") if e]
        forn_js.append({
            "n": r.get("fornecedor",""), "oficial": r.get("fornecedor",""),
            "cnpj": r.get("cdforneced",""), "emps": emps or ["RC"],
            "regiao": "SE", "curva": r.get("curva",""),
            "valor": int(float(r.get("spend_total",0) or 0)),
            "regime": "—", "cred": "Pendente",
            "cat": "|".join(r.get("categorias_top","").split("|")[:2]),
            "alerts": ["—"]
        })
    if forn_js:
        html = re.sub(r"const FORN\s*=\s*\[[\s\S]*?\];",
                      f"const FORN = {json.dumps(forn_js, ensure_ascii=False)};", html, count=1)

    # PRODS → produto tabela principal (com serie PMP)
    prods_data = load_elem_data("07_produto", "07_produto_r01_tabela_principal.csv") or []
    prods_js = []
    for r in prods_data[:12]:
        try: serie = json.loads(r.get("pmp_serie","[]") or "[]")
        except: serie = []
        if len(serie) < 13: serie = [float(r.get("pmp_atual",0))] * 13
        prods_js.append({
            "p": r.get("produto",""), "id": r.get("cdproduto",""),
            "cat": r.get("cat2",""), "cId": r.get("curva_id",""),
            "cP": r.get("curva_prod",""),
            "pmp": round(float(r.get("pmp_atual",0) or 0), 2),
            "var12": round(float(r.get("var_pmp_pct",0) or 0), 1),
            "imp": int(float(r.get("imp_cot",0) or 0)),
            "serie": [round(float(v),2) for v in serie[:13]],
        })
    if prods_js:
        html = re.sub(r"const PRODS\s*=\s*\[[\s\S]*?\];",
                      f"const PRODS = {json.dumps(prods_js, ensure_ascii=False)};", html, count=1)

    # OPP → oportunidades tabela principal
    opp_data = load_elem_data("02_oportunidade", "02_oportunidade_r01_tabela_principal.csv") or []
    opp_js = [{"tipo": r.get("tipo",""), "prio": "Alta" if str(r.get("prioridade","3")) in ("1","2") else "Média",
                "id": r.get("id",""), "prod": r.get("produto",""),
                "fAtual": r.get("fornecedor_atual",""), "menor": float(r.get("preco_minimo",0) or 0),
                "imp": int(float(r.get("imp_cot",0) or 0)), "ev": r.get("cat2",""),
                "acao": "Renegociar", "stat": "Aberto"} for r in opp_data[:12]]
    if opp_js:
        html = re.sub(r"const OPP\s*=\s*\[[\s\S]*?\];",
                      f"const OPP = {json.dumps(opp_js, ensure_ascii=False)};", html, count=1)

    # FILIAIS
    fil_data = load_elem_data("04_filial", "04_filial_r01_ranking.csv") or []
    fil_js = [{"f": r.get("nome",""), "neg": r.get("negocio",""), "uf": r.get("uf",""),
               "emp": r.get("empresa",""), "sigla": r.get("empresa","RC")[:2]+"."+r.get("uf","SP")[:3],
               "total": int(float(r.get("spend",0) or 0)),
               "qtde": 0, "cmv": int(float(r.get("spend",0) or 0)*0.75), "dias": 18,
               "cat": "I1 · I2", "forn": 0, "alerta": "OK"} for r in fil_data[:12]]
    if fil_js:
        html = re.sub(r"const FILIAIS\s*=\s*\[[\s\S]*?\];",
                      f"const FILIAIS = {json.dumps(fil_js, ensure_ascii=False)};", html, count=1)

    # CAT_VAL e CAT_INF
    cat_hier = load_elem_data("03_categoria", "03_categoria_r01_hierarquia.csv") or []
    cat_val = {}
    for r in cat_hier:
        for lv in range(1, 6):
            k = r.get(f"cat{lv}","")
            if not k: continue
            code = k.split(" - ")[0].strip().split(" ")[0]
            if code: cat_val[code] = round(cat_val.get(code, 0) + float(r.get("spend",0) or 0)/1e6, 1)
    if cat_val:
        html = re.sub(r"const CAT_VAL\s*=\s*\{[\s\S]*?\};",
                      f"var CAT_VAL = {json.dumps(cat_val, ensure_ascii=False)};", html, count=1)

    cat_inf_data = load_elem_data("10_inflacao", "10_inflacao_r04_por_categoria.csv") or []
    cat_inf = {}
    for r in cat_inf_data:
        code = r.get("cat2","").split(" - ")[0].strip().split(" ")[0]
        if code: cat_inf[code] = round(float(r.get("inflacao_media_pct",0) or 0), 1)
    if cat_inf:
        html = re.sub(r"const CAT_INF\s*=\s*\{[\s\S]*?\};",
                      f"var CAT_INF = {json.dumps(cat_inf, ensure_ascii=False)};", html, count=1)

    return html


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not DESIGN.exists():
        print(f"ERRO: {DESIGN} não encontrado"); sys.exit(1)

    DIST.mkdir(parents=True, exist_ok=True)

    print(f"Lendo {DESIGN.name}...")
    html = DESIGN.read_text(encoding="utf-8")

    print("Carregando indexes...")
    indexes = load_all_indexes()
    n_total = sum(len(idx.get("elementos",[])) for idx in indexes.values())
    n_vis   = sum(sum(1 for e in idx.get("elementos",[]) if e.get("layout",{}).get("visivel")) for idx in indexes.values())
    print(f"  {len(indexes)} abas · {n_total} elementos · {n_vis} visíveis")

    print("Aplicando overrides de layout...")
    indexes = apply_layout_overrides(indexes)

    print("Substituindo arrays mockados...")
    html = replace_mock_arrays(html, indexes)

    print("Gerando constantes JS dos elementos...")
    js_injection = build_js_injection(indexes)
    n_consts = js_injection.count("_BI_DATA[")
    print(f"  {n_consts} elementos com dados injetados")

    print("Injetando no HTML...")
    html = replace_filter_html(html)
    html = inject_relatorio_tab(html)
    html = inject_css(html, GRID_CSS)
    html = inject_css(html, EDITOR_CSS)
    html = inject_css(html, FILTER_CSS)
    html = inject_css(html, RELATORIO_CSS)
    html = inject_before_script_end(html, js_injection + "\n" + RENDERER_JS + "\n" + EDITOR_JS + "\n" + FILTER_JS + "\n" + RELATORIO_JS)
    html = update_timestamp(html)

    out = DIST / "index.html"
    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size // 1024
    print(f"\nGerado: {out}  ({size} KB)")
    print("Abrir: start dist\\index.html")


if __name__ == "__main__":
    main()
