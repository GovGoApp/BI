from __future__ import annotations

import argparse
import csv
import html
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BASE_DIR.parent
SCRIPT_DIR = BASE_DIR / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    import yaml
except ImportError as exc:  # pragma: no cover - friendly CLI error
    raise SystemExit("PyYAML nao esta instalado. Rode: pip install PyYAML") from exc

from zoho_analytics_client import ZohoAnalyticsClient, ZohoAnalyticsConfig, load_env_file  # noqa: E402


DEFAULT_CONFIG = BASE_DIR / "config" / "bi_suprimentos_impacto_poc.yml"
DEFAULT_OUTPUT = BASE_DIR / "output" / "modular_test" / "bi_impacto_modular_poc.html"
DEFAULT_DATA_JSON = BASE_DIR / "output" / "modular_test" / "data" / "impacto_modular_poc_data.json"


def repo_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else REPO_DIR / path


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Configuracao invalida: {path}")
    return data


def refresh_from_zoho(config: dict[str, Any], env_file: Path, interval: int = 3) -> Path:
    source = config["source"]
    output_path = repo_path(source["local_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    load_env_file(env_file)
    client = ZohoAnalyticsClient(ZohoAnalyticsConfig.from_env())
    token = client.refresh_access_token()
    job_id = client.create_export_job_for_sql(source["sql_query"], access_token=token, response_format="csv")
    client.wait_for_export_job(job_id, access_token=token, interval_seconds=interval)
    client.download_export_job(job_id, output_path, access_token=token)
    return output_path


def brl(value: float) -> str:
    if value is None or math.isnan(float(value)):
        return "R$ 0"
    n = float(value)
    sign = "-" if n < 0 else ""
    n = abs(n)
    formatted = f"{n:,.0f}".replace(",", ".")
    return f"{sign}R$ {formatted}"


def brl2(value: float) -> str:
    if value is None or math.isnan(float(value)):
        return "R$ 0,00"
    n = float(value)
    sign = "-" if n < 0 else ""
    n = abs(n)
    formatted = f"{n:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"{sign}R$ {formatted}"


def pct(value: float) -> str:
    if value is None or math.isnan(float(value)):
        return "0,0%"
    return f"{float(value) * 100:.1f}%".replace(".", ",")


def num(value: float) -> str:
    if value is None or math.isnan(float(value)):
        return "0"
    return f"{float(value):,.0f}".replace(",", ".")


def clean_text(value: Any, fallback: str = "Sem dado") -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def parse_number(value: Any) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    if not text:
        return 0.0
    if "," in text and "." in text and text.rfind(",") > text.rfind("."):
        text = text.replace(".", "").replace(",", ".")
    elif "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def group_by_field(records: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for record in records:
        key = clean_text(record.get(field))
        item = grouped.setdefault(key, {"label": key, "impact": 0.0, "total": 0.0, "rows": 0, "ids": set()})
        item["impact"] += float(record["IMP_COT_POS"])
        item["total"] += float(record["TOTAL"])
        item["rows"] += 1
        item["ids"].add(clean_text(record.get("ID")))

    result = []
    for item in grouped.values():
        result.append(
            {
                field: item["label"],
                "impact": item["impact"],
                "total": item["total"],
                "rows": item["rows"],
                "ids": len(item["ids"]),
            }
        )
    return sorted(result, key=lambda row: float(row["impact"]), reverse=True)


def build_top_ids(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str, str, str], dict[str, Any]] = {}
    for record in records:
        key = (
            clean_text(record.get("ID")),
            clean_text(record.get("NMPRODUTO_OFICIAL")),
            clean_text(record.get("CAT2")),
            clean_text(record.get("UF")),
            clean_text(record.get("FORN_MIN_COT")),
            clean_text(record.get("CURVA_ID")),
        )
        item = grouped.setdefault(
            key,
            {
                "ID": key[0],
                "NMPRODUTO_OFICIAL": key[1],
                "CAT2": key[2],
                "UF": key[3],
                "FORN_MIN_COT": key[4],
                "CURVA_ID": key[5],
                "IMP_COT_POS": 0.0,
                "IMP_COT_LIQ": 0.0,
                "TOTAL": 0.0,
                "QTDE_EST": 0.0,
                "PMP_SUM": 0.0,
                "PRE_SUM": 0.0,
                "LINHAS": 0,
            },
        )
        item["IMP_COT_POS"] += float(record["IMP_COT_POS"])
        item["IMP_COT_LIQ"] += float(record["IMP_COT"])
        item["TOTAL"] += float(record["TOTAL"])
        item["QTDE_EST"] += float(record["QTDE_EST"])
        item["PMP_SUM"] += float(record["VLRUNITPOND_EST"])
        item["PRE_SUM"] += float(record["PRE_MIN_COT"])
        item["LINHAS"] += 1

    result = []
    for item in grouped.values():
        divisor = item["LINHAS"] or 1
        row = dict(item)
        row["PMP_COMPRADO"] = item["PMP_SUM"] / divisor
        row["PRE_MIN_COT"] = item["PRE_SUM"] / divisor
        row.pop("PMP_SUM", None)
        row.pop("PRE_SUM", None)
        result.append(row)
    return sorted(result, key=lambda row: float(row["IMP_COT_POS"]), reverse=True)[:50]


def prepare_data(config: dict[str, Any]) -> dict[str, Any]:
    csv_path = repo_path(config["source"]["local_path"])
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Fonte nao encontrada: {csv_path}. Execute com --refresh-zoho ou gere o CSV primeiro."
        )

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        expected = config["source"]["expected_fields"]
        missing = [field for field in expected if field not in fieldnames]
        if missing:
            raise ValueError("Campos ausentes na fonte real: " + ", ".join(missing))

        numeric_fields = ["TOTAL", "QTDE_EST", "VLRUNITPOND_EST", "PMP_ID_1", "PRE_MIN_COT", "IMP_COT"]
        text_fields = ["ID", "NMPRODUTO_OFICIAL", "CAT2", "UF", "NMEMP", "MESANO", "FORN_MIN_COT", "CURVA_ID"]
        records: list[dict[str, Any]] = []
        for raw_row in reader:
            record: dict[str, Any] = {}
            for field in text_fields:
                record[field] = clean_text(raw_row.get(field))
            for field in numeric_fields:
                record[field] = parse_number(raw_row.get(field))
            record["IMP_COT_POS"] = max(float(record["IMP_COT"]), 0.0)
            if float(record["IMP_COT"]) > 0.009:
                record["STATUS_IMP"] = "Acima do menor"
            elif float(record["IMP_COT"]) < -0.009:
                record["STATUS_IMP"] = "Abaixo do menor"
            else:
                record["STATUS_IMP"] = "No menor"
            records.append(record)

    total_rows = len(records)
    total_compra = sum(float(record["TOTAL"]) for record in records)
    impact_total = sum(float(record["IMP_COT_POS"]) for record in records)
    impact_net = sum(float(record["IMP_COT"]) for record in records)
    above_rows = sum(1 for record in records if float(record["IMP_COT"]) > 0.009)
    pct_above = above_rows / total_rows if total_rows else 0
    unique_ids = len({clean_text(record.get("ID")) for record in records})
    ids_with_impact = len({clean_text(record.get("ID")) for record in records if float(record["IMP_COT"]) > 0.009})

    by_uf = group_by_field(records, "UF")
    by_cat = group_by_field(records, "CAT2")
    by_month = group_by_field(records, "MESANO")
    by_month = sorted(by_month, key=lambda row: clean_text(row.get("MESANO")))
    top_ids = build_top_ids(records)

    client_columns = [
        "ID",
        "NMPRODUTO_OFICIAL",
        "CAT2",
        "UF",
        "NMEMP",
        "MESANO",
        "TOTAL",
        "QTDE_EST",
        "VLRUNITPOND_EST",
        "PMP_ID_1",
        "PRE_MIN_COT",
        "FORN_MIN_COT",
        "IMP_COT",
        "IMP_COT_POS",
        "CURVA_ID",
        "STATUS_IMP",
    ]
    client_rows = [{field: record.get(field) for field in client_columns} for record in records]

    uf_leader = by_uf[0] if by_uf else {"UF": "Sem dado", "impact": 0}
    cat_leader = by_cat[0] if by_cat else {"CAT2": "Sem dado", "impact": 0}

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": {
            "name": config["source"]["name"],
            "workspace": config["source"]["workspace"],
            "local_path": config["source"]["local_path"],
            "rows": total_rows,
        },
        "metrics": {
            "impacto_cotacao_total": impact_total,
            "impacto_cotacao_liquido": impact_net,
            "total_compra": total_compra,
            "percentual_acima_menor": pct_above,
            "linhas_acima_menor": above_rows,
            "ids_unicos": unique_ids,
            "ids_com_impacto": ids_with_impact,
            "uf_lider": clean_text(uf_leader.get("UF")),
            "uf_lider_impacto": float(uf_leader.get("impact", 0)),
            "categoria_lider": clean_text(cat_leader.get("CAT2")),
            "categoria_lider_impacto": float(cat_leader.get("impact", 0)),
        },
        "series": {
            "impacto_por_uf": by_uf[:12],
            "impacto_por_categoria": by_cat[:12],
            "impacto_por_mes": by_month,
        },
        "tables": {
            "top_ids_imp_cot": top_ids,
        },
        "client_rows": client_rows,
    }


def grid_style(item: dict[str, Any]) -> str:
    col_start = int(item["col_start"])
    col_span = int(item["col_span"])
    row_start = int(item["row_start"])
    row_span = int(item["row_span"])
    return (
        f"grid-column:{col_start} / span {col_span};"
        f"grid-row:{row_start} / span {row_span};"
    )


def element_shell(element: dict[str, Any], item: dict[str, Any], body: str) -> str:
    title = html.escape(element["title"])
    element_id = html.escape(element["id"])
    return f"""
    <section class="module" data-element-id="{element_id}" style="{grid_style(item)}">
      <div class="module-handle">
        <h3>{title}</h3>
        <span>{element_id}</span>
      </div>
      <div class="module-body">{body}</div>
    </section>
    """


def render_kpi(element: dict[str, Any], data: dict[str, Any]) -> str:
    element_id = html.escape(element["id"])
    metric_id = element["data_bindings"]["primary_metric"]
    metrics = data["metrics"]
    value = metrics.get(metric_id)
    if metric_id in {"impacto_cotacao_total", "impacto_cotacao_liquido", "uf_lider_impacto"}:
        value_text = brl(float(value or 0))
    elif metric_id == "percentual_acima_menor":
        value_text = pct(float(value or 0))
    elif metric_id == "ids_com_impacto":
        value_text = num(float(value or 0))
    elif metric_id == "uf_lider_impacto":
        value_text = brl(float(value or 0))
    else:
        value_text = str(value or "")

    if element["id"] == "impacto.kpi.uf_lider":
        value_text = html.escape(data["metrics"]["uf_lider"])
        subtitle = f"{brl(data['metrics']['uf_lider_impacto'])} de impacto positivo"
    else:
        subtitle = next(
            (sub.get("value", "") for sub in element.get("sub_elements", []) if sub.get("type") == "text.subtitle"),
            "",
        )

    origin = next((sub.get("value", "") for sub in element.get("sub_elements", []) if sub.get("type") == "text.origin"), "")
    return f"""
      <div class="kpi-value" data-kpi-value="{element_id}">{value_text}</div>
      <div class="kpi-sub" data-kpi-sub="{element_id}">{html.escape(subtitle)}</div>
      <div class="kpi-origin">{html.escape(origin)}</div>
    """


def render_bar_chart(rows: list[dict[str, Any]], label_field: str, value_field: str) -> str:
    max_value = max((float(row.get(value_field, 0) or 0) for row in rows), default=1)
    parts: list[str] = ['<div class="bar-list">']
    for row in rows:
        value = float(row.get(value_field, 0) or 0)
        width = 0 if max_value == 0 else max(2, value / max_value * 100)
        label = html.escape(clean_text(row.get(label_field)))
        parts.append(
            f"""
            <div class="bar-row">
              <div class="bar-label">{label}</div>
              <div class="bar-track"><div class="bar-fill" style="width:{width:.2f}%"></div></div>
              <div class="bar-value">{brl(value)}</div>
            </div>
            """
        )
    parts.append("</div>")
    return "\n".join(parts)


def render_chart(element: dict[str, Any], data: dict[str, Any]) -> str:
    series_id = element["data_bindings"]["series"]
    if series_id == "impacto_por_uf":
        body = render_bar_chart(data["series"][series_id], "UF", "impact")
    else:
        body = render_bar_chart(data["series"][series_id], "CAT2", "impact")
    subtitle = next((sub.get("value", "") for sub in element.get("sub_elements", []) if sub.get("type") == "text.subtitle"), "")
    return f'<div class="chart-sub">{html.escape(subtitle)}</div>{body}'


def render_table(element: dict[str, Any], data: dict[str, Any]) -> str:
    rows = data["tables"]["top_ids_imp_cot"]
    columns = next(sub["columns"] for sub in element["sub_elements"] if sub.get("id") == "columns")
    headers = "".join(f"<th>{html.escape(col['label'])}</th>" for col in columns)
    body_rows = []
    for row in rows[:30]:
        cells = []
        for col in columns:
            field = col["field"]
            value = row.get(field, "")
            fmt = col.get("format")
            if fmt == "currency":
                cell = brl2(float(value or 0))
                cls = "num"
            elif fmt == "number":
                cell = num(float(value or 0))
                cls = "num"
            elif fmt == "badge":
                cell = f'<span class="badge">{html.escape(clean_text(value))}</span>'
                cls = ""
            else:
                cell = html.escape(clean_text(value))
                cls = ""
            cells.append(f'<td class="{cls}">{cell}</td>')
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    return f"""
      <div class="table-wrap">
        <table>
          <thead><tr>{headers}</tr></thead>
          <tbody data-table="top_ids_imp_cot">{''.join(body_rows)}</tbody>
        </table>
      </div>
    """


def render_note(config: dict[str, Any], data: dict[str, Any]) -> str:
    metrics = data["metrics"]
    source = data["source"]
    return f"""
      <dl class="note-list">
        <dt>Fonte</dt><dd>{html.escape(source['name'])}</dd>
        <dt>Workspace</dt><dd>{html.escape(source['workspace'])}</dd>
        <dt>Linhas reais</dt><dd>{num(source['rows'])}</dd>
        <dt>Dataset</dt><dd>{html.escape(config['dataset']['id'])}</dd>
        <dt>Grid</dt><dd>16 colunas</dd>
        <dt>Impacto liquido</dt><dd>{brl(metrics['impacto_cotacao_liquido'])}</dd>
        <dt>Categoria lider</dt><dd>{html.escape(metrics['categoria_lider'])}</dd>
      </dl>
      <p class="small-note">Use "Modo edicao" para arrastar os blocos. O layout e salvo no localStorage do navegador.</p>
    """


def render_element(element: dict[str, Any], item: dict[str, Any], config: dict[str, Any], data: dict[str, Any]) -> str:
    if element["type"] == "kpi":
        body = render_kpi(element, data)
    elif element["type"] == "chart":
        body = render_chart(element, data)
    elif element["type"] == "table":
        body = render_table(element, data)
    else:
        body = render_note(config, data)
    return element_shell(element, item, body)


def build_client_script(config: dict[str, Any]) -> str:
    table_element = next(element for element in config["elements"] if element["id"] == "impacto.table.top_ids_imp_cot")
    table_columns = next(sub["columns"] for sub in table_element["sub_elements"] if sub.get("id") == "columns")
    script = r"""
    const rawData = JSON.parse(document.getElementById('realData').textContent);
    const rows = rawData.client_rows || [];
    const defaultLayout = __DEFAULT_LAYOUT__;
    const tableColumns = __TABLE_COLUMNS__;
    const storageKey = 'bi-suprimentos-impacto-poc-layout-v1';
    const grid = document.getElementById('grid');
    let editMode = false;

    const brlFmt0 = new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      maximumFractionDigits: 0
    });
    const brlFmt2 = new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
    const numFmt0 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });

    function asNum(value) {
      const n = Number(value);
      return Number.isFinite(n) ? n : 0;
    }

    function cleanText(value) {
      if (value === null || value === undefined || String(value).trim() === '') return 'Sem dado';
      return String(value).trim();
    }

    function escapeHtml(value) {
      return cleanText(value).replace(/[&<>"']/g, function(ch) {
        return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch];
      });
    }

    function brl(value) { return brlFmt0.format(asNum(value)); }
    function brl2(value) { return brlFmt2.format(asNum(value)); }
    function num(value) { return numFmt0.format(asNum(value)); }
    function pct(value) {
      return (asNum(value) * 100).toLocaleString('pt-BR', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
      }) + '%';
    }

    function moduleById(id) {
      return Array.from(document.querySelectorAll('.module')).find(el => el.dataset.elementId === id);
    }

    function setKpi(elementId, value, subtitle) {
      const module = moduleById(elementId);
      if (!module) return;
      const valueEl = module.querySelector('.kpi-value');
      const subEl = module.querySelector('.kpi-sub');
      if (valueEl) valueEl.textContent = value;
      if (subEl) subEl.textContent = subtitle;
    }

    function uniqueValues(field) {
      return Array.from(new Set(rows.map(row => cleanText(row[field]))))
        .filter(value => value !== 'Sem dado')
        .sort((a, b) => a.localeCompare(b, 'pt-BR', { numeric: true }));
    }

    function fillSelect(id, field) {
      const select = document.getElementById(id);
      const current = select.value;
      const options = ['<option value="">Todas</option>'].concat(
        uniqueValues(field).map(value => '<option value="' + escapeHtml(value) + '">' + escapeHtml(value) + '</option>')
      );
      select.innerHTML = options.join('');
      select.value = current;
    }

    function populateFilters() {
      fillSelect('ufFilter', 'UF');
      fillSelect('catFilter', 'CAT2');
      fillSelect('curvaFilter', 'CURVA_ID');
    }

    function filteredRows() {
      const uf = document.getElementById('ufFilter').value;
      const cat = document.getElementById('catFilter').value;
      const curva = document.getElementById('curvaFilter').value;
      const status = document.getElementById('statusFilter').value;
      return rows.filter(row => {
        return (!uf || cleanText(row.UF) === uf)
          && (!cat || cleanText(row.CAT2) === cat)
          && (!curva || cleanText(row.CURVA_ID) === curva)
          && (!status || cleanText(row.STATUS_IMP) === status);
      });
    }

    function groupRows(dataRows, field) {
      const grouped = new Map();
      for (const row of dataRows) {
        const key = cleanText(row[field]);
        if (!grouped.has(key)) {
          grouped.set(key, { label: key, impact: 0, total: 0, rows: 0, ids: new Set() });
        }
        const item = grouped.get(key);
        item.impact += Math.max(asNum(row.IMP_COT), 0);
        item.total += asNum(row.TOTAL);
        item.rows += 1;
        item.ids.add(cleanText(row.ID));
      }
      return Array.from(grouped.values())
        .map(item => ({
          label: item.label,
          impact: item.impact,
          total: item.total,
          rows: item.rows,
          ids_count: item.ids.size
        }))
        .sort((a, b) => b.impact - a.impact);
    }

    function aggregateTopIds(dataRows) {
      const grouped = new Map();
      for (const row of dataRows) {
        const keyParts = [
          cleanText(row.ID),
          cleanText(row.NMPRODUTO_OFICIAL),
          cleanText(row.CAT2),
          cleanText(row.UF),
          cleanText(row.FORN_MIN_COT),
          cleanText(row.CURVA_ID)
        ];
        const key = keyParts.join('||');
        if (!grouped.has(key)) {
          grouped.set(key, {
            ID: keyParts[0],
            NMPRODUTO_OFICIAL: keyParts[1],
            CAT2: keyParts[2],
            UF: keyParts[3],
            FORN_MIN_COT: keyParts[4],
            CURVA_ID: keyParts[5],
            IMP_COT_POS: 0,
            IMP_COT_LIQ: 0,
            TOTAL: 0,
            QTDE_EST: 0,
            PMP_SUM: 0,
            PRE_SUM: 0,
            LINHAS: 0
          });
        }
        const item = grouped.get(key);
        item.IMP_COT_POS += Math.max(asNum(row.IMP_COT), 0);
        item.IMP_COT_LIQ += asNum(row.IMP_COT);
        item.TOTAL += asNum(row.TOTAL);
        item.QTDE_EST += asNum(row.QTDE_EST);
        item.PMP_SUM += asNum(row.VLRUNITPOND_EST);
        item.PRE_SUM += asNum(row.PRE_MIN_COT);
        item.LINHAS += 1;
      }
      return Array.from(grouped.values())
        .map(item => ({
          ...item,
          PMP_COMPRADO: item.LINHAS ? item.PMP_SUM / item.LINHAS : 0,
          PRE_MIN_COT: item.LINHAS ? item.PRE_SUM / item.LINHAS : 0
        }))
        .sort((a, b) => b.IMP_COT_POS - a.IMP_COT_POS)
        .slice(0, 30);
    }

    function aggregate(dataRows) {
      const rowCount = dataRows.length;
      const impactTotal = dataRows.reduce((acc, row) => acc + Math.max(asNum(row.IMP_COT), 0), 0);
      const impactNet = dataRows.reduce((acc, row) => acc + asNum(row.IMP_COT), 0);
      const totalCompra = dataRows.reduce((acc, row) => acc + asNum(row.TOTAL), 0);
      const aboveRows = dataRows.filter(row => asNum(row.IMP_COT) > 0.009).length;
      const ids = new Set(dataRows.map(row => cleanText(row.ID)));
      const idsImpact = new Set(dataRows.filter(row => asNum(row.IMP_COT) > 0.009).map(row => cleanText(row.ID)));
      const byUf = groupRows(dataRows, 'UF');
      const byCat = groupRows(dataRows, 'CAT2');
      return {
        rowCount,
        impactTotal,
        impactNet,
        totalCompra,
        aboveRows,
        pctAbove: rowCount ? aboveRows / rowCount : 0,
        idsCount: ids.size,
        idsImpactCount: idsImpact.size,
        ufLeader: byUf[0] || { label: 'Sem dado', impact: 0 },
        catLeader: byCat[0] || { label: 'Sem dado', impact: 0 },
        byUf,
        byCat,
        topIds: aggregateTopIds(dataRows)
      };
    }

    function renderBars(elementId, series) {
      const module = moduleById(elementId);
      if (!module) return;
      const list = module.querySelector('.bar-list');
      if (!list) return;
      if (!series.length) {
        list.innerHTML = '<div class="empty">Sem dados para o recorte atual.</div>';
        return;
      }
      const maxValue = Math.max.apply(null, series.map(item => item.impact).concat([1]));
      list.innerHTML = series.slice(0, 12).map(item => {
        const width = Math.max(2, item.impact / maxValue * 100);
        return '<div class="bar-row">'
          + '<div class="bar-label">' + escapeHtml(item.label) + '</div>'
          + '<div class="bar-track"><div class="bar-fill" style="width:' + width.toFixed(2) + '%"></div></div>'
          + '<div class="bar-value">' + brl(item.impact) + '</div>'
          + '</div>';
      }).join('');
    }

    function formatCell(value, format) {
      if (format === 'currency') return brl2(value);
      if (format === 'number') return num(value);
      if (format === 'badge') return '<span class="badge">' + escapeHtml(value) + '</span>';
      return escapeHtml(value);
    }

    function renderTopTable(rowsForTable) {
      const tbody = document.querySelector('[data-table="top_ids_imp_cot"]');
      if (!tbody) return;
      if (!rowsForTable.length) {
        tbody.innerHTML = '<tr><td colspan="' + tableColumns.length + '">Sem dados para o recorte atual.</td></tr>';
        return;
      }
      tbody.innerHTML = rowsForTable.map(row => {
        const cells = tableColumns.map(col => {
          const cls = (col.format === 'currency' || col.format === 'number') ? ' class="num"' : '';
          return '<td' + cls + '>' + formatCell(row[col.field], col.format) + '</td>';
        }).join('');
        return '<tr>' + cells + '</tr>';
      }).join('');
    }

    function updateNote(summary) {
      const module = moduleById('impacto.note.configuracao');
      if (!module) return;
      const list = module.querySelector('.note-list');
      if (!list) return;
      list.innerHTML = ''
        + '<dt>Fonte</dt><dd>' + escapeHtml(rawData.source.name) + '</dd>'
        + '<dt>Workspace</dt><dd>' + escapeHtml(rawData.source.workspace) + '</dd>'
        + '<dt>Linhas fonte</dt><dd>' + num(rawData.source.rows) + '</dd>'
        + '<dt>Linhas filtradas</dt><dd>' + num(summary.rowCount) + '</dd>'
        + '<dt>Grid</dt><dd>16 colunas</dd>'
        + '<dt>Impacto liquido</dt><dd>' + brl(summary.impactNet) + '</dd>'
        + '<dt>Categoria lider</dt><dd>' + escapeHtml(summary.catLeader.label) + '</dd>';
    }

    function renderFiltered() {
      const dataRows = filteredRows();
      const summary = aggregate(dataRows);
      setKpi('impacto.kpi.impacto_total', brl(summary.impactTotal), num(summary.rowCount) + ' linhas no recorte');
      setKpi('impacto.kpi.percentual_acima_menor', pct(summary.pctAbove), num(summary.aboveRows) + ' linhas com IMP_COT > 0');
      setKpi('impacto.kpi.ids_com_impacto', num(summary.idsImpactCount), num(summary.idsCount) + ' IDs no recorte');
      setKpi('impacto.kpi.uf_lider', summary.ufLeader.label, brl(summary.ufLeader.impact) + ' de impacto positivo');
      renderBars('impacto.chart.impacto_por_uf', summary.byUf);
      renderBars('impacto.chart.impacto_por_categoria', summary.byCat);
      renderTopTable(summary.topIds);
      updateNote(summary);
    }

    function applyLayout(items) {
      for (const item of items) {
        const el = moduleById(item.element);
        if (!el) continue;
        el.style.gridColumn = item.col_start + ' / span ' + item.col_span;
        el.style.gridRow = item.row_start + ' / span ' + item.row_span;
      }
    }

    function readCurrentLayout() {
      return defaultLayout.map(item => {
        const el = moduleById(item.element);
        if (!el) return item;
        return {
          ...item,
          col_start: Number(el.dataset.colStart || item.col_start),
          row_start: Number(el.dataset.rowStart || item.row_start)
        };
      });
    }

    function initLayout() {
      const saved = localStorage.getItem(storageKey);
      const items = saved ? JSON.parse(saved) : defaultLayout;
      applyLayout(items);
      for (const item of items) {
        const el = moduleById(item.element);
        if (el) {
          el.dataset.colStart = item.col_start;
          el.dataset.rowStart = item.row_start;
          el.dataset.colSpan = item.col_span;
          el.dataset.rowSpan = item.row_span;
        }
      }
    }

    function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

    function enableDrag() {
      document.querySelectorAll('.module').forEach(module => {
        const handle = module.querySelector('.module-handle');
        handle.onpointerdown = ev => {
          if (!editMode) return;
          ev.preventDefault();
          module.setPointerCapture(ev.pointerId);
          const startX = ev.clientX;
          const startY = ev.clientY;
          const startCol = Number(module.dataset.colStart);
          const startRow = Number(module.dataset.rowStart);
          const colSpan = Number(module.dataset.colSpan);
          const rowSpan = Number(module.dataset.rowSpan);
          const gridRect = grid.getBoundingClientRect();
          const colW = gridRect.width / 16;
          const rowH = 34;
          module.classList.add('editable');
          module.onpointermove = moveEv => {
            const dx = Math.round((moveEv.clientX - startX) / colW);
            const dy = Math.round((moveEv.clientY - startY) / rowH);
            const nextCol = clamp(startCol + dx, 1, 16 - colSpan + 1);
            const nextRow = clamp(startRow + dy, 1, 80);
            module.dataset.colStart = nextCol;
            module.dataset.rowStart = nextRow;
            module.style.gridColumn = nextCol + ' / span ' + colSpan;
            module.style.gridRow = nextRow + ' / span ' + rowSpan;
          };
          module.onpointerup = () => {
            module.classList.remove('editable');
            module.onpointermove = null;
            module.onpointerup = null;
            localStorage.setItem(storageKey, JSON.stringify(readCurrentLayout()));
          };
        };
      });
    }

    document.getElementById('editToggle').onclick = () => {
      editMode = !editMode;
      document.body.classList.toggle('edit', editMode);
      document.getElementById('editToggle').textContent = editMode ? 'Sair do modo edicao' : 'Modo edicao';
    };
    document.getElementById('resetLayout').onclick = () => {
      localStorage.removeItem(storageKey);
      initLayout();
    };
    ['ufFilter', 'catFilter', 'curvaFilter', 'statusFilter'].forEach(id => {
      document.getElementById(id).addEventListener('change', renderFiltered);
    });

    populateFilters();
    initLayout();
    enableDrag();
    renderFiltered();
    """
    return (
        script.replace("__DEFAULT_LAYOUT__", json.dumps(config["layout"]["items"], ensure_ascii=False))
        .replace("__TABLE_COLUMNS__", json.dumps(table_columns, ensure_ascii=False))
    )


def build_html(config: dict[str, Any], data: dict[str, Any]) -> str:
    elements = {element["id"]: element for element in config["elements"]}
    modules = []
    for item in config["layout"]["items"]:
        element = elements[item["element"]]
        modules.append(render_element(element, item, config, data))

    embedded_data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    client_script = build_client_script(config)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(config['title'])}</title>
  <style>
    :root {{
      --bg:#f4f6fa; --panel:#ffffff; --ink:#172033; --muted:#667085;
      --line:#d9e0ec; --line-soft:#edf1f7; --blue:#2563eb; --green:#159947;
      --red:#b42318; --amber:#b7791f; --shadow:0 8px 26px rgba(23,32,51,.08);
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Segoe UI, Arial, sans-serif; color:var(--ink); background:var(--bg); }}
    header {{ padding:18px 22px; background:#111827; color:white; display:flex; align-items:center; justify-content:space-between; gap:16px; }}
    h1 {{ margin:0; font-size:19px; letter-spacing:0; }}
    .header-sub {{ color:#b8c0cc; font-size:12px; margin-top:3px; }}
    .actions {{ display:flex; gap:8px; align-items:center; }}
    button {{ border:1px solid #4b5563; background:#1f2937; color:#fff; border-radius:6px; padding:8px 10px; cursor:pointer; font-size:12px; }}
    button.primary {{ background:var(--blue); border-color:var(--blue); }}
    main {{ padding:16px; max-width:1600px; margin:0 auto; }}
    .filterbar {{ display:grid; grid-template-columns:repeat(4, minmax(160px,1fr)); gap:10px; margin-bottom:12px; }}
    .filter {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:9px 10px; }}
    .filter label {{ display:block; font-size:11px; text-transform:uppercase; color:var(--muted); margin-bottom:5px; }}
    select {{ width:100%; border:0; outline:0; color:var(--ink); background:white; font-size:13px; }}
    .grid {{ display:grid; grid-template-columns:repeat(16, minmax(0, 1fr)); grid-auto-rows:24px; gap:10px; align-items:stretch; }}
    .module {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); min-width:0; overflow:hidden; }}
    .module.editable {{ outline:2px dashed var(--blue); outline-offset:-4px; }}
    .module-handle {{ padding:10px 12px; border-bottom:1px solid var(--line-soft); display:flex; align-items:center; justify-content:space-between; gap:10px; cursor:default; }}
    .edit .module-handle {{ cursor:move; }}
    .module-handle h3 {{ margin:0; font-size:13px; font-weight:700; }}
    .module-handle span {{ color:var(--muted); font-size:10px; font-family:Consolas, monospace; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .module-body {{ padding:12px; height:calc(100% - 42px); overflow:auto; }}
    .kpi-value {{ font-size:26px; font-weight:800; line-height:1.15; }}
    .kpi-sub {{ color:var(--muted); font-size:12px; margin-top:6px; }}
    .kpi-origin, .chart-sub {{ color:var(--muted); font-size:11px; margin-top:8px; }}
    .bar-list {{ display:flex; flex-direction:column; gap:8px; }}
    .bar-row {{ display:grid; grid-template-columns:120px 1fr 90px; gap:8px; align-items:center; font-size:12px; }}
    .bar-label {{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .bar-track {{ height:12px; background:#eef2f7; border-radius:4px; overflow:hidden; }}
    .bar-fill {{ height:100%; background:linear-gradient(90deg,#2563eb,#159947); border-radius:4px; }}
    .bar-value {{ text-align:right; color:var(--muted); font-variant-numeric:tabular-nums; }}
    .table-wrap {{ overflow:auto; height:100%; border:1px solid var(--line-soft); border-radius:6px; }}
    table {{ border-collapse:collapse; width:100%; min-width:1080px; font-size:12px; }}
    th {{ position:sticky; top:0; z-index:1; background:#f8fafc; color:#4b5563; text-align:left; padding:8px; border-bottom:1px solid var(--line); }}
    td {{ padding:7px 8px; border-bottom:1px solid var(--line-soft); vertical-align:top; }}
    td.num {{ text-align:right; font-variant-numeric:tabular-nums; }}
    .badge {{ display:inline-block; padding:2px 6px; border-radius:999px; background:#eef2ff; color:#1d4ed8; border:1px solid #c7d2fe; font-size:11px; }}
    .note-list {{ display:grid; grid-template-columns:110px 1fr; gap:6px 8px; font-size:12px; }}
    .note-list dt {{ color:var(--muted); }}
    .note-list dd {{ margin:0; font-weight:600; }}
    .small-note {{ color:var(--muted); font-size:12px; line-height:1.45; }}
    .edit-hint {{ display:none; margin-bottom:10px; border:1px solid #bfdbfe; background:#eff6ff; color:#1e3a8a; padding:8px 10px; border-radius:8px; font-size:12px; }}
    .edit .edit-hint {{ display:block; }}
    @media (max-width: 900px) {{
      .filterbar {{ grid-template-columns:1fr; }}
      .grid {{ display:block; }}
      .module {{ margin-bottom:10px; min-height:160px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>BI Suprimentos - POC modular da aba Impacto</h1>
      <div class="header-sub">Dados reais do Zoho - NFE - {html.escape(data['generated_at'])} - grid 16 colunas</div>
    </div>
    <div class="actions">
      <button id="editToggle" class="primary">Modo edicao</button>
      <button id="resetLayout">Reset layout</button>
    </div>
  </header>
  <main>
    <div class="filterbar">
      <div class="filter"><label>UF</label><select id="ufFilter"><option value="">Todas</option></select></div>
      <div class="filter"><label>Categoria</label><select id="catFilter"><option value="">Todas</option></select></div>
      <div class="filter"><label>Curva ID</label><select id="curvaFilter"><option value="">Todas</option></select></div>
      <div class="filter"><label>Leitura</label><select id="statusFilter"><option value="">Todas</option><option>Acima do menor</option><option>No menor</option><option>Abaixo do menor</option></select></div>
    </div>
    <div class="edit-hint">Modo edicao ativo: arraste os cards pelo cabecalho. As posicoes ficam salvas neste navegador.</div>
    <div id="grid" class="grid">
      {''.join(modules)}
    </div>
  </main>
  <script id="realData" type="application/json">{embedded_data}</script>
  <script>
{client_script}
  </script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera POC modular da aba Impacto com dados reais.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--data-json", default=str(DEFAULT_DATA_JSON))
    parser.add_argument("--env-file", default=str(BASE_DIR / "zoho.env"))
    parser.add_argument("--refresh-zoho", action="store_true")
    parser.add_argument("--interval", type=int, default=3)
    args = parser.parse_args()

    config = load_config(Path(args.config))
    if args.refresh_zoho:
        refresh_from_zoho(config, Path(args.env_file), interval=args.interval)

    data = prepare_data(config)

    data_path = Path(args.data_json)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_html(config, data), encoding="utf-8")

    print(f"Fonte: {config['source']['local_path']}")
    print(f"Linhas: {data['source']['rows']}")
    print(f"Impacto positivo: {brl(data['metrics']['impacto_cotacao_total'])}")
    print(f"HTML: {output_path}")
    print(f"JSON: {data_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
