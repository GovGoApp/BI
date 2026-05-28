from __future__ import annotations

import csv
import json
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_CSV = Path("output/08_regime_fiscal/04_fornecedores_08_auditoria_simplificada.csv")
OUT_DIR = Path("output/08_regime_fiscal")
CACHE_DIR = OUT_DIR / "cache_cnpja_publica"
QUEUE_CSV = OUT_DIR / "07_fila_resolucao_regime_indeterminado.csv"
RESULT_CSV = OUT_DIR / "08_resultado_busca_cnpja_fila_prioritaria.csv"
SUMMARY_JSON = OUT_DIR / "09_resumo_busca_cnpja_fila_prioritaria.json"
RUN_LOG = OUT_DIR / "09_busca_cnpja_progress.log"

PUBLIC_API_INTERVAL_SECONDS = 13.0
MAX_RETRIES = 3

SPECIAL_NATURE_KEYWORDS = (
    "estado",
    "municipio",
    "município",
    "orgao",
    "órgao",
    "órgão",
    "autarquia",
    "fundacao publica",
    "fundação pública",
    "judiciario",
    "judiciário",
    "servico notarial",
    "serviço notarial",
    "cartorio",
    "cartório",
    "fundo",
    "condominio",
    "condomínio",
)


def digits(value: str | None) -> str:
    return re.sub(r"\D+", "", value or "")


def money_to_float(value: str | None) -> float:
    try:
        return float(str(value or "0").replace(",", "."))
    except ValueError:
        return 0.0


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_log(message: str) -> None:
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}"
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def normalize_text(value: str | None) -> str:
    text = (value or "").lower()
    replacements = {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def is_special_nature(row: dict[str, Any]) -> bool:
    nature = normalize_text(row.get("natureza_juridica"))
    name = normalize_text(row.get("razao_original"))
    haystack = f"{nature} {name}"
    return any(keyword in haystack for keyword in SPECIAL_NATURE_KEYWORDS)


def cnpj_check(base12: str) -> str:
    nums = [int(x) for x in base12]
    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    rem = sum(n * w for n, w in zip(nums, weights_1)) % 11
    d1 = 0 if rem < 2 else 11 - rem
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    rem = sum(n * w for n, w in zip(nums + [d1], weights_2)) % 11
    d2 = 0 if rem < 2 else 11 - rem
    return base12 + str(d1) + str(d2)


def matriz_candidate(cnpj: str) -> str:
    clean = digits(cnpj)
    if len(clean) != 14:
        return ""
    return cnpj_check(clean[:8] + "0001")


def load_rows() -> list[dict[str, Any]]:
    with BASE_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build_queue(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    queue: list[dict[str, Any]] = []
    for row in rows:
        if row.get("regime_08") != "Indeterminado":
            continue
        if row.get("situacao_label") != "Ativa":
            continue
        if row.get("movimento_label") != "Com movimento":
            continue
        if is_special_nature(row):
            continue
        out = dict(row)
        out["cnpj_limpo"] = digits(row.get("documento"))
        out["cnpj_matriz_candidato"] = matriz_candidate(out["cnpj_limpo"])
        out["fila_regime"] = "privado_ativo_com_movimento"
        queue.append(out)
    queue.sort(key=lambda r: money_to_float(r.get("valor_referencia")), reverse=True)
    return queue


def cache_path(cnpj: str) -> Path:
    return CACHE_DIR / f"{cnpj}.json"


def read_cache(cnpj: str) -> dict[str, Any] | None:
    path = cache_path(cnpj)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def save_cache(cnpj: str, payload: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path(cnpj).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch_cnpja(cnpj: str) -> dict[str, Any]:
    cached = read_cache(cnpj)
    if cached:
        cached["_cache_hit"] = True
        return cached

    url = f"https://open.cnpja.com/office/{cnpj}"
    last_error: str | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = Request(url, headers={"User-Agent": "Fornecedores-RegimeFiscal/08"})
            with urlopen(req, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
                result = {
                    "_cache_hit": False,
                    "_status": response.status,
                    "_source_url": url,
                    "_fetched_at": datetime.now().isoformat(timespec="seconds"),
                    "payload": payload,
                }
                save_cache(cnpj, result)
                time.sleep(PUBLIC_API_INTERVAL_SECONDS)
                return result
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore")[:1000]
            last_error = f"HTTP {exc.code}: {body}"
            if exc.code == 429:
                wait = 70 * attempt
                append_log(f"rate_limit cnpj={cnpj} tentativa={attempt}/{MAX_RETRIES}; aguardando {wait}s")
                time.sleep(wait)
                continue
            break
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            time.sleep(10 * attempt)

    result = {
        "_cache_hit": False,
        "_status": "erro",
        "_source_url": url,
        "_fetched_at": datetime.now().isoformat(timespec="seconds"),
        "_error": last_error or "erro desconhecido",
        "payload": {},
    }
    save_cache(cnpj, result)
    time.sleep(PUBLIC_API_INTERVAL_SECONDS)
    return result


def classify_cnpja(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("payload") or {}
    company = payload.get("company") or {}
    simples = company.get("simples") or {}
    simei = company.get("simei") or {}
    simples_opt = simples.get("optant")
    simei_opt = simei.get("optant")
    source = "CNPJa publica"
    criterion = "sem flags Simples/SIMEI"
    evidence = ""
    regime = "Indeterminado"
    credit = "Pendente"

    if simei_opt is True:
        regime = "MEI"
        credit = "Baixo"
        criterion = "simei.optant=true"
        evidence = "SIMEI optante"
    elif simples_opt is True:
        regime = "Simples"
        credit = "Condicionado"
        criterion = "simples.optant=true"
        evidence = "Simples optante"
    elif simples_opt is False and simei_opt is False:
        regime = "Nao Simples"
        credit = "Alto"
        criterion = "simples.optant=false e simei.optant=false"
        evidence = "Nao optante Simples/SIMEI"
    elif simples_opt is False:
        regime = "Nao Simples"
        credit = "Alto"
        criterion = "simples.optant=false"
        evidence = "Nao optante Simples"

    return {
        "regime_cnpja": regime,
        "credito_cnpja": credit,
        "fonte_cnpja": source,
        "criterio_cnpja": criterion,
        "evidencia_cnpja": evidence,
        "status_cnpja": record.get("_status"),
        "cache_cnpja": "S" if record.get("_cache_hit") else "N",
        "razao_cnpja": company.get("name") or "",
        "natureza_cnpja": ((company.get("nature") or {}).get("text") if isinstance(company.get("nature"), dict) else ""),
        "simples_optante_cnpja": "" if simples_opt is None else str(simples_opt).lower(),
        "simei_optante_cnpja": "" if simei_opt is None else str(simei_opt).lower(),
        "erro_cnpja": record.get("_error") or "",
    }


def process_queue(queue: list[dict[str, Any]], limit: int | None = None) -> list[dict[str, Any]]:
    selected = queue[:limit] if limit else queue
    total = len(selected)
    results: list[dict[str, Any]] = []
    append_log(f"inicio total={total} limite_api_publica=5/min cache={CACHE_DIR}")

    for idx, row in enumerate(selected, start=1):
        cnpj = row["cnpj_limpo"]
        direct = fetch_cnpja(cnpj)
        direct_class = classify_cnpja(direct)
        matriz_class: dict[str, Any] = {}
        final_class = dict(direct_class)
        fonte_final = "direto"

        if direct_class["regime_cnpja"] == "Indeterminado" and row.get("matriz_filial") == "Filial":
            matriz = row.get("cnpj_matriz_candidato") or ""
            if matriz and matriz != cnpj:
                matriz_record = fetch_cnpja(matriz)
                matriz_class = classify_cnpja(matriz_record)
                if matriz_class["regime_cnpja"] != "Indeterminado":
                    final_class = dict(matriz_class)
                    fonte_final = "matriz"

        result = {
            "ordem": idx,
            "documento": cnpj,
            "documento_formatado": row.get("documento_formatado"),
            "fornecedor": row.get("razao_original"),
            "empresa": row.get("empresa"),
            "empresas_label": row.get("empresas_label"),
            "curva_label": row.get("curva_label"),
            "valor_referencia": row.get("valor_referencia"),
            "valor_referencia_fmt": row.get("valor_referencia_fmt"),
            "nfe_linhas": row.get("nfe_linhas"),
            "nfe_anos": row.get("nfe_anos"),
            "matriz_filial": row.get("matriz_filial"),
            "cnpj_matriz_candidato": row.get("cnpj_matriz_candidato"),
            "natureza_juridica": row.get("natureza_juridica"),
            "porte_empresa": row.get("porte_empresa"),
            "regime_anterior": row.get("regime_08"),
            "credito_anterior": row.get("credito_2027_08"),
            "regime_cnpja_direto": direct_class.get("regime_cnpja"),
            "credito_cnpja_direto": direct_class.get("credito_cnpja"),
            "criterio_cnpja_direto": direct_class.get("criterio_cnpja"),
            "status_cnpja_direto": direct_class.get("status_cnpja"),
            "cache_cnpja_direto": direct_class.get("cache_cnpja"),
            "simples_optante_cnpja": direct_class.get("simples_optante_cnpja"),
            "simei_optante_cnpja": direct_class.get("simei_optante_cnpja"),
            "regime_cnpja_matriz": matriz_class.get("regime_cnpja", ""),
            "credito_cnpja_matriz": matriz_class.get("credito_cnpja", ""),
            "criterio_cnpja_matriz": matriz_class.get("criterio_cnpja", ""),
            "status_cnpja_matriz": matriz_class.get("status_cnpja", ""),
            "regime_proposto": final_class.get("regime_cnpja"),
            "credito_proposto": final_class.get("credito_cnpja"),
            "fonte_proposta": fonte_final,
            "criterio_proposto": final_class.get("criterio_cnpja"),
            "evidencia_proposta": final_class.get("evidencia_cnpja"),
        }
        results.append(result)

        resolved = sum(1 for item in results if item.get("regime_proposto") != "Indeterminado")
        cache_hits = sum(1 for item in results if item.get("cache_cnpja_direto") == "S")
        percent = idx / total * 100 if total else 100
        append_log(
            f"CNPJa [{idx:>3}/{total}] {percent:5.1f}% "
            f"resolvidos={resolved} cache={cache_hits} "
            f"regime={result['regime_proposto']} cnpj={cnpj} fornecedor={row.get('razao_original')[:60]}"
        )

        write_csv(RESULT_CSV, results, result_fieldnames())

    return results


def result_fieldnames() -> list[str]:
    return [
        "ordem",
        "documento",
        "documento_formatado",
        "fornecedor",
        "empresa",
        "empresas_label",
        "curva_label",
        "valor_referencia",
        "valor_referencia_fmt",
        "nfe_linhas",
        "nfe_anos",
        "matriz_filial",
        "cnpj_matriz_candidato",
        "natureza_juridica",
        "porte_empresa",
        "regime_anterior",
        "credito_anterior",
        "regime_cnpja_direto",
        "credito_cnpja_direto",
        "criterio_cnpja_direto",
        "status_cnpja_direto",
        "cache_cnpja_direto",
        "simples_optante_cnpja",
        "simei_optante_cnpja",
        "regime_cnpja_matriz",
        "credito_cnpja_matriz",
        "criterio_cnpja_matriz",
        "status_cnpja_matriz",
        "regime_proposto",
        "credito_proposto",
        "fonte_proposta",
        "criterio_proposto",
        "evidencia_proposta",
    ]


def build_summary(queue: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "entrada": str(BASE_CSV),
        "fila_prioritaria": len(queue),
        "consultados": len(results),
        "regime_proposto": dict(Counter(row.get("regime_proposto") for row in results)),
        "credito_proposto": dict(Counter(row.get("credito_proposto") for row in results)),
        "fonte_proposta": dict(Counter(row.get("fonte_proposta") for row in results)),
        "status_cnpja_direto": dict(Counter(str(row.get("status_cnpja_direto")) for row in results)),
        "cache_direto": dict(Counter(row.get("cache_cnpja_direto") for row in results)),
        "arquivos": {
            "fila": str(QUEUE_CSV),
            "resultado": str(RESULT_CSV),
            "resumo": str(SUMMARY_JSON),
            "cache": str(CACHE_DIR),
            "log": str(RUN_LOG),
        },
    }


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RUN_LOG.write_text("", encoding="utf-8")
    rows = load_rows()
    queue = build_queue(rows)
    queue_fields = [
        "fila_regime",
        "cnpj_limpo",
        "documento_formatado",
        "razao_original",
        "empresa",
        "empresas_label",
        "curva_label",
        "valor_referencia",
        "valor_referencia_fmt",
        "nfe_linhas",
        "nfe_anos",
        "matriz_filial",
        "cnpj_matriz_candidato",
        "natureza_juridica",
        "porte_empresa",
        "situacao_label",
        "movimento_label",
        "regime_08",
        "credito_2027_08",
    ]
    write_csv(QUEUE_CSV, queue, queue_fields)
    append_log(f"fila_prioritaria={len(queue)} arquivo={QUEUE_CSV}")
    results = process_queue(queue, limit)
    summary = build_summary(queue, results)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    append_log(f"fim consultados={len(results)} resumo={SUMMARY_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
