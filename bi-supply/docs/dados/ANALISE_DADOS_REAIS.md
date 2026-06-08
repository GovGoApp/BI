# Análise dos Dados Reais — BI de Suprimentos

Documento técnico baseado na análise dos arquivos raw e processed. Referência para desenvolvimento do prompt NL-SQL e definição de elementos do BI.

**Gerado em:** 2026-06-03 | **Base:** 18 fontes, ~1,04M linhas totais

---

## 1. Visão Geral das Fontes

| Fonte | Linhas | Tipo | Frequência |
|---|---|---|---|
| NFE | 239.9K | Fato principal | 24h |
| NF COM ITENS | 122K | Fato detalhado | 24h |
| COT | 164.1K | Fato cotações | 24h |
| COT_MIN_FORN | 68K | Menor preço por ID/mês | 24h |
| NUM_COT | 68.2K | Contagem de cotações | 24h |
| CP | 118.3K | Contas a pagar | 24h |
| CP_MOV | 55.2K | Movimentação semanal CP | 24h |
| CP_SEMANA | 46K | Pagamentos semanais | 24h |
| CP_SALDO_2026 | 10.2K | Saldo de divida | 24h |
| AD_v3 | 5K | Adiantamentos | 24h |
| INFLACAO | 115.2K | Variação PMP | 24h |
| PMP_ID_INF_12 | 16.3K | Série PMP 12m por ID | 24h |
| PMP_PROD_INF_12 | 6.3K | Série PMP 12m por produto | 24h |
| CURVA ABC FORN | 3.5K | Curva fornecedor | 24h |
| CURVA ID | 13K | Curva ID/produto | 24h |
| CURVA PROD | 6K | Curva produto | 24h |
| FILIAIS_SUPPLY | 101 | Dimensão filial | 168h |
| TAB_PROD | 6.8K | Dimensão produto | 168h |

---

## 2. Mapa de Campos por Fonte

### NFE (239.9K linhas — fato principal)
```
Chaves:     ID, MESANO, CDFORNECED_OFICIAL
Valores:    TOTAL, VLRUNITPOND, VLRUNITPOND_EST, QTDE_EST
Análise:    CURVA_PROD, CURVA_ID, CURVA_FORN (curvas no momento da compra)
Preço:      PMP_PROD, PMP_ID (série 1/3/6/12 meses)
Impacto:    IMP_COT, IMP_ID, PRE_MIN_COT, FORN_MIN_COT
Inflação:   INF_ID_1, INF_ID_PMP, INF_PROD_1, INF_PROD_PMP
Dimensões:  CAT1-CAT5, NMPRODUTO_OFICIAL, FANTASIA_OFICIAL, CDFILIAL, UF, ANO
ATENÇÃO:    DTENTRADA e DTEMISSAO NÃO existem aqui — estão em NF COM ITENS
```

### NF COM ITENS - CONSOLIDADO (122K linhas)
```
Chaves:     ID, MESANO, NRNOTA, CHAVE (identificação única da nota)
Valores:    TOTAL, VLRUNIT, QTDE_EST
Datas:      DTENTRADA, DTEMISSAO (presentes aqui — não na NFE!)
Dimensões:  NEGOCIO, LOCAL, SIGLA (filial via CODFILIAL join)
Uso:        Quando precisar de número de nota, data exata, chave NFe
```

### COT (164.1K linhas)
```
Chaves:     ID, MESANO, CDFORNECED, MARCA (00001 = cotação padrão)
Preço:      PRECOUNIT, PRECOUNIT_EST
Curvas:     CURVA_PROD, CURVA_ID, CURVA_FORN (status por mês)
Vazios OK:  CDFORMPGTO, NMFORMPGTO (fornecedor não sempre informa)
ATENÇÃO:    NMPRODUTO_OFICIAL não está aqui — fazer JOIN via ID em outra fonte
```

### COT_MIN_FORN (68K linhas)
```
Chaves:     ID, MESANO
Resultado:  FORNE_FANTASIA, PRECOUNIT_COT, PRIORIDADE
Equivale a: GROUP BY ID, MESANO ORDER BY PRECOUNIT_COT LIMIT 1 na COT
Uso:        Comparação direta de preço pago vs menor cotado
```

### NUM_COT (68.2K linhas)
```
Chaves:     ID, MESANO
Contagem:   QTD_COT, MIN_COT, MED_COT, MAX_COT
Fornecedor: FORN_MENOR_PRECO, CNPJ_MENOR_PRECO (não existem na COT base!)
Rank:       POS_FORN, CURVA_FORN (do fornecedor do menor preço)
```

### CP — Contas a Pagar (118.3K linhas)
```
Chaves:     CDFORNECED, CDTPCTPAGAR, NRNOTAFISC
Status:     STATUSPAG = 'Baixado' ou 'Em Aberto' (NÃO 'ABERTO'/'PAGO'!)
            STATUS_VENC = 'Vencido' ou 'A Vencer'
            FAIXA_DIAS = faixas de vencimento
Datas:      DTEMISSAO, DTORIGVENPAG, DTATUAVENPAG, DTBAIXAPAG
Valores:    VRORIGPAG, VRATUAPAG, VRBAIXAPAG
```

### CP_SEMANA (46K linhas)
```
ATENÇÃO:    Colunas usam prefixo "T." — ex: "T.FORNECEDOR", "T.ANO"
            Exige aspas duplas: "T.FORNECEDOR"
Campos:     T.FORNECEDOR, T.ANO, T.SEMANA_ANO
Valores:    VALOR_PAGO_SEMANA, VALOR_VENCIMENTOS_SEMANA, VALOR_VENCIDO_SEMANA
```

### AD_v3 — Adiantamentos (5K linhas)
```
Chaves:     ANO, MES_ENTRADA, MES_PGTO, NMEMP, CDFORNECED, CDPRODESTO
Status:     STATUS_CONCILIACAO = 'CONCILIADO' ou 'ADIANTAMENTO ?'
            (com ponto de interrogação — nunca 'PENDENTE'!)
Valor:      VALOR_FINAL, E.QTDE_EST
```

### INFLACAO (115.2K linhas)
```
Chaves:     ID, MESANO
Dimensões:  UF, NMEMP, CAT1-CAT5, NMPRODUTO_EST, CDPRODUTO_OFICIAL, ANO
Curvas:     CURVA_ID + POS_ID  (por empresa+UF+produto)
            CURVA_PROD + POS_PROD  (produto nacional — novo 2026-06)
PMP:        PMP_ID, PMP_ID_1, PMP_PROD, PMP_PROD_1
Inflação R$: SOMA_INF_ID_1, SOMA_INF_ID_PMP, SOMA_INF_PROD_1, SOMA_INF_PROD_PMP
Inflação %:  PERC_INF_ID_1, PERC_INF_ID_PMP, PERC_INF_PROD_1, PERC_INF_PROD_PMP
ATENÇÃO:    Campos frequentemente NULL — usar IS NULL / IS NOT NULL
ATENÇÃO:    NMPRODUTO_OFICIAL não existe aqui — usar NMPRODUTO_EST
```

### PMP_ID_INF_12 e PMP_PROD_INF_12
```
Série:      PMP_1, PMP_2, ..., PMP_12 (PMP_1 = mais recente)
ATENÇÃO:    PMP_0 SEMPRE VAZIO — nunca usar! Usar PMP_1 como valor atual.
```

### CURVA ID - TODAS (13K linhas)
```
ATENÇÃO CRÍTICA: Coluna chave se chama "TE.ID" (com ponto!)
                 Exige aspas duplas: "TE.ID"
                 Nunca use apenas "ID" nessa fonte — não funciona!
Campos:     "TE.ID", CURVA, POS
```

### FILIAIS_SUPPLY (101 linhas — dimensão)
```
Chaves:     CDFILIAL
Empresa:    EMPRESA, S_EMP = RC | ME | SU
Localização: LOCAL, SIGLA, REGIAO
Negócio:    NEGOCIO = CD | COZINHA | ESCOLA | HOSPITAL | MERENDA | PRESIDIO | MATRIZ
Status:     ATIVA = 'Yes' ou 'No'
Uso:        JOIN obrigatório para adicionar contexto de filial, UF, negócio
```

---

## 3. Relacionamentos e Padrões de JOIN

```
NFE / NF COM ITENS
  ├─ LEFT JOIN COT           ON "ID" = "ID" AND "MESANO" = "MESANO"
  ├─ LEFT JOIN COT_MIN_FORN  ON "ID" = "ID" AND "MESANO" = "MESANO"
  ├─ LEFT JOIN CURVA ID      ON "ID" = "TE.ID"  ← CUIDADO com o nome!
  ├─ LEFT JOIN INFLACAO       ON "ID" = "ID" AND "MESANO" = "MESANO"
  ├─ LEFT JOIN PMP_ID_INF_12  ON "ID" = "ID" AND "MESANO" = "MESANO"
  ├─ LEFT JOIN FILIAIS_SUPPLY ON "CDFILIAL" = "CDFILIAL"
  └─ LEFT JOIN CURVA ABC FORN ON "CDFORNECED_OFICIAL" = "CDFORNECED"

CP
  ├─ LEFT JOIN FILIAIS_SUPPLY ON "CDFILIAL" = "CDFILIAL"
  ├─ LEFT JOIN CP_SEMANA      ON "T.FORNECEDOR" = "CDFORNECED" AND "T.ANO" = "ANO"
  └─ LEFT JOIN CURVA ABC FORN ON "CDFORNECED" = "CDFORNECED"

AD_v3
  ├─ LEFT JOIN FILIAIS_SUPPLY ON "CDFILIAL" = "CDFILIAL"
  └─ (NFE linkado por NMEMP + CDFORNECED — sem chave direta)
```

---

## 4. Campos Problemáticos e Anti-padrões

| Campo | Tabela | Problema | Solução correta |
|---|---|---|---|
| `STATUSPAG` | CP | Valores reais: 'Baixado', 'Em Aberto' | NÃO use 'ABERTO' ou 'PAGO' |
| `STATUS_CONCILIACAO` | AD_v3 | Pode ser 'ADIANTAMENTO ?' (com ?) | Usar valor exato com interrogação |
| `PRE_MIN_COT` | NFE | NULL quando sem cotação | IS NULL / IS NOT NULL |
| `IMP_COT` | NFE | NULL sem cotação; negativo = economia | Filtrar > 0 para oportunidades |
| `NMPRODUTO_OFICIAL` | NFE | Contém 'MUTUO', 'DEVOLUCAO' | Filtrar NOT LIKE '%MUTUO%' para spend real |
| `CAT2` | NFE | 'D5 - SERVICOS' = lançamentos financeiros | Separar de insumos operacionais |
| `PMP_0` | PMP_*_INF_12 | SEMPRE vazio/NULL | Usar PMP_1 (mais recente), PMP_12 (mais antigo) |
| `TE.ID` | CURVA ID | Nome de coluna com ponto | Sempre com aspas: "TE.ID" |
| `T.FORNECEDOR` | CP_SEMANA | Prefixo T. no nome | Sempre com aspas: "T.FORNECEDOR" |
| `MESANO` | Todos | Formato 'YYYY/MM' | LIKE '2025/%' para ano; = '2025/06' para mês |

---

## 5. Erros Identificados no Prompt v1

1. **Status CP errado** — `STATUSPAG` documentado como 'ABERTO'/'PAGO'. Valores reais: 'Baixado' / 'Em Aberto'
2. **`ORDER BY "POS"`** na query de curva ABC — coluna POS não existe em `CURVA ABC FORN - TOTAL`
3. **`STATUS_CONCILIACAO`** — prompt não documenta o valor 'ADIANTAMENTO ?' (com ponto de interrogação)
4. **`TE.ID`** — coluna da CURVA ID não mencionada; gera erro quando consultada sem aspas
5. **`PMP_0`** — documentado como série mas sempre vazio; induz a usar campo inválido

---

## 6. Valores de Referência por Campo

### Curva ABC
```
CURVA_FORN / CURVA_ID / CURVA_PROD:
  AAA = top 50% do gasto
  AA  = 50-65%
  A   = 65-80%
  B   = 80-90%
  BB  = 90-95%
  C   = 95-99%
  CC  = 99-99,5%
  CCC = 99,5-100% (cauda longa)
```

### Empresas (S_EMP / NMEMP)
```
RC = Ideal (Rede de compras principal)
ME = Melhor
SU = Supera / PV / Pomme Vita
```

### Negócios (NEGOCIO em FILIAIS_SUPPLY)
```
CD       = Centro de Distribuição
COZINHA  = Cozinha industrial
ESCOLA   = Escola/educação
HOSPITAL = Hospitalar
MERENDA  = Merenda escolar
PRESIDIO = Presídio/penitenciária
MATRIZ   = Matriz (excluir de análises operacionais)
```

### Status CP
```
STATUSPAG:  'Em Aberto' | 'Baixado'
STATUS_VENC: 'A Vencer' | 'Vencido'
FAIXA_DIAS: VE_1_30 | VE_31_60 | VE_61_90 | VE_91_120 | VE_121_180 | VE_181_MAIS
            AV_1_30 | AV_31_60 | AV_61_90 | AV_91_120 | AV_121_MAIS
```

### Status Adiantamento
```
STATUS_CONCILIACAO: 'CONCILIADO' | 'ADIANTAMENTO ?'
```

---

## 7. Filtros Obrigatórios por Análise

| Análise | Filtro necessário | Motivo |
|---|---|---|
| Spend operacional | `"CAT2" != 'D5 - SERVICOS'` ou `NOT LIKE 'D%'` | Excluir lançamentos financeiros |
| Spend real | `"NMPRODUTO_OFICIAL" NOT LIKE '%MUTUO%'` | Excluir mútuo e devoluções |
| Excluir Matriz | `"FI.NEGOCIO" <> '_MATRIZ'` | Não é operação real |
| CP em aberto | `"STATUSPAG" = 'Em Aberto'` | NÃO usar 'ABERTO' |
| AD pendente | `"STATUS_CONCILIACAO" = 'ADIANTAMENTO ?'` | Com ponto de interrogação |
| Oportunidade cotação | `"IMP_COT" > 0` | NULL = sem cotação, negativo = economia |
| PMP atual | `"PMP_1" IS NOT NULL` | PMP_0 sempre vazio |
| Inflação relevante | `"PERC_INF_ID_PMP" IS NOT NULL` | Muitos NULLs na fonte |
| Filiais ativas | `"ATIVA" = 'Yes'` | Excluir filiais desativadas |
