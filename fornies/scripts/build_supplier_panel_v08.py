from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"
INPUT_07 = OUTPUT_DIR / "07_cadastro_total_opencnpj" / "04_fornecedores_total_auditoria.csv"
OUT_DIR = OUTPUT_DIR / "08_regime_fiscal"
VISUAL_DIR = OUTPUT_DIR / "04_visualizacao"
CACHE_DIR = OUT_DIR / "cache_regime_fiscal"

OUT_00_SUMMARY = OUT_DIR / "00_resumo_versao_08.json"
OUT_01_BASE = OUT_DIR / "01_fornecedores_08_base.csv"
OUT_02_PENDING_BEFORE = OUT_DIR / "02_regimes_pendentes_para_consulta.csv"
OUT_03_RESOLVED = OUT_DIR / "03_regimes_resolvidos_fonte_complementar.csv"
OUT_04_AUDIT = OUT_DIR / "04_fornecedores_08_auditoria_simplificada.csv"
OUT_05_INCLUSIONS = OUT_DIR / "05_inclusoes_cadastro_endereco_previa_bd.csv"
OUT_06_PENDING_AFTER = OUT_DIR / "06_regimes_ainda_indeterminados.csv"
HTML_FILE = VISUAL_DIR / "08_painel_fornecedores_regime_fiscal.html"

CURVE_ORDER = {
    "AAA": 1,
    "AA": 2,
    "A": 3,
    "B": 4,
    "BB": 5,
    "C": 6,
    "CC": 7,
    "CCC": 8,
    "Sem curva": 99,
    "": 99,
}

REGIME_ORDER = {
    "Nao Simples": 1,
    "Simples": 3,
    "MEI": 4,
    "Indeterminado": 5,
    "Nao aplicavel": 6,
}

CREDIT_ORDER = {
    "Alto": 1,
    "Condicionado": 2,
    "Baixo": 3,
    "Presumido": 4,
    "Validar": 5,
    "Pendente": 6,
}


def clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def digits(value: Any) -> str:
    return re.sub(r"\D", "", str(value or ""))


def is_blank(value: Any) -> bool:
    return clean(value).lower() in {"", "sem dado", "sem uf", "nan", "none", "null"}


def bool_from_any(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = clean(value).lower()
    if text in {"true", "t", "s", "sim", "1", "yes"}:
        return True
    if text in {"false", "f", "n", "nao", "não", "0", "no"}:
        return False
    return None


def as_float(value: Any) -> float:
    text = clean(value).replace("R$", "").replace("%", "").replace(" ", "")
    if not text:
        return 0.0
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def money(value: Any) -> str:
    amount = as_float(value)
    formatted = f"{amount:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def format_document(doc: str) -> str:
    numbers = digits(doc)
    if len(numbers) == 14:
        return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:12]}-{numbers[12:]}"
    if len(numbers) == 11:
        return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"
    return numbers


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
                    for key, value in row.items()
                }
            )


def parse_json_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(str(value or ""))
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def split_items(value: Any) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def latest_tax_regime(payload: dict[str, Any] | None) -> tuple[str, str]:
    if not isinstance(payload, dict):
        return "", ""
    regimes = payload.get("regime_tributario")
    if not isinstance(regimes, list):
        return "", ""
    candidates: list[tuple[int, str]] = []
    for item in regimes:
        if not isinstance(item, dict):
            continue
        form = clean(item.get("forma_de_tributacao") or item.get("regime_tributario")).upper()
        if not form:
            continue
        try:
            year = int(item.get("ano") or 0)
        except (TypeError, ValueError):
            year = 0
        candidates.append((year, form))
    if not candidates:
        return "", ""
    candidates.sort(reverse=True)
    year, form = candidates[0]
    return str(year) if year else "", form


def credit_from_regime(regime: str, evidence: str) -> str:
    ev = evidence.upper()
    if regime == "MEI":
        return "Baixo"
    if regime == "Simples":
        return "Condicionado"
    if regime == "Nao Simples":
        if "IMUNE" in ev or "ISENTA" in ev or "ISENTO" in ev:
            return "Validar"
        return "Alto"
    if regime == "Nao aplicavel":
        return "Validar"
    return "Pendente"


def classify_from_opencnpj(row: dict[str, Any]) -> dict[str, str] | None:
    if clean(row.get("tipo")) != "PJ/CNPJ" or len(digits(row.get("documento"))) != 14:
        return {
            "regime_08": "Nao aplicavel",
            "origem_fiscal_08": "Nao aplicavel",
            "fonte_fiscal_08": "Cadastro",
            "criterio_fiscal_08": "documento nao PJ/CNPJ",
            "evidencia_fiscal_08": "",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Validar",
            "status_consulta_fiscal_08": "nao_aplicavel",
        }

    mei = bool_from_any(row.get("opcao_mei"))
    simples = bool_from_any(row.get("opcao_simples"))
    if mei is True:
        return {
            "regime_08": "MEI",
            "origem_fiscal_08": "OpenCNPJ",
            "fonte_fiscal_08": "OpenCNPJ",
            "criterio_fiscal_08": "opcao_mei = S",
            "evidencia_fiscal_08": "opcao_mei = S",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Baixo",
            "status_consulta_fiscal_08": "resolvido_opencnpj",
        }
    if simples is True:
        return {
            "regime_08": "Simples",
            "origem_fiscal_08": "OpenCNPJ",
            "fonte_fiscal_08": "OpenCNPJ",
            "criterio_fiscal_08": "opcao_simples = S",
            "evidencia_fiscal_08": "opcao_simples = S",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Condicionado",
            "status_consulta_fiscal_08": "resolvido_opencnpj",
        }
    if simples is False:
        return {
            "regime_08": "Nao Simples",
            "origem_fiscal_08": "OpenCNPJ",
            "fonte_fiscal_08": "OpenCNPJ",
            "criterio_fiscal_08": "opcao_simples = N",
            "evidencia_fiscal_08": "opcao_simples = N",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Alto",
            "status_consulta_fiscal_08": "resolvido_opencnpj",
        }
    return None


def classify_from_payload(payload: dict[str, Any] | None, source: str, status: str) -> dict[str, str]:
    if not isinstance(payload, dict):
        return {
            "regime_08": "Indeterminado",
            "origem_fiscal_08": "Sem evidencia",
            "fonte_fiscal_08": source or "Sem fonte",
            "criterio_fiscal_08": "sem payload fiscal",
            "evidencia_fiscal_08": "",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Pendente",
            "status_consulta_fiscal_08": status or "erro",
        }

    mei = bool_from_any(payload.get("opcao_pelo_mei"))
    simples = bool_from_any(payload.get("opcao_pelo_simples"))
    year, tax_regime = latest_tax_regime(payload)

    if mei is True:
        return {
            "regime_08": "MEI",
            "origem_fiscal_08": source,
            "fonte_fiscal_08": source,
            "criterio_fiscal_08": "opcao_pelo_mei = true",
            "evidencia_fiscal_08": "opcao_pelo_mei = true",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Baixo",
            "status_consulta_fiscal_08": status,
        }
    if simples is True:
        return {
            "regime_08": "Simples",
            "origem_fiscal_08": source,
            "fonte_fiscal_08": source,
            "criterio_fiscal_08": "opcao_pelo_simples = true",
            "evidencia_fiscal_08": "opcao_pelo_simples = true",
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Condicionado",
            "status_consulta_fiscal_08": status,
        }
    if simples is False:
        evidence = "opcao_pelo_simples = false"
        return {
            "regime_08": "Nao Simples",
            "origem_fiscal_08": source,
            "fonte_fiscal_08": source,
            "criterio_fiscal_08": evidence,
            "evidencia_fiscal_08": evidence,
            "ano_evidencia_fiscal_08": "",
            "credito_2027_08": "Alto",
            "status_consulta_fiscal_08": status,
        }
    if tax_regime:
        evidence = f"{year}: {tax_regime}" if year else tax_regime
        regime = "Nao Simples"
        return {
            "regime_08": regime,
            "origem_fiscal_08": "Regime tributario",
            "fonte_fiscal_08": source,
            "criterio_fiscal_08": "inferido por regime_tributario",
            "evidencia_fiscal_08": evidence,
            "ano_evidencia_fiscal_08": year,
            "credito_2027_08": credit_from_regime(regime, evidence),
            "status_consulta_fiscal_08": status,
        }
    return {
        "regime_08": "Indeterminado",
        "origem_fiscal_08": "Sem evidencia",
        "fonte_fiscal_08": source,
        "criterio_fiscal_08": "sem flag Simples/MEI e sem regime_tributario",
        "evidencia_fiscal_08": "",
        "ano_evidencia_fiscal_08": "",
        "credito_2027_08": "Pendente",
        "status_consulta_fiscal_08": status,
    }


def cache_file(cnpj: str) -> Path:
    return CACHE_DIR / f"{cnpj}.json"


def load_cache(cnpj: str) -> dict[str, Any] | None:
    path = cache_file(cnpj)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_cache(cnpj: str, record: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file(cnpj).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def http_json(url: str) -> tuple[int | str, dict[str, Any] | None, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 fornecedor-audit-v08/1.0",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read(500000).decode("utf-8", "replace")
            return response.status, json.loads(text), ""
    except urllib.error.HTTPError as exc:
        try:
            text = exc.read(3000).decode("utf-8", "replace")
        except Exception:
            text = ""
        return exc.code, None, text[:1000]
    except Exception as exc:
        return "ERR", None, f"{type(exc).__name__}: {exc}"


def fetch_regime_payload(cnpj: str, primary_source: str = "minhareceita") -> dict[str, Any]:
    now = datetime.now().isoformat(timespec="seconds")
    sources = (
        [("Minha Receita", f"https://minhareceita.org/{cnpj}"), ("BrasilAPI", f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")]
        if primary_source == "minhareceita"
        else [("BrasilAPI", f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"), ("Minha Receita", f"https://minhareceita.org/{cnpj}")]
    )

    attempts: list[dict[str, Any]] = []
    for source, url in sources:
        status, payload, error = http_json(url)
        attempts.append({"source": source, "url": url, "http_status": status, "error": error})
        if status == 200 and isinstance(payload, dict):
            record = {
                "cnpj": cnpj,
                "status": "ok",
                "source": source,
                "fetched_at": now,
                "payload": payload,
                "attempts": attempts,
            }
            write_cache(cnpj, record)
            return record
        # Fallback only if primary had HTTP/network failure.
        if status == 200:
            break

    record = {
        "cnpj": cnpj,
        "status": "erro",
        "source": sources[0][0],
        "fetched_at": now,
        "payload": None,
        "attempts": attempts,
    }
    write_cache(cnpj, record)
    return record


def progress_line(done: int, total: int, counters: Counter[str], suffix: str = "") -> str:
    pct = (done / total * 100) if total else 100.0
    width = 32
    filled = int(width * pct / 100)
    bar = "#" * filled + "-" * (width - filled)
    return (
        f"RegimeFiscal [{bar}] {done}/{total} {pct:5.1f}% "
        f"cache={counters['cache']} api={counters['api']} erro={counters['erro']} "
        f"resolvidos={counters['resolvido']} pendentes={counters['pendente']} {suffix}"
    )


def resolve_complementary_regimes(rows: list[dict[str, Any]], workers: int, primary_source: str) -> dict[str, dict[str, Any]]:
    candidates = sorted(
        {
            digits(row.get("documento"))
            for row in rows
            if len(digits(row.get("documento"))) == 14 and not classify_from_opencnpj(row)
        }
    )
    total = len(candidates)
    counters: Counter[str] = Counter()
    records: dict[str, dict[str, Any]] = {}
    pending_fetch: list[str] = []

    for cnpj in candidates:
        cached = load_cache(cnpj)
        if cached:
            records[cnpj] = cached
            counters["cache"] += 1
            classification = classify_from_payload(cached.get("payload"), cached.get("source", ""), cached.get("status", "cache"))
            if classification["regime_08"] == "Indeterminado":
                counters["pendente"] += 1
            else:
                counters["resolvido"] += 1
        else:
            pending_fetch.append(cnpj)

    done = len(records)
    print(progress_line(done, total, counters, "cache inicial"), flush=True)

    if pending_fetch:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {executor.submit(fetch_regime_payload, cnpj, primary_source): cnpj for cnpj in pending_fetch}
            last_print = 0.0
            for future in as_completed(futures):
                cnpj = futures[future]
                try:
                    record = future.result()
                except Exception as exc:
                    record = {
                        "cnpj": cnpj,
                        "status": "erro",
                        "source": primary_source,
                        "payload": None,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                    write_cache(cnpj, record)
                records[cnpj] = record
                counters["api"] += 1
                if record.get("status") != "ok":
                    counters["erro"] += 1
                classification = classify_from_payload(record.get("payload"), record.get("source", ""), record.get("status", "api"))
                if classification["regime_08"] == "Indeterminado":
                    counters["pendente"] += 1
                else:
                    counters["resolvido"] += 1
                done += 1
                now = time.time()
                if done == total or now - last_print >= 1.5:
                    print(progress_line(done, total, counters, cnpj), flush=True)
                    last_print = now

    print(progress_line(total, total, counters, "concluido"), flush=True)
    return records


def inclusion_fields(row: dict[str, Any]) -> tuple[list[str], list[str], list[dict[str, str]]]:
    cadastro: list[str] = []
    endereco: list[str] = []
    records: list[dict[str, str]] = []

    def add(group: str, field: str, value: Any, source: str) -> None:
        if is_blank(value):
            return
        target = cadastro if group == "Cadastro" else endereco
        target.append(field)
        records.append(
            {
                "documento": digits(row.get("documento")),
                "documento_formatado": row.get("documento_formatado") or format_document(row.get("documento", "")),
                "fornecedor": row.get("nome_exibicao") or row.get("razao_original") or "",
                "empresas": row.get("empresas_label") or row.get("empresa") or "",
                "grupo": group,
                "campo": field,
                "valor_incluir": clean(value),
                "fonte": source,
            }
        )

    if is_blank(row.get("razao_original")) and not is_blank(row.get("razao_social_oficial")):
        add("Cadastro", "Razao", row.get("razao_social_oficial"), "OpenCNPJ")
    if is_blank(row.get("fantasia_original")) and not is_blank(row.get("nome_fantasia_oficial")):
        add("Cadastro", "Fantasia", row.get("nome_fantasia_oficial"), "OpenCNPJ")
    if is_blank(row.get("status_interno_label")) and not is_blank(row.get("situacao_cadastral_oficial")):
        add("Cadastro", "Situacao", row.get("situacao_cadastral_oficial"), "OpenCNPJ")
    if not is_blank(row.get("porte_empresa")):
        add("Cadastro", "Porte", row.get("porte_empresa"), "OpenCNPJ")
    if not is_blank(row.get("natureza_juridica")):
        add("Cadastro", "Natureza juridica", row.get("natureza_juridica"), "OpenCNPJ")

    if row.get("endereco_opencnpj_incluido") == "S":
        add("Endereco", "Endereco", row.get("endereco_completo"), "OpenCNPJ")
    if row.get("cidade_opencnpj_incluida") == "S":
        add("Endereco", "Cidade", row.get("endereco_municipio"), "OpenCNPJ")
    if row.get("uf_opencnpj_incluida") == "S":
        add("Endereco", "UF", row.get("endereco_uf"), "OpenCNPJ")
    if row.get("telefone_opencnpj_incluido") == "S":
        add("Endereco", "Telefone", row.get("telefones_oficiais"), "OpenCNPJ")
    if row.get("email_opencnpj_incluido") == "S":
        add("Endereco", "Email", row.get("email_endereco_display") or row.get("email_oficial"), "OpenCNPJ")

    cadastro = list(dict.fromkeys(cadastro))
    endereco = list(dict.fromkeys(endereco))
    return cadastro, endereco, records


def build_rows(rows_07: list[dict[str, Any]], regime_records: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rows_08: list[dict[str, Any]] = []
    resolved_records: list[dict[str, Any]] = []
    inclusion_records: list[dict[str, str]] = []

    for row in rows_07:
        out = dict(row)
        out["empresas_lista"] = parse_json_list(row.get("empresas_lista"))
        out["codigos_lista"] = parse_json_list(row.get("codigos_lista"))
        out["ocorrencias"] = parse_json_list(row.get("ocorrencias"))

        doc = digits(row.get("documento"))
        classification = classify_from_opencnpj(row)
        if not classification:
            record = regime_records.get(doc) or {}
            classification = classify_from_payload(record.get("payload"), record.get("source", ""), record.get("status", "sem_cache"))

        out.update(classification)
        out["credito_2027_ordem"] = CREDIT_ORDER.get(out["credito_2027_08"], 99)
        out["regime_ordem"] = REGIME_ORDER.get(out["regime_08"], 99)
        out["sort_curva_rank"] = int(as_float(out.get("sort_curva_rank") or CURVE_ORDER.get(out.get("curva_label"), 99)))
        out["sort_curva_valor"] = as_float(out.get("sort_curva_valor") or out.get("curva_total_fornecedor"))
        out["sort_nfe_valor"] = as_float(out.get("sort_nfe_valor") or out.get("nfe_valor_total"))
        out["valor_referencia"] = max(out["sort_curva_valor"], out["sort_nfe_valor"])
        out["valor_referencia_fmt"] = money(out["valor_referencia"])
        out["documento_formatado"] = row.get("documento_formatado") or format_document(doc)

        cadastro, endereco, inclusions = inclusion_fields(out)
        inclusion_records.extend(inclusions)
        all_fields = cadastro + endereco
        out["inclusoes_cadastro_08"] = ";".join(cadastro)
        out["inclusoes_endereco_08"] = ";".join(endereco)
        out["campos_incluidos_lista"] = all_fields
        out["campos_incluidos_label"] = ";".join(all_fields)
        out["inclusao_status_08"] = "Com inclusao" if all_fields else "Sem inclusao"
        parts = []
        if cadastro:
            parts.append(f"Cadastro {len(cadastro)}")
        if endereco:
            parts.append(f"Endereco {len(endereco)}")
        out["inclusoes_resumo_08"] = " | ".join(parts) if parts else "Sem inclusao"

        resolved_records.append(
            {
                "documento": doc,
                "fornecedor": out.get("nome_exibicao"),
                "regime_anterior": out.get("regime_label"),
                "regime_08": out.get("regime_08"),
                "credito_2027_08": out.get("credito_2027_08"),
                "origem_fiscal_08": out.get("origem_fiscal_08"),
                "fonte_fiscal_08": out.get("fonte_fiscal_08"),
                "criterio_fiscal_08": out.get("criterio_fiscal_08"),
                "evidencia_fiscal_08": out.get("evidencia_fiscal_08"),
                "ano_evidencia_fiscal_08": out.get("ano_evidencia_fiscal_08"),
                "status_consulta_fiscal_08": out.get("status_consulta_fiscal_08"),
                "valor_referencia": out.get("valor_referencia"),
                "valor_referencia_fmt": out.get("valor_referencia_fmt"),
            }
        )

        rows_08.append(out)

    rows_08.sort(
        key=lambda item: (
            item.get("sort_curva_rank", 99),
            -as_float(item.get("valor_referencia")),
            item.get("regime_ordem", 99),
            clean(item.get("nome_exibicao")),
        )
    )
    return rows_08, resolved_records, inclusion_records


def js_string(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_html(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    data_json = json.dumps(rows, ensure_ascii=False)
    summary_json = json.dumps(summary, ensure_ascii=False)
    html_text = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Painel de Fornecedores</title>
  <style>
    :root {{
      --bg:#f3f6fa; --ink:#0f172a; --muted:#64748b; --line:#d8e0ea; --card:#fff;
      --blue:#2563eb; --green:#16a34a; --yellow:#a16207; --red:#b91c1c; --gray:#475569;
    }}
    *{{box-sizing:border-box}}
    body{{margin:0;background:var(--bg);color:var(--ink);font-family:Segoe UI,Arial,sans-serif;font-size:13px}}
    .page{{padding:14px 16px 24px}}
    .top{{display:flex;align-items:center;gap:22px;margin-bottom:10px}}
    h1{{margin:0;font-size:24px;line-height:1.1;font-weight:800;color:#111827;white-space:nowrap}}
    .search{{flex:0 1 620px;height:38px;border:1px solid #c9d5e3;border-radius:9px;background:#fff;padding:6px 10px;font-size:14px}}
    .method{{margin-left:auto;width:42px;height:42px;border:1px solid #c9d5e3;border-radius:10px;background:#fff;font-weight:900;cursor:pointer}}
    .filters{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-bottom:10px}}
    .filter{{position:relative;min-width:0}}
    .filter label{{display:block;font-weight:700;color:#64748b;text-transform:uppercase;font-size:10px;margin:0 0 2px;white-space:nowrap}}
    .filter button{{width:100%;height:31px;border:1px solid #c9d5e3;border-radius:7px;background:#fff;text-align:left;padding:4px 28px 4px 7px;font-size:12px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .filter button:after{{content:'▼';position:absolute;right:9px;top:23px;color:#64748b;font-size:9px}}
    .filter.active button{{border-color:#2563eb;background:#eff6ff}}
    .menu{{display:none;position:absolute;z-index:5000;left:0;right:0;top:47px;max-height:250px;overflow:auto;background:#fff;border:1px solid #c9d5e3;border-radius:8px;box-shadow:0 18px 35px rgba(15,23,42,.18);padding:7px}}
    .filter.open .menu{{display:block}}
    .menu label{{display:flex;align-items:center;gap:7px;font-size:11px;text-transform:none;color:#334155;padding:5px 3px;margin:0;cursor:pointer}}
    .menu input{{width:14px;height:14px}}
    .kpis{{display:grid;grid-template-columns:repeat(5,minmax(0,.85fr)) minmax(370px,1.45fr);gap:10px;margin-bottom:10px}}
    .card{{background:#fff;border:1px solid #dbe2eb;border-radius:8px;padding:8px 10px;min-height:74px}}
    .card b{{display:block;color:#64748b;text-transform:uppercase;font-size:10px;font-weight:700;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .card strong{{font-size:20px;font-weight:800;color:#111827}}
    .pager{{display:grid;grid-template-columns:32px 32px 70px 42px 32px 32px 66px;align-items:center;gap:5px;max-width:330px;white-space:nowrap}}
    .pager button,.pager input,.pager select{{height:32px;border:1px solid #c9d5e3;border-radius:8px;background:#fff;font-weight:800;min-width:0}}
    .pager button{{padding:0;width:32px}}
    .pager input{{width:74px;text-align:center;padding:0 4px}}
    .pager select{{width:66px;padding:0 4px}}
    .table-wrap{{background:#fff;border:1px solid #d8e0ea;border-radius:10px;overflow:hidden}}
    table{{width:100%;border-collapse:collapse;table-layout:fixed}}
    thead th{{background:#e9eff7;text-align:left;padding:7px 8px;font-size:11px;text-transform:uppercase;border-bottom:1px solid #d8e0ea;height:34px}}
    tbody td{{padding:8px;border-bottom:1px solid #e3e9f0;vertical-align:middle;overflow-wrap:anywhere}}
    th:nth-child(1),td:nth-child(1){{width:31%}}
    th:nth-child(2),td:nth-child(2){{width:17%}}
    th:nth-child(3),td:nth-child(3){{width:13%}}
    th:nth-child(4),td:nth-child(4){{width:17%}}
    th:nth-child(5),td:nth-child(5){{width:8%}}
    th:nth-child(6),td:nth-child(6){{width:14%}}
    tr.summary{{cursor:pointer}}
    tr.summary:hover{{background:#f8fafc}}
    .supplier-name{{font-weight:900;font-size:13px;letter-spacing:.1px}}
    .supplier-meta{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:5px;color:#475569}}
    .company{{display:inline-flex;align-items:center;height:18px;border-radius:5px;color:#fff;font-weight:800;font-size:10px;padding:0 6px}}
    .ideal{{background:#2563eb}} .pomme{{background:#dc2626}} .melhor{{background:#16a34a}}
    .tag,.pill{{display:inline-flex;align-items:center;justify-content:center;height:22px;border-radius:999px;padding:0 8px;font-weight:800;font-size:11px;line-height:1.1;white-space:nowrap}}
    .green{{background:#dcfce7;color:#166534}} .yellow{{background:#fef3c7;color:#92400e}} .red{{background:#fee2e2;color:#991b1b}} .blue{{background:#dbeafe;color:#1d4ed8}} .gray{{background:#e5e7eb;color:#334155}}
    .abc-high{{background:#dbeafe;color:#1d4ed8}} .abc-mid{{background:#fef3c7;color:#92400e}} .abc-low{{background:#ffedd5;color:#9a3412}} .abc-none{{background:#e5e7eb;color:#334155}}
    .muted{{color:#64748b;font-size:11px;margin-top:4px}}
    .copy-doc{{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border:1px solid #bfdbfe;border-radius:999px;background:#eff6ff;color:#1d4ed8;font-size:11px;cursor:pointer}}
    .copy-doc.copied{{background:#dcfce7;color:#166534;border-color:#86efac}}
    .detail td{{padding:0;background:#fbfdff}}
    .detail-grid{{display:grid;grid-template-columns:1.25fr 1.25fr 1fr 1fr;gap:10px;padding:10px;border-top:1px solid #d8e0ea}}
    .panel{{background:#fff;border:1px solid #dbe2eb;border-radius:9px;padding:10px;min-height:220px}}
    .panel h3{{margin:0 0 7px;font-size:12px;color:#111827}}
    .kv{{display:grid;grid-template-columns:96px minmax(0,1fr);gap:5px;margin:3px 0;line-height:1.32}}
    .kv b{{color:#334155}}
    .check{{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:999px;background:#dbeafe;color:#1d4ed8;font-weight:900;font-size:10px;margin-left:5px;vertical-align:middle}}
    .email-chip{{display:inline-flex;max-width:100%;padding:2px 6px;border-radius:999px;background:#f1f5f9;color:#334155;font-size:11px;margin:1px 3px 1px 0;overflow-wrap:anywhere}}
    .sortable{{cursor:pointer;user-select:none}}
    .sort-icon{{font-size:11px;margin-left:5px;color:#64748b}}
    .modal{{position:fixed;inset:0;background:rgba(15,23,42,.45);display:none;align-items:center;justify-content:center;z-index:9999;padding:24px}}
    .modal.open{{display:flex}}
    .modal-card{{background:#fff;border-radius:14px;max-width:920px;width:100%;max-height:86vh;overflow:auto;padding:24px;box-shadow:0 24px 80px rgba(15,23,42,.35)}}
    .modal-card h2{{margin:0 0 10px;font-size:24px}}
    .modal-card p,.modal-card li{{line-height:1.5}}
    .close{{float:right;border:1px solid #cbd5e1;border-radius:9px;background:#fff;width:38px;height:34px;font-weight:900;cursor:pointer}}
    @media (max-width:1100px){{.detail-grid{{grid-template-columns:1fr 1fr}}}}
  </style>
</head>
<body>
<div class="page">
  <div class="top">
    <h1>Painel de Fornecedores</h1>
    <input class="search" id="search" placeholder="Buscar por codigo, CNPJ, nome, email, cidade">
    <button class="method" id="methodBtn" title="Metodologia">?</button>
  </div>
  <div class="filters" id="filters"></div>
  <div class="kpis">
    <div class="card"><b>Registros</b><strong id="kpiRows">0</strong></div>
    <div class="card"><b>Alto credito</b><strong id="kpiHigh">0</strong></div>
    <div class="card"><b>Condicionado</b><strong id="kpiCond">0</strong></div>
    <div class="card"><b>Pendentes</b><strong id="kpiPending">0</strong></div>
    <div class="card"><b>Com inclusao</b><strong id="kpiIncl">0</strong></div>
    <div class="card"><b>Paginacao</b><div class="pager">
      <button id="first">|◀</button><button id="prev">◀</button><input id="pageNo" value="1"><span id="pageTotal">/1</span><button id="next">▶</button><button id="last">▶|</button><select id="pageSize"><option>10</option><option selected>20</option><option>30</option><option>50</option><option>100</option></select>
    </div></div>
  </div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Fornecedor</th>
          <th class="sortable" data-sort="regime">Regime fiscal <span class="sort-icon">↕</span></th>
          <th class="sortable" data-sort="credito">Credito 2027 <span class="sort-icon">↕</span></th>
          <th>Inclusoes</th>
          <th class="sortable" data-sort="abc">ABC <span class="sort-icon">↕</span></th>
          <th class="sortable" data-sort="valor">Valor <span class="sort-icon">↕</span></th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>
<div class="modal" id="methodModal">
  <div class="modal-card">
    <button class="close" id="closeMethod">x</button>
    <h2>Metodologia fiscal do painel 08</h2>
    <p>O painel classifica cada fornecedor PJ/CNPJ em MEI, Simples, Nao Simples ou Indeterminado. A regra sempre preserva a origem da evidencia.</p>
    <ol>
      <li>Primeiro usa OpenCNPJ: opcao MEI, opcao Simples ou Nao Simples.</li>
      <li>Se OpenCNPJ nao trouxer regime, consulta Minha Receita ou BrasilAPI.</li>
      <li>Se vier MEI=true, classifica como MEI.</li>
      <li>Se vier Simples=true, classifica como Simples.</li>
      <li>Se vier Simples=false, classifica como Nao Simples.</li>
      <li>Se as flags vierem vazias, mas houver Lucro Real, Lucro Presumido ou regime anual equivalente, classifica como Nao Simples, mantendo a origem como regime tributario.</li>
      <li>Sem qualquer evidencia fiscal, permanece Indeterminado.</li>
    </ol>
    <p>Para credito 2027: Nao Simples tende a alto potencial; Simples e condicionado; MEI e baixo; casos imunes/isentos ou PF exigem validacao; indeterminados ficam pendentes.</p>
  </div>
</div>
<script>
const DATA = {data_json};
const SUMMARY = {summary_json};
const filterDefs = [
  ['empresa','Empresa',['IDEAL','MELHOR','POMME']],
  ['uf','UF',null],
  ['movimento','Movimento',['Com movimento','Sem movimento']],
  ['curva','Curva',['AAA','AA','A','B','BB','C','CC','CCC','Sem curva']],
    ['regime','Regime fiscal',['Nao Simples','Simples','MEI','Indeterminado','Nao aplicavel']],
  ['credito','Credito 2027',['Alto','Condicionado','Baixo','Presumido','Validar','Pendente']],
  ['origem','Origem fiscal',['OpenCNPJ','Minha Receita','BrasilAPI','Regime tributario','Sem evidencia','Nao aplicavel']],
  ['inclusao','Inclusoes',['Com inclusao','Sem inclusao']],
  ['campo','Campo incluido',null],
];
const state = {{filters: {{}}, search:'', page:1, size:20, sort:'abc', dir:'asc', open:null}};
const els = {{}};
function safe(v){{return String(v ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));}}
function fmt(n){{return Number(n||0).toLocaleString('pt-BR');}}
function rowEmpresa(row){{return Array.isArray(row.empresas_lista) && row.empresas_lista.length ? row.empresas_lista : String(row.empresas_label||'').split(';').filter(Boolean);}}
function rowCampo(row){{return Array.isArray(row.campos_incluidos_lista) ? row.campos_incluidos_lista : String(row.campos_incluidos_label||'').split(';').filter(Boolean);}}
function unique(arr){{return [...new Set(arr.filter(Boolean))].sort((a,b)=>a.localeCompare(b,'pt-BR'));}}
function optionsFor(key, preset){{
  if (preset) return preset;
  if (key==='uf') return unique(DATA.map(r=>r.endereco_uf || r.uf_label || 'Sem UF'));
  if (key==='campo') return unique(DATA.flatMap(rowCampo));
  return [];
}}
function labelFor(filter, value){{
  if (filter==='uf' && !value) return 'Sem UF';
  return value || 'Sem dado';
}}
function initFilters(){{
  const root=document.getElementById('filters');
  filterDefs.forEach(([key,title,preset])=>{{
    const opts=optionsFor(key,preset);
    state.filters[key]=new Set(opts);
    const div=document.createElement('div'); div.className='filter'; div.dataset.key=key;
    div.innerHTML=`<label>${{title}}</label><button type="button" class="filterBtn">Todos</button><div class="menu"></div>`;
    const menu=div.querySelector('.menu');
    menu.innerHTML = `<label><input type="checkbox" data-all="1" checked> TODOS</label>` + opts.map(opt=>`<label><input type="checkbox" value="${{safe(opt)}}" checked> ${{safe(labelFor(key,opt))}}</label>`).join('');
    root.appendChild(div);
    div.querySelector('.filterBtn').addEventListener('click',()=>{{document.querySelectorAll('.filter.open').forEach(x=>{{if(x!==div)x.classList.remove('open')}});div.classList.toggle('open');}});
    menu.addEventListener('change', e=>{{
      const boxes=[...menu.querySelectorAll('input:not([data-all])')];
      const all=menu.querySelector('input[data-all]');
      if(e.target.dataset.all){{
        boxes.forEach(b=>b.checked=e.target.checked);
      }} else {{
        all.checked=boxes.every(b=>b.checked);
      }}
      state.filters[key]=new Set(boxes.filter(b=>b.checked).map(b=>b.value));
      state.page=1; updateFilterLabel(div,key,opts); render();
    }});
    updateFilterLabel(div,key,opts);
  }});
  document.addEventListener('click', e=>{{if(!e.target.closest('.filter')) document.querySelectorAll('.filter.open').forEach(x=>x.classList.remove('open'));}});
}}
function updateFilterLabel(div,key,opts){{
  const btn=div.querySelector('.filterBtn'); const selected=state.filters[key]||new Set();
  if(selected.size===opts.length){{btn.textContent='Todos';div.classList.remove('active');}}
  else if(selected.size===0){{btn.textContent='Nenhum';div.classList.add('active');}}
  else {{btn.textContent=`${{selected.size}} selecionados`;div.classList.add('active');}}
}}
function companyTags(row){{
  return rowEmpresa(row).map(c=>`<span class="company ${{c.toLowerCase()}}">${{safe(c)}}</span>`).join('');
}}
function copyButton(row){{
  const doc=String(row.documento||row.chave||'').replace(/\\D/g,'');
  return doc ? `<button type="button" class="copy-doc" data-doc="${{doc}}" title="Copiar numeros">⧉</button>` : '';
}}
function docBlock(row){{return `<span>${{safe(row.documento_formatado||row.documento||'')}}</span>${{copyButton(row)}}`;}}
function tagClass(value){{
  const v=String(value||'').toLowerCase();
  if(v.includes('alto')||v.includes('nao simples')) return 'green';
  if(v.includes('inferido')||v.includes('presumido')) return 'blue';
  if(v.includes('condicionado')||v.includes('simples')) return 'yellow';
  if(v.includes('mei')||v.includes('baixo')) return 'red';
  return 'gray';
}}
function abcClass(value){{
  if(['AAA','AA','A'].includes(String(value||''))) return 'abc-high';
  if(['B','BB'].includes(String(value||''))) return 'abc-mid';
  if(['C','CC','CCC'].includes(String(value||''))) return 'abc-low';
  return 'abc-none';
}}
function check(flag){{return flag==='S' ? '<span class="check">✓</span>' : '';}}
function valueWithCheck(value, flag){{return `${{safe(value||'Sem dado')}}${{check(flag)}}`;}}
function emails(value, flag){{
  const parts=String(value||'').toLowerCase().split(/[;|,\\s]+/).map(x=>x.trim()).filter(Boolean);
  const body=parts.length ? [...new Set(parts)].map(e=>`<span class="email-chip">${{safe(e)}}</span>`).join('') : 'Sem dado';
  return body + check(flag);
}}
function phoneFormat(value){{
  const parts=String(value||'').split(/[;|,/]+/).map(v=>v.replace(/\\D/g,'')).filter(Boolean).map(d=>{{
    if(d.startsWith('55') && d.length>11) d=d.slice(2);
    if(d.length===11) return `(${{d.slice(0,2)}}) ${{d.slice(2,7)}}-${{d.slice(7)}}`;
    if(d.length===10) return `(${{d.slice(0,2)}}) ${{d.slice(2,6)}}-${{d.slice(6)}}`;
    return d;
  }});
  return parts.length ? [...new Set(parts)].join('; ') : 'Sem dado';
}}
function cadastroPanel(row){{
  return `<div class="panel"><h3>Cadastro</h3>
    <div class="kv"><b>Razao</b><span>${{safe(row.razao_original||row.razao_social_oficial||'Sem dado')}}</span></div>
    <div class="kv"><b>Fantasia</b><span>${{safe(row.fantasia_original||row.nome_fantasia_oficial||'Sem dado')}}</span></div>
    <div class="kv"><b>Situacao</b><span>${{safe(row.status_interno_label||row.situacao_cadastral_oficial||'Sem dado')}}</span></div>
    <div class="kv"><b>CNPJ/CPF</b><span>${{docBlock(row)}}</span></div>
    <div class="kv"><b>IE</b><span>${{safe(row.ie_original||'Sem dado')}}</span></div>
    <div class="kv"><b>IM</b><span>${{safe(row.im_original||'Sem dado')}}</span></div>
    <div class="kv"><b>Porte</b><span>${{valueWithCheck(row.porte_empresa,'S')}}</span></div>
    <div class="kv"><b>Natureza</b><span>${{valueWithCheck(row.natureza_juridica,'S')}}</span></div>
  </div>`;
}}
function enderecoPanel(row){{
  return `<div class="panel"><h3>Endereco</h3>
    <div class="kv"><b>Endereco</b><span>${{valueWithCheck(row.endereco_completo,row.endereco_opencnpj_incluido)}}</span></div>
    <div class="kv"><b>Cidade</b><span>${{valueWithCheck(row.endereco_municipio,row.cidade_opencnpj_incluida)}}</span></div>
    <div class="kv"><b>UF</b><span>${{valueWithCheck(row.endereco_uf,row.uf_opencnpj_incluida)}}</span></div>
    <div class="kv"><b>Telefones</b><span>${{phoneFormat(row.telefones_oficiais)}}${{check(row.telefone_opencnpj_incluido)}}</span></div>
    <div class="kv"><b>Emails</b><span>${{emails(row.email_endereco_display||row.emails_originais,row.email_opencnpj_incluido)}}</span></div>
    <div class="kv"><b>Origem</b><span>${{safe(row.endereco_preferencial_origem||'Cadastro atual')}}</span></div>
  </div>`;
}}
function fiscalPanel(row){{
  return `<div class="panel"><h3>Fiscal</h3>
    <div class="kv"><b>Regime</b><span><span class="tag ${{tagClass(row.regime_08)}}">${{safe(row.regime_08)}}</span></span></div>
    <div class="kv"><b>Credito</b><span><span class="tag ${{tagClass(row.credito_2027_08)}}">${{safe(row.credito_2027_08)}}</span></span></div>
    <div class="kv"><b>Origem</b><span>${{safe(row.origem_fiscal_08)}}</span></div>
    <div class="kv"><b>Fonte</b><span>${{safe(row.fonte_fiscal_08)}}</span></div>
    <div class="kv"><b>Evidencia</b><span>${{safe(row.evidencia_fiscal_08||row.criterio_fiscal_08||'Sem evidencia')}}</span></div>
    <div class="kv"><b>Ano</b><span>${{safe(row.ano_evidencia_fiscal_08||'Sem ano')}}</span></div>
    <div class="kv"><b>Status</b><span>${{safe(row.status_consulta_fiscal_08)}}</span></div>
  </div>`;
}}
function operacaoPanel(row){{
  return `<div class="panel"><h3>Operacao</h3>
    <div class="kv"><b>Curva</b><span><span class="tag ${{abcClass(row.curva_label)}}">${{safe(row.curva_label||'Sem curva')}}</span> | posicao ${{safe(row.curva_posicao||'-')}}</span></div>
    <div class="kv"><b>Total</b><span>${{safe(row.valor_referencia_fmt||row.curva_valor_fmt||row.nfe_valor_fmt)}}</span></div>
    <div class="kv"><b>NFe</b><span>${{safe(row.nfe_linhas||0)}} Notas</span></div>
    <div class="kv"><b>UFs</b><span>${{safe(row.nfe_ufs||row.endereco_uf||'Sem UF')}}</span></div>
    <div class="kv"><b>Anos</b><span>${{safe(row.nfe_anos||'Sem movimento')}}</span></div>
  </div>`;
}}
function detailRow(row){{
  return `<tr class="detail"><td colspan="6"><div class="detail-grid">${{cadastroPanel(row)}}${{enderecoPanel(row)}}${{fiscalPanel(row)}}${{operacaoPanel(row)}}</div></td></tr>`;
}}
function rowMatches(row){{
  const search=state.search;
  if(search){{
    const hay=[row.nome_exibicao,row.razao_original,row.fantasia_original,row.documento,row.documento_formatado,row.email_endereco_display,row.emails_originais,row.endereco_municipio,row.endereco_uf].join(' ').toLowerCase();
    if(!hay.includes(search)) return false;
  }}
  const checks=[
    ['empresa', rowEmpresa(row)],
    ['uf', [row.endereco_uf||row.uf_label||'Sem UF']],
    ['movimento', [row.movimento_label]],
    ['curva', [row.curva_label]],
    ['regime', [row.regime_08]],
    ['credito', [row.credito_2027_08]],
    ['origem', [row.origem_fiscal_08]],
    ['inclusao', [row.inclusao_status_08]],
    ['campo', rowCampo(row)],
  ];
  return checks.every(([key,vals])=>{{
    const selected=state.filters[key]; if(!selected || !selected.size) return false;
    if(key==='campo' && vals.length===0) return selected.size===optionsFor('campo').length;
    return vals.some(v=>selected.has(v));
  }});
}}
function sortRows(rows){{
  const dir=state.dir==='asc'?1:-1;
  return rows.sort((a,b)=>{{
    let av,bv;
    if(state.sort==='valor'){{av=Number(a.valor_referencia||0);bv=Number(b.valor_referencia||0);}}
    else if(state.sort==='abc'){{av=Number(a.sort_curva_rank||99);bv=Number(b.sort_curva_rank||99); return (av-bv)*dir || (Number(b.valor_referencia||0)-Number(a.valor_referencia||0));}}
    else if(state.sort==='regime'){{av=Number(a.regime_ordem||99);bv=Number(b.regime_ordem||99); return (av-bv)*dir;}}
    else if(state.sort==='credito'){{av=Number(a.credito_2027_ordem||99);bv=Number(b.credito_2027_ordem||99); return (av-bv)*dir;}}
    return (av-bv)*dir;
  }});
}}
function render(){{
  let rows=sortRows(DATA.filter(rowMatches));
  const totalPages=Math.max(1,Math.ceil(rows.length/state.size));
  if(state.page>totalPages) state.page=totalPages;
  document.getElementById('kpiRows').textContent=fmt(rows.length);
  document.getElementById('kpiHigh').textContent=fmt(rows.filter(r=>r.credito_2027_08==='Alto').length);
  document.getElementById('kpiCond').textContent=fmt(rows.filter(r=>r.credito_2027_08==='Condicionado').length);
  document.getElementById('kpiPending').textContent=fmt(rows.filter(r=>r.regime_08==='Indeterminado').length);
  document.getElementById('kpiIncl').textContent=fmt(rows.filter(r=>r.inclusao_status_08==='Com inclusao').length);
  document.getElementById('pageNo').value=state.page; document.getElementById('pageTotal').textContent='/' + totalPages;
  const start=(state.page-1)*state.size; const pageRows=rows.slice(start,start+state.size);
  const body=document.getElementById('tbody');
  body.innerHTML=pageRows.map(row=>{{
    const key=safe(row.row_key||row.documento);
    const main=`<tr class="summary" data-key="${{key}}">
      <td><div class="supplier-name">${{safe(row.nome_exibicao)}}</div><div class="supplier-meta">${{companyTags(row)}}<span>${{safe(row.documento_formatado)}}</span>${{copyButton(row)}}</div></td>
      <td><span class="tag ${{tagClass(row.regime_08)}}">${{safe(row.regime_08)}}</span></td>
      <td><span class="tag ${{tagClass(row.credito_2027_08)}}">${{safe(row.credito_2027_08)}}</span></td>
      <td>${{safe(row.inclusoes_resumo_08)}}<div class="muted">${{safe(row.campos_incluidos_label||'')}}</div></td>
      <td><span class="tag ${{abcClass(row.curva_label)}}">${{safe(row.curva_label)}}</span></td>
      <td>${{safe(row.valor_referencia_fmt)}}<div class="muted">${{safe(row.nfe_linhas||0)}} Notas</div></td>
    </tr>`;
    return state.open===key ? main + detailRow(row) : main;
  }}).join('');
  body.querySelectorAll('tr.summary').forEach(tr=>tr.addEventListener('click',()=>{{state.open = state.open===tr.dataset.key ? null : tr.dataset.key; render();}}));
  body.querySelectorAll('.copy-doc').forEach(btn=>btn.addEventListener('click', async e=>{{e.stopPropagation(); try{{await navigator.clipboard.writeText(btn.dataset.doc||'');btn.classList.add('copied');btn.textContent='✓';setTimeout(()=>{{btn.classList.remove('copied');btn.textContent='⧉';}},900);}}catch(err){{}} }}));
}}
initFilters();
document.getElementById('search').addEventListener('input',e=>{{state.search=e.target.value.toLowerCase().trim();state.page=1;render();}});
document.getElementById('pageSize').addEventListener('change',e=>{{state.size=Number(e.target.value);state.page=1;render();}});
document.getElementById('pageNo').addEventListener('change',e=>{{state.page=Math.max(1,Number(e.target.value)||1);render();}});
document.getElementById('first').onclick=()=>{{state.page=1;render();}};
document.getElementById('prev').onclick=()=>{{state.page=Math.max(1,state.page-1);render();}};
document.getElementById('next').onclick=()=>{{state.page=state.page+1;render();}};
document.getElementById('last').onclick=()=>{{state.page=999999;render();}};
document.querySelectorAll('.sortable').forEach(th=>th.addEventListener('click',()=>{{const s=th.dataset.sort;if(state.sort===s) state.dir=state.dir==='asc'?'desc':'asc'; else {{state.sort=s;state.dir=s==='valor'?'desc':'asc';}} render();}}));
document.getElementById('methodBtn').onclick=()=>document.getElementById('methodModal').classList.add('open');
document.getElementById('closeMethod').onclick=()=>document.getElementById('methodModal').classList.remove('open');
document.getElementById('methodModal').addEventListener('click',e=>{{if(e.target.id==='methodModal') e.currentTarget.classList.remove('open');}});
render();
</script>
</body>
</html>
"""
    HTML_FILE.write_text(html_text, encoding="utf-8")


def build_summary(rows: list[dict[str, Any]], resolved: list[dict[str, Any]], inclusion_records: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "versao": "08",
        "base": str(INPUT_07.relative_to(BASE_DIR)),
        "registros": len(rows),
        "regime_08": dict(Counter(row.get("regime_08") for row in rows)),
        "credito_2027_08": dict(Counter(row.get("credito_2027_08") for row in rows)),
        "origem_fiscal_08": dict(Counter(row.get("origem_fiscal_08") for row in rows)),
        "status_consulta_fiscal_08": dict(Counter(row.get("status_consulta_fiscal_08") for row in rows)),
        "fornecedores_com_inclusao": sum(1 for row in rows if row.get("inclusao_status_08") == "Com inclusao"),
        "inclusoes_total_linhas": len(inclusion_records),
        "outputs": [
            str(OUT_00_SUMMARY.relative_to(BASE_DIR)),
            str(OUT_01_BASE.relative_to(BASE_DIR)),
            str(OUT_02_PENDING_BEFORE.relative_to(BASE_DIR)),
            str(OUT_03_RESOLVED.relative_to(BASE_DIR)),
            str(OUT_04_AUDIT.relative_to(BASE_DIR)),
            str(OUT_05_INCLUSIONS.relative_to(BASE_DIR)),
            str(OUT_06_PENDING_AFTER.relative_to(BASE_DIR)),
            str(HTML_FILE.relative_to(BASE_DIR)),
        ],
    }


def update_diary(summary: dict[str, Any]) -> None:
    diary = BASE_DIR / "docs" / "DIARIO_DE_BORDO.md"
    entry = f"""

#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `{summary['registros']}`.
- Distribuicao de regime `08`: `{summary['regime_08']}`.
- Distribuicao de credito 2027: `{summary['credito_2027_08']}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `{summary['fornecedores_com_inclusao']}`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.
"""
    with diary.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera output 08 simplificado com foco em regime fiscal.")
    parser.add_argument("--workers", type=int, default=4, help="Numero de consultas paralelas para fonte fiscal complementar.")
    parser.add_argument("--source", choices=["minhareceita", "brasilapi"], default="minhareceita")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)

    print("Lendo base 07...", flush=True)
    rows_07 = read_csv(INPUT_07)
    write_csv(OUT_01_BASE, rows_07)

    pending_before = [
        {
            "documento": digits(row.get("documento")),
            "fornecedor": row.get("nome_exibicao") or row.get("razao_original"),
            "empresa": row.get("empresas_label") or row.get("empresa"),
            "regime_anterior": row.get("regime_label"),
            "valor_referencia": max(as_float(row.get("sort_curva_valor")), as_float(row.get("sort_nfe_valor"))),
            "valor_referencia_fmt": money(max(as_float(row.get("sort_curva_valor")), as_float(row.get("sort_nfe_valor")))),
        }
        for row in rows_07
        if len(digits(row.get("documento"))) == 14 and not classify_from_opencnpj(row)
    ]
    pending_before.sort(key=lambda row: -as_float(row.get("valor_referencia")))
    write_csv(OUT_02_PENDING_BEFORE, pending_before)

    print(f"CNPJs pendentes para fonte complementar: {len({row['documento'] for row in pending_before})}", flush=True)
    regime_records = resolve_complementary_regimes(rows_07, workers=args.workers, primary_source=args.source)

    print("Montando base 08...", flush=True)
    rows_08, resolved_records, inclusion_records = build_rows(rows_07, regime_records)
    pending_after = [row for row in resolved_records if row.get("regime_08") == "Indeterminado"]

    write_csv(OUT_03_RESOLVED, resolved_records)
    write_csv(OUT_04_AUDIT, rows_08)
    write_csv(OUT_05_INCLUSIONS, inclusion_records)
    write_csv(OUT_06_PENDING_AFTER, pending_after)

    summary = build_summary(rows_08, resolved_records, inclusion_records)
    OUT_00_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Gerando HTML 08...", flush=True)
    build_html(rows_08, summary)
    update_diary(summary)

    print("Concluido.", flush=True)
    print(f"HTML: {HTML_FILE}", flush=True)
    print(f"CSV: {OUT_04_AUDIT}", flush=True)
    print(f"Resumo: {OUT_00_SUMMARY}", flush=True)
    print(f"Registros: {len(rows_08)}", flush=True)


if __name__ == "__main__":
    main()
