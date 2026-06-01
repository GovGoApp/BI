"""Transforma data/raw/ → data/processed/{aba}/

Nomenclatura:
  {nn}_{aba}/                        pasta por aba (numerada conforme ordem v4)
  {nn}_{aba}_k00_kpis.json           KPIs da aba
  {nn}_{aba}_r{nn}_{funcao}.csv/json relatórios
  {nn}_{aba}_00_index.json           índice com títulos, descrições e SQL

Uso: python pipeline/transform.py
"""

from __future__ import annotations

import csv, json, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW  = ROOT / "data" / "raw"
OUT  = ROOT / "data" / "processed"

# Abas na ordem exata do v4 (data-page → pasta)
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

GEO_NNE = {"MA","PA","PI","PB","PE","RN","SE","AL","BA","CE","AP","AM","RR","TO","AC","RO"}
GEO_SSE = {"SP","RJ","ES","MG","PR","SC","RS","MS","MT","GO","DF"}


# ── helpers ───────────────────────────────────────────────────────────────────

def load(fn):
    p = RAW / fn
    if not p.exists():
        print(f"  [AVISO] {fn} não encontrado"); return []
    with p.open(encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))

def flt(v):
    if not v or str(v).strip() == "": return 0.0
    try: return float(str(v).replace(",","."))
    except: return 0.0

def pct(a, t): return round(a/t*100,2) if t else 0.0
def r2(v):     return round(v, 2)

def sc(folder, name, rows, fields=None):
    if not rows: return
    d = OUT / folder / name; d.parent.mkdir(parents=True, exist_ok=True)
    fl = fields or list(rows[0].keys())
    with d.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fl, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def sj(folder, name, data):
    d = OUT / folder / name; d.parent.mkdir(parents=True, exist_ok=True)
    d.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── lookups (construídos uma vez) ─────────────────────────────────────────────

def build_lookups(nfe, cp, ad, curva_forn, pmp12):
    tg = sum(flt(r["TOTAL"]) for r in nfe)

    fcp = defaultdict(lambda: {"aberto":0.0,"vencido":0.0,"titulos":0,"nm":""})
    for r in cp:
        cd = r.get("CDFORNECED","")
        if r.get("STATUSPAG","") == "Em Aberto":
            fcp[cd]["aberto"]  += flt(r.get("VRATUAPAG",""))
            fcp[cd]["titulos"] += 1
            if r.get("FAIXA_DIAS","").strip().rstrip("\n").startswith("VE"):
                fcp[cd]["vencido"] += flt(r.get("VRATUAPAG",""))
        fcp[cd]["nm"] = r.get("NMFANTFORN","")

    fad = defaultdict(lambda: {"pendente":0.0,"conciliado":0.0,"nm":""})
    for r in ad:
        cd = r.get("CDFORNECED",""); v = flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","") == "ADIANTAMENTO ?": fad[cd]["pendente"] += v
        else: fad[cd]["conciliado"] += v
        fad[cd]["nm"] = r.get("FANTASIA_OFICIAL","")

    fc = {r.get("CDFORNECED",""):r.get("CURVA","") for r in curva_forn}
    fr = {r.get("CDFORNECED",""):r.get("RAZAO_SOCIAL","") for r in curva_forn}

    ps = {}
    for r in pmp12:
        id_ = r.get("ID","")
        if id_: ps[id_] = {"nome":r.get("NMPRODUTO_OFICIAL",""),"cat2":r.get("CAT2",""),
                            "curva":r.get("CURVA_ID",""),
                            "pmps":[flt(r.get(f"PMP_{i}","")) for i in range(13)]}

    fv = defaultdict(lambda:{"spend":0.0,"imp":0.0,"nm":"","curva":"","empresas":set(),"ufs":set(),"cats":set()})
    for r in nfe:
        cd = r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","")
        fv[cd]["spend"] += flt(r["TOTAL"])
        fv[cd]["nm"]     = r.get("FANTASIA_OFICIAL") or r.get("NMFANTFORN","")
        fv[cd]["curva"]  = r.get("CURVA_FORN","")
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: fv[cd]["imp"] += imp
        fv[cd]["empresas"].add(r.get("NMEMP","")); fv[cd]["ufs"].add(r.get("UF",""))
        fv[cd]["cats"].add(r.get("CAT2",""))

    return {"tg":tg,"fcp":fcp,"fad":fad,"fc":fc,"fr":fr,"ps":ps,"fv":fv}


# ── 01_resumo ─────────────────────────────────────────────────────────────────

def aba_resumo(nfe, cp, ad, lk):
    F = "01_resumo"
    print(f"  {F}/")
    tg = lk["tg"]; fcp = lk["fcp"]
    fin = {"MUTUO","DEVOLUCAO","EMPRESTIMO","ICMS","PARCELAMENTO"}
    def is_fin(r): nm=(r.get("NMPRODUTO_OFICIAL","") or "").upper(); return any(f in nm for f in fin)

    t_op  = sum(flt(r["TOTAL"]) for r in nfe if not is_fin(r))
    t2024 = sum(flt(r["TOTAL"]) for r in nfe if str(r.get("ANO",""))=="2024")
    t2025 = sum(flt(r["TOTAL"]) for r in nfe if str(r.get("ANO",""))=="2025")
    yoy   = pct(t2025-t2024, t2024)
    fat   = len({r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","") for r in nfe})
    cc    = sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("","0"))
    imp   = sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT",""))>0)
    cp_ab = sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","")=="Em Aberto")
    cp_t  = sum(1 for r in cp if r.get("STATUSPAG","")=="Em Aberto")
    adp   = sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","")=="ADIANTAMENTO ?")

    kpis = {"total_comprado_operacional":r2(t_op),"total_comprado_periodo":r2(tg),
            "crescimento_yoy_pct":yoy,"fornecedores_ativos":fat,
            "pct_com_cotacao":pct(cc,len(nfe)),"imp_cot_total":r2(imp),
            "cp_aberto":r2(cp_ab),"cp_titulos":cp_t,"ad_pendente":r2(adp)}
    sj(F,"01_resumo_k00_kpis.json", kpis)

    # r01 evolução mensal
    bm = defaultdict(float)
    for r in nfe: bm[r.get("MESANO","")]+=flt(r["TOTAL"])
    sc(F,"01_resumo_r01_por_mes.csv",
       [{"mesano":k,"spend":r2(v)} for k,v in sorted(bm.items()) if k.strip()])

    # r02 por negócio
    bn = defaultdict(lambda:{"spend":0.0,"imp":0.0})
    for r in nfe:
        neg=r.get("FI.NEGOCIO","") or ""
        bn[neg]["spend"]+=flt(r["TOTAL"])
        imp2=flt(r.get("IMP_COT",""))
        if imp2>0: bn[neg]["imp"]+=imp2
    sc(F,"01_resumo_r02_por_negocio.csv", sorted(
       [{"negocio":k,"spend":r2(d["spend"]),"pct":pct(d["spend"],tg),"imp_cot":r2(d["imp"])}
        for k,d in bn.items() if k.strip()],key=lambda x:-x["spend"]))

    # r03 top categorias
    bc = defaultdict(lambda:{"spend":0.0,"imp":0.0,"inf_s":0.0,"inf_n":0})
    for r in nfe:
        c=r.get("CAT2",""); bc[c]["spend"]+=flt(r["TOTAL"])
        imp2=flt(r.get("IMP_COT",""));
        if imp2>0: bc[c]["imp"]+=imp2
        inf=flt(r.get("INF_PROD_PMP",""))
        if inf!=0: bc[c]["inf_s"]+=inf; bc[c]["inf_n"]+=1
    sc(F,"01_resumo_r03_top_categoria.csv", sorted(
       [{"cat2":k,"spend":r2(d["spend"]),"pct":pct(d["spend"],tg),"imp_cot":r2(d["imp"]),
         "inflacao_media_pct":round(d["inf_s"]/d["inf_n"],2) if d["inf_n"] else 0.0}
        for k,d in bc.items() if k.strip()],key=lambda x:-x["spend"])[:20])

    # r04 top fornecedores (com CP)
    acum=0.0; rows_f=[]
    for cd,d in sorted(lk["fv"].items(),key=lambda x:-x[1]["spend"])[:20]:
        acum+=d["spend"]
        rows_f.append({"cdforneced":cd,"fornecedor":d["nm"],
            "curva":d["curva"] or lk["fc"].get(cd,""),
            "spend":r2(d["spend"]),"pct":pct(d["spend"],tg),"pct_acum":pct(acum,tg),
            "imp_cot":r2(d["imp"]),"cp_aberto":r2(fcp[cd]["aberto"]) if cd in fcp else 0.0})
    sc(F,"01_resumo_r04_top_fornecedor.csv", rows_f)

    # r05 por UF
    bu = defaultdict(float)
    for r in nfe: bu[r.get("UF","")]+=flt(r["TOTAL"])
    sc(F,"01_resumo_r05_por_uf.csv", sorted(
       [{"uf":k,"spend":r2(v),"pct":pct(v,tg)} for k,v in bu.items() if k.strip()],
       key=lambda x:-x["spend"]))

    # r06 geo N/NE
    sc(F,"01_resumo_r06_geo_nne.csv", sorted(
       [{"uf":k,"spend":r2(v),"pct":pct(v,tg)} for k,v in bu.items() if k in GEO_NNE],
       key=lambda x:-x["spend"]))

    # r07 geo S/SE
    sc(F,"01_resumo_r07_geo_sse.csv", sorted(
       [{"uf":k,"spend":r2(v),"pct":pct(v,tg)} for k,v in bu.items() if k in GEO_SSE],
       key=lambda x:-x["spend"]))

    # r08 por filial
    bf = defaultdict(lambda:{"spend":0.0,"neg":"","uf":"","emp":"","nm":"","imp":0.0})
    for r in nfe:
        fil=str(r.get("CDFILIAL","")).strip()
        if not fil: continue
        d=bf[fil]; d["spend"]+=flt(r["TOTAL"]); d["neg"]=r.get("FI.NEGOCIO","")
        d["uf"]=r.get("UF",""); d["emp"]=r.get("NMEMP",""); d["nm"]=r.get("NMFILIAL","")
        imp2=flt(r.get("IMP_COT",""))
        if imp2>0: d["imp"]+=imp2
    sc(F,"01_resumo_r08_por_filial.csv", sorted(
       [{"cdfilial":k,"nome":d["nm"],"negocio":d["neg"],"uf":d["uf"],"empresa":d["emp"],
         "spend":r2(d["spend"]),"pct":pct(d["spend"],tg),"imp_cot":r2(d["imp"])}
        for k,d in bf.items()],key=lambda x:-x["spend"])[:8])

    # r09 CAT2 × UF (heatmap)
    cu = defaultdict(float)
    for r in nfe: cu[(r.get("CAT2",""),r.get("UF",""))]+=flt(r["TOTAL"])
    sc(F,"01_resumo_r09_cat2_por_uf.csv",
       [{"cat2":k[0],"uf":k[1],"spend":r2(v)} for k,v in cu.items() if k[0].strip() and k[1].strip()])

    # index
    sj(F,"01_resumo_00_index.json",{
        "aba":"01_resumo","data_page":"resumo","label":"Resumo",
        "kpis_arquivo":"01_resumo_k00_kpis.json",
        "kpis":[
            {"id":"01_resumo_k01","chave":"total_comprado_operacional","titulo":"Total Comprado (operacional)",
             "descricao":"Soma do TOTAL do NFE excluindo lançamentos financeiros de D5 (MUTUO, DEVOLUCAO, etc.)",
             "sql":"SELECT SUM(\"TOTAL\") FROM \"NFE\" WHERE \"NMPRODUTO_OFICIAL\" NOT LIKE '%MUTUO%' AND \"NMPRODUTO_OFICIAL\" NOT LIKE '%DEVOLUCAO%'"},
            {"id":"01_resumo_k02","chave":"crescimento_yoy_pct","titulo":"Crescimento YoY %",
             "descricao":"Variação percentual do spend 2025 vs 2024",
             "sql":"SELECT \"ANO\", SUM(\"TOTAL\") FROM \"NFE\" WHERE \"ANO\" IN (2024,2025) GROUP BY \"ANO\""},
            {"id":"01_resumo_k03","chave":"fornecedores_ativos","titulo":"Fornecedores Ativos",
             "descricao":"Count distinct de CDFORNECED_OFICIAL com compras no período",
             "sql":"SELECT COUNT(DISTINCT \"CDFORNECED_OFICIAL\") FROM \"NFE\""},
            {"id":"01_resumo_k04","chave":"pct_com_cotacao","titulo":"% Compras com Cotação",
             "descricao":"% de linhas onde PRE_MIN_COT IS NOT NULL",
             "sql":"SELECT SUM(CASE WHEN \"PRE_MIN_COT\" IS NOT NULL THEN 1 ELSE 0 END)*100.0/COUNT(*) FROM \"NFE\""},
            {"id":"01_resumo_k05","chave":"imp_cot_total","titulo":"Oportunidade IMP_COT",
             "descricao":"Soma de IMP_COT onde positivo = valor que poderíamos economizar",
             "sql":"SELECT SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\" > 0"},
            {"id":"01_resumo_k06","chave":"cp_aberto","titulo":"CP em Aberto",
             "descricao":"Soma de VRATUAPAG onde STATUSPAG = 'Em Aberto'",
             "sql":"SELECT SUM(\"VRATUAPAG\") FROM \"CP\" WHERE \"STATUSPAG\" = 'Em Aberto'"},
            {"id":"01_resumo_k07","chave":"ad_pendente","titulo":"AD Pendente",
             "descricao":"Soma de VALOR_FINAL onde STATUS_CONCILIACAO = 'ADIANTAMENTO ?'",
             "sql":"SELECT SUM(\"VALOR_FINAL\") FROM \"AD_v3\" WHERE \"STATUS_CONCILIACAO\" = 'ADIANTAMENTO ?'"},
        ],
        "relatorios":[
            {"id":"01_resumo_r01","arquivo":"01_resumo_r01_por_mes.csv","titulo":"Evolução Mensal de Compras",
             "tipo":"GL","descricao":"Série temporal de spend por MESANO para gráfico de linhas",
             "colunas":["mesano","spend"],
             "sql":"SELECT \"MESANO\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"MESANO\" ORDER BY \"MESANO\""},
            {"id":"01_resumo_r02","arquivo":"01_resumo_r02_por_negocio.csv","titulo":"Compras por Tipo de Negócio",
             "tipo":"HL","descricao":"Spend e IMP_COT por FI.NEGOCIO (CD, COZINHA, HOSPITAL, MERENDA, etc.)",
             "colunas":["negocio","spend","pct","imp_cot"],
             "sql":"SELECT \"FI.NEGOCIO\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"FI.NEGOCIO\" ORDER BY spend DESC"},
            {"id":"01_resumo_r03","arquivo":"01_resumo_r03_top_categoria.csv","titulo":"Top Categorias (CAT2)",
             "tipo":"T","descricao":"Top 20 categorias por spend com inflação média e impacto de cotação",
             "colunas":["cat2","spend","pct","imp_cot","inflacao_media_pct"],
             "sql":"SELECT \"CAT2\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CAT2\" ORDER BY spend DESC LIMIT 20"},
            {"id":"01_resumo_r04","arquivo":"01_resumo_r04_top_fornecedor.csv","titulo":"Top Fornecedores",
             "tipo":"T","descricao":"Top 20 fornecedores com curva ABC, spend, IMP_COT e CP em aberto",
             "colunas":["fornecedor","curva","spend","pct","pct_acum","imp_cot","cp_aberto"],
             "sql":"SELECT \"FANTASIA_OFICIAL\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"FANTASIA_OFICIAL\" ORDER BY spend DESC LIMIT 20"},
            {"id":"01_resumo_r05","arquivo":"01_resumo_r05_por_uf.csv","titulo":"Spend por UF",
             "tipo":"HL","descricao":"Spend total por UF para mapas geográficos",
             "colunas":["uf","spend","pct"],
             "sql":"SELECT \"UF\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"UF\" ORDER BY spend DESC"},
            {"id":"01_resumo_r06","arquivo":"01_resumo_r06_geo_nne.csv","titulo":"SUP por GEO — N e NE",
             "tipo":"HL","descricao":"Spend UFs do Norte e Nordeste",
             "colunas":["uf","spend","pct"],
             "sql":"SELECT \"UF\", SUM(\"TOTAL\") AS spend FROM \"NFE\" WHERE \"UF\" IN ('MA','PA','PI','PB','PE','RN','SE','AL','BA','CE','AP','AM') GROUP BY \"UF\" ORDER BY spend DESC"},
            {"id":"01_resumo_r07","arquivo":"01_resumo_r07_geo_sse.csv","titulo":"SUP por GEO — S e SE",
             "tipo":"HL","descricao":"Spend UFs do Sul e Sudeste",
             "colunas":["uf","spend","pct"],
             "sql":"SELECT \"UF\", SUM(\"TOTAL\") AS spend FROM \"NFE\" WHERE \"UF\" IN ('SP','RJ','ES','MG','PR','SC','RS','DF') GROUP BY \"UF\" ORDER BY spend DESC"},
            {"id":"01_resumo_r08","arquivo":"01_resumo_r08_por_filial.csv","titulo":"Por Filial (top 8)",
             "tipo":"T","descricao":"Top 8 filiais por spend com negócio, UF e impacto",
             "colunas":["cdfilial","nome","negocio","uf","empresa","spend","pct","imp_cot"],
             "sql":"SELECT \"CDFILIAL\", \"NMFILIAL\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CDFILIAL\",\"NMFILIAL\" ORDER BY spend DESC LIMIT 8"},
            {"id":"01_resumo_r09","arquivo":"01_resumo_r09_cat2_por_uf.csv","titulo":"Categoria × UF (heatmap)",
             "tipo":"MX","descricao":"Spend por CAT2 × UF para heatmap",
             "colunas":["cat2","uf","spend"],
             "sql":"SELECT \"CAT2\", \"UF\", SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CAT2\",\"UF\""},
        ]
    })


# ── 02_oportunidade ───────────────────────────────────────────────────────────

def aba_oportunidade(nfe, num_cot, lk):
    F = "02_oportunidade"; print(f"  {F}/")
    tg = lk["tg"]
    id_num = {r.get("ID",""):int(flt(r.get("QTD_COT","0"))) for r in num_cot}

    ids_aaa_sc = set(); n_acima = 0
    for r in nfe:
        if r.get("PRE_MIN_COT","").strip() in ("","0") and r.get("CURVA_ID","") in ("AAA","AA","A"):
            ids_aaa_sc.add(r.get("ID",""))
        if flt(r.get("IMP_COT","")) > 0: n_acima += 1

    imp_tot = sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT",""))>0)
    mono = sum(1 for r in num_cot if flt(r.get("QTD_COT","0"))==1)

    sj(F,"02_oportunidade_k00_kpis.json",{
        "imp_cot_total":r2(imp_tot),
        "ids_aaa_sem_cotacao":len(ids_aaa_sc),
        "ids_comprados_acima_minimo":len({r.get("ID","") for r in nfe if flt(r.get("IMP_COT",""))>0}),
        "pct_linhas_acima_minimo":pct(n_acima,len(nfe)),
        "itens_mono_cotacao":mono,
    })

    # r01 tabela principal
    id_d = defaultdict(lambda:{"imp":0.0,"spend":0.0,"produto":"","cat2":"","uf":"",
                                "forn_atual":"","forn_min":"","preco_min":0.0,"curva_id":"","curva_forn":""})
    for r in nfe:
        imp=flt(r.get("IMP_COT","")); id_=r.get("ID","")
        if imp<=0 and r.get("PRE_MIN_COT","").strip() not in ("","0"): continue
        d=id_d[id_]; d["spend"]+=flt(r["TOTAL"])
        if imp>0: d["imp"]+=imp
        d["produto"]=r.get("NMPRODUTO_OFICIAL",""); d["cat2"]=r.get("CAT2",""); d["uf"]=r.get("UF","")
        d["forn_atual"]=r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        d["forn_min"]=r.get("FORN_MIN_COT",""); d["preco_min"]=flt(r.get("PRE_MIN_COT",""))
        d["curva_id"]=r.get("CURVA_ID",""); d["curva_forn"]=r.get("CURVA_FORN","")

    rows=[]
    for id_,d in id_d.items():
        if d["preco_min"]==0 and d["curva_id"] in ("AAA","AA","A"):
            tipo="Sem cotação AAA/A"; prio=1
        elif id_num.get(id_,0)==1:
            tipo="Monopólio de cotação"; prio=2
        elif d["imp"]>0:
            tipo="Acima do menor preço"; prio=3
        else:
            continue
        rows.append({"tipo":tipo,"prioridade":prio,"id":id_,"produto":d["produto"],
            "cat2":d["cat2"],"uf":d["uf"],"fornecedor_atual":d["forn_atual"],
            "fornecedor_mais_barato":d["forn_min"],"preco_minimo":r2(d["preco_min"]),
            "imp_cot":r2(d["imp"]),"spend":r2(d["spend"]),"curva_id":d["curva_id"],
            "status":"Acima do menor" if d["imp"]>0 else "Sem cotação"})
    rows.sort(key=lambda x:(x["prioridade"],-x["imp_cot"]))
    sc(F,"02_oportunidade_r01_tabela_principal.csv", rows[:300])

    # r02 por CAT2
    ci = defaultdict(lambda:{"imp":0.0,"ids":0})
    for r2_ in rows:
        if r2_["imp_cot"]>0: ci[r2_["cat2"]]["imp"]+=r2_["imp_cot"]; ci[r2_["cat2"]]["ids"]+=1
    sc(F,"02_oportunidade_r02_por_categoria.csv", sorted(
       [{"cat2":k,"imp_cot":r2(d["imp"]),"ids_afetados":d["ids"]} for k,d in ci.items() if k.strip()],
       key=lambda x:-x["imp_cot"]))

    # r03 por UF
    ui = defaultdict(float)
    for r in nfe:
        imp=flt(r.get("IMP_COT",""))
        if imp>0: ui[r.get("UF","")]+=imp
    sc(F,"02_oportunidade_r03_por_uf.csv", sorted(
       [{"uf":k,"imp_cot":r2(v)} for k,v in ui.items() if k.strip()],key=lambda x:-x["imp_cot"]))

    sj(F,"02_oportunidade_00_index.json",{
        "aba":"02_oportunidade","data_page":"oportunidades","label":"Oportunidades",
        "kpis_arquivo":"02_oportunidade_k00_kpis.json",
        "kpis":[
            {"id":"02_oportunidade_k01","chave":"imp_cot_total","titulo":"Oportunidade Total IMP_COT",
             "descricao":"Soma de IMP_COT positivo = dinheiro que poderíamos ter economizado comprando no menor preço cotado",
             "sql":"SELECT SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\" > 0"},
            {"id":"02_oportunidade_k02","chave":"ids_aaa_sem_cotacao","titulo":"IDs AAA/AA/A Sem Cotação",
             "descricao":"Produtos de alto valor (curva AAA/AA/A) sem nenhuma cotação registrada (PRE_MIN_COT IS NULL)",
             "sql":"SELECT COUNT(DISTINCT \"ID\") FROM \"NFE\" WHERE \"PRE_MIN_COT\" IS NULL AND \"CURVA_ID\" IN ('AAA','AA','A')"},
            {"id":"02_oportunidade_k03","chave":"pct_linhas_acima_minimo","titulo":"% Linhas Acima do Mínimo",
             "descricao":"Percentual de linhas de compra onde IMP_COT > 0 (compramos mais caro que o menor preço disponível)",
             "sql":"SELECT SUM(CASE WHEN \"IMP_COT\" > 0 THEN 1 ELSE 0 END)*100.0/COUNT(*) FROM \"NFE\" WHERE \"PRE_MIN_COT\" IS NOT NULL"},
            {"id":"02_oportunidade_k04","chave":"itens_mono_cotacao","titulo":"Itens com ≤ 1 Cotação",
             "descricao":"Número de IDs com apenas 1 cotação registrada em NUM_COT — sem concorrência real",
             "sql":"SELECT COUNT(*) FROM \"NUM_COT\" WHERE \"QTD_COT\" = 1"},
        ],
        "relatorios":[
            {"id":"02_oportunidade_r01","arquivo":"02_oportunidade_r01_tabela_principal.csv",
             "titulo":"Tabela de Oportunidades","tipo":"TE",
             "descricao":"Lista priorizada de IDs com tipo (Sem cotação / Monopólio / Acima do mínimo), impacto R$, fornecedor atual vs mais barato",
             "colunas":["tipo","prioridade","id","produto","cat2","uf","fornecedor_atual","fornecedor_mais_barato","preco_minimo","imp_cot","spend","curva_id","status"],
             "sql":"SELECT \"ID\",\"NMPRODUTO_OFICIAL\",\"CAT2\",\"UF\",\"FANTASIA_OFICIAL\",\"FORN_MIN_COT\",\"PRE_MIN_COT\",SUM(\"IMP_COT\") AS imp_cot FROM \"NFE\" WHERE \"IMP_COT\" > 0 GROUP BY \"ID\",\"NMPRODUTO_OFICIAL\",\"CAT2\",\"UF\",\"FANTASIA_OFICIAL\",\"FORN_MIN_COT\",\"PRE_MIN_COT\" ORDER BY imp_cot DESC LIMIT 200"},
            {"id":"02_oportunidade_r02","arquivo":"02_oportunidade_r02_por_categoria.csv",
             "titulo":"Oportunidade por Categoria","tipo":"GB",
             "descricao":"Impacto de cotação agregado por CAT2",
             "colunas":["cat2","imp_cot","ids_afetados"],
             "sql":"SELECT \"CAT2\", SUM(\"IMP_COT\") AS imp_cot FROM \"NFE\" WHERE \"IMP_COT\" > 0 GROUP BY \"CAT2\" ORDER BY imp_cot DESC"},
            {"id":"02_oportunidade_r03","arquivo":"02_oportunidade_r03_por_uf.csv",
             "titulo":"Oportunidade por UF","tipo":"HL",
             "descricao":"Impacto de cotação positivo por UF",
             "colunas":["uf","imp_cot"],
             "sql":"SELECT \"UF\", SUM(\"IMP_COT\") AS imp_cot FROM \"NFE\" WHERE \"IMP_COT\" > 0 GROUP BY \"UF\" ORDER BY imp_cot DESC"},
        ]
    })


# ── 03_categoria ──────────────────────────────────────────────────────────────

def aba_categoria(nfe, lk):
    F="03_categoria"; print(f"  {F}/")
    tg=lk["tg"]

    cd_ = defaultdict(lambda:{"spend":0.0,"imp":0.0,"inf_s":0.0,"inf_n":0,"ids":set(),"forn":set()})
    for r in nfe:
        k=(r.get("CAT1",""),r.get("CAT2",""),r.get("CAT3",""),r.get("CAT4",""),r.get("CAT5",""))
        d=cd_[k]; d["spend"]+=flt(r["TOTAL"])
        imp=flt(r.get("IMP_COT",""))
        if imp>0: d["imp"]+=imp
        inf=flt(r.get("INF_PROD_PMP",""))
        if inf!=0: d["inf_s"]+=inf; d["inf_n"]+=1
        d["ids"].add(r.get("ID","")); d["forn"].add(r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED",""))

    sc(F,"03_categoria_r01_hierarquia.csv", sorted(
       [{"cat1":k[0],"cat2":k[1],"cat3":k[2],"cat4":k[3],"cat5":k[4],
         "spend":r2(d["spend"]),"pct":pct(d["spend"],tg),"imp_cot":r2(d["imp"]),
         "ids_unicos":len(d["ids"]),"fornecedores":len(d["forn"]),
         "inflacao_media_pct":round(d["inf_s"]/d["inf_n"],2) if d["inf_n"] else 0.0}
        for k,d in cd_.items() if k[0].strip()],key=lambda x:-x["spend"]))

    top5 = {r["cat2"] for r in sorted(
        [{"cat2":k[1],"spend":v["spend"]} for k,v in cd_.items() if k[1].strip()],
        key=lambda x:-x["spend"])[:5]}
    cm = defaultdict(float)
    for r in nfe:
        if r.get("CAT2","") in top5: cm[(r.get("CAT2",""),r.get("MESANO",""))]+=flt(r["TOTAL"])
    sc(F,"03_categoria_r02_cat2_por_mes.csv", sorted(
       [{"cat2":k[0],"mesano":k[1],"spend":r2(v)} for k,v in cm.items() if k[1].strip()],
       key=lambda x:(x["cat2"],x["mesano"])))

    cu2 = defaultdict(float)
    for r in nfe: cu2[(r.get("CAT2",""),r.get("UF",""))]+=flt(r["TOTAL"])
    sc(F,"03_categoria_r03_cat2_por_uf.csv",
       [{"cat2":k[0],"uf":k[1],"spend":r2(v)} for k,v in cu2.items() if k[0].strip() and k[1].strip()])

    sj(F,"03_categoria_00_index.json",{
        "aba":"03_categoria","data_page":"categorias","label":"Categorias",
        "nota":"KPIs desta aba são contextuais ao filtro de categoria ativo. Calculados dinamicamente da hierarquia.",
        "relatorios":[
            {"id":"03_categoria_r01","arquivo":"03_categoria_r01_hierarquia.csv",
             "titulo":"Hierarquia Completa CAT1→CAT5","tipo":"TB",
             "descricao":"Drilldown de toda a hierarquia de categorias com spend, IDs únicos, fornecedores e inflação",
             "colunas":["cat1","cat2","cat3","cat4","cat5","spend","pct","imp_cot","ids_unicos","fornecedores","inflacao_media_pct"],
             "sql":"SELECT \"CAT1\",\"CAT2\",\"CAT3\",\"CAT4\",\"CAT5\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CAT1\",\"CAT2\",\"CAT3\",\"CAT4\",\"CAT5\" ORDER BY spend DESC"},
            {"id":"03_categoria_r02","arquivo":"03_categoria_r02_cat2_por_mes.csv",
             "titulo":"CAT2 por Mês","tipo":"GL",
             "descricao":"Evolução temporal das top 5 categorias (CAT2) — séries para gráfico de linhas",
             "colunas":["cat2","mesano","spend"],
             "sql":"SELECT \"CAT2\",\"MESANO\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CAT2\",\"MESANO\" ORDER BY \"CAT2\",\"MESANO\""},
            {"id":"03_categoria_r03","arquivo":"03_categoria_r03_cat2_por_uf.csv",
             "titulo":"CAT2 × UF (Heatmap)","tipo":"MX",
             "descricao":"Spend por CAT2 e UF para matriz de calor",
             "colunas":["cat2","uf","spend"],
             "sql":"SELECT \"CAT2\",\"UF\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CAT2\",\"UF\""},
        ]
    })


# ── 04_filial ─────────────────────────────────────────────────────────────────

def aba_filial(nfe, lk):
    F="04_filial"; print(f"  {F}/")
    tg=lk["tg"]

    bf = defaultdict(lambda:{"spend":0.0,"imp":0.0,"cc":0,"tot":0,"neg":"","uf":"","emp":"","nm":""})
    for r in nfe:
        fil=str(r.get("CDFILIAL","")).strip()
        if not fil: continue
        d=bf[fil]; d["spend"]+=flt(r["TOTAL"]); d["tot"]+=1
        d["neg"]=r.get("FI.NEGOCIO",""); d["uf"]=r.get("UF","")
        d["emp"]=r.get("NMEMP",""); d["nm"]=r.get("NMFILIAL","")
        if r.get("PRE_MIN_COT","").strip() not in ("","0"): d["cc"]+=1
        imp=flt(r.get("IMP_COT",""))
        if imp>0: d["imp"]+=imp

    n=len(bf); maior=max(bf.items(),key=lambda x:x[1]["spend"]) if bf else ("",{"nm":"","spend":0})
    sj(F,"04_filial_k00_kpis.json",{
        "total_comprado":r2(tg),"filiais_ativas":n,
        "compra_media_por_filial":r2(tg/n) if n else 0,
        "maior_filial":maior[1]["nm"] or maior[0],"maior_filial_spend":r2(maior[1]["spend"])})

    sc(F,"04_filial_r01_ranking.csv", sorted(
       [{"cdfilial":k,"nome":d["nm"],"negocio":d["neg"],"uf":d["uf"],"empresa":d["emp"],
         "spend":r2(d["spend"]),"pct":pct(d["spend"],tg),
         "pct_com_cotacao":pct(d["cc"],d["tot"]),"imp_cot":r2(d["imp"])}
        for k,d in bf.items()],key=lambda x:-x["spend"]))

    fn = defaultdict(float)
    for r in nfe:
        fn[(str(r.get("CDFILIAL","")),r.get("FI.NEGOCIO",""))]+=flt(r["TOTAL"])
    sc(F,"04_filial_r02_filial_negocio.csv",
       [{"cdfilial":k[0],"negocio":k[1],"spend":r2(v)} for k,v in fn.items() if k[0].strip() and k[1].strip()])

    top3=[x[0] for x in sorted(bf.items(),key=lambda x:-x[1]["spend"])[:3]]
    fm = defaultdict(float)
    for r in nfe:
        cd=str(r.get("CDFILIAL","")).strip()
        if cd in top3: fm[(cd,r.get("MESANO",""))]+=flt(r["TOTAL"])
    sc(F,"04_filial_r03_top3_por_mes.csv", sorted(
       [{"cdfilial":k[0],"mesano":k[1],"spend":r2(v),"nome":bf[k[0]]["nm"]}
        for k,v in fm.items() if k[1].strip()],key=lambda x:(x["cdfilial"],x["mesano"])))

    fc2 = defaultdict(float)
    for r in nfe:
        cd=str(r.get("CDFILIAL","")).strip()
        if cd: fc2[(cd,r.get("CAT2",""))]+=flt(r["TOTAL"])
    sc(F,"04_filial_r04_por_categoria.csv", sorted(
       [{"cdfilial":k[0],"cat2":k[1],"spend":r2(v)} for k,v in fc2.items() if k[0].strip() and k[1].strip()],
       key=lambda x:(x["cdfilial"],-x["spend"])))

    sj(F,"04_filial_00_index.json",{
        "aba":"04_filial","data_page":"filiais","label":"Filiais",
        "kpis_arquivo":"04_filial_k00_kpis.json",
        "kpis":[
            {"id":"04_filial_k01","chave":"total_comprado","titulo":"Total Comprado","sql":"SELECT SUM(\"TOTAL\") FROM \"NFE\""},
            {"id":"04_filial_k02","chave":"filiais_ativas","titulo":"Filiais Ativas","sql":"SELECT COUNT(DISTINCT \"CDFILIAL\") FROM \"NFE\""},
            {"id":"04_filial_k03","chave":"compra_media_por_filial","titulo":"Compra Média por Filial","sql":"SELECT SUM(\"TOTAL\")/COUNT(DISTINCT \"CDFILIAL\") FROM \"NFE\""},
        ],
        "relatorios":[
            {"id":"04_filial_r01","arquivo":"04_filial_r01_ranking.csv","titulo":"Ranking de Filiais","tipo":"HL",
             "colunas":["cdfilial","nome","negocio","uf","empresa","spend","pct","pct_com_cotacao","imp_cot"],
             "sql":"SELECT \"CDFILIAL\",\"NMFILIAL\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CDFILIAL\",\"NMFILIAL\" ORDER BY spend DESC"},
            {"id":"04_filial_r02","arquivo":"04_filial_r02_filial_negocio.csv","titulo":"Filial × Negócio (Heatmap)","tipo":"MX",
             "colunas":["cdfilial","negocio","spend"],
             "sql":"SELECT \"CDFILIAL\",\"FI.NEGOCIO\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CDFILIAL\",\"FI.NEGOCIO\""},
            {"id":"04_filial_r03","arquivo":"04_filial_r03_top3_por_mes.csv","titulo":"Filial × Mês (top 3)","tipo":"GL",
             "colunas":["cdfilial","mesano","spend","nome"],
             "sql":"SELECT \"CDFILIAL\",\"MESANO\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CDFILIAL\",\"MESANO\" ORDER BY \"MESANO\""},
            {"id":"04_filial_r04","arquivo":"04_filial_r04_por_categoria.csv","titulo":"Filial × Categoria","tipo":"T",
             "colunas":["cdfilial","cat2","spend"],
             "sql":"SELECT \"CDFILIAL\",\"CAT2\",SUM(\"TOTAL\") AS spend FROM \"NFE\" GROUP BY \"CDFILIAL\",\"CAT2\" ORDER BY spend DESC"},
        ]
    })


# ── 05_estoque ────────────────────────────────────────────────────────────────

def aba_estoque():
    F="05_estoque"; print(f"  {F}/ [PENDENTE]")
    (OUT/F).mkdir(parents=True, exist_ok=True)
    sj(F,"05_estoque_00_index.json",{
        "aba":"05_estoque","data_page":"estoque","label":"Estoque",
        "status":"PENDENTE",
        "nota":"Requer workspace APURAÇÃO DE RESULTADOS (ID 2130260000006068011). Adicionar ao sources.yml.",
        "kpis":[],"relatorios":[]})


# ── 06_fornecedor ─────────────────────────────────────────────────────────────

def aba_fornecedor(nfe, cp, ad, lk):
    F="06_fornecedor"; print(f"  {F}/")
    tg=lk["tg"]; fv=lk["fv"]; fcp=lk["fcp"]; fad=lk["fad"]; fc=lk["fc"]
    spend_top=sum(d["spend"] for cd,d in fv.items() if (d["curva"] or fc.get(cd,"")) in ("AAA","AA","A"))
    sj(F,"06_fornecedor_k00_kpis.json",{
        "fornecedores_ativos":len(fv),"spend_curva_aaa_aa_a":r2(spend_top),
        "pct_spend_top":pct(spend_top,tg),
        "forn_com_cp_aberto":sum(1 for cd in fv if fcp.get(cd,{}).get("aberto",0)>0),
        "forn_com_ad_pendente":sum(1 for cd in fv if fad.get(cd,{}).get("pendente",0)>0)})
    rows=[]
    for cd,d in sorted(fv.items(),key=lambda x:-x[1]["spend"]):
        curva=d["curva"] or fc.get(cd,"")
        rows.append({"cdforneced":cd,"fornecedor":d["nm"],"curva":curva,
            "empresas":"|".join(sorted(d["empresas"])),"ufs":"|".join(sorted(d["ufs"])),
            "categorias_top":"|".join(sorted(d["cats"])[:3]),
            "spend_total":r2(d["spend"]),"pct":pct(d["spend"],tg),"imp_cot":r2(d["imp"]),
            "cp_aberto":r2(fcp.get(cd,{}).get("aberto",0)),
            "cp_vencido":r2(fcp.get(cd,{}).get("vencido",0)),
            "ad_pendente":r2(fad.get(cd,{}).get("pendente",0))})
    sc(F,"06_fornecedor_r01_tabela_principal.csv",rows[:500])
    fcat=defaultdict(float)
    for r in nfe:
        cd=r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","")
        fcat[(cd,r.get("CAT2",""))]+=flt(r["TOTAL"])
    sc(F,"06_fornecedor_r02_por_categoria.csv",sorted(
        [{"cdforneced":k[0],"cat2":k[1],"spend":r2(v),"fornecedor":fv.get(k[0],{}).get("nm","")}
         for k,v in fcat.items() if k[0].strip() and k[1].strip()],key=lambda x:(x["cat2"],-x["spend"])))
    sj(F,"06_fornecedor_00_index.json",{
        "aba":"06_fornecedor","data_page":"forn360","label":"Fornecedor",
        "kpis_arquivo":"06_fornecedor_k00_kpis.json",
        "kpis":[
            {"id":"06_fornecedor_k01","chave":"fornecedores_ativos","titulo":"Fornecedores Ativos","sql":"SELECT COUNT(DISTINCT \"CDFORNECED_OFICIAL\") FROM \"NFE\""},
            {"id":"06_fornecedor_k02","chave":"spend_curva_aaa_aa_a","titulo":"Spend AAA/AA/A","sql":"SELECT SUM(\"TOT_FORN\") FROM \"CURVA ABC FORN - TOTAL\" WHERE \"CURVA\" IN ('AAA','AA','A')"},
            {"id":"06_fornecedor_k03","chave":"forn_com_cp_aberto","titulo":"Forn. com CP Aberto","sql":"SELECT COUNT(DISTINCT \"CDFORNECED\") FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto'"},
        ],
        "relatorios":[
            {"id":"06_fornecedor_r01","arquivo":"06_fornecedor_r01_tabela_principal.csv","titulo":"Tabela Fornecedor 360","tipo":"TE",
             "descricao":"Um fornecedor por linha: curva, empresas, UFs, spend, CP, AD","colunas":["cdforneced","fornecedor","curva","empresas","ufs","spend_total","pct","imp_cot","cp_aberto","cp_vencido","ad_pendente"],
             "sql":"SELECT \"CDFORNECED_OFICIAL\",\"FANTASIA_OFICIAL\",SUM(\"TOTAL\") FROM \"NFE\" GROUP BY \"CDFORNECED_OFICIAL\",\"FANTASIA_OFICIAL\" ORDER BY SUM(\"TOTAL\") DESC LIMIT 500"},
            {"id":"06_fornecedor_r02","arquivo":"06_fornecedor_r02_por_categoria.csv","titulo":"Fornecedor × Categoria","tipo":"T",
             "colunas":["cdforneced","fornecedor","cat2","spend"],"sql":"SELECT \"CDFORNECED_OFICIAL\",\"FANTASIA_OFICIAL\",\"CAT2\",SUM(\"TOTAL\") FROM \"NFE\" GROUP BY \"CDFORNECED_OFICIAL\",\"FANTASIA_OFICIAL\",\"CAT2\" ORDER BY SUM(\"TOTAL\") DESC"},
        ]})


# ── 07_produto ────────────────────────────────────────────────────────────────

def aba_produto(nfe, pmp12, lk):
    F="07_produto"; print(f"  {F}/")
    ps=lk["ps"]
    prod=defaultdict(lambda:{"spend":0.0,"imp":0.0,"nm":"","cat2":"","curva_id":"","curva_prod":""})
    for r in nfe:
        cd=r.get("CDPRODUTO_OFICIAL","")
        if not cd: continue
        d=prod[cd]; d["spend"]+=flt(r["TOTAL"]); d["nm"]=r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]=r.get("CAT2",""); d["curva_id"]=r.get("CURVA_ID",""); d["curva_prod"]=r.get("CURVA_PROD","")
        imp=flt(r.get("IMP_COT",""))
        if imp>0: d["imp"]+=imp
    pmp_m=sum(d["pmps"][0] for d in ps.values() if d["pmps"][0]>0)/max(1,sum(1 for d in ps.values() if d["pmps"][0]>0))
    sj(F,"07_produto_k00_kpis.json",{"total_ids":len(ps),"pmp_medio_cesta":r2(pmp_m)})
    rows=[]
    for cd,d in sorted(prod.items(),key=lambda x:-x[1]["spend"])[:200]:
        pd_=ps.get(cd); p0=pd_["pmps"][0] if pd_ and pd_["pmps"][0] else 0
        p12=pd_["pmps"][12] if pd_ and pd_["pmps"][12] else 0
        var=round((p0-p12)/p12*100,2) if p12 else 0.0
        rows.append({"cdproduto":cd,"produto":d["nm"],"cat2":d["cat2"],"curva_id":d["curva_id"],"curva_prod":d["curva_prod"],
            "spend":r2(d["spend"]),"imp_cot":r2(d["imp"]),"pmp_atual":r2(p0),"pmp_12m_anterior":r2(p12),"var_pmp_pct":var,
            "pmp_serie":json.dumps([r2(p) for p in (pd_["pmps"] if pd_ else [])])})
    sc(F,"07_produto_r01_tabela_principal.csv",rows)
    cp2=defaultdict(lambda:{"ps":0.0,"pn":0,"spend":0.0})
    for r in nfe:
        cat=r.get("CAT2",""); pmp=flt(r.get("PMP_PROD",""))
        if pmp>0 and cat.strip(): cp2[cat]["ps"]+=pmp; cp2[cat]["pn"]+=1
        cp2[cat]["spend"]+=flt(r["TOTAL"])
    sc(F,"07_produto_r02_pmp_por_categoria.csv",sorted(
        [{"cat2":k,"pmp_medio":round(d["ps"]/d["pn"],2) if d["pn"] else 0,"spend":r2(d["spend"])} for k,d in cp2.items() if k.strip()],key=lambda x:-x["spend"]))
    pvars=[]
    for cd,d in ps.items():
        pmps=[p for p in d["pmps"] if p>0]
        if len(pmps)<2: continue
        var=round((pmps[0]-pmps[-1])/pmps[-1]*100,2)
        sp=prod.get(cd,{}).get("spend",0)
        if sp<50_000: continue
        pvars.append({"cdproduto":cd,"produto":d["nome"],"cat2":d["cat2"],"curva_id":d["curva"],"var_pmp_pct":var,"spend":r2(sp)})
    sc(F,"07_produto_r03_top_inflacao.csv", sorted([x for x in pvars if x["var_pmp_pct"]>0],key=lambda x:-x["var_pmp_pct"])[:25])
    sc(F,"07_produto_r04_top_deflacao.csv", sorted([x for x in pvars if x["var_pmp_pct"]<0],key=lambda x: x["var_pmp_pct"])[:25])
    sj(F,"07_produto_00_index.json",{
        "aba":"07_produto","data_page":"produtos","label":"Produtos","kpis_arquivo":"07_produto_k00_kpis.json",
        "kpis":[{"id":"07_produto_k01","chave":"total_ids","titulo":"IDs Analisados","sql":"SELECT COUNT(DISTINCT \"ID\") FROM \"PMP_ID_INF_12\""},
                {"id":"07_produto_k02","chave":"pmp_medio_cesta","titulo":"PMP Médio da Cesta","sql":"SELECT AVG(\"PMP_0\") FROM \"PMP_ID_INF_12\" WHERE \"PMP_0\">0"}],
        "relatorios":[
            {"id":"07_produto_r01","arquivo":"07_produto_r01_tabela_principal.csv","titulo":"Tabela de Produtos","tipo":"TE",
             "colunas":["cdproduto","produto","cat2","curva_id","spend","imp_cot","pmp_atual","pmp_12m_anterior","var_pmp_pct","pmp_serie"],
             "sql":"SELECT \"ID\",\"NMPRODUTO_OFICIAL\",\"CAT2\",\"CURVA_ID\",SUM(\"TOTAL\") FROM \"NFE\" GROUP BY \"ID\",\"NMPRODUTO_OFICIAL\",\"CAT2\",\"CURVA_ID\" ORDER BY SUM(\"TOTAL\") DESC LIMIT 200"},
            {"id":"07_produto_r02","arquivo":"07_produto_r02_pmp_por_categoria.csv","titulo":"PMP por Categoria","tipo":"T",
             "colunas":["cat2","pmp_medio","spend"],"sql":"SELECT \"CAT2\",AVG(\"PMP_PROD\") FROM \"NFE\" WHERE \"PMP_PROD\">0 GROUP BY \"CAT2\""},
            {"id":"07_produto_r03","arquivo":"07_produto_r03_top_inflacao.csv","titulo":"Top Inflação","tipo":"HL",
             "colunas":["produto","cat2","curva_id","var_pmp_pct","spend"],"sql":"SELECT \"NMPRODUTO_OFICIAL\",\"CAT2\",\"PMP_0\",\"PMP_12\" FROM \"PMP_PROD_INF_12\" WHERE \"PMP_0\">0 AND \"PMP_12\">0 ORDER BY (\"PMP_0\"-\"PMP_12\")/\"PMP_12\" DESC LIMIT 25"},
            {"id":"07_produto_r04","arquivo":"07_produto_r04_top_deflacao.csv","titulo":"Top Deflação","tipo":"HL",
             "colunas":["produto","cat2","curva_id","var_pmp_pct","spend"],"sql":"SELECT \"NMPRODUTO_OFICIAL\",\"CAT2\",\"PMP_0\",\"PMP_12\" FROM \"PMP_PROD_INF_12\" WHERE \"PMP_0\">0 AND \"PMP_12\">0 ORDER BY (\"PMP_0\"-\"PMP_12\")/\"PMP_12\" ASC LIMIT 25"},
        ]})


# ── 08_cotacao ────────────────────────────────────────────────────────────────

def aba_cotacao(nfe, num_cot, cot, cot_min, lk):
    F="08_cotacao"; print(f"  {F}/")
    qtds=[flt(r.get("QTD_COT","")) for r in num_cot]
    t_ids=len({r.get("ID","") for r in nfe}); t_cot=len({r.get("ID","") for r in num_cot})
    imp_pot=sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT",""))>0)
    n_com=sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("","0"))
    n_ac=sum(1 for r in nfe if flt(r.get("IMP_COT",""))>0)
    sj(F,"08_cotacao_k00_kpis.json",{
        "produtos_cotados":t_cot,"pct_cobertura":pct(t_cot,t_ids),
        "media_cotacoes_produto":round(sum(qtds)/len(qtds),2) if qtds else 0,
        "com_zero_cotacao":sum(1 for q in qtds if q==0),
        "com_uma_cotacao":sum(1 for q in qtds if q==1),
        "com_le3_cotacoes":sum(1 for q in qtds if q<=3),
        "potencial_imp_cot":r2(imp_pot),
        "pct_comprado_no_menor":round(100-pct(n_ac,n_com),2) if n_com else 0})
    mb=defaultdict(lambda:{0:0,1:0,2:0,3:0,4:0,5:0})
    for r in num_cot:
        mes=r.get("MESANO","")
        if not mes.strip(): continue
        q=int(min(flt(r.get("QTD_COT","0")),5)); mb[mes][q]+=1
    sc(F,"08_cotacao_r01_cobertura_por_mes.csv",sorted(
        [{"mesano":k,"zero":d[0],"uma":d[1],"duas_tres":d[2]+d[3],"quatro_mais":d[4]+d[5]} for k,d in mb.items()],key=lambda x:x["mesano"]))
    cb=defaultdict(lambda:{"total":0,"zero":0,"uma":0,"duas_tres":0,"quatro_mais":0})
    for r in num_cot:
        c=r.get("CURVA_ID",""); q=flt(r.get("QTD_COT","0")); cb[c]["total"]+=1
        if q==0: cb[c]["zero"]+=1
        elif q==1: cb[c]["uma"]+=1
        elif q<=3: cb[c]["duas_tres"]+=1
        else: cb[c]["quatro_mais"]+=1
    sc(F,"08_cotacao_r02_cobertura_por_curva.csv",
        [{"curva_id":c,**cb[c],"pct_risco":pct(cb[c]["zero"]+cb[c]["uma"],cb[c]["total"])} for c in ["AAA","AA","A","B","BB","C","CC","CCC"] if cb[c]["total"]>0])
    top5c={k for k,v in sorted(defaultdict(int,{r.get("CAT2",""):1 for r in num_cot}).items(),key=lambda x:-x[1])[:5] if k.strip()}
    ccm=defaultdict(lambda:{"total":0,"com":0})
    for r in num_cot:
        cat2=r.get("CAT2",""); mes=r.get("MESANO","")
        if cat2 not in top5c or not mes.strip(): continue
        ccm[(cat2,mes)]["total"]+=1
        if flt(r.get("QTD_COT",""))>0: ccm[(cat2,mes)]["com"]+=1
    sc(F,"08_cotacao_r03_cobertura_por_cat_mes.csv",sorted(
        [{"cat2":k[0],"mesano":k[1],"total_ids":d["total"],"com_cotacao":d["com"],"pct_cobertura":pct(d["com"],d["total"])} for k,d in ccm.items()],key=lambda x:(x["cat2"],x["mesano"])))
    uc=defaultdict(lambda:{"total":0,"com":0,"spend":0.0,"imp":0.0})
    for r in nfe:
        uf=r.get("UF",""); uc[uf]["total"]+=1; uc[uf]["spend"]+=flt(r["TOTAL"])
        if r.get("PRE_MIN_COT","").strip() not in ("","0"): uc[uf]["com"]+=1
        imp=flt(r.get("IMP_COT",""))
        if imp>0: uc[uf]["imp"]+=imp
    sc(F,"08_cotacao_r04_cobertura_por_uf.csv",sorted(
        [{"uf":k,"total_linhas":d["total"],"com_cotacao":d["com"],"pct_cobertura":pct(d["com"],d["total"]),
          "spend":r2(d["spend"]),"imp_cot":r2(d["imp"]),"imp_sobre_spend_pct":pct(d["imp"],d["spend"])} for k,d in uc.items() if k.strip()],key=lambda x:-x["spend"]))
    fm=defaultdict(lambda:{"n":0,"ids":set(),"nm":""})
    for r in cot_min:
        nm=r.get("FORNE_FANTASIA",""); fm[nm]["n"]+=1; fm[nm]["ids"].add(r.get("ID","")); fm[nm]["nm"]=nm
    sc(F,"08_cotacao_r05_min_cotacao_fornecedor.csv",sorted(
        [{"fornecedor":d["nm"],"vezes_menor_preco":d["n"],"ids_unicos":len(d["ids"])} for cd,d in fm.items() if d["n"]>=2],key=lambda x:-x["vezes_menor_preco"])[:100])
    cr=defaultdict(lambda:{"mn":float("inf"),"ms":0.0,"mc":0,"mx":0.0})
    for r in cot:
        k=(r.get("ID",""),r.get("UF",""),r.get("MESANO","")); v=flt(r.get("PRECOUNIT_EST",""))
        if v<=0: continue
        d=cr[k]; d["mn"]=min(d["mn"],v); d["ms"]+=v; d["mc"]+=1; d["mx"]=max(d["mx"],v)
    sc(F,"08_cotacao_r06_relatorio.csv",sorted(
        [{"id":k[0],"uf":k[1],"mesano":k[2],"preco_min":r2(d["mn"]) if d["mn"]!=float("inf") else 0,
          "preco_med":r2(d["ms"]/d["mc"]) if d["mc"] else 0,"preco_max":r2(d["mx"]),"n_cotacoes":d["mc"]} for k,d in cr.items() if k[0].strip()],key=lambda x:x["mesano"])[:2000])
    sj(F,"08_cotacao_00_index.json",{
        "aba":"08_cotacao","data_page":"cotacoes","label":"Cotações","kpis_arquivo":"08_cotacao_k00_kpis.json",
        "kpis":[
            {"id":"08_cotacao_k01","chave":"produtos_cotados","titulo":"Produtos Cotados","sql":"SELECT COUNT(DISTINCT \"ID\") FROM \"NUM_COT\""},
            {"id":"08_cotacao_k02","chave":"pct_cobertura","titulo":"% Cobertura","sql":"SELECT COUNT(DISTINCT \"ID\")*100.0/(SELECT COUNT(DISTINCT \"ID\") FROM \"NFE\") FROM \"NUM_COT\""},
            {"id":"08_cotacao_k03","chave":"media_cotacoes_produto","titulo":"Média Cotações/Produto","sql":"SELECT AVG(\"QTD_COT\") FROM \"NUM_COT\""},
            {"id":"08_cotacao_k04","chave":"com_uma_cotacao","titulo":"Com 1 Cotação (Risco)","sql":"SELECT COUNT(*) FROM \"NUM_COT\" WHERE \"QTD_COT\"=1"},
            {"id":"08_cotacao_k05","chave":"potencial_imp_cot","titulo":"Potencial IMP_COT","sql":"SELECT SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\">0"},
        ],
        "relatorios":[
            {"id":"08_cotacao_r01","arquivo":"08_cotacao_r01_cobertura_por_mes.csv","titulo":"Distribuição QTD_COT por Mês","tipo":"GE","colunas":["mesano","zero","uma","duas_tres","quatro_mais"],"sql":"SELECT \"MESANO\",\"QTD_COT\",COUNT(*) FROM \"NUM_COT\" GROUP BY \"MESANO\",\"QTD_COT\" ORDER BY \"MESANO\""},
            {"id":"08_cotacao_r02","arquivo":"08_cotacao_r02_cobertura_por_curva.csv","titulo":"Cobertura por Curva ABC","tipo":"MX","colunas":["curva_id","total","zero","uma","duas_tres","quatro_mais","pct_risco"],"sql":"SELECT \"CURVA_ID\",\"QTD_COT\",COUNT(*) FROM \"NUM_COT\" GROUP BY \"CURVA_ID\",\"QTD_COT\""},
            {"id":"08_cotacao_r03","arquivo":"08_cotacao_r03_cobertura_por_cat_mes.csv","titulo":"Cobertura CAT × Mês","tipo":"GL","colunas":["cat2","mesano","total_ids","com_cotacao","pct_cobertura"],"sql":"SELECT \"CAT2\",\"MESANO\",COUNT(*) FROM \"NUM_COT\" GROUP BY \"CAT2\",\"MESANO\""},
            {"id":"08_cotacao_r04","arquivo":"08_cotacao_r04_cobertura_por_uf.csv","titulo":"Cobertura por UF","tipo":"T","colunas":["uf","total_linhas","com_cotacao","pct_cobertura","spend","imp_cot","imp_sobre_spend_pct"],"sql":"SELECT \"UF\",COUNT(*) FROM \"NFE\" GROUP BY \"UF\""},
            {"id":"08_cotacao_r05","arquivo":"08_cotacao_r05_min_cotacao_fornecedor.csv","titulo":"MIN Cotação por Fornecedor","tipo":"T","colunas":["fornecedor","vezes_menor_preco","ids_unicos"],"sql":"SELECT \"FORNE_FANTASIA\",COUNT(*) FROM \"COT_MIN_FORN\" GROUP BY \"FORNE_FANTASIA\" ORDER BY COUNT(*) DESC LIMIT 100"},
            {"id":"08_cotacao_r06","arquivo":"08_cotacao_r06_relatorio.csv","titulo":"Relatório Completo de Cotações","tipo":"T","colunas":["id","uf","mesano","preco_min","preco_med","preco_max","n_cotacoes"],"sql":"SELECT \"ID\",\"UF\",\"MESANO\",MIN(\"PRECOUNIT_EST\"),AVG(\"PRECOUNIT_EST\"),MAX(\"PRECOUNIT_EST\"),COUNT(*) FROM \"COT\" GROUP BY \"ID\",\"UF\",\"MESANO\" LIMIT 2000"},
        ]})


# ── 09_impacto ────────────────────────────────────────────────────────────────

def aba_impacto(nfe, cot_min, lk):
    F="09_impacto"; print(f"  {F}/")
    imp_tot=sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT",""))>0)
    n_ids=len({r.get("ID","") for r in nfe if flt(r.get("IMP_COT",""))>0})
    n_ac=sum(1 for r in nfe if flt(r.get("IMP_COT",""))>0)
    n_com=sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("","0"))
    bu=defaultdict(float)
    for r in nfe:
        imp=flt(r.get("IMP_COT",""))
        if imp>0: bu[r.get("UF","")]+=imp
    uf_l=max(bu.items(),key=lambda x:x[1],default=("",0))
    id_acc=defaultdict(float); id_nm={}
    for r in nfe:
        imp=flt(r.get("IMP_COT",""))
        if imp>0: id_acc[r.get("ID","")]+=imp; id_nm[r.get("ID","")]=r.get("NMPRODUTO_OFICIAL","")
    top_id=max(id_acc.items(),key=lambda x:x[1],default=("",0))
    sj(F,"09_impacto_k00_kpis.json",{
        "imp_cot_total":r2(imp_tot),"ids_com_impacto":n_ids,
        "pct_linhas_acima_minimo":pct(n_ac,n_com) if n_com else 0,
        "uf_lider":uf_l[0],"uf_lider_valor":r2(uf_l[1]),
        "top_produto_nome":id_nm.get(top_id[0],""),"top_produto_imp":r2(top_id[1])})
    bm=defaultdict(float)
    for r in nfe:
        imp=flt(r.get("IMP_COT",""))
        if imp>0: bm[r.get("MESANO","")]+=imp
    sc(F,"09_impacto_r01_por_mes.csv",sorted([{"mesano":k,"imp_cot":r2(v)} for k,v in bm.items() if k.strip()],key=lambda x:x["mesano"]))
    sc(F,"09_impacto_r02_por_uf.csv",sorted([{"uf":k,"imp_cot":r2(v)} for k,v in bu.items() if k.strip()],key=lambda x:-x["imp_cot"]))
    id_d=defaultdict(lambda:{"imp":0.0,"spend":0.0,"produto":"","cat2":"","uf":"","fa":"","fm":"","prm":0.0,"ci":"","cf":""})
    for r in nfe:
        imp=flt(r.get("IMP_COT",""))
        if imp<=0: continue
        k=r.get("ID",""); d=id_d[k]; d["imp"]+=imp; d["spend"]+=flt(r["TOTAL"])
        d["produto"]=r.get("NMPRODUTO_OFICIAL",""); d["cat2"]=r.get("CAT2",""); d["uf"]=r.get("UF","")
        d["fa"]=r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        d["fm"]=r.get("FORN_MIN_COT",""); d["prm"]=flt(r.get("PRE_MIN_COT",""))
        d["ci"]=r.get("CURVA_ID",""); d["cf"]=r.get("CURVA_FORN","")
    sc(F,"09_impacto_r03_top_id.csv",sorted(
        [{"id":k,"produto":d["produto"],"cat2":d["cat2"],"uf":d["uf"],"fornecedor_atual":d["fa"],"fornecedor_mais_barato":d["fm"],
          "preco_minimo":r2(d["prm"]),"imp_cot":r2(d["imp"]),"spend":r2(d["spend"]),"curva_id":d["ci"],"status":"Acima do menor"} for k,d in id_d.items()],
        key=lambda x:-x["imp_cot"])[:100])
    fmn=defaultdict(lambda:{"n":0,"ids":set(),"v":0.0})
    for r in nfe:
        if flt(r.get("IMP_COT",""))>0 and r.get("FORN_MIN_COT","").strip():
            fn=r.get("FORN_MIN_COT",""); fmn[fn]["n"]+=1; fmn[fn]["ids"].add(r.get("ID","")); fmn[fn]["v"]+=flt(r.get("IMP_COT",""))
    sc(F,"09_impacto_r04_forn_mais_barato_nao_escolhido.csv",sorted(
        [{"fornecedor":k,"vezes_mais_barato":d["n"],"ids_unicos":len(d["ids"]),"oportunidade_total":r2(d["v"])} for k,d in fmn.items() if d["n"]>=3],
        key=lambda x:-x["oportunidade_total"])[:50])
    sj(F,"09_impacto_00_index.json",{
        "aba":"09_impacto","data_page":"impacto","label":"Impacto","kpis_arquivo":"09_impacto_k00_kpis.json",
        "nota":"IMP_COT = (preco pago - menor cotacao) x quantidade. Positivo = compramos mais caro que o disponivel.",
        "kpis":[
            {"id":"09_impacto_k01","chave":"imp_cot_total","titulo":"Impacto Total","sql":"SELECT SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\">0"},
            {"id":"09_impacto_k02","chave":"pct_linhas_acima_minimo","titulo":"% Acima do Mínimo","sql":"SELECT SUM(CASE WHEN \"IMP_COT\">0 THEN 1 ELSE 0 END)*100.0/COUNT(*) FROM \"NFE\" WHERE \"PRE_MIN_COT\" IS NOT NULL"},
            {"id":"09_impacto_k03","chave":"uf_lider","titulo":"UF Líder em Impacto","sql":"SELECT \"UF\",SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\">0 GROUP BY \"UF\" ORDER BY SUM(\"IMP_COT\") DESC LIMIT 1"},
        ],
        "relatorios":[
            {"id":"09_impacto_r01","arquivo":"09_impacto_r01_por_mes.csv","titulo":"Impacto por Mês","tipo":"GB","colunas":["mesano","imp_cot"],"sql":"SELECT \"MESANO\",SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\">0 GROUP BY \"MESANO\" ORDER BY \"MESANO\""},
            {"id":"09_impacto_r02","arquivo":"09_impacto_r02_por_uf.csv","titulo":"Impacto por UF","tipo":"HL","colunas":["uf","imp_cot"],"sql":"SELECT \"UF\",SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\">0 GROUP BY \"UF\" ORDER BY SUM(\"IMP_COT\") DESC"},
            {"id":"09_impacto_r03","arquivo":"09_impacto_r03_top_id.csv","titulo":"Top IDs por IMP_COT","tipo":"T","colunas":["id","produto","cat2","uf","fornecedor_atual","fornecedor_mais_barato","preco_minimo","imp_cot","spend","curva_id","status"],"sql":"SELECT \"ID\",\"NMPRODUTO_OFICIAL\",\"CAT2\",\"UF\",\"FANTASIA_OFICIAL\",\"FORN_MIN_COT\",\"PRE_MIN_COT\",SUM(\"IMP_COT\") FROM \"NFE\" WHERE \"IMP_COT\">0 GROUP BY \"ID\",\"NMPRODUTO_OFICIAL\",\"CAT2\",\"UF\",\"FANTASIA_OFICIAL\",\"FORN_MIN_COT\",\"PRE_MIN_COT\" ORDER BY SUM(\"IMP_COT\") DESC LIMIT 100"},
            {"id":"09_impacto_r04","arquivo":"09_impacto_r04_forn_mais_barato_nao_escolhido.csv","titulo":"Fornecedores Mais Baratos Não Escolhidos","tipo":"T","colunas":["fornecedor","vezes_mais_barato","ids_unicos","oportunidade_total"],"sql":"SELECT \"FORN_MIN_COT\",COUNT(*) FROM \"NFE\" WHERE \"IMP_COT\">0 AND \"FORN_MIN_COT\" IS NOT NULL GROUP BY \"FORN_MIN_COT\" ORDER BY COUNT(*) DESC LIMIT 50"},
        ]})


# ── 10_inflacao ───────────────────────────────────────────────────────────────

def aba_inflacao(inf_raw, pmp_prod12, lk):
    F="10_inflacao"; print(f"  {F}/")
    if not inf_raw: print("    [AVISO] inflacao.csv ausente"); return
    inf_vals=[flt(r.get("PERC_INF_ID_PMP","")) for r in inf_raw if flt(r.get("PERC_INF_ID_PMP",""))!=0]
    exp_mon=sum(flt(r.get("SOMA_INF_ID_PMP","")) for r in inf_raw)
    cat_inf=defaultdict(float)
    for r in inf_raw: cat_inf[r.get("CAT2","")]+=flt(r.get("PERC_INF_ID_PMP",""))
    top_cat=max(cat_inf.items(),key=lambda x:x[1],default=("",0))
    sj(F,"10_inflacao_k00_kpis.json",{
        "inflacao_media_pct":round(sum(inf_vals)/len(inf_vals),2) if inf_vals else 0,
        "exposicao_monetaria_12m":r2(exp_mon),
        "ids_com_inflacao_gt10pct":sum(1 for v in inf_vals if v>10),
        "cat2_mais_inflada":top_cat[0]})
    cm=defaultdict(lambda:{"ps":0.0,"pn":0,"rs":0.0})
    for r in inf_raw:
        k=(r.get("CAT2",""),r.get("MESANO",""))
        p=flt(r.get("PERC_INF_ID_PMP",""))
        if p!=0: cm[k]["ps"]+=p; cm[k]["pn"]+=1
        cm[k]["rs"]+=flt(r.get("SOMA_INF_ID_PMP",""))
    sc(F,"10_inflacao_r01_por_cat_mes.csv",sorted(
        [{"cat2":k[0],"mesano":k[1],"inflacao_media_pct":round(d["ps"]/d["pn"],2) if d["pn"] else 0,"exposicao_rs":r2(d["rs"])} for k,d in cm.items() if k[0].strip() and k[1].strip()],
        key=lambda x:(x["cat2"],x["mesano"])))
    mr=defaultdict(float)
    for r in inf_raw: mr[r.get("MESANO","")]+=flt(r.get("SOMA_INF_ID_PMP",""))
    sc(F,"10_inflacao_r02_por_mes_rs.csv",sorted([{"mesano":k,"exposicao_rs":r2(v)} for k,v in mr.items() if k.strip()],key=lambda x:x["mesano"]))
    ui=defaultdict(lambda:{"ps":0.0,"pn":0,"rs":0.0})
    for r in inf_raw:
        uf=r.get("UF",""); p=flt(r.get("PERC_INF_ID_PMP",""))
        if p!=0: ui[uf]["ps"]+=p; ui[uf]["pn"]+=1
        ui[uf]["rs"]+=flt(r.get("SOMA_INF_ID_PMP",""))
    sc(F,"10_inflacao_r03_por_uf.csv",sorted(
        [{"uf":k,"inflacao_media_pct":round(d["ps"]/d["pn"],2) if d["pn"] else 0,"exposicao_rs":r2(d["rs"])} for k,d in ui.items() if k.strip()],
        key=lambda x:-abs(x["inflacao_media_pct"])))
    cat_nac=defaultdict(lambda:{"ps":0.0,"pn":0,"rs":0.0})
    for r in inf_raw:
        cat=r.get("CAT2",""); p=flt(r.get("PERC_INF_ID_PMP",""))
        if p!=0: cat_nac[cat]["ps"]+=p; cat_nac[cat]["pn"]+=1
        cat_nac[cat]["rs"]+=flt(r.get("SOMA_INF_ID_PMP",""))
    sc(F,"10_inflacao_r04_por_categoria.csv",sorted(
        [{"cat2":k,"inflacao_media_pct":round(d["ps"]/d["pn"],2) if d["pn"] else 0,"exposicao_rs":r2(d["rs"])} for k,d in cat_nac.items() if k.strip()],
        key=lambda x:-abs(x["inflacao_media_pct"])))
    pvars=[]
    for r in pmp_prod12:
        p0=flt(r.get("PMP_0","")); p12=flt(r.get("PMP_12",""))
        if p0<=0 or p12<=0: continue
        var=round((p0-p12)/p12*100,2)
        pvars.append({"produto":r.get("NMPRODUTO_OFICIAL",""),"cat2":r.get("CAT2",""),"curva":r.get("CURVA_PROD",""),"pmp_atual":r2(p0),"pmp_12m_anterior":r2(p12),"var_pct":var})
    sc(F,"10_inflacao_r05_top_produto.csv",  sorted([x for x in pvars if x["var_pct"]>0],key=lambda x:-x["var_pct"])[:25])
    sc(F,"10_inflacao_r06_top_deflacao.csv", sorted([x for x in pvars if x["var_pct"]<0],key=lambda x: x["var_pct"])[:25])
    sj(F,"10_inflacao_00_index.json",{
        "aba":"10_inflacao","data_page":"inflacao","label":"Inflação","kpis_arquivo":"10_inflacao_k00_kpis.json",
        "nota":"INF = variacao do PMP ao longo do tempo. DIFERENTE de IMP_COT.",
        "kpis":[
            {"id":"10_inflacao_k01","chave":"inflacao_media_pct","titulo":"Inflação Média (%)","sql":"SELECT AVG(\"PERC_INF_ID_PMP\") FROM \"INFLAÇÃO\" WHERE \"PERC_INF_ID_PMP\"<>0"},
            {"id":"10_inflacao_k02","chave":"exposicao_monetaria_12m","titulo":"Exposição R$ 12m","sql":"SELECT SUM(\"SOMA_INF_ID_PMP\") FROM \"INFLAÇÃO\""},
            {"id":"10_inflacao_k03","chave":"cat2_mais_inflada","titulo":"CAT2 Mais Inflada","sql":"SELECT \"CAT2\",AVG(\"PERC_INF_ID_PMP\") FROM \"INFLAÇÃO\" WHERE \"PERC_INF_ID_PMP\">0 GROUP BY \"CAT2\" ORDER BY AVG(\"PERC_INF_ID_PMP\") DESC LIMIT 1"},
        ],
        "relatorios":[
            {"id":"10_inflacao_r01","arquivo":"10_inflacao_r01_por_cat_mes.csv","titulo":"Inflação % por CAT × Mês","tipo":"GL","colunas":["cat2","mesano","inflacao_media_pct","exposicao_rs"],"sql":"SELECT \"CAT2\",\"MESANO\",AVG(\"PERC_INF_ID_PMP\"),SUM(\"SOMA_INF_ID_PMP\") FROM \"INFLAÇÃO\" GROUP BY \"CAT2\",\"MESANO\""},
            {"id":"10_inflacao_r02","arquivo":"10_inflacao_r02_por_mes_rs.csv","titulo":"Exposição R$ por Mês","tipo":"GB","colunas":["mesano","exposicao_rs"],"sql":"SELECT \"MESANO\",SUM(\"SOMA_INF_ID_PMP\") FROM \"INFLAÇÃO\" GROUP BY \"MESANO\" ORDER BY \"MESANO\""},
            {"id":"10_inflacao_r03","arquivo":"10_inflacao_r03_por_uf.csv","titulo":"Inflação por UF","tipo":"T","colunas":["uf","inflacao_media_pct","exposicao_rs"],"sql":"SELECT \"UF\",AVG(\"PERC_INF_ID_PMP\"),SUM(\"SOMA_INF_ID_PMP\") FROM \"INFLAÇÃO\" GROUP BY \"UF\""},
            {"id":"10_inflacao_r04","arquivo":"10_inflacao_r04_por_categoria.csv","titulo":"Inflação Nacional por Categoria","tipo":"T","colunas":["cat2","inflacao_media_pct","exposicao_rs"],"sql":"SELECT \"CAT2\",AVG(\"PERC_INF_ID_PMP\"),SUM(\"SOMA_INF_ID_PMP\") FROM \"INFLAÇÃO\" GROUP BY \"CAT2\" ORDER BY AVG(\"PERC_INF_ID_PMP\") DESC"},
            {"id":"10_inflacao_r05","arquivo":"10_inflacao_r05_top_produto.csv","titulo":"Top Inflação","tipo":"HL","colunas":["produto","cat2","curva","pmp_atual","pmp_12m_anterior","var_pct"],"sql":"SELECT \"NMPRODUTO_OFICIAL\",\"CAT2\",\"PMP_0\",\"PMP_12\" FROM \"PMP_PROD_INF_12\" WHERE \"PMP_0\">0 AND \"PMP_12\">0 ORDER BY (\"PMP_0\"-\"PMP_12\")/\"PMP_12\" DESC LIMIT 25"},
            {"id":"10_inflacao_r06","arquivo":"10_inflacao_r06_top_deflacao.csv","titulo":"Top Deflação","tipo":"HL","colunas":["produto","cat2","curva","pmp_atual","pmp_12m_anterior","var_pct"],"sql":"SELECT \"NMPRODUTO_OFICIAL\",\"CAT2\",\"PMP_0\",\"PMP_12\" FROM \"PMP_PROD_INF_12\" WHERE \"PMP_0\">0 AND \"PMP_12\">0 ORDER BY (\"PMP_0\"-\"PMP_12\")/\"PMP_12\" ASC LIMIT 25"},
        ]})


# ── 11_fiscal ─────────────────────────────────────────────────────────────────

def aba_fiscal():
    F="11_fiscal"; print(f"  {F}/ [PENDENTE]")
    (OUT/F).mkdir(parents=True, exist_ok=True)
    sj(F,"11_fiscal_00_index.json",{"aba":"11_fiscal","data_page":"fiscal","label":"Fiscal","status":"PENDENTE","nota":"Requer base cadastral de regime fiscal + crédito CBS/IBS 2027.","kpis":[],"relatorios":[]})


# ── 12_financeiro ─────────────────────────────────────────────────────────────

def aba_financeiro(cp, cp_semana, cp_saldo, lk):
    F="12_financeiro"; print(f"  {F}/")
    fc=lk["fc"]
    cp_ab=sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","")=="Em Aberto")
    cp_vc=sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","")=="Em Aberto" and r.get("FAIXA_DIAS","").strip().rstrip("\n").startswith("VE"))
    cp_7d=sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","")=="Em Aberto" and r.get("FAIXA_DIAS","").strip().rstrip("\n") in ("AV 0","AV 7"))
    cp_120=sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","")=="Em Aberto" and r.get("FAIXA_DIAS","").strip().rstrip("\n") in ("VE +120","VE 120"))
    sj(F,"12_financeiro_k00_kpis.json",{"cp_aberto_total":r2(cp_ab),"cp_titulos":sum(1 for r in cp if r.get("STATUSPAG","")=="Em Aberto"),"cp_vencido":r2(cp_vc),"cp_a_vencer_7d":r2(cp_7d),"cp_critico_120d":r2(cp_120)})
    ag=defaultdict(lambda:{"valor":0.0,"titulos":0})
    for r in cp:
        if r.get("STATUSPAG","")!="Em Aberto": continue
        fx=r.get("FAIXA_DIAS","").strip().rstrip("\n"); ag[fx]["valor"]+=flt(r.get("VRATUAPAG","")); ag[fx]["titulos"]+=1
    sc(F,"12_financeiro_r01_aging.csv",sorted([{"faixa_dias":k,"valor":r2(d["valor"]),"titulos":d["titulos"]} for k,d in ag.items() if k],key=lambda x:-x["valor"]))
    fa=defaultdict(lambda:{"aberto":0.0,"vencido":0.0,"a_vencer":0.0,"titulos":0,"nm":""})
    for r in cp:
        if r.get("STATUSPAG","")!="Em Aberto": continue
        cd=r.get("CDFORNECED",""); fx=r.get("FAIXA_DIAS","").strip().rstrip("\n"); v=flt(r.get("VRATUAPAG",""))
        fa[cd]["aberto"]+=v; fa[cd]["titulos"]+=1; fa[cd]["nm"]=r.get("NMFANTFORN","")
        if fx.startswith("VE"): fa[cd]["vencido"]+=v
        elif fx.startswith("AV"): fa[cd]["a_vencer"]+=v
    sc(F,"12_financeiro_r02_por_fornecedor.csv",sorted(
        [{"cdforneced":k,"fornecedor":d["nm"],"curva":fc.get(k,""),"cp_aberto":r2(d["aberto"]),"cp_vencido":r2(d["vencido"]),"cp_a_vencer":r2(d["a_vencer"]),"titulos":d["titulos"]} for k,d in fa.items()],
        key=lambda x:-x["cp_aberto"])[:100])
    if cp_semana:
        sc(F,"12_financeiro_r03_timeline_semanal.csv",sorted(
            [{"fornecedor":r.get("T.FORNECEDOR",""),"semana":r.get("T.SEMANA_ANO",""),"ini":r.get("T.INI_SEMANA",""),"fim":r.get("T.FIM_SEMANA",""),
              "valor_pago":r2(flt(r.get("VALOR_PAGO_SEMANA",""))),"valor_vencimentos":r2(flt(r.get("VALOR_VENCIMENTOS_SEMANA",""))),"valor_vencido":r2(flt(r.get("VALOR_VENCIDO_SEMANA","")))} for r in cp_semana],
            key=lambda x:x["semana"])[:500])
    if cp_saldo:
        sc(F,"12_financeiro_r04_saldo_semanal_2026.csv",sorted(
            [{"cdforneced":r.get("CDFORNECED",""),"fornecedor":r.get("NMFANTFORN",""),"semana":r.get("SEMANA_ANO",""),
              "ini":r.get("INI_SEMANA",""),"fim":r.get("FIM_SEMANA",""),
              "entra":r2(flt(r.get("ENTRA_DIVIDA_SEMANA",""))),"sai":r2(flt(r.get("SAI_DIVIDA_SEMANA",""))),"saldo":r2(flt(r.get("SALDO_DIVIDA_SEMANA","")))} for r in cp_saldo],
            key=lambda x:x["semana"])[:500])
    sj(F,"12_financeiro_00_index.json",{
        "aba":"12_financeiro","data_page":"financeiro","label":"Financeiro","kpis_arquivo":"12_financeiro_k00_kpis.json",
        "nota":"STATUSPAG: 'Em Aberto' = pendente, 'Baixado' = pago.",
        "kpis":[
            {"id":"12_financeiro_k01","chave":"cp_aberto_total","titulo":"CP em Aberto","sql":"SELECT SUM(\"VRATUAPAG\") FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto'"},
            {"id":"12_financeiro_k02","chave":"cp_vencido","titulo":"CP Vencido","sql":"SELECT SUM(\"VRATUAPAG\") FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto' AND \"STATUS_VENC\"='Vencido'"},
            {"id":"12_financeiro_k03","chave":"cp_a_vencer_7d","titulo":"A Vencer em 7d","sql":"SELECT SUM(\"VRATUAPAG\") FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto' AND \"FAIXA_DIAS\" IN ('AV 0','AV 7')"},
            {"id":"12_financeiro_k04","chave":"cp_critico_120d","titulo":"CP Crítico +120d","sql":"SELECT SUM(\"VRATUAPAG\") FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto' AND \"FAIXA_DIAS\" IN ('VE +120','VE 120')"},
        ],
        "relatorios":[
            {"id":"12_financeiro_r01","arquivo":"12_financeiro_r01_aging.csv","titulo":"Aging de CP","tipo":"T","colunas":["faixa_dias","valor","titulos"],"sql":"SELECT \"FAIXA_DIAS\",SUM(\"VRATUAPAG\"),COUNT(*) FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto' GROUP BY \"FAIXA_DIAS\" ORDER BY SUM(\"VRATUAPAG\") DESC"},
            {"id":"12_financeiro_r02","arquivo":"12_financeiro_r02_por_fornecedor.csv","titulo":"CP por Fornecedor","tipo":"T","colunas":["cdforneced","fornecedor","curva","cp_aberto","cp_vencido","cp_a_vencer","titulos"],"sql":"SELECT \"CDFORNECED\",\"NMFANTFORN\",SUM(\"VRATUAPAG\") FROM \"CP\" WHERE \"STATUSPAG\"='Em Aberto' GROUP BY \"CDFORNECED\",\"NMFANTFORN\" ORDER BY SUM(\"VRATUAPAG\") DESC LIMIT 100"},
            {"id":"12_financeiro_r03","arquivo":"12_financeiro_r03_timeline_semanal.csv","titulo":"Timeline Semanal","tipo":"GB","colunas":["semana","ini","fim","valor_pago","valor_vencimentos","valor_vencido"],"sql":"SELECT \"T.SEMANA_ANO\",SUM(\"VALOR_PAGO_SEMANA\"),SUM(\"VALOR_VENCIMENTOS_SEMANA\"),SUM(\"VALOR_VENCIDO_SEMANA\") FROM \"CP_SEMANA\" GROUP BY \"T.SEMANA_ANO\" ORDER BY \"T.SEMANA_ANO\""},
            {"id":"12_financeiro_r04","arquivo":"12_financeiro_r04_saldo_semanal_2026.csv","titulo":"Saldo Semanal 2026","tipo":"T","colunas":["cdforneced","fornecedor","semana","ini","fim","entra","sai","saldo"],"sql":"SELECT \"CDFORNECED\",\"NMFANTFORN\",\"SEMANA_ANO\",\"SALDO_DIVIDA_SEMANA\" FROM \"CP_SALDO_2026_v2\" ORDER BY \"SEMANA_ANO\""},
        ]})


# ── 13_adiantamento ───────────────────────────────────────────────────────────

def aba_adiantamento(ad, lk):
    F="13_adiantamento"; print(f"  {F}/")
    tot=sum(flt(r.get("VALOR_FINAL","")) for r in ad)
    conc=sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","")=="CONCILIADO")
    pend=sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","")=="ADIANTAMENTO ?")
    nc=sum(1 for r in ad if r.get("STATUS_CONCILIACAO","")=="CONCILIADO")
    np=sum(1 for r in ad if r.get("STATUS_CONCILIACAO","")=="ADIANTAMENTO ?")
    sj(F,"13_adiantamento_k00_kpis.json",{"ad_total_12m":r2(tot),"conciliado":r2(conc),"n_conciliado":nc,"pendente":r2(pend),"n_pendente":np,"pct_conciliado":pct(conc,tot)})
    sc(F,"13_adiantamento_r01_funil.csv",[{"status":"Total lançado","valor":r2(tot),"registros":len(ad)},{"status":"Conciliado","valor":r2(conc),"registros":nc},{"status":"Pendente","valor":r2(pend),"registros":np}])
    be=defaultdict(lambda:{"conc":0.0,"pend":0.0})
    for r in ad:
        emp=r.get("NMEMP",""); v=flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","")=="CONCILIADO": be[emp]["conc"]+=v
        else: be[emp]["pend"]+=v
    sc(F,"13_adiantamento_r02_por_empresa.csv",[{"empresa":k,"conciliado":r2(d["conc"]),"pendente":r2(d["pend"])} for k,d in be.items() if k.strip()])
    bm=defaultdict(lambda:{"conc":0.0,"pend":0.0})
    for r in ad:
        mes=r.get("MES_ENTRADA","") or r.get("MES_PGTO",""); v=flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","")=="CONCILIADO": bm[mes]["conc"]+=v
        else: bm[mes]["pend"]+=v
    sc(F,"13_adiantamento_r03_por_mes.csv",sorted([{"mesano":k,"conciliado":r2(d["conc"]),"pendente":r2(d["pend"])} for k,d in bm.items() if k.strip()],key=lambda x:x["mesano"]))
    bu=defaultdict(float)
    for r in ad: bu[r.get("UF","")]+=flt(r.get("VALOR_FINAL",""))
    sc(F,"13_adiantamento_r04_por_uf.csv",sorted([{"uf":k,"valor_total":r2(v)} for k,v in bu.items() if k.strip()],key=lambda x:-x["valor_total"]))
    bcat=defaultdict(lambda:{"pend":0.0,"conc":0.0})
    for r in ad:
        cat=r.get("CAT2","") or r.get("CAT1",""); v=flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","")=="CONCILIADO": bcat[cat]["conc"]+=v
        else: bcat[cat]["pend"]+=v
    sc(F,"13_adiantamento_r05_por_categoria.csv",sorted([{"categoria":k,"pendente":r2(d["pend"]),"conciliado":r2(d["conc"])} for k,d in bcat.items() if k.strip()],key=lambda x:-(x["pendente"]+x["conciliado"])))
    bf=defaultdict(lambda:{"pend":0.0,"conc":0.0,"nm":"","regs":0})
    for r in ad:
        cd=r.get("CDFORNECED",""); v=flt(r.get("VALOR_FINAL",""))
        bf[cd]["nm"]=r.get("FANTASIA_OFICIAL",""); bf[cd]["regs"]+=1
        if r.get("STATUS_CONCILIACAO","")=="CONCILIADO": bf[cd]["conc"]+=v
        else: bf[cd]["pend"]+=v
    sc(F,"13_adiantamento_r06_por_fornecedor.csv",sorted(
        [{"cdforneced":k,"fornecedor":d["nm"],"pendente":r2(d["pend"]),"conciliado":r2(d["conc"]),"registros":d["regs"]} for k,d in bf.items()],
        key=lambda x:-x["pendente"])[:100])
    sj(F,"13_adiantamento_00_index.json",{
        "aba":"13_adiantamento","data_page":"adiantamentos","label":"Adiantamentos","kpis_arquivo":"13_adiantamento_k00_kpis.json",
        "nota":"STATUS_CONCILIACAO: 'CONCILIADO'=ok, 'ADIANTAMENTO ?'=pendente/indefinido",
        "kpis":[
            {"id":"13_adiantamento_k01","chave":"ad_total_12m","titulo":"AD Total 12m","sql":"SELECT SUM(\"VALOR_FINAL\") FROM \"AD_v3\""},
            {"id":"13_adiantamento_k02","chave":"pendente","titulo":"AD Pendente","sql":"SELECT SUM(\"VALOR_FINAL\") FROM \"AD_v3\" WHERE \"STATUS_CONCILIACAO\"='ADIANTAMENTO ?'"},
            {"id":"13_adiantamento_k03","chave":"pct_conciliado","titulo":"% Conciliado","sql":"SELECT SUM(CASE WHEN \"STATUS_CONCILIACAO\"='CONCILIADO' THEN \"VALOR_FINAL\" ELSE 0 END)*100.0/SUM(\"VALOR_FINAL\") FROM \"AD_v3\""},
        ],
        "relatorios":[
            {"id":"13_adiantamento_r01","arquivo":"13_adiantamento_r01_funil.csv","titulo":"Funil de Conciliação","tipo":"FU","colunas":["status","valor","registros"],"sql":"SELECT \"STATUS_CONCILIACAO\",SUM(\"VALOR_FINAL\"),COUNT(*) FROM \"AD_v3\" GROUP BY \"STATUS_CONCILIACAO\""},
            {"id":"13_adiantamento_r02","arquivo":"13_adiantamento_r02_por_empresa.csv","titulo":"AD por Empresa","tipo":"HL","colunas":["empresa","conciliado","pendente"],"sql":"SELECT \"NMEMP\",\"STATUS_CONCILIACAO\",SUM(\"VALOR_FINAL\") FROM \"AD_v3\" GROUP BY \"NMEMP\",\"STATUS_CONCILIACAO\""},
            {"id":"13_adiantamento_r03","arquivo":"13_adiantamento_r03_por_mes.csv","titulo":"AD por Mês","tipo":"GL","colunas":["mesano","conciliado","pendente"],"sql":"SELECT \"MES_ENTRADA\",\"STATUS_CONCILIACAO\",SUM(\"VALOR_FINAL\") FROM \"AD_v3\" GROUP BY \"MES_ENTRADA\",\"STATUS_CONCILIACAO\" ORDER BY \"MES_ENTRADA\""},
            {"id":"13_adiantamento_r04","arquivo":"13_adiantamento_r04_por_uf.csv","titulo":"AD por UF","tipo":"HL","colunas":["uf","valor_total"],"sql":"SELECT \"UF\",SUM(\"VALOR_FINAL\") FROM \"AD_v3\" GROUP BY \"UF\" ORDER BY SUM(\"VALOR_FINAL\") DESC"},
            {"id":"13_adiantamento_r05","arquivo":"13_adiantamento_r05_por_categoria.csv","titulo":"AD por Categoria","tipo":"T","colunas":["categoria","pendente","conciliado"],"sql":"SELECT \"CAT2\",\"STATUS_CONCILIACAO\",SUM(\"VALOR_FINAL\") FROM \"AD_v3\" GROUP BY \"CAT2\",\"STATUS_CONCILIACAO\""},
            {"id":"13_adiantamento_r06","arquivo":"13_adiantamento_r06_por_fornecedor.csv","titulo":"AD por Fornecedor","tipo":"T","colunas":["cdforneced","fornecedor","pendente","conciliado","registros"],"sql":"SELECT \"CDFORNECED\",\"FANTASIA_OFICIAL\",\"STATUS_CONCILIACAO\",SUM(\"VALOR_FINAL\"),COUNT(*) FROM \"AD_v3\" GROUP BY \"CDFORNECED\",\"FANTASIA_OFICIAL\",\"STATUS_CONCILIACAO\" ORDER BY SUM(\"VALOR_FINAL\") DESC LIMIT 100"},
        ]})


# ── 14_servico ────────────────────────────────────────────────────────────────

def aba_servico(nfe, lk):
    F="14_servico"; print(f"  {F}/")
    fin={"MUTUO","DEVOLUCAO","EMPRESTIMO","ICMS","PARCELAMENTO"}
    def is_fin(r): nm=(r.get("NMPRODUTO_OFICIAL","") or "").upper(); return any(f in nm for f in fin)
    d5=[r for r in nfe if r.get("CAT2","").startswith("D5") and not is_fin(r)]
    tot=sum(flt(r["TOTAL"]) for r in d5)
    sj(F,"14_servico_k00_kpis.json",{
        "total_servicos":r2(tot),
        "fornecedores_servicos":len({r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","") for r in d5}),
        "ufs_atendidas":len({r.get("UF","") for r in d5})})
    bu=defaultdict(float)
    for r in d5: bu[r.get("UF","")]+=flt(r["TOTAL"])
    sc(F,"14_servico_r01_por_uf.csv",sorted([{"uf":k,"spend":r2(v),"pct":pct(v,tot)} for k,v in bu.items() if k.strip()],key=lambda x:-x["spend"]))
    bm=defaultdict(float)
    for r in d5: bm[r.get("MESANO","")]+=flt(r["TOTAL"])
    sc(F,"14_servico_r02_por_mes.csv",sorted([{"mesano":k,"spend":r2(v)} for k,v in bm.items() if k.strip()],key=lambda x:x["mesano"]))
    bc=defaultdict(float)
    for r in d5: bc[r.get("CAT3","") or r.get("CAT2","")]+=flt(r["TOTAL"])
    sc(F,"14_servico_r03_por_categoria.csv",sorted([{"categoria":k,"spend":r2(v),"pct":pct(v,tot)} for k,v in bc.items() if k.strip()],key=lambda x:-x["spend"])[:20])
    bf=defaultdict(lambda:{"spend":0.0,"nm":"","cat":""})
    for r in d5:
        cd=r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","")
        bf[cd]["spend"]+=flt(r["TOTAL"]); bf[cd]["nm"]=r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN",""); bf[cd]["cat"]=r.get("CAT3","") or r.get("CAT2","")
    sc(F,"14_servico_r04_por_fornecedor.csv",sorted([{"cdforneced":k,"fornecedor":d["nm"],"categoria":d["cat"],"spend":r2(d["spend"]),"pct":pct(d["spend"],tot)} for k,d in bf.items()],key=lambda x:-x["spend"])[:50])
    sj(F,"14_servico_00_index.json",{
        "aba":"14_servico","data_page":"servicos","label":"Serviços","kpis_arquivo":"14_servico_k00_kpis.json",
        "nota":"Filtra CAT2=D5 excluindo lancamentos financeiros (MUTUO, DEVOLUCAO, EMPRESTIMO, ICMS, PARCELAMENTO)",
        "kpis":[
            {"id":"14_servico_k01","chave":"total_servicos","titulo":"Total em Serviços","sql":"SELECT SUM(\"TOTAL\") FROM \"NFE\" WHERE \"CAT2\" LIKE 'D5%' AND \"NMPRODUTO_OFICIAL\" NOT LIKE '%MUTUO%'"},
            {"id":"14_servico_k02","chave":"fornecedores_servicos","titulo":"Fornecedores de Serviços","sql":"SELECT COUNT(DISTINCT \"CDFORNECED_OFICIAL\") FROM \"NFE\" WHERE \"CAT2\" LIKE 'D5%'"},
        ],
        "relatorios":[
            {"id":"14_servico_r01","arquivo":"14_servico_r01_por_uf.csv","titulo":"Serviços por UF","tipo":"HL","colunas":["uf","spend","pct"],"sql":"SELECT \"UF\",SUM(\"TOTAL\") FROM \"NFE\" WHERE \"CAT2\" LIKE 'D5%' GROUP BY \"UF\" ORDER BY SUM(\"TOTAL\") DESC"},
            {"id":"14_servico_r02","arquivo":"14_servico_r02_por_mes.csv","titulo":"Serviços por Mês","tipo":"GB","colunas":["mesano","spend"],"sql":"SELECT \"MESANO\",SUM(\"TOTAL\") FROM \"NFE\" WHERE \"CAT2\" LIKE 'D5%' GROUP BY \"MESANO\" ORDER BY \"MESANO\""},
            {"id":"14_servico_r03","arquivo":"14_servico_r03_por_categoria.csv","titulo":"Serviços por Categoria","tipo":"T","colunas":["categoria","spend","pct"],"sql":"SELECT \"CAT3\",SUM(\"TOTAL\") FROM \"NFE\" WHERE \"CAT2\" LIKE 'D5%' GROUP BY \"CAT3\" ORDER BY SUM(\"TOTAL\") DESC LIMIT 20"},
            {"id":"14_servico_r04","arquivo":"14_servico_r04_por_fornecedor.csv","titulo":"Fornecedores de Serviços","tipo":"T","colunas":["cdforneced","fornecedor","categoria","spend","pct"],"sql":"SELECT \"CDFORNECED_OFICIAL\",\"FANTASIA_OFICIAL\",SUM(\"TOTAL\") FROM \"NFE\" WHERE \"CAT2\" LIKE 'D5%' GROUP BY \"CDFORNECED_OFICIAL\",\"FANTASIA_OFICIAL\" ORDER BY SUM(\"TOTAL\") DESC LIMIT 50"},
        ]})


# ── 15_dados ──────────────────────────────────────────────────────────────────

def aba_dados(nfe, lk):
    F="15_dados"; print(f"  {F}/")
    mp=RAW/"manifest.json"
    manifest=json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    sources=[]
    for k,v in manifest.items():
        if isinstance(v,dict) and "status" in v:
            sources.append({"arquivo":k+".csv","linhas":v.get("rows",0),"status":v.get("status","")})
    sc(F,"15_dados_r01_status_fontes.csv",sources)
    lsc=sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() in ("","0"))
    prods_sc=sum(1 for r in nfe if not r.get("CDPRODUTO_OFICIAL","").strip())
    forn_so=sum(1 for r in nfe if not r.get("CDFORNECED_OFICIAL","").strip())
    lscat=sum(1 for r in nfe if not r.get("CAT1","").strip())
    sc(F,"15_dados_r02_fila_saneamento.csv",[
        {"problema":"Linhas sem cotação","campo":"PRE_MIN_COT","linhas":lsc,"pct":pct(lsc,len(nfe)),"impacto":"Alto"},
        {"problema":"Produtos sem código oficial","campo":"CDPRODUTO_OFICIAL","linhas":prods_sc,"pct":pct(prods_sc,len(nfe)),"impacto":"Médio"},
        {"problema":"Fornecedores sem código oficial","campo":"CDFORNECED_OFICIAL","linhas":forn_so,"pct":pct(forn_so,len(nfe)),"impacto":"Médio"},
        {"problema":"Linhas sem categoria","campo":"CAT1","linhas":lscat,"pct":pct(lscat,len(nfe)),"impacto":"Baixo"},
    ])
    sj(F,"15_dados_k00_kpis.json",{
        "linhas_total_nfe":len(nfe),"fontes_ok":sum(1 for s in sources if s.get("status")=="ok"),
        "fontes_total":len(sources),"linhas_sem_cotacao":lsc,"pct_sem_cotacao":pct(lsc,len(nfe)),"produtos_sem_codigo":prods_sc})
    sj(F,"15_dados_00_index.json",{
        "aba":"15_dados","data_page":"qualidade","label":"Dados","kpis_arquivo":"15_dados_k00_kpis.json",
        "kpis":[
            {"id":"15_dados_k01","chave":"linhas_total_nfe","titulo":"Linhas Totais NFE","sql":"SELECT COUNT(*) FROM \"NFE\""},
            {"id":"15_dados_k02","chave":"fontes_ok","titulo":"Fontes OK","descricao":"Fontes extraídas com sucesso no último extract.py"},
            {"id":"15_dados_k03","chave":"linhas_sem_cotacao","titulo":"Linhas sem Cotação","sql":"SELECT COUNT(*) FROM \"NFE\" WHERE \"PRE_MIN_COT\" IS NULL"},
        ],
        "relatorios":[
            {"id":"15_dados_r01","arquivo":"15_dados_r01_status_fontes.csv","titulo":"Status por Fonte","tipo":"T","colunas":["arquivo","linhas","status"],"descricao":"Status das 18 fontes do pipeline"},
            {"id":"15_dados_r02","arquivo":"15_dados_r02_fila_saneamento.csv","titulo":"Fila de Saneamento","tipo":"T","colunas":["problema","campo","linhas","pct","impacto"],"descricao":"Problemas de qualidade identificados"},
        ]})


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    import shutil
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    print(f"Carregando dados de {RAW}...")
    nfe=load("nfe.csv"); cp=load("cp.csv"); ad=load("ad_v3.csv")
    curva_forn=load("curva_forn.csv"); num_cot=load("num_cot.csv")
    cot=load("cot.csv"); cot_min=load("cot_min_forn.csv")
    inf_raw=load("inflacao.csv"); pmp12=load("pmp_id_inf_12.csv")
    pmp_p12=load("pmp_prod_inf_12.csv"); cp_semana=load("cp_semana.csv")
    cp_saldo=load("cp_saldo_2026.csv")
    print(f"  NFE:{len(nfe):,} CP:{len(cp):,} AD:{len(ad):,} COT:{len(cot):,} INF:{len(inf_raw):,}")
    print()
    lk=build_lookups(nfe,cp,ad,curva_forn,pmp12)
    print("Transformando por aba...")
    aba_resumo(nfe,cp,ad,lk)
    aba_oportunidade(nfe,num_cot,lk)
    aba_categoria(nfe,lk)
    aba_filial(nfe,lk)
    aba_estoque()
    aba_fornecedor(nfe,cp,ad,lk)
    aba_produto(nfe,pmp12,lk)
    aba_cotacao(nfe,num_cot,cot,cot_min,lk)
    aba_impacto(nfe,cot_min,lk)
    aba_inflacao(inf_raw,pmp_p12,lk)
    aba_fiscal()
    aba_financeiro(cp,cp_semana,cp_saldo,lk)
    aba_adiantamento(ad,lk)
    aba_servico(nfe,lk)
    aba_dados(nfe,lk)
    outputs=list(OUT.rglob("*.csv"))+list(OUT.rglob("*.json"))
    total_kb=sum(p.stat().st_size for p in outputs)/1024
    manifest={"generated_at":datetime.now(timezone.utc).isoformat(),"total_files":len(outputs),"total_kb":round(total_kb,1),"abas":{}}
    for p in outputs: manifest["abas"].setdefault(p.parent.name,[]).append(p.name)
    (OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"\nConcluído: {len(outputs)} arquivos  ({total_kb:.0f} KB)")
    for aba in sorted(manifest["abas"]):
        files=manifest["abas"][aba]
        kb=sum((OUT/aba/f).stat().st_size for f in files if (OUT/aba/f).exists())/1024
        print(f"  {aba:<28} {len(files):>3} arqs  {kb:>7.1f} KB")

if __name__=="__main__":
    main()
