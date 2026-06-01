"""Extrai as fontes de dados do workspace SUPRIMENTOS para data/raw/.

Lê pipeline/sources.yml, verifica o manifest e baixa apenas o que estiver
desatualizado. Usa a Bulk API assíncrona do Zoho em lotes.

Uso:
  python pipeline/extract.py --env-file zoho/zoho.env
  python pipeline/extract.py --env-file zoho/zoho.env --force
  python pipeline/extract.py --env-file zoho/zoho.env --source nfe
  python pipeline/extract.py --env-file zoho/zoho.env --max-age 48
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zoho.client import ZohoClient, ZohoConfig, ZohoError, load_env_file

SOURCES_FILE = ROOT / "pipeline" / "sources.yml"
RAW_DIR = ROOT / "data" / "raw"
MANIFEST_FILE = RAW_DIR / "manifest.json"

BATCH_SIZE = 4       # jobs simultâneos
JOB_INTERVAL = 8    # segundos entre polls
JOB_MAX_ATTEMPTS = 90


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def _load_manifest() -> dict[str, Any]:
    if MANIFEST_FILE.exists():
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    return {}


def _save_manifest(manifest: dict[str, Any]) -> None:
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _is_stale(source_id: str, manifest: dict[str, Any], max_age_hours: float) -> bool:
    """Retorna True se a fonte precisa ser atualizada."""
    entry = manifest.get(source_id)
    if not entry or entry.get("status") != "ok":
        return True
    out_file = RAW_DIR / entry.get("file", "")
    if not out_file.exists():
        return True
    extracted_at = entry.get("extracted_at", "")
    if not extracted_at:
        return True
    try:
        ts = datetime.fromisoformat(extracted_at).replace(tzinfo=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        return age_hours >= max_age_hours
    except ValueError:
        return True


# ---------------------------------------------------------------------------
# Extração em lote
# ---------------------------------------------------------------------------

def _count_csv_rows(path: Path) -> int:
    try:
        with path.open(encoding="utf-8-sig") as f:
            return sum(1 for _ in csv.reader(f)) - 1  # subtrai cabeçalho
    except Exception:
        return -1


def _extract_batch(
    client: ZohoClient,
    token: str,
    batch: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cria jobs para um lote, aguarda todos e baixa. Retorna resultados."""
    results: dict[str, Any] = {}

    # 1. Criar todos os jobs
    jobs: dict[str, str] = {}  # source_id -> job_id
    for source in batch:
        sid = source["id"]
        zoho_name = source["zoho_name"]
        sql = f'select * from "{zoho_name}"'
        try:
            job_id = client.create_job_sql(sql, token)
            jobs[sid] = job_id
            print(f"    Job criado: {sid} -> {job_id}")
        except ZohoError as exc:
            print(f"    ERRO ao criar job {sid}: {exc}")
            results[sid] = {"status": "error", "error": str(exc)}

    if not jobs:
        return results

    # 2. Polling de todos os jobs até completarem
    pending = dict(jobs)
    completed: dict[str, str] = {}
    failed: dict[str, str] = {}

    for attempt in range(1, JOB_MAX_ATTEMPTS + 1):
        if not pending:
            break
        still_pending: dict[str, str] = {}
        for sid, job_id in pending.items():
            try:
                status_data = client.job_status(job_id, token)
                payload = status_data.get("data") if isinstance(status_data.get("data"), dict) else {}
                code = str(payload.get("jobCode", ""))
                if code == "1004":
                    completed[sid] = job_id
                elif code in {"1003", "1005"}:
                    failed[sid] = f"jobCode={code}"
                else:
                    still_pending[sid] = job_id
            except ZohoError as exc:
                still_pending[sid] = job_id
                if attempt % 5 == 0:
                    print(f"    Polling {sid}: {exc}")

        pending = still_pending
        if pending:
            print(f"    Aguardando ({attempt}/{JOB_MAX_ATTEMPTS}): {list(pending.keys())}", end="\r", flush=True)
            time.sleep(JOB_INTERVAL)

    if pending:
        for sid in pending:
            failed[sid] = "timeout"
    if completed or failed:
        print()  # limpa linha do \r

    # 3. Marcar falhas
    for sid, reason in failed.items():
        print(f"    FALHOU: {sid} — {reason}")
        results[sid] = {"status": "error", "error": reason}

    # 4. Baixar completados
    for sid, job_id in completed.items():
        source = next(s for s in batch if s["id"] == sid)
        out_file = RAW_DIR / f"{sid}.csv"
        try:
            client.download_job(job_id, out_file, token)
            rows = _count_csv_rows(out_file)
            print(f"    OK: {sid} -> {out_file.name} ({rows:,} linhas)")
            results[sid] = {
                "status": "ok",
                "file": f"{sid}.csv",
                "rows": rows,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "zoho_name": source["zoho_name"],
            }
        except ZohoError as exc:
            print(f"    ERRO ao baixar {sid}: {exc}")
            results[sid] = {"status": "error", "error": str(exc)}

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extrai fontes do Zoho para data/raw/")
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--force", action="store_true", help="Ignora cache e baixa tudo.")
    parser.add_argument("--source", help="Extrai apenas uma fonte pelo ID (ex: nfe).")
    parser.add_argument("--max-age", type=float, default=None, help="Override de max_age_hours.")
    args = parser.parse_args(argv)

    load_env_file(args.env_file)
    client = ZohoClient(ZohoConfig.from_env())
    token = client.refresh_token()
    print("Token OK.")

    # Carregar definições
    config = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8"))
    default_max_age = config.get("defaults", {}).get("max_age_hours", 24)
    all_sources: list[dict[str, Any]] = config.get("sources", [])

    # Filtrar por --source se informado
    if args.source:
        all_sources = [s for s in all_sources if s["id"] == args.source]
        if not all_sources:
            print(f"ERRO: fonte '{args.source}' não encontrada em sources.yml.", file=sys.stderr)
            return 1

    # Verificar quais precisam de atualização
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()

    to_extract: list[dict[str, Any]] = []
    skipped: list[str] = []

    for source in all_sources:
        sid = source["id"]
        max_age = args.max_age if args.max_age is not None else source.get("max_age_hours", default_max_age)

        if args.force or _is_stale(sid, manifest, max_age):
            to_extract.append(source)
        else:
            skipped.append(sid)

    if skipped:
        print(f"Pulando {len(skipped)} fontes atualizadas: {', '.join(skipped)}")

    if not to_extract:
        print("Nenhuma fonte desatualizada. Use --force para forçar.")
        return 0

    print(f"\nExtraindo {len(to_extract)} fontes em lotes de {BATCH_SIZE}...\n")

    # Processar em lotes
    total_ok = 0
    total_err = 0

    for i in range(0, len(to_extract), BATCH_SIZE):
        batch = to_extract[i:i + BATCH_SIZE]
        nomes = [s["id"] for s in batch]
        print(f"  Lote {i // BATCH_SIZE + 1}: {nomes}")

        results = _extract_batch(client, token, batch)

        # Atualizar manifest
        for sid, result in results.items():
            manifest[sid] = result
            if result["status"] == "ok":
                total_ok += 1
            else:
                total_err += 1

        _save_manifest(manifest)
        print()

    # Resumo final
    print(f"Concluído: {total_ok} OK, {total_err} erro(s).")
    print(f"Manifest: {MANIFEST_FILE}")

    return 0 if total_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
