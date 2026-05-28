from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = BASE_DIR / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_supplier_panel_v08 as v08  # noqa: E402


OUT_DIR = BASE_DIR / "output" / "08_regime_fiscal"
VISUAL_DIR = BASE_DIR / "output" / "04_visualizacao"

INPUT_08 = OUT_DIR / "04_fornecedores_08_auditoria_simplificada.csv"
INPUT_CNPJA = OUT_DIR / "08_resultado_busca_cnpja_fila_prioritaria.csv"

OUT_08B_AUDIT = OUT_DIR / "11_fornecedores_08b_auditoria_simplificada.csv"
OUT_08B_CNPJA = OUT_DIR / "12_regimes_resolvidos_cnpja_08b.csv"
OUT_08B_PENDING = OUT_DIR / "13_regimes_ainda_indeterminados_08b.csv"
OUT_08B_COMPARE = OUT_DIR / "14_comparativo_08_para_08b.csv"
OUT_08B_SUMMARY = OUT_DIR / "10_resumo_versao_08b.json"
HTML_08B = VISUAL_DIR / "08b_painel_fornecedores_regime_fiscal.html"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def digits(value: Any) -> str:
    return v08.digits(value)


def apply_cnpja_results(rows_08: list[dict[str, str]], cnpja_rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cnpja_by_doc = {
        digits(row.get("documento")): row
        for row in cnpja_rows
        if digits(row.get("documento")) and row.get("regime_proposto") and row.get("regime_proposto") != "Indeterminado"
    }
    updated_rows: list[dict[str, Any]] = []
    compare_rows: list[dict[str, Any]] = []

    for index, row in enumerate(rows_08, start=1):
        out: dict[str, Any] = dict(row)
        doc = digits(out.get("documento"))
        result = cnpja_by_doc.get(doc)

        if result and out.get("regime_08") == "Indeterminado":
            before = {
                "regime_08_anterior": out.get("regime_08"),
                "credito_2027_08_anterior": out.get("credito_2027_08"),
                "origem_fiscal_08_anterior": out.get("origem_fiscal_08"),
                "fonte_fiscal_08_anterior": out.get("fonte_fiscal_08"),
                "criterio_fiscal_08_anterior": out.get("criterio_fiscal_08"),
                "evidencia_fiscal_08_anterior": out.get("evidencia_fiscal_08"),
                "status_consulta_fiscal_08_anterior": out.get("status_consulta_fiscal_08"),
            }
            out["regime_08"] = result.get("regime_proposto") or out.get("regime_08")
            out["credito_2027_08"] = result.get("credito_proposto") or out.get("credito_2027_08")
            out["origem_fiscal_08"] = "CNPJa publica"
            out["fonte_fiscal_08"] = "CNPJa publica"
            out["criterio_fiscal_08"] = result.get("criterio_proposto") or ""
            out["evidencia_fiscal_08"] = result.get("evidencia_proposta") or result.get("criterio_proposto") or ""
            out["ano_evidencia_fiscal_08"] = ""
            out["status_consulta_fiscal_08"] = "ok_cnpja_publica"
            out["credito_2027_ordem"] = v08.CREDIT_ORDER.get(out.get("credito_2027_08"), 99)
            out["regime_ordem"] = v08.REGIME_ORDER.get(out.get("regime_08"), 99)
            out["fonte_cnpja_08b"] = "CNPJa publica"
            out["criterio_cnpja_08b"] = result.get("criterio_proposto") or ""
            out["evidencia_cnpja_08b"] = result.get("evidencia_proposta") or ""
            out["status_cnpja_08b"] = result.get("status_cnpja_direto") or ""
            out["data_atualizacao_fiscal_08b"] = "2026-05-22"

            compare_rows.append(
                {
                    "linha": index,
                    "documento": doc,
                    "documento_formatado": out.get("documento_formatado"),
                    "fornecedor": out.get("nome_exibicao") or out.get("razao_original"),
                    "empresas": out.get("empresas_label") or out.get("empresa"),
                    "curva": out.get("curva_label"),
                    "valor_referencia_fmt": out.get("valor_referencia_fmt"),
                    **before,
                    "regime_08b": out.get("regime_08"),
                    "credito_2027_08b": out.get("credito_2027_08"),
                    "origem_fiscal_08b": out.get("origem_fiscal_08"),
                    "fonte_fiscal_08b": out.get("fonte_fiscal_08"),
                    "criterio_fiscal_08b": out.get("criterio_fiscal_08"),
                    "evidencia_fiscal_08b": out.get("evidencia_fiscal_08"),
                    "status_consulta_fiscal_08b": out.get("status_consulta_fiscal_08"),
                }
            )

        updated_rows.append(out)

    return updated_rows, compare_rows


def build_summary(rows_08b: list[dict[str, Any]], compare_rows: list[dict[str, Any]], cnpja_rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "versao": "08b",
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "base": str(INPUT_08.relative_to(BASE_DIR)),
        "fonte_complementar": str(INPUT_CNPJA.relative_to(BASE_DIR)),
        "registros": len(rows_08b),
        "fornecedores_atualizados_cnpja": len(compare_rows),
        "resultados_cnpja_lidos": len(cnpja_rows),
        "regime_08b": dict(Counter(row.get("regime_08") for row in rows_08b)),
        "credito_2027_08b": dict(Counter(row.get("credito_2027_08") for row in rows_08b)),
        "origem_fiscal_08b": dict(Counter(row.get("origem_fiscal_08") for row in rows_08b)),
        "status_consulta_fiscal_08b": dict(Counter(row.get("status_consulta_fiscal_08") for row in rows_08b)),
        "outputs": [
            str(OUT_08B_SUMMARY.relative_to(BASE_DIR)),
            str(OUT_08B_AUDIT.relative_to(BASE_DIR)),
            str(OUT_08B_CNPJA.relative_to(BASE_DIR)),
            str(OUT_08B_PENDING.relative_to(BASE_DIR)),
            str(OUT_08B_COMPARE.relative_to(BASE_DIR)),
            str(HTML_08B.relative_to(BASE_DIR)),
        ],
    }


def update_diary(summary: dict[str, Any]) -> None:
    diary = BASE_DIR / "docs" / "DIARIO_DE_BORDO.md"
    entry = f"""

### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Output 08b com CNPJa publica

#### Objetivo

- Criar uma copia evolutiva do `08`, chamada `08b`, incorporando os fornecedores resolvidos pela busca CNPJa publica.
- Manter o `08` original intacto.

#### Resultado

- Registros totais: `{summary['registros']}`.
- Fornecedores atualizados por CNPJa: `{summary['fornecedores_atualizados_cnpja']}`.
- Distribuicao de regime no `08b`: `{summary['regime_08b']}`.
- Distribuicao de credito 2027 no `08b`: `{summary['credito_2027_08b']}`.

#### Arquivos gerados

- `output/08_regime_fiscal/10_resumo_versao_08b.json`
- `output/08_regime_fiscal/11_fornecedores_08b_auditoria_simplificada.csv`
- `output/08_regime_fiscal/12_regimes_resolvidos_cnpja_08b.csv`
- `output/08_regime_fiscal/13_regimes_ainda_indeterminados_08b.csv`
- `output/08_regime_fiscal/14_comparativo_08_para_08b.csv`
- `output/04_visualizacao/08b_painel_fornecedores_regime_fiscal.html`
"""
    with diary.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def patch_html_methodology() -> None:
    text = HTML_08B.read_text(encoding="utf-8")
    text = text.replace(
        "<li>Se OpenCNPJ nao trouxer regime, consulta Minha Receita ou BrasilAPI.</li>",
        (
            "<li>Se OpenCNPJ nao trouxer regime, consulta Minha Receita ou BrasilAPI.</li>"
            "<li>No 08b, a fila prioritaria ainda Indeterminada foi complementada pela CNPJa publica, "
            "usando as flags simples.optant e simei.optant.</li>"
        ),
    )
    text = text.replace(
        "<li>Sem qualquer evidencia fiscal, permanece Indeterminado.</li>",
        (
            "<li>Quando a CNPJa retorna simples.optant=false e simei.optant=false, "
            "o fornecedor e classificado como Nao Simples com fonte CNPJa publica.</li>"
            "<li>Sem qualquer evidencia fiscal, permanece Indeterminado.</li>"
        ),
    )
    HTML_08B.write_text(text, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)

    print("Lendo output 08...", flush=True)
    rows_08 = read_csv(INPUT_08)
    print(f"Registros 08: {len(rows_08)}", flush=True)

    print("Lendo resultados CNPJa...", flush=True)
    cnpja_rows = read_csv(INPUT_CNPJA)
    print(f"Resultados CNPJa: {len(cnpja_rows)}", flush=True)

    print("Aplicando atualizacoes CNPJa no 08b...", flush=True)
    rows_08b, compare_rows = apply_cnpja_results(rows_08, cnpja_rows)
    pending_rows = [row for row in rows_08b if row.get("regime_08") == "Indeterminado"]

    print(f"Atualizados: {len(compare_rows)}", flush=True)
    print(f"Pendentes restantes: {len(pending_rows)}", flush=True)

    write_csv(OUT_08B_AUDIT, rows_08b)
    write_csv(OUT_08B_CNPJA, cnpja_rows)
    write_csv(OUT_08B_PENDING, pending_rows)
    write_csv(OUT_08B_COMPARE, compare_rows)

    summary = build_summary(rows_08b, compare_rows, cnpja_rows)
    OUT_08B_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Gerando HTML 08b...", flush=True)
    v08.HTML_FILE = HTML_08B
    v08.build_html(rows_08b, summary)
    patch_html_methodology()
    update_diary(summary)

    print("Concluido.", flush=True)
    print(f"HTML: {HTML_08B}", flush=True)
    print(f"CSV: {OUT_08B_AUDIT}", flush=True)
    print(f"Resumo: {OUT_08B_SUMMARY}", flush=True)


if __name__ == "__main__":
    main()
