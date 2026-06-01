# Hierarquia de Categorias — BI de Suprimentos

Categorias de compras organizadas em 3 grupos principais, nesta ordem obrigatória nos filtros: **I → D → A**.

Filtros em cascata: CAT1 → CAT2 → CAT3 → CAT4 → CAT5 (do mais amplo ao mais específico).

---

## Estrutura de CAT1 (nível mais amplo)

### I — INSUMOS

| CAT1 | Descrição |
|---|---|
| I0 | NUTRICIONAIS |
| I1 | ESTOCÁVEIS |
| I2 | PERECÍVEIS |
| I3 | HORTIFRUTI |
| I4 | DESCARTÁVEIS |
| I5 | LIMPEZA |
| I6 | GÁS |

### D — DESPESAS

| CAT1 | Descrição |
|---|---|
| D1 | VESTUÁRIOS/EPIs |
| D2 | ESCRITÓRIO |
| D3 | MANUTENÇÃO |
| D4 | CONSTRUÇÃO |
| D5 | SERVIÇOS |
| D6 | COMPRA A VISTA |
| D7 | CESTA BÁSICA / COMODATO |
| D8 | UTENSÍLIOS |

### A — ATIVOS

| CAT1 | Descrição |
|---|---|
| A1 | ATIVOS DIRETOS |
| A2 | ATIVOS INDIRETOS |

---

## Detalhamento por CAT1 (CAT2)

### I0 — NUTRICIONAIS
I001 · NUTRICIONAIS / I003 · FRASCO NUTRI ENTERAL

### I1 — ESTOCÁVEIS
I101 · NUTRICIONAIS / I102 · CEREAIS / I103 · FARINÁCEOS / I104 · PANIFICAÇÃO / I105 · FORMULADOS / I106 · BEBIDAS / I107 · MATINAIS / I108 · DOCES/SOBREMESA / I109 · LÁCTEOS / I110 · CONSERVAS / I111 · GORDURAS / I112 · EVENTOS / I113 · CESTAS

### I2 — PERECÍVEIS
I201 · CARNES / I202 · FRIOS/EMBUTIDOS / I203 · LATICÍNIOS / I204 · MASSAS FRESCAS / I205 · HORTIS CONGELADOS / I206 · PROCESSADOS CONGELADOS / I207 · SALGADOS CONGELADOS / I208 · CARNES ORGÂNICAS

### I3 — HORTIFRUTI
I301 · IN NATURA / I302 · PROCESSADOS / I303 · ORGÂNICOS / HORTI PE

### I4 — DESCARTÁVEIS
I401 · ALUMÍNIO / I402 · PAPEL / I403 · PLÁSTICO / I404 · MADEIRA/GARRAFAS

### I5 — LIMPEZA
I501 · ACESSÓRIOS E UTENSÍLIOS / I502 · HIGIENE / I503 · LÍQUIDOS

### I6 — GÁS
I601 · GÁS / I602 · CILINDRO

---

### D1 — VESTUÁRIOS/EPIs
D101 · VESTUÁRIO / D102 · EPI

### D2 — ESCRITÓRIO
D201 · ESCRITÓRIO / D202 · PAPEL / D203 · ORGANIZAÇÃO

### D3 — MANUTENÇÃO
D301 · FERRAMENTAS / D302 · MATERIAL PARA MANUTENÇÃO / D303 · FERRAGENS / D304 · PEÇAS / D305 · VEÍCULOS / D306 · FILTROS/JARDINAGEM

### D4 — CONSTRUÇÃO
D401 · MATERIAIS DE CONSTRUÇÃO / D402 · ELÉTRICA / D403 · HIDRÁULICA / D404 · ACABAMENTOS

### D5 — SERVIÇOS
D501 · SERVIÇOS (ALUGUEL, TI, VIAGEM, PESSOAL, ENERGIA, TRANSPORTE, etc.)

### D6 — COMPRA A VISTA
D601 · INSUMOS

### D7 — CESTA BÁSICA / COMODATO
D701 · ESTOCÁVEIS / D702 · PERECÍVEIS / D704 · DESCARTÁVEIS / D7 COMODATO · DISPENSER

### D8 — UTENSÍLIOS
D801 · UTENSÍLIOS COZINHA

---

### A1 — ATIVOS DIRETOS
A101 · EQUIPAMENTOS PARA COZINHA / A102 · MÓVEIS PARA COZINHA / A103 · UTENSÍLIOS PARA COZINHA / A104 · EQUIPAMENTOS AUXILIARES / A105 · EQUIPAMENTOS INFORMÁTICA / A106 · ESCRITÓRIO

### A2 — ATIVOS INDIRETOS
A201 · MÓVEIS PARA ESCRITÓRIO / A202 · EQUIPAMENTOS PARA ESCRITÓRIO / A203 · CARROS

---

## Regra de ordenação

Sempre ordenar por código crescente dentro de cada grupo:
- I: I0, I1, I2, I3, I4, I5, I6
- D: D1, D2, D3, D4, D5, D6, D7, D8
- A: A1, A2

Nunca misturar a ordem I/D/A nos filtros ou relatórios.

---

## Nota sobre a hierarquia completa

A hierarquia tem até 5 níveis (CAT1 → CAT5) com centenas de subcategorias específicas. Os arquivos de referência com a hierarquia completa estão nos docs de design originais do projeto. Para implementação dos filtros em cascata, os valores reais de CAT1 a CAT5 vêm dos dados do Zoho (`NFE`, `COT`, etc.) — não é necessário hardcodar todos os valores.
