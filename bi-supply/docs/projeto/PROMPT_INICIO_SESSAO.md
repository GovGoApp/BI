# Prompt de Início de Sessão — BI de Suprimentos

Use este prompt ao iniciar uma nova conversa com a IA para que ela entenda
o projeto antes de fazer qualquer alteração.

---

## PROMPT (copie e cole no início da conversa)

```
Você está trabalhando no projeto **BI de Suprimentos** (bi-supply).
Antes de qualquer ação, leia os seguintes arquivos para entender
completamente o projeto:

1. `bi-supply/CLAUDE.md` — regras de comportamento, arquitetura do pipeline,
   convenções críticas, arquivos grandes que não devem ser lidos completos.

2. `bi-supply/README.md` — visão geral do projeto, o que o BI mostra,
   como rodar, estrutura de abas.

3. `bi-supply/DIARIO.md` — histórico técnico de tudo que foi feito,
   bugs encontrados, decisões de arquitetura. Leia especialmente as
   entradas mais recentes para entender o estado atual.

4. `bi-supply/docs/projeto/BRIEFING.md` — contexto de negócio.

5. `bi-supply/docs/dados/ANALISE_DADOS_REAIS.md` — schema das 18 fontes
   de dados do Zoho Analytics, tipos de campos, filtros importantes.

6. `bi-supply/docs/zoho/MAPA_PAINEIS.md` — painéis Zoho existentes,
   KPIs identificados, Design System tokens e componentes.

7. Estrutura de diretórios (sem ler arquivos grandes):
   - `bi-supply/pipeline/` — extract.py, transform.py,
     generate_indexes.py, build.py
   - `bi-supply/dashboard/` — charts.json (configs elementos),
     chart_types.json (templates), tabs/*.layout.json (posições)
   - `bi-supply/nlsql/` — server.py, adapter.py, prompts/
   - `bi-supply/data/processed/` — CSVs e JSONs gerados
   - `bi-supply/docs/design/` — ESPECIFICACAO_ABAS.md,
     ELEMENTOS_BI.md, COBERTURA_ABAS.md

Após ler, responda:
1. Um resumo do projeto em 5 linhas
2. O estado atual (o que funciona, o que está pendente)
3. Os 3-5 pontos mais importantes que faltam para o projeto estar completo
4. Pergunte ao usuário o que deseja fazer nesta sessão
```

---

## Contexto rápido para a IA (complementar ao prompt acima)

**Pipeline completo:**
```
extract.py → transform.py → generate_indexes.py → build.py → dist/index.html
```

**Servidor NL-SQL** (porta 5001):
```
python nlsql/server.py
```

**BAT de atualização** (área de trabalho):
```
Atualizar BI Suprimentos.bat
```

**Arquivos NUNCA ler completos** (usar Grep/offset):
- `pipeline/build.py` (3000+ linhas)
- `pipeline/transform.py` (800+ linhas)
- `dist/index.html` (3.3 MB)
- `data/raw/*.csv`

**Regras críticas:**
- Commits atômicos, DIARIO.md append ao final a cada sessão
- Nunca spawnar subagentes sem solicitação explícita
- Nunca abrir browser (`start dist\index.html`)
- `generate_indexes.py` SEMPRE após `transform.py`
- `PMP_0` SEMPRE VAZIO — usar `PMP_1` como valor atual
- `STATUSPAG` CP: 'Em Aberto' ou 'Baixado' (nunca 'ABERTO'/'PAGO')

---

## Estado atual do projeto (atualizado em 2026-06-09)

### O que funciona completamente
- Pipeline completo: extract → transform → generate_indexes → build
- 13 abas ativas com dados reais do Zoho Analytics
- NL-SQL (Assistente v3): gera SQL, executa no Zoho, mostra resultado
- Aba Relatório: chat, histórico, elementos salvos, exportação CSV
- Editor de layout: drag&drop, persistência em disco via server.py
- Sistema de formatação: FIELD_FORMATS + col_fmts + fallback d2
- Config centralizada de visualizações: dashboard/chart_types.json + charts.json

### Abas PENDENTES (sem implementação)
- **Estoque** — requer workspace "Apuração de Resultados" (diferente do SUPRIMENTOS)
- **Fiscal** — análise de regime tributário CBS/IBS 2027

### Componentes faltantes (54 itens em COBERTURA_ABAS.md)
Principais gaps por aba:
- **Fornecedor**: ranking total, distribuição por categoria, impacto × fornecedor
- **Cotações**: contagem por ABC/CAT/UF, consulta de preços completa
- **Inflação**: gráfico temporal por CAT, painel nacional, painel por UF
- **Adiantamentos**: gráfico temporal, por UF, por CAT, por fornecedor
- **Financeiro**: CP_STATUS-TOTAL, saldo de dívida, CP semanal
- **Produtos**: produtos por CAT/ID/UF, padronização, PMP por ABC

### Funcionalidades de interface pendentes
- Formatação numérica no BI (tabelas em abas) — parcialmente resolvida
- Gráfico de barras GB melhorado (resolvido na última sessão)
- Gráfico GL multi-série (ainda sem suporte)
- Visualização Ranking (HL) com formato incorreto de % vs R$

### Próximas prioridades sugeridas
1. Corrigir visualização Ranking (HL) — mostra "R$ -11" em vez de "-10,6%"
2. Implementar GL multi-série (inflação por CAT ao longo do tempo)
3. Preencher gaps de Fornecedor 360 (ranking, categorias, impacto)
4. Completar aba Adiantamentos (gráficos temporais)
5. Melhorar aba Cotações (contagem por ABC, consulta de preços)
