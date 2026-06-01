# Mapa das Abas — BI de Suprimentos v4

Baseado na leitura direta do `design/BI Suprimentos v4.html`.

15 abas, nessa ordem exata. **Não alterar a ordem ou os nomes sem atualizar este documento e o README.**

| # | data-page | Label na aba | Domínio principal |
|---|---|---|---|
| 1 | `resumo` | Resumo | Visão executiva geral |
| 2 | `oportunidades` | Oportunidades | Impacto de cotação, negociação |
| 3 | `categorias` | Categorias | Hierarquia I→D→A |
| 4 | `filiais` | Filiais | Por filial, negócio, região |
| 5 | `estoque` | Estoque | Estoque por filial (APURAÇÃO DE RESULTADOS) |
| 6 | `forn360` | Fornecedor | Painel 360 por fornecedor |
| 7 | `produtos` | Produtos | Produtos, preços, PMP |
| 8 | `cotacoes` | Cotações | Contagem, cobertura, tabela de preços |
| 9 | `impacto` | Impacto | IMP_COT — compra acima do menor preço |
| 10 | `inflacao` | Inflação | INF — variação do PMP no tempo |
| 11 | `fiscal` | Fiscal | Regime tributário, crédito 2027 |
| 12 | `financeiro` | Financeiro | Contas a pagar, aging, saldo |
| 13 | `adiantamentos` | Adiantamentos | Conciliação AD × NF |
| 14 | `servicos` | Serviços | Despesas de serviços |
| 15 | `qualidade` | Dados | Qualidade e cobertura dos dados |

---

## Filtros globais

Definidos no topbar e aplicáveis em todas as abas:

- **Empresa/Filial**: RC, ME, SU (badges)
- **UF**: DF, ES, MA, PA, PB, PE, PI, RJ, RN, SE, SP
- **Período** (MESANO/ANO)
- **Curva**: AAA, AA, A, B, BB, C, CC, CCC
- **Negócio**: CD, COZINHA, ESCOLA, HOSPITAL, MERENDA, PRESIDIO, MATRIZ
- **CAT1** (com cascata para CAT2...CAT5 na aba Categorias)

---

## Componentes por tipo

O Design System define os seguintes tipos de elemento:

| Tipo | Classe CSS | Uso |
|---|---|---|
| KPI card | `.kpi` | Métricas principais no topo de cada aba |
| Tabela | `.table` | Dados tabulares com linhas expansíveis |
| Pill/Badge | `.pill`, `.badge` | Status, curva ABC, empresa |
| Barra proporcional | `.bar` | Progresso, participação |
| Spark | `.spark` | Micro gráfico de tendência |
| Curva ABC | `.curva` | AAA/AA/A/B/BB/C/CC/CCC |

### KPI card — estados

| Classe | Significado |
|---|---|
| `.kpi.alert` | Barra vermelha — atenção imediata |
| `.kpi.warn` | Barra amarela — monitorar |
| `.kpi.ok` | Barra verde — dentro do esperado |
| `.kpi` sem modificador | Neutro |

### Curva ABC — visual

| Curvas | Estilo |
|---|---|
| AAA, AA, A | Fundo preto (#0f172a), texto branco |
| B, BB | Fundo cinza escuro (#334155), texto branco |
| C, CC, CCC | Fundo cinza claro (#cbd5e1), texto escuro |

---

## Tokens de cor do Design System

```css
--bg:          #f3f6fa   /* fundo geral */
--ink:         #0f172a   /* texto principal */
--muted:       #64748b   /* texto secundário */
--line:        #d8e0ea   /* bordas */
--card:        #ffffff   /* cards */
--blue:        #2563eb   /* ação, ativo */
--blue-soft:   #eff6ff   /* fundo azul suave */
--green:       #16a34a   /* positivo */
--green-soft:  #ecfdf5
--yellow:      #a16207   /* alerta */
--yellow-soft: #fef9c3
--red:         #b91c1c   /* negativo/erro */
--red-soft:    #fee2e2
--gray:        #475569
--gray-soft:   #eef2f7
--head:        #e9eff7   /* cabeçalho de tabela */
--hover:       #f6f9fd   /* hover de linha */
```

---

## Hierarquia de categorias

Ordem obrigatória nos filtros: **I → D → A**

```
I - INSUMOS
  I0 - NUTRICIONAIS
  I1 - ESTOCÁVEIS
  I2 - PERECÍVEIS
  I3 - HORTIFRUTI
  I4 - DESCARTÁVEIS
  I5 - LIMPEZA
  I6 - GÁS

D - DESPESAS
  D1 - VESTUÁRIOS/EPIs
  D2 - ESCRITÓRIO
  D3 - MANUTENÇÃO
  D4 - CONSTRUÇÃO
  D5 - SERVIÇOS
  D6 - COMPRA A VISTA
  D7 - CESTA BÁSICA / COMODATO
  D8 - UTENSÍLIOS

A - ATIVOS
  A1 - ATIVOS DIRETOS
  A2 - ATIVOS INDIRETOS
```

Cada nível tem até CAT5. Filtros sempre em cascata: CAT1 → CAT2 → CAT3 → CAT4 → CAT5.
