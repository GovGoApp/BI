"""Transforma dados brutos de data/raw/ em métricas prontas em data/processed/.

Estrutura de saída:
  data/processed/{aba}/kpis.json      — KPIs da aba
  data/processed/{aba}/{dataset}.csv  — tabelas e séries

Segue fielmente ESTRUTURA_ABAS.md.
Uso: python pipeline/transform.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW  = ROOT / "data" / "raw"
OUT  = ROOT / "data" / "processed"

# UFs por região geográfica
GEO_NNE = {"MA", "PA", "PI", "PB", "PE", "RN", "SE", "AL", "BA", "CE", "AP", "AM", "RR", "TO", "AC", "RO"}
GEO_SSE = {"SP", "RJ", "ES", "MG", "PR", "SC", "RS", "MS", "MT", "GO", "DF"}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def load(filename: str) -> list[dict[str, str]]:
    path = RAW / filename
    if not path.exists():
        print(f"  [AVISO] {filename} não encontrado")
        return []
    with path.open(encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def flt(v: Any) -> float:
    if not v or str(v).strip() == "":
        return 0.0
    try:
        return float(str(v).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def pct(part: float, total: float) -> float:
    return round(part / total * 100, 2) if total else 0.0


def r2(v: float) -> float:
    return round(v, 2)


def save_csv(aba: str, name: str, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        return
    dest = OUT / aba / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    f_list = fields or list(rows[0].keys())
    with dest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=f_list, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def save_json(aba: str, name: str, data: Any) -> None:
    dest = OUT / aba / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def top_sorted(d: dict, key: str, n: int = None) -> list:
    rows = sorted(d.values(), key=lambda x: -x.get(key, 0))
    return rows[:n] if n else rows


# ─── Lookups (construídos uma vez, usados por múltiplas abas) ────────────────

def build_lookups(nfe, cp, ad, curva_forn, pmp12, cp_semana):
    print("  Construindo lookups...")

    total_geral = sum(flt(r["TOTAL"]) for r in nfe)

    # CP por fornecedor
    forn_cp: dict[str, dict] = defaultdict(lambda: {"aberto": 0.0, "vencido": 0.0, "titulos": 0, "nm": ""})
    for r in cp:
        cd = r.get("CDFORNECED", "")
        if r.get("STATUSPAG", "") == "Em Aberto":
            forn_cp[cd]["aberto"]  += flt(r.get("VRATUAPAG", ""))
            forn_cp[cd]["titulos"] += 1
            faixa = r.get("FAIXA_DIAS", "").strip().rstrip("\n")
            if faixa.startswith("VE"):
                forn_cp[cd]["vencido"] += flt(r.get("VRATUAPAG", ""))
        forn_cp[cd]["nm"] = r.get("NMFANTFORN", "")

    # AD por fornecedor
    forn_ad: dict[str, dict] = defaultdict(lambda: {"pendente": 0.0, "conciliado": 0.0, "nm": ""})
    for r in ad:
        cd = r.get("CDFORNECED", "")
        v  = flt(r.get("VALOR_FINAL", ""))
        if r.get("STATUS_CONCILIACAO", "") == "ADIANTAMENTO ?":
            forn_ad[cd]["pendente"] += v
        else:
            forn_ad[cd]["conciliado"] += v
        forn_ad[cd]["nm"] = r.get("FANTASIA_OFICIAL", "")

    # Curva forn (do arquivo CURVA ABC FORN - TOTAL)
    forn_curva: dict[str, str] = {}
    forn_razao: dict[str, str] = {}
    for r in curva_forn:
        cd = r.get("CDFORNECED", "")
        forn_curva[cd] = r.get("CURVA", "")
        forn_razao[cd] = r.get("RAZAO_SOCIAL", "")

    # PMP série 12 meses por ID
    pmp_series: dict[str, dict] = {}
    for r in pmp12:
        id_ = r.get("ID", "")
        if id_:
            pmp_series[id_] = {
                "nome": r.get("NMPRODUTO_OFICIAL", ""),
                "cat2": r.get("CAT2", ""),
                "curva": r.get("CURVA_ID", ""),
                "pmps": [flt(r.get(f"PMP_{i}", "")) for i in range(13)],
            }

    # Fornecedor spend do NFE
    forn_spend: dict[str, dict] = defaultdict(lambda: {
        "spend": 0.0, "imp_cot": 0.0, "nm": "", "curva": "",
        "empresas": set(), "ufs": set(), "cats": set()
    })
    for r in nfe:
        cd  = r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED", "")
        d   = forn_spend[cd]
        d["spend"]   += flt(r["TOTAL"])
        d["nm"]       = r.get("FANTASIA_OFICIAL") or r.get("NMFANTFORN", "")
        d["curva"]    = r.get("CURVA_FORN", "")
        imp = flt(r.get("IMP_COT", ""))
        if imp > 0:
            d["imp_cot"] += imp
        d["empresas"].add(r.get("NMEMP", ""))
        d["ufs"].add(r.get("UF", ""))
        d["cats"].add(r.get("CAT2", ""))

    return {
        "total_geral": total_geral,
        "forn_cp": forn_cp,
        "forn_ad": forn_ad,
        "forn_curva": forn_curva,
        "forn_razao": forn_razao,
        "pmp_series": pmp_series,
        "forn_spend": forn_spend,
    }


# ─── ABA: RESUMO ─────────────────────────────────────────────────────────────

def aba_resumo(nfe, cp, ad, lk):
    print("  resumo/")
    tg = lk["total_geral"]
    fcp = lk["forn_cp"]

    # KPIs
    financeiros = {"MUTUO","DEVOLUCAO","EMPRESTIMO","ICMS","PARCELAMENTO","IMPOSTO","TAXA","DEDUCAO"}
    def is_financeiro(r):
        nm = (r.get("NMPRODUTO_OFICIAL","") or "").upper()
        return any(f in nm for f in financeiros)

    total_op = sum(flt(r["TOTAL"]) for r in nfe if not is_financeiro(r))
    t2024    = sum(flt(r["TOTAL"]) for r in nfe if str(r.get("ANO","")) == "2024")
    t2025    = sum(flt(r["TOTAL"]) for r in nfe if str(r.get("ANO","")) == "2025")
    yoy      = pct(t2025 - t2024, t2024)
    forn_at  = len({r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","") for r in nfe})
    com_cot  = sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("","0"))
    pct_cot  = pct(com_cot, len(nfe))
    imp_tot  = sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT","")) > 0)
    cp_ab    = sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","") == "Em Aberto")
    cp_tit   = sum(1 for r in cp if r.get("STATUSPAG","") == "Em Aberto")
    ad_pend  = sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","") == "ADIANTAMENTO ?")

    save_json("resumo", "kpis.json", {
        "total_comprado_operacional": r2(total_op),
        "total_comprado_periodo": r2(tg),
        "crescimento_yoy_pct": yoy,
        "fornecedores_ativos": forn_at,
        "pct_com_cotacao": pct_cot,
        "imp_cot_total": r2(imp_tot),
        "cp_aberto": r2(cp_ab),
        "cp_titulos": cp_tit,
        "ad_pendente": r2(ad_pend),
    })

    # Evolução mensal
    by_mes: dict[str, float] = defaultdict(float)
    for r in nfe:
        by_mes[r.get("MESANO","")]  += flt(r["TOTAL"])
    save_csv("resumo", "por_mes.csv", [
        {"mesano": k, "spend": r2(v)}
        for k, v in sorted(by_mes.items()) if k.strip()
    ])

    # Por negócio (com CP e impacto)
    by_neg: dict[str, dict] = defaultdict(lambda: {"spend": 0.0, "imp_cot": 0.0, "linhas": 0})
    neg_cp: dict[str, float] = defaultdict(float)
    for r in nfe:
        neg = r.get("FI.NEGOCIO","") or ""
        by_neg[neg]["spend"]  += flt(r["TOTAL"])
        by_neg[neg]["linhas"] += 1
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            by_neg[neg]["imp_cot"] += imp
    # CP por negócio (aproximado via filial)
    for r in cp:
        if r.get("STATUSPAG","") == "Em Aberto":
            neg_cp[""] += flt(r.get("VRATUAPAG",""))
    save_csv("resumo", "por_negocio.csv", sorted([
        {"negocio": k, "spend": r2(d["spend"]), "pct": pct(d["spend"], tg), "imp_cot": r2(d["imp_cot"])}
        for k, d in by_neg.items() if k.strip()
    ], key=lambda x: -x["spend"]))

    # Top categorias
    by_cat2: dict[str, dict] = defaultdict(lambda: {"spend": 0.0, "imp": 0.0, "inf_s": 0.0, "inf_n": 0})
    for r in nfe:
        c = r.get("CAT2","")
        by_cat2[c]["spend"] += flt(r["TOTAL"])
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: by_cat2[c]["imp"] += imp
        inf = flt(r.get("INF_PROD_PMP",""))
        if inf != 0: by_cat2[c]["inf_s"] += inf; by_cat2[c]["inf_n"] += 1
    save_csv("resumo", "top_categorias.csv", sorted([
        {"cat2": k, "spend": r2(d["spend"]), "pct": pct(d["spend"], tg),
         "imp_cot": r2(d["imp"]),
         "inflacao_media_pct": round(d["inf_s"]/d["inf_n"],2) if d["inf_n"] else 0.0}
        for k, d in by_cat2.items() if k.strip()
    ], key=lambda x: -x["spend"])[:20])

    # Top fornecedores (com CP)
    fv = lk["forn_spend"]
    acum = 0.0
    rows_forn = []
    for cd, d in sorted(fv.items(), key=lambda x: -x[1]["spend"])[:20]:
        acum += d["spend"]
        rows_forn.append({
            "cdforneced": cd, "fornecedor": d["nm"],
            "curva": d["curva"] or lk["forn_curva"].get(cd,""),
            "spend": r2(d["spend"]), "pct": pct(d["spend"], tg), "pct_acum": pct(acum, tg),
            "imp_cot": r2(d["imp_cot"]),
            "cp_aberto": r2(fcp[cd]["aberto"]) if cd in fcp else 0.0,
        })
    save_csv("resumo", "top_fornecedores.csv", rows_forn)

    # Por UF (completo)
    by_uf: dict[str, float] = defaultdict(float)
    for r in nfe:
        by_uf[r.get("UF","")] += flt(r["TOTAL"])
    save_csv("resumo", "por_uf.csv", sorted([
        {"uf": k, "spend": r2(v), "pct": pct(v, tg)}
        for k, v in by_uf.items() if k.strip()
    ], key=lambda x: -x["spend"]))

    # Geo N/NE
    save_csv("resumo", "geo_nne.csv", sorted([
        {"uf": k, "spend": r2(v), "pct": pct(v, tg)}
        for k, v in by_uf.items() if k.strip() and k in GEO_NNE
    ], key=lambda x: -x["spend"]))

    # Geo S/SE
    save_csv("resumo", "geo_sse.csv", sorted([
        {"uf": k, "spend": r2(v), "pct": pct(v, tg)}
        for k, v in by_uf.items() if k.strip() and k in GEO_SSE
    ], key=lambda x: -x["spend"]))

    # Por filial top 8 (com negócio, UF, CP)
    by_fil: dict[str, dict] = defaultdict(lambda: {"spend": 0.0, "neg": "", "uf": "", "emp": "", "nm": "", "imp": 0.0})
    for r in nfe:
        fil = str(r.get("CDFILIAL","")).strip()
        if not fil: continue
        d = by_fil[fil]
        d["spend"] += flt(r["TOTAL"])
        d["neg"]    = r.get("FI.NEGOCIO","")
        d["uf"]     = r.get("UF","")
        d["emp"]    = r.get("NMEMP","")
        d["nm"]     = r.get("NMFILIAL","")
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: d["imp"] += imp
    save_csv("resumo", "por_filial.csv", sorted([
        {"cdfilial": k, "nome": d["nm"], "negocio": d["neg"], "uf": d["uf"],
         "empresa": d["emp"], "spend": r2(d["spend"]), "pct": pct(d["spend"], tg),
         "imp_cot": r2(d["imp"])}
        for k, d in by_fil.items()
    ], key=lambda x: -x["spend"])[:8])

    # CAT2 × UF (heatmap)
    cat_uf: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        cat_uf[(r.get("CAT2",""), r.get("UF",""))] += flt(r["TOTAL"])
    save_csv("resumo", "cat2_por_uf.csv", [
        {"cat2": k[0], "uf": k[1], "spend": r2(v)}
        for k, v in cat_uf.items() if k[0].strip() and k[1].strip()
    ])


# ─── ABA: OPORTUNIDADES ──────────────────────────────────────────────────────

def aba_oportunidades(nfe, num_cot, lk):
    print("  oportunidades/")
    tg = lk["total_geral"]

    # Contagens para KPIs
    ids_aaa_sem_cot = set()
    ids_com_imp     = set()
    n_acima_min     = 0

    id_num: dict[str, int] = defaultdict(int)
    for r in num_cot:
        id_num[r.get("ID","")] = int(flt(r.get("QTD_COT","0")))

    for r in nfe:
        id_  = r.get("ID","")
        curv = r.get("CURVA_ID","")
        sem_cot = r.get("PRE_MIN_COT","").strip() in ("","0")
        imp  = flt(r.get("IMP_COT",""))
        if imp > 0:
            ids_com_imp.add(id_)
            n_acima_min += 1
        if sem_cot and curv in ("AAA","AA","A"):
            ids_aaa_sem_cot.add(id_)

    mono_ids = {id_ for id_, n in id_num.items() if n == 1}
    ids_aaa_mono = {r.get("ID","") for r in nfe
                    if r.get("CURVA_ID","") in ("AAA","AA","A") and r.get("ID","") in mono_ids}

    save_json("oportunidades", "kpis.json", {
        "imp_cot_total": r2(sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT","")) > 0)),
        "ids_aaa_sem_cotacao": len(ids_aaa_sem_cot),
        "ids_com_impacto_positivo": len(ids_com_imp),
        "pct_linhas_acima_minimo": pct(n_acima_min, len(nfe)),
        "ids_aaa_mono_cotacao": len(ids_aaa_mono),
    })

    # Tabela principal com tipo e prioridade
    id_data: dict[str, dict] = defaultdict(lambda: {
        "imp_cot": 0.0, "spend": 0.0, "qtde": 0.0,
        "produto": "", "cat2": "", "uf": "",
        "forn_atual": "", "forn_min": "", "preco_min": 0.0,
        "curva_id": "", "curva_forn": ""
    })
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp <= 0 and r.get("PRE_MIN_COT","").strip() in ("","0"):
            # só incluir se curva alta sem cotação
            if r.get("CURVA_ID","") not in ("AAA","AA","A"):
                continue
        id_ = r.get("ID","")
        d   = id_data[id_]
        d["spend"]    += flt(r["TOTAL"])
        d["qtde"]     += flt(r.get("QTDE_EST",""))
        if imp > 0: d["imp_cot"] += imp
        d["produto"]   = r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]      = r.get("CAT2","")
        d["uf"]        = r.get("UF","")
        d["forn_atual"]= r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        d["forn_min"]  = r.get("FORN_MIN_COT","")
        d["preco_min"] = flt(r.get("PRE_MIN_COT",""))
        d["curva_id"]  = r.get("CURVA_ID","")
        d["curva_forn"]= r.get("CURVA_FORN","")

    def classify(id_, d):
        if d["preco_min"] == 0 and d["curva_id"] in ("AAA","AA","A"):
            return "Sem cotação AAA/A", 1
        if id_ in ids_aaa_mono:
            return "Monopólio de cotação", 2
        if d["imp_cot"] > 0:
            return "Acima do menor preço", 3
        return "Outros", 4

    rows = []
    for id_, d in id_data.items():
        tipo, prio = classify(id_, d)
        rows.append({
            "tipo": tipo, "prioridade": prio,
            "id": id_, "produto": d["produto"], "cat2": d["cat2"], "uf": d["uf"],
            "fornecedor_atual": d["forn_atual"], "fornecedor_mais_barato": d["forn_min"],
            "preco_minimo_cotado": r2(d["preco_min"]),
            "imp_cot": r2(d["imp_cot"]), "spend": r2(d["spend"]),
            "curva_id": d["curva_id"], "curva_forn": d["curva_forn"],
            "status": "Acima do menor" if d["imp_cot"] > 0 else
                      "Sem cotação" if d["preco_min"] == 0 else "OK"
        })
    rows.sort(key=lambda x: (x["prioridade"], -x["imp_cot"]))
    save_csv("oportunidades", "tabela_principal.csv", rows[:300])

    # Por CAT2
    cat_imp: dict[str, dict] = defaultdict(lambda: {"imp": 0.0, "ids": 0})
    for r in rows:
        if r["imp_cot"] > 0:
            cat_imp[r["cat2"]]["imp"] += r["imp_cot"]
            cat_imp[r["cat2"]]["ids"] += 1
    save_csv("oportunidades", "por_cat2.csv", sorted([
        {"cat2": k, "imp_cot": r2(d["imp"]), "ids_afetados": d["ids"]}
        for k, d in cat_imp.items() if k.strip()
    ], key=lambda x: -x["imp_cot"]))

    # Por UF
    uf_imp: dict[str, float] = defaultdict(float)
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: uf_imp[r.get("UF","")] += imp
    save_csv("oportunidades", "por_uf.csv", sorted([
        {"uf": k, "imp_cot": r2(v)} for k, v in uf_imp.items() if k.strip()
    ], key=lambda x: -x["imp_cot"]))

    # Matriz prioridade (Impacto × Esforço 3×3)
    # Impacto: alto (AAA/AA/A), médio (B/BB), baixo (C/CC/CCC)
    # Esforço: baixo (já tem cot. alternativa), médio (1 cotação), alto (sem cotação)
    matrix = {
        "alto_baixo": {"label": "Alto impacto / Fácil", "count": 0, "valor": 0.0},
        "alto_medio": {"label": "Alto impacto / Médio", "count": 0, "valor": 0.0},
        "alto_alto":  {"label": "Alto impacto / Difícil", "count": 0, "valor": 0.0},
        "medio_baixo": {"label": "Médio / Fácil", "count": 0, "valor": 0.0},
        "medio_medio": {"label": "Médio / Médio", "count": 0, "valor": 0.0},
        "medio_alto":  {"label": "Médio / Difícil", "count": 0, "valor": 0.0},
        "baixo_baixo": {"label": "Baixo / Fácil", "count": 0, "valor": 0.0},
        "baixo_medio": {"label": "Baixo / Médio", "count": 0, "valor": 0.0},
        "baixo_alto":  {"label": "Baixo / Difícil", "count": 0, "valor": 0.0},
    }
    for r in rows:
        curv = r["curva_id"]
        imp  = r["imp_cot"]
        if curv in ("AAA","AA","A"): imp_level = "alto"
        elif curv in ("B","BB"):     imp_level = "medio"
        else:                         imp_level = "baixo"
        n_cot = id_num.get(r["id"], 0)
        if n_cot >= 2:   esf = "baixo"
        elif n_cot == 1: esf = "medio"
        else:            esf = "alto"
        key = f"{imp_level}_{esf}"
        if key in matrix:
            matrix[key]["count"] += 1
            matrix[key]["valor"] += imp
    save_json("oportunidades", "matriz_prioridade.json",
              [{**v, "key": k, "valor": r2(v["valor"])} for k, v in matrix.items()])


# ─── ABA: CATEGORIAS ─────────────────────────────────────────────────────────

def aba_categorias(nfe, lk):
    print("  categorias/")
    tg = lk["total_geral"]

    # Hierarquia completa CAT1→CAT5
    cat_data: dict[tuple, dict] = defaultdict(lambda: {
        "spend": 0.0, "imp": 0.0, "inf_s": 0.0, "inf_n": 0,
        "ids": set(), "forn": set()
    })
    for r in nfe:
        key = (r.get("CAT1",""), r.get("CAT2",""), r.get("CAT3",""), r.get("CAT4",""), r.get("CAT5",""))
        d = cat_data[key]
        d["spend"] += flt(r["TOTAL"])
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: d["imp"] += imp
        inf = flt(r.get("INF_PROD_PMP",""))
        if inf != 0: d["inf_s"] += inf; d["inf_n"] += 1
        d["ids"].add(r.get("ID",""))
        d["forn"].add(r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED",""))
    save_csv("categorias", "hierarquia.csv", sorted([
        {"cat1": k[0], "cat2": k[1], "cat3": k[2], "cat4": k[3], "cat5": k[4],
         "spend": r2(d["spend"]), "pct": pct(d["spend"], tg),
         "imp_cot": r2(d["imp"]),
         "ids_unicos": len(d["ids"]), "fornecedores": len(d["forn"]),
         "inflacao_media_pct": round(d["inf_s"]/d["inf_n"],2) if d["inf_n"] else 0.0}
        for k, d in cat_data.items() if k[0].strip()
    ], key=lambda x: -x["spend"]))

    # CAT2 por mês (série temporal)
    top_cats = {r["cat2"] for r in sorted(
        [{"cat2": k[1], "spend": v["spend"]} for k, v in cat_data.items() if k[1].strip()],
        key=lambda x: -x["spend"]
    )[:6]}
    cat2_mes: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        cat2 = r.get("CAT2","")
        if cat2 in top_cats:
            cat2_mes[(cat2, r.get("MESANO",""))] += flt(r["TOTAL"])
    save_csv("categorias", "cat2_por_mes.csv", sorted([
        {"cat2": k[0], "mesano": k[1], "spend": r2(v)}
        for k, v in cat2_mes.items() if k[1].strip()
    ], key=lambda x: (x["cat2"], x["mesano"])))

    # CAT2 × UF
    cat2_uf: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        cat2_uf[(r.get("CAT2",""), r.get("UF",""))] += flt(r["TOTAL"])
    save_csv("categorias", "cat2_por_uf.csv", [
        {"cat2": k[0], "uf": k[1], "spend": r2(v)}
        for k, v in cat2_uf.items() if k[0].strip() and k[1].strip()
    ])


# ─── ABA: FILIAIS ─────────────────────────────────────────────────────────────

def aba_filiais(nfe, lk):
    print("  filiais/")
    tg = lk["total_geral"]

    fil: dict[str, dict] = defaultdict(lambda: {
        "spend": 0.0, "imp": 0.0, "com_cot": 0, "total": 0,
        "neg": "", "uf": "", "emp": "", "nm": ""
    })
    for r in nfe:
        cd = str(r.get("CDFILIAL","")).strip()
        if not cd: continue
        d = fil[cd]
        d["spend"] += flt(r["TOTAL"])
        d["total"] += 1
        d["neg"]    = r.get("FI.NEGOCIO","")
        d["uf"]     = r.get("UF","")
        d["emp"]    = r.get("NMEMP","")
        d["nm"]     = r.get("NMFILIAL","")
        if r.get("PRE_MIN_COT","").strip() not in ("","0"): d["com_cot"] += 1
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: d["imp"] += imp

    n_fil = len(fil)
    maior = max(fil.items(), key=lambda x: x[1]["spend"]) if fil else ("", {"nm":"","spend":0})

    save_json("filiais", "kpis.json", {
        "total_comprado": r2(tg),
        "filiais_ativas": n_fil,
        "compra_media_por_filial": r2(tg / n_fil) if n_fil else 0,
        "maior_filial": maior[1]["nm"] or maior[0],
        "maior_filial_spend": r2(maior[1]["spend"]),
    })

    # Ranking
    save_csv("filiais", "ranking.csv", sorted([
        {"cdfilial": k, "nome": d["nm"], "negocio": d["neg"], "uf": d["uf"],
         "empresa": d["emp"], "spend": r2(d["spend"]), "pct": pct(d["spend"], tg),
         "pct_com_cotacao": pct(d["com_cot"], d["total"]),
         "imp_cot": r2(d["imp"])}
        for k, d in fil.items()
    ], key=lambda x: -x["spend"]))

    # Filial × Negócio (heatmap)
    fil_neg: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        fil_neg[(str(r.get("CDFILIAL","")), r.get("FI.NEGOCIO",""))] += flt(r["TOTAL"])
    save_csv("filiais", "filial_negocio.csv", [
        {"cdfilial": k[0], "negocio": k[1], "spend": r2(v)}
        for k, v in fil_neg.items() if k[0].strip() and k[1].strip()
    ])

    # Top 3 filiais por mês
    top3 = [x[0] for x in sorted(fil.items(), key=lambda x: -x[1]["spend"])[:3]]
    fil_mes: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        cd = str(r.get("CDFILIAL","")).strip()
        if cd in top3:
            fil_mes[(cd, r.get("MESANO",""))] += flt(r["TOTAL"])
    save_csv("filiais", "top3_por_mes.csv", sorted([
        {"cdfilial": k[0], "mesano": k[1], "spend": r2(v), "nome": fil[k[0]]["nm"]}
        for k, v in fil_mes.items() if k[1].strip()
    ], key=lambda x: (x["cdfilial"], x["mesano"])))

    # Filial × Categoria
    fil_cat: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        cd = str(r.get("CDFILIAL","")).strip()
        if not cd: continue
        fil_cat[(cd, r.get("CAT2",""))] += flt(r["TOTAL"])
    save_csv("filiais", "por_categoria.csv", sorted([
        {"cdfilial": k[0], "cat2": k[1], "spend": r2(v)}
        for k, v in fil_cat.items() if k[0].strip() and k[1].strip()
    ], key=lambda x: (x["cdfilial"], -x["spend"])))


# ─── ABA: FORNECEDOR 360 ──────────────────────────────────────────────────────

def aba_forn360(nfe, cp, ad, curva_forn, lk):
    print("  forn360/")

    fv  = lk["forn_spend"]
    fcp = lk["forn_cp"]
    fad = lk["forn_ad"]
    fc  = lk["forn_curva"]
    tg  = lk["total_geral"]

    # Curva ABC + spend summary
    curva_totals: dict[str, dict] = defaultdict(lambda: {"spend": 0.0, "forn": 0})
    for cd, d in fv.items():
        curva = d["curva"] or fc.get(cd,"")
        curva_totals[curva]["spend"] += d["spend"]
        curva_totals[curva]["forn"]  += 1

    forn_com_cp = sum(1 for cd in fv if fcp.get(cd,{}).get("aberto",0) > 0)
    forn_com_ad = sum(1 for cd in fv if fad.get(cd,{}).get("pendente",0) > 0)
    spend_aaa = sum(d["spend"] for cd,d in fv.items() if (d["curva"] or fc.get(cd,"")) in ("AAA","AA","A"))

    save_json("forn360", "kpis.json", {
        "fornecedores_ativos": len(fv),
        "spend_curva_aaa_aa_a": r2(spend_aaa),
        "pct_spend_top": pct(spend_aaa, tg),
        "forn_com_cp_aberto": forn_com_cp,
        "forn_com_ad_pendente": forn_com_ad,
    })

    # Tabela principal (uma linha por fornecedor)
    rows = []
    for cd, d in sorted(fv.items(), key=lambda x: -x[1]["spend"]):
        curva = d["curva"] or fc.get(cd,"")
        rows.append({
            "cdforneced": cd,
            "fornecedor": d["nm"],
            "curva": curva,
            "empresas": "|".join(sorted(d["empresas"])),
            "ufs": "|".join(sorted(d["ufs"])),
            "categorias_top": "|".join(sorted(d["cats"])[:3]),
            "spend_total": r2(d["spend"]),
            "pct": pct(d["spend"], tg),
            "imp_cot": r2(d["imp_cot"]),
            "cp_aberto": r2(fcp.get(cd,{}).get("aberto",0)),
            "cp_vencido": r2(fcp.get(cd,{}).get("vencido",0)),
            "ad_pendente": r2(fad.get(cd,{}).get("pendente",0)),
        })
    save_csv("forn360", "tabela_principal.csv", rows[:500])

    # Por categoria (top fornecedores por CAT2)
    forn_cat: dict[tuple, float] = defaultdict(float)
    for r in nfe:
        cd = r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","")
        forn_cat[(cd, r.get("CAT2",""))] += flt(r["TOTAL"])
    save_csv("forn360", "por_categoria.csv", sorted([
        {"cdforneced": k[0], "cat2": k[1], "spend": r2(v),
         "fornecedor": fv.get(k[0],{}).get("nm","")}
        for k, v in forn_cat.items() if k[0].strip() and k[1].strip()
    ], key=lambda x: (x["cat2"], -x["spend"])))


# ─── ABA: PRODUTOS ────────────────────────────────────────────────────────────

def aba_produtos(nfe, pmp12, num_cot, lk):
    print("  produtos/")
    ps = lk["pmp_series"]

    # KPIs de curva ID
    curva_id_count: dict[str, int] = defaultdict(int)
    ids_com_inf = 0
    for id_, d in ps.items():
        curva_id_count[d["curva"]] += 1
        pmps = [p for p in d["pmps"] if p > 0]
        if len(pmps) >= 2:
            var = (pmps[0] - pmps[-1]) / pmps[-1] * 100 if pmps[-1] else 0
            if abs(var) > 10: ids_com_inf += 1

    ids_sem_cot = len({r.get("ID","") for r in nfe if r.get("PRE_MIN_COT","").strip() in ("","0")})
    pmp_medio   = sum(d["pmps"][0] for d in ps.values() if d["pmps"][0] > 0) / max(1, sum(1 for d in ps.values() if d["pmps"][0] > 0))

    save_json("produtos", "kpis.json", {
        "total_ids": len(ps),
        "ids_aaa_aa": curva_id_count.get("AAA",0) + curva_id_count.get("AA",0),
        "ids_variacao_pmp_gt10pct": ids_com_inf,
        "ids_sem_cotacao": ids_sem_cot,
        "pmp_medio_cesta": r2(pmp_medio),
    })

    # Tabela principal com série PMP inline
    prod_data: dict[str, dict] = defaultdict(lambda: {
        "spend": 0.0, "imp": 0.0, "nm": "", "cat2": "", "curva_id": "", "curva_prod": ""
    })
    for r in nfe:
        cd = r.get("CDPRODUTO_OFICIAL","")
        if not cd: continue
        d = prod_data[cd]
        d["spend"]    += flt(r["TOTAL"])
        d["nm"]        = r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]      = r.get("CAT2","")
        d["curva_id"]  = r.get("CURVA_ID","")
        d["curva_prod"]= r.get("CURVA_PROD","")
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: d["imp"] += imp

    rows = []
    for cd, d in sorted(prod_data.items(), key=lambda x: -x[1]["spend"])[:200]:
        pmp_d = ps.get(cd)
        pmp0  = pmp_d["pmps"][0] if pmp_d and pmp_d["pmps"][0] else 0
        pmp12_v = pmp_d["pmps"][12] if pmp_d and pmp_d["pmps"][12] else 0
        var = round((pmp0 - pmp12_v) / pmp12_v * 100, 2) if pmp12_v else 0.0
        rows.append({
            "cdproduto": cd, "produto": d["nm"], "cat2": d["cat2"],
            "curva_id": d["curva_id"], "curva_prod": d["curva_prod"],
            "spend": r2(d["spend"]), "imp_cot": r2(d["imp"]),
            "pmp_atual": r2(pmp0), "pmp_12m_anterior": r2(pmp12_v), "var_pmp_pct": var,
            "pmp_serie": json.dumps([r2(p) for p in (pmp_d["pmps"] if pmp_d else [])]),
        })
    save_csv("produtos", "tabela_principal.csv", rows)

    # PMP por CAT2
    cat_pmp: dict[str, dict] = defaultdict(lambda: {"pmp_s": 0.0, "pmp_n": 0, "spend": 0.0})
    for r in nfe:
        cat = r.get("CAT2","")
        pmp = flt(r.get("PMP_PROD",""))
        if pmp > 0 and cat.strip():
            cat_pmp[cat]["pmp_s"] += pmp
            cat_pmp[cat]["pmp_n"] += 1
        cat_pmp[cat]["spend"] += flt(r["TOTAL"])
    save_csv("produtos", "pmp_por_cat.csv", sorted([
        {"cat2": k, "pmp_medio": round(d["pmp_s"]/d["pmp_n"],2) if d["pmp_n"] else 0, "spend": r2(d["spend"])}
        for k, d in cat_pmp.items() if k.strip()
    ], key=lambda x: -x["spend"]))

    # Top inflação / deflação (da série PMP 12m)
    inf_rows = []
    for cd, d in ps.items():
        pmps = [p for p in d["pmps"] if p > 0]
        if len(pmps) < 2: continue
        var = round((pmps[0] - pmps[-1]) / pmps[-1] * 100, 2)
        spend = prod_data.get(cd,{}).get("spend",0)
        if spend < 50_000: continue
        inf_rows.append({"cdproduto": cd, "produto": d["nome"], "cat2": d["cat2"],
                          "curva_id": d["curva"], "var_pmp_pct": var, "spend": r2(spend)})
    save_csv("produtos", "top_inflacao.csv",  sorted([r for r in inf_rows if r["var_pmp_pct"] > 0], key=lambda x: -x["var_pmp_pct"])[:25])
    save_csv("produtos", "top_deflacao.csv",  sorted([r for r in inf_rows if r["var_pmp_pct"] < 0], key=lambda x: x["var_pmp_pct"])[:25])


# ─── ABA: COTAÇÕES ────────────────────────────────────────────────────────────

def aba_cotacoes(nfe, num_cot, cot, cot_min, lk):
    print("  cotacoes/")

    # KPIs
    total_ids_num = len({r.get("ID","") for r in num_cot})
    total_ids_nfe = len({r.get("ID","") for r in nfe})
    pct_cob = pct(total_ids_num, total_ids_nfe)
    qtds = [flt(r.get("QTD_COT","")) for r in num_cot]
    media_cot = round(sum(qtds)/len(qtds),2) if qtds else 0
    zero_cot  = sum(1 for q in qtds if q == 0)
    mono_cot  = sum(1 for q in qtds if q == 1)
    le3_cot   = sum(1 for q in qtds if q <= 3)
    imp_pot   = sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT","")) > 0)
    n_no_min  = sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("","0"))
    n_no_min_comprou = sum(1 for r in nfe if flt(r.get("IMP_COT","")) > 0)
    pct_menor = 100 - pct(n_no_min_comprou, n_no_min) if n_no_min else 0

    save_json("cotacoes", "kpis.json", {
        "produtos_cotados": total_ids_num,
        "pct_cobertura": pct_cob,
        "media_cotacoes_produto": media_cot,
        "com_zero_cotacao": zero_cot,
        "com_uma_cotacao": mono_cot,
        "com_le3_cotacoes": le3_cot,
        "potencial_imp_cot": r2(imp_pot),
        "pct_comprado_no_menor": r2(pct_menor),
    })

    # Cobertura por mês (stacked: 0/1/2/3/4/5+)
    mes_buckets: dict[str, dict] = defaultdict(lambda: {0:0, 1:0, 2:0, 3:0, 4:0, 5:0})
    for r in num_cot:
        mes = r.get("MESANO","")
        if not mes.strip(): continue
        q = int(min(flt(r.get("QTD_COT","0")), 5))
        mes_buckets[mes][q] += 1
    save_csv("cotacoes", "cobertura_por_mes.csv", sorted([
        {"mesano": k, "zero": d[0], "uma": d[1], "duas_tres": d[2]+d[3], "quatro_mais": d[4]+d[5]}
        for k, d in mes_buckets.items()
    ], key=lambda x: x["mesano"]))

    # Cobertura por curva ABC
    curva_buckets: dict[str, dict] = defaultdict(lambda: {"total":0, "zero":0, "uma":0, "duas_tres":0, "quatro_mais":0})
    for r in num_cot:
        curv = r.get("CURVA_ID","")
        q    = flt(r.get("QTD_COT","0"))
        curva_buckets[curv]["total"] += 1
        if q == 0:      curva_buckets[curv]["zero"] += 1
        elif q == 1:    curva_buckets[curv]["uma"]  += 1
        elif q <= 3:    curva_buckets[curv]["duas_tres"] += 1
        else:           curva_buckets[curv]["quatro_mais"] += 1
    order = ["AAA","AA","A","B","BB","C","CC","CCC"]
    save_csv("cotacoes", "cobertura_por_curva.csv", [
        {"curva_id": c, **curva_buckets[c], "pct_risco": pct(
            curva_buckets[c]["zero"]+curva_buckets[c]["uma"], curva_buckets[c]["total"])}
        for c in order if curva_buckets[c]["total"] > 0
    ])

    # Cobertura por categoria × mês (top 5 cats)
    cat_mes: dict[tuple, dict] = defaultdict(lambda: {"total":0,"com":0})
    top5_cats = set()
    cat_count: dict[str, int] = defaultdict(int)
    for r in num_cot:
        cat_count[r.get("CAT2","")] += 1
    top5_cats = {k for k,v in sorted(cat_count.items(), key=lambda x:-x[1])[:5] if k.strip()}
    for r in num_cot:
        cat2 = r.get("CAT2","")
        mes  = r.get("MESANO","")
        if cat2 not in top5_cats or not mes.strip(): continue
        cat_mes[(cat2, mes)]["total"] += 1
        if flt(r.get("QTD_COT","")) > 0: cat_mes[(cat2,mes)]["com"] += 1
    save_csv("cotacoes", "cobertura_por_cat_mes.csv", sorted([
        {"cat2": k[0], "mesano": k[1],
         "total_ids": d["total"], "com_cotacao": d["com"],
         "pct_cobertura": pct(d["com"], d["total"])}
        for k, d in cat_mes.items()
    ], key=lambda x: (x["cat2"], x["mesano"])))

    # Cobertura por UF
    uf_cot: dict[str, dict] = defaultdict(lambda: {"total":0,"com":0,"spend":0.0,"imp":0.0})
    for r in nfe:
        uf = r.get("UF","")
        uf_cot[uf]["total"] += 1
        uf_cot[uf]["spend"] += flt(r["TOTAL"])
        if r.get("PRE_MIN_COT","").strip() not in ("","0"): uf_cot[uf]["com"] += 1
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: uf_cot[uf]["imp"] += imp
    save_csv("cotacoes", "cobertura_por_uf.csv", sorted([
        {"uf": k, "total_linhas": d["total"], "com_cotacao": d["com"],
         "pct_cobertura": pct(d["com"],d["total"]), "spend": r2(d["spend"]),
         "imp_cot": r2(d["imp"]), "imp_sobre_spend_pct": pct(d["imp"],d["spend"])}
        for k, d in uf_cot.items() if k.strip()
    ], key=lambda x: -x["spend"]))

    # MIN cotação por fornecedor
    forn_min: dict[str, dict] = defaultdict(lambda: {"n":0,"ids":set(),"v_total":0.0,"nm":""})
    for r in cot_min:
        nm = r.get("FORNE_FANTASIA","")
        cd = nm.split(" - ")[0].strip() if " - " in nm else nm
        forn_min[cd]["n"]     += 1
        forn_min[cd]["ids"].add(r.get("ID",""))
        forn_min[cd]["v_total"] += flt(r.get("PRECOUNIT_COT",""))
        forn_min[cd]["nm"]    = nm
    save_csv("cotacoes", "min_cotacao_forn.csv", sorted([
        {"fornecedor": d["nm"], "vezes_menor_preco": d["n"], "ids_unicos": len(d["ids"])}
        for cd, d in forn_min.items() if d["n"] >= 2
    ], key=lambda x: -x["vezes_menor_preco"])[:100])

    # Relatório de cotações (COT agregado)
    cot_prod: dict[tuple, dict] = defaultdict(lambda: {"min":float("inf"),"med_s":0.0,"med_n":0,"max":0.0,"forn_nm":""})
    for r in cot:
        key = (r.get("ID",""), r.get("UF",""), r.get("MESANO",""))
        v = flt(r.get("PRECOUNIT_EST",""))
        if v <= 0: continue
        d = cot_prod[key]
        d["min"]    = min(d["min"], v)
        d["med_s"] += v; d["med_n"] += 1
        d["max"]    = max(d["max"], v)
    save_csv("cotacoes", "relatorio.csv", sorted([
        {"id": k[0], "uf": k[1], "mesano": k[2],
         "preco_min": r2(d["min"]) if d["min"] != float("inf") else 0,
         "preco_med": r2(d["med_s"]/d["med_n"]) if d["med_n"] else 0,
         "preco_max": r2(d["max"]), "n_cotacoes": d["med_n"]}
        for k, d in cot_prod.items() if k[0].strip()
    ], key=lambda x: x["mesano"])[:2000])


# ─── ABA: IMPACTO ─────────────────────────────────────────────────────────────

def aba_impacto(nfe, cot_min, lk):
    print("  impacto/")

    # KPIs
    imp_total   = sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT","")) > 0)
    n_ids_imp   = len({r.get("ID","") for r in nfe if flt(r.get("IMP_COT","")) > 0})
    n_acima     = sum(1 for r in nfe if flt(r.get("IMP_COT","")) > 0)
    total_com   = sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("","0"))

    by_uf_imp = defaultdict(float)
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: by_uf_imp[r.get("UF","")] += imp
    uf_lider = max(by_uf_imp.items(), key=lambda x: x[1], default=("",0))

    top_id = None
    top_id_v = 0
    id_imp_acc: dict[str,float] = defaultdict(float)
    id_nm: dict[str,str] = {}
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            id_imp_acc[r.get("ID","")] += imp
            id_nm[r.get("ID","")] = r.get("NMPRODUTO_OFICIAL","")
    if id_imp_acc:
        top_id, top_id_v = max(id_imp_acc.items(), key=lambda x: x[1])

    save_json("impacto", "kpis.json", {
        "imp_cot_total": r2(imp_total),
        "ids_com_impacto": n_ids_imp,
        "pct_linhas_acima_minimo": pct(n_acima, total_com) if total_com else 0,
        "uf_lider": uf_lider[0],
        "uf_lider_valor": r2(uf_lider[1]),
        "top_produto_nome": id_nm.get(top_id,"") if top_id else "",
        "top_produto_imp": r2(top_id_v),
    })

    # Por mês
    mes_imp: dict[str, float] = defaultdict(float)
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp > 0: mes_imp[r.get("MESANO","")] += imp
    save_csv("impacto", "por_mes.csv", sorted([
        {"mesano": k, "imp_cot": r2(v)} for k, v in mes_imp.items() if k.strip()
    ], key=lambda x: x["mesano"]))

    # Por UF
    save_csv("impacto", "por_uf.csv", sorted([
        {"uf": k, "imp_cot": r2(v)} for k, v in by_uf_imp.items() if k.strip()
    ], key=lambda x: -x["imp_cot"]))

    # Top IDs com status
    id_data: dict[str,dict] = defaultdict(lambda: {
        "imp_cot":0.0,"spend":0.0,"produto":"","cat2":"","uf":"",
        "forn_atual":"","forn_min":"","pre_min":0.0,"curva_id":"","curva_forn":""
    })
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp <= 0: continue
        k = r.get("ID","")
        d = id_data[k]
        d["imp_cot"]  += imp
        d["spend"]    += flt(r["TOTAL"])
        d["produto"]   = r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]      = r.get("CAT2","")
        d["uf"]        = r.get("UF","")
        d["forn_atual"]= r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        d["forn_min"]  = r.get("FORN_MIN_COT","")
        d["pre_min"]   = flt(r.get("PRE_MIN_COT",""))
        d["curva_id"]  = r.get("CURVA_ID","")
        d["curva_forn"]= r.get("CURVA_FORN","")
    save_csv("impacto", "top_ids.csv", sorted([
        {"id": k, "produto": d["produto"], "cat2": d["cat2"], "uf": d["uf"],
         "fornecedor_atual": d["forn_atual"], "fornecedor_mais_barato": d["forn_min"],
         "preco_minimo": r2(d["pre_min"]), "imp_cot": r2(d["imp_cot"]),
         "spend": r2(d["spend"]), "curva_id": d["curva_id"],
         "status": "Acima do menor"}
        for k, d in id_data.items()
    ], key=lambda x: -x["imp_cot"])[:100])

    # Fornecedores mais baratos não escolhidos
    forn_min_missed: dict[str,dict] = defaultdict(lambda:{"n":0,"ids":set(),"v":0.0,"nm":""})
    for r in nfe:
        if flt(r.get("IMP_COT","")) > 0 and r.get("FORN_MIN_COT","").strip():
            forn = r.get("FORN_MIN_COT","")
            forn_min_missed[forn]["n"]   += 1
            forn_min_missed[forn]["ids"].add(r.get("ID",""))
            forn_min_missed[forn]["v"]  += flt(r.get("IMP_COT",""))
            forn_min_missed[forn]["nm"]  = forn
    save_csv("impacto", "forn_mais_barato_nao_escolhido.csv", sorted([
        {"fornecedor": d["nm"], "vezes_mais_barato": d["n"],
         "ids_unicos": len(d["ids"]), "oportunidade_total": r2(d["v"])}
        for cd, d in forn_min_missed.items() if d["n"] >= 3
    ], key=lambda x: -x["oportunidade_total"])[:50])


# ─── ABA: INFLAÇÃO ────────────────────────────────────────────────────────────

def aba_inflacao(inflacao_raw, pmp12, pmp_prod12, lk):
    print("  inflacao/")
    if not inflacao_raw:
        print("    [AVISO] inflacao.csv não disponível")
        return

    # KPIs
    inf_vals = [flt(r.get("PERC_INF_ID_PMP","")) for r in inflacao_raw if flt(r.get("PERC_INF_ID_PMP","")) != 0]
    inf_media = round(sum(inf_vals)/len(inf_vals),2) if inf_vals else 0
    exp_mon   = sum(flt(r.get("SOMA_INF_ID_PMP","")) for r in inflacao_raw)
    ids_gt10  = sum(1 for v in inf_vals if v > 10)

    # Top cat inflada
    cat_inf: dict[str,float] = defaultdict(float)
    for r in inflacao_raw:
        cat_inf[r.get("CAT2","")] += flt(r.get("PERC_INF_ID_PMP",""))
    top_cat = max(cat_inf.items(), key=lambda x: x[1], default=("",0))

    save_json("inflacao", "kpis.json", {
        "inflacao_media_pct": inf_media,
        "exposicao_monetaria_12m": r2(exp_mon),
        "ids_com_inflacao_gt10pct": ids_gt10,
        "cat2_mais_inflada": top_cat[0],
    })

    # Por CAT × mês (%)
    cat_mes_pct: dict[tuple,dict] = defaultdict(lambda:{"pct_s":0.0,"pct_n":0,"rs":0.0})
    for r in inflacao_raw:
        key = (r.get("CAT2",""), r.get("MESANO",""))
        pct_v = flt(r.get("PERC_INF_ID_PMP",""))
        rs_v  = flt(r.get("SOMA_INF_ID_PMP",""))
        if pct_v != 0: cat_mes_pct[key]["pct_s"] += pct_v; cat_mes_pct[key]["pct_n"] += 1
        cat_mes_pct[key]["rs"] += rs_v
    save_csv("inflacao", "por_cat_mes_pct.csv", sorted([
        {"cat2": k[0], "mesano": k[1],
         "inflacao_media_pct": round(d["pct_s"]/d["pct_n"],2) if d["pct_n"] else 0.0,
         "exposicao_rs": r2(d["rs"])}
        for k, d in cat_mes_pct.items() if k[0].strip() and k[1].strip()
    ], key=lambda x: (x["cat2"], x["mesano"])))

    # Por mês R$ (soma exposição monetária)
    mes_rs: dict[str,float] = defaultdict(float)
    for r in inflacao_raw:
        mes_rs[r.get("MESANO","")] += flt(r.get("SOMA_INF_ID_PMP",""))
    save_csv("inflacao", "por_mes_rs.csv", sorted([
        {"mesano": k, "exposicao_rs": r2(v)} for k, v in mes_rs.items() if k.strip()
    ], key=lambda x: x["mesano"]))

    # Por UF
    uf_inf: dict[str,dict] = defaultdict(lambda:{"pct_s":0.0,"pct_n":0,"rs":0.0})
    for r in inflacao_raw:
        uf = r.get("UF","")
        p  = flt(r.get("PERC_INF_ID_PMP",""))
        if p != 0: uf_inf[uf]["pct_s"] += p; uf_inf[uf]["pct_n"] += 1
        uf_inf[uf]["rs"] += flt(r.get("SOMA_INF_ID_PMP",""))
    save_csv("inflacao", "por_uf.csv", sorted([
        {"uf": k, "inflacao_media_pct": round(d["pct_s"]/d["pct_n"],2) if d["pct_n"] else 0,
         "exposicao_rs": r2(d["rs"])}
        for k, d in uf_inf.items() if k.strip()
    ], key=lambda x: -abs(x["inflacao_media_pct"])))

    # Por categoria nacional
    cat_nac: dict[str,dict] = defaultdict(lambda:{"pct_s":0.0,"pct_n":0,"rs":0.0})
    for r in inflacao_raw:
        cat = r.get("CAT2","")
        p   = flt(r.get("PERC_INF_ID_PMP",""))
        if p != 0: cat_nac[cat]["pct_s"] += p; cat_nac[cat]["pct_n"] += 1
        cat_nac[cat]["rs"] += flt(r.get("SOMA_INF_ID_PMP",""))
    save_csv("inflacao", "por_categoria.csv", sorted([
        {"cat2": k, "inflacao_media_pct": round(d["pct_s"]/d["pct_n"],2) if d["pct_n"] else 0,
         "exposicao_rs": r2(d["rs"])}
        for k, d in cat_nac.items() if k.strip()
    ], key=lambda x: -abs(x["inflacao_media_pct"])))

    # Top produtos (da série PMP 12m)
    prod_var: list[dict] = []
    for r in pmp_prod12:
        pmp0 = flt(r.get("PMP_0",""))
        pmp12v = flt(r.get("PMP_12",""))
        if pmp0 <= 0 or pmp12v <= 0: continue
        var = round((pmp0 - pmp12v)/pmp12v*100, 2)
        prod_var.append({
            "produto": r.get("NMPRODUTO_OFICIAL",""), "cat2": r.get("CAT2",""),
            "curva": r.get("CURVA_PROD",""),
            "pmp_atual": r2(pmp0), "pmp_12m_anterior": r2(pmp12v), "var_pct": var
        })
    save_csv("inflacao", "top_produtos.csv",  sorted([x for x in prod_var if x["var_pct"] > 0], key=lambda x: -x["var_pct"])[:25])
    save_csv("inflacao", "top_deflacao.csv",  sorted([x for x in prod_var if x["var_pct"] < 0], key=lambda x: x["var_pct"])[:25])


# ─── ABA: FINANCEIRO ─────────────────────────────────────────────────────────

def aba_financeiro(cp, cp_semana, cp_saldo, lk):
    print("  financeiro/")
    fc = lk["forn_curva"]

    # KPIs
    cp_ab    = sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","") == "Em Aberto")
    cp_venc  = sum(flt(r.get("VRATUAPAG","")) for r in cp
                   if r.get("STATUSPAG","") == "Em Aberto" and r.get("FAIXA_DIAS","").strip().startswith("VE"))
    cp_7d    = sum(flt(r.get("VRATUAPAG","")) for r in cp
                   if r.get("STATUSPAG","") == "Em Aberto" and r.get("FAIXA_DIAS","").strip().rstrip("\n") in ("AV 0","AV 7"))
    cp_120   = sum(flt(r.get("VRATUAPAG","")) for r in cp
                   if r.get("STATUSPAG","") == "Em Aberto" and r.get("FAIXA_DIAS","").strip().rstrip("\n") in ("VE +120","VE 120"))
    n_ab     = sum(1 for r in cp if r.get("STATUSPAG","") == "Em Aberto")
    cp_titulos = n_ab

    save_json("financeiro", "kpis.json", {
        "cp_aberto_total": r2(cp_ab),
        "cp_titulos": cp_titulos,
        "cp_vencido": r2(cp_venc),
        "cp_a_vencer_7d": r2(cp_7d),
        "cp_critico_120d": r2(cp_120),
    })

    # Aging
    aging: dict[str,dict] = defaultdict(lambda:{"valor":0.0,"titulos":0})
    for r in cp:
        if r.get("STATUSPAG","") != "Em Aberto": continue
        faixa = r.get("FAIXA_DIAS","").strip().rstrip("\n")
        aging[faixa]["valor"]   += flt(r.get("VRATUAPAG",""))
        aging[faixa]["titulos"] += 1
    save_csv("financeiro", "aging.csv", sorted([
        {"faixa_dias": k, "valor": r2(d["valor"]), "titulos": d["titulos"]}
        for k, d in aging.items() if k
    ], key=lambda x: -x["valor"]))

    # Por fornecedor com curva
    fcp_agg: dict[str,dict] = defaultdict(lambda:{"aberto":0.0,"vencido":0.0,"a_vencer":0.0,"titulos":0,"nm":""})
    for r in cp:
        if r.get("STATUSPAG","") != "Em Aberto": continue
        cd    = r.get("CDFORNECED","")
        faixa = r.get("FAIXA_DIAS","").strip().rstrip("\n")
        v     = flt(r.get("VRATUAPAG",""))
        fcp_agg[cd]["aberto"]  += v
        fcp_agg[cd]["titulos"] += 1
        fcp_agg[cd]["nm"]       = r.get("NMFANTFORN","")
        if faixa.startswith("VE"):  fcp_agg[cd]["vencido"]   += v
        elif faixa.startswith("AV"): fcp_agg[cd]["a_vencer"] += v
    save_csv("financeiro", "por_fornecedor.csv", sorted([
        {"cdforneced": k, "fornecedor": d["nm"],
         "curva": fc.get(k,""),
         "cp_aberto": r2(d["aberto"]), "cp_vencido": r2(d["vencido"]),
         "cp_a_vencer": r2(d["a_vencer"]), "titulos": d["titulos"]}
        for k, d in fcp_agg.items()
    ], key=lambda x: -x["cp_aberto"])[:100])

    # Timeline semanal (CP_SEMANA)
    if cp_semana:
        save_csv("financeiro", "timeline_semanal.csv", sorted([
            {"fornecedor": r.get("T.FORNECEDOR",""),
             "semana": r.get("T.SEMANA_ANO",""), "ini": r.get("T.INI_SEMANA",""), "fim": r.get("T.FIM_SEMANA",""),
             "valor_pago": r2(flt(r.get("VALOR_PAGO_SEMANA",""))),
             "valor_vencimentos": r2(flt(r.get("VALOR_VENCIMENTOS_SEMANA",""))),
             "valor_vencido": r2(flt(r.get("VALOR_VENCIDO_SEMANA","")))}
            for r in cp_semana
        ], key=lambda x: (x["semana"],))[:500])

    # Saldo semanal 2026 (CP_SALDO_2026)
    if cp_saldo:
        save_csv("financeiro", "saldo_semanal_2026.csv", sorted([
            {"cdforneced": r.get("CDFORNECED",""),
             "fornecedor": r.get("NMFANTFORN",""),
             "semana": r.get("SEMANA_ANO",""),
             "ini": r.get("INI_SEMANA",""), "fim": r.get("FIM_SEMANA",""),
             "entra": r2(flt(r.get("ENTRA_DIVIDA_SEMANA",""))),
             "sai": r2(flt(r.get("SAI_DIVIDA_SEMANA",""))),
             "saldo": r2(flt(r.get("SALDO_DIVIDA_SEMANA","")))}
            for r in cp_saldo
        ], key=lambda x: (x["semana"],))[:500])


# ─── ABA: ADIANTAMENTOS ──────────────────────────────────────────────────────

def aba_adiantamentos(ad, nf_itens, lk):
    print("  adiantamentos/")

    # KPIs
    total_ad  = sum(flt(r.get("VALOR_FINAL","")) for r in ad)
    concil    = sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","") == "CONCILIADO")
    pendente  = sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","") == "ADIANTAMENTO ?")
    n_concil  = sum(1 for r in ad if r.get("STATUS_CONCILIACAO","") == "CONCILIADO")
    n_pend    = sum(1 for r in ad if r.get("STATUS_CONCILIACAO","") == "ADIANTAMENTO ?")

    save_json("adiantamentos", "kpis.json", {
        "ad_total_12m": r2(total_ad),
        "conciliado": r2(concil), "n_conciliado": n_concil,
        "pendente": r2(pendente), "n_pendente": n_pend,
        "pct_conciliado": pct(concil, total_ad),
    })

    # Funil de conciliação
    save_csv("adiantamentos", "funil.csv", [
        {"status": "Total lançado", "valor": r2(total_ad), "registros": len(ad)},
        {"status": "Conciliado", "valor": r2(concil), "registros": n_concil},
        {"status": "Pendente", "valor": r2(pendente), "registros": n_pend},
    ])

    # Por empresa
    emp_data: dict[str,dict] = defaultdict(lambda:{"concil":0.0,"pend":0.0})
    for r in ad:
        emp = r.get("NMEMP","")
        v   = flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","") == "CONCILIADO": emp_data[emp]["concil"] += v
        else: emp_data[emp]["pend"] += v
    save_csv("adiantamentos", "por_empresa.csv", [
        {"empresa": k, "conciliado": r2(d["concil"]), "pendente": r2(d["pend"])}
        for k, d in emp_data.items() if k.strip()
    ])

    # Por mês
    mes_data: dict[str,dict] = defaultdict(lambda:{"concil":0.0,"pend":0.0})
    for r in ad:
        mes = r.get("MES_ENTRADA","") or r.get("MES_PGTO","")
        v   = flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","") == "CONCILIADO": mes_data[mes]["concil"] += v
        else: mes_data[mes]["pend"] += v
    save_csv("adiantamentos", "por_mes.csv", sorted([
        {"mesano": k, "conciliado": r2(d["concil"]), "pendente": r2(d["pend"])}
        for k, d in mes_data.items() if k.strip()
    ], key=lambda x: x["mesano"]))

    # Por UF
    uf_ad: dict[str,float] = defaultdict(float)
    for r in ad:
        uf_ad[r.get("UF","")] += flt(r.get("VALOR_FINAL",""))
    save_csv("adiantamentos", "por_uf.csv", sorted([
        {"uf": k, "valor_total": r2(v)} for k, v in uf_ad.items() if k.strip()
    ], key=lambda x: -x["valor_total"]))

    # Por categoria
    cat_ad: dict[str,dict] = defaultdict(lambda:{"pend":0.0,"concil":0.0})
    for r in ad:
        cat = r.get("CAT2","") or r.get("CAT1","")
        v   = flt(r.get("VALOR_FINAL",""))
        if r.get("STATUS_CONCILIACAO","") == "CONCILIADO": cat_ad[cat]["concil"] += v
        else: cat_ad[cat]["pend"] += v
    save_csv("adiantamentos", "por_categoria.csv", sorted([
        {"categoria": k, "pendente": r2(d["pend"]), "conciliado": r2(d["concil"])}
        for k, d in cat_ad.items() if k.strip()
    ], key=lambda x: -(x["pendente"]+x["conciliado"])))

    # Por fornecedor
    forn_ad: dict[str,dict] = defaultdict(lambda:{"pend":0.0,"concil":0.0,"nm":"","regs":0})
    for r in ad:
        cd = r.get("CDFORNECED","")
        v  = flt(r.get("VALOR_FINAL",""))
        forn_ad[cd]["nm"]   = r.get("FANTASIA_OFICIAL","")
        forn_ad[cd]["regs"] += 1
        if r.get("STATUS_CONCILIACAO","") == "CONCILIADO": forn_ad[cd]["concil"] += v
        else: forn_ad[cd]["pend"] += v
    save_csv("adiantamentos", "por_fornecedor.csv", sorted([
        {"cdforneced": k, "fornecedor": d["nm"],
         "pendente": r2(d["pend"]), "conciliado": r2(d["concil"]), "registros": d["regs"]}
        for k, d in forn_ad.items()
    ], key=lambda x: -x["pendente"])[:100])


# ─── ABA: SERVIÇOS ────────────────────────────────────────────────────────────

def aba_servicos(nfe, lk):
    print("  servicos/")
    # Filtrar D5 (excluindo lançamentos financeiros)
    financeiros = {"MUTUO","DEVOLUCAO","EMPRESTIMO","ICMS","PARCELAMENTO"}
    def is_fin(r):
        nm = (r.get("NMPRODUTO_OFICIAL","") or "").upper()
        return any(f in nm for f in financeiros)

    d5 = [r for r in nfe if r.get("CAT2","").startswith("D5") and not is_fin(r)]
    if not d5:
        d5 = [r for r in nfe if r.get("CAT1","").startswith("D")]

    total_d5 = sum(flt(r["TOTAL"]) for r in d5)
    forn_d5  = len({r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","") for r in d5})
    ufs_d5   = len({r.get("UF","") for r in d5})

    save_json("servicos", "kpis.json", {
        "total_servicos": r2(total_d5),
        "fornecedores_servicos": forn_d5,
        "ufs_atendidas": ufs_d5,
    })

    # Por UF
    uf_sv: dict[str,float] = defaultdict(float)
    for r in d5: uf_sv[r.get("UF","")] += flt(r["TOTAL"])
    save_csv("servicos", "por_uf.csv", sorted([
        {"uf": k, "spend": r2(v), "pct": pct(v, total_d5)} for k, v in uf_sv.items() if k.strip()
    ], key=lambda x: -x["spend"]))

    # Por mês
    mes_sv: dict[str,float] = defaultdict(float)
    for r in d5: mes_sv[r.get("MESANO","")] += flt(r["TOTAL"])
    save_csv("servicos", "por_mes.csv", sorted([
        {"mesano": k, "spend": r2(v)} for k, v in mes_sv.items() if k.strip()
    ], key=lambda x: x["mesano"]))

    # Por categoria (CAT3 dentro de D5)
    cat_sv: dict[str,dict] = defaultdict(lambda:{"spend":0.0,"var_s":0.0,"var_n":0})
    cat_prev: dict[str,float] = defaultdict(float)
    for r in d5:
        cat = r.get("CAT3","") or r.get("CAT2","")
        cat_sv[cat]["spend"] += flt(r["TOTAL"])
    save_csv("servicos", "por_categoria.csv", sorted([
        {"categoria": k, "spend": r2(d["spend"]), "pct": pct(d["spend"], total_d5)}
        for k, d in cat_sv.items() if k.strip()
    ], key=lambda x: -x["spend"])[:20])

    # Top fornecedores de serviços
    forn_sv: dict[str,dict] = defaultdict(lambda:{"spend":0.0,"nm":"","cat":""})
    for r in d5:
        cd = r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","")
        forn_sv[cd]["spend"] += flt(r["TOTAL"])
        forn_sv[cd]["nm"]     = r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        forn_sv[cd]["cat"]    = r.get("CAT3","") or r.get("CAT2","")
    save_csv("servicos", "por_fornecedor.csv", sorted([
        {"cdforneced": k, "fornecedor": d["nm"], "categoria": d["cat"],
         "spend": r2(d["spend"]), "pct": pct(d["spend"], total_d5)}
        for k, d in forn_sv.items()
    ], key=lambda x: -x["spend"])[:50])


# ─── ABA: QUALIDADE ───────────────────────────────────────────────────────────

def aba_qualidade(nfe, lk):
    print("  qualidade/")
    manifest_path = RAW / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    # Status das fontes
    sources_status = []
    for entry in manifest.get("files", []) if "files" in manifest else [
        {"file": k+".csv", "rows": v.get("rows",0), "status": v.get("status","?")}
        for k,v in manifest.items() if isinstance(v,dict) and "status" in v
    ]:
        sources_status.append({
            "arquivo": entry.get("file",""),
            "linhas": entry.get("rows",0),
            "status": entry.get("status","ok"),
        })
    if not sources_status:
        for k, v in manifest.items():
            if isinstance(v, dict) and "status" in v:
                sources_status.append({"arquivo": k+".csv", "linhas": v.get("rows",0), "status": v.get("status","")})

    save_csv("qualidade", "status_fontes.csv", sources_status)

    # Fila de saneamento
    prods_sem_codigo  = sum(1 for r in nfe if not r.get("CDPRODUTO_OFICIAL","").strip())
    forn_sem_oficial  = sum(1 for r in nfe if not r.get("CDFORNECED_OFICIAL","").strip())
    linhas_sem_cot    = sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() in ("","0"))
    linhas_sem_cat    = sum(1 for r in nfe if not r.get("CAT1","").strip())

    save_csv("qualidade", "fila_saneamento.csv", [
        {"problema": "Linhas sem cotação (PRE_MIN_COT vazio)", "campo": "PRE_MIN_COT", "linhas": linhas_sem_cot,
         "pct": pct(linhas_sem_cot, len(nfe)), "impacto": "Alto - impede análise de oportunidades"},
        {"problema": "Produtos sem código oficial", "campo": "CDPRODUTO_OFICIAL", "linhas": prods_sem_codigo,
         "pct": pct(prods_sem_codigo, len(nfe)), "impacto": "Médio - dificulta padronização"},
        {"problema": "Fornecedores sem código oficial", "campo": "CDFORNECED_OFICIAL", "linhas": forn_sem_oficial,
         "pct": pct(forn_sem_oficial, len(nfe)), "impacto": "Médio - dificulta consolidação"},
        {"problema": "Linhas sem categoria", "campo": "CAT1", "linhas": linhas_sem_cat,
         "pct": pct(linhas_sem_cat, len(nfe)), "impacto": "Baixo"},
    ])

    save_json("qualidade", "kpis.json", {
        "linhas_total_nfe": len(nfe),
        "fontes_ok": sum(1 for s in sources_status if s.get("status") == "ok"),
        "fontes_total": len(sources_status),
        "linhas_sem_cotacao": linhas_sem_cot,
        "pct_sem_cotacao": pct(linhas_sem_cot, len(nfe)),
        "produtos_sem_codigo": prods_sem_codigo,
    })


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Carregando dados de {RAW}...")

    nfe         = load("nfe.csv")
    cp          = load("cp.csv")
    ad          = load("ad_v3.csv")
    curva_forn  = load("curva_forn.csv")
    num_cot     = load("num_cot.csv")
    cot         = load("cot.csv")
    cot_min     = load("cot_min_forn.csv")
    inflacao_r  = load("inflacao.csv")
    pmp12       = load("pmp_id_inf_12.csv")
    pmp_prod12  = load("pmp_prod_inf_12.csv")
    cp_semana   = load("cp_semana.csv")
    cp_saldo    = load("cp_saldo_2026.csv")
    nf_itens    = load("nf_com_itens.csv")

    print(f"  NFE:{len(nfe):,} CP:{len(cp):,} AD:{len(ad):,} COT:{len(cot):,} "
          f"INFLAÇÃO:{len(inflacao_r):,} PMP12:{len(pmp12):,}")
    print()

    lk = build_lookups(nfe, cp, ad, curva_forn, pmp12, cp_semana)

    print("Transformando por aba...")
    aba_resumo(nfe, cp, ad, lk)
    aba_oportunidades(nfe, num_cot, lk)
    aba_categorias(nfe, lk)
    aba_filiais(nfe, lk)
    aba_forn360(nfe, cp, ad, curva_forn, lk)
    aba_produtos(nfe, pmp12, num_cot, lk)
    aba_cotacoes(nfe, num_cot, cot, cot_min, lk)
    aba_impacto(nfe, cot_min, lk)
    aba_inflacao(inflacao_r, pmp12, pmp_prod12, lk)
    aba_financeiro(cp, cp_semana, cp_saldo, lk)
    aba_adiantamentos(ad, nf_itens, lk)
    aba_servicos(nfe, lk)
    aba_qualidade(nfe, lk)

    # Manifest final
    outputs = sorted(OUT.rglob("*.csv")) + sorted(OUT.rglob("kpis.json"))
    total_kb = sum(p.stat().st_size for p in outputs) / 1024
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(outputs),
        "total_kb": round(total_kb, 1),
        "abas": {},
    }
    for p in outputs:
        aba = p.parent.name
        manifest["abas"].setdefault(aba, []).append(p.name)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"Concluído: {len(outputs)} arquivos em data/processed/  ({total_kb:.0f} KB)")
    for aba in sorted(manifest["abas"]):
        files = manifest["abas"][aba]
        kb = sum((OUT/aba/f).stat().st_size for f in files if (OUT/aba/f).exists()) / 1024
        print(f"  {aba:<20} {len(files):>3} arquivos  {kb:>8.1f} KB")


if __name__ == "__main__":
    main()
