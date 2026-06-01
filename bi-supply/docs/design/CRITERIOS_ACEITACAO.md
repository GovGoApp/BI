# Critérios de Aceitação — BI de Suprimentos

Checklist para validar que o dashboard gerado está conforme o esperado.

---

## Estrutura

- [ ] Dashboard abre como arquivo HTML único no browser sem servidor
- [ ] Todas as 15 abas estão presentes e navegáveis
- [ ] A aba ativa ao abrir é **Resumo**
- [ ] Filtros globais estão visíveis no topo em todas as abas
- [ ] Filtros de categoria seguem a ordem I→D→A em cascata (CAT1→CAT5)

---

## Visual — conformidade com o Design System

- [ ] Fundo geral usa `--bg: #f3f6fa`
- [ ] Cards usam `--card: #ffffff` com borda `--line: #d8e0ea`
- [ ] Tipografia: Segoe UI ou Arial, 13px base
- [ ] Azul de ação: `#2563eb` (links, botões primários, filtro ativo)
- [ ] Nenhum CSS inventado fora do Design System
- [ ] Curvas ABC com estilos corretos: AAA/AA/A fundo preto, C/CC/CCC cinza
- [ ] KPIs com estado `.alert` (vermelho), `.warn` (amarelo), `.ok` (verde)
- [ ] Tabelas com cabeçalho `--head: #e9eff7` e hover `--hover: #f6f9fd`
- [ ] Pills com as classes `.b` (azul), `.g` (verde), `.y` (amarelo), `.r` (vermelho), `.k` (cinza)

---

## Interface — aparência de ferramenta de trabalho

- [ ] Nenhuma splash screen, capa ou texto institucional
- [ ] KPIs no topo de cada aba
- [ ] Filtros sempre visíveis (não colapsados por padrão)
- [ ] Tabelas compactas (padding reduzido, linhas densas)
- [ ] Linhas de tabela expansíveis onde há detalhe
- [ ] Nenhum texto decorativo ou marketing dentro da interface

---

## Dados

- [ ] IMP (impacto de cotação) e INF (inflação) em abas separadas
- [ ] Componentes com origem no Zoho têm `Origem Zoho: NOME_DA_VIEW` no subtítulo
- [ ] KPIs calculados corretamente (validar manualmente contra dados Zoho)
- [ ] Filtros funcionam — aplicam-se a todos os elementos da aba
- [ ] Dados embutidos no HTML como JSON (nenhuma requisição externa ao abrir)

---

## Abas — presença dos componentes mínimos

| Aba | Componente mínimo obrigatório | OK |
|---|---|---|
| Resumo | KPIs: total comprado, fornecedores, impacto | [ ] |
| Oportunidades | Ranking de IDs por IMP_COT | [ ] |
| Categorias | Filtros em cascata CAT1→CAT5 | [ ] |
| Filiais | Tabela por filial com total comprado | [ ] |
| Estoque | Tabela de estoque por filial | [ ] |
| Fornecedor 360 | Busca por fornecedor, painel expandido | [ ] |
| Produtos | Tabela com PMP e série 12 meses | [ ] |
| Cotações | Os 10 blocos obrigatórios (ver ESPECIFICACAO_ABAS) | [ ] |
| Impacto | Tabela com IMP_COT por ID | [ ] |
| Inflação | Gráfico INF por mês e categoria | [ ] |
| Fiscal | Tabela de fornecedores por regime fiscal | [ ] |
| Financeiro | Tabela CP com status de vencimento | [ ] |
| Adiantamentos | Tabela de conciliação AD × NF | [ ] |
| Serviços | Tabela de despesas por UF e categoria | [ ] |
| Dados | Monitor de qualidade com status por fonte | [ ] |

---

## Performance e compatibilidade

- [ ] Abre sem erros no Chrome e Edge
- [ ] Renderiza em 1366×768 sem scroll horizontal
- [ ] Renderiza em 1440×900
- [ ] HTML pesa menos de 5MB (com dados embutidos)
- [ ] Nenhum erro no console do navegador

---

## Segurança

- [ ] Nenhuma credencial Zoho no HTML gerado
- [ ] Nenhuma URL de API no HTML gerado
- [ ] `zoho/zoho.env` está no `.gitignore`
- [ ] `data/raw/` e `data/processed/` estão no `.gitignore`
- [ ] `dist/` está no `.gitignore`
