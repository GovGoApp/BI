# STATUS — Migração Pipeline → NL-SQL

Atualizado: 2026-06-09 15:26 | Meta: 139 elementos

## Legenda
- ✅ Concluído  ⏳ Em andamento  ❌ Falhou  — Pendente

| Aba | Elemento | Tipo | Fonte Zoho | SQL | Exec | Delta | Config | Aprovado |
|-----|----------|------|-----------|-----|------|-------|--------|---------|
| Resumo | Total Comprado | KPI | NFE | — | — | — | — | — |
| Resumo | Fornecedores Ativos | KPI | NFE | — | — | — | — | — |
| Resumo | Produtos / IDs | KPI | NFE | — | — | — | — | — |
| Resumo | Impacto R$ | KPI | NFE | — | — | — | — | — |
| Resumo | Oportunidade R$ | KPI | NFE | — | — | — | — | — |
| Resumo | Compras com Cotação | KPI | NFE | — | — | — | — | — |
| Resumo | AD Pendente | KPI | AD_v3 | — | — | — | — | — |
| Resumo | CP em Aberto | KPI | CP | — | — | — | — | — |
| Resumo | Tendência Mensal de Compras | GL | NFE | ✅ | ✅ | — | — | — |
| Resumo | Compras por Negócio | HL | NFE | — | — | — | — | — |
| Resumo | Top Categorias | T | NFE | — | — | — | — | — |
| Resumo | Top Fornecedores | T | NFE | — | — | — | — | — |
| Resumo | Alertas Executivos | AL |  | — | — | — | — | — |
| Resumo | SUP por GEO · N e NE | HL | NFE | ✅ | ✅ | — | — | — |
| Resumo | SUP por GEO · S e SE | HL | NFE | ✅ | ✅ | — | — | — |
| Resumo | RESUMO_FILIAL | T | NFE | — | — | — | — | — |
| Resumo | Categoria × UF | MX | NFE | — | — | — | — | — |
| Oportunidades | Oportunidade R$ | KPI | NFE | — | — | — | — | — |
| Oportunidades | IDs AAA/A Sem Cot. | KPI | NFE | — | — | — | — | — |
| Oportunidades | IDs Acima do Mín. | KPI | NFE | — | — | — | — | — |
| Oportunidades | % Acima do Mínimo | KPI | NFE | — | — | — | — | — |
| Oportunidades | ≤1 Cotação (Risco) | KPI | NUM_COT | — | — | — | — | — |
| Oportunidades | Matriz Prioridade | MX |  | — | — | — | — | — |
| Oportunidades | Por Tipo de Oportunidade | HL | NFE | — | — | — | — | — |
| Oportunidades | Por UF | HL | NFE | — | — | — | — | — |
| Oportunidades | Tabela de Oportunidades | TE | NFE | — | — | — | — | — |
| Oportunidades | Oportunidade por Categoria | GB | NFE | — | — | — | — | — |
| Categorias | Drilldown CAT1→CAT5 | TB | NFE | — | — | — | — | — |
| Categorias | CAT2 por Mês | GL | NFE | — | — | — | — | — |
| Categorias | CAT2 × UF | MX | NFE | — | — | — | — | — |
| Categorias | Top Fornecedores por Categoria | T | NFE | — | — | — | — | — |
| Categorias | Top Produtos por Categoria | T | NFE | — | — | — | — | — |
| Filiais | Total Comprado | KPI | NFE | — | — | — | — | — |
| Filiais | Compra Média/Filial | KPI | NFE | — | — | — | — | — |
| Filiais | Maior Filial | KPI | NFE | — | — | — | — | — |
| Filiais | Maior UF | KPI | NFE | — | — | — | — | — |
| Filiais | Maior Negócio | KPI | NFE | — | — | — | — | — |
| Filiais | Ranking de Filiais | HL | NFE | — | — | — | — | — |
| Filiais | Filial × Negócio | MX | NFE | — | — | — | — | — |
| Filiais | Top 3 Filiais × Mês | GL | NFE | — | — | — | — | — |
| Filiais | Filial × Categoria | T | NFE | — | — | — | — | — |
| Filiais | Filial × Fornecedor | T | NFE | — | — | — | — | — |
| Fornecedor | Fornecedores Ativos | KPI | NFE | — | — | — | — | — |
| Fornecedor | Forn. AAA+AA | KPI | CURVA ABC FORN | — | — | — | — | — |
| Fornecedor | Spend AAA/AA/A | KPI | CURVA ABC FORN | — | — | — | — | — |
| Fornecedor | % Spend Top | KPI |  | — | — | — | — | — |
| Fornecedor | Forn. c/ CP Aberto | KPI | CP | — | — | — | — | — |
| Fornecedor | CP Aberto R$ | KPI | CP | — | — | — | — | — |
| Fornecedor | Forn. c/ AD Pendente | KPI | AD_v3 | — | — | — | — | — |
| Fornecedor | AD Pendente R$ | KPI | AD_v3 | — | — | — | — | — |
| Fornecedor | Tabela Fornecedor 360 | TE | NFE · CP · AD_v3 | — | — | — | — | — |
| Fornecedor | Fornecedor × Categoria | T |  | — | — | — | — | — |
| Fornecedor | Produtos por Fornecedor | T |  | — | — | — | — | — |
| Produtos | Total IDs | KPI | PMP_ID_INF_12 | — | — | — | — | — |
| Produtos | PMP Médio Cesta | KPI | PMP_ID_INF_12 | — | — | — | — | — |
| Produtos | Var. PMP > 10% | KPI | PMP_ID_INF_12 | — | — | — | — | — |
| Produtos | IDs Sem Cotação | KPI | NUM_COT | — | — | — | — | — |
| Produtos | Inflação Média Cesta | KPI | INFLAÇÃO | — | — | — | — | — |
| Produtos | Tabela de Produtos | TE | NFE · PMP_ID_INF_12 | — | — | — | — | — |
| Produtos | Top Inflação | HL | PMP_PROD_INF_12 | — | — | — | — | — |
| Produtos | Top Deflação | HL | PMP_PROD_INF_12 | — | — | — | — | — |
| Produtos | PMP por Categoria | T |  | — | — | — | — | — |
| Cotações | Produtos Cotados | KPI | NUM_COT | — | — | — | — | — |
| Cotações | % Cobertura | KPI |  | — | — | — | — | — |
| Cotações | Média Cot./Produto | KPI |  | — | — | — | — | — |
| Cotações | Com 0 Cotação | KPI |  | — | — | — | — | — |
| Cotações | Com 1 Cotação | KPI |  | — | — | — | — | — |
| Cotações | Com ≤3 Cotações | KPI |  | — | — | — | — | — |
| Cotações | Potencial IMP_COT | KPI |  | — | — | — | — | — |
| Cotações | % Comprado no Mínimo | KPI |  | — | — | — | — | — |
| Cotações | Distribuição QTD_COT/Mês | GE | NUM_COT | — | — | — | — | — |
| Cotações | Cobertura por Curva ABC | MX | NUM_COT | — | — | — | — | — |
| Cotações | Cobertura por CAT × Mês | GL | NUM_COT | — | — | — | — | — |
| Cotações | Cobertura por UF | T | NFE | — | — | — | — | — |
| Cotações | MIN Cotação por Fornecedor | T |  | — | — | — | — | — |
| Cotações | Relatório de Cotações | T |  | — | — | — | — | — |
| Cotações | Consulta de Preços | T |  | — | — | — | — | — |
| Cotações | Cotações por Produto | T |  | — | — | — | — | — |
| Cotações | Matriz Produto × Mês | T |  | — | — | — | — | — |
| Cotações | MIN Cot. ≤3 Concorrentes | T |  | — | — | — | — | — |
| Impacto | Impacto Total | KPI | NFE | — | — | — | — | — |
| Impacto | IDs com Impacto | KPI |  | — | — | — | — | — |
| Impacto | % Acima do Mínimo | KPI |  | — | — | — | — | — |
| Impacto | UF Líder em Impacto | KPI |  | — | — | — | — | — |
| Impacto | Top Produto IMP | KPI |  | — | — | — | — | — |
| Impacto | Impacto Nacional por Mês | GB | NFE | ✅ | ✅ | — | — | — |
| Impacto | Impacto por UF | HL | NFE | ✅ | ✅ | — | — | — |
| Impacto | Top IDs por IMP_COT | T | NFE | — | — | — | — | — |
| Impacto | Forn. Mais Baratos Não Escolhidos | T |  | — | — | — | — | — |
| Impacto | Produtos × MIN COT | T |  | — | — | — | — | — |
| Inflação | Inflação Média % | KPI | INFLAÇÃO | — | — | — | — | — |
| Inflação | Exposição R$ 12m | KPI | INFLAÇÃO | — | — | — | — | — |
| Inflação | IDs Inflação >10% | KPI |  | — | — | — | — | — |
| Inflação | CAT2 Mais Inflada | KPI |  | — | — | — | — | — |
| Inflação | Inflação % por CAT × Mês | GL | INFLAÇÃO | — | — | — | — | — |
| Inflação | Exposição R$ por Mês | GB | INFLAÇÃO | ✅ | ✅ | — | — | — |
| Inflação | Top Inflação (Produtos) | HL | PMP_PROD_INF_12 | — | — | — | — | — |
| Inflação | Top Deflação (Produtos) | HL | PMP_PROD_INF_12 | — | — | — | — | — |
| Inflação | Nacional por Categoria | T | INFLAÇÃO | ✅ | ✅ | — | — | — |
| Inflação | Por UF | T | INFLAÇÃO | ✅ | ✅ | — | — | — |
| Inflação | Por Fornecedor | T |  | — | — | — | — | — |
| Inflação | Produto × Categoria | T |  | — | — | — | — | — |
| Financeiro | CP em Aberto | KPI | CP | — | — | — | — | — |
| Financeiro | Títulos Abertos | KPI |  | — | — | — | — | — |
| Financeiro | CP Vencido | KPI |  | — | — | — | — | — |
| Financeiro | A Vencer 7d | KPI |  | — | — | — | — | — |
| Financeiro | CP Crítico +120d | KPI |  | — | — | — | — | — |
| Financeiro | Timeline Semanal | GB | CP_SEMANA | — | — | — | — | — |
| Financeiro | Aging de CP | T | CP | ✅ | ✅ | — | — | — |
| Financeiro | CP por Fornecedor | T | CP | ✅ | ✅ | — | — | — |
| Financeiro | Saldo Semanal 2026 | T |  | — | — | — | — | — |
| Adiantamentos | AD Total 12m | KPI | AD_v3 | — | — | — | — | — |
| Adiantamentos | Conciliado | KPI |  | — | — | — | — | — |
| Adiantamentos | Pendente | KPI |  | — | — | — | — | — |
| Adiantamentos | % Conciliado | KPI |  | — | — | — | — | — |
| Adiantamentos | Registros Pendentes | KPI |  | — | — | — | — | — |
| Adiantamentos | Funil de Conciliação | FU | AD_v3 | — | — | — | — | — |
| Adiantamentos | AD por Empresa | HL | AD_v3 | ✅ | ✅ | — | — | — |
| Adiantamentos | AD por Fornecedor | T | AD_v3 | ✅ | ✅ | — | — | — |
| Adiantamentos | AD por Mês | GL |  | — | — | — | — | — |
| Adiantamentos | AD por UF | HL |  | — | — | — | — | — |
| Adiantamentos | AD por Categoria | T |  | — | — | — | — | — |
| Serviços | Total Serviços | KPI | NFE | — | — | — | — | — |
| Serviços | Fornecedores | KPI |  | — | — | — | — | — |
| Serviços | UFs Atendidas | KPI |  | — | — | — | — | — |
| Serviços | Variação Mensal | KPI |  | — | — | — | — | — |
| Serviços | Maior Categoria | KPI |  | — | — | — | — | — |
| Serviços | Por UF | HL | NFE | ✅ | ✅ | — | — | — |
| Serviços | Por Mês | GB | NFE | — | — | — | — | — |
| Serviços | Por Categoria | T | NFE | — | — | — | — | — |
| Serviços | Fornecedores Serviços | T | NFE | ✅ | ✅ | — | — | — |
| Serviços | Detalhe por CAT5 | T |  | — | — | — | — | — |
| Dados | Linhas Analisadas | KPI | NFE | — | — | — | — | — |
| Dados | Fontes OK | KPI |  | — | — | — | — | — |
| Dados | Fontes Total | KPI |  | — | — | — | — | — |
| Dados | Linhas Sem Cotação | KPI |  | — | — | — | — | — |
| Dados | % Sem Cotação | KPI |  | — | — | — | — | — |
| Dados | Status por Fonte | T |  | — | — | — | — | — |
| Dados | Fila de Saneamento | T |  | — | — | — | — | — |