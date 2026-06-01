"""Cliente Zoho Analytics API v2 com OAuth2.

Uso via CLI:
    python zoho/client.py --env-file zoho/zoho.env token
    python zoho/client.py --env-file zoho/zoho.env views
    python zoho/client.py --env-file zoho/zoho.env export-sql --sql "select * from NFE limit 10" --out data/raw/nfe.csv --wait
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests


DEFAULT_ACCOUNTS_URL = "https://accounts.zoho.com"
DEFAULT_ANALYTICS_URL = "https://analyticsapi.zoho.com"

# Códigos de status de job da Bulk API
_JOB_COMPLETE = "1004"
_JOB_FAILED = {"1003", "1005"}


class ZohoError(RuntimeError):
    """Erro retornado pela API Zoho ou por resposta inesperada."""


# ---------------------------------------------------------------------------
# Carregamento de .env
# ---------------------------------------------------------------------------

def load_env_file(path: str | Path) -> dict[str, str]:
    """Lê um arquivo .env e injeta as variáveis em os.environ."""
    loaded: dict[str, str] = {}
    env_path = Path(path)
    for line_no, raw in enumerate(env_path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Linha inválida em {env_path}:{line_no}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            raise ValueError(f"Variável sem nome em {env_path}:{line_no}")
        os.environ[key] = value
        loaded[key] = value
    return loaded


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZohoConfig:
    client_id: str
    client_secret: str
    refresh_token: str
    org_id: str = ""
    workspace_id: str = ""
    accounts_url: str = DEFAULT_ACCOUNTS_URL
    analytics_url: str = DEFAULT_ANALYTICS_URL

    @classmethod
    def from_env(cls, require_workspace: bool = True) -> "ZohoConfig":
        """Lê configuração de os.environ.

        require_workspace=False permite usar sem org_id/workspace_id
        (útil para os comandos 'orgs' e 'workspaces' durante setup inicial).
        """
        def get(key: str) -> str:
            return os.environ.get(key, "").strip()

        required = {
            "ZOHO_ANALYTICS_CLIENT_ID": get("ZOHO_ANALYTICS_CLIENT_ID"),
            "ZOHO_ANALYTICS_CLIENT_SECRET": get("ZOHO_ANALYTICS_CLIENT_SECRET"),
            "ZOHO_ANALYTICS_REFRESH_TOKEN": get("ZOHO_ANALYTICS_REFRESH_TOKEN"),
        }
        if require_workspace:
            required["ZOHO_ANALYTICS_ORG_ID"] = get("ZOHO_ANALYTICS_ORG_ID")
            required["ZOHO_ANALYTICS_WORKSPACE_ID"] = get("ZOHO_ANALYTICS_WORKSPACE_ID")

        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError("Variáveis obrigatórias ausentes: " + ", ".join(missing))

        return cls(
            client_id=required["ZOHO_ANALYTICS_CLIENT_ID"],
            client_secret=required["ZOHO_ANALYTICS_CLIENT_SECRET"],
            refresh_token=required["ZOHO_ANALYTICS_REFRESH_TOKEN"],
            org_id=get("ZOHO_ANALYTICS_ORG_ID"),
            workspace_id=get("ZOHO_ANALYTICS_WORKSPACE_ID"),
            accounts_url=get("ZOHO_ANALYTICS_ACCOUNTS_URL") or DEFAULT_ACCOUNTS_URL,
            analytics_url=get("ZOHO_ANALYTICS_API_URL") or DEFAULT_ANALYTICS_URL,
        )


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------

class ZohoClient:
    def __init__(
        self,
        config: ZohoConfig,
        session: requests.Session | None = None,
        timeout: int = 60,
    ) -> None:
        self.config = config
        self._session = session or requests.Session()
        self._timeout = timeout

    # ---- Autenticação ----

    def refresh_token(self) -> str:
        """Renova e retorna um access_token usando o refresh_token."""
        resp = self._session.post(
            f"{self.config.accounts_url.rstrip('/')}/oauth/v2/token",
            params={
                "refresh_token": self.config.refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "grant_type": "refresh_token",
            },
            timeout=self._timeout,
        )
        data = self._json(resp, "Não foi possível renovar o access token")
        token = data.get("access_token")
        if not token:
            raise ZohoError(f"Resposta sem access_token: {data}")
        return str(token)

    @staticmethod
    def exchange_code(
        accounts_url: str,
        client_id: str,
        client_secret: str,
        code: str,
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Troca o authorization code por access_token + refresh_token."""
        resp = requests.post(
            f"{accounts_url.rstrip('/')}/oauth/v2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
            },
            timeout=timeout,
        )
        return ZohoClient._json(resp, "Não foi possível trocar o authorization code")

    # ---- Descoberta ----

    def get_orgs(self, token: str) -> dict[str, Any]:
        resp = self._session.get(
            self._url("restapi/v2/orgs"),
            headers={"Authorization": f"Zoho-oauthtoken {token}"},
            timeout=self._timeout,
        )
        return self._json(resp, "Não foi possível listar organizações")

    def get_workspaces(self, token: str) -> dict[str, Any]:
        resp = self._session.get(
            self._url("restapi/v2/workspaces"),
            headers={"Authorization": f"Zoho-oauthtoken {token}"},
            timeout=self._timeout,
        )
        return self._json(resp, "Não foi possível listar workspaces")

    def get_views(
        self,
        token: str,
        keyword: str | None = None,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        """Lista views de um workspace. Usa workspace_id do config se não informado."""
        ws = workspace_id or self.config.workspace_id
        params: dict[str, str] = {}
        if keyword:
            params["CONFIG"] = json.dumps({"keyword": keyword})
        headers = {"Authorization": f"Zoho-oauthtoken {token}", "ZANALYTICS-ORGID": self.config.org_id}
        resp = self._session.get(
            self._url(f"restapi/v2/workspaces/{ws}/views"),
            headers=headers,
            params=params or None,
            timeout=self._timeout,
        )
        return self._json(resp, f"Não foi possível listar views do workspace {ws}")

    # ---- Exportação síncrona (views pequenas) ----

    def export_view(
        self,
        view_id: str,
        out: str | Path,
        token: str,
        fmt: str = "csv",
    ) -> Path:
        resp = self._session.get(
            self._url(f"restapi/v2/workspaces/{self.config.workspace_id}/views/{view_id}/data"),
            headers=self._headers(token),
            params={"CONFIG": json.dumps({"responseFormat": fmt})},
            timeout=self._timeout,
        )
        self._raise(resp, "Não foi possível exportar a view")
        return self._save(out, resp.content)

    # ---- Exportação assíncrona (Bulk API) ----

    def create_job_view(self, view_id: str, token: str, fmt: str = "csv") -> str:
        """Cria job de exportação assíncrono para uma view."""
        resp = self._session.get(
            self._url(f"restapi/v2/bulk/workspaces/{self.config.workspace_id}/views/{view_id}/data"),
            headers=self._headers(token),
            params={"CONFIG": json.dumps({"responseFormat": fmt})},
            timeout=self._timeout,
        )
        return self._job_id(self._json(resp, "Não foi possível criar job de exportação"))

    def create_job_sql(self, sql: str, token: str, fmt: str = "csv") -> str:
        """Cria job de exportação assíncrono via SQL SELECT."""
        resp = self._session.get(
            self._url(f"restapi/v2/bulk/workspaces/{self.config.workspace_id}/data"),
            headers=self._headers(token),
            params={"CONFIG": json.dumps({"sqlQuery": sql, "responseFormat": fmt})},
            timeout=self._timeout,
        )
        return self._job_id(self._json(resp, "Não foi possível criar job SQL"))

    def job_status(self, job_id: str, token: str) -> dict[str, Any]:
        resp = self._session.get(
            self._url(f"restapi/v2/bulk/workspaces/{self.config.workspace_id}/exportjobs/{job_id}"),
            headers=self._headers(token),
            timeout=self._timeout,
        )
        return self._json(resp, "Não foi possível consultar job")

    def wait_job(
        self,
        job_id: str,
        token: str,
        interval: int = 10,
        max_attempts: int = 60,
    ) -> dict[str, Any]:
        """Aguarda o job terminar. Imprime progresso no terminal."""
        for attempt in range(1, max_attempts + 1):
            data = self.job_status(job_id, token)
            payload = data.get("data") if isinstance(data.get("data"), dict) else {}
            code = str(payload.get("jobCode", ""))
            if code == _JOB_COMPLETE:
                print(" concluído.")
                return data
            if code in _JOB_FAILED:
                print()
                raise ZohoError(f"Job {job_id} falhou: {payload}")
            print(f"\r  Aguardando job {job_id}... tentativa {attempt}/{max_attempts}", end="", flush=True)
            if attempt < max_attempts:
                time.sleep(interval)
        print()
        raise ZohoError(f"Job {job_id} não concluiu após {max_attempts} tentativas")

    def download_job(self, job_id: str, out: str | Path, token: str) -> Path:
        resp = self._session.get(
            self._url(f"restapi/v2/bulk/workspaces/{self.config.workspace_id}/exportjobs/{job_id}/data"),
            headers=self._headers(token),
            timeout=self._timeout,
        )
        self._raise(resp, "Não foi possível baixar o arquivo do job")
        return self._save(out, resp.content)

    # ---- Helpers privados ----

    def _url(self, path: str) -> str:
        return f"{self.config.analytics_url.rstrip('/')}/{path.lstrip('/')}"

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Zoho-oauthtoken {token}",
            "ZANALYTICS-ORGID": self.config.org_id,
        }

    @staticmethod
    def _raise(resp: requests.Response, msg: str) -> None:
        if resp.status_code >= 400:
            raise ZohoError(f"{msg}. HTTP {resp.status_code}: {resp.text[:800]}")

    @classmethod
    def _json(cls, resp: requests.Response, msg: str) -> dict[str, Any]:
        cls._raise(resp, msg)
        try:
            data = resp.json()
        except ValueError as exc:
            raise ZohoError(f"{msg}. Resposta não-JSON: {resp.text[:800]}") from exc
        if not isinstance(data, dict):
            raise ZohoError(f"{msg}. JSON inesperado: {data}")
        if data.get("status") == "failure" or data.get("errorCode") or data.get("error"):
            raise ZohoError(f"{msg}: {data}")
        return data

    @staticmethod
    def _job_id(data: dict[str, Any]) -> str:
        payload = data.get("data") if isinstance(data.get("data"), dict) else {}
        job_id = payload.get("jobId")
        if not job_id:
            raise ZohoError(f"Resposta sem jobId: {data}")
        return str(job_id)

    @staticmethod
    def _save(path: str | Path, content: bytes) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        return p


# ---------------------------------------------------------------------------
# Saída formatada para CLI
# ---------------------------------------------------------------------------

def _print_orgs(data: dict[str, Any]) -> None:
    orgs = data.get("data", {}).get("orgs", []) if isinstance(data.get("data"), dict) else []
    print(f"Organizações: {len(orgs)}")
    for o in orgs:
        print(f"  {o.get('orgId')}  {o.get('orgName')}  default={o.get('isDefault')}  role={o.get('role')}")


def _print_workspaces(data: dict[str, Any]) -> None:
    payload = data.get("data", {}) if isinstance(data.get("data"), dict) else {}
    groups = [("ownedWorkspaces", "Próprios"), ("sharedWorkspaces", "Compartilhados")]
    total = sum(len(payload.get(k, [])) for k, _ in groups if isinstance(payload.get(k, []), list))
    print(f"Workspaces: {total}")
    for key, title in groups:
        rows = payload.get(key, [])
        if not isinstance(rows, list) or not rows:
            continue
        print(f"  {title}:")
        for ws in rows:
            print(f"    {ws.get('workspaceId')}  org={ws.get('orgId')}  {ws.get('workspaceName')}")


def _print_views(data: dict[str, Any], limit: int | None = None) -> None:
    views = data.get("data", {}).get("views", []) if isinstance(data.get("data"), dict) else []
    shown = views if limit is None else views[:limit]
    print(f"Views: {len(views)}")
    for v in shown:
        print(f"  {v.get('viewId')}  {v.get('viewType'):<15}  {v.get('viewName')}")
    if limit and len(views) > limit:
        print(f"  ... ({len(views) - limit} ocultadas — use --limit 0 para ver todas)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Zoho Analytics API v2 — cliente CLI.")
    p.add_argument("--env-file", metavar="PATH", help="Arquivo .env com credenciais ZOHO_ANALYTICS_*")
    sub = p.add_subparsers(dest="cmd", required=True)

    # exchange-code
    ex = sub.add_parser("exchange-code", help="Troca authorization code por refresh_token.")
    ex.add_argument("--code", required=True, help="Código gerado no Self Client do Zoho.")

    # token
    sub.add_parser("token", help="Valida credenciais renovando o access token.")

    # orgs
    sub.add_parser("orgs", help="Lista organizações e org_id.")

    # workspaces
    sub.add_parser("workspaces", help="Lista workspaces e workspace_id.")

    # views
    vw = sub.add_parser("views", help="Lista views do workspace configurado.")
    vw.add_argument("--keyword", help="Filtra por texto.")
    vw.add_argument("--limit", type=int, default=50, help="Máximo de views a exibir (0 = todas).")

    # export-view
    ev = sub.add_parser("export-view", help="Exporta dados de uma view por ID.")
    ev.add_argument("--view-id", required=True)
    ev.add_argument("--out", required=True)
    ev.add_argument("--format", default="csv", choices=["csv", "json", "xml"])
    ev.add_argument("--async", dest="async_mode", action="store_true", help="Usa Bulk API assíncrona.")
    ev.add_argument("--wait", action="store_true", help="Aguarda job e baixa o arquivo.")
    ev.add_argument("--interval", type=int, default=10, help="Segundos entre polling (default 10).")

    # export-sql
    es = sub.add_parser("export-sql", help="Exportação assíncrona via SQL SELECT.")
    es.add_argument("--sql", required=True)
    es.add_argument("--out", required=True)
    es.add_argument("--format", default="csv", choices=["csv", "json", "xml"])
    es.add_argument("--wait", action="store_true")
    es.add_argument("--interval", type=int, default=10)

    # job-status
    js = sub.add_parser("job-status", help="Consulta status de um job de exportação.")
    js.add_argument("--job-id", required=True)

    # download-job
    dj = sub.add_parser("download-job", help="Baixa arquivo de um job concluído.")
    dj.add_argument("--job-id", required=True)
    dj.add_argument("--out", required=True)

    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        if args.env_file:
            load_env_file(args.env_file)

        # exchange-code não precisa de workspace
        if args.cmd == "exchange-code":
            result = ZohoClient.exchange_code(
                accounts_url=os.environ.get("ZOHO_ANALYTICS_ACCOUNTS_URL", DEFAULT_ACCOUNTS_URL),
                client_id=os.environ.get("ZOHO_ANALYTICS_CLIENT_ID", ""),
                client_secret=os.environ.get("ZOHO_ANALYTICS_CLIENT_SECRET", ""),
                code=args.code,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if result.get("refresh_token"):
                print("\nCopie o refresh_token acima para ZOHO_ANALYTICS_REFRESH_TOKEN no zoho.env.")
            return 0

        # orgs e workspaces não precisam de workspace_id
        if args.cmd in {"orgs", "workspaces"}:
            client = ZohoClient(ZohoConfig.from_env(require_workspace=False))
            token = client.refresh_token()
            if args.cmd == "orgs":
                _print_orgs(client.get_orgs(token))
            else:
                _print_workspaces(client.get_workspaces(token))
            return 0

        # todos os outros comandos precisam de workspace
        client = ZohoClient(ZohoConfig.from_env())
        token = client.refresh_token()

        if args.cmd == "token":
            print("OK — credenciais válidas e access token renovado.")
            return 0

        if args.cmd == "views":
            limit = args.limit if args.limit > 0 else None
            _print_views(client.get_views(token, keyword=args.keyword), limit=limit)
            return 0

        if args.cmd == "export-view":
            if args.async_mode:
                job_id = client.create_job_view(args.view_id, token, fmt=args.format)
                print(f"Job criado: {job_id}")
                if args.wait:
                    client.wait_job(job_id, token, interval=args.interval)
                    path = client.download_job(job_id, args.out, token)
                    print(f"Salvo em: {path}")
            else:
                path = client.export_view(args.view_id, args.out, token, fmt=args.format)
                print(f"Salvo em: {path}")
            return 0

        if args.cmd == "export-sql":
            job_id = client.create_job_sql(args.sql, token, fmt=args.format)
            print(f"Job criado: {job_id}")
            if args.wait:
                client.wait_job(job_id, token, interval=args.interval)
                path = client.download_job(job_id, args.out, token)
                print(f"Salvo em: {path}")
            return 0

        if args.cmd == "job-status":
            print(json.dumps(client.job_status(args.job_id, token), ensure_ascii=False, indent=2))
            return 0

        if args.cmd == "download-job":
            path = client.download_job(args.job_id, args.out, token)
            print(f"Salvo em: {path}")
            return 0

    except (ZohoError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
