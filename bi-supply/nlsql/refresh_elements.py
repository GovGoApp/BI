"""
nlsql/refresh_elements.py — Atualiza snapshots de elementos NL-SQL.

Executa o SQL de cada elemento em elements.json diretamente via adapter.py.
Não requer o servidor Flask rodando — pode ser chamado pelo BAT de atualização.

Uso: python nlsql/refresh_elements.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.adapter import run_query

ELEMENTS_FILE = ROOT / "nlsql" / "elements.json"

# Mesmo mapa de server.py — campos Zoho → nomes usados pelo _pred
_FIELD_NORM: dict[str, str] = {
    "UF": "uf", "EMPRESA": "empresa", "NEGOCIO": "negocio",
    "FORNECEDOR": "fornecedor", "NMFANTASIA": "fornecedor",
    "CAT1": "cat1", "CAT2": "cat2", "CAT3": "cat3", "CAT4": "cat4", "CAT5": "cat5",
    "MESANO": "mesano", "ANO": "ano", "MES": "mes",
    "STATUSPAG": "statuspag", "STATUS_CONCILIACAO": "status_conciliacao",
    "CURVA": "curva", "CURVA_ID": "curva_id", "CURVA_PROD": "curva_prod",
    "PRODUTO": "produto", "NMPRODUTO": "produto", "CDPRODUTO": "cdproduto",
    "ID": "id", "NMFILIAL": "filial", "CDFILIAL": "filial", "NOME": "nome",
    "SPEND": "spend", "TOTAL": "spend", "IMP_COT": "imp_cot",
}


def _normalize_rows(rows: list) -> list:
    result = []
    for row in rows:
        new_row: dict = {}
        for k, v in row.items():
            mapped = _FIELD_NORM.get(k.upper(), k.lower())
            new_row[mapped] = v
        result.append(new_row)
    return result


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def refresh() -> int:
    if not ELEMENTS_FILE.exists():
        print("  elements.json não encontrado — nada a fazer")
        return 0

    els: list = json.loads(ELEMENTS_FILE.read_text(encoding="utf-8"))
    if not els:
        print("  Nenhum elemento registrado")
        return 0

    refreshed = skipped = n_errors = 0

    for el in els:
        sql = el.get("sql", "").strip()
        if not sql:
            skipped += 1
            continue
        title = el.get("title", el.get("id", "?"))
        print(f"  [{el.get('destination_tab','?')}] {title}...", end="", flush=True)
        result = run_query(sql)
        if result.get("ok"):
            rows = _normalize_rows(result["rows"][:200])
            el["rows_snapshot"] = rows
            el["updated_at"] = _now()
            print(f" OK ({len(rows)} linhas)")
            refreshed += 1
        else:
            print(f" ERRO: {result.get('error', '?')}")
            n_errors += 1

    ELEMENTS_FILE.write_text(
        json.dumps(els, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n  Concluido: {refreshed} atualizados · {skipped} sem SQL · {n_errors} erros")
    return n_errors


if __name__ == "__main__":
    sys.exit(refresh() or 0)
