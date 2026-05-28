from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import build_supplier_audit_panel_v05 as v05


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"
VISUAL_DIR = OUTPUT_DIR / "04_visualizacao"
CURVE_06_DIR = OUTPUT_DIR / "06_curva_total"

INPUT_AUDIT = CURVE_06_DIR / "04_fornecedores_curva_total_auditoria.csv"
OUTPUT_AUDIT_06B = CURVE_06_DIR / "06b_fornecedores_curva_total_auditoria_endereco_preferencial.csv"
OUTPUT_SUMMARY_06B = CURVE_06_DIR / "06b_resumo_endereco_preferencial.json"
OUTPUT_HTML_06B = VISUAL_DIR / "06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html"


def clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def is_blank(value: Any) -> bool:
    text = clean(value).lower()
    return text in {"", "sem dado", "sem uf", "nan", "none"}


def parse_json_field(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return fallback


def split_items(value: str) -> set[str]:
    return {item.strip() for item in str(value or "").split(";") if item.strip()}


def source_tag(label: str) -> str:
    return label


def load_rows() -> list[dict[str, Any]]:
    with INPUT_AUDIT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        row["empresas_lista"] = parse_json_field(row.get("empresas_lista", ""), [])
        row["codigos_lista"] = parse_json_field(row.get("codigos_lista", ""), [])
        row["ocorrencias"] = parse_json_field(row.get("ocorrencias", ""), [])

        novos = split_items(row.get("dados_novos_v06", ""))
        tags: list[str] = []

        # Regra 06b: cadastro/endereco interno e a fonte principal.
        # OpenCNPJ so aparece quando o campo interno estava vazio.
        row["endereco_opencnpj_incluido"] = "S" if "endereco_oficial" in novos else "N"
        row["cidade_opencnpj_incluida"] = "S" if "municipio_oficial" in novos else "N"
        row["uf_opencnpj_incluida"] = "S" if "uf_oficial" in novos else "N"
        row["telefone_opencnpj_incluido"] = "N"
        row["email_opencnpj_incluido"] = "N"

        if "endereco_oficial" in novos:
            tags.append(source_tag("incluido OpenCNPJ"))
        if "municipio_oficial" in novos:
            tags.append(source_tag("incluido OpenCNPJ"))
        if "uf_oficial" in novos:
            tags.append(source_tag("incluido OpenCNPJ"))

        if is_blank(row.get("telefone_interno")) and not is_blank(row.get("telefone_oficial")):
            row["telefones_oficiais"] = row["telefone_oficial"]
            row["telefone_opencnpj_incluido"] = "S"
            tags.append(source_tag("incluido OpenCNPJ"))
        else:
            row["telefones_oficiais"] = row.get("telefone_interno") or row.get("telefones_oficiais") or "Sem dado"

        if is_blank(row.get("emails_originais")) and not is_blank(row.get("email_oficial")):
            row["email_endereco_display"] = row["email_oficial"]
            row["email_opencnpj_incluido"] = "S"
            tags.append(source_tag("incluido OpenCNPJ"))
        else:
            row["email_endereco_display"] = row.get("emails_originais") or "Sem dado"

        if row.get("endereco_status_label") == "Sem endereco" and not is_blank(row.get("endereco_cep")):
            row["endereco_opencnpj_incluido"] = "S"
            tags.append(source_tag("incluido OpenCNPJ"))

        row["endereco_preferencial_origem"] = "OpenCNPJ complementar" if tags else "Cadastro atual"
        row["endereco_tags"] = ";".join(tags)

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = row.copy()
            out["empresas_lista"] = json.dumps(out.get("empresas_lista", []), ensure_ascii=False)
            out["codigos_lista"] = json.dumps(out.get("codigos_lista", []), ensure_ascii=False)
            out["ocorrencias"] = json.dumps(out.get("ocorrencias", []), ensure_ascii=False)
            writer.writerow(out)


def patch_html() -> None:
    html = OUTPUT_HTML_06B.read_text(encoding="utf-8")
    html = html.replace("<title>Painel de Auditoria de Fornecedores</title>", "<title>Painel de Fornecedores</title>")
    html = html.replace("<h1>Painel de Fornecedores</h1>", "<h1>Painel de Fornecedores</h1>")
    html = html.replace(
        '<div class="filter"><label>Divergência <span class="help" data-tip="Compara cadastro interno com dados oficiais em razao social, fantasia e email.">?</span></label><select id="divergencia"></select></div>',
        '<div class="filter"><label>Inclusões <span class="help" data-tip="Filtra fornecedores por campos efetivamente complementados por fonte externa ou enriquecimento: cadastro, contato, endereco e dados cadastrais oficiais.">?</span></label><select id="divergencia"></select></div>',
    )
    html = html.replace(
        ".detail-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;padding:9px;border-top:1px solid #e5e7eb}",
        ".detail-grid{display:grid;grid-template-columns:1.45fr 1.45fr .9fr .9fr .85fr;gap:8px;padding:9px;border-top:1px solid #e5e7eb}",
    )
    html = html.replace(
        ".tag.green{background:#dcfce7;color:#166534}",
        ".tag.green{background:#dcfce7;color:#166534}\n"
        ".tag.check{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;padding:0;border-radius:999px;background:#dbeafe;color:#1d4ed8;font-size:10px;font-weight:900;vertical-align:middle;flex:0 0 auto}\n"
        ".copy-doc{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;margin-left:5px;border:1px solid #bfdbfe;border-radius:999px;background:#eff6ff;color:#1d4ed8;font-size:11px;line-height:1;cursor:pointer;vertical-align:middle}\n"
        ".copy-doc:hover{background:#dbeafe;border-color:#93c5fd}\n"
        ".copy-doc.copied{background:#dcfce7;color:#166534;border-color:#86efac}\n"
        ".doc-wrap{display:inline-flex;align-items:center;gap:3px;max-width:100%;vertical-align:middle}\n"
        ".email-list{display:inline-flex;flex-wrap:wrap;gap:4px;align-items:center;vertical-align:middle}\n"
        ".email-chip{display:inline-flex;max-width:100%;padding:2px 6px;border-radius:999px;background:#f1f5f9;color:#334155;font-size:11px;line-height:1.4;overflow-wrap:anywhere}\n"
        ".score-total{margin-bottom:7px}\n"
        ".score-note{font-size:11px;line-height:1.35;color:#64748b;margin:0 0 7px}\n"
        ".score-list{display:grid;gap:5px}\n"
        ".score-item{display:grid;grid-template-columns:46px minmax(0,1fr);align-items:center;gap:5px;font-size:11px}\n"
        ".score-item span:last-child{overflow-wrap:anywhere}",
    )
    html = html.replace("<div class=\"panel\"><h3>Informacoes</h3>", "<div class=\"panel\"><h3>Endereco</h3>")
    html = html.replace(
        "function infoEmails(row) {\n"
        "  const values = [row.emails_originais, row.email_oficial].filter(Boolean);\n"
        "  return values.length ? values.join(' | ') : 'Sem dado';\n"
        "}\n",
        "function infoEmails(row) {\n"
        "  return row.email_endereco_display || row.emails_originais || 'Sem dado';\n"
        "}\n"
        "\n"
        "function copyDocumentButton(row) {\n"
        "  const digits = String(row.documento || row.chave || '').replace(/\\D/g, '');\n"
        "  if (!digits) return '';\n"
        "  return `<button type=\"button\" class=\"copy-doc\" data-doc=\"${digits}\" title=\"Copiar somente os numeros do CNPJ/CPF\" aria-label=\"Copiar CNPJ/CPF\">⧉</button>`;\n"
        "}\n"
        "\n"
        "function documentoComCopia(row) {\n"
        "  return `<span class=\"doc-wrap\"><span class=\"doc\">${safe(row.documento_formatado)}</span>${copyDocumentButton(row)}</span>`;\n"
        "}\n"
        "\n"
        "function checkOpenCnpj(flag) {\n"
        "  return flag === 'S' ? ' <span class=\"tag check\" title=\"Incluido pela OpenCNPJ\">&#10003;</span>' : '';\n"
        "}\n"
        "\n"
        "function enderecoCampo(row, field, flagField) {\n"
        "  return `${safe(row[field])}${checkOpenCnpj(row[flagField])}`;\n"
        "}\n"
        "\n"
        "function formatPhoneItem(value) {\n"
        "  let digits = String(value || '').replace(/\\D/g, '');\n"
        "  if (!digits) return '';\n"
        "  if (digits.startsWith('55') && digits.length > 11) digits = digits.slice(2);\n"
        "  if (digits.length === 11) return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;\n"
        "  if (digits.length === 10) return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;\n"
        "  if (digits.length === 9) return `${digits.slice(0, 5)}-${digits.slice(5)}`;\n"
        "  if (digits.length === 8) return `${digits.slice(0, 4)}-${digits.slice(4)}`;\n"
        "  return safe(value);\n"
        "}\n"
        "\n"
        "function formatPhones(value) {\n"
        "  const phones = String(value || '').split(/[;|,/]+/).map(formatPhoneItem).filter(Boolean);\n"
        "  return phones.length ? [...new Set(phones)].join('; ') : 'Sem dado';\n"
        "}\n"
        "\n"
        "function emailChips(value) {\n"
        "  const emails = String(value || '').toLowerCase().split(/[;|,\\s]+/).map(item => item.trim()).filter(Boolean);\n"
        "  if (!emails.length) return 'Sem dado';\n"
        "  return `<span class=\"email-list\">${[...new Set(emails)].map(email => `<span class=\"email-chip\">${safe(email)}</span>`).join('')}</span>`;\n"
        "}\n"
        "\n"
        "function enderecoEmail(row) {\n"
        "  return `${emailChips(infoEmails(row))}${checkOpenCnpj(row.email_opencnpj_incluido)}`;\n"
        "}\n",
    )
    html = html.replace(
        "  option(els.divergencia, 'Todas', ['Razao social', 'Fantasia', 'Email', 'Qualquer divergencia', 'Sem divergencia']);",
        "  option(els.divergencia, 'Todas', ['Razao social', 'Fantasia', 'Situacao', 'Email', 'Porte', 'Natureza juridica', 'Endereco', 'Cidade', 'UF', 'Telefone', 'Qualquer inclusao', 'Sem inclusao']);",
    )
    html = html.replace(
        "function divergenceSet(row) {\n"
        "  return new Set(String(row.divergencias_v06 || '').split(';').filter(Boolean));\n"
        "}\n"
        "\n"
        "function hasAnyDivergence(row) {\n"
        "  const values = divergenceSet(row);\n"
        "  return row.divergencia_razao_social === 'S' || row.divergencia_nome_fantasia === 'S' || row.divergencia_email === 'S' || values.size > 0;\n"
        "}\n"
        "\n"
        "function matchesDivergence(row, value) {\n"
        "  if (value.includes('__NONE__')) return false;\n"
        "  if (!value.length) return true;\n"
        "  const values = divergenceSet(row);\n"
        "  return value.some(item => {\n"
        "    if (item === 'Razao social') return row.divergencia_razao_social === 'S' || values.has('razao_social');\n"
        "    if (item === 'Nome fantasia') return row.divergencia_nome_fantasia === 'S' || values.has('nome_fantasia');\n"
        "    if (item === 'Email') return row.divergencia_email === 'S' || values.has('email');\n"
        "    if (item === 'Municipio') return values.has('municipio');\n"
        "    if (item === 'UF') return values.has('uf');\n"
        "    if (item === 'Qualquer divergencia') return hasAnyDivergence(row);\n"
        "    return !hasAnyDivergence(row);\n"
        "  });\n"
        "}\n",
        "function isEmptyValue(value) {\n"
        "  return ['', 'sem dado', 'sem uf', 'nan', 'none'].includes(String(value || '').trim().toLowerCase());\n"
        "}\n"
        "\n"
        "function hasInclusion(row, item) {\n"
        "  if (item === 'Razao social') return isEmptyValue(row.razao_original) && !isEmptyValue(row.razao_social_oficial);\n"
        "  if (item === 'Fantasia') return isEmptyValue(row.fantasia_original) && !isEmptyValue(row.nome_fantasia_oficial);\n"
        "  if (item === 'Situacao') return isEmptyValue(row.status_interno_label) && !isEmptyValue(row.situacao_cadastral_oficial);\n"
        "  if (item === 'Email') return (isEmptyValue(row.emails_originais) && !isEmptyValue(row.email_oficial)) || row.email_opencnpj_incluido === 'S';\n"
        "  if (item === 'Porte') return !isEmptyValue(row.porte_empresa);\n"
        "  if (item === 'Natureza juridica') return !isEmptyValue(row.natureza_juridica);\n"
        "  if (item === 'Endereco') return row.endereco_opencnpj_incluido === 'S';\n"
        "  if (item === 'Cidade') return row.cidade_opencnpj_incluida === 'S';\n"
        "  if (item === 'UF') return row.uf_opencnpj_incluida === 'S';\n"
        "  if (item === 'Telefone') return row.telefone_opencnpj_incluido === 'S';\n"
        "  return false;\n"
        "}\n"
        "\n"
        "function hasAnyInclusion(row) {\n"
        "  return ['Razao social', 'Fantasia', 'Situacao', 'Email', 'Porte', 'Natureza juridica', 'Endereco', 'Cidade', 'UF', 'Telefone'].some(item => hasInclusion(row, item));\n"
        "}\n"
        "\n"
        "function matchesDivergence(row, value) {\n"
        "  if (value.includes('__NONE__')) return false;\n"
        "  if (!value.length) return true;\n"
        "  return value.some(item => {\n"
        "    if (item === 'Qualquer inclusao') return hasAnyInclusion(row);\n"
        "    if (item === 'Sem inclusao') return !hasAnyInclusion(row);\n"
        "    return hasInclusion(row, item);\n"
        "  });\n"
        "}\n",
    )
    html = html.replace(
        "function cadastroTags(row) {\n"
        "  const out = [];\n"
        "  const missing = String(row.pendencias_essenciais || '').split(';').filter(Boolean);\n"
        "  if (missing.includes('email')) out.push('<span class=\"tag yellow\">email faltante</span>');\n"
        "  if (missing.includes('inscricao_estadual')) out.push('<span class=\"tag yellow\">inscricao estadual faltante</span>');\n"
        "  if (missing.includes('inscricao_municipal')) out.push('<span class=\"tag yellow\">inscricao municipal faltante</span>');\n"
        "  if (row.divergencia_razao_social === 'S') out.push('<span class=\"tag red\">divergencia razao social</span>');\n"
        "  if (row.divergencia_nome_fantasia === 'S') out.push('<span class=\"tag red\">divergencia fantasia</span>');\n"
        "  if (row.divergencia_email === 'S') out.push('<span class=\"tag red\">divergencia email</span>');\n"
        "  return out.join('') || '<span class=\"tag green\">cadastro sem alerta principal</span>';\n"
        "}\n",
        "function cadastroTags(row) {\n"
        "  return '';\n"
        "}\n"
        "\n"
        "function cadastroValorCampo(row, field, label) {\n"
        "  const value = String(row[field] || '').trim();\n"
        "  if (!value || ['Sem dado', 'sem dado'].includes(value)) return `<span class=\"tag yellow\">${label} faltante</span>`;\n"
        "  return safe(value);\n"
        "}\n",
    )
    html = html.replace(
        "function cadastroValorCampo(row, field, label) {\n"
        "  const value = String(row[field] || '').trim();\n"
        "  if (!value || ['Sem dado', 'sem dado'].includes(value)) return `<span class=\"tag yellow\">${label} faltante</span>`;\n"
        "  return safe(value);\n"
        "}\n",
        "function cadastroValorCampo(row, field, label) {\n"
        "  const value = String(row[field] || '').trim();\n"
        "  if (!value || ['Sem dado', 'sem dado'].includes(value)) return `<span class=\"tag yellow\">${label} faltante</span>`;\n"
        "  return safe(value);\n"
        "}\n"
        "\n"
        "function cadastroPreferencial(row, internalField, officialField, includedLabel, missingLabel = '') {\n"
        "  const internalValue = String(row[internalField] || '').trim();\n"
        "  const officialValue = String(row[officialField] || '').trim();\n"
        "  if (internalValue && !['Sem dado', 'sem dado'].includes(internalValue)) return safe(internalValue);\n"
        "  if (officialValue && !['Sem dado', 'sem dado'].includes(officialValue)) return `${safe(officialValue)} <span class=\"tag check\" title=\"Incluido pela OpenCNPJ\">&#10003;</span>`;\n"
        "  if (missingLabel) return `<span class=\"tag yellow\">${missingLabel} faltante</span>`;\n"
        "  return 'Sem dado';\n"
        "}\n"
        "\n"
        "function cadastroOpenCnpj(row, field, includedLabel) {\n"
        "  const value = String(row[field] || '').trim();\n"
        "  if (!value || ['Sem dado', 'sem dado'].includes(value)) return 'Sem dado';\n"
        "  return `${safe(value)} <span class=\"tag check\" title=\"Incluido pela OpenCNPJ\">&#10003;</span>`;\n"
        "}\n"
        "\n"
        "const SCORE_RULES = [\n"
        "  ['cnpj_invalido', 'CNPJ valido', 20],\n"
        "  ['razao_social', 'Razao social', 15],\n"
        "  ['email', 'Email', 15],\n"
        "  ['inscricao_estadual', 'Inscricao estadual', 10],\n"
        "  ['nome_fantasia', 'Nome fantasia', 5],\n"
        "  ['inscricao_municipal', 'Inscricao municipal', 5],\n"
        "  ['telefone_suporte', 'Telefone', 5],\n"
        "  ['site', 'Site', 5],\n"
        "  ['situacao_interna_nao_ativa', 'Situacao interna ativa', 5],\n"
        "  ['data_cadastro', 'Data de cadastro', 5],\n"
        "  ['grupo_fiscal', 'Grupo fiscal', 5],\n"
        "  ['indicador_contribuinte_icms', 'Indicador contribuinte ICMS', 5]\n"
        "];\n"
        "\n"
        "const SCORE_GROUPS = [\n"
        "  ['Cadastro', ['cnpj_invalido', 'razao_social', 'nome_fantasia', 'situacao_interna_nao_ativa', 'data_cadastro']],\n"
        "  ['Endereco', ['email', 'telefone_suporte', 'site']],\n"
        "  ['Fiscal', ['inscricao_estadual', 'inscricao_municipal', 'grupo_fiscal', 'indicador_contribuinte_icms']]\n"
        "];\n"
        "\n"
        "function scorePanel(row) {\n"
        "  const missingText = [row.pendencias_essenciais, row.pendencias_complementares].filter(Boolean).join(';');\n"
        "  const missing = new Set(String(missingText).split(';').filter(Boolean));\n"
        "  const forceZero = Number(row.score_cadastral || 0) === 0 && !missing.size;\n"
        "  const ruleByKey = Object.fromEntries(SCORE_RULES.map(([key, label, points]) => [key, {label, points}]));\n"
        "  const items = SCORE_GROUPS.map(([group, keys]) => {\n"
        "    const total = keys.reduce((sum, key) => sum + ruleByKey[key].points, 0);\n"
        "    const pts = keys.reduce((sum, key) => sum + ((!forceZero && !missing.has(key)) ? ruleByKey[key].points : 0), 0);\n"
        "    const cls = pts === total ? 'green' : pts > 0 ? 'yellow' : 'red';\n"
        "    return `<div class=\"score-item\"><span class=\"tag ${cls}\">${pts}/${total}</span><span>${group}</span></div>`;\n"
        "  }).join('');\n"
        "  return `<div class=\"score-total\"><span class=\"pill ${scorePillClass(row.faixa_completude)}\">${scoreLabel(row)}</span></div>` +\n"
        "    '<div class=\"score-note\">Score = soma dos grupos Cadastro, Endereco e Fiscal.</div>' +\n"
        "    `<div class=\"score-list\">${items}</div>`;\n"
        "}\n",
    )
    html = html.replace(
        "          <div class=\"panel\"><h3>Cadastro original</h3>\n"
        "            <div class=\"kv\"><b>Razao</b><span>${safe(row.razao_original)}</span></div>\n"
        "            <div class=\"kv\"><b>Fantasia</b><span>${safe(row.fantasia_original)}</span></div>\n"
        "            <div class=\"kv\"><b>Situacao</b><span>${safe(row.status_interno_label)}</span></div>\n"
        "            <div class=\"kv\"><b>CNPJ/CPF</b><span>${safe(row.documento_formatado)}</span></div>\n"
        "            <div class=\"kv\"><b>IE</b><span>${safe(row.ie_original)}</span></div>\n"
        "            <div class=\"kv\"><b>IM</b><span>${safe(row.im_original)}</span></div>\n"
        "            <div class=\"tags\">${cadastroTags(row)}</div>\n"
        "          </div>",
        "          <div class=\"panel\"><h3>Cadastro</h3>\n"
        "            <div class=\"kv\"><b>Razao</b><span>${cadastroPreferencial(row, 'razao_original', 'razao_social_oficial', 'razao')}</span></div>\n"
        "            <div class=\"kv\"><b>Fantasia</b><span>${cadastroPreferencial(row, 'fantasia_original', 'nome_fantasia_oficial', 'fantasia')}</span></div>\n"
        "            <div class=\"kv\"><b>Situacao</b><span>${cadastroPreferencial(row, 'status_interno_label', 'situacao_cadastral_oficial', 'situacao')}</span></div>\n"
        "            <div class=\"kv\"><b>CNPJ/CPF</b><span>${documentoComCopia(row)}</span></div>\n"
        "            <div class=\"kv\"><b>IE</b><span>${cadastroValorCampo(row, 'ie_original', 'inscricao estadual')}</span></div>\n"
        "            <div class=\"kv\"><b>IM</b><span>${cadastroValorCampo(row, 'im_original', 'inscricao municipal')}</span></div>\n"
        "            <div class=\"kv\"><b>Porte</b><span>${cadastroOpenCnpj(row, 'porte_empresa', 'porte')}</span></div>\n"
        "            <div class=\"kv\"><b>Natureza</b><span>${cadastroOpenCnpj(row, 'natureza_juridica', 'natureza')}</span></div>\n"
        "          </div>",
    )
    html = html.replace(
        "          <div class=\"panel\"><h3>Dados incluidos</h3>\n"
        "            <div class=\"kv\"><b>Razao oficial</b><span>${safe(row.razao_social_oficial)}</span></div>\n"
        "            <div class=\"kv\"><b>Fantasia oficial</b><span>${safe(row.nome_fantasia_oficial)}</span></div>\n"
        "            <div class=\"kv\"><b>Status oficial</b><span>${safe(row.situacao_cadastral_oficial)}</span></div>\n"
        "            <div class=\"kv\"><b>Email oficial</b><span>${safe(row.email_oficial)}</span></div>\n"
        "            <div class=\"kv\"><b>Porte</b><span>${safe(row.porte_empresa)}</span></div>\n"
        "            <div class=\"kv\"><b>Natureza</b><span>${safe(row.natureza_juridica)}</span></div>\n"
        "          </div>\n",
        "",
    )
    html = html.replace(
        "option(els.divergencia, 'Todas', ['Razao social', 'Fantasia', 'Email', 'Qualquer divergencia', 'Sem divergencia']);",
        "option(els.divergencia, 'Todas', ['Razao social', 'Fantasia', 'Situacao', 'Email', 'Porte', 'Natureza juridica', 'Endereco', 'Cidade', 'UF', 'Telefone', 'Qualquer inclusao', 'Sem inclusao']);",
    )
    html = html.replace(
        "function matchesDivergence(row, value) {\n"
        "  if (value.includes('__NONE__')) return false;\n"
        "  if (!value.length) return true;\n"
        "  return value.some(item => {\n"
        "    if (item === 'Razao social') return row.divergencia_razao_social === 'S';\n"
        "    if (item === 'Fantasia') return row.divergencia_nome_fantasia === 'S';\n"
        "    if (item === 'Email') return row.divergencia_email === 'S';\n"
        "    if (item === 'Qualquer divergencia') return row.divergencia_label === 'Qualquer divergencia';\n"
        "    return row.divergencia_label === 'Sem divergencia';\n"
        "  });\n"
        "}\n",
        "function isEmptyValue(value) {\n"
        "  return ['', 'sem dado', 'sem uf', 'nan', 'none'].includes(String(value || '').trim().toLowerCase());\n"
        "}\n"
        "\n"
        "function hasInclusion(row, item) {\n"
        "  if (item === 'Razao social') return isEmptyValue(row.razao_original) && !isEmptyValue(row.razao_social_oficial);\n"
        "  if (item === 'Fantasia') return isEmptyValue(row.fantasia_original) && !isEmptyValue(row.nome_fantasia_oficial);\n"
        "  if (item === 'Situacao') return isEmptyValue(row.status_interno_label) && !isEmptyValue(row.situacao_cadastral_oficial);\n"
        "  if (item === 'Email') return (isEmptyValue(row.emails_originais) && !isEmptyValue(row.email_oficial)) || row.email_opencnpj_incluido === 'S';\n"
        "  if (item === 'Porte') return !isEmptyValue(row.porte_empresa);\n"
        "  if (item === 'Natureza juridica') return !isEmptyValue(row.natureza_juridica);\n"
        "  if (item === 'Endereco') return row.endereco_opencnpj_incluido === 'S';\n"
        "  if (item === 'Cidade') return row.cidade_opencnpj_incluida === 'S';\n"
        "  if (item === 'UF') return row.uf_opencnpj_incluida === 'S';\n"
        "  if (item === 'Telefone') return row.telefone_opencnpj_incluido === 'S';\n"
        "  return false;\n"
        "}\n"
        "\n"
        "function hasAnyInclusion(row) {\n"
        "  return ['Razao social', 'Fantasia', 'Situacao', 'Email', 'Porte', 'Natureza juridica', 'Endereco', 'Cidade', 'UF', 'Telefone'].some(item => hasInclusion(row, item));\n"
        "}\n"
        "\n"
        "function matchesDivergence(row, value) {\n"
        "  if (value.includes('__NONE__')) return false;\n"
        "  if (!value.length) return true;\n"
        "  return value.some(item => {\n"
        "    if (item === 'Qualquer inclusao') return hasAnyInclusion(row);\n"
        "    if (item === 'Sem inclusao') return !hasAnyInclusion(row);\n"
        "    return hasInclusion(row, item);\n"
        "  });\n"
        "}\n",
    )
    html = html.replace(
        "divergencia: 'Compara campos cadastrais internos com campos oficiais retornados. Razao social, fantasia e email filtram divergencias especificas; Qualquer divergencia captura qualquer uma dessas diferencas; Sem divergencia mostra fornecedores sem conflito cadastral nesses campos comparados.'",
        "divergencia: 'Filtra os campos incluidos no painel a partir de fonte externa/enriquecimento. Use Razao social, Fantasia, Situacao, Email, Porte, Natureza juridica, Endereco, Cidade, UF ou Telefone para ver inclusoes especificas. Qualquer inclusao mostra fornecedores com pelo menos um campo incluido; Sem inclusao mostra fornecedores sem campo complementar detectado.'",
    )
    html = html.replace(
        "    acao: richHelp('Acao operacional sugerida para tratar o fornecedor.', [",
        "    divergencia: richHelp('Campos incluidos por fonte externa ou enriquecimento.', [\n"
        "      `${tag('Razao social', 'info')} razao preenchida pela fonte oficial quando faltava no cadastro.` ,\n"
        "      `${tag('Fantasia', 'info')} fantasia preenchida pela fonte oficial quando faltava no cadastro.` ,\n"
        "      `${tag('Situacao', 'info')} situacao cadastral preenchida pela fonte oficial quando faltava no cadastro.` ,\n"
        "      `${tag('Email', 'info')} email incluido quando o cadastro interno nao tinha email.` ,\n"
        "      `${tag('Porte', 'info')} porte vindo da OpenCNPJ.` ,\n"
        "      `${tag('Natureza juridica', 'info')} natureza juridica vinda da OpenCNPJ.` ,\n"
        "      `${tag('Endereco', 'info')} endereco incluido quando faltava no cadastro de enderecos.` ,\n"
        "      `${tag('Cidade', 'info')} cidade incluida quando faltava no cadastro de enderecos.` ,\n"
        "      `${tag('UF', 'info')} UF incluida quando faltava no cadastro de enderecos.` ,\n"
        "      `${tag('Telefone', 'info')} telefone incluido quando faltava no cadastro de enderecos.` ,\n"
        "      `${tag('Qualquer inclusao', 'info')} pelo menos uma inclusao em qualquer campo acima.` ,\n"
        "      `${tag('Sem inclusao', 'gray')} nenhum desses campos foi complementado.`\n"
        "    ]),\n"
        "    acao: richHelp('Acao operacional sugerida para tratar o fornecedor.', [",
    )
    html = html.replace(
        "<div class=\"kv\"><b>Endereco</b><span>${safe(row.endereco_completo)}</span></div>",
        "<div class=\"kv\"><b>Endereco</b><span>${enderecoCampo(row, 'endereco_completo', 'endereco_opencnpj_incluido')}</span></div>",
    )
    html = html.replace(
        "<div class=\"kv\"><b>Cidade</b><span>${safe(row.endereco_municipio)}</span></div>",
        "<div class=\"kv\"><b>Cidade</b><span>${enderecoCampo(row, 'endereco_municipio', 'cidade_opencnpj_incluida')}</span></div>",
    )
    html = html.replace(
        "<div class=\"kv\"><b>UF</b><span>${safe(row.endereco_uf)}</span></div>",
        "<div class=\"kv\"><b>UF</b><span>${enderecoCampo(row, 'endereco_uf', 'uf_opencnpj_incluida')}</span></div>",
    )
    html = html.replace(
        "<div class=\"kv\"><b>Telefones</b><span>${safe(row.telefones_oficiais)}</span></div>",
        "<div class=\"kv\"><b>Telefones</b><span>${formatPhones(row.telefones_oficiais)}${checkOpenCnpj(row.telefone_opencnpj_incluido)}</span></div>",
    )
    html = html.replace(
        "<div class=\"kv\"><b>Emails</b><span>${infoEmails(row)}</span></div>",
        "<div class=\"kv\"><b>Emails</b><span>${enderecoEmail(row)}</span></div>",
    )
    html = html.replace(
        '<div class="kv"><b>Curva</b><span><span class="pill ${abcPillClass(row.curva_label)}">${row.curva_label}</span> | pos. ${safe(row.curva_posicao)} | ${row.curva_valor_fmt}</span></div>\n'
        '            <div class="kv"><b>NFe</b><span>${safe(row.nfe_linhas)} linhas | ${row.nfe_valor_fmt}</span></div>',
        '<div class="kv"><b>Curva</b><span><span class="pill ${abcPillClass(row.curva_label)}">${row.curva_label}</span> | posição ${safe(row.curva_posicao)}</span></div>\n'
        '            <div class="kv"><b>Total</b><span>${row.nfe_valor_fmt}</span></div>\n'
        '            <div class="kv"><b>NFe</b><span>${safe(row.nfe_linhas)} Notas</span></div>',
    )
    html = html.replace(
        '<div class="supplier-meta">${companyTags(row)}<span class="doc">${safe(row.documento_formatado)}</span></div>',
        '<div class="supplier-meta">${companyTags(row)}${documentoComCopia(row)}</div>',
    )
    html = html.replace(
        "  els.tbody.querySelectorAll('tr.summary').forEach(tr => {\n"
        "    tr.addEventListener('click', () => {",
        "  els.tbody.querySelectorAll('.copy-doc').forEach(btn => {\n"
        "    btn.addEventListener('click', async event => {\n"
        "      event.stopPropagation();\n"
        "      const value = btn.dataset.doc || '';\n"
        "      try {\n"
        "        await navigator.clipboard.writeText(value);\n"
        "        btn.classList.add('copied');\n"
        "        btn.textContent = '✓';\n"
        "        setTimeout(() => { btn.classList.remove('copied'); btn.textContent = '⧉'; }, 1000);\n"
        "      } catch (err) {\n"
        "        const input = document.createElement('input');\n"
        "        input.value = value;\n"
        "        document.body.appendChild(input);\n"
        "        input.select();\n"
        "        document.execCommand('copy');\n"
        "        input.remove();\n"
        "      }\n"
        "    });\n"
        "  });\n"
        "  els.tbody.querySelectorAll('tr.summary').forEach(tr => {\n"
        "    tr.addEventListener('click', () => {",
    )
    html = html.replace(
        "            <div class=\"kv\"><b>Contato</b><span>${safe(row.contatos_qsa)}</span></div>\n"
        "          </div>\n"
        "          <div class=\"panel\"><h3>Fiscal e credito</h3>",
        "            <div class=\"kv\"><b>Contato</b><span>${safe(row.contatos_qsa)}</span></div>\n"
        "          </div>\n"
        "          <div class=\"panel\"><h3>Fiscal e credito</h3>",
    )
    html = html.replace(
        "            <div class=\"kv\"><b>Saneamento</b><span><span class=\"pill ${pillClass(row.saneamento_label)}\">${row.saneamento_label}</span></span></div>\n"
        "          </div>\n"
        "        </div>",
        "            <div class=\"kv\"><b>Saneamento</b><span><span class=\"pill ${pillClass(row.saneamento_label)}\">${row.saneamento_label}</span></span></div>\n"
        "          </div>\n"
        "          <div class=\"panel\"><h3>Score de Cadastro</h3>\n"
        "            ${scorePanel(row)}\n"
        "          </div>\n"
        "        </div>",
    )
    html = html.replace(
        "Versao 06: fornecedores da curva ABC total, com enderecos internos, cache/API OpenCNPJ e comparacao de UF/municipio.",
        "Versao 06b: endereco do cadastro atual como padrao; OpenCNPJ aparece apenas para completar campo vazio.",
    )
    OUTPUT_HTML_06B.write_text(html, encoding="utf-8")


def build_html(rows: list[dict[str, Any]]) -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    original_target = v05.AUDIT_HTML_FILE
    v05.AUDIT_HTML_FILE = OUTPUT_HTML_06B
    try:
        v05.build_html(rows)
    finally:
        v05.AUDIT_HTML_FILE = original_target
    patch_html()


def write_summary(rows: list[dict[str, Any]]) -> None:
    with_open = sum(1 for row in rows if row.get("endereco_tags"))
    summary = {
        "versao": "06b",
        "base": str(INPUT_AUDIT.relative_to(BASE_DIR)),
        "html": str(OUTPUT_HTML_06B.relative_to(BASE_DIR)),
        "csv": str(OUTPUT_AUDIT_06B.relative_to(BASE_DIR)),
        "registros": len(rows),
        "registros_com_algum_campo_endereco_complementado_por_opencnpj": with_open,
        "regra": "Cadastro atual e fonte principal; OpenCNPJ so complementa campo vazio.",
    }
    OUTPUT_SUMMARY_06B.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def update_diary(rows: list[dict[str, Any]]) -> None:
    diary = BASE_DIR / "docs" / "DIARIO_DE_BORDO.md"
    marker = "#### Output 06b - Endereco preferencial do cadastro"
    current = diary.read_text(encoding="utf-8") if diary.exists() else ""
    if marker in current:
        return
    entry = f"""

{marker}

- Foi criado o output visual `06b` a partir da base de auditoria do `06`.
- O layout geral do painel foi preservado.
- A regra do box de endereco passou a ser: cadastro atual como fonte principal; OpenCNPJ somente quando o campo correspondente esta vazio no cadastro atual.
- Campos complementados por OpenCNPJ aparecem destacados com tag azul `incluido OpenCNPJ`.
- Registros no `06b`: `{len(rows)}`.
- Registros com pelo menos um campo de endereco/contato complementado por OpenCNPJ: `{sum(1 for row in rows if row.get('endereco_tags'))}`.
- Arquivo HTML gerado: `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.
"""
    with diary.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def main() -> None:
    rows = load_rows()
    write_csv(OUTPUT_AUDIT_06B, rows)
    build_html(rows)
    write_summary(rows)
    update_diary(rows)
    print(f"HTML gerado: {OUTPUT_HTML_06B}")
    print(f"CSV gerado: {OUTPUT_AUDIT_06B}")
    print(f"Registros: {len(rows)}")


if __name__ == "__main__":
    main()
