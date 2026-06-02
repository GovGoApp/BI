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

ROOT   = Path(__file__).resolve().parents[1]
PROC   = ROOT / "data" / "processed"
DESIGN = ROOT / "design" / "BI Suprimentos v4.html"
DIST   = ROOT / "dist"

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

def load_all_indexes():
    indexes = {}
    for p in sorted(PROC.iterdir()):
        idx_file = p / f"{p.name}_00_index.json"
        if idx_file.exists():
            idx = rj(idx_file)
            indexes[p.name] = idx
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
  top: 4px; right: 4px;
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
  const ths = cols.map(c => `<th class="${c.cls || ''}">${c.label || c.key}</th>`).join('');
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
    const handle = `<div class="grid-editor-handle" data-id="${e.id}" title="${e.id}">⠿ ${e.variavel_js}</div>`;
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

# ── Injeção no HTML ───────────────────────────────────────────────────────────

def inject_css(html, css):
    """Injeta CSS antes do </style>."""
    return html.replace("</style>", css + "\n</style>", 1)

def inject_before_script_end(html, js):
    """Injeta JS antes do último </script>."""
    pos = html.rfind("</script>")
    if pos == -1: return html + f"\n<script>\n{js}\n</script>"
    return html[:pos] + "\n" + js + "\n" + html[pos:]

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
                      f"const CAT_VAL = {json.dumps(cat_val, ensure_ascii=False)};", html, count=1)

    cat_inf_data = load_elem_data("10_inflacao", "10_inflacao_r04_por_categoria.csv") or []
    cat_inf = {}
    for r in cat_inf_data:
        code = r.get("cat2","").split(" - ")[0].strip().split(" ")[0]
        if code: cat_inf[code] = round(float(r.get("inflacao_media_pct",0) or 0), 1)
    if cat_inf:
        html = re.sub(r"const CAT_INF\s*=\s*\{[\s\S]*?\};",
                      f"const CAT_INF = {json.dumps(cat_inf, ensure_ascii=False)};", html, count=1)

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

    print("Substituindo arrays mockados...")
    html = replace_mock_arrays(html, indexes)

    print("Gerando constantes JS dos elementos...")
    js_injection = build_js_injection(indexes)
    n_consts = js_injection.count("_BI_DATA[")
    print(f"  {n_consts} elementos com dados injetados")

    print("Injetando no HTML...")
    html = inject_css(html, GRID_CSS)
    html = inject_before_script_end(html, js_injection + "\n" + RENDERER_JS)
    html = update_timestamp(html)

    out = DIST / "index.html"
    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size // 1024
    print(f"\nGerado: {out}  ({size} KB)")
    print("Abrir: start dist\\index.html")


if __name__ == "__main__":
    main()
