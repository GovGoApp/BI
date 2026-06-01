"""Transforma dados brutos de data/raw/ em métricas prontas em data/processed/.

Lê os 18 CSVs extraídos do Zoho, calcula agregações por aba e salva
arquivos menores e já prontos para o dashboard.

Uso:
    python pipeline/transform.py
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
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load(filename: str) -> list[dict[str, str]]:
    path = RAW / filename
    if not path.exists():
        print(f"  [AVISO] {filename} não encontrado em data/raw/")
        return []
    with path.open(encoding="utf-8-sig", errors="replace") as f:
        return list(csv.DictReader(f))


def flt(v: str | None) -> float:
    """Converte valor numérico do Zoho. Trata '', NULL, notação científica."""
    if not v or str(v).strip() == "":
        return 0.0
    try:
        return float(str(v).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def save_csv(filename: str, rows: list[dict], fieldnames: list[str] | None = None) -> Path:
    path = OUT / filename
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fields = fieldnames or list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


def save_json(filename: str, data: Any) -> Path:
    path = OUT / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def pct(part: float, total: float) -> float:
    return round(part / total * 100, 2) if total else 0.0


def fmt_r(v: float) -> float:
    return round(v, 2)


# ---------------------------------------------------------------------------
# 1. RESUMO
# ---------------------------------------------------------------------------

def transform_resumo(nfe: list, cp: list, ad: list, curva_forn: list) -> None:
    print("  Resumo...")

    total_geral = sum(flt(r["TOTAL"]) for r in nfe)
    total_2024  = sum(flt(r["TOTAL"]) for r in nfe if str(r.get("ANO","")) == "2024")
    total_2025  = sum(flt(r["TOTAL"]) for r in nfe if str(r.get("ANO","")) == "2025")
    yoy = pct(total_2025 - total_2024, total_2024) if total_2024 else 0.0

    forn_ativos = len({r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","") for r in nfe})
    com_cot     = sum(1 for r in nfe if flt(r.get("PRE_MIN_COT","")) > 0 or
                      (r.get("PRE_MIN_COT","") and r.get("PRE_MIN_COT","").strip() not in ("","0")))
    # No CSV local, campos vazios do Zoho vêm como ''. Contamos com PRE_MIN_COT não vazio.
    com_cot     = sum(1 for r in nfe if r.get("PRE_MIN_COT","").strip() not in ("", "0"))
    pct_cot     = pct(com_cot, len(nfe))

    imp_total   = sum(flt(r.get("IMP_COT","")) for r in nfe if flt(r.get("IMP_COT","")) > 0)

    cp_aberto   = sum(flt(r.get("VRATUAPAG","")) for r in cp if r.get("STATUSPAG","") == "Em Aberto")
    cp_titulos  = sum(1 for r in cp if r.get("STATUSPAG","") == "Em Aberto")

    ad_pendente = sum(flt(r.get("VALOR_FINAL","")) for r in ad if r.get("STATUS_CONCILIACAO","") == "ADIANTAMENTO ?")

    save_json("kpis_resumo.json", {
        "total_comprado": fmt_r(total_geral),
        "crescimento_yoy_pct": yoy,
        "fornecedores_ativos": forn_ativos,
        "pct_com_cotacao": pct_cot,
        "imp_cot_total": fmt_r(imp_total),
        "cp_aberto": fmt_r(cp_aberto),
        "cp_titulos": cp_titulos,
        "ad_pendente": fmt_r(ad_pendente),
    })

    # Evolução mensal
    by_mes: dict[str, float] = defaultdict(float)
    for r in nfe:
        by_mes[r.get("MESANO","")]  += flt(r["TOTAL"])
    save_csv("resumo_por_mes.csv", [
        {"mesano": k, "spend": fmt_r(v)}
        for k, v in sorted(by_mes.items()) if k.strip()
    ])

    # Por negócio
    by_neg: dict[str, float] = defaultdict(float)
    for r in nfe:
        by_neg[r.get("FI.NEGOCIO","") or r.get("NEGOCIO","")]  += flt(r["TOTAL"])
    rows_neg = sorted(
        [{"negocio": k, "spend": fmt_r(v), "pct": pct(v, total_geral)} for k, v in by_neg.items() if k.strip()],
        key=lambda x: -x["spend"]
    )
    save_csv("resumo_por_negocio.csv", rows_neg)

    # Top categorias CAT2
    by_cat2: dict[str, dict] = defaultdict(lambda: {"spend": 0.0, "imp_cot": 0.0, "inf_sum": 0.0, "inf_n": 0})
    for r in nfe:
        cat = r.get("CAT2","")
        by_cat2[cat]["spend"]   += flt(r["TOTAL"])
        by_cat2[cat]["imp_cot"] += flt(r.get("IMP_COT",""))
        inf = flt(r.get("INF_PROD_PMP",""))
        if inf != 0:
            by_cat2[cat]["inf_sum"] += inf
            by_cat2[cat]["inf_n"]   += 1
    rows_cat = sorted(
        [{"cat2": k,
          "spend": fmt_r(d["spend"]),
          "pct": pct(d["spend"], total_geral),
          "imp_cot": fmt_r(d["imp_cot"]),
          "inflacao_media_pct": round(d["inf_sum"] / d["inf_n"], 2) if d["inf_n"] else 0.0
         } for k, d in by_cat2.items() if k.strip()],
        key=lambda x: -x["spend"]
    )
    save_csv("resumo_top_categorias.csv", rows_cat[:20])

    # Top fornecedores
    forn_spend: dict[str, float] = defaultdict(float)
    forn_nm:    dict[str, str]   = {}
    forn_curva: dict[str, str]   = {}
    for r in nfe:
        cd = r.get("CDFORNECED_OFICIAL") or r.get("CDFORNECED","")
        forn_spend[cd] += flt(r["TOTAL"])
        forn_nm[cd]    = r.get("FANTASIA_OFICIAL") or r.get("NMFANTFORN","")
        forn_curva[cd] = r.get("CURVA_FORN","")
    acum = 0.0
    rows_forn = []
    for cd, v in sorted(forn_spend.items(), key=lambda x: -x[1])[:20]:
        acum += v
        rows_forn.append({
            "cdforneced": cd,
            "fornecedor": forn_nm.get(cd,""),
            "curva": forn_curva.get(cd,""),
            "spend": fmt_r(v),
            "pct": pct(v, total_geral),
            "pct_acum": pct(acum, total_geral),
        })
    save_csv("resumo_top_fornecedores.csv", rows_forn)

    # Por UF
    by_uf: dict[str, float] = defaultdict(float)
    for r in nfe:
        by_uf[r.get("UF","")]  += flt(r["TOTAL"])
    save_csv("resumo_por_uf.csv", [
        {"uf": k, "spend": fmt_r(v), "pct": pct(v, total_geral)}
        for k, v in sorted(by_uf.items(), key=lambda x: -x[1]) if k.strip()
    ])


# ---------------------------------------------------------------------------
# 2. OPORTUNIDADES (IMP_COT)
# ---------------------------------------------------------------------------

def transform_oportunidades(nfe: list) -> None:
    print("  Oportunidades...")
    id_data: dict[str, dict] = defaultdict(lambda: {
        "imp_cot": 0.0, "spend": 0.0, "qtde": 0.0,
        "produto": "", "cat2": "", "uf": "",
        "forn_atual": "", "forn_min": "", "preco_min": 0.0,
        "curva_id": "", "curva_forn": ""
    })
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp <= 0:
            continue
        k = r.get("ID","")
        d = id_data[k]
        d["imp_cot"]   += imp
        d["spend"]     += flt(r["TOTAL"])
        d["qtde"]      += flt(r.get("QTDE_EST",""))
        d["produto"]    = r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]       = r.get("CAT2","")
        d["uf"]         = r.get("UF","")
        d["forn_atual"] = r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        d["forn_min"]   = r.get("FORN_MIN_COT","")
        d["preco_min"]  = flt(r.get("PRE_MIN_COT",""))
        d["curva_id"]   = r.get("CURVA_ID","")
        d["curva_forn"] = r.get("CURVA_FORN","")

    rows = sorted(
        [{"id": k, **v, "imp_cot": fmt_r(v["imp_cot"]), "spend": fmt_r(v["spend"])}
         for k, v in id_data.items()],
        key=lambda x: -x["imp_cot"]
    )
    save_csv("oportunidades_top.csv", rows[:200])


# ---------------------------------------------------------------------------
# 3. COTAÇÕES
# ---------------------------------------------------------------------------

def transform_cotacoes(nfe: list, num_cot: list) -> None:
    print("  Cotações...")

    # Cobertura mensal
    mes_data: dict[str, dict] = defaultdict(lambda: {"total": 0, "com_cot": 0})
    for r in nfe:
        mes = r.get("MESANO","")
        if not mes.strip():
            continue
        mes_data[mes]["total"] += 1
        if r.get("PRE_MIN_COT","").strip() not in ("","0"):
            mes_data[mes]["com_cot"] += 1
    save_csv("cotacoes_cobertura_mes.csv", [
        {"mesano": k,
         "total_linhas": d["total"],
         "com_cotacao": d["com_cot"],
         "pct_cobertura": pct(d["com_cot"], d["total"])}
        for k, d in sorted(mes_data.items()) if k.strip()
    ])

    # Cobertura por UF
    uf_data: dict[str, dict] = defaultdict(lambda: {"total": 0, "com_cot": 0, "imp_cot": 0.0, "spend": 0.0})
    for r in nfe:
        uf = r.get("UF","")
        uf_data[uf]["total"] += 1
        uf_data[uf]["spend"] += flt(r["TOTAL"])
        if r.get("PRE_MIN_COT","").strip() not in ("","0"):
            uf_data[uf]["com_cot"] += 1
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            uf_data[uf]["imp_cot"] += imp
    save_csv("cotacoes_por_uf.csv", sorted([
        {"uf": k,
         "total_linhas": d["total"],
         "com_cotacao": d["com_cot"],
         "pct_cobertura": pct(d["com_cot"], d["total"]),
         "imp_cot": fmt_r(d["imp_cot"]),
         "spend": fmt_r(d["spend"]),
         "imp_sobre_spend_pct": pct(d["imp_cot"], d["spend"])}
        for k, d in uf_data.items() if k.strip()
    ], key=lambda x: -x["spend"]))

    # Cobertura por curva ABC do ID
    curva_data: dict[str, dict] = defaultdict(lambda: {"total": 0, "sem_cot": 0, "mono_cot": 0})
    for r in num_cot:
        curva = r.get("CURVA_ID","")
        qtd   = flt(r.get("QTD_COT",""))
        curva_data[curva]["total"] += 1
        if qtd == 0:
            curva_data[curva]["sem_cot"] += 1
        elif qtd == 1:
            curva_data[curva]["mono_cot"] += 1
    curva_order = ["AAA","AA","A","B","BB","C","CC","CCC"]
    save_csv("cotacoes_curva_abc.csv", [
        {"curva_id": c,
         "total_ids": curva_data[c]["total"],
         "sem_cotacao": curva_data[c]["sem_cot"],
         "mono_cotacao": curva_data[c]["mono_cot"],
         "pct_risco": pct(curva_data[c]["sem_cot"] + curva_data[c]["mono_cot"], curva_data[c]["total"])}
        for c in curva_order if curva_data[c]["total"] > 0
    ])


# ---------------------------------------------------------------------------
# 4. IMPACTO
# ---------------------------------------------------------------------------

def transform_impacto(nfe: list) -> None:
    print("  Impacto...")

    # Por UF
    uf_imp: dict[str, float] = defaultdict(float)
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            uf_imp[r.get("UF","")] += imp
    save_csv("impacto_por_uf.csv", sorted(
        [{"uf": k, "imp_cot": fmt_r(v)} for k, v in uf_imp.items() if k.strip()],
        key=lambda x: -x["imp_cot"]
    ))

    # Top IDs
    id_data: dict[str, dict] = defaultdict(lambda: {
        "imp_cot": 0.0, "spend": 0.0,
        "produto": "", "cat2": "", "uf": "",
        "forn_atual": "", "forn_min": "", "pre_min_cot": 0.0,
        "curva_id": "", "curva_forn": ""
    })
    for r in nfe:
        imp = flt(r.get("IMP_COT",""))
        if imp <= 0:
            continue
        k = r.get("ID","")
        d = id_data[k]
        d["imp_cot"]      += imp
        d["spend"]        += flt(r["TOTAL"])
        d["produto"]       = r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]          = r.get("CAT2","")
        d["uf"]            = r.get("UF","")
        d["forn_atual"]    = r.get("FANTASIA_OFICIAL","") or r.get("NMFANTFORN","")
        d["forn_min"]      = r.get("FORN_MIN_COT","")
        d["pre_min_cot"]   = flt(r.get("PRE_MIN_COT",""))
        d["curva_id"]      = r.get("CURVA_ID","")
        d["curva_forn"]    = r.get("CURVA_FORN","")

    save_csv("impacto_top_ids.csv", sorted(
        [{"id": k, **{kk: (fmt_r(vv) if isinstance(vv, float) else vv) for kk, vv in v.items()}}
         for k, v in id_data.items()],
        key=lambda x: -x["imp_cot"]
    )[:100])


# ---------------------------------------------------------------------------
# 5. INFLAÇÃO
# ---------------------------------------------------------------------------

def transform_inflacao(nfe: list) -> None:
    print("  Inflação...")

    # Por CAT2 × MESANO
    cat_mes: dict[tuple, dict] = defaultdict(lambda: {"inf_sum": 0.0, "inf_n": 0, "spend": 0.0})
    for r in nfe:
        cat  = r.get("CAT2","")
        mes  = r.get("MESANO","")
        if not cat.strip() or not mes.strip():
            continue
        inf = flt(r.get("INF_PROD_PMP",""))
        d   = cat_mes[(cat, mes)]
        d["spend"] += flt(r["TOTAL"])
        if inf != 0:
            d["inf_sum"] += inf
            d["inf_n"]   += 1
    save_csv("inflacao_por_cat_mes.csv", sorted(
        [{"cat2": k[0], "mesano": k[1],
          "spend": fmt_r(d["spend"]),
          "inflacao_media_pct": round(d["inf_sum"] / d["inf_n"], 2) if d["inf_n"] else 0.0}
         for k, d in cat_mes.items()],
        key=lambda x: (x["cat2"], x["mesano"])
    ))

    # Top produtos por inflação
    prod_inf: dict[str, dict] = defaultdict(lambda: {"inf_sum": 0.0, "inf_n": 0, "spend": 0.0, "cat2": "", "nome": ""})
    for r in nfe:
        cd   = r.get("CDPRODUTO_OFICIAL","")
        inf  = flt(r.get("INF_PROD_PMP",""))
        if not cd:
            continue
        prod_inf[cd]["spend"] += flt(r["TOTAL"])
        prod_inf[cd]["nome"]   = r.get("NMPRODUTO_OFICIAL","")
        prod_inf[cd]["cat2"]   = r.get("CAT2","")
        if inf != 0:
            prod_inf[cd]["inf_sum"] += inf
            prod_inf[cd]["inf_n"]   += 1

    rows = [{"cdproduto": k,
             "produto": d["nome"],
             "cat2": d["cat2"],
             "spend": fmt_r(d["spend"]),
             "inflacao_media_pct": round(d["inf_sum"] / d["inf_n"], 2) if d["inf_n"] else 0.0}
            for k, d in prod_inf.items() if d["inf_n"] >= 3 and d["spend"] > 100_000]
    top_inf  = sorted(rows, key=lambda x: -x["inflacao_media_pct"])[:25]
    top_defl = sorted(rows, key=lambda x: x["inflacao_media_pct"])[:25]
    save_csv("inflacao_top_produtos.csv", top_inf)
    save_csv("deflacao_top_produtos.csv", top_defl)


# ---------------------------------------------------------------------------
# 6. FILIAIS
# ---------------------------------------------------------------------------

def transform_filiais(nfe: list) -> None:
    print("  Filiais...")
    fil_data: dict[str, dict] = defaultdict(lambda: {
        "spend": 0.0, "com_cot": 0, "total": 0, "imp_cot": 0.0,
        "negocio": "", "uf": "", "empresa": "", "nome": ""
    })
    for r in nfe:
        fil = str(r.get("CDFILIAL","")).strip()
        if not fil:
            continue
        d = fil_data[fil]
        d["spend"]   += flt(r["TOTAL"])
        d["total"]   += 1
        d["negocio"]  = r.get("FI.NEGOCIO","")
        d["uf"]       = r.get("UF","")
        d["empresa"]  = r.get("NMEMP","")
        d["nome"]     = r.get("NMFILIAL","")
        if r.get("PRE_MIN_COT","").strip() not in ("","0"):
            d["com_cot"] += 1
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            d["imp_cot"] += imp

    total_geral = sum(d["spend"] for d in fil_data.values())
    save_csv("filiais_resumo.csv", sorted(
        [{"cdfilial": k,
          "nome": d["nome"],
          "negocio": d["negocio"],
          "uf": d["uf"],
          "empresa": d["empresa"],
          "spend": fmt_r(d["spend"]),
          "pct": pct(d["spend"], total_geral),
          "pct_com_cotacao": pct(d["com_cot"], d["total"]),
          "imp_cot": fmt_r(d["imp_cot"])}
         for k, d in fil_data.items()],
        key=lambda x: -x["spend"]
    ))


# ---------------------------------------------------------------------------
# 7. PRODUTOS
# ---------------------------------------------------------------------------

def transform_produtos(nfe: list) -> None:
    print("  Produtos...")
    prod_data: dict[str, dict] = defaultdict(lambda: {
        "spend": 0.0, "cat2": "", "curva_id": "", "curva_prod": "",
        "pmp_atual": 0.0, "pmp_12m": 0.0, "imp_cot": 0.0, "nome": ""
    })
    for r in nfe:
        cd  = r.get("CDPRODUTO_OFICIAL","")
        if not cd:
            continue
        d = prod_data[cd]
        d["spend"]     += flt(r["TOTAL"])
        d["nome"]       = r.get("NMPRODUTO_OFICIAL","")
        d["cat2"]       = r.get("CAT2","")
        d["curva_id"]   = r.get("CURVA_ID","")
        d["curva_prod"] = r.get("CURVA_PROD","")
        pmp = flt(r.get("PMP_PROD",""))
        if pmp > 0:
            d["pmp_atual"] = pmp
        pmp12 = flt(r.get("PMP_PROD_12",""))
        if pmp12 > 0:
            d["pmp_12m"] = pmp12
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            d["imp_cot"] += imp

    rows = sorted(
        [{"cdproduto": k,
          "produto": d["nome"],
          "cat2": d["cat2"],
          "curva_id": d["curva_id"],
          "curva_prod": d["curva_prod"],
          "spend": fmt_r(d["spend"]),
          "pmp_atual": fmt_r(d["pmp_atual"]),
          "pmp_12m": fmt_r(d["pmp_12m"]),
          "var_pmp_pct": round((d["pmp_atual"] - d["pmp_12m"]) / d["pmp_12m"] * 100, 2)
                          if d["pmp_12m"] > 0 else 0.0,
          "imp_cot": fmt_r(d["imp_cot"])}
         for k, d in prod_data.items() if d["spend"] > 0],
        key=lambda x: -x["spend"]
    )
    save_csv("produtos_top.csv", rows[:200])


# ---------------------------------------------------------------------------
# 8. FINANCEIRO (CP)
# ---------------------------------------------------------------------------

def transform_cp(cp: list) -> None:
    print("  CP (Financeiro)...")

    # Aging por FAIXA_DIAS
    aging: dict[str, dict] = defaultdict(lambda: {"valor": 0.0, "titulos": 0})
    for r in cp:
        if r.get("STATUSPAG","") != "Em Aberto":
            continue
        faixa = r.get("FAIXA_DIAS","").strip().rstrip("\n").rstrip()
        aging[faixa]["valor"]   += flt(r.get("VRATUAPAG",""))
        aging[faixa]["titulos"] += 1
    save_csv("cp_aging.csv", sorted(
        [{"faixa_dias": k, "valor": fmt_r(d["valor"]), "titulos": d["titulos"]}
         for k, d in aging.items() if k],
        key=lambda x: -x["valor"]
    ))

    # Por fornecedor
    forn_cp: dict[str, dict] = defaultdict(lambda: {"valor": 0.0, "titulos": 0, "nm": ""})
    for r in cp:
        if r.get("STATUSPAG","") != "Em Aberto":
            continue
        cd = r.get("CDFORNECED","")
        forn_cp[cd]["valor"]   += flt(r.get("VRATUAPAG",""))
        forn_cp[cd]["titulos"] += 1
        forn_cp[cd]["nm"]       = r.get("NMFANTFORN","")
    save_csv("cp_por_fornecedor.csv", sorted(
        [{"cdforneced": k, "fornecedor": d["nm"], "cp_aberto": fmt_r(d["valor"]), "titulos": d["titulos"]}
         for k, d in forn_cp.items()],
        key=lambda x: -x["cp_aberto"]
    )[:100])


# ---------------------------------------------------------------------------
# 9. ADIANTAMENTOS
# ---------------------------------------------------------------------------

def transform_adiantamentos(ad: list) -> None:
    print("  Adiantamentos...")
    status_totals: dict[str, dict] = defaultdict(lambda: {"valor": 0.0, "registros": 0})
    for r in ad:
        s = r.get("STATUS_CONCILIACAO","")
        status_totals[s]["valor"]     += flt(r.get("VALOR_FINAL",""))
        status_totals[s]["registros"] += 1

    save_csv("ad_resumo.csv", [
        {"status": k, "valor": fmt_r(d["valor"]), "registros": d["registros"]}
        for k, d in status_totals.items()
    ])

    # Top fornecedores com AD pendente
    forn_ad: dict[str, dict] = defaultdict(lambda: {"valor": 0.0, "registros": 0, "nm": ""})
    for r in ad:
        if r.get("STATUS_CONCILIACAO","") != "ADIANTAMENTO ?":
            continue
        cd = r.get("CDFORNECED","")
        forn_ad[cd]["valor"]     += flt(r.get("VALOR_FINAL",""))
        forn_ad[cd]["registros"] += 1
        forn_ad[cd]["nm"]         = r.get("FANTASIA_OFICIAL","")
    save_csv("ad_por_fornecedor.csv", sorted(
        [{"cdforneced": k, "fornecedor": d["nm"], "valor_pendente": fmt_r(d["valor"]), "registros": d["registros"]}
         for k, d in forn_ad.items()],
        key=lambda x: -x["valor_pendente"]
    )[:50])


# ---------------------------------------------------------------------------
# 10. CATEGORIAS (hierarquia)
# ---------------------------------------------------------------------------

def transform_categorias(nfe: list) -> None:
    print("  Categorias...")
    cat_data: dict[tuple, dict] = defaultdict(lambda: {"spend": 0.0, "imp_cot": 0.0, "inf_n": 0, "inf_sum": 0.0})
    for r in nfe:
        key = (r.get("CAT1",""), r.get("CAT2",""), r.get("CAT3",""), r.get("CAT4",""), r.get("CAT5",""))
        cat_data[key]["spend"]   += flt(r["TOTAL"])
        imp = flt(r.get("IMP_COT",""))
        if imp > 0:
            cat_data[key]["imp_cot"] += imp
        inf = flt(r.get("INF_PROD_PMP",""))
        if inf != 0:
            cat_data[key]["inf_sum"] += inf
            cat_data[key]["inf_n"]   += 1

    total_geral = sum(d["spend"] for d in cat_data.values())
    save_csv("categorias_hierarquia.csv", sorted(
        [{"cat1": k[0], "cat2": k[1], "cat3": k[2], "cat4": k[3], "cat5": k[4],
          "spend": fmt_r(d["spend"]),
          "pct": pct(d["spend"], total_geral),
          "imp_cot": fmt_r(d["imp_cot"]),
          "inflacao_media_pct": round(d["inf_sum"] / d["inf_n"], 2) if d["inf_n"] else 0.0}
         for k, d in cat_data.items() if k[0].strip()],
        key=lambda x: (-x["spend"])
    ))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Carregando dados de {RAW}...")

    nfe     = load("nfe.csv")
    cp      = load("cp.csv")
    ad      = load("ad_v3.csv")
    curva_f = load("curva_forn.csv")
    num_cot = load("num_cot.csv")

    print(f"  NFE: {len(nfe):,}  CP: {len(cp):,}  AD: {len(ad):,}  NUM_COT: {len(num_cot):,}")
    print()
    print(f"Transformando...")

    transform_resumo(nfe, cp, ad, curva_f)
    transform_oportunidades(nfe)
    transform_cotacoes(nfe, num_cot)
    transform_impacto(nfe)
    transform_inflacao(nfe)
    transform_filiais(nfe)
    transform_produtos(nfe)
    transform_cp(cp)
    transform_adiantamentos(ad)
    transform_categorias(nfe)

    # Manifest
    outputs = sorted(OUT.glob("*.csv")) + sorted(OUT.glob("*.json"))
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {"file": p.name, "size_kb": round(p.stat().st_size / 1024, 1)}
            for p in outputs
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    total_kb = sum(p.stat().st_size for p in outputs) / 1024
    print()
    print(f"Concluído: {len(outputs)} arquivos em data/processed/  ({total_kb:.0f} KB total)")
    for p in outputs:
        print(f"  {p.name:<40} {p.stat().st_size/1024:>7.1f} KB")


if __name__ == "__main__":
    main()
