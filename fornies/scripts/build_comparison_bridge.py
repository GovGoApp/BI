from __future__ import annotations

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PHASE_01_DIR = BASE_DIR / "output" / "fase_01_cadastro"
PHASE_02_DIR = BASE_DIR / "output" / "fase_02_reconciliacao"
PHASE_03_DIR = BASE_DIR / "output" / "fase_03_enriquecimento"

NORMALIZED_FILE = PHASE_01_DIR / "01_fornecedores_cadastro_normalizado.csv"
UNIFIED_FILE = PHASE_01_DIR / "02_fornecedores_cadastro_unificado.csv"
RECONCILED_FILE = PHASE_02_DIR / "01_fornecedores_reconciliados_movimento.csv"
ENRICHED_FILE = PHASE_03_DIR / "03_fornecedores_classificacao_fiscal_inicial_lote_completo.csv"
OUTPUT_FILE = PHASE_03_DIR / "05_mapa_comparacao_original_para_fases.csv"

COLUMNS = [
    "empresa_origem",
    "codigo_fornecedor",
    "chave_unificacao",
    "cnpj",
    "razao_social_original_normalizada",
    "nome_fantasia_original_normalizada",
    "situacao_cadastral_interna_original",
    "score_completude_fase_01",
    "faixa_completude_fase_01",
    "pendencias_essenciais_fase_01",
    "pendencias_complementares_fase_01",
    "divergencia_razao_social_fase_01",
    "divergencia_nome_fantasia_fase_01",
    "divergencia_status_interno_fase_01",
    "tem_movimento_nfe_fase_02",
    "nfe_linhas_fase_02",
    "nfe_valor_total_fase_02",
    "tem_curva_fase_02",
    "curva_classificacao_fase_02",
    "prioridade_saneamento_score_fase_02",
    "prioridade_saneamento_faixa_fase_02",
    "fila_enriquecimento_cnpj_fase_02",
    "situacao_cadastral_oficial_fase_03",
    "matriz_filial_fase_03",
    "porte_empresa_fase_03",
    "natureza_juridica_fase_03",
    "regime_indiciado_fase_03",
    "potencial_credito_2027_inicial_fase_03",
    "necessita_saneamento_cadastral_fase_03",
    "motivos_saneamento_cadastral_fase_03",
    "necessita_validacao_fiscal_fase_03",
    "motivos_validacao_fiscal_fase_03",
]


def load_by_key(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row[key_field]: row for row in csv.DictReader(handle)}


def main() -> None:
    unified_by_key = load_by_key(UNIFIED_FILE, "chave_unificacao")
    reconciled_by_key = load_by_key(RECONCILED_FILE, "chave_unificacao")
    enriched_by_key = load_by_key(ENRICHED_FILE, "chave_unificacao")

    rows_out: list[dict[str, str]] = []
    with NORMALIZED_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            key = row["chave_unificacao"]
            unified = unified_by_key.get(key, {})
            reconciled = reconciled_by_key.get(key, {})
            enriched = enriched_by_key.get(key, {})
            rows_out.append(
                {
                    "empresa_origem": row.get("empresa_origem", ""),
                    "codigo_fornecedor": row.get("codigo_fornecedor", ""),
                    "chave_unificacao": key,
                    "cnpj": row.get("cnpj", ""),
                    "razao_social_original_normalizada": row.get("razao_social", ""),
                    "nome_fantasia_original_normalizada": row.get("nome_fantasia", ""),
                    "situacao_cadastral_interna_original": row.get("situacao_cadastral_interna", ""),
                    "score_completude_fase_01": unified.get("score_completude", ""),
                    "faixa_completude_fase_01": unified.get("faixa_completude", ""),
                    "pendencias_essenciais_fase_01": unified.get("pendencias_essenciais", ""),
                    "pendencias_complementares_fase_01": unified.get("pendencias_complementares", ""),
                    "divergencia_razao_social_fase_01": unified.get("divergencia_razao_social", ""),
                    "divergencia_nome_fantasia_fase_01": unified.get("divergencia_nome_fantasia", ""),
                    "divergencia_status_interno_fase_01": unified.get("divergencia_status_interno", ""),
                    "tem_movimento_nfe_fase_02": reconciled.get("tem_movimento_nfe", ""),
                    "nfe_linhas_fase_02": reconciled.get("nfe_linhas", ""),
                    "nfe_valor_total_fase_02": reconciled.get("nfe_valor_total", ""),
                    "tem_curva_fase_02": reconciled.get("tem_curva", ""),
                    "curva_classificacao_fase_02": reconciled.get("curva_classificacao", ""),
                    "prioridade_saneamento_score_fase_02": reconciled.get("prioridade_saneamento_score", ""),
                    "prioridade_saneamento_faixa_fase_02": reconciled.get("prioridade_saneamento_faixa", ""),
                    "fila_enriquecimento_cnpj_fase_02": reconciled.get("fila_enriquecimento_cnpj", ""),
                    "situacao_cadastral_oficial_fase_03": enriched.get("situacao_cadastral_oficial", ""),
                    "matriz_filial_fase_03": enriched.get("matriz_filial", ""),
                    "porte_empresa_fase_03": enriched.get("porte_empresa", ""),
                    "natureza_juridica_fase_03": enriched.get("natureza_juridica", ""),
                    "regime_indiciado_fase_03": enriched.get("regime_indiciado", ""),
                    "potencial_credito_2027_inicial_fase_03": enriched.get("potencial_credito_2027_inicial", ""),
                    "necessita_saneamento_cadastral_fase_03": enriched.get("necessita_saneamento_cadastral", ""),
                    "motivos_saneamento_cadastral_fase_03": enriched.get("motivos_saneamento_cadastral", ""),
                    "necessita_validacao_fiscal_fase_03": enriched.get("necessita_validacao_fiscal", ""),
                    "motivos_validacao_fiscal_fase_03": enriched.get("motivos_validacao_fiscal", ""),
                }
            )

    with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Arquivo gerado: {OUTPUT_FILE}")
    print(f"Linhas: {len(rows_out)}")


if __name__ == "__main__":
    main()
