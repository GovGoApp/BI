"""Orquestrador NL-SQL usando OpenAI Responses API com function calling.

Fluxo:
  1. Usuário faz pergunta em português
  2. Modelo chama search_schema para descobrir tabelas relevantes
  3. Modelo chama describe_table para ver colunas e exemplos
  4. Modelo gera SQL e chama run_readonly_query
  5. Resultado tabular é retornado

Requer: OPENAI_API_KEY e OPENAI_MODEL em nlsql/.env
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nlsql.adapter import run_query
from zoho.catalog import search_schema, describe_table

# ── Carregar nlsql/.env ──────────────────────────────────────────────────────
_NLSQL_ENV = ROOT / "nlsql" / ".env"
if _NLSQL_ENV.exists():
    for line in _NLSQL_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

INSTRUCTIONS = """Você é um assistente de análise de dados de suprimentos.

Seu objetivo é responder perguntas consultando o Zoho Analytics (workspace SUPRIMENTOS),
que contém dados de compras, fornecedores, cotações, preços e contas a pagar
de uma empresa de food service (hospitais, escolas, presídios, restaurantes).

Conceitos do domínio:
- ID: chave analítica empresa+UF+produto (ex: RCPEI201203000)
- IMP_COT: (preço pago − menor cotação) × quantidade. Positivo = oportunidade de economia.
- PMP: Preço Médio Ponderado histórico
- INF: variação do PMP no tempo (inflação do produto)
- Curva ABC: AAA/AA/A = mais relevantes por volume; CCC = cauda longa
- NMEMP: RC (Ideal/RC) | ME (Melhor) | SU (Supera)
- CAT1..CAT5: hierarquia de categorias (I=Insumos, D=Despesas, A=Ativos)
- TOTAL: valor total comprado em reais

Fluxo obrigatório:
1. Chame search_schema para encontrar tabelas relevantes
2. Chame describe_table para confirmar colunas e exemplos
3. Se ambíguo, peça esclarecimento antes de executar
4. Gere uma única query SELECT com aliases claros em português quando possível
5. Chame run_readonly_query
6. Resuma o resultado de forma direta e objetiva

Regras SQL (dialeto Zoho Analytics):
- Nomes de tabelas e colunas entre aspas duplas: "NFE", "TOTAL"
- Sempre inclua LIMIT
- Use SUM(), COUNT(), AVG() para agregações
- Prefira agregações sobre listagens brutas
- Nunca invente tabelas ou colunas não confirmadas pelas ferramentas
"""

TOOLS = [
    {
        "type": "function",
        "name": "search_schema",
        "description": (
            "Busca tabelas e colunas relevantes no catálogo do workspace SUPRIMENTOS. "
            "Use antes de escrever SQL quando as tabelas relevantes não são claras."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termos relacionados à pergunta. Ex: cotacao preco fornecedor",
                }
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "describe_table",
        "description": (
            "Retorna colunas, tipos e exemplos de valores de uma tabela específica. "
            "Use após search_schema para confirmar quais colunas usar no SQL."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nome exato da tabela (ex: NFE, COT, CP, AD_v3)",
                }
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "run_readonly_query",
        "description": (
            "Valida e executa uma query SELECT no Zoho Analytics. "
            "Use somente SELECT ou WITH ... SELECT. Inclua LIMIT. "
            "Nomes de tabelas e colunas entre aspas duplas."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": 'Query SQL somente leitura. Ex: SELECT "NMEMP", sum("TOTAL") FROM "NFE" GROUP BY "NMEMP" LIMIT 10',
                }
            },
            "required": ["sql"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def _call_tool(name: str, args: dict) -> str:
    """Executa uma tool call e retorna resultado como JSON string."""
    if name == "search_schema":
        results = search_schema(args["query"], top_n=5)
        return json.dumps(
            [{"table": r["table"], "description": r["description"],
              "relevant_columns": r["relevant_columns"]} for r in results],
            ensure_ascii=False,
        )

    if name == "describe_table":
        try:
            info = describe_table(args["name"])
            return json.dumps(
                {"table": info["table"], "description": info["description"],
                 "columns": info["columns"]},
                ensure_ascii=False,
            )
        except KeyError as exc:
            return json.dumps({"error": str(exc)})

    if name == "run_readonly_query":
        result = run_query(args["sql"])
        # Envia amostra pequena ao modelo para não desperdiçar tokens
        sample = {k: v for k, v in result.items() if k != "rows"}
        if result.get("rows"):
            sample["rows"] = result["rows"][:5]
            sample["note"] = f"Amostra de 5/{result['row_count']} linhas enviada ao modelo."
        return json.dumps(sample, ensure_ascii=False, default=str)

    return json.dumps({"error": f"Tool desconhecida: {name}"})


def ask(question: str, verbose: bool = False) -> dict[str, Any]:
    """Faz uma pergunta em linguagem natural e retorna resultado.

    Returns:
        {
          "answer": str,
          "table": dict | None,
          "sql_used": str | None,
          "tool_calls": int,
        }
    """
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "answer": "Dependência 'openai' não instalada. Execute: pip install openai",
            "table": None, "sql_used": None, "tool_calls": 0,
        }

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return {
            "answer": "OPENAI_API_KEY não configurada. Adicione em nlsql/.env",
            "table": None, "sql_used": None, "tool_calls": 0,
        }

    client = OpenAI(api_key=api_key)
    last_table: dict | None = None
    last_sql: str | None = None
    tool_call_count = 0

    # Formato Chat Completions — compatível com openai >= 1.0
    messages: list = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": question},
    ]

    # Converter tools para formato Chat Completions
    chat_tools = [
        {"type": "function", "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"],
        }}
        for t in TOOLS
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=chat_tools,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        messages.append(msg)

        if verbose and msg.tool_calls:
            print(f"  [tools: {[tc.function.name for tc in msg.tool_calls]}]", flush=True)

        # Sem tool calls = resposta final
        if not msg.tool_calls:
            return {
                "answer": msg.content or "",
                "table": last_table,
                "sql_used": last_sql,
                "tool_calls": tool_call_count,
            }

        # Processar cada tool call
        for tc in msg.tool_calls:
            tool_call_count += 1
            args = json.loads(tc.function.arguments)
            result_str = _call_tool(tc.function.name, args)

            # Capturar resultado completo da query para retornar ao caller
            if tc.function.name == "run_readonly_query":
                try:
                    result_data = json.loads(result_str)
                    if result_data.get("ok"):
                        last_sql = result_data.get("sql_used")
                        full = run_query(args["sql"])
                        if full.get("ok"):
                            last_table = full
                except Exception:
                    pass

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_str,
            })
