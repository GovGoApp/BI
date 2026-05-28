from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = BASE_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from zoho_analytics_client import (  # noqa: E402
    ZohoAnalyticsClient,
    ZohoAnalyticsConfig,
    ZohoAnalyticsError,
    load_env_file,
)


class FakeResponse:
    def __init__(self, status_code: int = 200, data: dict | None = None, content: bytes = b"", text: str = "") -> None:
        self.status_code = status_code
        self._data = data if data is not None else {}
        self.content = content
        self.text = text or json.dumps(self._data)

    def json(self) -> dict:
        return self._data


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def request(self, method: str, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("FakeSession sem respostas configuradas")
        return self.responses.pop(0)


def config() -> ZohoAnalyticsConfig:
    return ZohoAnalyticsConfig(
        accounts_url="https://accounts.zoho.com",
        analytics_url="https://analyticsapi.zoho.com",
        client_id="client-id",
        client_secret="client-secret",
        refresh_token="refresh-token",
        org_id="123",
        workspace_id="456",
    )


class ZohoAnalyticsConfigTests(unittest.TestCase):
    def test_load_env_file_sets_variables_and_ignores_comments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "zoho.env"
            path.write_text(
                "\n".join(
                    [
                        "# comentario",
                        "ZOHO_ANALYTICS_CLIENT_ID=client",
                        'ZOHO_ANALYTICS_CLIENT_SECRET="secret"',
                    ]
                ),
                encoding="utf-8",
            )

            loaded = load_env_file(path)

        self.assertEqual("client", loaded["ZOHO_ANALYTICS_CLIENT_ID"])
        self.assertEqual("secret", loaded["ZOHO_ANALYTICS_CLIENT_SECRET"])

    def test_from_env_requires_core_variables(self) -> None:
        with self.assertRaises(ValueError) as raised:
            ZohoAnalyticsConfig.from_env({})
        self.assertIn("ZOHO_ANALYTICS_CLIENT_ID", str(raised.exception))
        self.assertIn("ZOHO_ANALYTICS_WORKSPACE_ID", str(raised.exception))

    def test_from_env_uses_default_domains(self) -> None:
        loaded = ZohoAnalyticsConfig.from_env(
            {
                "ZOHO_ANALYTICS_CLIENT_ID": "client",
                "ZOHO_ANALYTICS_CLIENT_SECRET": "secret",
                "ZOHO_ANALYTICS_REFRESH_TOKEN": "refresh",
                "ZOHO_ANALYTICS_ORG_ID": "org",
                "ZOHO_ANALYTICS_WORKSPACE_ID": "workspace",
            }
        )
        self.assertEqual("https://accounts.zoho.com", loaded.accounts_url)
        self.assertEqual("https://analyticsapi.zoho.com", loaded.analytics_url)

    def test_from_env_for_discovery_does_not_require_org_or_workspace(self) -> None:
        loaded = ZohoAnalyticsConfig.from_env_for_discovery(
            {
                "ZOHO_ANALYTICS_CLIENT_ID": "client",
                "ZOHO_ANALYTICS_CLIENT_SECRET": "secret",
                "ZOHO_ANALYTICS_REFRESH_TOKEN": "refresh",
            }
        )
        self.assertEqual("", loaded.org_id)
        self.assertEqual("", loaded.workspace_id)


class ZohoAnalyticsClientTests(unittest.TestCase):
    def test_refresh_access_token_posts_to_accounts_url(self) -> None:
        session = FakeSession([FakeResponse(data={"access_token": "access-token", "expires_in": 3600})])
        client = ZohoAnalyticsClient(config(), session=session)

        token = client.refresh_access_token()

        self.assertEqual("access-token", token)
        call = session.calls[0]
        self.assertEqual("POST", call["method"])
        self.assertEqual("https://accounts.zoho.com/oauth/v2/token", call["url"])
        self.assertEqual("refresh_token", call["kwargs"]["params"]["grant_type"])
        self.assertEqual("client-id", call["kwargs"]["params"]["client_id"])

    def test_exchange_authorization_code_returns_refresh_token(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    data={
                        "access_token": "access-token",
                        "refresh_token": "refresh-token",
                        "expires_in": 3600,
                    }
                )
            ]
        )

        data = ZohoAnalyticsClient.exchange_authorization_code(
            accounts_url="https://accounts.zoho.com",
            client_id="client-id",
            client_secret="client-secret",
            code="grant-code",
            session=session,
        )

        self.assertEqual("refresh-token", data["refresh_token"])
        call = session.calls[0]
        self.assertEqual("POST", call["method"])
        self.assertEqual("https://accounts.zoho.com/oauth/v2/token", call["url"])
        self.assertEqual("authorization_code", call["kwargs"]["params"]["grant_type"])
        self.assertEqual("grant-code", call["kwargs"]["params"]["code"])

    def test_get_views_sends_org_and_oauth_headers(self) -> None:
        session = FakeSession(
            [
                FakeResponse(
                    data={
                        "status": "success",
                        "data": {"views": [{"viewId": "789", "viewName": "Compras", "viewType": "Table"}]},
                    }
                )
            ]
        )
        client = ZohoAnalyticsClient(config(), session=session)

        data = client.get_views(access_token="access-token", view_types=[0])

        self.assertEqual("success", data["status"])
        call = session.calls[0]
        self.assertEqual("GET", call["method"])
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/workspaces/456/views", call["url"])
        self.assertEqual("123", call["kwargs"]["headers"]["ZANALYTICS-ORGID"])
        self.assertEqual("Zoho-oauthtoken access-token", call["kwargs"]["headers"]["Authorization"])
        self.assertEqual({"viewTypes": [0]}, json.loads(call["kwargs"]["params"]["CONFIG"]))

    def test_get_orgs_uses_metadata_endpoint_without_org_header(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "success", "data": {"orgs": []}})])
        client = ZohoAnalyticsClient(config(), session=session)

        data = client.get_orgs(access_token="access-token")

        self.assertEqual("success", data["status"])
        call = session.calls[0]
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/orgs", call["url"])
        self.assertEqual({"Authorization": "Zoho-oauthtoken access-token"}, call["kwargs"]["headers"])

    def test_get_workspaces_uses_metadata_endpoint_without_org_header(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "success", "data": {"ownedWorkspaces": []}})])
        client = ZohoAnalyticsClient(config(), session=session)

        data = client.get_workspaces(access_token="access-token")

        self.assertEqual("success", data["status"])
        call = session.calls[0]
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/workspaces", call["url"])
        self.assertEqual({"Authorization": "Zoho-oauthtoken access-token"}, call["kwargs"]["headers"])

    def test_create_export_job_for_view_encodes_config_and_returns_job_id(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "success", "data": {"jobId": "job-123"}})])
        client = ZohoAnalyticsClient(config(), session=session)

        job_id = client.create_export_job_for_view("789", access_token="access-token", response_format="csv")

        self.assertEqual("job-123", job_id)
        call = session.calls[0]
        self.assertEqual(
            "https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/456/views/789/data",
            call["url"],
        )
        self.assertEqual({"responseFormat": "csv"}, json.loads(call["kwargs"]["params"]["CONFIG"]))

    def test_create_export_job_for_sql_uses_bulk_workspace_data_endpoint(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "success", "data": {"jobId": "job-sql"}})])
        client = ZohoAnalyticsClient(config(), session=session)

        job_id = client.create_export_job_for_sql("select * from Compras", access_token="access-token")

        self.assertEqual("job-sql", job_id)
        call = session.calls[0]
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/456/data", call["url"])
        self.assertEqual(
            {"sqlQuery": "select * from Compras", "responseFormat": "csv"},
            json.loads(call["kwargs"]["params"]["CONFIG"]),
        )

    def test_download_export_job_writes_file(self) -> None:
        session = FakeSession([FakeResponse(content=b"col\nvalor\n")])
        client = ZohoAnalyticsClient(config(), session=session)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "zoho.csv"
            path = client.download_export_job("job-123", out, access_token="access-token")

            self.assertEqual(out, path)
            self.assertEqual(b"col\nvalor\n", out.read_bytes())

    def test_json_failure_response_raises_error(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "failure", "errorCode": 7103})])
        client = ZohoAnalyticsClient(config(), session=session)

        with self.assertRaises(ZohoAnalyticsError):
            client.get_views(access_token="access-token")


if __name__ == "__main__":
    unittest.main()
