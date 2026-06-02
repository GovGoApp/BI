/* ============================================================
   BI de Suprimentos — Dashboard JS
   Lógica de interação: abas, filtros, tabelas expansíveis,
   tag bars, sparklines, formatação numérica.
   ============================================================ */

'use strict';

/* ── Formatação ──────────────────────────────────────────────── */
const FMT = {
  brl:  n => 'R$ ' + Number(n).toLocaleString('pt-BR', {maximumFractionDigits:0}),
  brl2: n => 'R$ ' + Number(n).toLocaleString('pt-BR', {minimumFractionDigits:2,maximumFractionDigits:2}),
  mi:   n => { const v=Number(n)/1e6; return 'R$ '+(v>=10?v.toFixed(1):v.toFixed(2))+' mi' },
  mil:  n => { const v=Number(n)/1e3; return (v>=10?v.toFixed(0):v.toFixed(1))+' mil' },
  pct:  n => { const v=Number(n); return (v>0?'+':'')+v.toFixed(1)+'%' },
  num:  n => Number(n).toLocaleString('pt-BR'),
  dec:  n => Number(n).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}),
  auto: n => {
    const v = Math.abs(Number(n));
    if (v >= 1e6)  return FMT.mi(n);
    if (v >= 1e3)  return FMT.brl(n);
    if (v % 1 !== 0) return FMT.brl2(n);
    return FMT.brl(n);
  },
};

/* ── Abas ────────────────────────────────────────────────────── */
function initTabs() {
  const nav = document.getElementById('tabs');
  if (!nav) return;
  nav.addEventListener('click', e => {
    const btn = e.target.closest('.tab');
    if (!btn) return;
    const page = btn.dataset.page;
    nav.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.page === page));
    document.querySelectorAll('.page').forEach(p => p.classList.toggle('active', p.dataset.page === page));
    if (page) localStorage.setItem('bi_active_tab', page);
  });
  const saved = localStorage.getItem('bi_active_tab');
  if (saved) {
    const btn = nav.querySelector(`.tab[data-page="${saved}"]`);
    if (btn) btn.click();
  }
}

/* ── Filtros globais ─────────────────────────────────────────── */
const FILTERS = { empresa: [], uf: [], mesano: [], curva: [], negocio: [], cat1: [] };

function initFilters() {
  document.querySelectorAll('.f .pick').forEach(pick => {
    pick.addEventListener('click', () => {
      const key  = pick.closest('.f').dataset.filter;
      const val  = pick.dataset.value;
      if (!key) return;
      const idx = FILTERS[key]?.indexOf(val);
      if (idx === -1 || idx === undefined) {
        (FILTERS[key] = FILTERS[key] || []).push(val);
        pick.classList.add('active');
      } else {
        FILTERS[key].splice(idx, 1);
        pick.classList.remove('active');
      }
      renderActivePills();
      applyFilters();
    });
  });
  document.querySelectorAll('.filters-clear').forEach(btn => {
    btn.addEventListener('click', () => {
      Object.keys(FILTERS).forEach(k => FILTERS[k] = []);
      document.querySelectorAll('.f .pick').forEach(p => p.classList.remove('active'));
      renderActivePills();
      applyFilters();
    });
  });
  document.querySelectorAll('.filters-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const wrap = btn.closest('.filters');
      wrap?.classList.toggle('collapsed');
      btn.classList.toggle('open');
    });
  });
}

function renderActivePills() {
  const container = document.querySelector('.filter-foot .applied');
  if (!container) return;
  const pills = Object.entries(FILTERS)
    .flatMap(([k,vals]) => vals.map(v => `<button class="pill b" data-filter="${k}" data-value="${v}">${v} ×</button>`));
  container.innerHTML = pills.join('');
  container.querySelectorAll('.pill').forEach(p => {
    p.addEventListener('click', () => {
      const k = p.dataset.filter; const v = p.dataset.value;
      FILTERS[k] = (FILTERS[k]||[]).filter(x => x !== v);
      document.querySelectorAll(`.f .pick[data-value="${v}"]`).forEach(pk => pk.classList.remove('active'));
      renderActivePills(); applyFilters();
    });
  });
}

function applyFilters() {
  document.dispatchEvent(new CustomEvent('bi:filter', { detail: { ...FILTERS } }));
}

function passesFilter(row) {
  for (const [key, vals] of Object.entries(FILTERS)) {
    if (!vals.length) continue;
    const col = { empresa:'NMEMP', uf:'UF', negocio:'negocio', curva:'curva', cat1:'cat1' }[key];
    if (col && row[col] && !vals.includes(row[col])) return false;
    if (key==='mesano' && row.mesano && !vals.some(v => row.mesano.startsWith(v))) return false;
  }
  return true;
}

/* ── Tag bars ────────────────────────────────────────────────── */
function initTagbars() {
  document.querySelectorAll('.tagbar').forEach(bar => {
    bar.addEventListener('click', e => {
      const tg = e.target.closest('.tg');
      if (!tg) return;
      if (tg.dataset.exclusive !== 'false') {
        bar.querySelectorAll('.tg').forEach(t => t.classList.remove('active'));
      }
      tg.classList.toggle('active');
      const event = new CustomEvent('bi:tagbar', { detail: { bar: bar.id, value: tg.dataset.value } });
      document.dispatchEvent(event);
    });
  });
}

/* ── Tabelas expansíveis ─────────────────────────────────────── */
function initExpandable(tableEl) {
  if (!tableEl) return;
  tableEl.querySelectorAll('.row-hd').forEach(row => {
    row.addEventListener('click', () => {
      const detail = row.nextElementSibling;
      if (!detail?.classList.contains('detail')) return;
      const open = row.classList.toggle('open');
      detail.style.display = open ? '' : 'none';
      row.classList.toggle('expanded', open);
    });
  });
}

/* ── Barras proporcionais ────────────────────────────────────── */
function renderBars(containerEl) {
  if (!containerEl) return;
  containerEl.querySelectorAll('.bar[data-pct]').forEach(bar => {
    const pct = Math.min(100, Math.max(0, parseFloat(bar.dataset.pct) || 0));
    let span = bar.querySelector('span');
    if (!span) { span = document.createElement('span'); bar.appendChild(span); }
    span.style.width = pct + '%';
  });
}

/* ── Sparklines SVG (inline, com círculo no ponto final) ─────── */
function svgSpark(arr, color) {
  color = color || '#2563eb';
  const w=160, h=36, p=2;
  const vals = arr.map(Number).filter(v => !isNaN(v));
  if (!vals.length) return '';
  const mn=Math.min(...vals), mx=Math.max(...vals);
  const span=Math.max(0.0001,mx-mn);
  const pts=vals.map((v,i)=>{
    const x=p+i*(w-2*p)/(vals.length-1);
    const y=h-p-((v-mn)/span)*(h-2*p);
    return x.toFixed(1)+','+y.toFixed(1);
  }).join(' ');
  const last=pts.trim().split(' ').pop().split(',');
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" style="width:100%;height:36px;display:block">
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="${last[0]}" cy="${last[1]}" r="2.4" fill="${color}"/>
  </svg>`;
}

function renderSparkline(canvas, values, color) {
  if (!canvas) return;
  const html = svgSpark(values || [], color);
  canvas.outerHTML = html; // substitui canvas por SVG
}

/* ── Gráfico de linhas SVG (GL) ─────────────────────────────── */
function svgLineChart(series, opts) {
  // series: [{label, data:[{x,y}], color}]
  // opts: {width, height, paddingL, paddingR, paddingT, paddingB}
  const o = opts || {};
  const W=600, H=180, pL=o.pL||35, pR=o.pR||10, pT=o.pT||15, pB=o.pB||28;
  const iW=W-pL-pR, iH=H-pT-pB;

  if (!series?.length) return '';

  const allY = series.flatMap(s => s.data.map(p => Number(p.y)||0));
  const allX = series[0].data.map(p => p.x);
  const minY=Math.min(0,...allY), maxY=Math.max(...allY)||1;
  const colors = ['#2563eb','#16a34a','#a16207','#b91c1c'];

  const toX = (i) => pL + (i/(allX.length-1))*iW;
  const toY = (v) => pT + iH - ((Number(v)-minY)/(maxY-minY))*iH;

  // Grid lines (4)
  let lines='';
  for (let i=0;i<4;i++) {
    const y = pT + (i/3)*iH;
    const val = maxY - (i/3)*(maxY-minY);
    lines += `<line x1="${pL}" x2="${W-pR}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#eef2f7"/>`;
    lines += `<text x="${pL-4}" y="${(y+3).toFixed(1)}" text-anchor="end" font-size="9" fill="#94a3b8" font-family="Segoe UI">${_fmtY(val)}</text>`;
  }

  // X labels
  let xlabels='';
  const step = Math.max(1, Math.floor(allX.length/12));
  allX.forEach((lbl,i) => {
    if (i%step===0 || i===allX.length-1)
      xlabels += `<text x="${toX(i).toFixed(1)}" y="${H-5}" text-anchor="middle" font-size="9" fill="#94a3b8" font-family="Segoe UI">${lbl}</text>`;
  });

  // Series
  let paths='', gradients='';
  series.forEach((s, si) => {
    const c = s.color || colors[si%colors.length];
    const pts = s.data.map((p,i) => `${toX(i).toFixed(1)},${toY(p.y).toFixed(1)}`).join(' ');
    const first = `${toX(0).toFixed(1)},${toY(s.data[0]?.y||0).toFixed(1)}`;
    const last  = `${toX(s.data.length-1).toFixed(1)},${toY(s.data[s.data.length-1]?.y||0).toFixed(1)}`;
    const gid = `gl${si}`;
    gradients += `<linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${c}" stop-opacity=".15"/>
      <stop offset="100%" stop-color="${c}" stop-opacity="0"/>
    </linearGradient>`;
    // área preenchida
    paths += `<path d="M${pts.split(' ').join(' L')} L${toX(s.data.length-1).toFixed(1)},${(pT+iH).toFixed(1)} L${pL},${(pT+iH).toFixed(1)} Z" fill="url(#${gid})"/>`;
    // linha
    paths += `<polyline points="${pts}" fill="none" stroke="${c}" stroke-width="1.8"/>`;
  });

  return `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">
    <defs>${gradients}</defs>
    ${lines}${paths}${xlabels}
  </svg>`;
}

function _fmtY(v) {
  if (Math.abs(v)>=1e6) return (v/1e6).toFixed(0)+'M';
  if (Math.abs(v)>=1e3) return (v/1e3).toFixed(0)+'K';
  return v.toFixed(0);
}

/* ── Gráfico de barras SVG (GB) ─────────────────────────────── */
function svgBarChart(data, xKey, yKey, opts) {
  const o = opts || {};
  const W=600, H=o.height||160, pL=40, pR=10, pT=15, pB=28;
  const color = o.color || '#2563eb';
  if (!data?.length) return '';

  const vals = data.map(r => Number(r[yKey])||0);
  const maxY = Math.max(...vals)||1;
  const bW   = Math.floor((W-pL-pR)/data.length * 0.65);
  const gap  = Math.floor((W-pL-pR)/data.length * 0.35);

  let bars='', labels='', ylines='';
  for (let i=0;i<3;i++) {
    const y=pT+(i/2)*(H-pT-pB);
    ylines+=`<line x1="${pL}" x2="${W-pR}" y1="${y.toFixed(1)}" y2="${y.toFixed(1)}" stroke="#eef2f7"/>`;
    const v=maxY-(i/2)*maxY;
    ylines+=`<text x="${pL-4}" y="${(y+3).toFixed(1)}" text-anchor="end" font-size="9" fill="#94a3b8">${_fmtY(v)}</text>`;
  }

  data.forEach((r,i) => {
    const x = pL + i*((W-pL-pR)/data.length) + gap/2;
    const v = Number(r[yKey])||0;
    const bH = ((v/maxY)*(H-pT-pB));
    const y  = H-pB-bH;
    bars   += `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${bW}" height="${bH.toFixed(1)}" fill="${color}" rx="2" opacity="0.85"/>`;
    labels += `<text x="${(x+bW/2).toFixed(1)}" y="${(H-5)}" text-anchor="middle" font-size="9" fill="#94a3b8">${String(r[xKey]).slice(-7)}</text>`;
  });

  return `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">
    ${ylines}${bars}${labels}
  </svg>`;
}

/* ── Gráfico empilhado SVG (GE) ─────────────────────────────── */
function svgStackedChart(data, xKey, stackKeys, colors, opts) {
  const o = opts||{};
  const W=600, H=o.height||160, pL=40, pR=10, pT=15, pB=28;
  const dfltColors=['#b91c1c','#f59e0b','#2563eb','#16a34a','#6366f1'];

  if (!data?.length) return '';
  const totals=data.map(r=>stackKeys.reduce((s,k)=>s+(Number(r[k])||0),0));
  const maxT=Math.max(...totals)||1;
  const bW=Math.floor((W-pL-pR)/data.length*0.65);
  const gap=Math.floor((W-pL-pR)/data.length*0.35);

  let bars='', labels='';
  data.forEach((r,i)=>{
    const x=pL+i*((W-pL-pR)/data.length)+gap/2;
    let yOff=H-pB;
    stackKeys.forEach((k,ki)=>{
      const v=Number(r[k])||0;
      const bH=(v/maxT)*(H-pT-pB);
      if(bH>0){
        const c=(colors||dfltColors)[ki%dfltColors.length];
        bars+=`<rect x="${x.toFixed(1)}" y="${(yOff-bH).toFixed(1)}" width="${bW}" height="${bH.toFixed(1)}" fill="${c}" opacity="0.8"/>`;
        yOff-=bH;
      }
    });
    labels+=`<text x="${(x+bW/2).toFixed(1)}" y="${H-5}" text-anchor="middle" font-size="9" fill="#94a3b8">${String(r[xKey]).slice(-7)}</text>`;
  });

  return `<svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" preserveAspectRatio="none">
    ${bars}${labels}
  </svg>`;
}

/* ── Gráfico de barras simples ───────────────────────────────── */
function renderBarChart(containerEl, data, xKey, yKey, opts) {
  if (!containerEl || !data?.length) return;
  const o = opts || {};
  const maxVal = Math.max(...data.map(r => Number(r[yKey])||0)) || 1;
  const color  = o.color || 'var(--blue)';
  const fmtFn  = o.fmt || (v => FMT.auto(v));
  const H = o.height || 120;

  const bars = data.map((r,i) => {
    const v   = Number(r[xKey])||0;
    const pct = (Number(r[yKey])||0) / maxVal * 100;
    return `<div class="bc-col">
      <div class="bc-bar-wrap" style="height:${H}px">
        <div class="bc-bar" style="height:${pct}%;background:${color}"></div>
      </div>
      <div class="bc-label">${r[xKey]}</div>
    </div>`;
  }).join('');

  containerEl.innerHTML = `<div class="bc-wrap" style="display:flex;gap:4px;align-items:flex-end">${bars}</div>`;

  containerEl.querySelectorAll('.bc-col').forEach((col,i) => {
    const bar = col.querySelector('.bc-bar');
    if (!bar) return;
    bar.title = fmtFn(data[i][yKey]);
  });
}

/* ── Heatmap / Matrix ────────────────────────────────────────── */
function renderHeatmap(containerEl, data, rowKey, colKey, valKey) {
  if (!containerEl || !data?.length) return;
  const rows = [...new Set(data.map(r => r[rowKey]))];
  const cols = [...new Set(data.map(r => r[colKey]))];
  const lookup = {};
  data.forEach(r => { lookup[`${r[rowKey]}|${r[colKey]}`] = Number(r[valKey])||0; });
  const maxVal = Math.max(...Object.values(lookup)) || 1;

  const header = `<tr><th></th>${cols.map(c=>`<th>${c}</th>`).join('')}</tr>`;
  const body   = rows.map(row =>
    `<tr><td style="font-size:11px;font-weight:600;padding:4px 8px;white-space:nowrap">${row}</td>` +
    cols.map(col => {
      const v = lookup[`${row}|${col}`]||0;
      const s = Math.round((v/maxVal)*4)+1;
      return `<td><div class="cell s${s}" title="${FMT.brl(v)}">${FMT.mi(v)}</div></td>`;
    }).join('') + '</tr>'
  ).join('');

  containerEl.innerHTML = `<table style="border-collapse:separate;border-spacing:4px;width:100%"><thead>${header}</thead><tbody>${body}</tbody></table>`;
}

/* ── Formatação de KPIs ──────────────────────────────────────── */
function renderKpi(el, value, opts) {
  if (!el) return;
  const o = opts || {};
  const valEl   = el.querySelector('.val');
  const deltaEl = el.querySelector('.delta');
  if (valEl) valEl.textContent = o.fmt ? o.fmt(value) : FMT.auto(value);
  if (deltaEl && o.delta !== undefined) {
    const d = Number(o.delta);
    deltaEl.innerHTML = `<b>${FMT.pct(d)}</b> ${o.deltaLabel||'vs anterior'}`;
    deltaEl.className = 'delta ' + (d>0?'up':d<0?'down':'');
  }
  if (o.state) el.classList.add(o.state);
}

/* ── Paginação ───────────────────────────────────────────────── */
function initPager(pagerEl, total, perPage, onPage) {
  if (!pagerEl) return;
  let current = 1;
  const pages = Math.ceil(total / perPage);

  function render() {
    const info = pagerEl.querySelector('.info');
    const ctrl = pagerEl.querySelector('.ctrl');
    if (info) info.textContent = `${(current-1)*perPage+1}–${Math.min(current*perPage,total)} de ${FMT.num(total)}`;
    if (ctrl) {
      ctrl.innerHTML = '';
      const prev = document.createElement('button');
      prev.textContent = '‹'; prev.disabled = current<=1;
      prev.addEventListener('click', () => { if(current>1){current--;render();onPage(current);} });
      ctrl.appendChild(prev);
      const next = document.createElement('button');
      next.textContent = '›'; next.disabled = current>=pages;
      next.addEventListener('click', () => { if(current<pages){current++;render();onPage(current);} });
      ctrl.appendChild(next);
    }
  }
  render();
}

/* ── Ordenação de tabela ─────────────────────────────────────── */
function initSortable(tableEl) {
  if (!tableEl) return;
  tableEl.querySelectorAll('thead th[data-sort]').forEach(th => {
    th.style.cursor = 'pointer';
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      const asc = th.dataset.dir !== 'asc';
      th.dataset.dir = asc ? 'asc' : 'desc';
      const tbody = tableEl.querySelector('tbody');
      if (!tbody) return;
      const rows = [...tbody.querySelectorAll('tr:not(.detail)')];
      rows.sort((a,b) => {
        const av = a.querySelector(`[data-key="${key}"]`)?.textContent.replace(/[^\d.-]/g,'');
        const bv = b.querySelector(`[data-key="${key}"]`)?.textContent.replace(/[^\d.-]/g,'');
        const diff = (parseFloat(av)||0) - (parseFloat(bv)||0);
        return asc ? diff : -diff;
      });
      rows.forEach(r => tbody.appendChild(r));
    });
  });
}

/* ── Busca global ────────────────────────────────────────────── */
function initSearch() {
  const inp = document.querySelector('.search input');
  if (!inp) return;
  inp.addEventListener('input', () => {
    const q = inp.value.toLowerCase().trim();
    document.dispatchEvent(new CustomEvent('bi:search', { detail: { q } }));
  });
}

/* ── Init ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initFilters();
  initTagbars();
  initSearch();
  document.querySelectorAll('[data-expandable]').forEach(t => initExpandable(t));
  document.querySelectorAll('[data-sortable]').forEach(t => initSortable(t));
  renderBars(document);
});
