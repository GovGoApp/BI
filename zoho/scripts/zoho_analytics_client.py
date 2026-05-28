from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


DEFAULT_ACCOUNTS_URL = "https://accounts.zoho.com"
DEFAULT_ANALYTICS_URL = "https://analyticsapi.zoho.com"


class ZohoAnalyticsError(RuntimeError):
    """Raised when Zoho returns an error or an unexpected response."""


def load_env_file(path: str | Path) -> dict[str, str]:
    loaded: dict[str, str] = {}
    env_path = Path(path)
    for line_number, raw_line in enumerate(env_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Linha invalida em {env_path}:{line_number}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if not key:
            raise ValueError(f"Variavel sem nome em {env_path}:{line_number}")
        os.environ[key] = value
        loaded[key] = value
    return loaded


@dataclass(frozen=True)
class ZohoAnalyticsConfig:
    accounts_url: str
    analytics_url: str
    client_id: str
    client_secret: str
    refresh_token: str
    org_id: str
    workspace_id: str

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "ZohoAnalyticsConfig":
        source = env if env is not None else os.environ
        required = {
            "ZOHO_ANALYTICS_CLIENT_ID": source.get("ZOHO_ANALYTICS_CLIENT_ID", "").strip(),
            "ZOHO_ANALYTICS_CLIENT_SECRET": source.get("ZOHO_ANALYTICS_CLIENT_SECRET", "").strip(),
            "ZOHO_ANALYTICS_REFRESH_TOKEN": source.get("ZOHO_ANALYTICS_REFRESH_TOKEN", "").strip(),
            "ZOHO_ANALYTICS_ORG_ID": source.get("ZOHO_ANALYTICS_ORG_ID", "").strip(),
            "ZOHO_ANALYTICS_WORKSPACE_ID": source.get("ZOHO_ANALYTICS_WORKSPACE_ID", "").strip(),
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError("Variaveis obrigatorias ausentes: " + ", ".join(missing))

        return cls(
            accounts_url=source.get("ZOHO_ANALYTICS_ACCOUNTS_URL", DEFAULT_ACCOUNTS_URL).strip().rstrip("/"),
            analytics_url=source.get("ZOHO_ANALYTICS_API_URL", DEFAULT_ANALYTICS_URL).strip().rstrip("/"),
            client_id=required["ZOHO_ANALYTICS_CLIENT_ID"],
            client_secret=required["ZOHO_ANALYTICS_CLIENT_SECRET"],
            refresh_token=required["ZOHO_ANALYTICS_REFRESH_TOKEN"],
            org_id=required["ZOHO_ANALYTICS_ORG_ID"],
            workspace_id=required["ZOHO_ANALYTICS_WORKSPACE_ID"],
        )

    @classmethod
    def from_env_for_discovery(cls, env: dict[str, str] | None = None) -> "ZohoAnalyticsConfig":
        source = env if env is not None else os.environ
        required = {
            "ZOHO_ANALYTICS_CLIENT_ID": source.get("ZOHO_ANALYTICS_CLIENT_ID", "").strip(),
            "ZOHO_ANALYTICS_CLIENT_SECRET": source.get("ZOHO_ANALYTICS_CLIENT_SECRET", "").strip(),
            "ZOHO_ANALYTICS_REFRESH_TOKEN": source.get("ZOHO_ANALYTICS_REFRESH_TOKEN", "").strip(),
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise ValueError("Variaveis obrigatorias ausentes: " + ", ".join(missing))

        return cls(
            accounts_url=source.get("ZOHO_ANALYTICS_ACCOUNTS_URL", DEFAULT_ACCOUNTS_URL).strip().rstrip("/"),
            analytics_url=source.get("ZOHO_ANALYTICS_API_URL", DEFAULT_ANALYTICS_URL).strip().rstrip("/"),
            client_id=required["ZOHO_ANALYTICS_CLIENT_ID"],
            client_secret=required["ZOHO_ANALYTICS_CLIENT_SECRET"],
            refresh_token=required["ZOHO_ANALYTICS_REFRESH_TOKEN"],
            org_id=source.get("ZOHO_ANALYTICS_ORG_ID", "").strip(),
            workspace_id=source.get("ZOHO_ANALYTICS_WORKSPACE_ID", "").strip(),
        )


class ZohoAnalyticsClient:
    def __init__(
        self,
        config: ZohoAnalyticsConfig,
        session: requests.Session | None = None,
        timeout: int = 60,
    ) -> None:
        self.config = config
        self.session = session or requests.Session()
        self.timeout = timeout

    def refresh_access_token(self) -> str:
        url = f"{self.config.accounts_url}/oauth/v2/token"
        response = self.session.request(
            "POST",
            url,
            params={
                "refresh_token": self.config.refresh_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "grant_type": "refresh_token",
            },
            timeout=self.timeout,
        )
        data = self._json_response(response, "Nao foi possivel renovar o access token")
        token = data.get("access_token")
        if not token:
            raise ZohoAnalyticsError(f"Resposta sem access_token: {data}")
        return str(token)

    @staticmethod
    def exchange_authorization_code(
        accounts_url: str,
        client_id: str,
        client_secret: str,
        code: str,
        session: requests.Session | None = None,
        timeout: int = 60,
    ) -> dict[str, Any]:
        http = session or requests.Session()
        response = http.request(
            "POST",
            f"{accounts_url.rstrip('/')}/oauth/v2/token",
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "code": code,
            },
            timeout=timeout,
        )
        return ZohoAnalyticsClient._json_response(response, "Nao foi possivel trocar o authorization code")

    def get_views(
        self,
        access_token: str | None = None,
        view_types: list[int] | None = None,
        keyword: str | None = None,
    ) -> dict[str, Any]:
        token = access_token or self.refresh_access_token()
        config: dict[str, Any] = {}
        if view_types is not None:
            config["viewTypes"] = view_types
        if keyword:
            config["keyword"] = keyword

        params = self._config_params(config) if config else None
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "workspaces", self.config.workspace_id, "views"),
            headers=self._headers(token),
            params=params,
            timeout=self.timeout,
        )
        return self._json_response(response, "Nao foi possivel listar as views")

    def get_orgs(self, access_token: str | None = None) -> dict[str, Any]:
        token = access_token or self.refresh_access_token()
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "orgs"),
            headers={"Authorization": f"Zoho-oauthtoken {token}"},
            timeout=self.timeout,
        )
        return self._json_response(response, "Nao foi possivel listar as organizacoes")

    def get_workspaces(self, access_token: str | None = None) -> dict[str, Any]:
        token = access_token or self.refresh_access_token()
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "workspaces"),
            headers={"Authorization": f"Zoho-oauthtoken {token}"},
            timeout=self.timeout,
        )
        return self._json_response(response, "Nao foi possivel listar os workspaces")

    def export_view_data(
        self,
        view_id: str,
        output_path: str | Path,
        response_format: str = "csv",
        access_token: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Path:
        token = access_token or self.refresh_access_token()
        params = self._config_params({"responseFormat": response_format, **(config or {})})
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "workspaces", self.config.workspace_id, "views", view_id, "data"),
            headers=self._headers(token),
            params=params,
            timeout=self.timeout,
        )
        self._raise_for_status(response, "Nao foi possivel exportar a view")
        return self._write_bytes(output_path, response.content)

    def create_export_job_for_view(
        self,
        view_id: str,
        response_format: str = "csv",
        access_token: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> str:
        token = access_token or self.refresh_access_token()
        params = self._config_params({"responseFormat": response_format, **(config or {})})
        response = self.session.request(
            "GET",
            self._analytics_url(
                "restapi",
                "v2",
                "bulk",
                "workspaces",
                self.config.workspace_id,
                "views",
                view_id,
                "data",
            ),
            headers=self._headers(token),
            params=params,
            timeout=self.timeout,
        )
        data = self._json_response(response, "Nao foi possivel criar o job de exportacao")
        return self._job_id(data)

    def create_export_job_for_sql(
        self,
        sql_query: str,
        response_format: str = "csv",
        access_token: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> str:
        token = access_token or self.refresh_access_token()
        params = self._config_params({"sqlQuery": sql_query, "responseFormat": response_format, **(config or {})})
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "bulk", "workspaces", self.config.workspace_id, "data"),
            headers=self._headers(token),
            params=params,
            timeout=self.timeout,
        )
        data = self._json_response(response, "Nao foi possivel criar o job SQL de exportacao")
        return self._job_id(data)

    def get_export_job(self, job_id: str, access_token: str | None = None) -> dict[str, Any]:
        token = access_token or self.refresh_access_token()
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "bulk", "workspaces", self.config.workspace_id, "exportjobs", job_id),
            headers=self._headers(token),
            timeout=self.timeout,
        )
        return self._json_response(response, "Nao foi possivel consultar o job de exportacao")

    def wait_for_export_job(
        self,
        job_id: str,
        access_token: str | None = None,
        interval_seconds: int = 10,
        max_attempts: int = 60,
    ) -> dict[str, Any]:
        token = access_token or self.refresh_access_token()
        for attempt in range(1, max_attempts + 1):
            job = self.get_export_job(job_id, access_token=token)
            job_data = job.get("data") if isinstance(job.get("data"), dict) else {}
            code = str(job_data.get("jobCode", ""))
            if code == "1004":
                return job
            if code in {"1003", "1005"}:
                raise ZohoAnalyticsError(f"Job {job_id} falhou: {job_data}")
            if attempt < max_attempts:
                time.sleep(interval_seconds)
        raise ZohoAnalyticsError(f"Job {job_id} nao concluiu apos {max_attempts} tentativas")

    def download_export_job(
        self,
        job_id: str,
        output_path: str | Path,
        access_token: str | None = None,
    ) -> Path:
        token = access_token or self.refresh_access_token()
        response = self.session.request(
            "GET",
            self._analytics_url("restapi", "v2", "bulk", "workspaces", self.config.workspace_id, "exportjobs", job_id, "data"),
            headers=self._headers(token),
            timeout=self.timeout,
        )
        self._raise_for_status(response, "Nao foi possivel baixar o arquivo exportado")
        return self._write_bytes(output_path, response.content)

    def _headers(self, access_token: str) -> dict[str, str]:
        return {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "ZANALYTICS-ORGID": self.config.org_id,
        }

    def _analytics_url(self, *parts: str) -> str:
        suffix = "/".join(str(part).strip("/") for part in parts)
        return f"{self.config.analytics_url}/{suffix}"

    @staticmethod
    def _config_params(config: dict[str, Any]) -> dict[str, str]:
        return {"CONFIG": json.dumps(config, ensure_ascii=False, separators=(",", ":"))}

    @staticmethod
    def _job_id(data: dict[str, Any]) -> str:
        payload = data.get("data") if isinstance(data.get("data"), dict) else {}
        job_id = payload.get("jobId")
        if not job_id:
            raise ZohoAnalyticsError(f"Resposta sem jobId: {data}")
        return str(job_id)

    @staticmethod
    def _raise_for_status(response: requests.Response, message: str) -> None:
        if response.status_code >= 400:
            body = getattr(response, "text", "")[:800]
            raise ZohoAnalyticsError(f"{message}. HTTP {response.status_code}: {body}")

    @classmethod
    def _json_response(cls, response: requests.Response, message: str) -> dict[str, Any]:
        cls._raise_for_status(response, message)
        try:
            data = response.json()
        except ValueError as exc:
            raise ZohoAnalyticsError(f"{message}. Resposta nao JSON: {response.text[:800]}") from exc
        if not isinstance(data, dict):
            raise ZohoAnalyticsError(f"{message}. JSON inesperado: {data}")
        if data.get("status") == "failure" or data.get("errorCode") or data.get("error"):
            raise ZohoAnalyticsError(f"{message}: {data}")
        return data

    @staticmethod
    def _write_bytes(output_path: str | Path, content: bytes) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path


def _print_views(data: dict[str, Any]) -> None:
    views = data.get("data", {}).get("views", []) if isinstance(data.get("data"), dict) else []
    print(f"Views acessiveis: {len(views)}")
    for view in views[:20]:
        print(f"- {view.get('viewId')} | {view.get('viewType')} | {view.get('viewName')}")


def _print_orgs(data: dict[str, Any]) -> None:
    orgs = data.get("data", {}).get("orgs", []) if isinstance(data.get("data"), dict) else []
    print(f"Organizacoes acessiveis: {len(orgs)}")
    for org in orgs:
        print(f"- {org.get('orgId')} | {org.get('orgName')} | default={org.get('isDefault')} | role={org.get('role')}")


def _print_workspaces(data: dict[str, Any]) -> None:
    payload = data.get("data", {}) if isinstance(data.get("data"), dict) else {}
    groups = [
        ("ownedWorkspaces", "Proprios"),
        ("sharedWorkspaces", "Compartilhados"),
    ]
    total = sum(len(payload.get(key, [])) for key, _ in groups if isinstance(payload.get(key, []), list))
    print(f"Workspaces acessiveis: {total}")
    for key, title in groups:
        rows = payload.get(key, [])
        if not isinstance(rows, list) or not rows:
            continue
        print(title + ":")
        for workspace in rows:
            print(f"- {workspace.get('workspaceId')} | org={workspace.get('orgId')} | {workspace.get('workspaceName')}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Testa acesso ao Zoho Analytics API v2.")
    parser.add_argument("--env-file", help="Arquivo .env com variaveis ZOHO_ANALYTICS_*. Deve vir antes do comando.")
    sub = parser.add_subparsers(dest="command", required=True)

    exchange = sub.add_parser("exchange-code", help="Troca o authorization code inicial por refresh_token.")
    exchange.add_argument("--code", help="Codigo gerado no Self Client do Zoho API Console.")

    sub.add_parser("orgs", help="Lista organizacoes e mostra os org_id disponiveis.")
    sub.add_parser("workspaces", help="Lista workspaces e mostra workspace_id e org_id.")
    sub.add_parser("token", help="Renova o access token e valida as credenciais.")

    views = sub.add_parser("views", help="Lista views/tabelas acessiveis no workspace.")
    views.add_argument("--keyword", help="Filtra views por texto.")

    export_view = sub.add_parser("export-view", help="Exporta dados de uma view por ID.")
    export_view.add_argument("--view-id", required=True)
    export_view.add_argument("--out", required=True)
    export_view.add_argument("--format", default="csv", choices=["csv", "json", "xml", "xls", "pdf", "html"])
    export_view.add_argument("--async-export", action="store_true", help="Usa Bulk API assincrona.")
    export_view.add_argument("--wait", action="store_true", help="Aguarda job assincrono e baixa o arquivo.")
    export_view.add_argument("--interval", type=int, default=10)

    export_sql = sub.add_parser("export-sql", help="Cria exportacao assincrona via SQL SELECT.")
    export_sql.add_argument("--sql", required=True)
    export_sql.add_argument("--out", required=True)
    export_sql.add_argument("--format", default="csv", choices=["csv", "json", "xml", "xls", "pdf", "html"])
    export_sql.add_argument("--wait", action="store_true")
    export_sql.add_argument("--interval", type=int, default=10)

    job = sub.add_parser("job-status", help="Consulta status de um job de exportacao.")
    job.add_argument("--job-id", required=True)

    download = sub.add_parser("download-job", help="Baixa arquivo de um job concluido.")
    download.add_argument("--job-id", required=True)
    download.add_argument("--out", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.env_file:
            load_env_file(args.env_file)

        if args.command == "exchange-code":
            env = os.environ
            accounts_url = env.get("ZOHO_ANALYTICS_ACCOUNTS_URL", DEFAULT_ACCOUNTS_URL).strip().rstrip("/")
            client_id = env.get("ZOHO_ANALYTICS_CLIENT_ID", "").strip()
            client_secret = env.get("ZOHO_ANALYTICS_CLIENT_SECRET", "").strip()
            code = (args.code or env.get("ZOHO_ANALYTICS_AUTHORIZATION_CODE", "")).strip()
            missing = [
                name
                for name, value in {
                    "ZOHO_ANALYTICS_CLIENT_ID": client_id,
                    "ZOHO_ANALYTICS_CLIENT_SECRET": client_secret,
                    "ZOHO_ANALYTICS_AUTHORIZATION_CODE": code,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError("Variaveis obrigatorias ausentes: " + ", ".join(missing))
            token_data = ZohoAnalyticsClient.exchange_authorization_code(
                accounts_url=accounts_url,
                client_id=client_id,
                client_secret=client_secret,
                code=code,
            )
            print(json.dumps(token_data, ensure_ascii=False, indent=2))
            refresh_token = token_data.get("refresh_token")
            if refresh_token:
                print("\nUse este valor em ZOHO_ANALYTICS_REFRESH_TOKEN.")
            return 0

        if args.command in {"orgs", "workspaces"}:
            discovery_client = ZohoAnalyticsClient(ZohoAnalyticsConfig.from_env_for_discovery())
            token = discovery_client.refresh_access_token()
            if args.command == "orgs":
                _print_orgs(discovery_client.get_orgs(access_token=token))
            else:
                _print_workspaces(discovery_client.get_workspaces(access_token=token))
            return 0

        client = ZohoAnalyticsClient(ZohoAnalyticsConfig.from_env())
        token = client.refresh_access_token()

        if args.command == "token":
            print("Credenciais OK. Access token renovado com sucesso.")
            return 0
        if args.command == "views":
            _print_views(client.get_views(access_token=token, keyword=args.keyword))
            return 0
        if args.command == "export-view":
            if args.async_export:
                job_id = client.create_export_job_for_view(args.view_id, response_format=args.format, access_token=token)
                print(f"Job criado: {job_id}")
                if args.wait:
                    client.wait_for_export_job(job_id, access_token=token, interval_seconds=args.interval)
                    print(f"Arquivo salvo em: {client.download_export_job(job_id, args.out, access_token=token)}")
            else:
                print(f"Arquivo salvo em: {client.export_view_data(args.view_id, args.out, args.format, access_token=token)}")
            return 0
        if args.command == "export-sql":
            job_id = client.create_export_job_for_sql(args.sql, response_format=args.format, access_token=token)
            print(f"Job criado: {job_id}")
            if args.wait:
                client.wait_for_export_job(job_id, access_token=token, interval_seconds=args.interval)
                print(f"Arquivo salvo em: {client.download_export_job(job_id, args.out, access_token=token)}")
            return 0
        if args.command == "job-status":
            print(json.dumps(client.get_export_job(args.job_id, access_token=token), ensure_ascii=False, indent=2))
            return 0
        if args.command == "download-job":
            print(f"Arquivo salvo em: {client.download_export_job(args.job_id, args.out, access_token=token)}")
            return 0
    except Exception as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
