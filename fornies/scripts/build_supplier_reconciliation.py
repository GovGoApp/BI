from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
PHASE_01_DIR = BASE_DIR / "output" / "fase_01_cadastro"
PHASE_OUTPUT_DIR = BASE_DIR / "output" / "fase_02_reconciliacao"

NORMALIZED_FILE = PHASE_01_DIR / "01_fornecedores_cadastro_normalizado.csv"
UNIFIED_FILE = PHASE_01_DIR / "02_fornecedores_cadastro_unificado.csv"
CURVE_FILE = DATA_DIR / "CURVA_FORN_-_TODAS.csv"
NFE_FILE = DATA_DIR / "NFE.csv"

RECONCILED_COLUMNS = [
    "chave_unificacao",
    "cnpj",
    "razao_social",
    "nome_fantasia",
    "empresas_origem",
    "codigos_fornecedor",
    "situacao_cadastral_interna",
    "score_completude",
    "faixa_completude",
    "possui_pendencia_essencial",
    "pendencias_essenciais",
    "pendencias_complementares",
    "divergencia_razao_social",
    "divergencia_nome_fantasia",
    "divergencia_status_interno",
    "divergencia_ie",
    "divergencia_im",
    "tem_movimento_nfe",
    "nfe_linhas",
    "nfe_valor_total",
    "nfe_produtos_unicos",
    "nfe_ufs",
    "nfe_empresas",
    "nfe_anos",
    "tem_curva",
    "curva_classificacao",
    "curva_posicao",
    "curva_total_fornecedor",
    "curva_percentual",
    "curva_origem",
    "curva_nfe_predominante",
    "codigo_conflito_resolvido",
    "prioridade_saneamento_score",
    "prioridade_saneamento_faixa",
    "fila_enriquecimento_cnpj",
]

PRIORITY_COLUMNS = [
    "prioridade_saneamento_score",
    "prioridade_saneamento_faixa",
    "fila_enriquecimento_cnpj",
    "chave_unificacao",
    "cnpj",
    "razao_social",
    "nome_fantasia",
    "empresas_origem",
    "codigos_fornecedor",
    "nfe_valor_total",
    "nfe_linhas",
    "curva_classificacao",
    "score_completude",
    "faixa_completude",
    "possui_pendencia_essencial",
    "pendencias_essenciais",
    "pendencias_complementares",
    "emails",
    "divergencia_razao_social",
    "divergencia_nome_fantasia",
    "divergencia_status_interno",
    "divergencia_ie",
    "divergencia_im",
]

MISSING_COLUMNS = [
    "codigo_fornecedor",
    "tipo_codigo_inferido",
    "tipo_cadastro_inferido",
    "fonte",
    "cnpj_inferido",
    "razao_social_referencia",
    "nfe_linhas",
    "nfe_valor_total",
    "nfe_empresas",
    "nfe_ufs",
    "curva_classificacao",
    "curva_posicao",
    "curva_total_fornecedor",
    "observacao",
]

CURVE_PRIORITY = {
    "AAA": 35,
    "AA": 30,
    "A": 25,
    "B": 20,
    "BB": 15,
    "C": 10,
    "CC": 7,
    "CCC": 5,
    "": 0,
}


def to_float(value: Any) -> float:
    text = str(value or "").strip()
    if not text:
        return 0.0
    text = text.replace(".", "").replace(",", ".") if text.count(",") == 1 and text.count(".") > 1 else text
    try:
        return float(text)
    except Exception:
        try:
            return float(text.replace(",", "."))
        except Exception:
            return 0.0


def to_int(value: Any) -> int:
    try:
        return int(float(str(value or "0").strip()))
    except Exception:
        return 0


def yes_no(value: bool) -> str:
    return "S" if value else "N"


def split_multi(value: Any) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def classify_code_type(code: str) -> str:
    prefix = str(code or "").strip()[:1].upper()
    if prefix == "J":
        return "PJ_CNPJ"
    if prefix == "F":
        return "PF_CPF"
    if prefix == "I":
        return "INSCRICAO_OUTRO"
    if prefix == "O":
        return "OUTRO"
    return "NAO_IDENTIFICADO"


def divergence_count(row: dict[str, Any]) -> int:
    return sum(
        1
        for field in [
            "divergencia_razao_social",
            "divergencia_nome_fantasia",
            "divergencia_status_interno",
            "divergencia_ie",
            "divergencia_im",
        ]
        if str(row.get(field) or "").strip().upper() == "S"
    )


def essential_count(row: dict[str, Any]) -> int:
    return len(split_multi(row.get("pendencias_essenciais")))


def pick_priority_band(score: int) -> str:
    if score >= 90:
        return "critica"
    if score >= 65:
        return "alta"
    if score >= 40:
        return "media"
    return "baixa"


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def load_normalized_records() -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, list[str]]]:
    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)

    with NORMALIZED_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            by_key[row["chave_unificacao"]].append(row)
            code = row["codigo_fornecedor"].strip()
            if code:
                by_code[code].append(row)

    preferred_by_code: dict[str, dict[str, Any]] = {}
    conflicts: dict[str, list[str]] = {}
    for code, rows in by_code.items():
        sorted_rows = sorted(
            rows,
            key=lambda row: (
                bool(row["cnpj"]),
                to_int(row["score_completude"]),
                row["empresa_origem"],
            ),
            reverse=True,
        )
        preferred_by_code[code] = sorted_rows[0]
        keys = sorted({row["chave_unificacao"] for row in rows})
        if len(keys) > 1:
            conflicts[code] = keys

    return preferred_by_code, by_key, conflicts


def load_unified_rows() -> list[dict[str, Any]]:
    with UNIFIED_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_curve_by_code() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with CURVE_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = str(row["CDFORNECED"] or "").strip()
            if not code:
                continue
            out[code] = {
                "curva": str(row["CURVA"] or "").strip(),
                "pos": str(row["POS"] or "").strip(),
                "tot_forn": str(row["TOT_FORN"] or "").strip(),
                "perc": str(row["PERC"] or "").strip(),
            }
    return out


def load_nfe_by_code() -> dict[str, dict[str, Any]]:
    aggregated: dict[str, dict[str, Any]] = {}
    products_by_code: dict[str, set[str]] = defaultdict(set)
    ufs_by_code: dict[str, set[str]] = defaultdict(set)
    companies_by_code: dict[str, set[str]] = defaultdict(set)
    years_by_code: dict[str, set[str]] = defaultdict(set)
    curve_counter_by_code: dict[str, Counter[str]] = defaultdict(Counter)

    with NFE_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            code = str(row["CDFORNECED_OFICIAL"] or row["CDFORNECED"] or "").strip()
            if not code:
                continue

            bucket = aggregated.setdefault(
                code,
                {
                    "codigo_fornecedor": code,
                    "razao_social_referencia": str(row["RAZAO_OFICIAL"] or row["NMRAZSOCFORN"] or "").strip(),
                    "cnpj_inferido": code[1:] if code.startswith("J") and len(code) == 15 else "",
                    "nfe_linhas": 0,
                    "nfe_valor_total": 0.0,
                },
            )
            bucket["nfe_linhas"] += 1
            bucket["nfe_valor_total"] += to_float(row["TOTAL"])

            product = str(row["CDPRODUTO_OFICIAL"] or row["CDPRODUTO"] or "").strip()
            uf = str(row["UF"] or "").strip()
            company = str(row["NMEMP"] or "").strip()
            year = str(row["ANO"] or "").strip()
            curve = str(row["CURVA_FORN"] or "").strip()

            if product:
                products_by_code[code].add(product)
            if uf:
                ufs_by_code[code].add(uf)
            if company:
                companies_by_code[code].add(company)
            if year:
                years_by_code[code].add(year)
            if curve:
                curve_counter_by_code[code][curve] += 1

    for code, bucket in aggregated.items():
        curve_counter = curve_counter_by_code[code]
        predominant_curve = ""
        if curve_counter:
            predominant_curve = sorted(curve_counter.items(), key=lambda item: (item[1], CURVE_PRIORITY.get(item[0], 0), item[0]), reverse=True)[0][0]
        bucket["nfe_valor_total"] = f"{bucket['nfe_valor_total']:.2f}"
        bucket["nfe_produtos_unicos"] = len(products_by_code[code])
        bucket["nfe_ufs"] = ";".join(sorted(ufs_by_code[code]))
        bucket["nfe_empresas"] = ";".join(sorted(companies_by_code[code]))
        bucket["nfe_anos"] = ";".join(sorted(years_by_code[code]))
        bucket["curva_nfe_predominante"] = predominant_curve

    return aggregated


def compute_priority(row: dict[str, Any]) -> tuple[int, str, str]:
    score = 0
    has_nfe = str(row["tem_movimento_nfe"]) == "S"
    has_curve = str(row["tem_curva"]) == "S"
    essential = essential_count(row)
    divergences = divergence_count(row)
    curve_class = str(row.get("curva_classificacao") or "").strip()
    curve_from_nfe = str(row.get("curva_nfe_predominante") or "").strip()
    effective_curve = curve_class or curve_from_nfe
    nfe_value = to_float(row.get("nfe_valor_total"))

    if has_nfe:
        score += 30
    if has_curve:
        score += 20
    score += min(24, essential * 8)
    score += min(20, divergences * 4)
    score += CURVE_PRIORITY.get(effective_curve, 0)

    if nfe_value >= 1_000_000:
        score += 20
    elif nfe_value >= 250_000:
        score += 15
    elif nfe_value >= 50_000:
        score += 10
    elif nfe_value > 0:
        score += 5

    if has_nfe and str(row.get("situacao_cadastral_interna") or "").strip().upper() != "A":
        score += 15

    queue_for_enrichment = "N"
    if row.get("cnpj") and has_nfe and (str(row.get("possui_pendencia_essencial") or "") == "S" or divergences > 0):
        queue_for_enrichment = "S"

    return score, pick_priority_band(score), queue_for_enrichment


def build_reconciliation() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    preferred_by_code, _by_key, conflicts = load_normalized_records()
    unified_rows = load_unified_rows()
    curve_by_code = load_curve_by_code()
    nfe_by_code = load_nfe_by_code()

    reconciled_rows: list[dict[str, Any]] = []
    matched_codes: set[str] = set()
    conflict_hits = 0

    for row in unified_rows:
        codes = split_multi(row.get("codigos_fornecedor"))
        nfe_hits = [nfe_by_code[code] for code in codes if code in nfe_by_code]
        curve_hits = [(code, curve_by_code[code]) for code in codes if code in curve_by_code]

        if nfe_hits:
            matched_codes.update(hit["codigo_fornecedor"] for hit in nfe_hits)
        if curve_hits:
            matched_codes.update(code for code, _curve in curve_hits)

        total_lines = sum(to_int(hit["nfe_linhas"]) for hit in nfe_hits)
        total_value = sum(to_float(hit["nfe_valor_total"]) for hit in nfe_hits)
        unique_products = sum(to_int(hit["nfe_produtos_unicos"]) for hit in nfe_hits)
        ufs = sorted({uf for hit in nfe_hits for uf in split_multi(hit["nfe_ufs"])})
        companies = sorted({company for hit in nfe_hits for company in split_multi(hit["nfe_empresas"])})
        years = sorted({year for hit in nfe_hits for year in split_multi(hit["nfe_anos"])})
        nfe_curve_counter = Counter(hit["curva_nfe_predominante"] for hit in nfe_hits if hit["curva_nfe_predominante"])
        nfe_curve_predominant = ""
        if nfe_curve_counter:
            nfe_curve_predominant = sorted(nfe_curve_counter.items(), key=lambda item: (item[1], CURVE_PRIORITY.get(item[0], 0), item[0]), reverse=True)[0][0]

        selected_curve_code = ""
        selected_curve = None
        if curve_hits:
            selected_curve_code, selected_curve = sorted(
                curve_hits,
                key=lambda item: (
                    CURVE_PRIORITY.get(item[1]["curva"], 0),
                    -to_int(item[1]["pos"]) if item[1]["pos"] else 0,
                    to_float(item[1]["tot_forn"]),
                ),
                reverse=True,
            )[0]

        conflict_flag = "N"
        for code in codes:
            if code in conflicts:
                preferred = preferred_by_code.get(code)
                if preferred and preferred["chave_unificacao"] == row["chave_unificacao"]:
                    conflict_flag = "S"
                    conflict_hits += 1
                    break

        merged = dict(row)
        merged["tem_movimento_nfe"] = yes_no(total_lines > 0)
        merged["nfe_linhas"] = total_lines
        merged["nfe_valor_total"] = f"{total_value:.2f}"
        merged["nfe_produtos_unicos"] = unique_products
        merged["nfe_ufs"] = ";".join(ufs)
        merged["nfe_empresas"] = ";".join(companies)
        merged["nfe_anos"] = ";".join(years)
        merged["tem_curva"] = yes_no(selected_curve is not None)
        merged["curva_classificacao"] = selected_curve["curva"] if selected_curve else ""
        merged["curva_posicao"] = selected_curve["pos"] if selected_curve else ""
        merged["curva_total_fornecedor"] = selected_curve["tot_forn"] if selected_curve else ""
        merged["curva_percentual"] = selected_curve["perc"] if selected_curve else ""
        merged["curva_origem"] = selected_curve_code
        merged["curva_nfe_predominante"] = nfe_curve_predominant
        merged["codigo_conflito_resolvido"] = conflict_flag

        priority_score, priority_band, queue_for_enrichment = compute_priority(merged)
        merged["prioridade_saneamento_score"] = priority_score
        merged["prioridade_saneamento_faixa"] = priority_band
        merged["fila_enriquecimento_cnpj"] = queue_for_enrichment
        reconciled_rows.append(merged)

    priority_rows = [
        {column: row.get(column, "") for column in PRIORITY_COLUMNS}
        for row in reconciled_rows
        if row["tem_movimento_nfe"] == "S" and (
            row["possui_pendencia_essencial"] == "S"
            or divergence_count(row) > 0
            or row["situacao_cadastral_interna"] != "A"
        )
    ]
    priority_rows.sort(
        key=lambda row: (
            to_int(row["prioridade_saneamento_score"]),
            to_float(row["nfe_valor_total"]),
            row["razao_social"],
        ),
        reverse=True,
    )

    missing_rows: list[dict[str, Any]] = []
    all_known_codes = set(preferred_by_code)
    for code, nfe_data in nfe_by_code.items():
        if code in all_known_codes:
            continue
        curve_data = curve_by_code.get(code, {})
        missing_rows.append(
            {
                "codigo_fornecedor": code,
                "tipo_codigo_inferido": code[:1],
                "tipo_cadastro_inferido": classify_code_type(code),
                "fonte": "NFE" if not curve_data else "NFE+CURVA",
                "cnpj_inferido": nfe_data.get("cnpj_inferido", ""),
                "razao_social_referencia": nfe_data.get("razao_social_referencia", ""),
                "nfe_linhas": nfe_data.get("nfe_linhas", 0),
                "nfe_valor_total": nfe_data.get("nfe_valor_total", "0.00"),
                "nfe_empresas": nfe_data.get("nfe_empresas", ""),
                "nfe_ufs": nfe_data.get("nfe_ufs", ""),
                "curva_classificacao": curve_data.get("curva", ""),
                "curva_posicao": curve_data.get("pos", ""),
                "curva_total_fornecedor": curve_data.get("tot_forn", ""),
                "observacao": "Fornecedor com movimento fora do cadastro mestre reconciliado.",
            }
        )

    for code, curve_data in curve_by_code.items():
        if code in all_known_codes or code in nfe_by_code:
            continue
        missing_rows.append(
            {
                "codigo_fornecedor": code,
                "tipo_codigo_inferido": code[:1],
                "tipo_cadastro_inferido": classify_code_type(code),
                "fonte": "CURVA",
                "cnpj_inferido": code[1:] if code.startswith("J") and len(code) == 15 else "",
                "razao_social_referencia": "",
                "nfe_linhas": 0,
                "nfe_valor_total": "0.00",
                "nfe_empresas": "",
                "nfe_ufs": "",
                "curva_classificacao": curve_data.get("curva", ""),
                "curva_posicao": curve_data.get("pos", ""),
                "curva_total_fornecedor": curve_data.get("tot_forn", ""),
                "observacao": "Fornecedor classificado na curva sem correspondencia na base reconciliada.",
            }
        )

    missing_rows.sort(
        key=lambda row: (
            CURVE_PRIORITY.get(str(row.get("curva_classificacao") or "").strip(), 0),
            to_float(row.get("nfe_valor_total")),
            to_int(row.get("nfe_linhas")),
            row.get("codigo_fornecedor", ""),
        ),
        reverse=True,
    )

    reconciled_rows.sort(
        key=lambda row: (
            to_int(row["prioridade_saneamento_score"]),
            to_float(row["nfe_valor_total"]),
            row["razao_social"],
        ),
        reverse=True,
    )

    summary = {
        "fontes": {
            "cadastro_normalizado": str(NORMALIZED_FILE),
            "cadastro_unificado": str(UNIFIED_FILE),
            "curva": str(CURVE_FILE),
            "nfe": str(NFE_FILE),
        },
        "totais": {
            "fornecedores_reconciliados": len(reconciled_rows),
            "fornecedores_com_movimento_nfe": sum(1 for row in reconciled_rows if row["tem_movimento_nfe"] == "S"),
            "fornecedores_com_curva": sum(1 for row in reconciled_rows if row["tem_curva"] == "S"),
            "fornecedores_prioridade_saneamento": len(priority_rows),
            "fornecedores_fila_enriquecimento_cnpj": sum(1 for row in reconciled_rows if row["fila_enriquecimento_cnpj"] == "S"),
            "fornecedores_movimento_sem_cadastro": len(missing_rows),
            "codigos_conflitantes_resolvidos": len(conflicts),
            "ocorrencias_conflito_na_base_reconciliada": conflict_hits,
        },
        "prioridade_faixas": dict(Counter(row["prioridade_saneamento_faixa"] for row in reconciled_rows)),
        "fornecedores_movimento_sem_cadastro_por_prefixo": dict(Counter(row["tipo_codigo_inferido"] for row in missing_rows)),
        "fornecedores_movimento_sem_cadastro_por_tipo": dict(Counter(row["tipo_cadastro_inferido"] for row in missing_rows)),
        "fornecedores_movimento_sem_cadastro_por_fonte": dict(Counter(row["fonte"] for row in missing_rows)),
        "top_curvas_reconciliadas": dict(Counter(row["curva_classificacao"] or row["curva_nfe_predominante"] or "<vazio>" for row in reconciled_rows).most_common()),
        "top_pendencias_essenciais_em_movimento": dict(
            Counter(
                field
                for row in reconciled_rows
                if row["tem_movimento_nfe"] == "S"
                for field in split_multi(row["pendencias_essenciais"])
            ).most_common()
        ),
    }

    return reconciled_rows, priority_rows, missing_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Reconcilia cadastro unificado com NFE e curva de fornecedores.")
    parser.add_argument("--output-dir", default=str(PHASE_OUTPUT_DIR), help="Diretorio de saida dos artefatos.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    reconciled_rows, priority_rows, missing_rows, summary = build_reconciliation()

    write_csv(output_dir / "01_fornecedores_reconciliados_movimento.csv", RECONCILED_COLUMNS, reconciled_rows)
    write_csv(output_dir / "02_fornecedores_prioridade_saneamento.csv", PRIORITY_COLUMNS, priority_rows)
    write_csv(output_dir / "03_fornecedores_movimento_sem_cadastro.csv", MISSING_COLUMNS, missing_rows)

    with (output_dir / "04_fornecedores_reconciliacao_resumo.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print(f"Arquivos gerados em: {output_dir}")
    print(f"- 01_fornecedores_reconciliados_movimento.csv: {len(reconciled_rows)} linhas")
    print(f"- 02_fornecedores_prioridade_saneamento.csv: {len(priority_rows)} linhas")
    print(f"- 03_fornecedores_movimento_sem_cadastro.csv: {len(missing_rows)} linhas")
    print("- 04_fornecedores_reconciliacao_resumo.json")


if __name__ == "__main__":
    main()
