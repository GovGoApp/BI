# Elementos do BI de Suprimentos

Guia completo dos tipos de elemento disponíveis no dashboard. Serve como referência para a equipe e como knowledge base do assistant de classificação automática de visualizações.

---

## Princípio geral de escolha

A escolha do elemento certo depende de três fatores, **nesta ordem de prioridade**:

1. **A pergunta feita** — qual é a intenção analítica? Comparar? Ver evolução? Detectar concentração? A pergunta é o sinal mais forte.
2. **O shape dos dados** — quantas linhas, quantas colunas, quais tipos, qual cardinalidade.
3. **O contexto de uso** — onde o elemento vai ficar? É um KPI de destaque ou um detalhe operacional?

Nunca escolha um tipo apenas pelo shape. Um resultado de 2 colunas (texto + numérico) pode ser HL, GB, T ou até KPI dependendo do que a pergunta pede.

---

## KPI — Indicador-chave de desempenho

### O que é
Um número único com título, formato e, opcionalmente, um delta (variação percentual) e um estado visual de saúde (verde/amarelo/vermelho).

### Aparência
```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Total Comprado      │    │  Fornecedores Ativos │    │  IDs sem Cotação    │
│  R$ 772 mi           │    │  3.518               │    │  1.204              │
│  ▲ +36,8% vs ano ant│    │  ● estável           │    │  ▼ risco: alto      │
│  [verde]             │    │  [cinza]             │    │  [vermelho]         │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Dados necessários
Um objeto JSON com **uma chave numérica** (e opcionalmente uma segunda para o delta).
```json
{ "total_comprado": 772652870.31, "crescimento_yoy_pct": 36.85 }
```
O KPI usa apenas `total_comprado`. O delta usa `crescimento_yoy_pct`. São dois campos do mesmo objeto — não duas linhas.

### Configuração
| Campo | Obrigatório | Valores | Descrição |
|---|---|---|---|
| `chave` | sim | nome da coluna | Campo numérico a exibir |
| `fmt` | sim | `brl`, `brl2`, `mi`, `pct`, `num`, `dec`, `str` | Formato de exibição |
| `delta_chave` | não | nome da coluna | Campo percentual do delta |
| `delta_ctx` | não | texto livre | Ex: "vs. 12m anteriores" |
| `delta_dir` | não | `up`, `down` | Se subir é bom (`up`) ou ruim (`down`) |
| `state` | não | `ok`, `warn`, `alert` | Cor de fundo: verde/amarelo/vermelho |

### Formatos disponíveis
| Código | Exemplo | Quando usar |
|---|---|---|
| `brl` | R$ 772 mi | Valores monetários acima de 1.000 |
| `brl2` | R$ 1.234,56 | Valores monetários com centavos |
| `mi` | 772,6 mi | Valores grandes não monetários |
| `pct` | 36,8% | Percentuais |
| `num` | 3.518 | Contagens inteiras |
| `dec` | 4,2 | Decimais com 1-2 casas |
| `str` | texto | Valores textuais (ex: nome do top fornecedor) |

### Quando usar KPI
- A pergunta é "quanto", "qual o total", "quantos", "qual a média"
- O resultado tem **1 linha** com colunas numéricas
- O resultado tem **N linhas com 1 linha de total** — usar a linha de total como KPI
- Quer destacar um número para tomada de decisão executiva

### Quando NÃO usar KPI
- Há múltiplas linhas com valores diferentes por categoria → use HL, T ou GB
- O número tem contexto temporal que precisa ser mostrado → use GL
- O valor é um ID ou código → use str apenas se realmente necessário

### Exemplos de queries que geram KPI
```sql
-- 1 linha, 1 coluna numérica → KPI simples
SELECT SUM("TOTAL") AS total_comprado FROM "NFE" WHERE "ANO" = 2026

-- 1 linha, múltiplas colunas → múltiplos KPIs (um por coluna numérica)
SELECT SUM("TOTAL") AS total, COUNT(DISTINCT "CNPJ") AS fornecedores, 
       AVG("TOTAL") AS ticket_medio FROM "NFE" WHERE "ANO" = 2026

-- Com delta (subquery ou CTE)
SELECT 
  SUM(CASE WHEN "ANO"=2026 THEN "TOTAL" END) AS total_2026,
  (SUM(CASE WHEN "ANO"=2026 THEN "TOTAL" END) - SUM(CASE WHEN "ANO"=2025 THEN "TOTAL" END))
  / SUM(CASE WHEN "ANO"=2025 THEN "TOTAL" END) * 100 AS crescimento_pct
FROM "NFE"
```

---

## GL — Gráfico de Linhas

### O que é
Série temporal ou sequência ordenada. Mostra **evolução** ao longo do tempo com área preenchida abaixo da linha.

### Aparência
```
R$ 80mi ┤              ╭────╮
R$ 70mi ┤         ╭────╯    ╰──
R$ 60mi ┤    ╭────╯
R$ 50mi ┤────╯
        └─────────────────────────
        jan  fev  mar  abr  mai  jun
```

### Dados necessários
Array com coluna de período e coluna numérica, **ordenado por período**.
```json
[
  {"mesano": "2026/01", "spend": 52000000},
  {"mesano": "2026/02", "spend": 61000000},
  {"mesano": "2026/03", "spend": 78000000}
]
```

### Configuração
| Campo | Obrigatório | Descrição |
|---|---|---|
| `x` | sim | Coluna do eixo horizontal (período, sequência) |
| `y` | sim | Coluna do valor numérico |
| `color` | não | Cor da linha (hex, padrão: azul) |

### Quando usar GL
- A pergunta tem "ao longo do tempo", "por mês", "evolução", "histórico", "tendência"
- O eixo X é temporal: MESANO (`2026/01`), ANO, trimestre
- O eixo X é uma sequência ordenada com sentido progressivo
- Há 6 a 36 pontos de dados

### Quando NÃO usar GL
- Menos de 4 pontos → KPI com delta é mais limpo
- O eixo X não tem ordem natural (categorias sem sequência) → use GB
- Há múltiplas séries para comparar → use GB ou GE
- Mais de 50 pontos → linha fica ilegível

### Exemplos de queries que geram GL
```sql
-- Série mensal padrão
SELECT "MESANO", SUM("TOTAL") AS spend 
FROM "NFE" WHERE "ANO" IN (2025,2026)
GROUP BY "MESANO" ORDER BY "MESANO"

-- PMP de um produto ao longo do tempo
SELECT "MESANO", AVG("PMP_0") AS pmp_medio
FROM "PMP_ID_INF_12" WHERE "CDPRODUTO" = 'X123'
GROUP BY "MESANO" ORDER BY "MESANO"

-- Evolução de inflação por categoria
SELECT "MESANO", AVG("PERC_INF_ID_PMP") AS inflacao_media
FROM "INFLACAO" WHERE "CAT2" = 'I2 - PERECIVEIS'
GROUP BY "MESANO" ORDER BY "MESANO"
```

---

## GB — Gráfico de Barras

### O que é
Comparação entre **categorias discretas** com barras verticais. Ideal quando o eixo X é nominal (não temporal) e a quantidade de categorias é pequena.

### Aparência
```
R$200mi│███
R$150mi│███ ███
R$100mi│███ ███ ███
R$ 50mi│███ ███ ███ ███ ███
       └──────────────────────
        SP  RJ  MG  BA  RS
```

### Dados necessários
Array com coluna categórica (texto curto) e coluna numérica.
```json
[
  {"uf": "SP", "spend": 200000000},
  {"uf": "RJ", "spend": 150000000},
  {"uf": "MG", "spend": 120000000}
]
```

### Configuração
| Campo | Obrigatório | Descrição |
|---|---|---|
| `x` | sim | Coluna de categorias (eixo horizontal) |
| `y` | sim | Coluna de valores |
| `color` | não | Cor das barras (hex) |

### Quando usar GB
- A pergunta é "por UF", "por negócio", "por empresa", "por região"
- As categorias têm labels curtos (2-5 chars): UF, código, sigla
- Há 3 a 15 categorias
- A **comparação absoluta** entre categorias é mais importante que a proporção

### Quando NÃO usar GB
- Labels longos (nomes de fornecedores, produtos) → use HL
- Mais de 15-20 categorias → use HL ou T
- Eixo X é temporal → use GL
- Quer mostrar composição dentro de cada barra → use GE

### Exemplos de queries que geram GB
```sql
-- Por UF
SELECT "UF", SUM("TOTAL") AS spend 
FROM "NFE" GROUP BY "UF" ORDER BY spend DESC LIMIT 10

-- Por empresa
SELECT "NMEMP" AS empresa, SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "NMEMP" ORDER BY spend DESC

-- Por negócio
SELECT "FI.NEGOCIO" AS negocio, SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "FI.NEGOCIO" ORDER BY spend DESC
```

---

## GE — Gráfico Empilhado

### O que é
Barras verticais com **composição interna** — cada barra mostra o total e a divisão por sub-categoria. Ideal para ver "quanto de cada parte" existe em cada grupo.

### Aparência
```
R$200mi│▓▓▓░░░▒▒
R$150mi│▓▓▓░░░▒▒ ▓▓▓▒▒
R$100mi│▓▓▓░░░▒▒ ▓▓▓▒▒ ▓▓▒
       └──────────────────
        SP        RJ    MG
        ▓=D5  ░=I2  ▒=A2
```

### Dados necessários
Array com coluna de grupo (eixo X), coluna de sub-grupo e coluna numérica. O sistema faz o pivot internamente.
```json
[
  {"uf": "SP", "cat2": "D5 - SERVICOS", "spend": 120000000},
  {"uf": "SP", "cat2": "I2 - PERECIVEIS", "spend": 80000000},
  {"uf": "RJ", "cat2": "D5 - SERVICOS", "spend": 90000000}
]
```

### Configuração
| Campo | Obrigatório | Descrição |
|---|---|---|
| `x` | sim | Coluna do eixo principal (grupos) |
| `stacks` | sim | Array de sub-grupos a empilhar |
| `color` | não | Paleta (automática por padrão) |

### Quando usar GE
- A pergunta é "por X dividido por Y", "composição de", "participação de cada categoria em"
- Há 2 dimensões categóricas + 1 numérica
- O eixo X tem até 8-10 grupos
- O eixo de sub-grupos tem até 5-6 valores (mais que isso fica ilegível)

### Quando NÃO usar GE
- Sub-grupos têm cardinalidade alta (>6) → use MX
- A escala entre sub-grupos é muito diferente → use T para preservar legibilidade
- Interesse é só no total, não na composição → use GB

### Exemplos de queries que geram GE
```sql
-- Composição por categoria dentro de cada UF
SELECT "UF", "CAT2", SUM("TOTAL") AS spend
FROM "NFE" WHERE "UF" IN ('SP','RJ','MG','BA','RS')
GROUP BY "UF", "CAT2" ORDER BY "UF", spend DESC

-- Gasto por empresa e negócio
SELECT "NMEMP" AS empresa, "FI.NEGOCIO" AS negocio, SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "NMEMP", "FI.NEGOCIO"
```

---

## HL — Lista de Barras Horizontais

### O que é
Ranking visual com barras horizontais proporcionais. Cada linha tem label (nome), valor numérico e barra de comprimento proporcional ao maior valor. Excelente para listas de fornecedores, produtos, categorias.

### Aparência
```
Fornecedor Alfa S.A.       ████████████████████ R$ 48 mi
Beta Distribuidora Ltda    █████████████        R$ 32 mi
Gamma Comércio             █████████            R$ 22 mi
Delta Importação           ████                 R$ 10 mi
```

### Dados necessários
Array com coluna de label e coluna numérica, preferencialmente ordenado por valor descendente.
```json
[
  {"fornecedor": "Alfa S.A.", "spend": 48000000},
  {"fornecedor": "Beta Ltda", "spend": 32000000},
  {"fornecedor": "Gamma Com.", "spend": 22000000}
]
```

### Configuração
| Campo | Obrigatório | Descrição |
|---|---|---|
| `label` | sim | Coluna de nomes/labels |
| `value` | sim | Coluna de valores numéricos |
| `sub` | não | Coluna de subtítulo (ex: UF, ABC, categoria) |

### Quando usar HL
- A pergunta tem "top", "maiores", "principais", "ranking de"
- Labels são longos (nomes de fornecedores, produtos, categorias com código)
- Há 5 a 20 itens
- A **proporção relativa** entre itens é importante (a barra visual comunica isso)
- É um ranking — a ordenação é parte da mensagem

### Quando NÃO usar HL
- Labels muito curtos (UF, siglas) → GB fica mais limpo visualmente
- Mais de 20 itens → T/TE com paginação é mais navegável
- Há múltiplas métricas por item → T permite mostrar todas as colunas
- A pergunta não é sobre ranking → outros tipos são mais adequados

### Exemplos de queries que geram HL
```sql
-- Top fornecedores
SELECT "FANTASIA_OFICIAL" AS fornecedor, SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "FANTASIA_OFICIAL" ORDER BY spend DESC LIMIT 15

-- Top produtos
SELECT "NMPRODUTO_OFICIAL" AS produto, SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "NMPRODUTO_OFICIAL" ORDER BY spend DESC LIMIT 20

-- Top categorias CAT2
SELECT "CAT2", SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "CAT2" ORDER BY spend DESC LIMIT 10

-- Com subtítulo (curva ABC)
SELECT "FANTASIA_OFICIAL" AS fornecedor, "CURVA_FORN" AS abc, SUM("TOTAL") AS spend
FROM "NFE" GROUP BY "FANTASIA_OFICIAL", "CURVA_FORN" ORDER BY spend DESC LIMIT 15
```

---

## T — Tabela Simples

### O que é
Tabela configurável com colunas selecionadas, formatos personalizados e suporte a badges coloridas (para %, curva ABC, status). Ideal para dados multidimensionais onde a leitura linha-a-linha importa.

### Aparência
```
┌────────────────────┬───────────┬──────┬────────────┬──────────┐
│ Fornecedor         │ Gasto     │ ABC  │ Cotações   │ CP Aberto│
├────────────────────┼───────────┼──────┼────────────┼──────────┤
│ Alfa S.A.          │ R$ 48 mi  │ AAA  │ 12         │ R$ 2 mi  │
│ Beta Ltda          │ R$ 32 mi  │ AA   │  8         │ R$ 1 mi  │
│ Gamma Com.         │ R$ 22 mi  │ A    │  5         │ —        │
└────────────────────┴───────────┴──────┴────────────┴──────────┘
```

### Dados necessários
Array de objetos com qualquer número de colunas.
```json
[
  {"fornecedor": "Alfa", "spend": 48000000, "curva": "AAA", "num_cot": 12, "cp_aberto": 2000000},
  {"fornecedor": "Beta", "spend": 32000000, "curva": "AA", "num_cot": 8, "cp_aberto": 1000000}
]
```

### Configuração — colunas
Cada coluna é definida por:
```json
{"key": "spend", "label": "Gasto", "fmt": "brl", "cls": "num"}
```

| `cls` | Comportamento |
|---|---|
| `nm` | Nome longo — permite quebra de linha, coluna mais larga |
| `num` | Alinhamento à direita (padrão para numérico) |
| `spark` | Esperado um array JSON na célula — renderiza como sparkline SVG mini |

| `fmt` | Exemplo |
|---|---|
| `brl` | R$ 48 mi |
| `brl2` | R$ 48.000.000,00 |
| `pct` | 36,8% (com badge verde/vermelho) |
| `num` | 12.345 |
| nenhum | valor bruto como string |

### TE — Tabela Expandível
Idêntica a T, mas com limite de 100 linhas (vs 50 no T) e altura maior. Use quando o resultado tem muitas linhas e o usuário precisa rolar para ver tudo.

### Quando usar T ou TE
- A pergunta envolve múltiplas colunas por entidade ("fornecedor com gasto, cotações e CP")
- O resultado tem mais de 2 colunas relevantes
- Há mais de 20 linhas → HL fica grande demais, T com paginação é melhor
- O usuário precisa comparar vários atributos de cada linha

### Quando NÃO usar T
- Resultado de 1 coluna numérica → KPI
- Resultado de 2 colunas (nome + valor) com até 20 linhas → HL é mais visual
- Dados são temporais → GL conta a história melhor

### Exemplos de queries que geram T
```sql
-- Ficha completa do fornecedor
SELECT "FANTASIA_OFICIAL" AS fornecedor, "UF", "CURVA_FORN" AS abc,
       SUM("TOTAL") AS spend, COUNT(DISTINCT "CDPRODUTO") AS produtos,
       SUM("IMP_COT") AS impacto_cot
FROM "NFE" GROUP BY "FANTASIA_OFICIAL", "UF", "CURVA_FORN"
ORDER BY spend DESC LIMIT 50

-- Produtos sem cotação com detalhes
SELECT "NMPRODUTO_OFICIAL" AS produto, "CAT2", "CAT3",
       SUM("TOTAL") AS spend, COUNT(DISTINCT "CDFILIAL") AS filiais
FROM "NFE" WHERE "NUM_COT" = 0
GROUP BY "NMPRODUTO_OFICIAL", "CAT2", "CAT3"
ORDER BY spend DESC LIMIT 100
```

---

## MX — Heatmap Matrix (Matriz de Calor)

### O que é
Cruzamento de **duas dimensões categóricas** com intensidade de cor representando o valor. Ideal para detectar concentrações, lacunas e padrões em dados bidimensionais.

### Aparência
```
           SP        RJ        MG        BA        RS
D5        ████      ███       ██        ██        █
I2        ███       ██        ██        ░         ░
A2        ██        █         █         ░         ░
I1        █         █         ░         ░         ░

████ = muito alto    ░ = baixo/zero
```

### Dados necessários
Array com exatamente **3 colunas**: linha (texto), coluna (texto), valor (numérico). O pivot é automático.
```json
[
  {"cat2": "D5 - SERVICOS", "uf": "SP", "spend": 200000000},
  {"cat2": "D5 - SERVICOS", "uf": "RJ", "spend": 90000000},
  {"cat2": "I2 - PERECIVEIS", "uf": "SP", "spend": 80000000}
]
```

### Configuração
| Campo | Obrigatório | Descrição |
|---|---|---|
| `row_key` | sim | Coluna das linhas da matriz |
| `col_key` | sim | Coluna das colunas da matriz |
| `val_key` | sim | Coluna do valor (determina intensidade da cor) |

### Quando usar MX
- A pergunta é "cruzamento de X com Y", "como X se distribui por Y", "mapa de concentração"
- Há exatamente 2 dimensões categóricas + 1 numérica
- Dimensão de linhas: 4 a 15 valores
- Dimensão de colunas: 4 a 15 valores (matriz até ~15×15)
- O interesse é no **padrão visual** de concentração, não nos valores exatos

### Quando NÃO usar MX
- Uma das dimensões tem cardinalidade alta (>20) → T é mais navegável
- Menos de 3×3 → GE ou GB mostra melhor
- Os valores exatos importam mais que o padrão → T com `fmt:brl`
- Há só uma dimensão categórica → HL, GB ou GL

### Diferença entre MX e GE
- **GE** enfatiza a composição dentro de cada grupo (stacked) — bom quando o total de cada coluna é tão importante quanto a divisão
- **MX** enfatiza o padrão bidimensional — bom quando tanto linhas quanto colunas são dimensões de interesse independente

### Exemplos de queries que geram MX
```sql
-- Gasto por categoria e UF (caso clássico)
SELECT "CAT2", "UF", SUM("TOTAL") AS spend
FROM "NFE" WHERE "UF" IN ('SP','RJ','MG','BA','RS','GO','SC','PR','CE','PE')
GROUP BY "CAT2", "UF"

-- Número de cotações por produto e fornecedor (top 10)
SELECT "NMPRODUTO_OFICIAL" AS produto, "FANTASIA_OFICIAL" AS fornecedor,
       COUNT(*) AS num_cot
FROM "COT"
GROUP BY "NMPRODUTO_OFICIAL", "FANTASIA_OFICIAL"
HAVING COUNT(*) > 0
ORDER BY num_cot DESC LIMIT 150

-- Impacto por negócio e categoria
SELECT "FI.NEGOCIO" AS negocio, "CAT2", SUM("IMP_COT") AS impacto
FROM "NFE" WHERE "IMP_COT" > 0
GROUP BY "FI.NEGOCIO", "CAT2"
```

---

## FU — Funil

### O que é
Etapas sequenciais com volumes decrescentes. Comunica **conversão** ou **concentração progressiva**. Raramente gerado por NL-SQL livre — mais usado para análises de pipeline pré-definidas.

### Aparência
```
████████████████████████████  Total cotado (1.200)
█████████████████████         Com proposta (840)
████████████                  Comprado abaixo preço (480)
███████                       Abaixo do mínimo (280)
```

### Dados necessários
Array ordenado de `{label, valor}` com valores decrescentes.
```json
[
  {"etapa": "IDs cotados", "n": 1200},
  {"etapa": "Comprados com cotação", "n": 840},
  {"etapa": "Comprados no menor preço", "n": 480}
]
```

### Quando usar FU
- A pergunta descreve etapas de um processo com filtragem progressiva
- Os valores têm relação de subconjunto (cada etapa cabe dentro da anterior)
- Há 3 a 6 etapas

### Exemplos de queries que geram FU
```sql
-- Funil de cobertura de cotação
SELECT 'IDs distintos' AS etapa, COUNT(DISTINCT "CDPRODUTO") AS n FROM "NFE"
UNION ALL
SELECT 'Com cotação', COUNT(DISTINCT "CDPRODUTO") FROM "COT"
UNION ALL
SELECT 'Comprado no menor preço', COUNT(DISTINCT "CDPRODUTO") 
FROM "NFE" WHERE "IMP_COT" = 0
```

---

## Guia de decisão rápida

Use este fluxo ao receber um resultado de query:

```
O resultado tem quantas linhas?
│
├─ 1 linha
│   └─ → KPI (uma por coluna numérica)
│
└─ Múltiplas linhas
    │
    ├─ A pergunta menciona tempo, evolução, histórico, mês?
    │   └─ → GL (se eixo X tem padrão YYYY/MM ou data)
    │
    ├─ A pergunta menciona top, ranking, maiores, principais?
    │   ├─ Labels longos (nomes) → HL
    │   └─ Labels curtos (UF, siglas) e ≤15 itens → GB
    │
    ├─ Há exatamente 2 dimensões texto + 1 numérica?
    │   ├─ Dimensão de coluna tem ≤6 valores → GE (composição)
    │   └─ Ambas têm 4-15 valores → MX (heatmap)
    │
    ├─ O resultado tem 3+ colunas heterogêneas?
    │   ├─ ≤50 linhas → T
    │   └─ >50 linhas → TE
    │
    └─ Os valores representam etapas sequenciais decrescentes?
        └─ → FU (funil)
```

---

## Anti-padrões comuns

| Situação | Tipo errado | Tipo correto | Por quê |
|---|---|---|---|
| Top 15 fornecedores | GB | HL | GB com nomes longos no eixo X fica ilegível |
| Gasto por mês | GB | GL | Dados temporais ordenados têm narrativa de evolução |
| 1 número grande | T | KPI | Tabela de 1 linha × 1 coluna desperdiça espaço |
| Categoria × UF com 10×10 | GE | MX | GE com 10 stacks fica ilegível; MX mostra o padrão |
| 200 fornecedores rankeados | HL | TE | HL funciona bem até ~20 itens; acima disso, tabela |
| 2 categorias × gasto | MX | GE ou GB | Matriz 2×2 não tem padrão visual relevante |

---

## Notas sobre o BI de Suprimentos

### Convenções de nomes de colunas nos dados do Zoho

| Padrão | Significa |
|---|---|
| `MESANO` | Período no formato "YYYY/MM" — sempre GL |
| `TOTAL` | Valor monetário da NF — sempre `fmt: brl` |
| `CURVA_FORN`, `CURVA_PROD` | Curva ABC (AAA/AA/A/B/BB/C/CC/CCC) |
| `IMP_COT` | Impacto de cotação (quanto pagou acima do menor preço) |
| `PERC_INF_ID_PMP` | Inflação percentual — cuidado com outliers (cap em ±500%) |
| `FANTASIA_OFICIAL` | Nome oficial do fornecedor — label para HL/T |
| `NMPRODUTO_OFICIAL` | Nome oficial do produto — label para HL/T |
| `CDPRODUTO` | Código do produto — não usar como label sozinho |

### Filtros implícitos importantes

Sempre considerar ao gerar SQL para o BI:
- **Excluir D5 para análise operacional:** `"CAT1" NOT LIKE 'D%'` ou `"CAT2" != 'D5 - SERVICOS'`
- **Excluir _MATRIZ:** `"FI.NEGOCIO" <> '_MATRIZ'`
- **Período padrão:** `"ANO" = 2026` ou últimos 12 meses com `"MESANO" >= '2025/06'`
- **Curva ABC relevante:** `"CURVA_FORN" IN ('AAA','AA','A')` para análise estratégica

### Limites de linhas por tipo (hard limits no renderer)

| Tipo | Limite | O que acontece acima |
|---|---|---|
| KPI | sem limite | Objeto JSON, não tem linhas |
| GL | 50 | Pontos comprimidos, ilegível |
| GB | 24 | Barras finas, ilegível |
| GE | 24 | Idem GB |
| HL | 20 | Lista longa perde o impacto visual |
| T | 50 | Truncado; use TE |
| TE | 100 | Truncado |
| MX | 200 linhas | Pivot pode gerar matriz muito grande |
| FU | 10 | Raramente necessário mais |
