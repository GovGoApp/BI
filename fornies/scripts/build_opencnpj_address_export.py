from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
PHASE_03_DIR = BASE_DIR / "output" / "fase_03_enriquecimento"
INPUT_FILE = PHASE_03_DIR / "01_fornecedores_opencnpj_enriquecidos_lote_completo.csv"
CACHE_DIR = PHASE_03_DIR / "99_cache_opencnpj"
OUTPUT_FILE = PHASE_03_DIR / "06_fornecedores_opencnpj_enriquecidos_lote_completo_com_endereco.csv"

ADDRESS_COLUMNS = [
    "endereco_tipo_logradouro",
    "endereco_logradouro",
    "endereco_numero",
    "endereco_complemento",
    "endereco_bairro",
    "endereco_cep",
    "endereco_municipio",
    "endereco_uf",
    "endereco_completo",
    "contatos_qsa",
]


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def cache_file(cnpj: str) -> Path:
    return CACHE_DIR / f"{cnpj}.json"


def load_payload(cnpj: str) -> dict[str, Any]:
    path = cache_file(cnpj)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def collect_phones(payload: dict[str, Any]) -> str:
    out: list[str] = []
    for item in payload.get("telefones") or []:
        if not isinstance(item, dict):
            continue
        ddd = normalize_text(item.get("ddd"))
        numero = normalize_text(item.get("numero"))
        if ddd or numero:
            label = f"({ddd}) {numero}" if ddd else numero
            if item.get("is_fax"):
                label = f"{label} fax"
            out.append(label)
    return ";".join(out)


def collect_qsa(payload: dict[str, Any]) -> str:
    out: list[str] = []
    for item in payload.get("QSA") or []:
        if not isinstance(item, dict):
            continue
        name = normalize_text(item.get("nome_socio"))
        role = normalize_text(item.get("qualificacao_socio"))
        if name and role:
            out.append(f"{name} ({role})")
        elif name:
            out.append(name)
    return ";".join(out)


def build_address(payload: dict[str, Any]) -> dict[str, str]:
    tipo = normalize_text(payload.get("tipo_logradouro"))
    logradouro = normalize_text(payload.get("logradouro"))
    numero = normalize_text(payload.get("numero"))
    complemento = normalize_text(payload.get("complemento"))
    bairro = normalize_text(payload.get("bairro"))
    cep = normalize_text(payload.get("cep"))
    municipio = normalize_text(payload.get("municipio"))
    uf = normalize_text(payload.get("uf"))

    first_part = " ".join(part for part in [tipo, logradouro] if part)
    if numero:
        first_part = f"{first_part}, {numero}" if first_part else numero
    pieces = [first_part, complemento, bairro, municipio, uf, cep]
    endereco_completo = " - ".join(part for part in pieces if part)

    return {
        "endereco_tipo_logradouro": tipo,
        "endereco_logradouro": logradouro,
        "endereco_numero": numero,
        "endereco_complemento": complemento,
        "endereco_bairro": bairro,
        "endereco_cep": cep,
        "endereco_municipio": municipio,
        "endereco_uf": uf,
        "endereco_completo": endereco_completo,
        "contatos_qsa": collect_qsa(payload),
    }


def main() -> None:
    with INPUT_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        input_columns = list(reader.fieldnames or [])
        rows = list(reader)

    output_columns = input_columns[:]
    for column in ADDRESS_COLUMNS:
        if column not in output_columns:
            output_columns.append(column)

    for row in rows:
        payload = load_payload(normalize_text(row.get("cnpj")))
        address = build_address(payload)
        row.update(address)
        if payload:
            row["uf"] = row.get("uf") or address["endereco_uf"]
            row["municipio"] = row.get("municipio") or address["endereco_municipio"]
            row["email_oficial"] = row.get("email_oficial") or normalize_text(payload.get("email")).lower()
            row["telefones_oficiais"] = row.get("telefones_oficiais") or collect_phones(payload)

    with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Arquivo gerado: {OUTPUT_FILE}")
    print(f"Registros: {len(rows)}")


if __name__ == "__main__":
    main()
