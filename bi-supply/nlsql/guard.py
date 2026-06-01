"""Valida que o SQL gerado pelo modelo é somente leitura.

Aceita apenas SELECT ou WITH ... SELECT.
Bloqueia DDL, DML, comandos administrativos e múltiplos statements.
"""

from __future__ import annotations

import re

_BLOCKED = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|COPY|GRANT|REVOKE"
    r"|EXEC|EXECUTE|CALL|PRAGMA|VACUUM|ATTACH|DETACH|LOAD)\b",
    re.IGNORECASE,
)

_ALLOWED_START = re.compile(
    r"^\s*(SELECT|WITH)\b",
    re.IGNORECASE,
)

# Limit máximo de linhas injetado automaticamente se ausente
DEFAULT_LIMIT = 500
_HAS_LIMIT = re.compile(r"\bLIMIT\s+\d+", re.IGNORECASE)


class SQLGuardError(ValueError):
    pass


def validate(sql: str) -> str:
    """Valida e normaliza o SQL. Retorna SQL pronto para execução.

    - Verifica que começa com SELECT ou WITH
    - Bloqueia palavras-chave destrutivas
    - Bloqueia múltiplos statements (;)
    - Injeta LIMIT se ausente

    Raises:
        SQLGuardError: se o SQL não for seguro
    """
    sql = sql.strip().rstrip(";")

    # Múltiplos statements
    if ";" in sql:
        raise SQLGuardError("Múltiplos statements não são permitidos.")

    # Deve começar com SELECT ou WITH
    if not _ALLOWED_START.match(sql):
        raise SQLGuardError(
            f"Apenas SELECT ou WITH ... SELECT são permitidos. SQL recebido: {sql[:80]}"
        )

    # Palavras-chave bloqueadas
    m = _BLOCKED.search(sql)
    if m:
        raise SQLGuardError(f"Palavra-chave não permitida: {m.group(0).upper()}")

    # Injetar LIMIT se ausente
    if not _HAS_LIMIT.search(sql):
        sql = f"{sql} LIMIT {DEFAULT_LIMIT}"

    return sql
