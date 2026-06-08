# BI de Suprimentos — Contexto para Claude Code

## Projeto

Dashboard HTML auto-contido gerado a partir do Zoho Analytics.
Pipeline: `extract.py → transform.py → generate_indexes.py → build.py → dist/index.html`
**CRÍTICO:** `generate_indexes.py` SEMPRE após `transform.py`.

## Arquivos grandes — ler com Grep/offset, nunca ler completo

- `pipeline/build.py` — 3000+ linhas. Usar Grep para localizar seções.
- `pipeline/transform.py` — 800+ linhas. Usar Grep por função.
- `dist/index.html` — 3.3 MB. Nunca ler.
- `data/raw/*.csv` — grandes. Usar head/tail ou python para amostras.

## Arquivos de referência rápida

- `docs/dados/ANALISE_DADOS_REAIS.md` — tipos e filtros de cada tabela Zoho
- `docs/zoho/MAPA_PAINEIS.md` — painéis Zoho + Design System tokens
- `docs/design/ELEMENTOS_BI.md` — tipos de elemento (KPI, GL, HL, MX, etc.)
- `nlsql/prompts/bi_suprimentos_sql_v3.md` — prompt NL-SQL completo

## Arquitetura do build.py (seções-chave)

Buscar por estas strings para localizar cada bloco:
- `RELATORIO_CSS` / `RELATORIO_JS` — aba Relatório
- `EDITOR_CSS` / `EDITOR_JS` — editor visual
- `FILTER_CSS` / `FILTER_JS` — filtros
- `RENDERER_JS` — renderização de elementos
- `ELEMENTS_RUNTIME_JS` — Biblioteca de elementos no editor
- `GRID_CSS` — grid layout
- `def build_dashboard` — função principal de build

## Convenções críticas

- `window._BI_DATA[variavel_js]` — registry de dados dos elementos
- `_ABAS_SKIP = new Set(['categorias','estoque'])` — preservam implementação v4
- KPIs: `row_span=2`, posicionamento sequencial no topo (8 por linha)
- Empresas: RC=Ideal, ME=Melhor, SU/PV=Supera
- Curvas ABC: AAA>AA>A>B>BB>C>CC>CCC
- `MESANO` = texto formato 'YYYY/MM'
- `STATUSPAG` CP: 'Em Aberto' ou 'Baixado' (nunca 'ABERTO'/'PAGO')
- `STATUS_CONCILIACAO` AD: 'CONCILIADO' ou 'ADIANTAMENTO ?' (com ?)
- `PMP_0` SEMPRE VAZIO — usar PMP_1 como valor atual
- `TE.ID` em CURVA ID: coluna com ponto, sempre aspas duplas

## NL-SQL

- Servidor: `python nlsql/server.py` (porta 5001)
- Versão ativa: `nlsql/active_version.txt` (default: v2)
- Endpoints principais: POST /run, POST /classify, GET /elements, POST /elements
- Elementos salvos: `nlsql/elements.json`

## generate_indexes.py — como adicionar/modificar elementos

Cada aba tem um `IDX_XX = {...}` com array `"elementos"`.
Função `e()` cria elemento: `e(id, variavel_js, tipo, titulo, dados_file, config, col=, col_span=, row=, row_span=)`
KPI config: `{"chave": "nome_campo", "fmt": "brl|pct|num", "state": "ok|warn|alert", "delta_chave": "...", "delta_ctx": "..."}`

## transform.py — como adicionar KPIs

KPIs ficam em `{aba}_k00_kpis.json`. Para adicionar:
1. Calcular o valor na função `aba_XXX()`
2. Adicionar à dict `kpis = {..., "novo_campo": valor}`
3. Atualizar config em `generate_indexes.py`

## Regras de comportamento (economizar tokens)

- Nunca spawnar subagentes (Agent tool) sem solicitação explícita
- Ler arquivos grandes com Grep + Read(offset/limit), não completo
- Commits atômicos: uma mudança = um commit
- DIARIO.md: append no final, nunca no meio
- Não pedir confirmação antes de executar (usuário autorizou commits automáticos)
- Não abrir browser (nunca `start dist\index.html`)
- Sempre listar arquivos alterados com links ao final de cada entrega
- **README.md**: atualizar quando houver mudança estrutural (nova aba, nova feature, novo endpoint)
- **DIARIO.md**: append no FINAL a cada sessão de trabalho com data, commits e detalhes técnicos
