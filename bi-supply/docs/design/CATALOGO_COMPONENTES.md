# Catálogo de Componentes — BI Suprimentos v4

Extraído diretamente do HTML `design/BI Suprimentos v4.html`.
**Fonte da verdade para build.py e dashboard.js.**

---

## 1. KPI Card (`.kpi`)

```html
<div class="kpi ok">
  <div class="lab">Total comprado</div>
  <div class="val">R$ 184,2 mi</div>
  <div class="delta up"><b>+6,8%</b><span>vs. 12m anteriores</span></div>
</div>
```

### Estados
| Classe | Barra esquerda | Uso |
|---|---|---|
| `.ok` | Verde | Meta atingida |
| `.warn` | Amarelo | Atenção |
| `.alert` | Vermelho | Crítico |
| *(sem classe)* | Nenhuma | Neutro |

### Delta variants
```html
<div class="delta up"><b>+6,8%</b><span>vs. 12m anteriores</span></div>
<div class="delta down"><b>R$ 4,1 mi</b><span>vencido</span></div>
<div class="delta warn"><b>68%</b><span>meta: 80%</span></div>
<div class="delta"><b>312</b><span>na curva A+</span></div>
```
- `.up` → `<b>` fica verde
- `.down` → `<b>` fica vermelho
- `.warn` → `<b>` fica amarelo
- *(sem classe)* → `<b>` fica muted

### Grid KPIs
```css
.kpis { display:grid; grid-template-columns:repeat(8,1fr); gap:10px }
```

---

## 2. Tabela (`.table`)

```html
<table class="table">
  <thead>
    <tr>
      <th>Fornecedor</th>
      <th class="ck"></th>
      <th>Curva</th>
      <th class="num">Valor 12m</th>
    </tr>
  </thead>
  <tbody>
    <tr class="row-hd open expanded" data-i="0">
      <td class="nm">FONTE VIVA ALIMENTOS</td>
      <td class="ck"><span class="chev">▶</span></td>
      <td><span class="curva AAA">AAA</span></td>
      <td class="num">R$ 18,42 mi</td>
    </tr>
    <tr class="detail" style="display:none">
      <td colspan="4" style="padding:0">
        <div class="det-grid">
          <div class="det">
            <h4>Identidade</h4>
            <dl class="kv">
              <dt>CDFORNECED</dt><dd class="mono">12.034</dd>
              <dt>CNPJ</dt><dd class="mono">12.345.678/0001-90</dd>
            </dl>
          </div>
        </div>
      </td>
    </tr>
  </tbody>
</table>
```

### Classes de coluna
| Classe | Uso |
|---|---|
| `.num` | Números — right-align, tabular-nums, nowrap |
| `.nm` | Nome — font-weight:600 |
| `.id` | ID/código — monospace, 11.5px, gray |
| `.sm` | Subtexto — 11px, muted |
| `.ck` | Expand icon — 24px, centered |
| `.chev` | Chevron — rotaciona 90° quando `.open` |

### Expandable rows
- `.row-hd` → clicável, cursor:pointer
- `.row-hd.open` → `.chev` rotaciona, fica blue
- `.expanded` → fundo azul claro
- `.detail` → linha de detalhe (display:none por padrão)

### Detail grid (`.det-grid`)
```css
.det-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; padding:12px }
.det { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:10px 11px }
.det h4 { font-size:11px; text-transform:uppercase; color:var(--muted); letter-spacing:.5px }
.kv { display:grid; grid-template-columns:auto 1fr; gap:4px 10px }
.kv dt { color:var(--muted) }
.kv dd { font-weight:600; text-align:right; margin:0 }
```

---

## 3. HBar List (`.hbar`)

```html
<div class="hbar">
  <div class="lab">Cozinha central
    <div class="sub">RC + ME</div>
  </div>
  <div class="bar g"><span style="width:90%"></span></div>
  <div class="v">R$ 62,4 mi</div>
</div>
```

Grid: `140px 1fr 90px` — label, barra, valor

### Variantes de cor da barra
| Classe | Cor |
|---|---|
| *(padrão)* | Azul `--blue` |
| `.g` | Verde `--green` |
| `.y` | Amarelo `--yellow` |
| `.r` | Vermelho `--red` |
| `.k` | Cinza `--gray` |

---

## 4. Gráfico de Linhas — SVG inline

```html
<svg viewBox="0 0 600 180" width="100%" height="180" preserveAspectRatio="none">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2563eb" stop-opacity=".18"/>
      <stop offset="100%" stop-color="#2563eb" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <!-- Grid horizontal -->
  <line x1="30" x2="595" y1="30" y2="30" stroke="#eef2f7"/>
  <!-- Área preenchida -->
  <path d="M30,120 L77,108 ... L595,48 L595,180 L30,180 Z" fill="url(#g1)"/>
  <!-- Série -->
  <polyline points="30,120 77,108 ..." fill="none" stroke="#2563eb" stroke-width="1.8"/>
  <!-- Labels X -->
  <text x="54" y="170" text-anchor="middle" font-size="9" fill="#94a3b8" font-family="Segoe UI">Jun</text>
  <!-- Labels Y -->
  <text x="22" y="36" text-anchor="end" font-size="9" fill="#94a3b8" font-family="Segoe UI">R$ 20 mi</text>
</svg>
```

### Legenda (abaixo do SVG)
```html
<div style="display:flex;gap:14px;font-size:11px;color:var(--muted);padding-top:6px">
  <span>
    <span style="display:inline-block;width:10px;height:10px;background:#2563eb;border-radius:2px;vertical-align:1px;margin-right:5px"></span>
    I2 Perecíveis
  </span>
</div>
```

---

## 5. Gráfico de Barras — SVG inline

```html
<svg viewBox="0 0 680 220" width="100%" height="220" preserveAspectRatio="none">
  <line x1="40" x2="675" y1="30" y2="30" stroke="#eef2f7"/>
  <!-- Barra de um mês -->
  <rect x="50" y="100" width="38" height="100" fill="#2563eb" opacity="0.85"/>
  <!-- Label mês -->
  <text x="69" y="214" text-anchor="middle" font-size="9" fill="#64748b">Jun</text>
  <!-- Label valor -->
  <text x="69" y="95" text-anchor="middle" font-size="9" fill="#64748b">R$ 18,4 mi</text>
</svg>
```

---

## 6. Gráfico Empilhado (GE) — SVG inline

```html
<svg viewBox="0 0 680 220" width="100%" height="220" preserveAspectRatio="none">
  <!-- Mês com 4 faixas empilhadas -->
  <rect x="50" y="178" width="38" height="22" fill="#b91c1c" opacity="0.7"/>  <!-- 0 cot -->
  <rect x="50" y="152" width="38" height="26" fill="#dc2626" opacity="0.72"/> <!-- 1 cot -->
  <rect x="50" y="120" width="38" height="32" fill="#a16207" opacity="0.74"/> <!-- 2-3 cot -->
  <rect x="50" y="55"  width="38" height="65" fill="#2563eb" opacity="0.8"/>  <!-- 4+ cot -->
</svg>
```

---

## 7. Sparkline inline (`.spark`)

```html
<svg class="spark" viewBox="0 0 160 36" preserveAspectRatio="none">
  <polyline points="2,18.2 15.3,15.6 28.6,17.8 ..." 
            fill="none" stroke="#2563eb" stroke-width="1.6" stroke-linejoin="round"/>
  <circle cx="161" cy="0.8" r="2.4" fill="#2563eb"/>
</svg>
```

Geração JavaScript:
```javascript
function svgSpark(arr, color='#2563eb') {
  const w=160, h=36, p=2;
  const min=Math.min(...arr), max=Math.max(...arr);
  const span=Math.max(0.0001,max-min);
  const pts=arr.map((v,i)=>{
    const x=p+i*(w-2*p)/(arr.length-1);
    const y=h-p-((v-min)/span)*(h-2*p);
    return x.toFixed(1)+','+y.toFixed(1);
  }).join(' ');
  const last=pts.split(' ').pop();
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.6" stroke-linejoin="round"/>
    <circle cx="${last.split(',')[0]}" cy="${last.split(',')[1]}" r="2.4" fill="${color}"/>
  </svg>`;
}
```

---

## 8. Matrix / Heatmap (`.matrix`)

```html
<div class="matrix" style="grid-template-columns:170px repeat(7,1fr)">
  <div class="cell head"></div>
  <div class="cell head">SP</div>
  <div class="cell head">RJ</div>
  
  <div class="cell head" style="justify-content:flex-start;font-size:11.5px;font-weight:600;color:var(--ink);text-transform:none">I2 · Perecíveis</div>
  <div class="cell s4" title="R$ 18,4 mi">18.4</div>
  <div class="cell s3" title="R$ 12,2 mi">12.2</div>
</div>
```

### Intensidade s1→s5
| Classe | Hex | Uso |
|---|---|---|
| `.s1` | `#eef2f7` | 0–20% do máximo |
| `.s2` | `#dbeafe` | 20–40% |
| `.s3` | `#93c5fd` / ink | 40–60% |
| `.s4` | `#3b82f6` / #fff | 60–80% |
| `.s5` | `#1d4ed8` / #fff | 80–100% |
| `.cell.alert` | `#fee2e2` / --red | Alerta |
| `.cell.warn` | `#fef9c3` / `#854d0e` | Atenção |

---

## 9. Card Header (`.card-h`)

```html
<div class="card-h">
  <div>
    <h3>Tendência mensal de compras</h3>
    <div class="sub">Valor comprado · jun/2025 → mai/2026</div>
  </div>
  <div class="meta">
    <span class="zoho-src">ZOHO · NFE</span>
    <div class="subtabs">
      <button class="st active">12m</button>
      <button class="st">6m</button>
    </div>
  </div>
</div>
```

### Badge de origem Zoho
```html
<span style="font-size:10px;font-weight:700;color:var(--blue);background:var(--blue-soft);
             border:1px solid #bfdbfe;border-radius:4px;padding:1px 6px;letter-spacing:.3px">
  ZOHO · NOME_DA_VIEW
</span>
```

---

## 10. Tagbar (`.tagbar .tg`)

```html
<div class="tagbar">
  <span class="tg active" data-value="todos">Todos <span class="n">1284</span></span>
  <span class="tg" data-value="aaa">Curva AAA <span class="n">42</span></span>
</div>
```

- `.tg.active` → `#0f172a` bg, branco, bold
- `.n` → badge contador (font-weight:700, opacity:.8)

---

## 11. Pills, Badges e Curvas

### Pills (`.pill`)
| Classe | Aparência |
|---|---|
| `.pill.b` | Fundo azul suave, texto azul |
| `.pill.g` | Fundo verde suave, texto verde |
| `.pill.y` | Fundo amarelo suave, texto amarelo |
| `.pill.r` | Fundo vermelho suave, texto vermelho |
| `.pill.k` | Fundo cinza suave, texto cinza |
| `.pill.ghost` | Transparente, borda, cinza |

### Badges empresa (`.badge`)
| Classe | Cor de fundo |
|---|---|
| `.badge.rc` | `#0f172a` |
| `.badge.me` | `#1e3a8a` |
| `.badge.su` | `#155e75` |

### Curva ABC (`.curva`)
| Classe | Fundo / texto |
|---|---|
| `.curva.AAA`, `.curva.AA`, `.curva.A` | `#0f172a` / branco |
| `.curva.B`, `.curva.BB` | `#334155` / branco |
| `.curva.C`, `.curva.CC`, `.curva.CCC` | `#cbd5e1` / `#334155` |

---

## 12. Alertas (`.alert-row`)

```html
<div class="alerts">
  <div class="alert-row r">
    <span class="dot"></span>
    <div>
      <div class="nm">Acima da menor cotação</div>
      <div class="who">FONTE VIVA · Frango kg · SU/PE</div>
    </div>
    <div class="num">R$ 184.500</div>
    <span class="pill ghost">Compras</span>
    <button class="act">Abrir</button>
  </div>
</div>
```

Grid: `18px 1fr auto auto auto`

Cores do `.dot`:
- `.r` → `--red`
- `.y` → `--yellow`
- `.b` → `--blue`
- `.g` → `--green`

---

## 13. Filtros (`.filters`)

```html
<div class="filters">
  <div class="row">
    <div class="f">
      <label>Empresa</label>
      <button class="pick active">
        <span class="v">RC · ME · SU</span>
        <span class="caret">▾</span>
      </button>
    </div>
  </div>
  <div class="filter-foot">
    <button class="filters-toggle open">Filtros avançados <span class="chev">▾</span></button>
    <div class="applied">
      <button class="pill b">RC <span class="x">×</span></button>
    </div>
    <button class="filters-clear">Limpar filtros</button>
  </div>
</div>
```

---

## 14. Layouts de seção (grids dentro de cada aba)

```css
.row-2  { display:grid; grid-template-columns:1.4fr 1fr; gap:10px }
.row-2b { display:grid; grid-template-columns:1fr 1fr; gap:10px }
.row-3  { display:grid; grid-template-columns:repeat(3,1fr); gap:10px }
```

---

## 15. Categoria cascata (`.cat-cols`)

```html
<div class="cat-cols" style="display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px">
  <div class="cat-col">
    <h4 class="lvl-h">Nível 1 <span class="muted">/ todas</span></h4>
    <div class="hbar-list compact">
      <div class="hbar hbar-clk sel" data-lvl="1" data-k="I" data-n="I - INSUMOS">
        <div class="lab">I - INSUMOS<div class="sub">+9,1%</div></div>
        <div class="bar"><span style="width:100%"></span></div>
        <div class="v">R$ 487,4 mi</div>
      </div>
    </div>
  </div>
</div>
```

- `.sel` → selecionado (bg:--blue-soft, label azul)
- `.cat-col.locked` → coluna bloqueada (listras diagonais)

---

## 16. Status dots (`.sdot`)

```html
<span class="sdot g"></span> OK
<span class="sdot y"></span> Atenção
<span class="sdot r"></span> Erro
<span class="sdot b"></span> Info
```

8×8px, border-radius:999px, margin-right:6px

---

## Checklist para build.py

Antes de considerar um componente "completo" no dashboard gerado:

- [ ] KPI tem `.lab`, `.val`, `.delta` com `<b>` e `<span>`
- [ ] Delta tem classe `.up`/`.down`/`.warn` conforme valor
- [ ] Tabela usa `.num`/`.nm`/`.id`/`.sm` por coluna
- [ ] Expandable rows têm `.row-hd` + `.detail` + `.chev`
- [ ] Barras proporcional têm `<span style="width:X%">` (não CSS)
- [ ] Card header tem `.sub` com período/fonte + badge Zoho
- [ ] Gráficos são SVG inline (não canvas)
- [ ] Sparklines têm `<circle>` no ponto final
- [ ] Pills e badges usam as classes corretas (não inline color)
- [ ] Curvas ABC usam `.curva.AAA` etc. (não texto puro)
- [ ] Tagbar tem `.n` com contagem
- [ ] Alertas têm grid 5 colunas com `.dot`, `.nm`, `.who`, valor, pill, botão
