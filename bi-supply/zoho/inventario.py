"""
Regenera o inventário completo do Zoho Analytics e perfiliza as fontes do SUPRIMENTOS.

Gera:
  docs/zoho/INVENTARIO_WORKSPACES.md   — todos os workspaces e suas views (UTF-8)
  data/raw/samples/{nome}.csv          — 5 linhas de cada Table/QueryTable do SUPRIMENTOS
  docs/dados/PERFIL_FONTES.md          — colunas, tipos inferidos e amostras por fonte

Uso:
  python zoho/inventario.py --env-file zoho/zoho.env
  python zoho/inventario.py --env-file zoho/zoho.env --skip-samples
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zoho.client import ZohoClient, ZohoConfig, ZohoError, load_env_file


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SUPRIMENTOS_WS = "2130260000001511306"
SAMPLE_LIMIT = 5
BATCH_SIZE = 5      # jobs simultâneos
JOB_INTERVAL = 8   # segundos entre polls

DOCS_INVENTARIO = ROOT / "docs" / "zoho" / "INVENTARIO_WORKSPACES.md"
DOCS_PERFIL = ROOT / "docs" / "dados" / "PERFIL_FONTES.md"
SAMPLES_DIR = ROOT / "data" / "raw" / "samples"


# ---------------------------------------------------------------------------
# Coleta de dados
# ---------------------------------------------------------------------------

def get_all_workspaces(client: ZohoClient, token: str) -> list[dict[str, Any]]:
    """Retorna lista de todos os workspaces acessíveis com suas views."""
    print("Buscando workspaces...")
    ws_data = client.get_workspaces(token)
    payload = ws_data.get("data", {}) if isinstance(ws_data.get("data"), dict) else {}

    workspaces: list[dict[str, Any]] = []
    for group in ("ownedWorkspaces", "sharedWorkspaces"):
        for ws in payload.get(group, []):
            workspaces.append({
                "workspaceId": ws.get("workspaceId", ""),
                "workspaceName": ws.get("workspaceName", ""),
                "orgId": ws.get("orgId", ""),
                "ownership": "Próprio" if group == "ownedWorkspaces" else "Compartilhado",
            })

    print(f"  {len(workspaces)} workspaces encontrados")

    for ws in workspaces:
        ws_id = ws["workspaceId"]
        ws_name = ws["workspaceName"]
        print(f"  Buscando views: {ws_name}...", end=" ", flush=True)
        try:
            views_data = client.get_views(token, workspace_id=ws_id)
            views = views_data.get("data", {}).get("views", []) if isinstance(views_data.get("data"), dict) else []
            ws["views"] = views
            ws["view_count"] = len(views)

            by_type: dict[str, int] = {}
            for v in views:
                t = v.get("viewType", "Unknown")
                by_type[t] = by_type.get(t, 0) + 1
            ws["by_type"] = by_type
            print(f"{len(views)} views")
        except ZohoError as exc:
            print(f"ERRO: {exc}")
            ws["views"] = []
            ws["view_count"] = 0
            ws["by_type"] = {}

    return workspaces


def infer_type(values: list[str]) -> str:
    """Infere tipo de dado a partir de amostras."""
    clean = [v.strip() for v in values if v.strip()]
    if not clean:
        return "vazio"

    int_count = sum(1 for v in clean if v.lstrip("-").isdigit())
    if int_count == len(clean):
        return "inteiro"

    float_count = 0
    for v in clean:
        try:
            float(v.replace(",", "."))
            float_count += 1
        except ValueError:
            pass
    if float_count == len(clean):
        return "decimal"

    return "texto"


def profile_view(client: ZohoClient, token: str, view_name: str) -> dict[str, Any] | None:
    """Baixa 5 linhas de uma view e retorna perfil de colunas."""
    sql = f'select * from "{view_name}" limit {SAMPLE_LIMIT}'
    try:
        job_id = client.create_job_sql(sql, token)
        # polling silencioso
        for _ in range(30):
            status = client.job_status(job_id, token)
            payload = status.get("data") if isinstance(status.get("data"), dict) else {}
            code = str(payload.get("jobCode", ""))
            if code == "1004":
                break
            if code in {"1003", "1005"}:
                return None
            time.sleep(JOB_INTERVAL)
        else:
            return None

        # download em memória
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sample.csv"
            client.download_job(job_id, out, token)
            content = out.read_bytes().decode("utf-8-sig", errors="replace")

        rows = list(csv.DictReader(io.StringIO(content)))
        if not rows:
            return {"columns": [], "rows": [], "raw_csv": content}

        columns = list(rows[0].keys())
        col_profiles = []
        for col in columns:
            vals = [r.get(col, "") for r in rows]
            col_profiles.append({
                "name": col,
                "type": infer_type(vals),
                "sample": vals[0] if vals else "",
            })

        return {
            "columns": col_profiles,
            "row_count": len(rows),
            "raw_rows": rows,
        }

    except (ZohoError, Exception):
        return None


# ---------------------------------------------------------------------------
# Geração de Markdown
# ---------------------------------------------------------------------------

def build_inventario_md(workspaces: list[dict[str, Any]], generated_at: str) -> str:
    lines: list[str] = []
    lines.append("# Inventário Zoho Analytics — Workspaces e Views")
    lines.append("")
    lines.append(f"Gerado em: `{generated_at}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resumo
    total_views = sum(ws.get("view_count", 0) for ws in workspaces)
    lines.append("## Resumo geral")
    lines.append("")
    lines.append(f"- Workspaces acessíveis: `{len(workspaces)}`")
    lines.append(f"- Views totais: `{total_views}`")
    lines.append("")

    # Tabela resumo
    lines.append("| Workspace | Workspace ID | Acesso | Views | Table | QueryTable | Pivot | AnalysisView | Dashboard |")
    lines.append("|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for ws in workspaces:
        bt = ws.get("by_type", {})
        lines.append(
            f"| **{ws['workspaceName']}** "
            f"| `{ws['workspaceId']}` "
            f"| {ws['ownership']} "
            f"| {ws['view_count']} "
            f"| {bt.get('Table', 0)} "
            f"| {bt.get('QueryTable', 0)} "
            f"| {bt.get('Pivot', 0)} "
            f"| {bt.get('AnalysisView', 0)} "
            f"| {bt.get('Dashboard', 0)} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Detalhe por workspace
    for ws in workspaces:
        lines.append(f"## {ws['workspaceName']}")
        lines.append("")
        lines.append(f"- Workspace ID: `{ws['workspaceId']}`")
        lines.append(f"- Org ID: `{ws['orgId']}`")
        lines.append(f"- Acesso: {ws['ownership']}")
        lines.append(f"- Views: `{ws['view_count']}`")
        bt = ws.get("by_type", {})
        if bt:
            dist = ", ".join(f"`{t}`: {n}" for t, n in sorted(bt.items()))
            lines.append(f"- Distribuição: {dist}")
        lines.append("")

        views = ws.get("views", [])
        if views:
            lines.append("| Tipo | View ID | Nome |")
            lines.append("|---|---:|---|")
            for v in sorted(views, key=lambda x: (x.get("viewType", ""), x.get("viewName", ""))):
                lines.append(f"| {v.get('viewType', '')} | `{v.get('viewId', '')}` | {v.get('viewName', '')} |")
        else:
            lines.append("_Sem views ou acesso negado._")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def build_perfil_md(profiles: dict[str, Any], generated_at: str) -> str:
    lines: list[str] = []
    lines.append("# Perfil das Fontes — SUPRIMENTOS")
    lines.append("")
    lines.append(f"Gerado em: `{generated_at}` — amostras de {SAMPLE_LIMIT} linhas por fonte.")
    lines.append("")
    lines.append("Cobre apenas **Tables** e **QueryTables** do workspace SUPRIMENTOS.")
    lines.append("Pivots, AnalysisViews e Dashboards são camada visual — não incluídos.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resumo
    ok = sum(1 for p in profiles.values() if p and p.get("columns"))
    lines.append(f"- Fontes analisadas: `{len(profiles)}`")
    lines.append(f"- Com amostra OK: `{ok}`")
    lines.append(f"- Com erro ou vazia: `{len(profiles) - ok}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    for name, profile in sorted(profiles.items()):
        lines.append(f"## {name}")
        lines.append("")
        if not profile or not profile.get("columns"):
            lines.append("_Amostra indisponível._")
            lines.append("")
            continue

        cols = profile["columns"]
        lines.append(f"**Colunas:** {len(cols)}  |  **Linhas na amostra:** {profile.get('row_count', 0)}")
        lines.append("")
        lines.append("| Coluna | Tipo inferido | Exemplo |")
        lines.append("|---|---|---|")
        for col in cols:
            sample = str(col.get("sample", "")).replace("|", "\\|")[:80]
            lines.append(f"| `{col['name']}` | {col['type']} | {sample} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenera inventário Zoho e perfil de fontes.")
    parser.add_argument("--env-file", required=True)
    parser.add_argument("--skip-samples", action="store_true", help="Só inventário, sem amostrar o SUPRIMENTOS.")
    args = parser.parse_args(argv)

    load_env_file(args.env_file)
    client = ZohoClient(ZohoConfig.from_env(require_workspace=False))
    token = client.refresh_token()
    print("Token OK.")

    from datetime import datetime
    generated_at = datetime.now().strftime("%Y-%m-%dT%H:%M")

    # ---- 1. Inventário completo ----
    workspaces = get_all_workspaces(client, token)

    print(f"\nGravando {DOCS_INVENTARIO}...")
    DOCS_INVENTARIO.parent.mkdir(parents=True, exist_ok=True)
    DOCS_INVENTARIO.write_text(build_inventario_md(workspaces, generated_at), encoding="utf-8")
    print("  OK")

    # Salvar JSON bruto também
    inv_json = ROOT / "data" / "raw" / "zoho_inventory.json"
    inv_json.parent.mkdir(parents=True, exist_ok=True)
    inv_json.write_text(json.dumps(workspaces, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  JSON bruto: {inv_json}")

    if args.skip_samples:
        print("\nSkip samples — concluído.")
        return 0

    # ---- 2. Perfil do SUPRIMENTOS ----
    suprimentos = next((ws for ws in workspaces if ws["workspaceId"] == SUPRIMENTOS_WS), None)
    if not suprimentos:
        print("ERRO: workspace SUPRIMENTOS não encontrado.")
        return 1

    sources = [
        v for v in suprimentos.get("views", [])
        if v.get("viewType") in ("Table", "QueryTable")
    ]
    print(f"\nPerfilando {len(sources)} fontes (Tables + QueryTables) do SUPRIMENTOS...")
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    profiles: dict[str, Any] = {}
    for i, view in enumerate(sources, 1):
        name = view.get("viewName", "")
        print(f"  [{i:02d}/{len(sources)}] {name}...", end=" ", flush=True)
        profile = profile_view(client, token, name)
        if profile and profile.get("columns"):
            # Salvar CSV da amostra
            safe_name = "".join(c if c.isalnum() or c in "- _" else "_" for c in name)
            csv_path = SAMPLES_DIR / f"{safe_name}.csv"
            if profile.get("raw_rows"):
                with csv_path.open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(profile["raw_rows"][0].keys()))
                    writer.writeheader()
                    writer.writerows(profile["raw_rows"])
            print(f"{len(profile['columns'])} colunas")
        else:
            print("erro/vazio")
        profiles[name] = profile

    print(f"\nGravando {DOCS_PERFIL}...")
    DOCS_PERFIL.parent.mkdir(parents=True, exist_ok=True)
    DOCS_PERFIL.write_text(build_perfil_md(profiles, generated_at), encoding="utf-8")
    print("  OK")

    # Salvar JSON do perfil
    perfil_json = ROOT / "data" / "raw" / "suprimentos_profile.json"
    serializable = {
        k: {kk: vv for kk, vv in v.items() if kk != "raw_rows"} if v else None
        for k, v in profiles.items()
    }
    perfil_json.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for p in profiles.values() if p and p.get("columns"))
    print(f"\nConcluído: {ok}/{len(sources)} fontes perfiladas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
