"""CLI interativa do modo NL-SQL.

Uso:
    python nlsql/cli.py

Comandos especiais dentro da CLI:
    /favoritar [nome]   — salva a última resposta como favorita
    /favoritos          — lista perguntas favoritas
    /tabelas            — lista as 18 fontes disponíveis
    /sair               — encerra

Favoritos são salvos em nlsql/favorites.json e podem virar
elementos do dashboard quando o transform.py for implementado.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.orchestrator import ask
from zoho.catalog import list_tables

FAVORITES_FILE = ROOT / "nlsql" / "favorites.json"


# ── Favoritos ────────────────────────────────────────────────────────────────

def _load_favorites() -> list[dict]:
    if FAVORITES_FILE.exists():
        return json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
    return []


def _save_favorite(question: str, result: dict, name: str | None = None) -> None:
    favorites = _load_favorites()
    entry = {
        "id": name or f"fav_{len(favorites)+1:03d}",
        "question": question,
        "sql": result.get("sql_used", ""),
        "answer_summary": result.get("answer", "")[:200],
        "columns": [c["name"] for c in (result.get("table") or {}).get("columns", [])],
        "row_count": (result.get("table") or {}).get("row_count", 0),
        "saved_at": datetime.now().isoformat(),
    }
    favorites.append(entry)
    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    FAVORITES_FILE.write_text(json.dumps(favorites, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Salvo como '{entry['id']}'.")


# ── Formatação de tabela ─────────────────────────────────────────────────────

def _print_table(table: dict, max_rows: int = 20) -> None:
    if not table or not table.get("columns"):
        return
    cols = [c["name"] for c in table["columns"]]
    rows = table.get("rows", [])[:max_rows]
    # Larguras
    widths = [max(len(c), max((len(str(r.get(c, ""))) for r in rows), default=0)) for c in cols]
    widths = [min(w, 35) for w in widths]
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = "| " + " | ".join(c[:widths[i]].ljust(widths[i]) for i, c in enumerate(cols)) + " |"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "| " + " | ".join(str(row.get(c, ""))[:widths[i]].ljust(widths[i]) for i, c in enumerate(cols)) + " |"
        print(line)
    print(sep)
    total = table.get("row_count", len(rows))
    trunc = " (truncado)" if table.get("truncated") else ""
    print(f"  {total} linha(s){trunc}  |  {table.get('elapsed_ms', 0)}ms")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 60)
    print("  BI Suprimentos — Modo Relatório NL-SQL")
    print("  Digite sua pergunta em português.")
    print("  Comandos: /favoritar [nome]  /favoritos  /tabelas  /sair")
    print("=" * 60)
    print()

    last_question: str = ""
    last_result: dict = {}

    while True:
        try:
            raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo.")
            break

        if not raw:
            continue

        # Comandos especiais
        if raw.startswith("/"):
            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None

            if cmd == "/sair":
                print("Até logo.")
                break

            if cmd == "/tabelas":
                tables = list_tables()
                print()
                for t in tables:
                    status = "OK" if t["available"] else "--"
                    print(f"  [{status}] {t['table']:<30} {t['column_count']:>3} cols")
                print()
                continue

            if cmd == "/favoritos":
                favs = _load_favorites()
                if not favs:
                    print("  Nenhum favorito salvo ainda.")
                else:
                    print(f"\n  {len(favs)} favorito(s):\n")
                    for f in favs:
                        print(f"  [{f['id']}] {f['question'][:60]}")
                        if f.get("sql"):
                            print(f"    SQL: {f['sql'][:80]}")
                        print(f"    Colunas: {', '.join(f.get('columns', [])[:5])}")
                        print()
                continue

            if cmd == "/favoritar":
                if not last_result.get("sql_used") and not last_result.get("answer"):
                    print("  Nenhuma resposta para favoritar ainda.")
                else:
                    _save_favorite(last_question, last_result, name=arg)
                continue

            print(f"  Comando desconhecido: {cmd}")
            continue

        # Pergunta normal
        last_question = raw
        print()
        print("  Consultando...", flush=True)

        result = ask(raw, verbose=False)
        last_result = result

        # Resposta em texto
        if result.get("answer"):
            print()
            print(result["answer"])

        # Tabela de resultados
        if result.get("table") and result["table"].get("rows"):
            print()
            _print_table(result["table"])

        # SQL usado
        if result.get("sql_used"):
            print(f"\n  SQL: {result['sql_used'][:120]}")

        print(f"  ({result.get('tool_calls', 0)} tool call(s))")
        print()
        print("  /favoritar [nome] para salvar esta resposta")
        print()


if __name__ == "__main__":
    main()
