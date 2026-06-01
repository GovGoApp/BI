# Dados e Domínios — BI de Suprimentos

## Contexto

O BI é construído a partir de dados extraídos do Zoho Analytics (workspace `SUPRIMENTOS`), cruzados com a base de fornecedores e regime fiscal do projeto principal.

## Fontes principais por domínio

### Compras / notas

- `NFE` — fato principal de compras, 239K linhas, 63 colunas
- `NF COM ITENS - CONSOLIDADO` — preserva dados de nota, chave, número e datas
- `ENTRADA DE NOTAS - [TODAS]`
- `NFE - IDEAL`, `NFE - MELHOR`, `NFE - SUPERA` — por empresa

### Cotações

- `COT` — 159K linhas, cotações por produto/fornecedor/mês
- `COT_MIN_FORN` — fornecedor com menor preço por produto
- `NUM_COT` — contagem de cotações por produto/período
- `COT - IDEAL`, `COT - MELHOR`, `COT - SUPERA`

### Curvas ABC

- `CURVA FORN - TODAS` — curva de fornecedor
- `CURVA ABC FORN - TOTAL`
- `CURVA PROD - TODAS` — curva de produto
- `CURVA ID - TODAS` — curva de ID

### Preço médio, inflação e impacto

- `PMP_ID`, `PMP_ID_INF`, `PMP_ID_INF_12` — preço médio por ID
- `PMP_PROD`, `PMP_PROD_INF`, `PMP_PROD_INF_12` — preço médio por produto
- `INFLAÇÃO` — variação do PMP por período

### Financeiro / Contas a pagar

- `CP` — 116K linhas, contas a pagar completas
- `CP_MOV`, `CP_SEMANA`, `CP_SALDO_2025`, `CP_SALDO_2026`
- `TODAS - CONTAS A PAGAR`

### Adiantamentos

- `AD_v3` — versão principal
- `ADIANTAMENTO_NFE`, `AD_v1`, `AD_v2`
- `NF ADT - IDEAL`, `NF ADT - MELHOR`, `NF ADT - POMME VITA`

### Filiais e organização

- `FILIAIS_SUPPLY` — principal para suprimentos
- `FILIAIS`, `FILIAIS_DRO`, `FILIAIS_NEW`

---

## Empresas

| Código | Empresa |
|---|---|
| RC | Ideal / RC |
| ME | Melhor |
| SU | Supera / Pomme Vita |

Badges no BI: `RC`, `ME`, `SU`

## Tipos de negócio

`CD` · `COZINHA` · `ESCOLA` · `HOSPITAL` · `MERENDA` · `PRESIDIO` · `MATRIZ`

## UFs presentes

`DF` · `ES` · `MA` · `PA` · `PB` · `PE` · `PI` · `RJ` · `RN` · `SE` · `SP`

---

## Campos de fornecedor

| Campo | Descrição |
|---|---|
| `CDFORNECED` | Código interno do fornecedor |
| `NMRAZSOCFORN` | Razão social |
| `NMFANTFORN` | Nome fantasia |
| `CDFORNECED_OFICIAL` | Código padronizado |
| `FANTASIA_OFICIAL` | Nome fantasia oficial |
| `RAZAO_OFICIAL` | Razão social oficial |
| `CNPJ` | Documento (quando disponível) |

## Campos de produto

| Campo | Descrição |
|---|---|
| `ID` | Chave analítica (combina empresa + UF + produto) |
| `CDPRODUTO` | Código do produto |
| `NMPRODUTO` | Nome do produto |
| `CDPRODESTO` | Código padronizado de estoque |
| `NMPRODUTO_EST` | Nome padronizado de estoque |
| `CDPRODUTO_OFICIAL` | Código oficial |
| `NMPRODUTO_OFICIAL` | Nome oficial |
| `CAT1` a `CAT5` | Hierarquia de categorias |

## O que é ID

`ID` é uma chave analítica que combina empresa, UF e código padronizado de produto.

Exemplo: `RCSPI105201000`

No BI, `ID` é o nível de análise mais específico — permite comparar preço, cotação, inflação e impacto dentro de um contexto operacional preciso.

---

## Curvas ABC

Classifica fornecedores, produtos ou IDs por relevância econômica.

| Curva | Faixa acumulada |
|---|---|
| AAA | Até 50% |
| AA | 50% a 60% |
| A | 60% a 70% |
| B | 70% a 80% |
| BB | 80% a 90% |
| C | 90% a 95% |
| CC | 95% a 98% |
| CCC | 98% a 100% |

No design, curvas aparecem como chips com fundo escuro (AAA/AA/A) ou cinza (C/CC/CCC).

---

## IMP — Impacto de Cotação

Impacto é a perda/oportunidade econômica de comprar acima da menor cotação disponível.

**Fórmula:**
```
IMP_COT = (preço médio comprado - menor cotação) × quantidade
```

Campos relacionados:
- `IMP_COT` — impacto de cotação
- `IMP_ID` — impacto por ID
- `IMP_PRODT` — impacto por produto
- `PRE_MIN_COT` — preço mínimo cotado
- `FORN_MIN_COT` — fornecedor do menor preço

**Onde aparece no BI:** abas Impacto, Cotações, Oportunidades, Fornecedor 360

---

## INF — Inflação / Variação de PMP

Inflação é a variação do Preço Médio Ponderado ao longo do tempo.

Campos relacionados:
- `PMP_0` a `PMP_12` — série mensal de PMP
- `SOMA_INF_*`, `PERC_INF_*` — soma e percentual de variação
- `INF_ID`, `INF_ID_PMP`, `INF_PROD_PMP`

**Onde aparece no BI:** aba Inflação, Categorias, Produtos

**Regra:** IMP e INF são conceitos distintos. Nunca misturar no mesmo gráfico sem identificação clara.

---

## Cotações — campos principais

| Campo | Descrição |
|---|---|
| `QTD_COT` | Quantidade de cotações |
| `MIN_COT` | Menor preço cotado |
| `MED_COT` | Preço médio cotado |
| `MAX_COT` | Maior preço cotado |
| `PRE_MIN_COT` | Preço mínimo da cotação |
| `FORN_MIN_COT` | Fornecedor com menor preço |
| `FORN_MENOR_PRECO` | Nome do fornecedor mais barato |
| `CNPJ_MENOR_PRECO` | CNPJ do fornecedor mais barato |

---

## Adiantamentos — campos de análise

| Campo | Descrição |
|---|---|
| `STATUS_CONC` | Status de conciliação |
| `STATUS_CONCILIACAO` | Descrição do status |
| `VALOR_CONCILIADO` | Valor conciliado |
| `NRONOTA_NF` | Número da nota fiscal |
| `NRONOTA_AD` | Número do adiantamento |

---

## Contas a pagar — campos principais

| Campo | Descrição |
|---|---|
| `DTEMISSAO` | Data de emissão |
| `DTORIGVENPAG` | Data de vencimento original |
| `DTATUAVENPAG` | Data de vencimento atual |
| `DTBAIXAPAG` | Data de baixa/pagamento |
| `VRATUAPAG` | Valor atualizado |
| `VRBAIXAPAG` | Valor baixado |
| `STATUSPAG` | Status do pagamento |
| `STATUS_VENC` | Status de vencimento |
| `FAIXA_DIAS` | Faixa de dias em atraso |
