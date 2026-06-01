from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = BASE_DIR / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from zoho_analytics_client import (  # noqa: E402
    ZohoAnalyticsClient,
    ZohoAnalyticsConfig,
    ZohoAnalyticsError,
    load_env_file,
)


OUT_DIR = BASE_DIR / "output" / "zoho_analytics_inventory"
DOC_FILE = BASE_DIR / "docs" / "INVENTARIO_ZOHO_ANALYTICS_WORKSPACES.md"
JSON_FILE = OUT_DIR / "zoho_workspaces_inventory.json"
CSV_FILE = OUT_DIR / "zoho_views_inventory.csv"
WORKSPACES_CSV_FILE = OUT_DIR / "zoho_workspaces_summary.csv"


def clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def orgs_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    return [org for org in as_list(data.get("orgs")) if isinstance(org, dict)]


def workspaces_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    rows: list[dict[str, Any]] = []
    for key, label in [
        ("ownedWorkspaces", "Proprio"),
        ("sharedWorkspaces", "Compartilhado"),
    ]:
        for workspace in as_list(data.get(key)):
            if isinstance(workspace, dict):
                row = dict(workspace)
                row["workspaceGroup"] = label
                rows.append(row)
    return rows


def views_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    return [view for view in as_list(data.get("views")) if isinstance(view, dict)]


def view_type_counts(views: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(clean(view.get("viewType")) or "Sem tipo" for view in views))


def table_row(headers: list[str], values: list[Any]) -> str:
    cells = [clean(value).replace("|", "\\|") for value in values]
    return "| " + " | ".join(cells) + " |"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "org_id",
        "org_name",
        "workspace_id",
        "workspace_name",
        "workspace_group",
        "view_id",
        "view_name",
        "view_type",
        "raw_json",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_workspaces_csv(path: Path, workspaces: list[dict[str, Any]]) -> None:
    fields = [
        "org_id",
        "org_name",
        "workspace_id",
        "workspace_name",
        "workspace_group",
        "views",
        "table",
        "querytable",
        "pivot",
        "analysisview",
        "dashboard",
        "summaryview",
        "outros",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for workspace in workspaces:
            counts = workspace.get("view_type_counts", {})
            total = len(workspace.get("views", []))
            known_total = sum(
                counts.get(key, 0)
                for key in ["Table", "QueryTable", "Pivot", "AnalysisView", "Dashboard", "SummaryView"]
            )
            writer.writerow(
                {
                    "org_id": workspace.get("orgId"),
                    "org_name": workspace.get("org_name"),
                    "workspace_id": workspace.get("workspaceId"),
                    "workspace_name": workspace.get("workspaceName"),
                    "workspace_group": workspace.get("workspaceGroup"),
                    "views": total,
                    "table": counts.get("Table", 0),
                    "querytable": counts.get("QueryTable", 0),
                    "pivot": counts.get("Pivot", 0),
                    "analysisview": counts.get("AnalysisView", 0),
                    "dashboard": counts.get("Dashboard", 0),
                    "summaryview": counts.get("SummaryView", 0),
                    "outros": max(total - known_total, 0),
                    "error": workspace.get("error", ""),
                }
            )


def write_markdown(path: Path, inventory: dict[str, Any]) -> None:
    generated_at = inventory["generated_at"]
    orgs = inventory["orgs"]
    workspaces = inventory["workspaces"]
    total_views = sum(len(workspace.get("views", [])) for workspace in workspaces)

    lines: list[str] = [
        "# Inventario Zoho Analytics - Workspaces e Views",
        "",
        f"Gerado em: `{generated_at}`.",
        "",
        "Este documento lista todos os workspaces acessiveis pelo token configurado em `zoho.env` e todas as views retornadas pela API do Zoho Analytics para cada workspace.",
        "",
        "Arquivos tecnicos gerados:",
        "",
        f"- `{JSON_FILE.relative_to(BASE_DIR)}`: inventario completo em JSON, preservando os objetos retornados pela API.",
        f"- `{WORKSPACES_CSV_FILE.relative_to(BASE_DIR)}`: resumo tabular dos workspaces.",
        f"- `{CSV_FILE.relative_to(BASE_DIR)}`: inventario tabular das views.",
        "",
        "## Resumo geral",
        "",
        f"- Organizacoes acessiveis: `{len(orgs)}`.",
        f"- Workspaces acessiveis: `{len(workspaces)}`.",
        f"- Views totais: `{total_views}`.",
        "",
        "## Organizacoes",
        "",
        table_row(["Org ID", "Organizacao", "Papel", "Default"], ["Org ID", "Organizacao", "Papel", "Default"]),
        "|---|---|---|---|",
    ]

    for org in orgs:
        lines.append(
            table_row(
                ["Org ID", "Organizacao", "Papel", "Default"],
                [org.get("orgId"), org.get("orgName"), org.get("role"), org.get("isDefault")],
            )
        )

    lines.extend(
        [
            "",
            "## Workspaces",
            "",
            "| Organizacao | Workspace | Workspace ID | Tipo de acesso | Views | Table | QueryTable | Pivot | AnalysisView | Dashboard | SummaryView | Outros |",
            "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for workspace in workspaces:
        counts = workspace.get("view_type_counts", {})
        known_total = sum(counts.get(key, 0) for key in ["Table", "QueryTable", "Pivot", "AnalysisView", "Dashboard", "SummaryView"])
        total = len(workspace.get("views", []))
        lines.append(
            table_row(
                [],
                [
                    workspace.get("org_name"),
                    workspace.get("workspaceName"),
                    workspace.get("workspaceId"),
                    workspace.get("workspaceGroup"),
                    total,
                    counts.get("Table", 0),
                    counts.get("QueryTable", 0),
                    counts.get("Pivot", 0),
                    counts.get("AnalysisView", 0),
                    counts.get("Dashboard", 0),
                    counts.get("SummaryView", 0),
                    max(total - known_total, 0),
                ],
            )
        )

    lines.extend(["", "## Inventario por workspace", ""])

    for workspace in workspaces:
        views = workspace.get("views", [])
        counts = workspace.get("view_type_counts", {})
        lines.extend(
            [
                f"### {clean(workspace.get('workspaceName'))}",
                "",
                f"- Organizacao: `{clean(workspace.get('org_name'))}` (`{clean(workspace.get('orgId'))}`).",
                f"- Workspace ID: `{clean(workspace.get('workspaceId'))}`.",
                f"- Tipo de acesso: `{clean(workspace.get('workspaceGroup'))}`.",
                f"- Views: `{len(views)}`.",
                f"- Distribuicao por tipo: `{json.dumps(counts, ensure_ascii=False, sort_keys=True)}`.",
                "",
            ]
        )
        if workspace.get("error"):
            lines.extend([f"Erro ao listar views: `{workspace['error']}`.", ""])
            continue

        lines.extend(
            [
                "| Tipo | View ID | Nome |",
                "|---|---:|---|",
            ]
        )
        for view in sorted(views, key=lambda row: (clean(row.get("viewType")), clean(row.get("viewName")))):
            lines.append(table_row([], [view.get("viewType"), view.get("viewId"), view.get("viewName")]))
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_inventory(env_file: Path) -> dict[str, Any]:
    load_env_file(env_file)
    base_config = ZohoAnalyticsConfig.from_env_for_discovery()
    client = ZohoAnalyticsClient(base_config)
    token = client.refresh_access_token()

    org_payload = client.get_orgs(access_token=token)
    workspace_payload = client.get_workspaces(access_token=token)

    orgs = orgs_from_payload(org_payload)
    org_name_by_id = {clean(org.get("orgId")): clean(org.get("orgName")) for org in orgs}
    workspaces = workspaces_from_payload(workspace_payload)
    workspaces.sort(key=lambda row: (clean(row.get("orgId")), clean(row.get("workspaceName"))))

    inventory_workspaces: list[dict[str, Any]] = []
    csv_rows: list[dict[str, Any]] = []

    for workspace in workspaces:
        workspace_id = clean(workspace.get("workspaceId"))
        org_id = clean(workspace.get("orgId")) or base_config.org_id
        workspace_name = clean(workspace.get("workspaceName"))
        org_name = org_name_by_id.get(org_id, "")

        config = ZohoAnalyticsConfig(
            accounts_url=base_config.accounts_url,
            analytics_url=base_config.analytics_url,
            client_id=base_config.client_id,
            client_secret=base_config.client_secret,
            refresh_token=base_config.refresh_token,
            org_id=org_id,
            workspace_id=workspace_id,
        )
        workspace_client = ZohoAnalyticsClient(config, session=client.session)
        record = dict(workspace)
        record["org_name"] = org_name
        record["views"] = []
        record["view_type_counts"] = {}
        record["error"] = ""

        try:
            views_payload = workspace_client.get_views(access_token=token)
            views = views_from_payload(views_payload)
            record["views"] = views
            record["view_type_counts"] = view_type_counts(views)
            for view in views:
                csv_rows.append(
                    {
                        "org_id": org_id,
                        "org_name": org_name,
                        "workspace_id": workspace_id,
                        "workspace_name": workspace_name,
                        "workspace_group": workspace.get("workspaceGroup"),
                        "view_id": view.get("viewId"),
                        "view_name": view.get("viewName"),
                        "view_type": view.get("viewType"),
                        "raw_json": json.dumps(view, ensure_ascii=False, sort_keys=True),
                    }
                )
        except ZohoAnalyticsError as exc:
            record["error"] = str(exc)

        inventory_workspaces.append(record)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "env_file": str(env_file.relative_to(BASE_DIR) if env_file.is_relative_to(BASE_DIR) else env_file),
        "orgs": orgs,
        "workspaces": inventory_workspaces,
        "csv_rows": csv_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera inventario completo dos workspaces/views do Zoho Analytics.")
    parser.add_argument("--env-file", default="zoho.env", help="Arquivo .env com credenciais do Zoho.")
    args = parser.parse_args()

    env_file = Path(args.env_file)
    if not env_file.is_absolute():
        env_file = BASE_DIR / env_file

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(env_file)
    csv_rows = inventory.pop("csv_rows")

    JSON_FILE.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(CSV_FILE, csv_rows)
    write_workspaces_csv(WORKSPACES_CSV_FILE, inventory["workspaces"])
    write_markdown(DOC_FILE, inventory)

    total_views = sum(len(workspace.get("views", [])) for workspace in inventory["workspaces"])
    errors = [workspace for workspace in inventory["workspaces"] if workspace.get("error")]
    print(f"Organizacoes: {len(inventory['orgs'])}")
    print(f"Workspaces: {len(inventory['workspaces'])}")
    print(f"Views: {total_views}")
    print(f"Erros em workspaces: {len(errors)}")
    print(f"Markdown: {DOC_FILE.relative_to(BASE_DIR)}")
    print(f"CSV workspaces: {WORKSPACES_CSV_FILE.relative_to(BASE_DIR)}")
    print(f"CSV: {CSV_FILE.relative_to(BASE_DIR)}")
    print(f"JSON: {JSON_FILE.relative_to(BASE_DIR)}")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
