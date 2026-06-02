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

/* ── Sparklines SVG ──────────────────────────────────────────── */
function renderSparkline(canvas, values, color) {
  if (!canvas || !values?.length) return;
  const vals = values.map(Number).filter(v => !isNaN(v));
  if (!vals.length) return;
  const W = canvas.clientWidth || 80; const H = canvas.clientHeight || 32;
  const mn = Math.min(...vals); const mx = Math.max(...vals);
  const range = mx - mn || 1;
  const pts = vals.map((v, i) => {
    const x = (i / (vals.length - 1)) * W;
    const y = H - ((v - mn) / range) * (H - 4) - 2;
    return `${x},${y}`;
  }).join(' ');
  canvas.setAttribute('viewBox', `0 0 ${W} ${H}`);
  canvas.innerHTML = `<polyline points="${pts}" fill="none" stroke="${color||'var(--blue)'}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>`;
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
