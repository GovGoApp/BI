"""Testes unitários para zoho/client.py — sem chamadas reais à API Zoho."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zoho.client import ZohoClient, ZohoConfig, ZohoError, load_env_file


# ---------------------------------------------------------------------------
# Helpers de teste
# ---------------------------------------------------------------------------

class FakeResponse:
    """Simula requests.Response sem fazer HTTP."""

    def __init__(
        self,
        status_code: int = 200,
        data: dict | None = None,
        content: bytes = b"",
    ) -> None:
        self.status_code = status_code
        self._data = data if data is not None else {}
        self.content = content
        self.text = json.dumps(self._data)

    def json(self) -> dict:
        return self._data


class FakeSession:
    """Sessão HTTP falsa que devolve respostas pré-configuradas em sequência."""

    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    def _call(self, method: str, url: str, **kwargs) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        if not self._responses:
            raise AssertionError("FakeSession sem respostas configuradas")
        return self._responses.pop(0)

    def get(self, url: str, **kwargs) -> FakeResponse:
        return self._call("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> FakeResponse:
        return self._call("POST", url, **kwargs)


def _config() -> ZohoConfig:
    return ZohoConfig(
        client_id="client-id",
        client_secret="client-secret",
        refresh_token="refresh-token",
        org_id="123",
        workspace_id="456",
    )


def _ok(**extra) -> FakeResponse:
    return FakeResponse(data={"status": "success", **extra})


# ---------------------------------------------------------------------------
# Testes de ZohoConfig
# ---------------------------------------------------------------------------

class TestZohoConfig(unittest.TestCase):

    def test_load_env_file_carrega_variaveis_e_ignora_comentarios(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "zoho.env"
            path.write_text(
                "# comentario\n"
                "ZOHO_ANALYTICS_CLIENT_ID=client\n"
                'ZOHO_ANALYTICS_CLIENT_SECRET="secret"\n',
                encoding="utf-8",
            )
            loaded = load_env_file(path)

        self.assertEqual("client", loaded["ZOHO_ANALYTICS_CLIENT_ID"])
        self.assertEqual("secret", loaded["ZOHO_ANALYTICS_CLIENT_SECRET"])

    def test_from_env_falha_sem_variaveis_obrigatorias(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                ZohoConfig.from_env()
        self.assertIn("ZOHO_ANALYTICS_CLIENT_ID", str(ctx.exception))

    def test_from_env_carrega_corretamente(self) -> None:
        env = {
            "ZOHO_ANALYTICS_CLIENT_ID": "cid",
            "ZOHO_ANALYTICS_CLIENT_SECRET": "csecret",
            "ZOHO_ANALYTICS_REFRESH_TOKEN": "rtoken",
            "ZOHO_ANALYTICS_ORG_ID": "org1",
            "ZOHO_ANALYTICS_WORKSPACE_ID": "ws1",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = ZohoConfig.from_env()

        self.assertEqual("cid", cfg.client_id)
        self.assertEqual("org1", cfg.org_id)
        self.assertEqual("ws1", cfg.workspace_id)
        self.assertEqual("https://accounts.zoho.com", cfg.accounts_url)
        self.assertEqual("https://analyticsapi.zoho.com", cfg.analytics_url)

    def test_from_env_sem_workspace_quando_require_workspace_false(self) -> None:
        env = {
            "ZOHO_ANALYTICS_CLIENT_ID": "cid",
            "ZOHO_ANALYTICS_CLIENT_SECRET": "csecret",
            "ZOHO_ANALYTICS_REFRESH_TOKEN": "rtoken",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = ZohoConfig.from_env(require_workspace=False)

        self.assertEqual("", cfg.org_id)
        self.assertEqual("", cfg.workspace_id)

    def test_from_env_usa_urls_customizadas(self) -> None:
        env = {
            "ZOHO_ANALYTICS_CLIENT_ID": "cid",
            "ZOHO_ANALYTICS_CLIENT_SECRET": "csec",
            "ZOHO_ANALYTICS_REFRESH_TOKEN": "rtoken",
            "ZOHO_ANALYTICS_ORG_ID": "org",
            "ZOHO_ANALYTICS_WORKSPACE_ID": "ws",
            "ZOHO_ANALYTICS_ACCOUNTS_URL": "https://accounts.zoho.eu",
            "ZOHO_ANALYTICS_API_URL": "https://analyticsapi.zoho.eu",
        }
        with patch.dict("os.environ", env, clear=True):
            cfg = ZohoConfig.from_env()

        self.assertEqual("https://accounts.zoho.eu", cfg.accounts_url)
        self.assertEqual("https://analyticsapi.zoho.eu", cfg.analytics_url)


# ---------------------------------------------------------------------------
# Testes de ZohoClient
# ---------------------------------------------------------------------------

class TestZohoClientAuth(unittest.TestCase):

    def test_refresh_token_faz_post_e_retorna_token(self) -> None:
        session = FakeSession([FakeResponse(data={"access_token": "tok-123", "expires_in": 3600})])
        client = ZohoClient(_config(), session=session)

        token = client.refresh_token()

        self.assertEqual("tok-123", token)
        call = session.calls[0]
        self.assertEqual("POST", call["method"])
        self.assertEqual("https://accounts.zoho.com/oauth/v2/token", call["url"])
        self.assertEqual("refresh_token", call["params"]["grant_type"])
        self.assertEqual("client-id", call["params"]["client_id"])

    def test_refresh_token_levanta_erro_sem_access_token(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "failure"})])
        client = ZohoClient(_config(), session=session)

        with self.assertRaises(ZohoError):
            client.refresh_token()

    def test_exchange_code_faz_post_e_retorna_refresh_token(self) -> None:
        session = FakeSession([
            FakeResponse(data={"access_token": "at", "refresh_token": "rt", "expires_in": 3600})
        ])
        # exchange_code usa requests diretamente — precisamos mocar requests.post
        with patch("zoho.client.requests") as mock_requests:
            mock_requests.post.return_value = FakeResponse(
                data={"access_token": "at", "refresh_token": "rt", "expires_in": 3600}
            )
            result = ZohoClient.exchange_code(
                accounts_url="https://accounts.zoho.com",
                client_id="cid",
                client_secret="csec",
                code="grant-code",
            )

        self.assertEqual("rt", result["refresh_token"])


class TestZohoClientDiscovery(unittest.TestCase):

    def test_get_orgs_usa_endpoint_correto_sem_org_header(self) -> None:
        session = FakeSession([_ok(data={"orgs": []})])
        client = ZohoClient(_config(), session=session)

        data = client.get_orgs("access-token")

        self.assertEqual("success", data["status"])
        call = session.calls[0]
        self.assertEqual("GET", call["method"])
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/orgs", call["url"])
        self.assertNotIn("ZANALYTICS-ORGID", call.get("headers", {}))

    def test_get_workspaces_usa_endpoint_correto(self) -> None:
        session = FakeSession([_ok(data={"ownedWorkspaces": [], "sharedWorkspaces": []})])
        client = ZohoClient(_config(), session=session)

        data = client.get_workspaces("access-token")

        call = session.calls[0]
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/workspaces", call["url"])

    def test_get_views_envia_headers_corretos(self) -> None:
        session = FakeSession([_ok(data={"views": [{"viewId": "789", "viewName": "NFE", "viewType": "QueryTable"}]})])
        client = ZohoClient(_config(), session=session)

        data = client.get_views("access-token")

        call = session.calls[0]
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/workspaces/456/views", call["url"])
        self.assertEqual("123", call["headers"]["ZANALYTICS-ORGID"])
        self.assertEqual("Zoho-oauthtoken access-token", call["headers"]["Authorization"])

    def test_get_views_com_keyword_envia_config(self) -> None:
        session = FakeSession([_ok(data={"views": []})])
        client = ZohoClient(_config(), session=session)

        client.get_views("access-token", keyword="NFE")

        call = session.calls[0]
        self.assertIn("CONFIG", call.get("params", {}))
        self.assertEqual({"keyword": "NFE"}, json.loads(call["params"]["CONFIG"]))


class TestZohoClientBulk(unittest.TestCase):

    def test_create_job_view_retorna_job_id(self) -> None:
        session = FakeSession([_ok(data={"jobId": "job-view-1"})])
        client = ZohoClient(_config(), session=session)

        job_id = client.create_job_view("789", "access-token")

        self.assertEqual("job-view-1", job_id)
        call = session.calls[0]
        self.assertEqual(
            "https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/456/views/789/data",
            call["url"],
        )
        self.assertEqual({"responseFormat": "csv"}, json.loads(call["params"]["CONFIG"]))

    def test_create_job_sql_usa_endpoint_bulk_workspace_data(self) -> None:
        session = FakeSession([_ok(data={"jobId": "job-sql-1"})])
        client = ZohoClient(_config(), session=session)

        job_id = client.create_job_sql("select * from NFE limit 10", "access-token")

        self.assertEqual("job-sql-1", job_id)
        call = session.calls[0]
        self.assertEqual("https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/456/data", call["url"])
        config_sent = json.loads(call["params"]["CONFIG"])
        self.assertEqual("select * from NFE limit 10", config_sent["sqlQuery"])
        self.assertEqual("csv", config_sent["responseFormat"])

    def test_job_status_usa_endpoint_exportjobs(self) -> None:
        session = FakeSession([_ok(data={"jobId": "job-1", "jobCode": "1002"})])
        client = ZohoClient(_config(), session=session)

        client.job_status("job-1", "access-token")

        call = session.calls[0]
        self.assertEqual(
            "https://analyticsapi.zoho.com/restapi/v2/bulk/workspaces/456/exportjobs/job-1",
            call["url"],
        )

    def test_wait_job_retorna_quando_job_completo(self) -> None:
        responses = [
            _ok(data={"jobId": "job-1", "jobCode": "1002"}),
            _ok(data={"jobId": "job-1", "jobCode": "1004"}),
        ]
        session = FakeSession(responses)
        client = ZohoClient(_config(), session=session)

        result = client.wait_job("job-1", "access-token", interval=0)

        self.assertEqual(2, len(session.calls))
        self.assertEqual("1004", result["data"]["jobCode"])

    def test_wait_job_levanta_erro_em_job_falho(self) -> None:
        session = FakeSession([_ok(data={"jobId": "job-1", "jobCode": "1003"})])
        client = ZohoClient(_config(), session=session)

        with self.assertRaises(ZohoError):
            client.wait_job("job-1", "access-token", interval=0)

    def test_wait_job_levanta_erro_apos_max_tentativas(self) -> None:
        session = FakeSession([_ok(data={"jobCode": "1002"})] * 3)
        client = ZohoClient(_config(), session=session)

        with self.assertRaises(ZohoError):
            client.wait_job("job-1", "access-token", interval=0, max_attempts=3)

    def test_download_job_salva_arquivo(self) -> None:
        session = FakeSession([FakeResponse(content=b"col\nvalor\n")])
        client = ZohoClient(_config(), session=session)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "resultado.csv"
            path = client.download_job("job-1", out, "access-token")

            self.assertEqual(out, path)
            self.assertEqual(b"col\nvalor\n", out.read_bytes())

    def test_download_job_cria_diretorios_intermediarios(self) -> None:
        session = FakeSession([FakeResponse(content=b"data")])
        client = ZohoClient(_config(), session=session)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "sub" / "dir" / "resultado.csv"
            client.download_job("job-1", out, "access-token")
            self.assertTrue(out.exists())


class TestZohoClientErros(unittest.TestCase):

    def test_resposta_failure_levanta_zoho_error(self) -> None:
        session = FakeSession([FakeResponse(data={"status": "failure", "errorCode": 7103})])
        client = ZohoClient(_config(), session=session)

        with self.assertRaises(ZohoError):
            client.get_views("access-token")

    def test_http_4xx_levanta_zoho_error(self) -> None:
        session = FakeSession([FakeResponse(status_code=401)])
        client = ZohoClient(_config(), session=session)

        with self.assertRaises(ZohoError):
            client.get_views("access-token")

    def test_json_sem_job_id_levanta_erro(self) -> None:
        session = FakeSession([_ok(data={"sem_job_id": True})])
        client = ZohoClient(_config(), session=session)

        with self.assertRaises(ZohoError):
            client.create_job_sql("select 1", "access-token")


if __name__ == "__main__":
    unittest.main()
