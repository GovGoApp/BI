from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = BASE_DIR / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from zoho_analytics_client import ZohoAnalyticsClient, ZohoAnalyticsConfig, load_env_file  # noqa: E402


INVENTORY_CSV = BASE_DIR / "output" / "zoho_analytics_inventory" / "zoho_views_inventory.csv"
OUT_DIR = BASE_DIR / "output" / "suprimentos_profile"
SAMPLES_DIR = OUT_DIR / "samples"
PROFILE_JSON = OUT_DIR / "suprimentos_sources_profile.json"
PROFILE_CSV = OUT_DIR / "suprimentos_sources_profile.csv"
PROFILE_MD = BASE_DIR / "docs" / "PERFIL_DADOS_SUPRIMENTOS.md"


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def slug(value: str) -> str:
    text = clean(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "sem_nome"


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def read_inventory() -> list[dict[str, str]]:
    with INVENTORY_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        row
        for row in rows
        if row.get("workspace_name") == "SUPRIMENTOS" and row.get("view_type") in {"Table", "QueryTable"}
    ]


def read_csv_header(path: Path) -> tuple[list[str], int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        row_count = sum(1 for _ in reader)
    return header, row_count


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "view_type",
        "view_id",
        "view_name",
        "status",
        "sample_rows",
        "column_count",
        "columns",
        "sample_file",
        "job_id",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["columns"] = "; ".join(row.get("columns", []))
            writer.writerow(out)


def write_markdown(path: Path, profile: dict[str, Any]) -> None:
    rows = profile["sources"]
    ok = [row for row in rows if row["status"] == "ok"]
    failed = [row for row in rows if row["status"] != "ok"]
    lines = [
        "# Perfil de dados - SUPRIMENTOS",
        "",
        f"Gerado em: `{profile['generated_at']}`.",
        "",
        "Este perfil foi criado a partir de amostras pequenas (`limit 5`) das fontes `Table` e `QueryTable` do workspace `SUPRIMENTOS`.",
        "",
        "Arquivos tecnicos:",
        "",
        f"- `{PROFILE_JSON.relative_to(BASE_DIR)}`",
        f"- `{PROFILE_CSV.relative_to(BASE_DIR)}`",
        f"- `{SAMPLES_DIR.relative_to(BASE_DIR)}/`",
        "",
        "## Resumo",
        "",
        f"- Fontes analisadas: `{len(rows)}`.",
        f"- Fontes com amostra OK: `{len(ok)}`.",
        f"- Fontes com erro de amostra: `{len(failed)}`.",
        "",
        "## Fontes por dominio inferido",
        "",
    ]

    by_domain: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_domain.setdefault(row["domain"], []).append(row)
    for domain, items in sorted(by_domain.items()):
        lines.append(f"### {domain}")
        lines.append("")
        lines.append("| Tipo | Fonte | Colunas | Amostra | Status |")
        lines.append("|---|---|---:|---:|---|")
        for row in sorted(items, key=lambda item: (item["view_type"], item["view_name"])):
            lines.append(
                "| "
                + " | ".join(
                    [
                        clean(row["view_type"]),
                        clean(row["view_name"]).replace("|", "\\|"),
                        str(row["column_count"]),
                        str(row["sample_rows"]),
                        clean(row["status"]),
                    ]
                )
                + " |"
            )
        lines.append("")

    lines.extend(["## Dicionario preliminar por fonte", ""])
    for row in sorted(rows, key=lambda item: (item["domain"], item["view_type"], item["view_name"])):
        lines.append(f"### {clean(row['view_name'])}")
        lines.append("")
        lines.append(f"- Tipo: `{row['view_type']}`.")
        lines.append(f"- View ID: `{row['view_id']}`.")
        lines.append(f"- Dominio inferido: `{row['domain']}`.")
        lines.append(f"- Status da amostra: `{row['status']}`.")
        if row.get("sample_file"):
            lines.append(f"- Amostra: `{row['sample_file']}`.")
        if row.get("error"):
            lines.append(f"- Erro: `{clean(row['error'])}`.")
        lines.append("")
        if row.get("columns"):
            lines.append("| # | Coluna |")
            lines.append("|---:|---|")
            for index, column in enumerate(row["columns"], start=1):
                lines.append(f"| {index} | {clean(column).replace('|', '\\|')} |")
        else:
            lines.append("Sem colunas capturadas.")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def infer_domain(name: str) -> str:
    text = clean(name).upper()
    if text.startswith("NFE") or "ENTRADA DE NOTAS" in text or "NF COM ITENS" in text:
        return "Notas fiscais e itens"
    if text.startswith("CURVA"):
        return "Curva ABC e consumo"
    if text.startswith("COT") or "COTA" in text or "MIN COT" in text or text.startswith("NUM_COT"):
        return "Cotacoes"
    if text.startswith("PMP") or "INFLA" in text:
        return "Preco medio e inflacao"
    if text.startswith("CP") or "CONTAS A PAGAR" in text or "SALDO" in text:
        return "Contas a pagar"
    if text.startswith("AD") or "ADIANTAMENTO" in text or "NF ADT" in text:
        return "Adiantamentos"
    if text.startswith("FILIAIS"):
        return "Filiais e organizacao"
    if "DRO" in text or "FAT_SUP" in text or "TIPOCONTA" in text:
        return "Resultado/financeiro gerencial"
    if "FORN" in text:
        return "Fornecedores"
    if "PROD" in text or text == "TAB_PROD":
        return "Produtos"
    return "Outros"


def build_profile(env_file: Path, limit: int, interval: int, max_attempts: int) -> dict[str, Any]:
    load_env_file(env_file)
    config = ZohoAnalyticsConfig.from_env()
    client = ZohoAnalyticsClient(config)
    token = client.refresh_access_token()
    rows = read_inventory()
    rows.sort(key=lambda row: (row["view_type"], row["view_name"]))
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    sources: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        view_name = row["view_name"]
        view_type = row["view_type"]
        view_id = row["view_id"]
        file_name = f"{index:02d}_{view_type.lower()}_{slug(view_name)}.csv"
        sample_path = SAMPLES_DIR / file_name
        sql = f"select * from {quote_identifier(view_name)} limit {limit}"
        record: dict[str, Any] = {
            "view_type": view_type,
            "view_id": view_id,
            "view_name": view_name,
            "domain": infer_domain(view_name),
            "status": "erro",
            "sample_rows": 0,
            "column_count": 0,
            "columns": [],
            "sample_file": "",
            "job_id": "",
            "error": "",
        }
        print(f"[{index}/{len(rows)}] {view_type} | {view_name}", flush=True)
        try:
            job_id = client.create_export_job_for_sql(sql, access_token=token)
            record["job_id"] = job_id
            client.wait_for_export_job(job_id, access_token=token, interval_seconds=interval, max_attempts=max_attempts)
            client.download_export_job(job_id, sample_path, access_token=token)
            columns, sample_rows = read_csv_header(sample_path)
            record.update(
                {
                    "status": "ok",
                    "sample_rows": sample_rows,
                    "column_count": len(columns),
                    "columns": columns,
                    "sample_file": str(sample_path.relative_to(BASE_DIR)),
                }
            )
        except Exception as exc:
            record["error"] = f"{type(exc).__name__}: {exc}"
        sources.append(record)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "workspace": "SUPRIMENTOS",
        "limit": limit,
        "sources": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera perfil de colunas das fontes de dados do workspace SUPRIMENTOS.")
    parser.add_argument("--env-file", default="zoho.env")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--max-attempts", type=int, default=40)
    args = parser.parse_args()

    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = BASE_DIR / env_file

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    profile = build_profile(env_file, limit=args.limit, interval=args.interval, max_attempts=args.max_attempts)

    PROFILE_JSON.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(PROFILE_CSV, profile["sources"])
    write_markdown(PROFILE_MD, profile)

    ok = sum(1 for row in profile["sources"] if row["status"] == "ok")
    failed = len(profile["sources"]) - ok
    print(f"Fontes: {len(profile['sources'])}")
    print(f"OK: {ok}")
    print(f"Erros: {failed}")
    print(f"Markdown: {PROFILE_MD.relative_to(BASE_DIR)}")
    print(f"CSV: {PROFILE_CSV.relative_to(BASE_DIR)}")
    print(f"JSON: {PROFILE_JSON.relative_to(BASE_DIR)}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
