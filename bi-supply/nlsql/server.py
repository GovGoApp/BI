"""
nlsql/server.py — Servidor Flask para a Aba Relatório do BI de Suprimentos.

Endpoints:
  POST /run             — pergunta → SQL → execução → título → histórico
  POST /generate-sql    — pergunta → SQL (sem executar)
  POST /execute         — SQL → execução direta
  GET  /history         — lista do histórico (com chats)
  GET  /history/<id>    — relatório completo
  DELETE /history/<id>  — soft delete
  POST /favorites/<id>  — toggle favorito
  GET  /prompt          — lê nlsql/prompts/bi_suprimentos_sql.md
  POST /prompt          — grava prompt (faz backup antes)
  GET  /export/<id>     — baixar CSV do relatório
  GET  /chats           — lista de chats
  POST /chats           — criar novo chat
  DELETE /chats/<id>    — deletar chat

Uso: python nlsql/server.py
     (ou: flask --app nlsql/server run --port 5001)
"""

from __future__ import annotations

import csv
import io
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

# Carrega .env do nlsql
_ENV = ROOT / "nlsql" / ".env"
if _ENV.exists():
    for _line in _ENV.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
except ImportError:
    print("Instale dependências: pip install flask flask-cors")
    sys.exit(1)

from nlsql.orchestrator import _load_prompt, _extract_sql, _build_context, _openai_client, MODEL
from nlsql.adapter import run_query

# ── Paths ──────────────────────────────────────────────────────────────────────

NLSQL_DIR      = ROOT / "nlsql"
HISTORY_FILE   = NLSQL_DIR / "history.json"
CHATS_FILE     = NLSQL_DIR / "chats.json"
PROMPT_DIR     = NLSQL_DIR / "prompts"
ACTIVE_VER_FILE = NLSQL_DIR / "active_version.txt"
PROMPT_VERSIONS = {
    "v1": PROMPT_DIR / "bi_suprimentos_sql_v1.md",
    "v2": PROMPT_DIR / "bi_suprimentos_sql_v2.md",
}

def _active_version() -> str:
    try: return ACTIVE_VER_FILE.read_text(encoding="utf-8").strip() or "v2"
    except: return "v2"

def _prompt_file(version: str | None = None) -> "Path":
    v = version or _active_version()
    return PROMPT_VERSIONS.get(v, PROMPT_VERSIONS["v2"])

def _prompt_bak(version: str | None = None) -> "Path":
    v = version or _active_version()
    return PROMPT_DIR / f"bi_suprimentos_sql_{v}.backup.md"

# Compatibilidade com código antigo
PROMPT_FILE = property(_prompt_file)   # não é mais usado diretamente
PROMPT_BAK  = property(_prompt_bak)
ELEMENTOS_FILE = ROOT / "docs" / "design" / "ELEMENTOS_BI.md"
ELEMENTS_FILE  = NLSQL_DIR / "elements.json"

# ── App ────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app, origins="*")

# ── Persistência ───────────────────────────────────────────────────────────────

def _rj(path: Path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def _wj(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _uid() -> str:
    return str(uuid.uuid4())

# ── História ───────────────────────────────────────────────────────────────────

def _load_history() -> list:
    return _rj(HISTORY_FILE)

def _save_history(h: list) -> None:
    _wj(HISTORY_FILE, h[-500:])

def _add_report(report: dict) -> None:
    h = _load_history()
    h.append(report)
    _save_history(h)

def _get_report(rid: str) -> dict | None:
    for r in reversed(_load_history()):
        if r.get("id") == rid and not r.get("deletedAt"):
            return r
    return None

# ── Chats ──────────────────────────────────────────────────────────────────────

def _load_chats() -> list:
    return _rj(CHATS_FILE)

def _save_chats(c: list) -> None:
    _wj(CHATS_FILE, c[-200:])

def _get_chat(cid: str) -> dict | None:
    for c in _load_chats():
        if c.get("id") == cid and not c.get("deletedAt"):
            return c
    return None

def _upsert_chat(chat: dict) -> None:
    chats = _load_chats()
    for i, c in enumerate(chats):
        if c["id"] == chat["id"]:
            chats[i] = chat
            _save_chats(chats)
            return
    chats.append(chat)
    _save_chats(chats)

def _build_msg_context(chat: dict, max_msgs: int = 12) -> list[dict]:
    """Últimas max_msgs mensagens do chat para contexto da IA."""
    msgs = chat.get("messages", [])[-max_msgs:]
    return [{"role": m["role"], "content": m.get("text", "") or m.get("sql", "")}
            for m in msgs if m.get("text") or m.get("sql")]

# ── Geração de SQL ─────────────────────────────────────────────────────────────

def _generate_sql(question: str, chat: dict | None = None) -> str:
    pf = _prompt_file()
    prompt = pf.read_text(encoding="utf-8") if pf.exists() else _load_prompt()
    context_msgs = _build_msg_context(chat) if chat else []

    # Monta input: pergunta + contexto
    if context_msgs:
        ctx_text = "\n\nContexto do chat (use para resolver referências como 'agora por UF'):\n"
        for m in context_msgs[-6:]:
            ctx_text += f"- {m['role']}: {m['content'][:300]}\n"
        user_input = question + ctx_text
    else:
        user_input = question

    client = _openai_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": user_input},
        ],
        temperature=0,
        max_tokens=1500,
    )
    raw = response.choices[0].message.content or ""
    return _extract_sql(raw)

# ── Geração de título ──────────────────────────────────────────────────────────

def _generate_title(question: str, sql: str, columns: list, rows: list) -> dict:
    sample = rows[:3] if rows else []
    prompt = f"""Você é um gerador de títulos para relatórios de dados.
Dado uma pergunta, SQL e amostra de dados, retorne JSON com "title" (max 70 chars) e "subtitle" (max 110 chars).
Não mencione SQL. Use linguagem analítica clara em português.

Pergunta: {question}
SQL: {sql[:300]}
Colunas: {columns}
Amostra (3 linhas): {json.dumps(sample[:3], ensure_ascii=False)[:500]}

Retorne apenas JSON: {{"title": "...", "subtitle": "..."}}"""

    try:
        client = _openai_client()
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=150,
            response_format={"type": "json_object"},
        )
        data = json.loads(r.choices[0].message.content or "{}")
        return {
            "title":    str(data.get("title",    question[:70])),
            "subtitle": str(data.get("subtitle", "")),
        }
    except Exception:
        return {"title": question[:70], "subtitle": ""}

# ── Endpoint: /run ─────────────────────────────────────────────────────────────

@app.route("/run", methods=["POST"])
def run():
    body     = request.get_json(force=True) or {}
    question = str(body.get("question", "")).strip()
    chat_id  = body.get("chatId") or _uid()

    if not question:
        return jsonify({"ok": False, "error": "Pergunta vazia."}), 400

    # Carregar ou criar chat
    chat = _get_chat(chat_id)
    if not chat:
        chat = {"id": chat_id, "title": question[:60], "messages": [],
                "reportIds": [], "createdAt": _now(), "updatedAt": _now()}

    # 1. Gerar SQL
    try:
        sql = _generate_sql(question, chat)
    except Exception as exc:
        return jsonify({"ok": False, "error": f"Erro ao gerar SQL: {exc}"}), 500

    if not sql:
        return jsonify({"ok": False, "error": "Não foi possível gerar SQL para essa pergunta."}), 422

    # 2. Executar no Zoho
    import time as _t; t0 = _t.monotonic()
    result = run_query(sql)
    elapsed = int((_t.monotonic() - t0) * 1000)

    # 3. Montar relatório
    rid = _uid()
    columns = [c["name"] if isinstance(c, dict) else c for c in result.get("columns", [])]
    rows    = result.get("rows", [])
    ok      = result.get("ok", False)

    # 4. Gerar título (apenas se ok)
    if ok and rows:
        titles = _generate_title(question, sql, columns, rows)
    else:
        titles = {"title": question[:70], "subtitle": ""}

    report = {
        "id":         rid,
        "chatId":     chat_id,
        "title":      titles["title"],
        "subtitle":   titles["subtitle"],
        "question":   question,
        "sql":        sql,
        "columns":    columns,
        "rows":       rows[:200],    # preview no histórico
        "rowCount":   result.get("row_count", len(rows)),
        "elapsedMs":  elapsed,
        "status":     "ok" if ok else "error",
        "error":      result.get("error", ""),
        "saved":      False,
        "createdAt":  _now(),
        "deletedAt":  None,
    }

    # 5. Atualizar chat
    user_msg = {"id": _uid(), "role": "user",      "text": question,
                "sql": None, "reportId": None, "createdAt": _now()}
    asst_msg = {"id": _uid(), "role": "assistant",
                "text": titles["title"] if ok else report["error"],
                "sql": sql, "reportId": rid,
                "reportTitle": titles["title"], "rowCount": report["rowCount"],
                "status": report["status"], "createdAt": _now()}
    chat["messages"].extend([user_msg, asst_msg])
    chat["reportIds"] = (chat.get("reportIds", []) + [rid])[-200:]
    chat["updatedAt"] = _now()
    if len(chat["messages"]) == 2:  # primeira mensagem → define título
        chat["title"] = question[:60]

    _add_report(report)
    _upsert_chat(chat)

    history = _visible_history()
    chats   = _visible_chats()

    return jsonify({"ok": True, "report": report, "chat": chat,
                    "history": history[:50], "chats": chats[:50]})

# ── Endpoint: /generate-sql ───────────────────────────────────────────────────

@app.route("/generate-sql", methods=["POST"])
def generate_sql_endpoint():
    body     = request.get_json(force=True) or {}
    question = str(body.get("question", "")).strip()
    chat_id  = body.get("chatId")
    chat     = _get_chat(chat_id) if chat_id else None

    if not question:
        return jsonify({"ok": False, "error": "Pergunta vazia."}), 400

    try:
        sql = _generate_sql(question, chat)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500

    return jsonify({"ok": True, "sql": sql})

# ── Endpoint: /execute ────────────────────────────────────────────────────────

@app.route("/execute", methods=["POST"])
def execute_endpoint():
    body = request.get_json(force=True) or {}
    sql  = str(body.get("sql", "")).strip()
    if not sql:
        return jsonify({"ok": False, "error": "SQL vazio."}), 400

    import time as _t; t0 = _t.monotonic()
    result = run_query(sql)
    elapsed = int((_t.monotonic() - t0) * 1000)

    columns = [c["name"] if isinstance(c, dict) else c for c in result.get("columns", [])]
    return jsonify({
        "ok":       result.get("ok", False),
        "columns":  columns,
        "rows":     result.get("rows", []),
        "rowCount": result.get("row_count", 0),
        "elapsedMs": elapsed,
        "error":    result.get("error", ""),
    })

# ── Endpoint: /history ────────────────────────────────────────────────────────

def _visible_history() -> list:
    return [r for r in reversed(_load_history()) if not r.get("deletedAt")]

def _visible_chats() -> list:
    return [c for c in reversed(_load_chats()) if not c.get("deletedAt")]

@app.route("/history", methods=["GET"])
def get_history():
    saved_only = request.args.get("saved") == "1"
    h = _visible_history()
    if saved_only:
        h = [r for r in h if r.get("saved")]
    return jsonify({"ok": True, "history": h[:100],
                    "chats": _visible_chats()[:50]})

@app.route("/history/<rid>", methods=["GET"])
def get_report(rid):
    r = _get_report(rid)
    if not r:
        return jsonify({"ok": False, "error": "Não encontrado."}), 404
    return jsonify({"ok": True, "report": r})

@app.route("/history/<rid>", methods=["DELETE"])
def delete_report(rid):
    h = _load_history()
    for r in h:
        if r.get("id") == rid:
            r["deletedAt"] = _now()
            _save_history(h)
            return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Não encontrado."}), 404

# ── Endpoint: /favorites/<id> ─────────────────────────────────────────────────

@app.route("/favorites/<rid>", methods=["POST"])
def toggle_favorite(rid):
    h = _load_history()
    for r in h:
        if r.get("id") == rid:
            r["saved"] = not r.get("saved", False)
            _save_history(h)
            return jsonify({"ok": True, "saved": r["saved"]})
    return jsonify({"ok": False, "error": "Não encontrado."}), 404

# ── Endpoint: /chats ──────────────────────────────────────────────────────────

@app.route("/chats", methods=["GET"])
def get_chats():
    return jsonify({"ok": True, "chats": _visible_chats()[:50]})

@app.route("/chats", methods=["POST"])
def create_chat():
    body  = request.get_json(force=True) or {}
    title = str(body.get("title", "Novo chat"))[:60]
    chat  = {"id": _uid(), "title": title, "messages": [],
             "reportIds": [], "createdAt": _now(), "updatedAt": _now()}
    _upsert_chat(chat)
    return jsonify({"ok": True, "chat": chat})

@app.route("/chats/<cid>", methods=["DELETE"])
def delete_chat(cid):
    chats = _load_chats()
    for c in chats:
        if c.get("id") == cid:
            c["deletedAt"] = _now()
            _save_chats(chats)
            return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Não encontrado."}), 404

# ── Endpoints: /prompt ────────────────────────────────────────────────────────

@app.route("/prompt/versions", methods=["GET"])
def get_prompt_versions():
    active = _active_version()
    versions = []
    for v, path in PROMPT_VERSIONS.items():
        if not path.exists():
            continue
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
        size  = path.stat().st_size
        versions.append({"version": v, "filename": path.name, "updatedAt": mtime,
                          "sizeBytes": size, "active": v == active})
    return jsonify({"ok": True, "versions": versions, "active": active})

@app.route("/prompt/activate", methods=["POST"])
def activate_prompt():
    body = request.get_json(force=True) or {}
    v    = str(body.get("version", "")).strip()
    if v not in PROMPT_VERSIONS:
        return jsonify({"ok": False, "error": f"Versão desconhecida: {v}"}), 400
    ACTIVE_VER_FILE.write_text(v, encoding="utf-8")
    return jsonify({"ok": True, "active": v})

@app.route("/prompt", methods=["GET"])
def get_prompt():
    version = request.args.get("version")       # ?version=v1 para ver versão específica
    pf  = _prompt_file(version)
    bak = _prompt_bak(version)
    if not pf.exists():
        return jsonify({"ok": False, "error": "Prompt não encontrado."}), 404
    content = pf.read_text(encoding="utf-8")
    mtime   = datetime.fromtimestamp(pf.stat().st_mtime, tz=timezone.utc).isoformat()
    return jsonify({"ok": True, "content": content, "updatedAt": mtime,
                    "version": version or _active_version(),
                    "hasBackup": bak.exists()})

@app.route("/prompt", methods=["POST"])
def save_prompt():
    body    = request.get_json(force=True) or {}
    content = body.get("content", "")
    version = str(body.get("version", "")).strip() or _active_version()
    if not content.strip():
        return jsonify({"ok": False, "error": "Conteúdo vazio."}), 400
    pf  = _prompt_file(version)
    bak = _prompt_bak(version)
    if pf.exists():
        bak.write_text(pf.read_text(encoding="utf-8"), encoding="utf-8")
    pf.write_text(content, encoding="utf-8")
    return jsonify({"ok": True, "backup": bak.name, "updatedAt": _now(), "version": version})

@app.route("/prompt/reset", methods=["POST"])
def reset_prompt():
    body    = request.get_json(force=True) or {}
    version = str(body.get("version", "")).strip() or _active_version()
    pf  = _prompt_file(version)
    bak = _prompt_bak(version)
    if not bak.exists():
        return jsonify({"ok": False, "error": "Sem backup disponível."}), 404
    pf.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
    return jsonify({"ok": True, "version": version})

# ── Endpoint: /export/<id> ────────────────────────────────────────────────────

@app.route("/export/<rid>", methods=["GET"])
def export_report(rid):
    r = _get_report(rid)
    if not r:
        return jsonify({"ok": False, "error": "Não encontrado."}), 404

    cols = r.get("columns", [])
    rows = r.get("rows", [])

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(cols)
    for row in rows:
        writer.writerow([row.get(c, "") for c in cols])

    filename = f"BI_Relatorio_{rid[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        out.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ── Endpoint: /classify ───────────────────────────────────────────────────────

_CLASSIFY_BASE = """Você é especialista em visualização de dados para BI de suprimentos.
Analise o resultado de uma query SQL e sugira os 1-3 melhores tipos de elemento visual.

REGRAS OBRIGATÓRIAS:
- Use APENAS os nomes de colunas exatos fornecidos no input (nunca invente nomes)
- Para GE: retorne {x, group, value} — dados de 3 colunas não pivotados
- Para KPI: config deve ter {chave, fmt} onde fmt é: brl, pct, num, dec ou str
- Para HL: config deve ter {label, value} — nomes das colunas
- Para GL: config deve ter {x, y, color} — x=período, y=numérico
- Para GB: config deve ter {x, y, color}
- Para MX: config deve ter {row_key, col_key, val_key}
- Para T/TE: config pode ser {} (colunas auto-detectadas) ou ter {colunas:[{key,label}]}
- confidence: float 0.0–1.0 (não precisa somar 1.0)
- reason: 1-2 frases em português, direto ao ponto

Retorne APENAS JSON válido:
{"suggestions": [{"tipo": "HL", "confidence": 0.92, "reason": "...", "config": {...}}]}

Tipos válidos: KPI, GL, GB, GE, HL, T, TE, MX, FU

GUIA COMPLETO DE ELEMENTOS:
"""

def _classify_system() -> str:
    guide = ELEMENTOS_FILE.read_text(encoding="utf-8") if ELEMENTOS_FILE.exists() else ""
    return _CLASSIFY_BASE + guide


@app.route("/classify", methods=["POST"])
def classify_element():
    body      = request.get_json(force=True) or {}
    question  = str(body.get("question", ""))[:300]
    sql       = str(body.get("sql", ""))[:600]
    columns   = body.get("columns", [])        # lista de strings com nomes
    rows      = body.get("rows", [])[:5]        # amostra de até 5 linhas
    row_count = int(body.get("rowCount", 0))

    user_msg = (
        f"Pergunta: {question}\n"
        f"SQL: {sql}\n"
        f"Colunas: {json.dumps(columns, ensure_ascii=False)}\n"
        f"Total de linhas: {row_count}\n"
        f"Amostra (até 5 linhas):\n{json.dumps(rows, ensure_ascii=False)[:1200]}\n\n"
        "Qual(is) tipo(s) de elemento visual melhor representam este resultado?"
    )

    try:
        client = _openai_client()
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": _classify_system()},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0,
            max_tokens=700,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")
        suggestions = data.get("suggestions", [])
        # valida tipos
        VALID = {"KPI","GL","GB","GE","HL","T","TE","MX","FU"}
        suggestions = [s for s in suggestions if s.get("tipo") in VALID][:3]
        return jsonify({"ok": True, "suggestions": suggestions})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


# ── Endpoints: /elements ─────────────────────────────────────────────────────

def _load_elements() -> list:
    return _rj(ELEMENTS_FILE)

def _save_elements_file(els: list) -> None:
    _wj(ELEMENTS_FILE, els)


@app.route("/elements", methods=["GET"])
def get_elements():
    tab = request.args.get("tab")
    els = _load_elements()
    if tab:
        els = [e for e in els if e.get("destination_tab") == tab]
    return jsonify({"ok": True, "elements": els})


@app.route("/elements", methods=["POST"])
def save_element():
    body      = request.get_json(force=True) or {}
    title     = str(body.get("title", "")).strip()
    dest_tab  = str(body.get("destination_tab", "")).strip()

    if not title:
        return jsonify({"ok": False, "error": "title é obrigatório"}), 400
    if not dest_tab:
        return jsonify({"ok": False, "error": "destination_tab é obrigatório"}), 400

    els = _load_elements()
    # Deduplicação: mesmo título + mesma aba de destino
    dup = next((e for e in els
                if e.get("title","").strip().lower() == title.lower()
                and e.get("destination_tab") == dest_tab), None)
    if dup:
        return jsonify({
            "ok": False,
            "error": f'Já existe um elemento com este título na aba "{dest_tab}". Altere o título ou delete o existente primeiro.'
        }), 409

    el = {
        "id":              _uid(),
        "tipo":            str(body.get("tipo", "T")),
        "title":           title,
        "destination_tab": dest_tab,
        "config":          body.get("config", {}),
        "sql":             str(body.get("sql", "")),
        "columns":         body.get("columns", []),
        "rows_snapshot":   (body.get("rows_snapshot") or [])[:200],
        "variavel_js":     str(body.get("variavel_js", "NLEL_" + _uid()[:8].upper())),
        "question":        str(body.get("question", "")),
        "created_at":      _now(),
        "updated_at":      _now(),
    }
    els.append(el)
    _save_elements_file(els)
    return jsonify({"ok": True, "element": el})


@app.route("/elements/<eid>", methods=["DELETE"])
def delete_element(eid):
    els = [e for e in _load_elements() if e.get("id") != eid]
    _save_elements_file(els)
    return jsonify({"ok": True})


# ── Health ─────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "model": MODEL})

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("NLSQL_PORT", 5001))
    print(f"BI NL-SQL Server → http://localhost:{port}")
    print(f"  Modelo: {MODEL}")
    print(f"  Prompt: {PROMPT_FILE}")
    app.run(host="0.0.0.0", port=port, debug=False)
