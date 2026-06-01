"""Valida que o SQL gerado pelo modelo é somente leitura.

Aceita apenas SELECT ou WITH ... SELECT.
Bloqueia DDL, DML, comandos administrativos e múltiplos statements.
Usa mascaramento de strings/comentários antes de checar palavras bloqueadas
para evitar falsos positivos.
"""

from __future__ import annotations

import re

_BLOCKED = {
    "alter", "call", "copy", "create", "delete", "drop", "execute",
    "grant", "insert", "listen", "merge", "notify", "reindex",
    "revoke", "truncate", "unlisten", "update", "vacuum",
}

DEFAULT_LIMIT = 500
_HAS_LIMIT = re.compile(r"\blimit\s+\d+", re.IGNORECASE)
_STARTS_SELECT = re.compile(r"^\s*(select|with)\b", re.IGNORECASE)


class SQLGuardError(ValueError):
    pass


def _mask_strings_and_comments(sql: str) -> str:
    """Substitui conteúdo de strings e comentários por espaços.
    Evita falsos positivos em palavras bloqueadas dentro de strings.
    """
    chars = list(sql)
    i = 0
    in_single = in_double = in_line = in_block = False

    while i < len(chars):
        c = chars[i]
        n = chars[i + 1] if i + 1 < len(chars) else ""

        if in_line:
            if c == "\n":
                in_line = False
            else:
                chars[i] = " "
            i += 1
            continue

        if in_block:
            chars[i] = " "
            if c == "*" and n == "/":
                chars[i + 1] = " "
                in_block = False
                i += 2
            else:
                i += 1
            continue

        if in_single:
            chars[i] = " "
            if c == "'" and n == "'":
                chars[i + 1] = " "
                i += 2
                continue
            if c == "'":
                in_single = False
            i += 1
            continue

        if in_double:
            chars[i] = " "
            if c == '"' and n == '"':
                chars[i + 1] = " "
                i += 2
                continue
            if c == '"':
                in_double = False
            i += 1
            continue

        if c == "-" and n == "-":
            chars[i] = chars[i + 1] = " "
            in_line = True
            i += 2
            continue
        if c == "/" and n == "*":
            chars[i] = chars[i + 1] = " "
            in_block = True
            i += 2
            continue
        if c == "'":
            chars[i] = " "
            in_single = True
            i += 1
            continue
        if c == '"':
            chars[i] = " "
            in_double = True
            i += 1
            continue
        i += 1

    return "".join(chars)


def validate(sql: str) -> str:
    """Valida e normaliza o SQL. Retorna SQL pronto para execução.

    Raises:
        SQLGuardError: se o SQL não for seguro
    """
    raw = str(sql or "").strip().rstrip(";")
    if not raw:
        raise SQLGuardError("SQL vazio.")

    masked = _mask_strings_and_comments(raw)

    # Múltiplos statements
    if ";" in masked:
        raise SQLGuardError("Múltiplos statements não são permitidos.")

    # Deve começar com SELECT ou WITH
    if not _STARTS_SELECT.match(masked):
        raise SQLGuardError(
            f"Apenas SELECT ou WITH ... SELECT são permitidos. SQL: {raw[:80]}"
        )

    # Palavras bloqueadas no SQL mascarado
    normalized = masked.lower()
    found = sorted({kw for kw in _BLOCKED if re.search(rf"\b{kw}\b", normalized)})
    if found:
        raise SQLGuardError(
            f"Palavra-chave não permitida: {', '.join(found).upper()}"
        )

    # SELECT INTO
    if re.search(r"\bselect\b[\s\S]*\binto\b", normalized):
        raise SQLGuardError("SELECT INTO não é permitido.")

    # Injetar LIMIT se ausente
    if not _HAS_LIMIT.search(normalized):
        raw = f"SELECT * FROM ({raw}) AS _report_query LIMIT {DEFAULT_LIMIT}"

    return raw
