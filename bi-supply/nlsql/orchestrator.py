"""Orquestrador NL-SQL usando Claude API com tool use.

Fluxo:
  1. Usuário faz pergunta em português
  2. Claude chama search_schema para descobrir tabelas relevantes
  3. Claude chama describe_table para ver colunas e exemplos
  4. Claude gera SQL e chama run_readonly_query
  5. Resultado tabular é retornado

Requer: ANTHROPIC_API_KEY no ambiente ou em nlsql/.env
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
from nlsql.guard import SQLGuardError
from zoho.catalog import search_schema, describe_table, list_tables

# ── Carrega .env da pasta nlsql se existir ───────────────────────────────────
_NLSQL_ENV = ROOT / "nlsql" / ".env"
if _NLSQL_ENV.exists():
    for line in _NLSQL_ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

SYSTEM = """Você é um assistente de análise de dados de suprimentos.

Seu objetivo é responder perguntas do usuário consultando o banco de dados Zoho Analytics
do workspace SUPRIMENTOS, que contém dados de compras, fornecedores, cotações,
preços e contas a pagar de uma empresa de food service.

Conceitos importantes do domínio:
- ID: chave analítica que combina empresa + UF + produto (ex: RCPEI201203000)
- IMP_COT: impacto de cotação — (preço pago − menor cotação) × quantidade. Positivo = pagamos mais que o mínimo.
- PMP: Preço Médio Ponderado histórico
- INF: variação do PMP ao longo do tempo (inflação do produto)
- Curva ABC: AAA/AA/A são os mais relevantes em volume; CCC são a cauda longa
- NMEMP: empresa (RC = Ideal/RC, ME = Melhor, SU = Supera)
- CAT1 a CAT5: hierarquia de categorias (I=Insumos, D=Despesas, A=Ativos)

Fluxo obrigatório:
1. Use search_schema para encontrar tabelas relevantes
2. Use describe_table para confirmar colunas e exemplos
3. Se ambíguo, peça esclarecimento
4. Gere uma única query SELECT com aliases claros
5. Chame run_readonly_query
6. Resuma o resultado de forma objetiva

Regras:
- Nunca invente tabelas ou colunas não confirmadas
- Sempre use LIMIT (máximo 500)
- Use aspas duplas nos nomes de tabelas e colunas do Zoho
- Prefira somas e agrupamentos sobre listagens brutas
- Se a pergunta puder ter mais de uma interpretação, peça esclarecimento
"""

TOOLS = [
    {
        "name": "search_schema",
        "description": (
            "Busca tabelas e colunas relevantes no catálogo do workspace SUPRIMENTOS. "
            "Use antes de escrever SQL quando as tabelas relevantes não são claras."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Termos de busca relacionados à pergunta. Ex: cotacao preco fornecedor",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "describe_table",
        "description": (
            "Retorna colunas, tipos e exemplos de valores de uma tabela específica. "
            "Use após search_schema para confirmar quais colunas usar."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Nome exato da tabela no catálogo (ex: NFE, COT, CP)",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "run_readonly_query",
        "description": (
            "Valida e executa uma query SELECT no Zoho Analytics. "
            "Use somente SELECT ou WITH ... SELECT. Nunca DDL ou DML. "
            "Inclua LIMIT."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "Query SQL somente leitura no dialeto Zoho Analytics.",
                }
            },
            "required": ["sql"],
        },
    },
]


def _call_tool(name: str, args: dict) -> str:
    """Executa uma tool call e retorna o resultado como JSON string."""
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
        except KeyError as e:
            return json.dumps({"error": str(e)})

    if name == "run_readonly_query":
        result = run_query(args["sql"])
        # Envia ao modelo só uma amostra pequena para não desperdiçar tokens
        sample = result.copy()
        if result.get("rows"):
            sample["rows"] = result["rows"][:5]
            sample["note"] = f"Mostrando 5 de {result['row_count']} linhas para o modelo. Resultado completo disponível."
        return json.dumps(sample, ensure_ascii=False, default=str)

    return json.dumps({"error": f"Tool desconhecida: {name}"})


def ask(question: str, verbose: bool = False) -> dict[str, Any]:
    """Faz uma pergunta em linguagem natural e retorna o resultado.

    Returns:
        {
          "answer": str,           # resposta em texto
          "table": dict | None,    # resultado tabular completo (não truncado)
          "sql_used": str | None,  # SQL executado
          "tool_calls": int,       # quantas tool calls foram feitas
        }
    """
    try:
        import anthropic
    except ImportError:
        return {
            "answer": "Dependência 'anthropic' não instalada. Execute: pip install anthropic",
            "table": None, "sql_used": None, "tool_calls": 0,
        }

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {
            "answer": "ANTHROPIC_API_KEY não configurada. Adicione em nlsql/.env ou no ambiente.",
            "table": None, "sql_used": None, "tool_calls": 0,
        }

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": "user", "content": question}]
    last_table: dict | None = None
    last_sql: str | None = None
    tool_call_count = 0

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages,
        )

        if verbose:
            print(f"  [stop_reason: {response.stop_reason}]", flush=True)

        # Adicionar resposta do assistente ao histórico
        messages.append({"role": "assistant", "content": response.content})

        # Se parou sem tool_use, chegamos na resposta final
        if response.stop_reason == "end_turn":
            answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    answer += block.text
            return {
                "answer": answer,
                "table": last_table,
                "sql_used": last_sql,
                "tool_calls": tool_call_count,
            }

        # Processar tool calls
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                tool_call_count += 1
                tool_name = block.name
                tool_args = block.input

                if verbose:
                    print(f"  [tool: {tool_name}({list(tool_args.keys())})]", flush=True)

                result_str = _call_tool(tool_name, tool_args)

                # Capturar resultado da query para retornar ao caller
                if tool_name == "run_readonly_query":
                    try:
                        result_data = json.loads(result_str)
                        if result_data.get("ok"):
                            last_sql = result_data.get("sql_used")
                            # Buscar resultado completo para o caller
                            full_result = run_query(tool_args["sql"])
                            if full_result.get("ok"):
                                last_table = full_result
                    except Exception:
                        pass

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

            messages.append({"role": "user", "content": tool_results})
            continue

        # Stop reason inesperado
        break

    return {"answer": "Resposta não obtida.", "table": None, "sql_used": None, "tool_calls": tool_call_count}
