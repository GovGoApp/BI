"""Testes do SQL guard — sem chamadas à API ou ao Zoho."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.guard import validate, SQLGuardError


class TestGuard(unittest.TestCase):

    # ── Casos válidos ──────────────────────────────────────────────────────

    def test_select_simples_passa(self):
        sql = validate('SELECT * FROM "NFE" LIMIT 10')
        self.assertIn("SELECT", sql.upper())

    def test_with_select_passa(self):
        sql = validate('WITH x AS (SELECT 1) SELECT * FROM x')
        self.assertIn("WITH", sql.upper())

    def test_injeta_limit_se_ausente(self):
        sql = validate('SELECT "ID" FROM "NFE"')
        self.assertIn("LIMIT", sql.upper())

    def test_nao_duplica_limit_existente(self):
        sql = validate('SELECT "ID" FROM "NFE" LIMIT 50')
        self.assertEqual(sql.upper().count("LIMIT"), 1)

    def test_remove_ponto_virgula_final(self):
        sql = validate('SELECT 1;')
        self.assertNotIn(";", sql)

    # ── Casos bloqueados ──────────────────────────────────────────────────

    def test_bloqueia_insert(self):
        with self.assertRaises(SQLGuardError):
            validate("INSERT INTO tabela VALUES (1)")

    def test_bloqueia_update(self):
        with self.assertRaises(SQLGuardError):
            validate("UPDATE tabela SET col = 1")

    def test_bloqueia_delete(self):
        with self.assertRaises(SQLGuardError):
            validate("DELETE FROM tabela")

    def test_bloqueia_drop(self):
        with self.assertRaises(SQLGuardError):
            validate("DROP TABLE NFE")

    def test_bloqueia_create(self):
        with self.assertRaises(SQLGuardError):
            validate("CREATE TABLE x (id INT)")

    def test_bloqueia_alter(self):
        with self.assertRaises(SQLGuardError):
            validate("ALTER TABLE NFE ADD col INT")

    def test_bloqueia_multiplos_statements(self):
        with self.assertRaises(SQLGuardError):
            validate("SELECT 1; SELECT 2")

    def test_bloqueia_nao_select(self):
        with self.assertRaises(SQLGuardError):
            validate("SHOW TABLES")

    def test_bloqueia_exec(self):
        with self.assertRaises(SQLGuardError):
            validate("EXEC sp_something")

    # ── Casos de segurança via injeção ───────────────────────────────────

    def test_bloqueia_drop_dentro_de_select(self):
        with self.assertRaises(SQLGuardError):
            validate("SELECT * FROM x; DROP TABLE y")

    def test_permite_insert_dentro_de_string_literal(self):
        # INSERT dentro de string literal é mascarado antes da checagem — deve passar
        sql = validate("SELECT * FROM \"NFE\" WHERE \"NMPRODUTO_OFICIAL\" = 'INSERT NUTRI'")
        self.assertIn("SELECT", sql.upper())

    def test_bloqueia_insert_fora_de_string(self):
        # INSERT fora de string (como comando real) deve ser bloqueado
        with self.assertRaises(SQLGuardError):
            validate("INSERT INTO tabela VALUES (1)")


if __name__ == "__main__":
    unittest.main()
