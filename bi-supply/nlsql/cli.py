"""CLI interativa do modo NL-SQL.

Uso:
    python nlsql/cli.py

Comandos especiais:
    /salvar            — salva o ultimo resultado no historico
    /historico         — lista ultimas perguntas
    /favoritos         — lista perguntas salvas
    /sql               — exibe o SQL da ultima consulta
    /sair              — encerra
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.orchestrator import ask, get_history, mark_saved


# ── Formatação de tabela ─────────────────────────────────────────────────────

def _print_table(table: dict, max_rows: int = 25) -> None:
    if not table or not table.get("columns"):
        return
    cols = [c["name"] for c in table["columns"]]
    rows = table.get("rows", [])[:max_rows]
    widths = [
        min(max(len(c), max((len(str(r.get(c, ""))) for r in rows), default=0)), 38)
        for c in cols
    ]
    sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = "| " + " | ".join(c[:widths[i]].ljust(widths[i]) for i, c in enumerate(cols)) + " |"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "| " + " | ".join(
            str(row.get(c, ""))[:widths[i]].ljust(widths[i]) for i, c in enumerate(cols)
        ) + " |"
        print(line)
    print(sep)
    total = table.get("row_count", len(rows))
    trunc = " (truncado — use LIMIT maior)" if table.get("truncated") else ""
    print(f"  {total} linha(s)  |  {table.get('elapsed_ms', 0)}ms{trunc}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print()
    print("=" * 58)
    print("  BI Suprimentos — Modo Relatório NL-SQL")
    print("  Digite sua pergunta em português.")
    print("  /salvar  /historico  /favoritos  /sql  /sair")
    print("=" * 58)
    print()

    last_result: dict = {}

    while True:
        try:
            raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo.")
            break

        if not raw:
            continue

        if raw.startswith("/"):
            cmd = raw.split()[0].lower()

            if cmd == "/sair":
                print("Até logo.")
                break

            if cmd == "/sql":
                sql = last_result.get("sql_used", "")
                if sql:
                    print(f"\n{sql}\n")
                else:
                    print("  Nenhuma consulta executada ainda.")
                continue

            if cmd == "/salvar":
                record = last_result.get("record")
                if record:
                    if mark_saved(record["id"]):
                        print(f"  Salvo: [{record['id']}] {record['question'][:60]}")
                    else:
                        print("  Não foi possível salvar.")
                else:
                    print("  Nenhum resultado para salvar.")
                continue

            if cmd == "/historico":
                items = get_history(limit=20)
                if not items:
                    print("  Histórico vazio.")
                else:
                    print(f"\n  Últimas {len(items)} consulta(s):\n")
                    for h in items:
                        status = "OK" if h["status"] == "ok" else "ERR"
                        saved = " [salvo]" if h.get("saved") else ""
                        print(f"  [{h['id']}] [{status}]{saved} {h['question'][:60]}")
                        print(f"    {h.get('row_count', 0)} linhas  |  {h.get('elapsed_ms', 0)}ms")
                print()
                continue

            if cmd == "/favoritos":
                items = get_history(limit=50, saved_only=True)
                if not items:
                    print("  Nenhum favorito salvo.")
                else:
                    print(f"\n  {len(items)} favorito(s):\n")
                    for h in items:
                        print(f"  [{h['id']}] {h['question'][:70]}")
                        if h.get("sql"):
                            print(f"    SQL: {h['sql'][:100]}")
                        print(f"    Cols: {', '.join(h.get('columns', [])[:6])}")
                        print()
                continue

            print(f"  Comando desconhecido: {cmd}")
            continue

        # Pergunta normal
        print()
        print("  Consultando...", flush=True)

        result = ask(raw, verbose=False)
        last_result = result

        # Resposta
        if result.get("answer"):
            print()
            print(result["answer"])

        # Tabela
        if result.get("table") and result["table"].get("rows"):
            print()
            _print_table(result["table"])

        # SQL resumido
        sql = result.get("sql_used", "")
        if sql:
            preview = sql[:100] + ("..." if len(sql) > 100 else "")
            print(f"\n  SQL: {preview}")

        record = result.get("record")
        if record:
            print(f"  id: {record['id']}  |  /salvar para guardar")
        print()


if __name__ == "__main__":
    main()
