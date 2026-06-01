"""Testes unitários para zoho/catalog.py."""

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

import zoho.catalog as catalog


# ---------------------------------------------------------------------------
# Perfil mínimo para testes (não depende do arquivo real)
# ---------------------------------------------------------------------------

_FAKE_PROFILE = {
    "NFE": {
        "columns": [
            {"name": "ID", "type": "texto", "sample": "RCSPI102101000"},
            {"name": "NMPRODUTO_OFICIAL", "type": "texto", "sample": "ARROZ AGULHINHA - KG"},
            {"name": "UF", "type": "texto", "sample": "SP"},
            {"name": "IMP_COT", "type": "decimal", "sample": "-20.7"},
            {"name": "PMP_ID", "type": "decimal", "sample": "3.50"},
            {"name": "CURVA_FORN", "type": "texto", "sample": "AAA"},
        ],
        "row_count": 5,
    },
    "COT": {
        "columns": [
            {"name": "ID", "type": "texto", "sample": "RCMAI108105060"},
            {"name": "PRECOUNIT", "type": "decimal", "sample": "49.65"},
            {"name": "CURVA_FORN", "type": "texto", "sample": "AAA"},
            {"name": "MESANO", "type": "texto", "sample": "2026/03"},
        ],
        "row_count": 5,
    },
    "COT_MIN_FORN": {
        "columns": [
            {"name": "ID", "type": "texto", "sample": "MEESI102101000"},
            {"name": "PRECOUNIT_COT", "type": "decimal", "sample": "4.6"},
            {"name": "FORNE_FANTASIA", "type": "texto", "sample": "SUDESTE"},
        ],
        "row_count": 5,
    },
    "CP": {
        "columns": [
            {"name": "CDFORNECED", "type": "texto", "sample": "J44407989000128"},
            {"name": "VRATUAPAG", "type": "decimal", "sample": "1200.00"},
            {"name": "STATUSPAG", "type": "texto", "sample": "ABERTO"},
        ],
        "row_count": 5,
    },
    "AD_v3": {
        "columns": [
            {"name": "CDFORNECED", "type": "texto", "sample": "J13328409000183"},
            {"name": "STATUS_CONCILIACAO", "type": "texto", "sample": "CONCILIADO"},
            {"name": "VALOR_FINAL", "type": "decimal", "sample": "344.85"},
        ],
        "row_count": 5,
    },
    # Simular fonte sem perfil disponível
    "INFLAÇÃO": None,
}

# Preencher as demais fontes do GOLDEN com perfis vazios para não quebrar list_tables
_ALL_GOLDEN_KEYS = list(catalog.GOLDEN.keys())
for _k in _ALL_GOLDEN_KEYS:
    if _k not in _FAKE_PROFILE:
        _FAKE_PROFILE[_k] = {"columns": [{"name": "COL", "type": "texto", "sample": "x"}], "row_count": 1}


def _patch_profile(test_func):
    """Decorator que substitui o arquivo de perfil por _FAKE_PROFILE."""
    def wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_path = Path(tmp) / "suprimentos_profile.json"
            fake_path.write_text(json.dumps(_FAKE_PROFILE, ensure_ascii=False), encoding="utf-8")
            with patch.object(catalog, "PROFILE_PATH", fake_path):
                test_func(self)
    return wrapper


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------

class TestGoldenList(unittest.TestCase):
    def test_golden_tem_18_fontes(self):
        self.assertEqual(18, len(catalog.GOLDEN))

    def test_todas_as_fontes_tem_descricao_nao_vazia(self):
        for name, desc in catalog.GOLDEN.items():
            self.assertTrue(desc.strip(), f"Descrição vazia para '{name}'")

    def test_fontes_obrigatorias_presentes(self):
        obrigatorias = {"NFE", "COT", "CP", "AD_v3", "INFLAÇÃO", "FILIAIS_SUPPLY"}
        for fonte in obrigatorias:
            self.assertIn(fonte, catalog.GOLDEN, f"'{fonte}' ausente do GOLDEN")


class TestListTables(unittest.TestCase):
    @_patch_profile
    def test_retorna_18_fontes(self):
        tables = catalog.list_tables()
        self.assertEqual(18, len(tables))

    @_patch_profile
    def test_cada_entrada_tem_campos_obrigatorios(self):
        for t in catalog.list_tables():
            self.assertIn("table", t)
            self.assertIn("description", t)
            self.assertIn("column_count", t)
            self.assertIn("available", t)

    @_patch_profile
    def test_fonte_sem_perfil_aparece_como_indisponivel(self):
        tables = {t["table"]: t for t in catalog.list_tables()}
        self.assertFalse(tables["INFLAÇÃO"]["available"])
        self.assertEqual(0, tables["INFLAÇÃO"]["column_count"])

    def test_erro_sem_arquivo_de_perfil(self):
        with patch.object(catalog, "PROFILE_PATH", Path("/inexistente/perfil.json")):
            with self.assertRaises(FileNotFoundError):
                catalog.list_tables()


class TestDescribeTable(unittest.TestCase):
    @_patch_profile
    def test_retorna_colunas_corretamente(self):
        result = catalog.describe_table("NFE")
        self.assertEqual("NFE", result["table"])
        self.assertEqual(6, result["column_count"])
        nomes = [c["name"] for c in result["columns"]]
        self.assertIn("IMP_COT", nomes)
        self.assertIn("CURVA_FORN", nomes)

    @_patch_profile
    def test_inclui_descricao_de_dominio(self):
        result = catalog.describe_table("COT_MIN_FORN")
        self.assertIn("menor", result["description"].lower())

    def test_nome_fora_da_allowlist_levanta_key_error(self):
        with self.assertRaises(KeyError):
            catalog.describe_table("TABELA_INEXISTENTE")

    def test_nome_redundante_nao_esta_na_allowlist(self):
        with self.assertRaises(KeyError):
            catalog.describe_table("NFE - IDEAL")

    def test_nome_descartado_nao_esta_na_allowlist(self):
        with self.assertRaises(KeyError):
            catalog.describe_table("FORN_CP_25_26")


class TestSearchSchema(unittest.TestCase):
    @_patch_profile
    def test_busca_cotacao_retorna_cot_min_forn_primeiro(self):
        results = catalog.search_schema("cotacao menor preco fornecedor")
        self.assertTrue(len(results) > 0)
        self.assertEqual("COT_MIN_FORN", results[0]["table"])

    @_patch_profile
    def test_busca_cp_retorna_contas_pagar(self):
        results = catalog.search_schema("contas pagar")
        tabelas = [r["table"] for r in results]
        self.assertIn("CP", tabelas)

    @_patch_profile
    def test_busca_adiantamento_retorna_ad_v3_primeiro(self):
        results = catalog.search_schema("adiantamento conciliacao")
        self.assertTrue(len(results) > 0)
        self.assertEqual("AD_v3", results[0]["table"])

    @_patch_profile
    def test_resultado_tem_campos_obrigatorios(self):
        results = catalog.search_schema("produto preco")
        for r in results:
            self.assertIn("table", r)
            self.assertIn("description", r)
            self.assertIn("score", r)
            self.assertIn("relevant_columns", r)

    @_patch_profile
    def test_query_vazia_retorna_lista_vazia(self):
        results = catalog.search_schema("")
        self.assertEqual([], results)

    @_patch_profile
    def test_top_n_limita_resultados(self):
        results = catalog.search_schema("produto", top_n=2)
        self.assertLessEqual(len(results), 2)

    @_patch_profile
    def test_resultados_ordenados_por_score_decrescente(self):
        results = catalog.search_schema("cotacao")
        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    @_patch_profile
    def test_termo_sem_match_retorna_lista_vazia(self):
        results = catalog.search_schema("xyzabc123naoexiste")
        self.assertEqual([], results)


if __name__ == "__main__":
    unittest.main()
