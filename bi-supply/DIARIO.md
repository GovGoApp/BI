# Diário de Bordo — BI de Suprimentos

Registro técnico de todas as alterações do projeto, em ordem cronológica (mais antigo → mais recente).

**Regras:**
- Atualizar este diário a cada alteração relevante, sempre com data e detalhes técnicos.
- Atualizar o README somente quando a estrutura geral ou o uso do projeto mudar.
- Nunca deixar uma sessão de trabalho sem registrar o que foi feito.

---

## [2026-06-01] Fundação do projeto bi-supply

### O que foi feito

Projeto criado do zero na pasta `bi-supply`, substituindo a estrutura anterior em `supply` que tinha problemas de organização e arquitetura.

### Motivação

O projeto anterior (`supply`) foi desenvolvido com outra ferramenta e não respeitou os princípios de design definidos no `BI Design System.html` e no mock `BI Suprimentos v4.html`. A organização de pastas era confusa, os scripts misturavam responsabilidades e a documentação era inconsistente.

### Estrutura criada

```
bi-supply/
├── README.md
├── DIARIO.md
├── zoho/zoho.env          ← credenciais existentes
├── zoho/zoho.env.example  ← template
├── pipeline/              ← pasta para extract, transform, build
├── data/raw/              ← dados brutos do Zoho
├── data/processed/        ← métricas calculadas
├── dashboard/tabs/        ← configs YAML por aba
├── dashboard/templates/   ← templates HTML por tipo
├── dashboard/static/      ← CSS e JS
├── nlsql/                 ← módulo NL-SQL
├── tests/zoho/
├── tests/pipeline/
├── tests/nlsql/
├── tests/dashboard/
├── docs/projeto/
├── docs/dados/
├── docs/design/
├── docs/zoho/
└── dist/
```

### Arquivos de design preservados

- `design/BI Design System.html` — fonte da verdade visual (não modificar)
- `design/BI Suprimentos v4.html` — mock de referência com as 15 abas definitivas

### Abas definidas (v4)

Lidas diretamente do HTML do mock v4:

| data-page | Label |
|---|---|
| resumo | Resumo |
| oportunidades | Oportunidades |
| categorias | Categorias |
| filiais | Filiais |
| estoque | Estoque |
| forn360 | Fornecedor |
| produtos | Produtos |
| cotacoes | Cotações |
| impacto | Impacto |
| inflacao | Inflação |
| fiscal | Fiscal |
| financeiro | Financeiro |
| adiantamentos | Adiantamentos |
| servicos | Serviços |
| qualidade | Dados |

### Docs migrados do projeto supply

| Origem | Destino |
|---|---|
| `supply/docs/ESTUDO_ZOHO_ANALYTICS_API.md` | `docs/zoho/ESTUDO_API.md` |
| `supply/docs/INVENTARIO_ZOHO_ANALYTICS_WORKSPACES.md` | `docs/zoho/INVENTARIO_WORKSPACES.md` |
| `supply/docs/PERFIL_DADOS_SUPRIMENTOS.md` | `docs/dados/PERFIL_FONTES.md` |
| `supply/docs/ESTUDO_SUPRIMENTOS_BI_E_FERRAMENTAS.md` | `docs/dados/ESTUDO_DOMINIOS.md` |
| `supply/docs/claude_design/01_BRIEFING.md` | `docs/projeto/BRIEFING.md` |
| `supply/docs/claude_design/05_DADOS_E_DOMINIOS.md` | `docs/dados/DOMINIOS_NEGOCIO.md` |
| `CATEGORIAS_I_D_ORDENADAS.md` + `CATEGORIAS_I_D_A_ORDENADAS.md` | `docs/dados/CATEGORIAS.md` (merge) |
| `ANALISE_AUDITORIA_BI_SUPRIMENTOS_V3.md` | `docs/design/COBERTURA_ABAS.md` |
| `PROMPT_CORRECAO_V3_CLAUDE_DESIGN.md` | `docs/design/ESPECIFICACAO_ABAS.md` |

### Docs descartados do supply

Não migrados por serem prompts para Claude Design (não são documentação do projeto), versões desatualizadas, ou ponteiros para arquivos que não existem mais.

### Docs criados do zero

- `docs/projeto/ARQUITETURA.md` — arquitetura técnica atual (3 camadas + NL-SQL)
- `docs/design/MAPA_ABAS.md` — mapa das 15 abas baseado no v4.html
- `docs/design/CRITERIOS_ACEITACAO.md` — critérios para validar o dashboard

### Decisões técnicas registradas

1. **Dados embutidos no HTML**: os dados processados são embutidos como JSON dentro do `dist/index.html`. O dashboard funciona offline e pode ser distribuído sem arquivos externos.

2. **Pipeline separado em 3 etapas**: extract → transform → build. Cada etapa tem responsabilidade única e pode rodar independentemente.

3. **Snapshot local**: os dados são exportados do Zoho periodicamente (não em tempo real). A execução de `extract.py` atualiza os snapshots em `data/raw/`.

4. **YAML simples por aba**: cada aba tem um `.yml` em `dashboard/tabs/` que declara fontes, filtros e elementos. O YAML não reinventa o CSS — os estilos vêm do Design System.

5. **Módulo NL-SQL**: baseado no padrão de tool calls com LLM (guia `GUIA_IMPLEMENTACAO_MODO_RELATORIO_NL_SQL.md`). Permite fazer perguntas em português que viram SQL executado no Zoho. Ficará em `nlsql/`.

### Fase 0 concluída — Próximos passos

- [x] Reescrever `zoho/client.py`
- [ ] Criar `zoho/catalog.py`
- [ ] Criar testes de catalog

---

---

## [2026-06-01] Fase 1 — Passo 1: zoho/client.py

**Commit:** `f94ecaf`

### O que foi feito

Reescrita limpa do cliente Zoho Analytics API v2, portado de `supply/scripts/zoho_analytics_client.py` para `bi-supply/zoho/client.py`.

### Arquivo: `zoho/client.py` (≈270 linhas)

**Estruturas principais:**

```
load_env_file(path)         ← lê .env e injeta em os.environ
ZohoConfig                  ← dataclass frozen com credenciais
  .from_env(require_workspace=True)
ZohoClient(config, session, timeout)
  .refresh_token()          ← POST /oauth/v2/token → access_token
  .exchange_code(...)       ← troca authorization code por refresh_token (static)
  .get_orgs(token)          ← GET /restapi/v2/orgs
  .get_workspaces(token)    ← GET /restapi/v2/workspaces
  .get_views(token, keyword)← GET /restapi/v2/workspaces/{ws}/views
  .export_view(...)         ← exportação síncrona (views pequenas)
  .create_job_view(...)     ← cria job bulk assíncrono por view_id
  .create_job_sql(...)      ← cria job bulk assíncrono por SQL SELECT
  .job_status(job_id, token)← consulta status do job
  .wait_job(job_id, token, interval, max_attempts) ← polling com progresso
  .download_job(job_id, out, token) ← baixa o arquivo do job concluído
ZohoError(RuntimeError)     ← erro da API ou resposta inesperada
```

**Melhorias em relação ao código anterior:**

| Antes | Depois |
|---|---|
| `from_env()` + `from_env_for_discovery()` (dois métodos) | `from_env(require_workspace=False)` (um método com flag) |
| `session.request("GET", ...)` para tudo | `session.get(...)` / `session.post(...)` — mais idiomático |
| Nenhum feedback durante polling | Imprime progresso: `Aguardando job ... tentativa N/60` |
| `views` mostrava só primeiros 20 | `--limit N` (padrão 50, `--limit 0` = todas) |
| Nome `ZohoAnalyticsError` | `ZohoError` — mais curto |

**CLI disponível:**

```powershell
python zoho/client.py --env-file zoho/zoho.env token
python zoho/client.py --env-file zoho/zoho.env orgs
python zoho/client.py --env-file zoho/zoho.env workspaces
python zoho/client.py --env-file zoho/zoho.env views [--keyword NFE] [--limit 0]
python zoho/client.py --env-file zoho/zoho.env exchange-code --code CODIGO
python zoho/client.py --env-file zoho/zoho.env export-view --view-id ID --out arquivo.csv [--async --wait]
python zoho/client.py --env-file zoho/zoho.env export-sql --sql "select..." --out arquivo.csv --wait
python zoho/client.py --env-file zoho/zoho.env job-status --job-id ID
python zoho/client.py --env-file zoho/zoho.env download-job --job-id ID --out arquivo.csv
```

### Arquivo: `tests/zoho/test_client.py` (≈230 linhas)

**23 testes unitários — todos passando — sem chamadas reais à API.**

Organização:

| Classe | Testes | O que cobre |
|---|---|---|
| `TestZohoConfig` | 5 | `load_env_file`, `from_env` com e sem workspace, URLs customizadas |
| `TestZohoClientAuth` | 3 | `refresh_token`, `exchange_code`, erro sem access_token |
| `TestZohoClientDiscovery` | 4 | `get_orgs`, `get_workspaces`, `get_views` com e sem keyword |
| `TestZohoClientBulk` | 8 | `create_job_view`, `create_job_sql`, `job_status`, `wait_job` (sucesso/falha/timeout), `download_job` |
| `TestZohoClientErros` | 3 | failure response, HTTP 4xx, jobId ausente |

**Infraestrutura de teste:**
- `FakeResponse` — simula `requests.Response` com `status_code`, `content`, `json()`
- `FakeSession` — devolve respostas pré-configuradas em sequência, registra todas as chamadas em `session.calls` para assertivas de URL e headers

### Fase 1 concluída

- [x] Reescrever `zoho/client.py`
- [x] Criar `zoho/inventario.py`
- [x] Criar `zoho/catalog.py` + 20 testes
- [x] 43 testes totais passando

---

---

## [2026-06-01] Fase 2 — Passo 1: pipeline/extract.py

**Commit:** a registrar

### O que foi feito

Criação do pipeline de extração de dados do Zoho para `data/raw/`.

### Arquivos criados

**`pipeline/sources.yml`** — declara as 18 fontes a extrair:
- `id`: identificador local (ex: `nfe`, `cot`, `cp`)
- `zoho_name`: nome exato no Zoho (ex: `NFE`, `INFLACAO`)
- `description`: o que a fonte representa
- `abas`: quais abas do dashboard consomem essa fonte
- `max_age_hours`: frequência de atualização (padrão 24h; dimensões como FILIAIS usam 168h = 7 dias)

**`pipeline/extract.py`** — script de extração:
- Lê `sources.yml` e `data/raw/manifest.json`
- Pula fontes com extração recente — **lógica incremental** com `max_age_hours`
- `--force`: ignora cache e baixa tudo
- `--source ID`: extrai só uma fonte específica
- `--max-age N`: override do tempo de cache
- Processa em lotes de 4 jobs simultâneos via Bulk API assíncrona
- Grava `data/raw/manifest.json` com status, linhas e timestamp de cada extração

### Teste executado

```
python pipeline/extract.py --env-file zoho/zoho.env --source filiais
  -> 101 linhas, 12 colunas, manifest atualizado

python pipeline/extract.py --env-file zoho/zoho.env --source filiais
  -> "Pulando 1 fontes atualizadas: filiais" (cache funcionando)
```

### Decisões de arquitetura

1. **Opção A (manual)** por agora — sem agendamento automático
2. **Deploy futuro no Render** com cron job — a lógica incremental já está preparada
3. O `sources.yml` é a única fonte de verdade sobre o que extrair — nomes de fontes não estão hardcoded no script

### Estratégia de atualização dos dados

Decisão registrada em 2026-06-01.

As 18 fontes foram classificadas em 4 grupos com frequências diferentes:

| Grupo | Fontes | max_age_hours | Motivo |
|---|---|---:|---|
| Transacionais | `nfe`, `nf_com_itens`, `cot` | 24h | Novas linhas chegam todo dia |
| Status mutável | `cp`, `cp_*`, `ad_v3`, `cot_min_forn`, `num_cot` | 24h | Linhas mudam de ABERTO→PAGO, PENDENTE→CONCILIADO |
| Recalculadas | `inflacao`, `pmp_*`, `curva_*` | 24h | O Zoho recalcula rankings/PMP — não existe delta |
| Dimensões estáticas | `filiais`, `tab_prod` | 168h | Raramente mudam — atualização semanal |

**Estratégia adotada: full replace com frequências diferenciadas.**

Incremental não vale a pena agora porque:
1. Os grupos "status mutável" e "recalculadas" precisam de full replace de qualquer forma
2. NFE com 177 MB é rápido de baixar diariamente
3. Incremental adicionaria complexidade (rastrear última data, merge de arquivos, tratar correções retroativas)
4. Para Render + cron, ~500 MB/dia é totalmente viável

### Próximos passos

- [x] Rodar extração completa das 18 fontes
- [ ] Criar `pipeline/transform.py`

---

---

## [2026-06-01] Fase 1 — Passo 2: inventário completo e perfil de fontes

**Commits:** a registrar

### O que foi feito

Geração ao vivo — diretamente do Zoho Analytics — de dois documentos reconstruídos do zero:
- `docs/zoho/INVENTARIO_WORKSPACES.md` — todos os 10 workspaces e 561 views em UTF-8 limpo
- `docs/dados/PERFIL_FONTES.md` — 51/53 fontes do SUPRIMENTOS com colunas, tipos inferidos e amostra de 5 linhas

Arquivos de dados gerados (gitignored):
- `data/raw/zoho_inventory.json` — inventário bruto JSON
- `data/raw/suprimentos_profile.json` — perfil JSON
- `data/raw/samples/{fonte}.csv` — amostra CSV de cada fonte

### Problema corrigido

`INVENTARIO_WORKSPACES.md` anterior (de 27/05) tinha caracteres corrompidos (`TOP DEFLA�O`).
Causa: arquivo gerado em Windows-1252. Novo documento usa `open(..., encoding="utf-8")` explicitamente.

### Arquivos criados

**`zoho/inventario.py`** — script utilitário (rodar uma vez):
- `get_all_workspaces()` — itera todos os workspaces via API, coleta views de cada um
- `profile_view()` — executa `select * from "VIEW" limit 5` via Bulk API assíncrona
- `build_inventario_md()` — gera o markdown do inventário
- `build_perfil_md()` — gera o markdown do perfil com colunas e tipos inferidos
- `infer_type()` — infere tipo (inteiro/decimal/texto/vazio) a partir dos valores de amostra

**`zoho/client.py`** — atualização pequena:
- `get_views()` agora aceita `workspace_id` opcional — permite listar views de qualquer workspace

### Resultado do profiling (53 fontes)

| Resultado | Fontes |
|---|---:|
| OK | 51 |
| Erro (sem amostra) | 2 |

Erros: `ADIANTAMENTO_NFE` e `TODAS - CONTAS A PAGAR` — a investigar.

### Descobertas principais da análise

**1. QueryTables consolidadas adicionam enrichment — não são só UNION:**

| Fonte | Cols | Extra (não existe na por-empresa) |
|---|---:|---|
| `NFE - IDEAL/MELHOR/SUPERA` | 25 | — |
| `NFE` | 63 | CURVA_*, PMP_*, IMP_*, INF_*, FI.* |
| `COT - IDEAL/MELHOR/SUPERA` | 25 | — |
| `COT` | 32 | CURVA_PROD, CURVA_FORN, CURVA_ID |
| `NF COM ITENS - IDEAL/ME/SU` | 29 | — |
| `NF COM ITENS - CONSOLIDADO` | 47 | Mais dimensões de produto e filial |

**2. Redundâncias confirmadas e descartadas:**

| Descartar | Usar em vez |
|---|---|
| `NFE - IDEAL/MELHOR/SUPERA` | `NFE` |
| `COT - IDEAL/MELHOR/SUPERA` | `COT` |
| `NF COM ITENS - IDEAL/ME/SU` | `NF COM ITENS - CONSOLIDADO` |
| `CURVA PROD - IDEAL/MELHOR/SUPERA` | `CURVA PROD - TODAS` |
| `AD_v1`, `AD_v2` (11 cols) | `AD_v3` (16 cols, tem UF/filial/cat/status) |
| `PMP_ID`, `PMP_ID_INF` | `PMP_ID_INF_12` (22 cols) |
| `PMP_PROD`, `PMP_PROD_INF` | `PMP_PROD_INF_12` (21 cols) |
| `CP_SALDO_2025`, `CP_SALDO_2026` | `CP_SALDO_2026_v2` |
| `ENTRADA DE NOTAS - [TODAS]` (42 cols) | `NFE` (63 cols, superconjunto) |
| `CURVA FORN - TODAS` (6 cols, sem nome) | `CURVA ABC FORN - TOTAL` (7 cols, tem `RAZAO_SOCIAL`) |
| `FORN_CP_25_26` (1 col, corrompida) | — (descartar) |
| `TODAS - CONTAS A PAGAR` (erro) | `CP` |
| `FILIAIS/FILIAIS_DRO/FILIAIS_NEW` | `FILIAIS_SUPPLY` |
| `[RC] COTAÇÃO DE PREÇOS - OLD` | — (obsoleta) |

**3. Lista golden — 19 fontes para o BI:**

NFE · NF COM ITENS - CONSOLIDADO · COT · COT_MIN_FORN · NUM_COT ·
CURVA ABC FORN - TOTAL · CURVA ID - TODAS · CURVA PROD - TODAS ·
INFLAÇÃO · PMP_ID_INF_12 · PMP_PROD_INF_12 ·
CP · CP_MOV · CP_SEMANA · CP_SALDO_2026_v2 ·
AD_v3 · FILIAIS_SUPPLY · TAB_PROD · FAT_SUP


---

---

## [2026-06-02] Fase 3 — Sistema unificado de elementos (passos 1-3)

### Abordagem correta do build.py
O build.py usa design/BI Suprimentos v4.html como template base.
Substitui apenas arrays JS mockados. Estrutura HTML/CSS/JS: 100% intacta.

### Auditoria (pipeline/audit_elements.py)
87 acoes: 38 conectar, 27 criar+conectar, 22 adicionar ao v4, 1 rule-based.

### Sistema unificado definido
Grid: 16 colunas x 40px por row_span.
Cada elemento: id, variavel_js, tipo, dados, config, layout.
layout.origem = v4 -> posicionado no grid.
layout.origem = processed -> sem posicao, painel lateral do editor.
variavel_js = nome da constante JS que build.py injeta.

### pipeline/generate_indexes.py
Gera os 15 00_index.json completos:
136 elementos total: 114 com layout (v4) + 22 sem posicao (processed).

### Decisoes tecnicas
1. Grid 16 colunas x 40px fixo (ajustavel pelo usuario depois)
2. Elementos Tipo B (visivel:false) -> painel lateral do editor
3. Ciclo: editar no browser -> salvar layout.json -> build.py -> HTML novo
4. v4.html nao modificado — adaptacoes injetadas pelo build.py

---

---

## [2026-06-02] Fase 3 — Passos 4-5: build.py unificado + renderer CSS Grid

**Commits:** `bb5a656`, `9512f5b`, `b6795a5`

### pipeline/build.py (≈660 linhas)

Pipeline de build completo com injeção de dados reais:

1. Lê `design/BI Suprimentos v4.html` como template base (nunca modificado)
2. Carrega todos os `00_index.json` de `data/processed/`
3. Substitui arrays mockados do v4 (`FORN`, `PRODS`, `OPP`, `FILIAIS`, `CAT_VAL`, `CAT_INF`) com dados reais
4. Injeta `window._BI_DATA[variavel_js] = dados` para cada elemento (registry global)
5. Injeta `const ABAS_INDEX = {...}` com config completa de layout de todas as abas
6. Injeta CSS do grid e renderer JS
7. Salva `dist/index.html`

**Decisão arquitetural:** usar `window._BI_DATA[key]` em vez de `const NOME = ...` porque constantes JS não se anexam ao `window`, tornando impossível o acesso dinâmico por nome no renderer.

**Limites por tipo** para controlar tamanho do HTML:

| Tipo | Limite |
|---|---:|
| GL, HL | 50, 20 linhas |
| GB, GE | 24 linhas |
| T | 50 linhas |
| TE | 100 linhas |
| MX | 200 linhas |
| TB | 150 linhas |

### RENDERER_JS (injetado no HTML)

Renderer unificado substituindo todos os `pages.XXX()` do v4, exceto `categorias` e `estoque` que preservam implementação original (cascata interativa e filtros complexos):

```javascript
const _ABAS_SKIP = new Set(['categorias','estoque']);
_ABAS_KEYS.filter(pg => !_ABAS_SKIP.has(pg)).forEach(pg => {
  pages[pg] = () => _renderPage(pg);
});
```

Renderers implementados: `_renderKPI`, `_renderHL`, `_renderT`, `_renderTE`, `_renderGL`, `_renderGB`, `_renderGE`, `_renderMX`.

### GRID_CSS (injetado no HTML)

```css
.page-grid {
  display: grid;
  grid-template-columns: repeat(16, 1fr);
  grid-auto-rows: 40px;
  gap: 10px;
}
```

---

---

## [2026-06-02] Fase 3 — Passo 6: 22 elementos processed posicionados

**Commits:** `e6d5781`, `55dd4d9`, `5d5422f`

### generate_indexes.py — posicionamento dos elementos processed

Os 22 elementos gerados pelo `transform.py` (que não existiam no mock v4) foram todos posicionados no grid via `PROCESSED_POSITIONS` em `generate_indexes.py`:

```python
PROCESSED_POSITIONS = {
    "02_oportunidade_r02_por_cat":  (1, 16, 19, 4),
    "03_categoria_r04_top_forn":    (1, 16, 18, 6),
    # ... 22 entradas totais
}
```

### KPI row_span reduzido

KPIs estavam com `row_span=3` (120px — muito alto). Corrigido para `row_span=2` (80px) em todas as 15 abas.

Todos os elementos de cada aba foram deslocados -1 linha para compensar.

### Correções técnicas

| Problema | Causa | Solução |
|---|---|---|
| `window[e.variavel_js]` undefined | `const` não se anexa ao `window` | `window._BI_DATA[key]` registry |
| `pages.categorias` quebrada | Renderer sobrescrevia a cascata interativa | `_ABAS_SKIP = new Set(['categorias','estoque'])` |
| KPI height voltava ao rebuild | Valor não estava no source do generate_indexes.py | KPI row_span=2 baked no source |
| HTML com 8 MB | Sem limite de linhas por elemento | MAX_ROWS por tipo (T:50, TE:100, etc.) |

---

---

## [2026-06-02] Correção: fontes SVG fora do Design System

**Commit:** `e30f927`

Eixos dos gráficos SVG usavam `fill="#94a3b8"` e `font-family` incorreto.

**Corrigido para:**
- `fill="#64748b"` (= CSS `--muted` do Design System)
- `font-family="'Segoe UI',Arial,sans-serif"` (stack completo)

---

---

## [2026-06-02] Fase 3 — Passo 7: editor visual de layout

**Commits:** `658aae4`, `4ebc90f`, `f06304d`

### Editor injetado no dist/index.html pelo build.py

Botão `✎ Editar layout` adicionado ao topbar via JS. Ao ativar o modo edição (`body.edit-mode`):

**Drag e drop livre:**
- Arrastar qualquer elemento mostra um ghost azul tracejado indicando a posição alvo
- Drop em espaço vazio → move o elemento livremente
- Drop sobre outro elemento → SWAP completo de posições
- Posição calculada por coordenadas do mouse relativas ao grid (colW = gridWidth/16, rowH = 50px)

**Resize:**
- Handle `⇲` no canto inferior direito de cada elemento
- Drag do handle → ajusta `col_span` e `row_span` em tempo real
- Posição relativa ao grid: `CP = gridWidth/16`, `RP = 50`

**Visibilidade:**
- Botão `👁` na action bar de cada elemento
- Toggle `ed-hidden` → opacidade 18%
- Persiste `visivel: false` no override

**Edição de textos:**
- Títulos (`h3` em `.card-h`) e subtítulos (`.sub`) → `contentEditable`
- Headers de tabela (`th[data-key]`) → `contentEditable`; `data-key` injetado pelo renderer
- Labels de eixo SVG → input flutuante posicionado sobre o texto via `getBoundingClientRect()`

**Persistência (`localStorage`):**
- Cada ação auto-salva em `localStorage['bi_layout_{page_key}']`
- Ao carregar a página: `_loadAll()` restaura todos os estados salvos
- Ao trocar de aba: `_applyLayout(pk)` re-aplica overrides após o renderer rodar (setTimeout 60ms)
- Flash `✓ salvo` aparece brevemente na toolbar após cada save

**Undo:**
- Snapshot do DOM (gridColumn, gridRow, visibility) antes de cada ação
- Botão `↩ Desfazer` restaura DOM e `_st` sem re-render

**Exportar JSON:**
- Botão `⬇ Exportar JSON` baixa `{page_key}.layout.json`
- Formato compatível com `apply_layout_overrides()` no `build.py`
- Ao copiar para `dashboard/tabs/` e rodar `build.py`, mudanças persistem no próximo build

### apply_layout_overrides() no build.py

```python
def apply_layout_overrides(indexes):
    for _, idx in indexes.items():
        page_key = idx.get("data_page", "")
        layout_file = TABS_DIR / f"{page_key}.layout.json"
        if not layout_file.exists(): continue
        overrides = rj(layout_file).get("overrides", {})
        for elem in idx.get("elementos", []):
            eid = elem.get("id", "")
            if eid not in overrides: continue
            ov = overrides[eid]
            for k in ("col", "col_span", "row", "row_span", "visivel"):
                if k in ov: elem["layout"][k] = ov[k]
            if "texto" in ov:
                txt = ov["texto"]
                if "titulo"    in txt: elem["titulo"]    = txt["titulo"]
                if "subtitulo" in txt: elem["subtitulo"] = txt["subtitulo"]
                if "colunas"   in txt:
                    for col in elem.get("config", {}).get("colunas", []):
                        if col.get("key") in txt["colunas"]:
                            col["label"] = txt["colunas"][col["key"]]
    return indexes
```

### Estado atual do dist/index.html

- 721 KB, 15 abas funcionais
- 132 elementos com dados reais injetados
- 136 elementos no total (4 sem dados — rule-based ou hardcoded no v4)
- Editor funcional: drag livre, resize, visibilidade, textos, SVG labels, auto-save

---

---

## [2026-06-02] Passo 8 — Sistema de filtros multi-select

**Commit:** `298a06c`

### O que foi feito

Sistema completo de filtros interativos injetado no dashboard pelo `build.py`.

### Nova estrutura de filtros

**Linha 1 (9 filtros):** Empresa · Negócio · Região · UF · Filial · Ano · Período · ABC fornecedor · Fornecedor

**Linha 2 (13 filtros, colapsável):** CAT1 · CAT2 · CAT3 · CAT4 · CAT5 · Produto · ID · ABC produto · ABC ID · Status cotação · Status CP · Status AD · Tipo alerta

### Componente multi-select

- Botão mostra `Todos` ou `N sel.` ou valor único
- Dropdown com busca, `Selecionar todos`, checkboxes, contador e `Limpar`
- Um único `div#flt-dd` reposicionado dinamicamente abaixo do botão ativo
- Fecha ao clicar fora; aplica filtros ao fechar

### Persistência e estado

- Estado `_F` salvo em `localStorage['bi_filters']`
- Filtros restaurados e aplicados automaticamente ao abrir o dashboard
- Chips clicáveis na `filter-foot` mostram filtros ativos; clicar num chip remove aquele filtro
- "Limpar filtros" reseta tudo e salva estado vazio

### Arquitetura de dados

```
window._BI_DATA_RAW  ← cópia inicial (preservada)
       ↓ _applyF()
window._BI_DATA      ← dados filtrados (usados pelo renderer)
       ↓ pages[pk]()
DOM                  ← re-renderizado com dados filtrados
```

### Predicado de filtro (`_pred`)

Aplica todos os filtros ativos a cada linha de dados. Colunas mapeadas:

| Filtro | Coluna |
|---|---|
| empresa | `empresa` ou `empresas` (pipe-separated) |
| negocio | `negocio` |
| uf | `uf` (+ expansão de `regiao`) |
| filial | `filial` ou `nome` |
| cat1–5 | `cat1`–`cat5` |
| fornecedor | `fornecedor` |
| produto | `produto` |
| id | `id` ou `cdproduto` |
| abc_forn/prod/id | `curva`, `curva_prod`, `curva_id` |
| periodo | `mesano` |
| ano | ano extraído de `mesano` |
| status_cp | `statuspag` |
| status_ad | `status_conciliacao` |

### Recálculo de KPIs (`_KC`)

38 KPIs deriváveis recalculados em runtime a partir dos dados de linha já filtrados. Exemplos:

- `FILIAL_K01_TOTAL` → `SUM(FILIAL_R01_RANKING.spend)` após filtro
- `IMPACTO_K04_UF` → `MAX(IMPACTO_R02_UF, imp_cot).uf` após filtro
- `ADIANTAMENTO_K04_PCT` → `SUM(conciliado) / (SUM(pendente) + SUM(conciliado))`

~10 KPIs mantêm valor original (cross-source ou dependentes de data): `produtos_unicos`, `pct_com_cotacao`, `ids_sem_cotacao_12m`, `cp_a_vencer_7d`, `cp_critico_120d`, etc.

### Cascatas (`_CASC`)

| Filtro pai | Restringe opções de |
|---|---|
| Região | UF, Filial |
| Empresa, Negócio, UF | Filial |
| CAT1 → CAT2 → … → CAT5 | cada nível seguinte + Produto + ID |
| Produto | ID |
| ABC fornecedor | Fornecedor |
| ABC produto | Produto, ID |
| ABC ID | ID |
| Ano | Período |

### Integração com Editor (`_BI_EDITOR`)

`window._BI_EDITOR = { applyLayout, decorate, enText, enSvg }` exposto pelo EDITOR_JS.

Após re-render por filtro, FILTER_JS chama `_BI_EDITOR.applyLayout(pk)` para restaurar overrides de layout, e re-decora elementos se o modo edição estiver ativo.

---

---

## [2026-06-02] Passo 8 — Correções pós-entrega dos filtros

**Commits:** `77e448a`, `c309b4b`, `fb10c1f`, `97fae8e`, `b84e94b`

### Bugs corrigidos

| Bug | Causa | Solução |
|---|---|---|
| Labels do dropdown em linha horizontal | CSS `#flt-dd-list` mas HTML usava `id="flt-list"` | Seletor corrigido para `#flt-list` |
| Dropdown aparecia atrás do conteúdo | `position:fixed` e `z-index` vinham só da stylesheet; `style.cssText` os sobrescrevia | `position:fixed;z-index:9999` definidos no inline style |
| Fundo do dropdown transparente | `var(--surface)` não existe no v4 | `background:#fff` definido no inline style |
| "Selecionar todos" não funcionava | Seletor CSS inválido `[#flt-list...` lançava `DOMException` antes da lógica | Linha removida (variável `vis` nunca era usada) |
| Categorias CAT1–5 vazias | Chave `CAT_R01_HIERARQUIA` errada | Corrigido para `CATEGORIA_R01_HIERARQUIA` |
| ABC incompleto | `['AAA','AA','A','B','C']` | Corrigido para `['AAA','AA','A','B','BB','C','CC','CCC']` |
| Filtros ID e Produto separados | Redundância — ID é `cdproduto` do produto | Mergeados em único filtro Produto com formato `"ID - Nome"` |

### Mudanças estruturais

- Linha 2 dos filtros: de 13 para 12 colunas (remoção do botão ID)
- Predicado `_pred`: matching de produto usa `Set` de IDs e `Set` de nomes
- Cascata: `abc_id` e `abc_prod` afetam `produto` (não mais `id` separado)

---

---

## [2026-06-02] Dimensões completas para filtros (fornecedor, filial, categorias, produto)

**Commits:** `fb9c671`, `6e74d3e`

### Problema
Filtros usavam dados processados com MAX_ROWS truncados:
- Categorias: 150 de 1386 combinações cat1-5
- Produto: 200 de 6302 produtos com nome
- Filial: 20 de 79 filiais (HL=20)
- Fornecedor: 300 de 3518 com curva ABC

### Solução: 4 dimensões injetadas sem limite

| Dimensão | Fonte | Total |
|---|---|---|
| `DIM_CATEGORIAS` | `03_categoria_r01_hierarquia.csv` (processado) | 1386 |
| `DIM_PRODUTOS` | `raw/pmp_id_inf_12.csv` (Zoho) | 6302 |
| `DIM_FILIAIS` | `04_filial_r01_ranking.csv` (processado) | 79 |
| `DIM_FORNECEDORES` | `raw/curva_forn.csv` (Zoho) | 3518 |

### Filtro Produto unificado
`ID + Nome` no formato `"D501112009 - FRANGO CONGELADO"` — merged dos filtros separados ID e Produto.

### Empresas: apenas 3
`_EMPS = ['RC','ME','PV']` — RC=Ideal, ME=Melhor, PV=Pomme Vita

### ABC corrigido
`['AAA','AA','A','B','BB','C','CC','CCC']`

### Amarração Categoria→Produto via _vc2
`_computeVC2()` pré-computa Set<cat2> válidos da hierarquia completa antes de filtrar.
Garante que CAT1→CAT2→…→Produto funcione mesmo sem cat1-5 no arquivo de produtos.

### HTML: 746 KB → 1727 KB
Crescimento esperado com 3518 fornecedores + 6302 produtos + 1386 categorias.

---

---

## [2026-06-02] Passo 9 — Validação de dados + ativação de filtros faltantes

**Commits:** `e7b88eb`, `708a94c`, `0358d4e`

### Validação realizada: 131 elementos em 15 abas

Leitura completa de todos os `00_index.json` e arquivos de dados de cada aba. Resultado:

| Status | Count |
|---|---:|
| OK | 127 |
| PROBLEMAS (corrigidos) | 4 |
| PENDENTE (sem dados) | 2 abas |

**Abas PENDENTE:** `05_estoque` (requer workspace APURAÇÃO DE RESULTADOS) · `11_fiscal` (requer base cadastral de regime fiscal)

### Problemas encontrados e corrigidos

#### 1. `inflacao_media_pct = 29316%` (e `inflacao_media_cesta` em produto)

**Causa:** `PERC_INF_ID_PMP` no Zoho tem outliers extremos — divisão de variação por PMP≈0 gera valores como 1,69 bilhões de %. Havia 1.516 registros > 100%, máx = 1.692.571.328%.

**Fix em `transform.py`:**
```python
_INF_CAP = 500  # cap ±500%

def _inf_p(r):
    p = flt(r.get("PERC_INF_ID_PMP",""))
    return p if abs(p) <= _INF_CAP else 0.0
```
Aplicado em todas as 4 funções que leem `PERC_INF_ID_PMP`: `aba_inflacao`, `_produto_fix_kpis`, e derivados.

**Resultado:** `inflacao_media_pct`: 29316 → **4.0%** · `cat2_mais_inflada`: D3 → **A2 - ATIVOS INDIRETOS**

#### 2. Arquivos ausentes: r03/r04 (produto) e r05/r06 (inflação)

**Causa:** `pmp_prod_inf_12.csv` tem PMP_0–PMP_12 todos vazios (export Zoho sem série de preços). Condição `if p0<=0 or p12<=0: continue` excluía todas as linhas.

**Fix:** fallback que agrega `PERC_INF_ID_PMP` por produto via `inflacao.csv` quando PMP não disponível:
```python
if not pvars and inf_raw:
    pd_ = defaultdict(...)
    for r in inf_raw:
        nm = r.get("NMPRODUTO_EST",""); p = _inf_p(r)
        if not nm or p == 0: continue
        pd_[nm]["ps"] += p; pd_[nm]["pn"] += 1
    pvars = [...] # produtos com ≥3 meses de dado
```

**Resultado:** 4 arquivos criados com 25 linhas cada.

#### 3. `pmp_medio_cesta = 0`

**Causa:** PMP_0–PMP_12 vazios na fonte Zoho. Não corrigível sem novo extract.
**Status:** PENDENTE — aguarda nova extração do Zoho com série de preços.

### Filtros ativados na aba Categorias

**Problema:** aba `categorias` usa implementação v4 original que lê `const CAT_VAL` e `const CAT_INF`. Por serem `const`, não podiam ser reatribuídos pelo FILTER_JS.

**Fix em `build.py`:**
- `const CAT_VAL` → `var CAT_VAL`
- `const CAT_INF` → `var CAT_INF`

**Fix em FILTER_JS (`_applyF`):** após filtrar os arrays de `_BI_DATA`, rebuild dinâmico:
```javascript
// Rebuild CAT_VAL a partir de CATEGORIA_R01_HIERARQUIA filtrado
const hier = _BDF('CATEGORIA_R01_HIERARQUIA') || [];
const cv = {};
hier.forEach(r => {
  ['cat1','cat2','cat3','cat4','cat5'].forEach(k => {
    const code = r[k]?.split(' - ')[0]?.trim()?.split(' ')[0];
    if (code) cv[code] = Math.round(((cv[code]||0) + (parseFloat(r.spend)||0)/1e6)*10)/10;
  });
});
CAT_VAL = cv;

// Rebuild CAT_INF a partir de INFLACAO_R04_POR_CAT filtrado
CAT_INF = Object.fromEntries(
  (_BDF('INFLACAO_R04_POR_CAT')||[]).map(r => [
    r.cat2?.split(' - ')[0]?.trim()?.split(' ')[0],
    parseFloat(r.inflacao_media_pct)||0
  ]).filter(([k]) => k)
);
```

**Resultado:** aba Categorias (cascata interativa v4) agora responde a filtros de CAT1-5, UF, empresa.

### Bug crítico descoberto e corrigido: indexes sobrescritos

**Causa:** `transform.py` grava `{aba}_00_index.json` com formato `"relatorios"`, sobrescrevendo o formato `"elementos"` criado por `generate_indexes.py`. O `build.py` busca `"elementos"` → resultado: 136 elementos mas só 5 com dados injetados, todos os gráficos vazios.

**Fix:** `run.bat` agora chama `generate_indexes.py` depois de `transform.py`:
```
extract.py → transform.py → generate_indexes.py → build.py
```

### Estado atual do dashboard

- **131/131 elementos** com dados (exceto abas PENDENTE)
- **141 elementos com dados injetados** (incluindo 5 dimensões de filtro)
- **HTML:** 3.201 KB
- **Filtros:** todos os 15 filtros funcionais, incluindo categorias
- **Aba estoque:** PENDENTE · **Aba fiscal:** PENDENTE

---

---

## [2026-06-02] Passo 10 — Aba Relatório (NL-SQL com UI completa)

**Commit:** `d2cd9c8`

Implementação da Aba Relatório inspirada no GovGo v2, adaptada para Zoho Analytics.

### `nlsql/server.py` (Flask, `http://localhost:5001`)

| Endpoint | Função |
|---|---|
| `POST /run` | Pergunta → SQL → Zoho → título IA → histórico |
| `POST /generate-sql` | NL → SQL sem executar |
| `POST /execute` | SQL direto |
| `GET /history` · `DELETE /history/:id` | Histórico, soft delete |
| `POST /favorites/:id` | Toggle favorito |
| `GET/POST /chats` · `DELETE /chats/:id` | Gestão de chats |
| `GET/POST /prompt` · `POST /prompt/reset` | Ler/gravar/restaurar `bi_suprimentos_sql.md` |
| `GET /export/:id` | Download CSV |

Storage: `nlsql/history.json` + `nlsql/chats.json`. Chat contextual: últimas 6 mensagens passadas ao LLM.

### Frontend (RELATORIO_CSS + RELATORIO_JS via build.py)

- Layout 2-colunas: sidebar 300px (Chats/Histórico/Favoritos) + main
- Auto-detecta resultado: ≤4 linhas + numérico → KPIs · senão → tabela paginada (10/página)
- Enter envia, Shift+Enter nova linha · status visual spinner/verde/vermelho
- Copy SQL, Export CSV, toggle favorito, "Adicionar ao BI" (insere no grid da aba ativa)
- Aba "Assistente": editor textarea do `bi_suprimentos_sql.md` com salvar/restaurar backup

### Para usar
```
python nlsql/server.py   # Terminal 1
# Abrir dist/index.html → aba "Relatório"
```

---

## [2026-06-02] Passo 10 — Correções Aba Relatório

**Commits:** `0a98a8d`, `0f3ef18`

### Refatoração completa do layout (versão anterior estava errada)

Inspiração: estudo aprofundado do `RelatoriosWorkspace.jsx` do GovGo v2.

**Layout correto:** `grid-template-columns: 360px minmax(0,1fr)` — sidebar e main **simultâneos**, não abas alternadas.

**Sidebar esquerda (360px):**
- Botões Chat | Histórico para alternar modo (não são abas de resultado)
- Chat: bolhas user (azul escuro, direita) + assistente (azul claro, esquerda) + input fixo no fundo (height:58px, 3 rows)
- Histórico: 3 sub-abas (Chats | Relatórios | Favoritos) + lista clicável

**Main direita:**
- Barra de abas horizontal: uma aba por query (closable, count de linhas, spinner)
- Botão `+` nova consulta + botão `🤖 Assistente` fixo à direita
- Conteúdo: título 20px + subtítulo + bloco SQL dark (max 92px) + tabela (400px, 10 linhas/pág)

**Design System:** `--blue`, `--text`, `--muted`, `--line`, `--head`, `--border`

### Correções pós-feedback

| Problema | Causa | Fix |
|---|---|---|
| "Failed to fetch" sem contexto | Servidor não rodando, erro genérico | Detecta string fetch/Failed/Network → fecha aba criada, exibe mensagem instrutiva |
| Aba "Erro" aparece sem motivo | Toda query cria aba, inclusive falhas de rede | `_closeTab(tabId)` quando é erro de rede |
| Histórico não atualiza | `GET /history` só rodava no primeiro init | Ao clicar em "📋 Histórico" sempre chama `refreshHist()` |
| Assistente vazio quando servidor off | `GET /prompt` falhava silenciosamente | Exibe texto instrutivo na textarea: "Inicie com: python nlsql/server.py" |

---

## [2026-06-03] Melhorias Aba Relatório (UX)

**Commit:** `235ec4b`

### Topbar em linha única
- JS move `.stamp` para após `.brand` no DOM (2ª posição na grid)
- Grid: `auto auto 1fr auto...` — brand=auto, stamp=auto (encostado), search=1fr (preenche o meio), botões=auto
- EDITOR_JS: `par.appendChild` em vez de `insertBefore(stamp)` → "Editar layout" sempre no canto direito

### Scroll do chat (fix definitivo)
`.rel-msgs`: `position:absolute; top:41px; left:0; right:0; bottom:0` dentro de `.rel-chat-section { position:relative }` — elimina dependência da cadeia flex para altura

### Sidebar altura correta
- `calc(100vh - 140px)` (era 175px — novo cálculo: app.padding-top 14 + topbar 42 + topbar-mb 10 + tabs 48 + app.padding-bottom 24 = 138px)
- `_init()`: `app.paddingBottom = '0'` ao entrar na aba; restaurado ao sair

### Botões lixeira e refresh nos itens do histórico
Botões `🔄 Atualizar` e `🗑 Apagar` empilhados à direita de cada item de Relatório/Favorito:
- `histRefresh(id)`: `POST /execute` com o SQL existente, atualiza rows sem custo de LLM
- `histDel(id)`: `DELETE /history/:id`, remove do estado `_S.history` e re-renderiza

### Respostas do chat no formato card (igual ao histórico)
Respostas bem-sucedidas do assistente usam o mesmo visual dos boxes do histórico:
- Título do relatório em negrito
- Timestamp, chip `✓`, contagem de linhas
- Botão `→` (abre aba) e `⎘` (copia SQL) empilhados à direita
- Erros: bolha vermelha · Rodando: bolha com spinner (sem mudança)

---

## [2026-06-03] Aba Relatório — correções e melhorias de UX (continuação)

**Commits:** `f88f682`, `ce65f13`, `cddc78a`, `53e78e2`

### Fix definitivo: event delegation nos cards do chat

**Problema raiz:** onclick inline com template literals (`onclick="fn('${m.tabId}')"`) falha silenciosamente quando `m.tabId` ou `m.rid` são `undefined` — gera strings vazias e as funções não fazem nada.

**Solução:** event delegation no `#rel-msgs`:
- Cards têm `data-mid="${m.id}"` e class `rel-chat-card`
- Botões têm `data-action="refresh"` ou `"copy-sql"` + `data-mid`
- Um único listener no container captura todos os cliques e despacha:
  - click no card → `openOrLoad(mid)` — lookup `m.tabId`/`m.rid` via `_S.msgs`
  - click refresh → `chatRefresh(mid)` — lookup `m.sql` via `_S.msgs`
  - click copy → `copyMsgSQL(mid)` — lookup `m.sql` via `_S.msgs`
- `openOrLoad(msgId)` recebe apenas msgId, faz lookup em `_S.msgs` para obter tabId e rid — nunca mais depende de dados embutidos no onclick

### SVG constantes globais

`_SVG_REFRESH`, `_SVG_TRASH`, `_SVG_CODE`, `_SVG_SPIN` definidos uma vez no topo do IIFE, reutilizados em todos os botões (histórico + chat).

### Loading indicators

- **Spinner circular**: botão de refresh vira `_SVG_SPIN` + `disabled` durante fetch
- **Barra linear `.rel-lp`**: CSS `translateX(-100%→400%)`, animação 1.4s, prepend no `rel-content`, removida após fetch
- Aplicado em `chatRefresh` e `histRefresh`

### Outros fixes desta sessão
- `.rel-wrap`: card com `border + border-radius:10px` (igual outros elementos da página)
- Botões 26×26px com SVG stroke (era 20×18 com texto)
- Todos os emojis removidos do RELATORIO_JS e CSS
- Chat cards: `cursor:pointer`, botão "ver resultado" removido (card já abre)
- Barra de progresso linear `.rel-lp` no CSS

---

## [2026-06-03] Aba Relatório — correções de UX (close, cards, Assistente)

**Commit:** `deeec94`

### a) Ícone de fechar nas abas de resultado

**Problema:** `×` não aparecia nas abas. Causa: `.rel-rtab-x` era `position:absolute` dentro de um `<button>` — vários browsers clipam filhos absolutos de botões.

**Solução:** `.rel-rtab` mudou de `<button>` para `<div>` com `display:flex`. O `×` virou um `<span>` filho direto (flex child), sem position:absolute. Event delegation na `rel-tabs-bar` trata clique no `[data-close]` para fechar e no `.rel-rtab[data-tid]` para abrir.

### b) Cards do chat — click e atualizar

**Problema:** clicar no card não abria a aba de resultado; `chatRefresh` não atualizava nada quando a aba havia sido fechada.

**Causa raiz:** event delegation usava `card.dataset.tid` / `card.dataset.rid` embutidos no HTML em tempo de render. Se o estado mudou após o render, esses valores podiam estar desatualizados ou vazios.

**Fix:** delegação agora faz lookup em `_S.msgs` pelo `data-mid` do card — dados sempre frescos:
```javascript
const m=_S.msgs.find(m=>m.id===card.dataset.mid);
if(m) window._RL.openOrLoad(m.tabId, m.rid);
```

`chatRefresh`: quando `m.tabId` existe mas a aba foi fechada (`_S.reports[m.tabId]` inexistente), agora reabre a aba com os dados atualizados em vez de não fazer nada.

### c) Assistente na sidebar

**Layout anterior:** botão "Assistente" na barra de abas do main (direita), abrindo como uma aba de resultado.

**Novo layout:**
- Botão `[Chat] [Histórico] [Assistente]` no topo da sidebar esquerda
- Ao ativar: sidebar mostra info do arquivo + botões `Salvar` e `Restaurar` (sub-botões no mesmo estilo dos sub-tabs do Histórico)
- Main mostra a textarea do prompt ocupando toda a área
- `Salvar` e `Restaurar` desativados até haver mudança no texto (`_S.promptDirty`)
- `_S.promptDirty=true` ao digitar; volta a `false` após salvar ou restaurar
- Ao sair do modo Assistente (clicar Chat ou Histórico), barra de abas volta ao normal

---

## [2026-06-03] Fase 1 — Classificação automática de elemento + preview inline

**Commit:** `cfbacf0`

### Objetivo

Conectar o resultado de uma query NL-SQL ao sistema de renderização do BI: ao executar uma pergunta, a IA sugere automaticamente os melhores tipos de elemento (HL, GL, KPI, etc.) e renderiza um preview com os dados reais.

### Endpoint `POST /classify` (nlsql/server.py)

Recebe: `{question, sql, columns, rows (amostra 5), rowCount}`

Usa como system prompt o arquivo completo `docs/design/ELEMENTOS_BI.md` + regras obrigatórias de formato de config.

Retorna: `{ok, suggestions: [{tipo, confidence, reason, config}]}` — até 3 sugestões, validadas contra lista de tipos válidos (`KPI,GL,GB,GE,HL,T,TE,MX,FU`).

### Mudanças no pipeline/build.py

**Novo estado:** `_S.classify = {}` — por aba: `{loading, suggestions, activeType}`

**`_classify(tid)`** — chamada async após primeiro render de um resultado `ok`. Dispara `/classify`, atualiza `_S.classify[tid]`, re-renderiza conteúdo.

**`_renderVizBar(tid)`** — barra "Ver como: [Tabela] [HL 92%] [T 71%]":
- Estado inicial (não disparado): vazio
- Loading: spinner + "Analisando visualização…"
- Com sugestões: botões de tipo com % de confiança; tooltip com `reason`

**`_renderPreview(tipo, config, data, columns)`** — chama o renderer existente com os dados reais:
- KPI: transforma `rows[0]` em objeto, detecta chave numérica automaticamente
- GE: faz pivot via `_pivotGE()` se config tem `{x, group, value}`
- T/TE: auto-gera `colunas` a partir dos nomes das colunas reais
- Todos os outros: passagem direta ao renderer

**`_pivotGE(data, xKey, groupKey, valueKey)`** — transforma 3 colunas em formato wide para `_renderGE`.

**`_renderTableSection(r, tid)`** — tabela extraída como função separada para reuso sem duplicação.

**`_renderContent()` modificado:**
1. Renderiza título + subtítulo + SQL block (igual ao anterior)
2. Adiciona `_renderVizBar(tid)` acima da tabela
3. Se `activeType !== 'table'`: renderiza `reason` + preview do elemento
4. Sempre renderiza a tabela abaixo como referência
5. Ao final, dispara `_classify(tid)` se ainda não iniciado

**`setVizType(tid, tipo)`** — troca o tipo ativo e re-renderiza.

### Fluxo completo

```
Pergunta → resultado ok → _renderContent() → tabela aparece + viz bar "Analisando…"
  ↓ (assíncrono, ~2s)
_classify() → POST /classify → OpenAI (ELEMENTOS_BI.md) → sugestões
  ↓
_renderContent() re-chamado → viz bar atualizada: [Tabela] [HL 92%] [T 71%] [GB 58%]
  ↓
Usuário clica [HL 92%] → setVizType() → preview renderizado acima da tabela
```


---

## [2026-06-03] Sessao completa — UX Relatorio, Biblioteca, Prompt v3, Resumo

### Correcoes UX da Aba Relatorio
- Cards do chat: substituido event delegation por inline onclick (mesmo padrao dos cards de historico)
- Normalizacao de campos servidor->cliente ao carregar chat do historico (role, st, rid, refTitle)
- Botao copiar SQL: substituido texto 'Copiar' por icone SVG; SQL removido do onclick (prevenia HTML quebrado)
- Barra de visualizacao: spinner visivel desde primeiro render; icones SVG + nomes em portugues
- Visualizacao exclusiva: apertar tipo substitui a tabela (nao acumula)
- KPI: regra de insercao sequencial no topo (8 por linha, 2x2, ultimo fecha ate col 16)
- _isInGrid: usa _BI_EDITOR.getOv() para estado real (nao ABAS_INDEX original)
- _rerender: reatribui draggable=true apos render() do v4

### Biblioteca de Elementos (Fase 3)
- Drawer lateral esquerdo com puller "Biblioteca"
- Mostra TODOS os elementos da aba: default (chip cinza 'BI') + NL-SQL (chip azul 'Relatorio')
- Duas secoes: "No grid" com botao Retirar + "Disponiveis" com botao Inserir
- Botao X no editor substitui toggle ocultar/mostrar (chama _NL.removeElem)
- Insercao usa render(pg) do v4 em vez de pages[pg]() que so retorna string

### Assistente — seletor de versoes
- GET /prompt/versions: lista v1, v2, v3 com metadata
- POST /prompt/activate: define versao ativa para SQL (persiste em active_version.txt)
- Cards no sidebar com badge "Em uso", borda azul no card ativo
- Tabs __prompt_v1, __prompt_v2, __prompt_v3 na area de resultado
- v1 readonly, versao ativa editavel com Salvar/Restaurar

### Estudo dos dados (Fase 1 do plano de melhoria)
- docs/dados/ANALISE_DADOS_REAIS.md: 18 fontes, tipos de campo, filtros obrigatorios
- docs/zoho/MAPA_PAINEIS.md: 72 pivots + 31 analysis views + Design System completo
- Identificados 5 bugs no prompt v1 (STATUSPAG, PMP_0, TE.ID, T.FORNECEDOR, POS errado)

### Prompt NL-SQL v3 (nlsql/prompts/bi_suprimentos_sql_v3.md — 39KB)
- Tipos de dados de cada campo com exemplos reais dos CSVs
- 2 linhas de amostra por tabela (dados reais)
- Exemplos SQL com resultado esperado
- Produto vs CDPRODUTO_EST: embalagem vs unidade de estoque (KG/LT/UN)
- ID = NMEMP + UF + CDPRODESTO explicado com exemplos (RCPEI201203000)
- Tres curvas ABC separadas: CURVA_FORN, CURVA_PROD, CURVA_ID — quando usar cada
- MESANO: todos os padroes de filtro (LIKE, =, intervalo)
- Inflacao: PERC_* em % vs SOMA_* em R$; filtro NULL; outliers com ABS < 200
- Hierarquia correta de categorias (dados reais do processed):
  I1=ESTOCAVEIS, I2=PERECIVEIS, I3=HORTIFRUTI, I4=DESCARTAVEIS, I5=LIMPEZA, I6=GAS
- Mapa linguagem natural -> SQL: "carnes" -> CAT2='I2 - PERECIVEIS', etc.

### transform.py aba Resumo
- Adicionado: ids_unicos (16.343), produtos_unicos (6.302), cp_vencido (R$ 65.9mi)
- K07: era placeholder 'fornecedores_ativos' -> agora 'ad_pendente' (R$ 44mi)
- K08 CP: delta era 'cp_titulos' -> agora 'cp_vencido' com delta_dir=down

---

## [2026-06-08] Aba Fornecedor: KPIs + layout + colunas r01

### Motivação
Revisão da aba Fornecedor comparando implementação vs MAPA_PAINEIS.md e ESPECIFICACAO_ABAS.md. Mesmo processo aplicado à aba Resumo na sessão anterior.

### Gaps identificados
- `forn_curva_aaa_aa` (contagem fornecedores AAA+AA) ausente — citado no MAPA_PAINEIS linha 179
- `cp_aberto_total` e `ad_pendente_total` (somas R$) ausentes — existiam apenas as contagens
- Layout: 5 KPIs com col_span variável (3/3/3/3/4), inconsistente com padrão 8×2 da aba Resumo
- r01_tabela: 4 colunas do CSV ausentes no IDX (ufs, categorias_top, pct, cp_vencido)
- K02/K03 sem `state` visual

### Correções — transform.py (`aba_fornecedor`)
- `forn_curva_aaa_aa = sum(1 for cd,d in fv.items() if curva in ("AAA","AA"))`
- `cp_aberto_total = r2(sum(fcp.get(cd,{}).get("aberto",0) for cd in fv))`
- `ad_pendente_total = r2(sum(fad.get(cd,{}).get("pendente",0) for cd in fv))`

### Correções — generate_indexes.py (IDX_06)
- Reorganizado para 8 KPIs × col_span=2 (cols 1→16):
  - k01 Fornecedores Ativos | k02 Forn. AAA+AA (ok) | k03 Spend AAA/AA/A (ok) | k04 % Spend Top (ok)
  - k05 Forn. c/ CP Aberto (warn) | k06 CP Aberto R$ (warn) | k07 Forn. c/ AD Pendente (warn) | k08 AD Pendente R$ (warn)
- r01_tabela: +ufs, +categorias_top, +pct, +cp_vencido

### Valores gerados
- forn_curva_aaa_aa: 54 | cp_aberto_total: R$ 105mi | ad_pendente_total: R$ 44mi

### Commits
- `373e53b` aba Fornecedor: +3 KPIs, 8 KPIs col_span=2, +4 colunas r01

---

## [2026-06-08] Prompt v3: bug PERC_INF_* em NFE

### Problema relatado
Usuário usou o assistente NL-SQL para "percentual de inflação por categoria CAT2 por mês nos últimos 12 meses". O assistente gerou `PERC_INF_PROD_PMP` com `FROM "NFE"`, causando HTTP 400 INVALID_COLUMN.

### Causa raiz (dois bugs no prompt)
1. **Seção #6 sem atribuição de tabela**: listava PERC_INF_* e SOMA_INF_* como campos genéricos sem dizer que pertencem à tabela INFLACAO. NFE tem `INF_PROD_PMP` (sem PERC_/SOMA_).
2. **Documentação INFLACAO incompleta**: prompt omitia CAT1..CAT5, UF, NMEMP, NMPRODUTO_EST, ANO da tabela INFLACAO — modelo não sabia que CAT2 existe lá para GROUP BY direto.

### Correções — bi_suprimentos_sql_v3.md
- Seção #6: aviso crítico "PERC_INF_*/SOMA_INF_* SOMENTE em INFLACAO"; regra de roteamento (por CAT2/UF → FROM INFLACAO); exemplos com FROM explícito
- Seção INFLACAO: +12 campos documentados (CAT1..CAT5, UF, NMEMP, NMPRODUTO_EST, CDPRODUTO_OFICIAL, POS_ID, ANO)
- Novo exemplo SQL: inflação por CAT2 por mês com FROM INFLACAO correto

### SQL correto para a consulta do usuário
```sql
SELECT "CAT2", "MESANO", AVG("PERC_INF_PROD_PMP") AS inflacao_media_pct
FROM "INFLACAO"
WHERE "CAT2" IN ('I1 - ESTOCAVEIS','I2 - PERECIVEIS','I3 - HORTIFRUTI','I4 - DESCARTAVEIS','I5 - LIMPEZA','I6 - GAS')
  AND "PERC_INF_PROD_PMP" IS NOT NULL
  AND "MESANO" >= '2025/07' AND "MESANO" <= '2026/06'
GROUP BY "CAT2", "MESANO"
ORDER BY "CAT2", "MESANO" ASC
```

### Commits
- `62481a3` prompt v3: corrigir bug PERC_INF_* em NFE + adicionar CAT2 em INFLACAO

---

## [2026-06-08] Prompt v3: MESANO INFLAÇÃO tipo data + nomes de tabela Zoho

### Problemas reportados
1. MESANO na INFLAÇÃO mostrava "2.026" (= 2026) em vez de "2025/07"
2. `"INFLACAO"` (sem acento) gerava HTTP 400 INVALID_TABLE (commit anterior desta sessão)

### Causa raiz MESANO
A view INFLAÇÃO no Zoho é do tipo `QueryTable`. O Zoho detecta `MESANO` como coluna data (Ano-Mês). `SELECT "MESANO"` retorna apenas o ano exibido em notação brasileira (ponto como separador de milhar). Os dados estão corretos (72 linhas = 6 cat × 12 meses), mas o Zoho oculta o mês.

### Correção MESANO
Usar `DATEFORMAT("MESANO", 'yyyy/MM')` no SELECT, GROUP BY e ORDER BY.
Filtros `WHERE "MESANO" >= '2025/07'` continuam funcionando normalmente.

### Correções nomes de tabela (commit anterior)
- `"INFLACAO"` → `"INFLAÇÃO"` (replace_all no prompt)
- `"CP_SALDO_2026"` → `"CP_SALDO_2026_v2"` (replace_all no prompt)

### Commits
- `db95b33` prompt v3: corrigir nomes de tabela Zoho
- `42137f1` prompt v3: MESANO INFLACAO e tipo data — usar DATEFORMAT para YYYY/MM

---

## [2026-06-08] Reverter DATEFORMAT + botão aba Relatório azul

### Prompt v3 — DATEFORMAT revertido
DATEFORMAT("MESANO", 'yyyy/MM') causava UNSUPPORTED_MYSQL_FN no Zoho.
MESANO é texto 'YYYY/MM' em todas as tabelas, inclusive INFLAÇÃO.
SQL correto: usar "MESANO" diretamente em SELECT, GROUP BY e WHERE.

### build.py — botão aba Relatório diferenciado
CSS adicionado ao RELATORIO_CSS para distinguir o botão da aba Relatório:
- Inativo: `background: #eff6ff` (blue-soft) + `border-color: #2563eb`
- Ativo: `background: #2563eb; color: #fff` — igual ao botão Enviar
- Implementado via seletor `.tab[data-page="relatorio"]` com especificidade maior

### Commits
- `51facf8` prompt v3: reverter DATEFORMAT
- `7e4130b` prompt v3: reverter DATEFORMAT; build.py: botao aba Relatorio azul

---

## [2026-06-08] build.py: _isN parseFloat→Number + alinhar th numéricos

### Bugs reportados
1. MESANO exibido como "2.025" em vez de "2025/07" na tabela do Relatório
2. Cabeçalho de colunas numéricas centralizado enquanto valores estavam à direita

### Causa raiz
`_isN` usava `parseFloat('2025/07')` = 2025 (JavaScript para de parsear no `/`), então retornava `true` para MESANO. A função `_fv` formatava `2025` como número em notação brasileira "2.025".

### Correções — build.py (_renderTableSection)
- `_isN`: `parseFloat(v)` → `Number(v)`. `Number('2025/07') = NaN` → identifica corretamente como texto
- `ths` generator: detecta se primeira linha da coluna é numérica e aplica `text-align:right` ao `<th>` correspondente

### Commits
- `5e01727` build.py: corrigir _isN (parseFloat->Number) + alinhar th numericos

---

## [2026-06-08] server.py: export CSV padrão BR + _isN parseFloat→Number

### Bugs reportados
1. inflacao_media_pct no CSV exportado aparecia como "30.033.919.057.555.400" em vez de "-3,003"
2. MESANO virava data "01/07/2025" no Excel

### Causa raiz — CSV export
Os dados armazenados estão corretos: `inflacao_media_pct = '-3.0033919057555445'`. O CSV era gerado com ponto como separador decimal (padrão Python), mas o Excel Brasil interpreta ponto como separador de MILHAR, convertendo -3.003...445 em -30.033.919.057.555.445 (~10^16 vezes maior).

### Fix — server.py
- `_csv_val()`: converte floats para formato BR (vírgula como decimal). Texto permanece inalterado (MESANO '2025/07' não vira float).
- Delimitador trocado de `,` para `;` (padrão CSV Brasil/Europa, evita conflito com vírgula decimal).

### Fix anterior — build.py (_isN parseFloat→Number)
MESANO '2025/07' era tratado como número pela tabela BI porque `parseFloat('2025/07') = 2025` (JS para no `/`). Trocado por `Number('2025/07') = NaN` → texto.

### Commits
- `5e01727` build.py: _isN + alinhamento th
- `fa081f7` server.py: export CSV padrão BR

---

## [2026-06-08] Sessão tarde: NL-SQL bugs, BI elementos, BAT atualização

### Prompt v3 — série de bugs e correções

#### Tabela INFLAÇÃO
- `"INFLACAO"` → `"INFLAÇÃO"` (com acento) — HTTP 400 INVALID_TABLE (`db95b33`)
- `"CP_SALDO_2026"` → `"CP_SALDO_2026_v2"` — HTTP 400 INVALID_TABLE (`db95b33`)
- `DATEFORMAT("MESANO",'yyyy/MM')` adicionado e depois revertido — Zoho retorna UNSUPPORTED_MYSQL_FN; MESANO é texto 'YYYY/MM' direto (`51facf8`)
- `NMPRODUTO_OFICIAL` não existia em INFLAÇÃO → documentado + aviso; depois usuário adicionou o campo e documentação foi atualizada (`c8802ee`, `63a54a1`)
- `CURVA_PROD` e `POS_PROD` adicionados pelo usuário à view INFLAÇÃO → documentados no prompt e em ANALISE_DADOS_REAIS.md (`6145490`)
- Re-extract inflação: 117.578 linhas, 39.6 MB (era 36.7 MB) com novos campos

#### Outros bugs SQL Zoho
- `ORDER BY MIN("POS_PROD")` → SQL_INVALID_GROUP_FUNC_USE — Zoho não aceita agregação em ORDER BY; fix: adicionar coluna ao GROUP BY (`b567613`)
- `NMPRODUTO_OFICIAL` usado em query de INFLAÇÃO → INVALID_COLUMN; campo correto é `NMPRODUTO_EST` em INFLAÇÃO (`c8802ee`)

### BI — elementos adicionados ao BI (Adicionar ao BI)

#### Bugs identificados (colunas e formatação)
- Ordem das colunas ficava alfabética em vez de ordem SQL (`Object.keys` não garante ordem)
- Limite de 6 colunas (`slice(0,6)`) em `_renderT` e `_renderPreview`
- Números sem `fmt` configurado mostravam precisão total (ex: 1.0922272909392708)

#### Fix aplicado (seguro)
- `_renderT`: `let cols` com `if(!cols||!cols.length)` — usa `elem.columns` (ordem SQL) como fallback, sem limite de colunas (`1226a5a`, `71ee3fe`)

#### Bug crítico recorrente — NUNCA TOCAR
O bloco `else if (!fmt && _isN(v)) { v = toLocaleString(...) }` dentro de `_renderT`
foi adicionado 3 vezes e TODAS as 3 vezes quebrou a inicialização das abas do BI.
**Causa raiz: não identificada.** Parece que `_renderT` é chamada durante inicialização
em algum contexto onde esse bloco gera um erro que cascateia.
**Regra: não adicionar formatação automática em `_renderT` até investigar com DevTools.**
Commits que quebraram: `1acff97`, `6ba7a37`
Commits que reverteram: `71ee3fe`, `b0156af`

### BI — Relatório sumia ao voltar para a aba

#### Causa
`pages['relatorio']()` é chamada a cada visita à aba. Dentro dela havia
`document.addEventListener('click',...)` que acumulava listeners. Após N visitas:
N chamadas `_init()` simultâneas → a última re-renderizava com estado limpo.

#### Fix
`window._RL_CLICK_BOUND` — guard para registrar o listener só uma vez (`6ba7a37`, `b0156af`)

### BAT de atualização
- Criado `Atualizar BI Suprimentos.bat` na área de trabalho
- Versão 1: `mode con cols=200` para evitar quebra de linha do progress bar
- Versão 2: output verboso redirecionado para `atualizar.log`, mostra só resumo no terminal

### Aba Fornecedor (início do dia)
- +3 KPIs: `forn_curva_aaa_aa`, `cp_aberto_total`, `ad_pendente_total`
- Reorganizado para 8 KPIs × col_span=2 (padrão aba Resumo)
- r01_tabela: +4 colunas (ufs, categorias_top, pct, cp_vencido)

### Export CSV
- Delimitador: `,` → `;` (padrão BR/Europa)
- Números: ponto decimal → vírgula (`_csv_val` em server.py)
- Evita que Excel BR interprete ponto como separador de milhar

### Commits desta sessão (ordem)
`373e53b` aba Fornecedor KPIs → `62481a3` prompt PERC_INF → `db95b33` nomes tabelas Zoho
→ `5e01727` _isN+alinhamento → `fa081f7` CSV export BR → `7616f9e` botão copiar erro
→ `c8802ee` NMPRODUTO/GROUP BY → `b567613` ORDER BY → `6145490` CURVA_PROD/POS_PROD
→ `63a54a1` NMPRODUTO_OFICIAL INFLAÇÃO → `1acff97` ❌QUEBROU → `1226a5a` fix parcial
→ `71ee3fe` revert seguro → `6ba7a37` ❌QUEBROU NOVAMENTE → `b0156af` revert final

---

## [2026-06-08] Correção definitiva: Relatório sumia ao voltar para a aba

### Sintoma
Ao clicar na aba Relatório após ter estado em outra aba, o conteúdo aparecia por ~30ms (blink) e depois sumia, deixando a tela branca.

### Causa raiz
`_applyF()` em FILTER_JS (linha 1294) é chamada 90ms após qualquer clique de aba **quando há filtros ativos**. Ela re-renderiza a aba ativa com `pg.innerHTML = pages[pk]()` — inserindo HTML limpo e apagando o que o `_init()` do Relatório havia renderizado 60ms antes.

Timeline do bug:
- t=0ms: clica Relatório → HTML limpo inserido pelo tab system
- t=60ms: `_init()` do Relatório → conteúdo renderizado (blink visível)
- t=90ms: `_applyF()` → `pg.innerHTML = pages['relatorio']()` → HTML limpo novamente → tela branca

### Correção
Uma linha em `_applyF()`: `if(pk && pk !== 'relatorio')` — pula o re-render da aba Relatório porque ela tem sistema de renderização próprio via `_init()` e não usa o pipeline de dados filtrados.

### Outros bugs desta rodada (ja registrados acima)
- `else if (!fmt && _isN(v))` em `_renderT` quebra abas — causa ainda não identificada, não tocar
- `_RL_CLICK_BOUND` guard adicionado (listener do Relatório era já single-use, guard redundante mas inofensivo)

### Commits
- `b0156af` reverter else-if numerico em _renderT (terceira vez)
- `d04bf5a` corrigir Relatorio sumindo — _applyF nao re-renderiza aba relatorio

---

## [2026-06-08] Formato numérico BR — causa raiz dos crashes identificada

### Causa raiz dos crashes anteriores
`_fv()` está dentro do IIFE do `RELATORIO_JS`. `_renderT` está dentro do IIFE do `RENDERER_JS`. São escopos isolados — chamar `_fv()` de dentro de `_renderT` lançava `ReferenceError: _fv is not defined` que quebrava toda a inicialização das abas. Isso explica por que adicionar `else if (!fmt && _isN(v)) v = _fv(v)` ao `_renderT` sempre quebrava as abas (3 tentativas).

### Solução
Formatar inline em `_renderT` sem chamar funções do outro IIFE. Mesma lógica em `_fv`.

Formato: `n.toFixed(2)` → separar inteiro/decimal → regex `\B(?=(\d{3})+(?!\d))` → ponto como milhar → vírgula como decimal.

Resultado: `20.9900000002` → `20,99` | `3.899...` → `3,90` | `1234567` → `1.234.567,00`

### Commits
- `0350f5c` build.py: formato numerico BR 2 casas decimais

---

## [2026-06-08] Causa raiz confirmada + formatação numérica BR definitiva

### Causa raiz dos crashes (confirmada com inspeção de código)
- **RENDERER_JS**: escopo GLOBAL (sem IIFE)
- **RELATORIO_JS**: tem `(function(){ 'use strict'; ... })()` — IIFE privado
- `_isN` e `_fv` estão DENTRO do IIFE do RELATORIO_JS → não acessíveis globalmente
- Chamar `_isN(v)` ou `_fv(v)` de `_renderT` (global) = `ReferenceError: _isN is not defined`
- Esse ReferenceError quebrava a inicialização das abas silenciosamente

### Solução definitiva
- `_renderT` (RENDERER_JS global): substituir `_isN(v)` pela lógica inline completa. Zero chamadas a funções do IIFE.
- `_fv` (dentro do RELATORIO_JS IIFE): seguro alterar, não sai do escopo. 2 casas decimais fixas.

### Formato resultante
`20.9900000002` → `20,99` | `3.899...` → `3,90` | `1.234.567,89` | `-3,00`

### Commits
- `90cb8fb` reverter formatacao numerica (estado seguro)
- `c679c56` formatacao BR definitiva — inline sem chamar IIFE

---

## [2026-06-08] Tabelas das abas: paginação + CSV + expandir

### Features adicionadas às tabelas T/TE das abas do BI

**a) Paginação** — `«` `‹` `[1/20]` `›` `»`
- 25 linhas por página (mesmo padrão do Relatório)
- Estado global `window._TS[vjs]` por `variavel_js`
- Navegação substitui só o innerHTML do wrapper sem re-render do elemento inteiro

**b) Export CSV** — botão `⬇ CSV`
- Exporta todos os dados (todas as páginas) como CSV com `;` como delimitador
- UTF-8 BOM para Excel BR

**c) Expandir/Recolher** — botão `⤢` / `⤡`
- `position:fixed` para ocupar toda a área visível
- Overlay escuro ao fundo; clicar novamente recolhe

### Implementação
- `_fmtTCell`: formatação de célula inline (sem chamar `_isN`/`_fv` do IIFE)
- `_renderTInner(vjs)`: conteúdo paginado, reutilizado na navegação
- `_renderT`: cria wrapper `id="tw_{vjs}"`, chama `_renderTInner`
- CSS `.t-ctrl` adicionado ao GRID_CSS

### Commits
- `f5792bc` build.py: paginacao + CSV + expandir nas tabelas das abas BI

---

## [2026-06-08] Controles tabela movidos para o cabeçalho

### Mudança
Paginação, CSV e expandir agora ficam no lado direito do `card-h` (cabeçalho da tabela), sem criar linha adicional.

### Implementação
- `_tCtrlHtml(vjs)`: retorna apenas os botões (sem wrapper)
- `_renderTInner`: retorna apenas a tabela (sem barra)
- `_renderElemento` T/TE: gera cabeçalho customizado com `id="tc_{vjs}"` para update sem re-render
- `_T_NAV` e `_T_EXPAND`: atualizam `tw_{vjs}` (tabela) E `tc_{vjs}` (controles no header)
- CSS: `.t-pgb`, `.t-pgn`, `.t-info` — botões compactos para caber no header

### Commits
- `f5792bc` paginacao + CSV + expandir (linha extra)
- `7f397ed` controles movidos para o cabecalho

---

## [2026-06-08] Registry FIELD_FORMATS + _fmt unificado

### Problema resolvido
Formatação inconsistente: CDFILIAL (código) aparecia como "3.002,00", POS_PROD (inteiro) como "1,00". A causa era lógica de auto-format sem distinguir tipos de dado.

### Solução: arquitetura em 3 camadas
1. **`FIELD_FORMATS`** (Python, ~100 campos): registry central derivado de análise de todos os CSVs raw + generate_indexes.py. Injetado como `window._FF`.
2. **`_fmt(v, key, override)`** (RENDERER_JS global): função única de formatação. Prioridade: `override` > `window._FF[key]` > raw. Exposta como `window._fmt`.
3. **Aliases `_FA`**: retrocompat com códigos antigos (`brl`→`r0`, `pct`→`p1`, etc.)

### Catálogo de formatos
`d0/d2/d4` (decimal sem R$) | `r0/r2/r4` (com R$) | `rmi` (milhões)
`n0/n2/n4` (numérico puro) | `p1` (% pill c/sinal) | `p2/p4` (% simples)
`code` (ID/código) | `text` | `date`

### Para novos campos
Usar assistente OpenAI com nome do campo + 3 exemplos de valores + lista de formatos → retorna código sugerido para adicionar ao FIELD_FORMATS.

### Commits
- `4dcb660` build.py: registry FIELD_FORMATS + _fmt unificado

---

## [2026-06-08] Editor de layout: sobreposição + persistência F5

### Bugs reportados
a) Novo elemento inserido ficava sobre o último elemento (sobreposição)
b) Após F5, posições manuais do editor desapareciam

### Diagnóstico
**Bug a:** `_lastRow(pg)` lia `ABAS_INDEX[pg].elementos[i].layout.row` — posições ORIGINAIS do build.py. Quando o editor arrasta um elemento, `_st[pk].overrides` é atualizado mas `ABAS_INDEX` não. Então `_lastRow` retornava linha já ocupada por elemento movido.

**Bug b:** `_applyLayout` aplicava overrides ao CSS do DOM mas não atualizava `ABAS_INDEX`. Em qualquer re-render posterior (troca de aba, filtros), `ABAS_INDEX` regenerava posições originais.

### Correções
- `_lastRow`: usa `_BI_EDITOR.getOv(pg, e.id)` para ler posição REAL, com fallback ao layout
- `_insertElem`: loop de detecção de sobreposição — avança a linha até encontrar espaço livre
- `_applyLayout`: sincroniza `ABAS_INDEX.elementos[i].layout` com os overrides ao aplicar

### Commits
- `55ddc78` build.py: corrigir posicionamento e persistencia do editor de layout

---

## [2026-06-08] _findFreePos: busca 2D completa no grid

### Mudança
Substituiu `_findFreeRow` (bounding box + col=1 fixo) por `_findFreePos`:
varredura esquerda→direita, cima→baixo, verificando CADA CÉLULA do bloco candidato contra mapa de ocupação célula a célula.

**Algoritmo:**
1. Constrói `taken[r][c] = 1` para cada célula ocupada por elemento visível
2. Testa cada posição (row, col) de cima para baixo, esquerda para direita
3. Para cada candidato, verifica todas as `col_span × row_span` células
4. Retorna `{row, col}` da primeira posição sem conflito

**Resultado:** novo elemento ocupa o primeiro espaço livre no grid (ex: gap deixado por elemento removido), com posição `col` também otimizada.

### Commits
- `eaa20c6` _findFreeRow primeira versão
- `bb03223` _findFreePos busca 2D completa

---

## [2026-06-08] Persistência de layout: causa raiz real corrigida

### Causa raiz
`_renderPage` usava `e.layout.col/row` (posições originais do build.py) para gerar o HTML. Os overrides do editor só eram aplicados **60ms depois** via `_applyLayout` (CSS patch após render). Isso causava flash visual e aparência de "não salvar" ao trocar de aba.

### Correção definitiva
`_renderPage` agora consulta `window._BI_EDITOR.getOv(pageKey, e.id)` **antes** de ler `e.layout`. Prioridade: override > layout original. Resultado: elementos já renderizam nas posições corretas desde o primeiro frame — sem flash, sem delay.

`_applyLayout` continua rodando (60ms) mas agora é redundante para posições — serve de safety net para edge cases.

### Flow após fix
1. F5 → `_loadAll()` restaura overrides no `_st`
2. Usuário clica aba Produtos
3. `_renderPage` consulta `_BI_EDITOR.getOv` → HTML gerado com posições corretas
4. Elementos visualmente corretos desde o primeiro frame ✓

### Commits
- `55ddc78` _applyLayout sincroniza ABAS_INDEX; _lastRow usa overrides reais
- `bb03223` _findFreePos busca 2D completa
- `1b877bb` _renderPage usa overrides do editor (fix real da persistência)
