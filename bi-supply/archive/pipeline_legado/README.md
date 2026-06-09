# Pipeline Legado — Arquivado em 2026-06-09

Estes scripts faziam parte do pipeline original de extração e transformação.
Foram substituídos pelo caminho NL-SQL (elements.json + refresh_elements.py).

## Por que foram aposentados

O Zoho Analytics já mantém todos os cálculos nas suas views:
- `CURVA ABC FORN`, `CURVA ID`, `CURVA PROD` — curvas ABC pré-calculadas
- `PMP_ID_INF_12`, `INFLAÇÃO` — PMP e inflação pré-calculados
- `NFE` já tem `IMP_COT`, `PRE_MIN_COT`, `FORN_MIN_COT` calculados

Não havia razão para recalcular em Python o que o Zoho já faz.

## Novo pipeline (3 passos)

```
refresh_elements.py  → executa 139 SQLs no Zoho → elements.json
generate_indexes.py  → posicionamento no grid → 00_index.json
build.py             → HTML 100% SQL → dist/index.html
```

## Recovery

Para restaurar o pipeline antigo:
```
git checkout v-pre-migration -- bi-supply/pipeline/extract.py
git checkout v-pre-migration -- bi-supply/pipeline/transform.py
```
