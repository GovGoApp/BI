"""Catálogo das fontes do workspace SUPRIMENTOS.

Serve como camada de descoberta para o módulo NL-SQL: lista as 18 fontes
confirmadas (allowlist), expõe colunas/tipos e responde buscas por termos.

Nunca chama o Zoho em tempo real — lê o perfil de data/raw/suprimentos_profile.json
gerado pelo zoho/inventario.py.

Funções principais:
    list_tables()             → todas as fontes com domínio e contagem de colunas
    search_schema(query)      → fontes relevantes para uma pergunta
    describe_table(name)      → colunas, tipos e exemplos de uma fonte
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "data" / "raw" / "suprimentos_profile.json"


# ---------------------------------------------------------------------------
# Allowlist das 18 fontes confirmadas
# ---------------------------------------------------------------------------
# Cada entrada: nome exato no Zoho → descrição do domínio de negócio

GOLDEN: dict[str, str] = {
    "NFE": (
        "fato principal de compras: notas fiscais consolidadas de todas as empresas. "
        "Tem curvas ABC de fornecedor produto e ID, PMP histórico, impacto de cotação "
        "(IMP_COT), inflação (INF), filial, UF, categoria CAT1-CAT5."
    ),
    "NF COM ITENS - CONSOLIDADO": (
        "notas fiscais com itens: detalhe de entrada por nota, chave, número, datas. "
        "Mais granular que NFE — preserva data de emissão e entrada por nota."
    ),
    "COT": (
        "cotações de preços: todas as cotações por produto, fornecedor, mês e UF. "
        "Inclui curvas ABC de produto, fornecedor e ID embutidas."
    ),
    "COT_MIN_FORN": (
        "menor cotação por fornecedor: para cada produto e mês, qual fornecedor "
        "ofereceu o menor preço (PRECOUNIT_COT) e sua curva."
    ),
    "NUM_COT": (
        "contagem de cotações: quantas cotações existem por produto, ID e mês. "
        "Usado para medir cobertura e concorrência no processo de compra."
    ),
    "CURVA ABC FORN - TOTAL": (
        "curva ABC de fornecedores: ranking por volume total comprado (TOT_FORN), "
        "percentual, acumulado e classificação AAA-CCC. Inclui razão social."
    ),
    "CURVA ID - TODAS": (
        "curva ABC de IDs: ranking de IDs (combinação empresa+UF+produto) "
        "por volume comprado, percentual e classificação AAA-CCC."
    ),
    "CURVA PROD - TODAS": (
        "curva ABC de produtos: ranking de produtos por volume total comprado, "
        "percentual, acumulado e classificação. Inclui nome oficial do produto."
    ),
    "INFLAÇÃO": (
        "inflação e variação de preço médio ponderado (PMP) ao longo do tempo. "
        "Série mensal por produto, ID, categoria e UF. "
        "Campos INF_* medem variação percentual e em reais do PMP."
    ),
    "PMP_ID_INF_12": (
        "preço médio ponderado por ID com série de 12 meses: PMP_0 a PMP_12, "
        "variação de inflação por período. Nível mais detalhado de análise de preço."
    ),
    "PMP_PROD_INF_12": (
        "preço médio ponderado por produto com série de 12 meses: mesma estrutura "
        "que PMP_ID_INF_12 mas agregada por produto padronizado."
    ),
    "CP": (
        "contas a pagar: todas as contas com 49 colunas. Datas de emissão, "
        "vencimento original, vencimento atual e baixa. Status, faixa de dias, "
        "valor original, atualizado e baixado. Por fornecedor e filial."
    ),
    "CP_MOV": (
        "movimentos de contas a pagar: entradas e saídas de CP por semana. "
        "Útil para analisar fluxo de pagamentos e variação de saldo."
    ),
    "CP_SEMANA": (
        "saldo semanal de contas a pagar: saldo de dívida por semana do ano, "
        "com datas de início e fim da semana e variação líquida."
    ),
    "CP_SALDO_2026_v2": (
        "saldo 2026 de contas a pagar por fornecedor e semana: versão agregada "
        "sem separação por tipo de conta. Mais limpa para análise de saldo total."
    ),
    "AD_v3": (
        "adiantamentos versão 3: a mais completa. Tem UF, filial, categoria (CAT1, CAT2), "
        "fornecedor, produto, valor final e STATUS_CONCILIACAO (CONCILIADO / PENDENTE)."
    ),
    "FILIAIS_SUPPLY": (
        "dimensão de filiais: empresa (RC/ME/SU), filial, nome, UF, negócio "
        "(CD/COZINHA/ESCOLA/HOSPITAL/MERENDA/PRESIDIO/MATRIZ), região, sigla."
    ),
    "TAB_PROD": (
        "tabela de referência de produtos: código padronizado e nome oficial. "
        "Usado para padronizar nomes entre diferentes fontes."
    ),
}


# ---------------------------------------------------------------------------
# Carregamento do perfil
# ---------------------------------------------------------------------------

def _load_profile() -> dict[str, Any]:
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"Perfil não encontrado em {PROFILE_PATH}. "
            "Execute: python zoho/inventario.py --env-file zoho/zoho.env"
        )
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def _normalize(text: str) -> str:
    """Remove acentos e converte para minúsculas para comparação."""
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower())
        if unicodedata.category(c) != "Mn"
    )


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def list_tables() -> list[dict[str, Any]]:
    """Retorna todas as 18 fontes com domínio, contagem de colunas e view_id."""
    profile = _load_profile()
    result = []
    for name, description in GOLDEN.items():
        p = profile.get(name)
        columns = p.get("columns", []) if p else []
        result.append({
            "table": name,
            "description": description,
            "column_count": len(columns),
            "available": bool(columns),
        })
    return result


def describe_table(name: str) -> dict[str, Any]:
    """Retorna colunas, tipos e exemplos de uma fonte específica.

    Args:
        name: nome exato da fonte (ex: "NFE", "COT_MIN_FORN")

    Returns:
        {
          "table": str,
          "description": str,
          "columns": [{"name": str, "type": str, "sample": str}],
          "column_count": int,
        }

    Raises:
        KeyError: se o nome não estiver na allowlist
        FileNotFoundError: se o perfil não existir
    """
    if name not in GOLDEN:
        allowed = ", ".join(sorted(GOLDEN.keys()))
        raise KeyError(f"'{name}' não está na allowlist. Fontes disponíveis: {allowed}")

    profile = _load_profile()
    p = profile.get(name)
    columns = p.get("columns", []) if p else []

    return {
        "table": name,
        "description": GOLDEN[name],
        "columns": columns,
        "column_count": len(columns),
    }


def search_schema(query: str, top_n: int = 5) -> list[dict[str, Any]]:
    """Busca fontes relevantes para uma pergunta em linguagem natural.

    Pontua cada fonte com base em correspondência de termos contra:
      - nome da fonte
      - descrição do domínio
      - nomes das colunas

    Args:
        query: termos de busca (ex: "cotação menor preço fornecedor")
        top_n: quantas fontes retornar (padrão 5)

    Returns:
        Lista de {table, description, score, relevant_columns} ordenada por score.
    """
    terms = _normalize(query).split()
    if not terms:
        return []

    profile = _load_profile()
    scores: list[dict[str, Any]] = []

    for name, description in GOLDEN.items():
        p = profile.get(name)
        columns = p.get("columns", []) if p else []

        norm_name = _normalize(name)
        norm_desc = _normalize(description)
        col_names = [_normalize(c["name"]) for c in columns]

        score = 0
        relevant_cols: list[str] = []

        for term in terms:
            # nome da fonte (peso alto)
            if term in norm_name:
                score += 3
            # descrição do domínio (peso médio)
            if term in norm_desc:
                score += 2
            # colunas (peso unitário por coluna que bate)
            for col, orig_col in zip(col_names, columns):
                if term in col:
                    score += 1
                    orig_name = orig_col["name"]
                    if orig_name not in relevant_cols:
                        relevant_cols.append(orig_name)

        if score > 0:
            scores.append({
                "table": name,
                "description": description,
                "score": score,
                "relevant_columns": relevant_cols[:10],
                "column_count": len(columns),
            })

    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:top_n]


# ---------------------------------------------------------------------------
# CLI de diagnóstico
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print(f"=== Catálogo SUPRIMENTOS — {len(GOLDEN)} fontes ===\n")

    tables = list_tables()
    ok = sum(1 for t in tables if t["available"])
    print(f"Fontes com perfil OK: {ok}/{len(tables)}")
    print()

    for t in tables:
        status = "OK" if t["available"] else "SEM PERFIL"
        print(f"  [{status:10}] {t['table']} ({t['column_count']} cols)")

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n=== Busca: '{query}' ===\n")
        results = search_schema(query)
        if not results:
            print("Nenhum resultado.")
        for r in results:
            print(f"  score={r['score']:3d}  {r['table']}")
            if r["relevant_columns"]:
                print(f"           cols: {', '.join(r['relevant_columns'][:6])}")
