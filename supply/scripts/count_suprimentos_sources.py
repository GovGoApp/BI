from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = BASE_DIR / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from zoho_analytics_client import ZohoAnalyticsClient, ZohoAnalyticsConfig, load_env_file  # noqa: E402


PROFILE_CSV = BASE_DIR / "output" / "suprimentos_profile" / "suprimentos_sources_profile.csv"
ROW_COUNTS_CSV = BASE_DIR / "output" / "suprimentos_profile" / "suprimentos_source_row_counts.csv"
TMP_FILE = BASE_DIR / "output" / "suprimentos_profile" / "row_count_tmp.csv"


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def read_profile(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_count(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        first = next(reader, {})
    return str(next(iter(first.values()), "")) if first else ""


def write_counts(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["view_type", "view_id", "view_name", "row_count", "status", "error"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Conta linhas das fontes Table/QueryTable do workspace SUPRIMENTOS.")
    parser.add_argument("--env-file", default="zoho.env")
    parser.add_argument("--profile", default=str(PROFILE_CSV.relative_to(BASE_DIR)))
    parser.add_argument("--out", default=str(ROW_COUNTS_CSV.relative_to(BASE_DIR)))
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--max-attempts", type=int, default=40)
    args = parser.parse_args()

    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = BASE_DIR / env_file
    profile_path = Path(args.profile)
    if not profile_path.is_absolute():
        profile_path = BASE_DIR / profile_path
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = BASE_DIR / out_path

    load_env_file(env_file)
    client = ZohoAnalyticsClient(ZohoAnalyticsConfig.from_env())
    token = client.refresh_access_token()

    rows = read_profile(profile_path)
    results: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        view_name = row["view_name"]
        print(f"[{index}/{len(rows)}] {view_name}", flush=True)
        out: dict[str, Any] = {
            "view_type": row.get("view_type", ""),
            "view_id": row.get("view_id", ""),
            "view_name": view_name,
            "row_count": "",
            "status": "erro",
            "error": "",
        }
        try:
            sql = f"select count(*) as ROW_COUNT from {quote_identifier(view_name)}"
            job_id = client.create_export_job_for_sql(sql, access_token=token)
            client.wait_for_export_job(job_id, access_token=token, interval_seconds=args.interval, max_attempts=args.max_attempts)
            client.download_export_job(job_id, TMP_FILE, access_token=token)
            out["row_count"] = read_count(TMP_FILE)
            out["status"] = "ok"
        except Exception as exc:
            out["error"] = f"{type(exc).__name__}: {exc}"
        results.append(out)

    if TMP_FILE.exists():
        TMP_FILE.unlink()
    write_counts(out_path, results)

    ok = sum(1 for row in results if row["status"] == "ok")
    print(f"OK: {ok} / {len(results)}")
    print(f"CSV: {out_path.relative_to(BASE_DIR)}")
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
