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

BATCH_SIZE = 2       # jobs simultâneos (Zoho limita ~4 concurrent; 2 é seguro)
JOB_INTERVAL = 8    # segundos entre polls
JOB_MAX_ATTEMPTS = 90
JOB_RETRY_WAIT = 40  # segundos de espera antes de retry em LIMIT_EXCEEDED
BAR_WIDTH = 30       # largura da barra de progresso


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

def _bar(done: int, total: int) -> str:
    """Barra de progresso ASCII. Ex: [==========----------] 10/18 (55%)"""
    pct = done / total if total else 0
    filled = int(BAR_WIDTH * pct)
    empty = BAR_WIDTH - filled
    return f"[{'=' * filled}{'-' * empty}] {done}/{total} ({int(pct * 100)}%)"


def _count_csv_rows(path: Path) -> int:
    """Conta linhas contando '\n' no binário — muito mais rápido que csv.reader."""
    try:
        with path.open("rb") as f:
            return f.read().count(b"\n") - 1  # subtrai cabeçalho
    except Exception:
        return -1


def _extract_batch(
    client: ZohoClient,
    token: str,
    batch: list[dict[str, Any]],
    global_done: int,
    global_total: int,
) -> dict[str, Any]:
    """Cria jobs para um lote, aguarda todos e baixa. Retorna resultados."""
    results: dict[str, Any] = {}

    # 1. Criar todos os jobs (com retry automático em LIMIT_EXCEEDED)
    jobs: dict[str, str] = {}  # source_id -> job_id
    for source in batch:
        sid = source["id"]
        zoho_name = source["zoho_name"]
        sql = f'select * from "{zoho_name}"'
        for tentativa in range(1, 4):  # até 3 tentativas
            try:
                job_id = client.create_job_sql(sql, token)
                jobs[sid] = job_id
                break
            except ZohoError as exc:
                if "ASYNC_EXPORT_LIMIT_EXCEEDED" in str(exc) and tentativa < 3:
                    print(f"  Limite de jobs atingido. Aguardando {JOB_RETRY_WAIT}s antes de tentar {sid} novamente...")
                    time.sleep(JOB_RETRY_WAIT)
                else:
                    print(f"  ERRO ao criar job {sid}: {exc}")
                    results[sid] = {"status": "error", "error": str(exc)}
                    break

    if not jobs:
        return results

    print(f"  Jobs criados: {list(jobs.keys())}")

    # 2. Polling até todos completarem
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
            except ZohoError:
                still_pending[sid] = job_id

        pending = still_pending
        if pending:
            done_in_batch = len(jobs) - len(pending)
            bar_batch = _bar(done_in_batch, len(jobs))
            bar_global = _bar(global_done, global_total)
            line = f"  Lote {bar_batch}  |  Total {bar_global}  |  aguardando: {list(pending.keys())}"
            print(f"{line:<120}", end="\r", flush=True)
            time.sleep(JOB_INTERVAL)

    if pending:
        for sid in pending:
            failed[sid] = "timeout"
    print()  # limpa linha do \r

    # 3. Marcar falhas
    for sid, reason in failed.items():
        print(f"  FALHOU: {sid} ({reason})")
        results[sid] = {"status": "error", "error": reason}

    # 4. Baixar completados
    for i, (sid, job_id) in enumerate(completed.items(), 1):
        source = next(s for s in batch if s["id"] == sid)
        out_file = RAW_DIR / f"{sid}.csv"
        g_done = global_done + i
        bar_global = _bar(g_done, global_total)
        print(f"  Baixando {bar_global}  {sid}...", end="\r", flush=True)
        try:
            client.download_job(job_id, out_file, token)
            rows = _count_csv_rows(out_file)
            size_mb = out_file.stat().st_size / 1_048_576
            print(f"  {_bar(g_done, global_total)}  OK  {sid:<25} {rows:>8,} linhas  {size_mb:.1f} MB")
            results[sid] = {
                "status": "ok",
                "file": f"{sid}.csv",
                "rows": rows,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "zoho_name": source["zoho_name"],
            }
        except ZohoError as exc:
            print(f"  ERRO ao baixar {sid}: {exc}")
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

    total = len(to_extract)
    n_lotes = (total + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nExtraindo {total} fontes em {n_lotes} lote(s) de {BATCH_SIZE}...\n")
    print(f"  {_bar(0, total)}")
    print()

    total_ok = 0
    total_err = 0
    global_done = 0

    for i in range(0, total, BATCH_SIZE):
        batch = to_extract[i:i + BATCH_SIZE]
        lote_num = i // BATCH_SIZE + 1
        print(f"--- Lote {lote_num}/{n_lotes}: {[s['id'] for s in batch]} ---")

        results = _extract_batch(client, token, batch, global_done, total)

        for sid, result in results.items():
            manifest[sid] = result
            if result["status"] == "ok":
                total_ok += 1
                global_done += 1
            else:
                total_err += 1

        _save_manifest(manifest)
        print()

    # Resumo final
    print(f"  {_bar(total_ok, total)}")
    print(f"\nConcluido: {total_ok} OK, {total_err} erro(s).")
    print(f"Manifest: {MANIFEST_FILE}")

    return 0 if total_err == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
