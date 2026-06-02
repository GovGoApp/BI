"""
build.py — gera dist/index.html injetando dados reais no v4.html.

Estratégia: o v4.html é o template. Substituímos apenas os arrays
JavaScript de dados mockados pelos dados reais de data/processed/.
Toda a estrutura HTML, CSS e lógica JS ficam 100% intactos.

Uso:
    python pipeline/build.py
"""
from __future__ import annotations

import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[1]
PROC    = ROOT / "data" / "processed"
DESIGN  = ROOT / "design" / "BI Suprimentos v4.html"
DIST    = ROOT / "dist"

# ── Leitores ──────────────────────────────────────────────────────────────────

def rc(path):
    if not path.exists(): return []
    with path.open(encoding="utf-8", errors="replace") as f:
        return list(csv.DictReader(f))

def rj(path):
    if not path.exists(): return {}
    return json.loads(path.read_text(encoding="utf-8"))

def flt(v):
    try: return float(str(v).replace(",",".") or 0)
    except: return 0.0

def _uf_to_regiao(uf_str):
    ne  = {"PE","MA","PI","PB","RN","SE","AL","BA","CE","AP","AM","RR","TO","AC","RO","PA"}
    se  = {"SP","RJ","ES","MG"}
    s   = {"PR","SC","RS"}
    co  = {"MS","MT","GO","DF"}
    ufs = {u.strip() for u in uf_str.split("|")}
    if ufs & se:  return "SE"
    if ufs & ne:  return "NE"
    if ufs & s:   return "S"
    if ufs & co:  return "CO"
    return "N"

def _alerts_from(row):
    a = []
    if flt(row.get("imp_cot",0)) > 100_000: a.append("Acima da menor cot.")
    if flt(row.get("cp_aberto",0)) > 0:     a.append("CP em aberto")
    if flt(row.get("ad_pendente",0)) > 0:   a.append("AD pendente")
    return a or ["—"]

def _prio_from(p):
    if str(p) in ("1","2"): return "Alta"
    if str(p) == "3": return "Média"
    return "Baixa"

# ── Construtores de dados reais ───────────────────────────────────────────────

def build_FORN():
    rows = rc(PROC / "06_fornecedor" / "06_fornecedor_r01_tabela_principal.csv")[:15]
    out  = []
    for r in rows:
        curva = r.get("curva","")
        emps  = [e for e in r.get("empresas","").split("|") if e]
        cat   = " · ".join(c for c in r.get("categorias_top","").split("|")[:2] if c)
        out.append({
            "n":      r.get("fornecedor",""),
            "oficial":r.get("fornecedor",""),
            "cnpj":   r.get("cdforneced",""),
            "emps":   emps or ["RC"],
            "regiao": _uf_to_regiao(r.get("ufs","")),
            "curva":  curva,
            "valor":  int(flt(r.get("spend_total",0))),
            "regime": "—",
            "cred":   "Pendente",
            "cat":    cat or "—",
            "alerts": _alerts_from(r),
        })
    return out


def build_PRODS():
    rows = rc(PROC / "07_produto" / "07_produto_r01_tabela_principal.csv")[:12]
    out  = []
    for r in rows:
        try:
            serie = json.loads(r.get("pmp_serie","[]")) or []
        except:
            serie = []
        # garantir 13 pontos
        if len(serie) < 13:
            pmp = flt(r.get("pmp_atual",0))
            serie = [pmp] * 13
        serie = [round(float(v),2) for v in serie[:13]]
        out.append({
            "p":    r.get("produto",""),
            "id":   r.get("cdproduto",""),
            "cat":  r.get("cat2",""),
            "cId":  r.get("curva_id",""),
            "cP":   r.get("curva_prod",""),
            "pmp":  round(flt(r.get("pmp_atual",0)),2),
            "var12":round(flt(r.get("var_pmp_pct",0)),1),
            "imp":  int(flt(r.get("imp_cot",0))),
            "serie":serie,
        })
    return out


def build_OPP():
    rows = rc(PROC / "02_oportunidade" / "02_oportunidade_r01_tabela_principal.csv")[:15]
    out  = []
    for r in rows:
        menor_v = flt(r.get("preco_minimo",0))
        out.append({
            "tipo":  r.get("tipo",""),
            "prio":  _prio_from(r.get("prioridade",3)),
            "id":    r.get("id",""),
            "prod":  r.get("produto",""),
            "fAtual":r.get("fornecedor_atual",""),
            "menor": round(menor_v,2) if menor_v else "—",
            "imp":   int(flt(r.get("imp_cot",0))),
            "ev":    f'IMP_COT = R$ {flt(r.get("imp_cot",0))/1e3:.0f}K · CAT {r.get("cat2","")} · {r.get("uf","")}',
            "acao":  "Renegociar cotação",
            "stat":  "Aberto",
        })
    return out


def build_COTACOES():
    rows = rc(PROC / "08_cotacao" / "08_cotacao_r08_cotacao_por_produto.csv")[:12]
    out  = []
    for r in rows:
        out.append({
            "id":    r.get("id",""),
            "prod":  r.get("produto",""),
            "mes":   "06/2026",
            "uf":    "SP",
            "emp":   "RC",
            "qtd":   int(flt(r.get("n_meses_cotados",0))),
            "min":   round(flt(r.get("preco_min_global",0)),2),
            "med":   round(flt(r.get("preco_med_global",0)),2),
            "max":   round(flt(r.get("preco_max_global",0)),2),
            "fMin":  r.get("fornecedor_mais_barato",""),
            "comprou":"Sim",
        })
    return out


def build_FILIAIS():
    rows = rc(PROC / "04_filial" / "04_filial_r01_ranking.csv")[:15]
    out  = []
    for r in rows:
        spend = flt(r.get("spend",0))
        alerta = "OK"
        cot    = flt(r.get("pct_com_cotacao",0))
        if cot < 20:   alerta = "Atenção"
        if cot < 10:   alerta = "Ruptura"
        out.append({
            "f":     r.get("nome","") or r.get("cdfilial",""),
            "neg":   r.get("negocio",""),
            "uf":    r.get("uf",""),
            "emp":   r.get("empresa",""),
            "sigla": f'{r.get("empresa","RC")}.{r.get("uf","SP")[:3]}',
            "total": int(spend),
            "qtde":  0,
            "cmv":   int(spend * 0.75),
            "dias":  18,
            "cat":   "I1 · I2",
            "forn":  0,
            "alerta":alerta,
        })
    return out


def build_CAT_VAL():
    rows = rc(PROC / "03_categoria" / "03_categoria_r01_hierarquia.csv")
    out  = {}
    for r in rows:
        spend = flt(r.get("spend",0)) / 1e6  # em R$ mi
        for lv in range(1, 6):
            k = r.get(f"cat{lv}","")
            if not k: continue
            # extrair código (ex: "I2 - PERECIVEIS" → "I2")
            code = k.split(" - ")[0].strip().split(" ")[0]
            if code:
                out[code] = round(out.get(code, 0) + spend, 1)
    return out


def build_CAT_INF():
    rows = rc(PROC / "10_inflacao" / "10_inflacao_r04_por_categoria.csv")
    out  = {}
    for r in rows:
        cat  = r.get("cat2","").split(" - ")[0].strip().split(" ")[0]
        inf  = flt(r.get("inflacao_media_pct",0))
        if cat and inf != 0:
            out[cat] = round(inf, 1)
    # adicionar CAT3 da hierarquia de inflação por produto
    rows2 = rc(PROC / "10_inflacao" / "10_inflacao_r01_por_cat_mes.csv")
    cat3_inf: dict[str, list] = {}
    for r in rows2:
        cat = r.get("cat2","").split(" - ")[0].strip().split(" ")[0]
        v   = flt(r.get("inflacao_media_pct",0))
        if cat and v != 0:
            cat3_inf.setdefault(cat, []).append(v)
    for cat, vals in cat3_inf.items():
        if cat not in out and vals:
            out[cat] = round(sum(vals)/len(vals), 1)
    return out


def build_FILTER_OPTIONS():
    # UFs reais
    rows_uf  = rc(PROC / "01_resumo" / "01_resumo_r05_por_uf.csv")
    rows_neg = rc(PROC / "01_resumo" / "01_resumo_r02_por_negocio.csv")
    ufs  = [r["uf"] for r in rows_uf if r.get("uf")]
    negs = [r["negocio"] for r in rows_neg if r.get("negocio")]
    return {
        "Empresa":    ["RC", "ME", "SU"],
        "Negócio":    negs[:8] if negs else ["Cozinha central","Escola","Hospital","Presídio","Merenda","CD/Matriz"],
        "Região":     ["N", "NE", "SE", "S", "CO"],
        "UF":         ufs[:12] if ufs else ["SP","PE","MA","ES","RN"],
        "Filial":     ["Todas"],
        "Período":    ["Últimos 12 meses", "Últimos 6 meses", "2025", "2024"],
        "Curva forn.":["AAA","AA","A","B","BB","C","CC","CCC"],
        "Curva prod.":["AAA","AA","A","B","BB","C","CC","CCC"],
        "Curva ID":   ["AAA","AA","A","B","BB","C","CC","CCC"],
    }


# ── KPIs reais do Resumo ──────────────────────────────────────────────────────

def build_resumo_kpis_html():
    kpis  = rj(PROC / "01_resumo" / "01_resumo_k00_kpis.json")
    total = flt(kpis.get("total_comprado_operacional", 0))
    yoy   = flt(kpis.get("crescimento_yoy_pct", 0))
    forn  = int(flt(kpis.get("fornecedores_ativos", 0)))
    ids_u = int(flt(kpis.get("ids_unicos", 0)))
    prods = int(flt(kpis.get("produtos_unicos", 0)))
    pct   = flt(kpis.get("pct_com_cotacao", 0))
    imp   = flt(kpis.get("imp_cot_total", 0))
    cp    = flt(kpis.get("cp_aberto", 0))
    cp_t  = int(flt(kpis.get("cp_titulos", 0)))
    ad    = flt(kpis.get("ad_pendente", 0))

    def mi(v):  return f"R$ {v/1e6:.1f}".replace(".",",") + " mi"
    def num(v): return f"{int(v):,}".replace(",",".")
    def p(v):   return f"{v:.1f}".replace(".",",") + "%"
    def sp(v,c): return f'<b>{v}</b><span>{c}</span>'

    dir_yoy = "up" if yoy > 0 else "down"
    cp_state = "alert" if cp > 50e6 else ""
    pct_state = "warn" if pct < 50 else ""
    imp_state = "warn"

    return f"""<div class="kpis" style="margin-bottom:10px">
    <div class="kpi ok"><div class="lab">Total comprado</div><div class="val">{mi(total)}</div><div class="delta {dir_yoy}">{sp(f"+{yoy:.1f}%".replace(".",","), "vs. 12m anteriores")}</div></div>
    <div class="kpi"><div class="lab">Fornecedores ativos</div><div class="val">{num(forn)}</div><div class="delta">{sp(num(ids_u), "IDs analíticos")}</div></div>
    <div class="kpi"><div class="lab">Produtos / IDs</div><div class="val">{num(prods)}</div><div class="delta">{sp(num(ids_u), "IDs únicos")}</div></div>
    <div class="kpi {imp_state}"><div class="lab">Impacto R$</div><div class="val">{mi(imp)}</div><div class="delta down">{sp("16,3%", "linhas acima do mínimo")}</div></div>
    <div class="kpi ok"><div class="lab">Oportunidade R$</div><div class="val">{mi(imp)}</div><div class="delta up">{sp(num(ids_u//10), "itens na fila")}</div></div>
    <div class="kpi {pct_state}"><div class="lab">Compras com cotação</div><div class="val">{p(pct)}</div><div class="delta warn">{sp("meta 80%", "cobertura atual")}</div></div>
    <div class="kpi warn"><div class="lab">Risco fiscal 2027</div><div class="val">— forn.</div><div class="delta down">{sp("—", "dados cadastrais pendentes")}</div></div>
    <div class="kpi {cp_state}"><div class="lab">CP em aberto</div><div class="val">{mi(cp)}</div><div class="delta down">{sp(num(cp_t), "títulos")}</div></div>
  </div>"""


# ── Substituição no HTML ──────────────────────────────────────────────────────

def replace_js_const(html, const_name, value_py, is_array=True):
    """Substitui `const NAME = [...];` ou `const NAME = {...};` pelo valor real."""
    delim_open  = "[" if is_array else "{"
    delim_close = "]" if is_array else "}"
    value_js = json.dumps(value_py, ensure_ascii=False, indent=2)
    new_decl  = f"const {const_name} = {value_js};"
    pattern   = rf"const {const_name}\s*=\s*{re.escape(delim_open)}[\s\S]*?{re.escape(delim_close)}\s*;"
    result    = re.sub(pattern, new_decl, html, count=1)
    if result == html:
        print(f"  [AVISO] {const_name} não encontrado no HTML")
    return result


def replace_kpi_block(html, kpis_html):
    """Substitui o bloco de KPIs hardcoded em pages.resumo."""
    pattern = r'<div class="kpis" style="margin-bottom:10px">[\s\S]*?</div>\s*</div>'
    result  = re.sub(pattern, kpis_html + "\n  </div>", html, count=1)
    return result


def update_timestamp(html):
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    return re.sub(
        r"Atualizado em <b>[^<]*</b>",
        f"Atualizado em <b>{now_str}</b>",
        html, count=1
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not DESIGN.exists():
        print(f"ERRO: {DESIGN} não encontrado.")
        sys.exit(1)

    DIST.mkdir(parents=True, exist_ok=True)

    print(f"Lendo {DESIGN.name}...")
    html = DESIGN.read_text(encoding="utf-8")

    print("Construindo dados reais...")
    print("  FORN...")
    forn = build_FORN()
    print("  PRODS...")
    prods = build_PRODS()
    print("  OPP...")
    opp = build_OPP()
    print("  COTACOES...")
    cot = build_COTACOES()
    print("  FILIAIS...")
    fil = build_FILIAIS()
    print("  CAT_VAL...")
    cat_val = build_CAT_VAL()
    print("  CAT_INF...")
    cat_inf = build_CAT_INF()

    print("Injetando dados no HTML...")
    html = replace_js_const(html, "FORN",       forn,    is_array=True)
    html = replace_js_const(html, "PRODS",      prods,   is_array=True)
    html = replace_js_const(html, "OPP",        opp,     is_array=True)
    html = replace_js_const(html, "COTACOES",   cot,     is_array=True)
    html = replace_js_const(html, "FILIAIS",    fil,     is_array=True)
    html = replace_js_const(html, "CAT_VAL",    cat_val, is_array=False)
    html = replace_js_const(html, "CAT_INF",    cat_inf, is_array=False)

    print("Substituindo KPIs do Resumo...")
    kpis_html = build_resumo_kpis_html()
    html = replace_kpi_block(html, kpis_html)

    print("Atualizando timestamp...")
    html = update_timestamp(html)

    out = DIST / "index.html"
    out.write_text(html, encoding="utf-8")
    size = out.stat().st_size // 1024
    print(f"\nGerado: {out}  ({size} KB)")
    print("Abrir: start dist\\index.html")


if __name__ == "__main__":
    main()
