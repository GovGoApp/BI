from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


BASE_DIR = Path(__file__).resolve().parents[1]
PHASE_02_DIR = BASE_DIR / "output" / "fase_02_reconciliacao"
PHASE_OUTPUT_DIR = BASE_DIR / "output" / "fase_03_enriquecimento"
INPUT_FILE = PHASE_02_DIR / "02_fornecedores_prioridade_saneamento.csv"
CACHE_DIR = PHASE_OUTPUT_DIR / "99_cache_opencnpj"

ENRICHED_COLUMNS = [
    "prioridade_saneamento_score",
    "prioridade_saneamento_faixa",
    "chave_unificacao",
    "cnpj",
    "razao_social_interna",
    "nome_fantasia_interna",
    "empresas_origem",
    "codigos_fornecedor",
    "nfe_valor_total",
    "nfe_linhas",
    "curva_classificacao",
    "score_completude",
    "faixa_completude",
    "emails_internos",
    "pendencias_essenciais",
    "pendencias_complementares",
    "status_api",
    "razao_social_oficial",
    "nome_fantasia_oficial",
    "situacao_cadastral_oficial",
    "data_situacao_cadastral",
    "matriz_filial",
    "natureza_juridica",
    "porte_empresa",
    "opcao_simples",
    "data_opcao_simples",
    "opcao_mei",
    "data_opcao_mei",
    "cnae_principal",
    "cnaes_secundarios",
    "uf",
    "municipio",
    "email_oficial",
    "telefones_oficiais",
    "regime_indiciado",
    "potencial_credito_2027_inicial",
    "divergencia_razao_social_oficial",
    "divergencia_nome_fantasia_oficial",
    "divergencia_email_oficial",
]

CLASSIFICATION_COLUMNS = [
    "prioridade_saneamento_score",
    "prioridade_saneamento_faixa",
    "chave_unificacao",
    "cnpj",
    "razao_social_interna",
    "razao_social_oficial",
    "empresas_origem",
    "codigos_fornecedor",
    "nfe_valor_total",
    "nfe_linhas",
    "curva_classificacao",
    "situacao_cadastral_oficial",
    "matriz_filial",
    "porte_empresa",
    "natureza_juridica",
    "opcao_simples",
    "opcao_mei",
    "regime_indiciado",
    "potencial_credito_2027_inicial",
    "status_cadastro_oficial",
    "status_regime_fiscal",
    "necessita_saneamento_cadastral",
    "motivos_saneamento_cadastral",
    "necessita_validacao_fiscal",
    "motivos_validacao_fiscal",
    "divergencia_razao_social_oficial",
    "divergencia_nome_fantasia_oficial",
    "divergencia_email_oficial",
    "pendencias_essenciais",
    "pendencias_complementares",
    "status_api",
]


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def text_upper(value: Any) -> str:
    return normalize_text(value).upper()


def yes_no(value: bool) -> str:
    return "S" if value else "N"


def split_multi(value: Any) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=2,
        backoff_factor=0.8,
        status_forcelist=[408, 429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "accept": "application/json",
            "user-agent": "Fornecedores-OpenCNPJ/1.0",
            "accept-language": "pt-BR,pt;q=0.9",
        }
    )
    return session


def cache_file(cnpj: str) -> Path:
    return CACHE_DIR / f"{cnpj}.json"


def load_cached_payload(cnpj: str) -> dict[str, Any] | None:
    path = cache_file(cnpj)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_cached_payload(cnpj: str, payload: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file(cnpj).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_payload(session: requests.Session, cnpj: str, delay_seconds: float) -> tuple[str, dict[str, Any] | None]:
    cached = load_cached_payload(cnpj)
    if cached is not None:
        return "cache", cached

    try:
        response = session.get(f"https://api.opencnpj.org/{cnpj}", timeout=20)
    except Exception:
        return "erro_requisicao", None

    if response.status_code != 200:
        return f"http_{response.status_code}", None

    try:
        payload = response.json()
    except Exception:
        return "json_invalido", None

    if not isinstance(payload, dict):
        return "payload_invalido", None

    save_cached_payload(cnpj, payload)
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    return "api", payload


def infer_regime(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return "indeterminado"
    mei = str(payload.get("opcao_mei") or "").strip().upper()
    simples = str(payload.get("opcao_simples") or "").strip().upper()
    if mei == "S":
        return "mei"
    if simples == "S":
        return "simples_nacional"
    if simples == "N":
        return "regime_nao_simples"
    return "indeterminado"


def infer_credit_potential(payload: dict[str, Any] | None) -> str:
    regime = infer_regime(payload)
    if regime == "regime_nao_simples":
        return "alto_potencial"
    if regime == "simples_nacional":
        return "potencial_condicionado"
    if regime == "mei":
        return "baixo_ou_inexistente"
    return "indeterminado"


def collect_emails(payload: dict[str, Any] | None) -> list[str]:
    if not isinstance(payload, dict):
        return []
    email = normalize_text(payload.get("email")).lower()
    return [email] if email else []


def collect_phones(payload: dict[str, Any] | None) -> list[str]:
    if not isinstance(payload, dict):
        return []
    out: list[str] = []
    for item in payload.get("telefones") or []:
        if not isinstance(item, dict):
            continue
        ddd = normalize_text(item.get("ddd"))
        numero = normalize_text(item.get("numero"))
        if ddd or numero:
            out.append(f"{ddd}{numero}")
    return out


def compare_names(internal_value: str, official_value: str) -> str:
    left = text_upper(internal_value)
    right = text_upper(official_value)
    if not left or not right:
        return "N"
    return yes_no(left != right)


def build_label(limit: int | None, loaded_count: int, available_count: int) -> str:
    if limit is None or loaded_count >= available_count:
        return "lote_completo"
    return f"top_{loaded_count}"


def classify_official_status(row: dict[str, Any]) -> str:
    official = normalize_text(row.get("situacao_cadastral_oficial")).lower()
    if official == "ativa":
        return "ativa"
    if official:
        return "nao_ativa"
    if row.get("status_api") in {"api", "cache"}:
        return "sem_status_retorno"
    return "nao_consultado"


def classify_regime_status(row: dict[str, Any]) -> str:
    regime = normalize_text(row.get("regime_indiciado"))
    if regime == "regime_nao_simples":
        return "definido_nao_simples"
    if regime == "simples_nacional":
        return "definido_simples"
    if regime == "mei":
        return "definido_mei"
    return "indeterminado"


def build_validation_flags(row: dict[str, Any]) -> tuple[str, str]:
    reasons: list[str] = []
    if row.get("status_api") not in {"api", "cache"}:
        reasons.append("falha_consulta")
    if classify_official_status(row) != "ativa":
        reasons.append("situacao_cadastral_oficial_nao_ativa")
    if classify_regime_status(row) == "indeterminado":
        reasons.append("regime_indeterminado")
    if row.get("divergencia_razao_social_oficial") == "S":
        reasons.append("divergencia_razao_social")
    if row.get("divergencia_nome_fantasia_oficial") == "S":
        reasons.append("divergencia_nome_fantasia")
    if row.get("divergencia_email_oficial") == "S":
        reasons.append("divergencia_email")
    return yes_no(bool(reasons)), ";".join(reasons)


def build_cadastral_sanitation_flags(row: dict[str, Any]) -> tuple[str, str]:
    reasons = split_multi(row.get("pendencias_essenciais"))
    return yes_no(bool(reasons)), ";".join(reasons)


def build_classification_rows(enriched_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    status_counter: Counter[str] = Counter()
    regime_counter: Counter[str] = Counter()
    validate_counter: Counter[str] = Counter()

    for row in enriched_rows:
        official_status = classify_official_status(row)
        regime_status = classify_regime_status(row)
        needs_validation, validation_reasons = build_validation_flags(row)
        needs_sanitation, sanitation_reasons = build_cadastral_sanitation_flags(row)
        classified = {
            "prioridade_saneamento_score": row.get("prioridade_saneamento_score", ""),
            "prioridade_saneamento_faixa": row.get("prioridade_saneamento_faixa", ""),
            "chave_unificacao": row.get("chave_unificacao", ""),
            "cnpj": row.get("cnpj", ""),
            "razao_social_interna": row.get("razao_social_interna", ""),
            "razao_social_oficial": row.get("razao_social_oficial", ""),
            "empresas_origem": row.get("empresas_origem", ""),
            "codigos_fornecedor": row.get("codigos_fornecedor", ""),
            "nfe_valor_total": row.get("nfe_valor_total", ""),
            "nfe_linhas": row.get("nfe_linhas", ""),
            "curva_classificacao": row.get("curva_classificacao", ""),
            "situacao_cadastral_oficial": row.get("situacao_cadastral_oficial", ""),
            "matriz_filial": row.get("matriz_filial", ""),
            "porte_empresa": row.get("porte_empresa", ""),
            "natureza_juridica": row.get("natureza_juridica", ""),
            "opcao_simples": row.get("opcao_simples", ""),
            "opcao_mei": row.get("opcao_mei", ""),
            "regime_indiciado": row.get("regime_indiciado", ""),
            "potencial_credito_2027_inicial": row.get("potencial_credito_2027_inicial", ""),
            "status_cadastro_oficial": official_status,
            "status_regime_fiscal": regime_status,
            "necessita_saneamento_cadastral": needs_sanitation,
            "motivos_saneamento_cadastral": sanitation_reasons,
            "necessita_validacao_fiscal": needs_validation,
            "motivos_validacao_fiscal": validation_reasons,
            "divergencia_razao_social_oficial": row.get("divergencia_razao_social_oficial", ""),
            "divergencia_nome_fantasia_oficial": row.get("divergencia_nome_fantasia_oficial", ""),
            "divergencia_email_oficial": row.get("divergencia_email_oficial", ""),
            "pendencias_essenciais": row.get("pendencias_essenciais", ""),
            "pendencias_complementares": row.get("pendencias_complementares", ""),
            "status_api": row.get("status_api", ""),
        }
        rows.append(classified)
        status_counter[official_status] += 1
        regime_counter[regime_status] += 1
        validate_counter[needs_validation] += 1

    rows.sort(
        key=lambda item: (
            item["necessita_validacao_fiscal"] == "S",
            int(float(item["prioridade_saneamento_score"] or 0)),
            float(item["nfe_valor_total"] or 0),
        ),
        reverse=True,
    )

    summary = {
        "status_cadastro_oficial": dict(status_counter),
        "status_regime_fiscal": dict(regime_counter),
        "necessita_saneamento_cadastral": dict(Counter(row["necessita_saneamento_cadastral"] for row in rows)),
        "necessita_validacao_fiscal": dict(validate_counter),
    }
    return rows, summary


def write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def load_input_rows(limit: int | None) -> tuple[list[dict[str, Any]], int]:
    with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if limit is not None:
        return rows[:limit], len(rows)
    return rows, len(rows)


def build_enriched_rows(input_rows: list[dict[str, Any]], delay_seconds: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    session = build_session()
    enriched_rows: list[dict[str, Any]] = []
    status_counter: Counter[str] = Counter()
    regime_counter: Counter[str] = Counter()
    credit_counter: Counter[str] = Counter()

    try:
        for row in input_rows:
            cnpj = normalize_text(row.get("cnpj"))
            status = "sem_cnpj"
            payload = None
            if cnpj:
                status, payload = fetch_payload(session, cnpj, delay_seconds)

            official_emails = collect_emails(payload)
            official_phones = collect_phones(payload)
            regime = infer_regime(payload)
            credit = infer_credit_potential(payload)

            enriched = {
                "prioridade_saneamento_score": row.get("prioridade_saneamento_score", ""),
                "prioridade_saneamento_faixa": row.get("prioridade_saneamento_faixa", ""),
                "chave_unificacao": row.get("chave_unificacao", ""),
                "cnpj": cnpj,
                "razao_social_interna": row.get("razao_social", ""),
                "nome_fantasia_interna": row.get("nome_fantasia", ""),
                "empresas_origem": row.get("empresas_origem", ""),
                "codigos_fornecedor": row.get("codigos_fornecedor", ""),
                "nfe_valor_total": row.get("nfe_valor_total", ""),
                "nfe_linhas": row.get("nfe_linhas", ""),
                "curva_classificacao": row.get("curva_classificacao", ""),
                "score_completude": row.get("score_completude", ""),
                "faixa_completude": row.get("faixa_completude", ""),
                "emails_internos": row.get("emails", ""),
                "pendencias_essenciais": row.get("pendencias_essenciais", ""),
                "pendencias_complementares": row.get("pendencias_complementares", ""),
                "status_api": status,
                "razao_social_oficial": normalize_text(payload.get("razao_social")) if isinstance(payload, dict) else "",
                "nome_fantasia_oficial": normalize_text(payload.get("nome_fantasia")) if isinstance(payload, dict) else "",
                "situacao_cadastral_oficial": normalize_text(payload.get("situacao_cadastral")) if isinstance(payload, dict) else "",
                "data_situacao_cadastral": normalize_text(payload.get("data_situacao_cadastral")) if isinstance(payload, dict) else "",
                "matriz_filial": normalize_text(payload.get("matriz_filial")) if isinstance(payload, dict) else "",
                "natureza_juridica": normalize_text(payload.get("natureza_juridica")) if isinstance(payload, dict) else "",
                "porte_empresa": normalize_text(payload.get("porte_empresa")) if isinstance(payload, dict) else "",
                "opcao_simples": normalize_text(payload.get("opcao_simples")) if isinstance(payload, dict) else "",
                "data_opcao_simples": normalize_text(payload.get("data_opcao_simples")) if isinstance(payload, dict) else "",
                "opcao_mei": normalize_text(payload.get("opcao_mei")) if isinstance(payload, dict) else "",
                "data_opcao_mei": normalize_text(payload.get("data_opcao_mei")) if isinstance(payload, dict) else "",
                "cnae_principal": normalize_text(payload.get("cnae_principal")) if isinstance(payload, dict) else "",
                "cnaes_secundarios": ";".join(payload.get("cnaes_secundarios") or []) if isinstance(payload, dict) else "",
                "uf": normalize_text(payload.get("uf")) if isinstance(payload, dict) else "",
                "municipio": normalize_text(payload.get("municipio")) if isinstance(payload, dict) else "",
                "email_oficial": ";".join(official_emails),
                "telefones_oficiais": ";".join(official_phones),
                "regime_indiciado": regime,
                "potencial_credito_2027_inicial": credit,
                "divergencia_razao_social_oficial": compare_names(row.get("razao_social", ""), payload.get("razao_social", "") if isinstance(payload, dict) else ""),
                "divergencia_nome_fantasia_oficial": compare_names(row.get("nome_fantasia", ""), payload.get("nome_fantasia", "") if isinstance(payload, dict) else ""),
                "divergencia_email_oficial": yes_no(
                    bool(official_emails)
                    and bool(split_multi(row.get("emails", "")))
                    and not set(split_multi(row.get("emails", ""))).intersection(official_emails)
                ),
            }
            enriched_rows.append(enriched)
            status_counter[status] += 1
            regime_counter[regime] += 1
            credit_counter[credit] += 1
    finally:
        session.close()

    summary = {
        "totais": {
            "linhas_entrada": len(input_rows),
            "linhas_enriquecidas": len(enriched_rows),
            "cache_local": len(list(CACHE_DIR.glob("*.json"))) if CACHE_DIR.exists() else 0,
        },
        "status_api": dict(status_counter),
        "regime_indiciado": dict(regime_counter),
        "potencial_credito_2027_inicial": dict(credit_counter),
    }
    return enriched_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Enriquece fornecedores prioritarios com dados da OpenCNPJ.")
    parser.add_argument("--limit", type=int, default=0, help="Quantidade maxima de fornecedores a enriquecer nesta execucao. Use 0 para lote completo.")
    parser.add_argument("--delay-seconds", type=float, default=0.05, help="Pausa entre requisicoes novas para reduzir carga externa.")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    input_rows, available_count = load_input_rows(args.limit if args.limit and args.limit > 0 else None)
    enriched_rows, summary = build_enriched_rows(input_rows, args.delay_seconds)
    classified_rows, classification_summary = build_classification_rows(enriched_rows)

    suffix = build_label(args.limit if args.limit and args.limit > 0 else None, len(enriched_rows), available_count)
    PHASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_csv = PHASE_OUTPUT_DIR / f"01_fornecedores_opencnpj_enriquecidos_{suffix}.csv"
    output_json = PHASE_OUTPUT_DIR / f"02_fornecedores_opencnpj_enriquecidos_{suffix}_resumo.json"
    class_csv = PHASE_OUTPUT_DIR / f"03_fornecedores_classificacao_fiscal_inicial_{suffix}.csv"
    class_json = PHASE_OUTPUT_DIR / f"04_fornecedores_classificacao_fiscal_inicial_{suffix}_resumo.json"

    write_csv(output_csv, ENRICHED_COLUMNS, enriched_rows)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(class_csv, CLASSIFICATION_COLUMNS, classified_rows)
    class_json.write_text(json.dumps(classification_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Arquivo gerado: {output_csv}")
    print(f"Resumo gerado: {output_json}")
    print(f"Classificacao gerada: {class_csv}")
    print(f"Resumo da classificacao: {class_json}")
    print(f"Fornecedores enriquecidos: {len(enriched_rows)}")


if __name__ == "__main__":
    main()
