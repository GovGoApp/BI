"""Executa SQL somente-leitura no Zoho Analytics e retorna linhas.

Usa a Bulk API assíncrona do Zoho para todos os queries.
Sempre injeta LIMIT via guard.py antes de executar.
"""

from __future__ import annotations

import csv
import io
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.guard import validate, SQLGuardError
from zoho.client import ZohoClient, ZohoConfig, ZohoError, load_env_file

ENV_FILE = ROOT / "zoho" / "zoho.env"

_JOB_COMPLETE = "1004"
_JOB_FAILED = {"1003", "1005"}
_POLL_INTERVAL = 6
_MAX_ATTEMPTS = 60


class AdapterError(RuntimeError):
    pass


def _get_client() -> tuple[ZohoClient, str]:
    """Cria cliente e renova token."""
    if ENV_FILE.exists():
        load_env_file(ENV_FILE)
    client = ZohoClient(ZohoConfig.from_env())
    token = client.refresh_token()
    return client, token


def run_query(sql: str) -> dict[str, Any]:
    """Valida e executa um SQL SELECT no Zoho. Retorna resultado tabular.

    Returns:
        {
          "ok": bool,
          "columns": [{"name": str, "type": str}],
          "rows": [dict],
          "row_count": int,
          "truncated": bool,
          "sql_used": str,
          "elapsed_ms": int,
          "error": str | None,
        }
    """
    import time as _time
    t0 = _time.monotonic()

    # Validar
    try:
        safe_sql = validate(sql)
    except SQLGuardError as exc:
        return {"ok": False, "error": str(exc), "columns": [], "rows": [], "row_count": 0,
                "truncated": False, "sql_used": sql, "elapsed_ms": 0}

    try:
        client, token = _get_client()

        # Criar job
        job_id = client.create_job_sql(safe_sql, token)

        # Polling
        for _ in range(_MAX_ATTEMPTS):
            status = client.job_status(job_id, token)
            payload = status.get("data") if isinstance(status.get("data"), dict) else {}
            code = str(payload.get("jobCode", ""))
            if code == _JOB_COMPLETE:
                break
            if code in _JOB_FAILED:
                raise AdapterError(f"Job falhou: jobCode={code}")
            time.sleep(_POLL_INTERVAL)
        else:
            raise AdapterError("Timeout aguardando job de exportação.")

        # Download em memória
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "result.csv"
            client.download_job(job_id, out, token)
            content = out.read_bytes().decode("utf-8-sig", errors="replace")

        elapsed = int((_time.monotonic() - t0) * 1000)

        # Parse CSV
        rows = list(csv.DictReader(io.StringIO(content)))
        if not rows:
            return {"ok": True, "columns": [], "rows": [], "row_count": 0,
                    "truncated": False, "sql_used": safe_sql, "elapsed_ms": elapsed, "error": None}

        columns = [{"name": col, "type": _infer_type(col, rows)} for col in rows[0].keys()]
        truncated = len(rows) >= 500

        return {
            "ok": True,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated,
            "sql_used": safe_sql,
            "elapsed_ms": elapsed,
            "error": None,
        }

    except (ZohoError, AdapterError, Exception) as exc:
        elapsed = int((_time.monotonic() - t0) * 1000)
        return {"ok": False, "error": str(exc), "columns": [], "rows": [],
                "row_count": 0, "truncated": False, "sql_used": sql, "elapsed_ms": elapsed}


def _infer_type(col_name: str, rows: list[dict]) -> str:
    """Infere tipo da coluna a partir dos primeiros valores."""
    values = [r.get(col_name, "") for r in rows[:10] if r.get(col_name, "").strip()]
    if not values:
        return "text"
    int_hits = sum(1 for v in values if v.lstrip("-").isdigit())
    if int_hits == len(values):
        return "integer"
    float_hits = 0
    for v in values:
        try:
            float(v.replace(",", "."))
            float_hits += 1
        except ValueError:
            pass
    if float_hits == len(values):
        return "numeric"
    return "text"
