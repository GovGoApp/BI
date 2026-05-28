from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import build_supplier_audit_panel_v05 as v05
import build_supplier_audit_panel_v06 as v06
import build_supplier_audit_panel_v06b as v06b


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

PHASE_01_DIR = OUTPUT_DIR / "01_cadastro"
PHASE_02_DIR = OUTPUT_DIR / "02_reconciliacao"
PHASE_03_DIR = OUTPUT_DIR / "03_enriquecimento"
PHASE_04_DIR = OUTPUT_DIR / "04_visualizacao"
PHASE_07_DIR = OUTPUT_DIR / "07_cadastro_total_opencnpj"

RECONCILED_FILE = PHASE_02_DIR / "01_fornecedores_reconciliados_movimento.csv"
UNIFIED_FILE = PHASE_01_DIR / "02_fornecedores_cadastro_unificado.csv"
CACHE_DIR = PHASE_03_DIR / "99_cache_opencnpj"

HTML_FILE = PHASE_04_DIR / "07_painel_auditoria_fornecedores_total_opencnpj.html"
OUT_00_SUMMARY = PHASE_07_DIR / "00_resumo_versao_07.json"
OUT_01_BASE = PHASE_07_DIR / "01_fornecedores_total_base_reconciliada.csv"
OUT_02_ADDRESS = PHASE_07_DIR / "02_fornecedores_total_com_endereco_interno.csv"
OUT_03_OPENCNPJ = PHASE_07_DIR / "03_fornecedores_total_opencnpj.csv"
OUT_04_AUDIT = PHASE_07_DIR / "04_fornecedores_total_auditoria.csv"
OUT_05_PENDING = PHASE_07_DIR / "05_fornecedores_total_pendencias.csv"

CURVE_ORDER = {
    "AAA": 1,
    "AA": 2,
    "A": 3,
    "B": 4,
    "BB": 5,
    "C": 6,
    "CC": 7,
    "CCC": 8,
    "Sem curva": 99,
    "": 99,
}


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
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
                    for key, value in row.items()
                }
            )


def split_multi(value: Any) -> list[str]:
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def is_blank(value: Any) -> bool:
    text = v06.clean(value).lower()
    return text in {"", "sem dado", "sem uf", "nan", "none"}


def as_reconciled_float(value: Any) -> float:
    """Converte numeros da base reconciliada sem destruir decimais com ponto."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").strip()
    if not text:
        return 0.0
    text = text.replace("R$", "").replace("%", "").replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def first_code(row: dict[str, Any]) -> str:
    codes = split_multi(row.get("codigos_fornecedor"))
    return v06.clean_upper(codes[0]) if codes else v06.clean_upper(row.get("chave_unificacao"))


def code_type_for_row(row: dict[str, Any]) -> str:
    if v06.digits(row.get("cnpj")) and len(v06.digits(row.get("cnpj"))) == 14:
        return "PJ/CNPJ"
    return v06.code_type(first_code(row))


def build_address_index() -> dict[str, list[dict[str, Any]]]:
    address_by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in v06.read_excel_all_sheets(v06.find_address_file()):
        code = v06.clean_upper(row.get("CDFORNECED"))
        if code:
            address_by_code[code].append(row)
    return address_by_code


def choose_best_address_for_codes(codes: list[str], address_by_code: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for code in codes:
        rows.extend(address_by_code.get(v06.clean_upper(code), []))
    return v06.choose_best_address(rows)


def make_occurrences(codes: list[str], companies: list[str]) -> list[dict[str, str]]:
    occurrences: list[dict[str, str]] = []
    if not companies:
        companies = ["FORA_CADASTRO"]
    for idx, code in enumerate(codes):
        occurrences.append(
            {
                "empresa": companies[idx] if idx < len(companies) else companies[0],
                "codigo": code,
                "linha_original": "",
                "razao_original": "",
                "fantasia_original": "",
                "status_interno": "",
            }
        )
    return occurrences


def build_v07_rows(delay_seconds: float = 0.15) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    PHASE_07_DIR.mkdir(parents=True, exist_ok=True)
    PHASE_04_DIR.mkdir(parents=True, exist_ok=True)

    # Reaproveita as funcoes de OpenCNPJ da v06, mas apontando para a pasta correta.
    v06.CACHE_DIR = CACHE_DIR

    reconciled_rows = read_csv(RECONCILED_FILE)
    unified_by_key = {row["chave_unificacao"]: row for row in read_csv(UNIFIED_FILE)}
    address_by_code = build_address_index()

    valid_cnpjs = sorted(
        {
            v06.digits(row.get("cnpj"))
            for row in reconciled_rows
            if len(v06.digits(row.get("cnpj"))) == 14
        }
    )
    opencnpj = v06.fetch_opencnpj_payloads(valid_cnpjs, delay_seconds=delay_seconds)

    rows: list[dict[str, Any]] = []
    address_records: list[dict[str, Any]] = []
    opencnpj_records: list[dict[str, Any]] = []
    pending_records: list[dict[str, Any]] = []

    for source in reconciled_rows:
        key = v06.clean(source.get("chave_unificacao"))
        unified = unified_by_key.get(key, {})
        codes = [v06.clean_upper(code) for code in split_multi(source.get("codigos_fornecedor"))] or [first_code(source)]
        companies = [v06.clean_upper(company) for company in split_multi(source.get("empresas_origem"))]
        address = choose_best_address_for_codes(codes, address_by_code)

        cnpj = v06.digits(source.get("cnpj"))
        api_status, payload = opencnpj.get(cnpj, ("nao_aplicavel", None)) if len(cnpj) == 14 else ("nao_aplicavel", None)
        if code_type_for_row(source) != "PJ/CNPJ":
            api_status, payload = "nao_aplicavel", None

        internal_address = v06.format_internal_address(address)
        internal_city = v06.clean(address.get("NMMUNICIPIO"))
        internal_uf = v06.clean(address.get("SGESTADO"))
        internal_cep = v06.clean(address.get("NRCEPFORN"))
        internal_phone = v06.collect_internal_phones(address) or v06.clean(unified.get("telefone_suporte"))
        internal_email = v06.join_unique([unified.get("emails"), address.get("DSEMAILFORN")])

        official_address = v06.format_official_address(payload)
        official_city = v06.clean(payload.get("municipio")) if isinstance(payload, dict) else ""
        official_uf = v06.clean(payload.get("uf")) if isinstance(payload, dict) else ""
        official_cep = v06.clean(payload.get("cep")) if isinstance(payload, dict) else ""
        official_phone = v06.collect_official_phones(payload)
        official_email = v06.clean(payload.get("email")) if isinstance(payload, dict) else ""

        endereco_opencnpj = is_blank(internal_address) and not is_blank(official_address)
        cidade_opencnpj = is_blank(internal_city) and not is_blank(official_city)
        uf_opencnpj = is_blank(internal_uf) and not is_blank(official_uf)
        telefone_opencnpj = is_blank(internal_phone) and not is_blank(official_phone)
        email_opencnpj = is_blank(internal_email) and not is_blank(official_email)

        display_address = internal_address or official_address or "Sem dado"
        display_city = internal_city or official_city or "Sem dado"
        display_uf = internal_uf or official_uf or "Sem UF"
        display_cep = internal_cep or official_cep
        display_phone = internal_phone or official_phone or "Sem dado"
        display_email = internal_email or official_email or "Sem dado"

        uf_status = v06.compare_uf(internal_uf, official_uf) if cnpj else "Nao aplicavel"
        city_status = v06.compare_place(internal_city, official_city) if cnpj else "Nao aplicavel"
        regime = v06.infer_regime(payload)
        credit = v06.infer_credit(payload)

        razao_internal = v06.best_value([unified.get("razao_social"), source.get("razao_social")])
        fantasia_internal = v06.best_value([unified.get("nome_fantasia"), source.get("nome_fantasia")])
        status_internal = v06.best_value([unified.get("situacao_cadastral_interna"), source.get("situacao_cadastral_interna")])
        ie_internal = v06.best_value([unified.get("inscricao_estadual")]) or "Sem dado"
        im_internal = v06.best_value([unified.get("inscricao_municipal")]) or "Sem dado"
        official_razao = v06.clean(payload.get("razao_social")) if isinstance(payload, dict) else ""
        official_fantasia = v06.clean(payload.get("nome_fantasia")) if isinstance(payload, dict) else ""
        official_status = v06.clean(payload.get("situacao_cadastral")) if isinstance(payload, dict) else ""

        divergences: list[str] = []
        if official_razao and v06.strip_accents(razao_internal) != v06.strip_accents(official_razao):
            divergences.append("razao_social")
        if official_fantasia and fantasia_internal and v06.strip_accents(fantasia_internal) != v06.strip_accents(official_fantasia):
            divergences.append("nome_fantasia")
        if official_email and internal_email and official_email.lower() not in internal_email.lower():
            divergences.append("email")
        if uf_status == "Divergencia":
            divergences.append("uf")
        if city_status == "Divergencia":
            divergences.append("municipio")

        missing: list[str] = []
        if not internal_address:
            missing.append("endereco_interno")
        if not internal_uf:
            missing.append("uf")
        if not internal_city:
            missing.append("municipio")
        if not internal_cep:
            missing.append("cep")
        if not internal_phone:
            missing.append("telefone")
        if not internal_email:
            missing.append("email")

        new_data: list[str] = []
        if uf_opencnpj:
            new_data.append("uf_oficial")
        if cidade_opencnpj:
            new_data.append("municipio_oficial")
        if endereco_opencnpj:
            new_data.append("endereco_oficial")
        if telefone_opencnpj:
            new_data.append("telefone_oficial")
        if email_opencnpj:
            new_data.append("email_oficial")
        if internal_address:
            new_data.append("endereco_interno")
        if internal_phone:
            new_data.append("telefone_interno")

        has_payload = isinstance(payload, dict) and not str(payload.get("__status_api", "")).startswith("http_")
        has_new_data = bool(new_data) or has_payload
        any_divergence = bool(divergences)
        needs_saneamento = bool(missing)
        needs_validation = any_divergence or regime == "indeterminado"
        action = (
            "Revisar antes"
            if any_divergence
            else "Validar fiscal"
            if needs_validation
            else "Sanear cadastro"
            if needs_saneamento
            else "Atualizar BD"
            if has_new_data
            else "Sem alteracao"
        )

        curve = v06.clean_upper(source.get("curva_classificacao")) or "Sem curva"
        movement = v06.clean_upper(source.get("tem_movimento_nfe")) == "S"
        curve_value = as_reconciled_float(source.get("curva_total_fornecedor"))
        nfe_value = as_reconciled_float(source.get("nfe_valor_total"))
        score = v06.best_value([source.get("score_completude"), unified.get("score_completude")]) or "0"
        score_float = as_reconciled_float(score)
        faixa = v06.best_value([source.get("faixa_completude"), unified.get("faixa_completude")])
        if not faixa:
            faixa = "alta" if score_float >= 85 else "media" if score_float >= 60 else "baixa"

        summary = []
        if new_data:
            summary.append(f"{len(new_data)} incluidos")
        if divergences:
            summary.append(f"{len(divergences)} divergencias")
        if not summary:
            summary.append("sem dado novo")

        row = {
            "linha_original": "",
            "empresa": companies[0] if companies else "CADASTRO",
            "codigo": codes[0],
            "tipo": code_type_for_row(source),
            "documento": cnpj or v06.digits(key),
            "chave": key,
            "razao_original": razao_internal,
            "fantasia_original": fantasia_internal or "Sem dado",
            "status_interno": status_internal,
            "emails_originais": internal_email,
            "ie_original": ie_internal,
            "im_original": im_internal,
            "razao_social_oficial": official_razao,
            "nome_fantasia_oficial": official_fantasia,
            "situacao_cadastral_oficial": official_status,
            "email_oficial": official_email,
            "telefones_oficiais": display_phone,
            "endereco_completo": display_address,
            "endereco_municipio": display_city,
            "endereco_uf": display_uf,
            "endereco_cep": display_cep,
            "contatos_qsa": v06.clean(address.get("NMCONTFORN")) or "Sem dado",
            "matriz_filial": v06.clean(payload.get("matriz_filial")) if isinstance(payload, dict) else "",
            "porte_empresa": v06.clean(payload.get("porte_empresa")) if isinstance(payload, dict) else "",
            "natureza_juridica": v06.clean(payload.get("natureza_juridica")) if isinstance(payload, dict) else "",
            "opcao_simples": v06.clean(payload.get("opcao_simples")) if isinstance(payload, dict) else "",
            "opcao_mei": v06.clean(payload.get("opcao_mei")) if isinstance(payload, dict) else "",
            "status_api": api_status,
            "regime_indiciado": regime,
            "potencial_credito_2027": credit,
            "status_cadastro_oficial": v06.classify_status(official_status, api_status),
            "status_regime_fiscal": v06.classify_regime_status(regime),
            "necessita_saneamento_cadastral": "S" if needs_saneamento else "N",
            "motivos_saneamento_cadastral": ";".join(missing),
            "necessita_validacao_fiscal": "S" if needs_validation else "N",
            "motivos_validacao_fiscal": ";".join(divergences),
            "divergencia_razao_social": "S" if "razao_social" in divergences else "N",
            "divergencia_nome_fantasia": "S" if "nome_fantasia" in divergences else "N",
            "divergencia_email": "S" if "email" in divergences else "N",
            "movimento_nfe": "S" if movement else "N",
            "nfe_linhas": source.get("nfe_linhas") or "0",
            "nfe_valor_total": nfe_value,
            "nfe_produtos_unicos": source.get("nfe_produtos_unicos", ""),
            "nfe_ufs": source.get("nfe_ufs") or "Sem UF",
            "nfe_anos": source.get("nfe_anos") or "Sem movimento",
            "curva": curve,
            "curva_posicao": source.get("curva_posicao") or "",
            "curva_total_fornecedor": curve_value,
            "curva_percentual": as_reconciled_float(source.get("curva_percentual")),
            "score_cadastral": score,
            "faixa_completude": faixa,
            "pendencias_essenciais": source.get("pendencias_essenciais") or unified.get("pendencias_essenciais", ""),
            "pendencias_complementares": source.get("pendencias_complementares") or unified.get("pendencias_complementares", ""),
            "prioridade_saneamento_score": source.get("prioridade_saneamento_score", ""),
            "prioridade_saneamento_faixa": source.get("prioridade_saneamento_faixa", ""),
            "origem_cadastro_label": "Cadastrado",
            "endereco_status_label": "Sem endereco" if not address else "Completo" if internal_uf and internal_city and internal_cep and internal_address else "Incompleto",
            "uf_status": uf_status,
            "municipio_status": city_status,
            "endereco_oficial": official_address,
            "telefone_oficial": official_phone,
            "telefone_interno": internal_phone,
            "dados_novos_v06": ";".join(new_data),
            "divergencias_v06": ";".join(divergences),
            "linha_curva_detalhe": "",
            "nome_exibicao": razao_internal or official_razao or key,
            "status_interno_label": v05.internal_status_label(status_internal),
            "situacao_label": v05.official_status_label(official_status, api_status),
            "regime_label": v05.short_regime(regime),
            "credito_label": v05.short_credit(credit),
            "movimento_label": "Com movimento" if movement else "Sem movimento",
            "curva_label": curve or "Sem curva",
            "uf_label": display_uf,
            "curva_valor_fmt": v05.money(curve_value),
            "curva_pct_fmt": v05.pct(as_reconciled_float(source.get("curva_percentual"))),
            "nfe_valor_fmt": v05.money(nfe_value),
            "dado_novo_label": "Com dado novo" if has_new_data else "Sem dado novo",
            "divergencia_label": "Qualquer divergencia" if any_divergence else "Sem divergencia",
            "saneamento_label": v05.yes_no_label("S" if needs_saneamento else "N", "Precisa sanear", "Nao precisa"),
            "validacao_label": v05.yes_no_label("S" if needs_validation else "N", "Precisa validar", "Nao precisa"),
            "acao_label": action,
            "mudanca_resumo": " / ".join(summary),
            "sort_curva_rank": CURVE_ORDER.get(curve, 99),
            "sort_curva_valor": curve_value,
            "sort_nfe_valor": nfe_value,
            "row_tone": v05.action_to_tone(action, has_new_data),
            "empresas_lista": companies or ["CADASTRO"],
            "empresas_label": ";".join(companies) if companies else "CADASTRO",
            "codigos_lista": codes,
            "codigos_label": ";".join(codes),
            "ocorrencias": make_occurrences(codes, companies),
            "documento_formatado": v05.format_document(cnpj or v06.digits(key)),
            "row_key": key,
            "endereco_opencnpj_incluido": "S" if endereco_opencnpj else "N",
            "cidade_opencnpj_incluida": "S" if cidade_opencnpj else "N",
            "uf_opencnpj_incluida": "S" if uf_opencnpj else "N",
            "telefone_opencnpj_incluido": "S" if telefone_opencnpj else "N",
            "email_opencnpj_incluido": "S" if email_opencnpj else "N",
            "email_endereco_display": display_email,
            "endereco_preferencial_origem": "OpenCNPJ complementar" if any([endereco_opencnpj, cidade_opencnpj, uf_opencnpj, telefone_opencnpj, email_opencnpj]) else "Cadastro atual",
            "endereco_tags": "incluido OpenCNPJ" if any([endereco_opencnpj, cidade_opencnpj, uf_opencnpj, telefone_opencnpj, email_opencnpj]) else "",
        }

        rows.append(row)
        address_records.append(
            {
                "chave": key,
                "codigos": row["codigos_label"],
                "cnpj": cnpj,
                "endereco_status": row["endereco_status_label"],
                "uf_interna": internal_uf,
                "municipio_interno": internal_city,
                "uf_oficial": official_uf,
                "municipio_oficial": official_city,
                "uf_status": uf_status,
                "municipio_status": city_status,
                "telefone_interno": internal_phone,
                "telefone_oficial": official_phone,
                "email_interno": internal_email,
                "email_oficial": official_email,
            }
        )
        opencnpj_records.append(
            {
                "chave": key,
                "cnpj": cnpj,
                "status_api": api_status,
                "razao_oficial": official_razao,
                "situacao_oficial": official_status,
                "regime": row["regime_label"],
                "credito": row["credito_label"],
                "porte": row["porte_empresa"],
                "natureza": row["natureza_juridica"],
            }
        )
        if missing or divergences:
            pending_records.append(
                {
                    "chave": key,
                    "cnpj": cnpj,
                    "razao": row["nome_exibicao"],
                    "pendencias": ";".join(missing),
                    "divergencias": ";".join(divergences),
                    "acao": action,
                }
            )

    rows.sort(key=lambda item: (item["sort_curva_rank"], -item["sort_curva_valor"], -item["sort_nfe_valor"], item["nome_exibicao"]))
    write_csv(OUT_01_BASE, reconciled_rows)
    write_csv(OUT_02_ADDRESS, address_records)
    write_csv(OUT_03_OPENCNPJ, opencnpj_records)
    write_csv(OUT_04_AUDIT, rows)
    write_csv(OUT_05_PENDING, pending_records)

    summary = {
        "versao": "07",
        "universo": "todos os fornecedores consolidados da base 05",
        "registros": len(rows),
        "cnpjs_validos_opencnpj": len(valid_cnpjs),
        "opencnpj_status": dict(Counter(row["status_api"] for row in rows)),
        "fornecedores_com_curva": sum(1 for row in rows if row["curva_label"] != "Sem curva"),
        "fornecedores_sem_curva": sum(1 for row in rows if row["curva_label"] == "Sem curva"),
        "fornecedores_com_movimento": sum(1 for row in rows if row["movimento_label"] == "Com movimento"),
        "fornecedores_sem_movimento": sum(1 for row in rows if row["movimento_label"] == "Sem movimento"),
        "fornecedores_com_endereco_completo": sum(1 for row in rows if row["endereco_status_label"] == "Completo"),
        "fornecedores_com_endereco_incompleto": sum(1 for row in rows if row["endereco_status_label"] == "Incompleto"),
        "fornecedores_sem_endereco": sum(1 for row in rows if row["endereco_status_label"] == "Sem endereco"),
        "uf_status": dict(Counter(row["uf_status"] for row in rows)),
        "municipio_status": dict(Counter(row["municipio_status"] for row in rows)),
        "outputs": [
            str(OUT_01_BASE.relative_to(BASE_DIR)),
            str(OUT_02_ADDRESS.relative_to(BASE_DIR)),
            str(OUT_03_OPENCNPJ.relative_to(BASE_DIR)),
            str(OUT_04_AUDIT.relative_to(BASE_DIR)),
            str(OUT_05_PENDING.relative_to(BASE_DIR)),
            str(HTML_FILE.relative_to(BASE_DIR)),
        ],
    }
    OUT_00_SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows, summary


def build_html(rows: list[dict[str, Any]]) -> None:
    original_target = v05.AUDIT_HTML_FILE
    v05.AUDIT_HTML_FILE = HTML_FILE
    try:
        v05.build_html(rows)
    finally:
        v05.AUDIT_HTML_FILE = original_target

    original_06b_target = v06b.OUTPUT_HTML_06B
    v06b.OUTPUT_HTML_06B = HTML_FILE
    try:
        v06b.patch_html()
    finally:
        v06b.OUTPUT_HTML_06B = original_06b_target


def update_diary(summary: dict[str, Any]) -> None:
    diary = BASE_DIR / "docs" / "DIARIO_DE_BORDO.md"
    current = diary.read_text(encoding="utf-8") if diary.exists() else ""
    marker = "#### Implementacao da versao 07 - Cadastro total OpenCNPJ"
    if marker in current:
        return
    entry = f"""

{marker}

- Foi criado o script `scripts/build_supplier_audit_panel_v07.py`.
- A versao `07` usa o universo completo da base reconciliada da versao `05`, com `{summary['registros']}` fornecedores consolidados.
- A versao `07` inclui fornecedores com curva e sem curva.
- Todos os CNPJs validos sao resolvidos via OpenCNPJ, usando cache local primeiro e API apenas para faltantes.
- O script exibe barra de progresso linear no terminal durante a resolucao OpenCNPJ, com contadores de cache, API e erro.
- CNPJs validos tratados para OpenCNPJ: `{summary['cnpjs_validos_opencnpj']}`.
- Fornecedores com curva: `{summary['fornecedores_com_curva']}`; fornecedores sem curva: `{summary['fornecedores_sem_curva']}`.
- Fornecedores com movimento: `{summary['fornecedores_com_movimento']}`; fornecedores sem movimento: `{summary['fornecedores_sem_movimento']}`.
- Fornecedores com endereco completo: `{summary['fornecedores_com_endereco_completo']}`; incompleto: `{summary['fornecedores_com_endereco_incompleto']}`; sem endereco: `{summary['fornecedores_sem_endereco']}`.
- O layout HTML segue o padrao visual final construido na versao `06b`.
- Arquivo HTML gerado: `output/04_visualizacao/07_painel_auditoria_fornecedores_total_opencnpj.html`.
"""
    with diary.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def main() -> None:
    rows, summary = build_v07_rows()
    build_html(rows)
    update_diary(summary)
    print(f"HTML gerado: {HTML_FILE}")
    print(f"Resumo: {OUT_00_SUMMARY}")
    print(f"Registros: {len(rows)}")


if __name__ == "__main__":
    main()
