"""Orquestrador NL-SQL — geração de SQL em uma única chamada à API.

Fluxo:
  1. Carrega prompt do arquivo prompts/bi_suprimentos_sql.md
  2. Monta contexto com historico recente (opcional)
  3. Uma chamada à OpenAI — modelo retorna só SQL
  4. Extrai e valida SQL
  5. Executa no Zoho via adapter
  6. Salva em history.json
  7. Retorna resultado

Requer: OPENAI_API_KEY e OPENAI_MODEL em nlsql/.env
"""

from __future__ import annotations

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.adapter import run_query
from nlsql.guard import validate, SQLGuardError

# ── Config ───────────────────────────────────────────────────────────────────

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"
SQL_PROMPT_FILE = "bi_suprimentos_sql.md"
HISTORY_FILE = ROOT / "nlsql" / "history.json"

_NLSQL_ENV = ROOT / "nlsql" / ".env"
if _NLSQL_ENV.exists():
    for _line in _NLSQL_ENV.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
MAX_HISTORY_CONTEXT = 6  # últimas N perguntas no contexto


# ── Prompt ───────────────────────────────────────────────────────────────────

def _load_prompt() -> str:
    path = PROMPTS_DIR / SQL_PROMPT_FILE
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise RuntimeError(f"Prompt não encontrado: {path}")


# ── Extração de SQL ──────────────────────────────────────────────────────────

def _extract_sql(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    # Remover bloco markdown ```sql ... ```
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1)
    # Encontrar início do SELECT/WITH
    start = re.search(r"\b(with|select)\b", text, flags=re.IGNORECASE)
    if start:
        text = text[start.start():]
    text = text.replace("```sql", "").replace("```", "")
    text = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    return text.strip()


# ── Histórico ────────────────────────────────────────────────────────────────

def _load_history() -> list[dict[str, Any]]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_history(history: list[dict[str, Any]]) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(
        json.dumps(history[-200:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _record(
    question: str,
    sql: str,
    result: dict[str, Any],
    saved: bool = False,
) -> dict[str, Any]:
    entry = {
        "id": str(uuid.uuid4())[:8],
        "question": question,
        "sql": sql,
        "columns": [c["name"] for c in result.get("columns", [])],
        "row_count": result.get("row_count", 0),
        "elapsed_ms": result.get("elapsed_ms", 0),
        "status": "ok" if result.get("ok") else "error",
        "error": result.get("error", ""),
        "saved": saved,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    history = _load_history()
    history.append(entry)
    _save_history(history)
    return entry


def _build_context(history: list[dict[str, Any]]) -> str:
    """Constrói contexto das últimas perguntas para continuidade."""
    recent = [h for h in history[-MAX_HISTORY_CONTEXT * 2:] if h.get("status") == "ok"]
    if not recent:
        return ""
    lines = ["\nContexto das últimas consultas (use apenas para resolver referências como 'agora por UF' ou 'o mesmo por mês'):"]
    for h in recent[-MAX_HISTORY_CONTEXT:]:
        lines.append(f"- Pergunta: {h['question']}")
        if h.get("sql"):
            lines.append(f"  SQL: {h['sql'][:200]}")
    return "\n".join(lines)


# ── API ───────────────────────────────────────────────────────────────────────

def _openai_client():
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("Instale openai: pip install openai")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada em nlsql/.env")
    return OpenAI(api_key=api_key)


# ── Função principal ─────────────────────────────────────────────────────────

def ask(
    question: str,
    verbose: bool = False,
    use_history: bool = True,
    save: bool = False,
) -> dict[str, Any]:
    """Pergunta em linguagem natural → SQL → execução → resultado.

    Args:
        question: pergunta em português
        verbose: imprime SQL e etapas intermediárias
        use_history: inclui últimas perguntas no contexto
        save: marca como salvo no histórico

    Returns:
        {
          "answer": str,      # resposta formatada
          "table": dict,      # resultado completo da query
          "sql_used": str,
          "record": dict,     # entrada gravada no histórico
        }
    """
    question = str(question or "").strip()
    if not question:
        return {"answer": "Pergunta vazia.", "table": None, "sql_used": None, "record": None}

    prompt = _load_prompt()
    history = _load_history() if use_history else []

    # Montar input com contexto opcional
    context = _build_context(history) if use_history else ""
    user_input = question
    if context:
        user_input = f"{question}{context}"

    if verbose:
        print(f"  [modelo: {MODEL}]", flush=True)
        print(f"  [gerando SQL...]", flush=True)

    # Chamar modelo
    client = _openai_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input},
        ],
        temperature=0,
        max_tokens=1500,
    )
    raw_response = response.choices[0].message.content or ""

    # Extrair SQL
    sql = _extract_sql(raw_response)
    if not sql:
        return {
            "answer": f"Não foi possível extrair SQL da resposta: {raw_response[:200]}",
            "table": None, "sql_used": None, "record": None,
        }

    if verbose:
        print(f"  [SQL: {sql[:120]}]", flush=True)

    # Validar
    try:
        safe_sql = validate(sql)
    except SQLGuardError as exc:
        return {
            "answer": f"SQL bloqueado pela validação: {exc}",
            "table": None, "sql_used": sql, "record": None,
        }

    # Executar
    if verbose:
        print(f"  [executando no Zoho...]", flush=True)

    result = run_query(safe_sql)

    # Formatar resposta
    if result.get("ok") and result.get("row_count", 0) > 0:
        answer = _format_answer(question, result)
    elif result.get("ok"):
        answer = "A consulta não retornou resultados."
    else:
        answer = f"Erro na execução: {result.get('error', 'desconhecido')}"

    # Gravar histórico
    record = _record(question, safe_sql, result, saved=save)

    return {
        "answer": answer,
        "table": result if result.get("ok") else None,
        "sql_used": safe_sql,
        "record": record,
    }


def _format_answer(question: str, result: dict[str, Any]) -> str:
    """Formata uma resposta simples baseada no resultado."""
    rows = result.get("rows", [])
    cols = [c["name"] for c in result.get("columns", [])]
    count = result.get("row_count", 0)
    elapsed = result.get("elapsed_ms", 0)
    trunc = " (resultado truncado)" if result.get("truncated") else ""

    lines = [f"{count} linha(s) retornada(s) em {elapsed}ms{trunc}."]

    # Se só 1 linha e poucas colunas, exibe inline
    if count == 1 and len(cols) <= 4:
        row = rows[0]
        parts = [f"{k}: {v}" for k, v in row.items()]
        lines.append(" | ".join(parts))
    elif count <= 5:
        for row in rows:
            parts = [f"{k}: {v}" for k, v in list(row.items())[:5]]
            lines.append("  " + " | ".join(parts))

    return "\n".join(lines)


# ── Utilitários de histórico ─────────────────────────────────────────────────

def get_history(limit: int = 50, saved_only: bool = False) -> list[dict[str, Any]]:
    history = _load_history()
    if saved_only:
        history = [h for h in history if h.get("saved")]
    return list(reversed(history[-limit:]))


def mark_saved(record_id: str) -> bool:
    history = _load_history()
    for entry in history:
        if entry.get("id") == record_id:
            entry["saved"] = True
            _save_history(history)
            return True
    return False
