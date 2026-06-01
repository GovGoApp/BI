# Arquitetura Modular - BI Suprimentos

Este documento define a arquitetura conceitual para transformar o BI de Suprimentos em um sistema modular, configuravel e seguro.

Objetivo: permitir alterar fontes, metricas, elementos visuais, conteudos e posicionamento sem reescrever a pagina inteira.

## Principio central

Cada item do BI deve seguir uma cadeia clara:

```text
Fonte de dado -> Dataset -> Metrica -> Elemento -> Sub-elementos -> Layout -> Aba
```

Com isso, cada decisao fica no seu lugar:

- fonte: de onde vem o dado;
- dataset: como o dado e preparado para analise;
- metrica: qual formula ou indicador e calculado;
- elemento: qual bloco visual aparece na tela;
- sub-elementos: quais partes internas compoem o bloco;
- layout: onde o bloco fica;
- aba: em qual guia do BI o bloco aparece.

## Camadas

### 1. Fontes

Camada de origem dos dados.

Exemplos:

- Zoho Analytics - workspace `SUPRIMENTOS`;
- Zoho Analytics - workspace `APURACAO DE RESULTADOS`;
- arquivos CSV periodicos;
- bases locais tratadas;
- futuras APIs externas.

Cada fonte precisa registrar:

- `id`;
- `nome`;
- `workspace`;
- `view_id`;
- `tipo`;
- frequencia de atualizacao;
- criticidade;
- campos esperados;
- politica de cache;
- regra de privacidade.

### 2. Datasets

Camada de dados logicos prontos para consumo.

Exemplos:

- `compras_nfe`;
- `cotacoes_por_produto`;
- `impacto_cotacao_por_id`;
- `inflacao_por_categoria`;
- `estoque_por_filial`;
- `cp_por_fornecedor`.

Um dataset pode vir de uma fonte unica ou de joins entre varias fontes.

### 3. Metricas

Camada semantica. Aqui ficam formulas e definicoes de negocio.

Exemplos:

- `total_comprado_12m`;
- `impacto_cotacao_total`;
- `produtos_com_uma_cotacao`;
- `inflacao_media_cesta`;
- `cp_vencido`;
- `dias_estoque_medio`.

Regra importante: `IMP` e `INF` devem permanecer metricas separadas.

- `IMP`: impacto economico, principalmente diferenca entre preco comprado/PMP e menor cotacao vezes quantidade.
- `INF`: variacao de PMP no tempo.

### 4. Elementos

Elemento e o bloco funcional maior exibido na interface.

Tipos previstos:

- `kpi`;
- `chart`;
- `table`;
- `pivot`;
- `matrix`;
- `ranking`;
- `alert_list`;
- `drilldown`;
- `detail_panel`;
- `filter_panel`;
- `status_board`;
- `timeline`;
- `map`;
- `text_note`.

Cada elemento deve ter ID unico e contrato proprio.

Exemplo:

```text
cotacoes.kpi.produtos_cotados
impacto.table.top_ids_imp_cot
estoque.chart.dias_por_filial
```

### 5. Sub-elementos

Sub-elementos sao as partes internas de cada elemento.

Exemplo: um KPI nao e apenas um numero. Ele pode conter:

- titulo;
- valor principal;
- subtitulo;
- delta;
- contador auxiliar;
- tag;
- icone;
- origem do dado;
- tooltip;
- mini sparkline;
- estado de alerta.

Uma tabela tambem pode ter sub-elementos:

- titulo;
- subtitulo;
- toolbar;
- busca local;
- colunas;
- celulas formatadas;
- badges;
- barras de progresso;
- paginacao;
- linha expansivel;
- acoes por linha.

Essa anatomia deve ser pre-definida em uma tabela de estruturas de dados para garantir consistencia.

### 6. Layout

O layout deve ser configuravel em grade de 16 colunas.

Motivo:

- melhora divisao em metades, quartos, oitavos e combinacoes pares;
- evita a dependencia natural de grid 12 com multiplos de 3;
- facilita telas densas de BI;
- permite paines mais flexiveis sem quebrar proporcao visual.

Modelo:

```yaml
layout:
  grid:
    columns: 16
    row_height: 24
  items:
    - element: impacto.kpi.impacto_total
      col_start: 1
      col_span: 4
      row_start: 1
      row_span: 3
```

### 7. Abas

As abas devem manter exatamente a nomenclatura do design v4:

1. Resumo
2. Oportunidades
3. Categorias
4. Filiais
5. Estoque
6. Fornecedor
7. Produtos
8. Cotações
9. Impacto
10. Inflação
11. Fiscal
12. Financeiro
13. Adiantamentos
14. Serviços
15. Dados

## Modo edição

O BI deve prever um modo edicao para reposicionamento visual sem escrita manual.

### Objetivo

Permitir que o usuario autorizado:

- arraste elementos com mouse;
- redimensione blocos;
- oculte ou exiba elementos;
- reorganize a ordem visual;
- duplique um elemento;
- salve rascunho;
- publique layout;
- reverta alteracoes.

### Regras

- O modo edicao altera apenas arquivos/configuracoes de layout, nao formulas nem credenciais.
- Toda alteracao deve persistir em uma estrutura versionavel.
- O layout publicado deve ter versao.
- Deve existir diferenca entre `draft` e `published`.
- Deve haver validacao antes de publicar.

### Interacoes previstas

- drag-and-drop com snap na grade de 16 colunas;
- resize por alcas laterais;
- guias de alinhamento;
- undo/redo;
- lock/unlock de elemento;
- reset da aba para layout padrao;
- painel lateral de propriedades do elemento;
- pre-visualizacao desktop/tablet/mobile.

## Contrato de elemento

Todo elemento deve ter, no minimo:

```yaml
id: impacto.table.top_ids_imp_cot
tab: Impacto
type: table
title: Top IDs por IMP_COT
dataset: impacto_cotacao_por_id
data_bindings:
  rows: impacto_cotacao_por_id
sub_elements:
  - id: title
    type: text.title
    value: Top IDs por IMP_COT
  - id: origin
    type: text.origin
    value: "Origem Zoho: IMP_COT_ID"
layout:
  col_start: 1
  col_span: 16
  row_start: 4
  row_span: 8
```

## Tabela de estruturas de sub-elementos

| Tipo | Uso | Dados esperados | Design token |
|---|---|---|---|
| `text.title` | Titulo do elemento | texto curto | `typography.card_title` |
| `text.subtitle` | Contexto do elemento | texto medio | `typography.card_subtitle` |
| `text.origin` | Origem tecnica | nome de view/fonte | `typography.origin` |
| `metric.primary` | Numero principal | valor numerico ou texto | `metric.primary` |
| `metric.secondary` | Numero auxiliar | valor numerico ou texto | `metric.secondary` |
| `metric.delta` | Variacao | valor + direcao | `metric.delta` |
| `tag.status` | Status operacional | label + severidade | `badge.status` |
| `tag.filter` | Filtro aplicado | label + estado | `badge.filter` |
| `counter` | Contador pequeno | numero + label | `counter.default` |
| `icon` | Sinal visual | nome do icone | `icon.default` |
| `sparkline` | Tendencia compacta | serie temporal curta | `chart.sparkline` |
| `legend` | Legenda de grafico | itens + cores | `chart.legend` |
| `table.column` | Coluna de tabela | campo, label, formato | `table.column` |
| `table.cell_badge` | Celula com badge | valor + severidade | `table.badge_cell` |
| `table.cell_bar` | Celula com barra | valor percentual | `table.bar_cell` |
| `action.button` | Acao do usuario | label + acao | `button.default` |
| `tooltip` | Ajuda contextual | texto | `tooltip.default` |
| `empty_state` | Estado sem dados | titulo + texto | `state.empty` |
| `loading_state` | Estado carregando | mensagem | `state.loading` |
| `error_state` | Estado de erro | mensagem + acao | `state.error` |

## Contrato de layout em 16 colunas

Cada item posicionado deve conter:

- `element`;
- `col_start`;
- `col_span`;
- `row_start`;
- `row_span`;
- `min_height`;
- `visibility`;
- `locked`;
- `breakpoints`.

Exemplo:

```yaml
element: resumo.kpi.total_comprado
col_start: 1
col_span: 4
row_start: 1
row_span: 3
min_height: 96
locked: false
visibility: visible
breakpoints:
  tablet:
    col_start: 1
    col_span: 8
  mobile:
    col_start: 1
    col_span: 16
```

## Validacoes necessarias

Antes de publicar layout ou elementos, validar:

- todos os IDs sao unicos;
- toda aba existe no manifesto oficial;
- todo elemento aponta para dataset existente;
- toda metrica aponta para dataset e campos existentes;
- nenhum elemento usa fonte com segredo no frontend;
- `col_start + col_span - 1` nao passa de 16;
- `row_span` e `col_span` sao positivos;
- design tokens referenciados existem;
- formatos de numero, moeda, percentual e data estao definidos;
- componentes obrigatorios de erro/carregamento/vazio existem.

## Proxima implementacao recomendada

1. Criar `zoho/config/bi_suprimentos_modular_schema.yml`.
2. Transformar `zoho/docs/MAPA_ABAS_ELEMENTOS_BI_SUPRIMENTOS_V4.md` em manifesto inicial de elementos.
3. Criar validador Python para checar IDs, datasets, metricas, layout e tokens.
4. Criar renderer inicial que leia o manifesto e monte uma pagina simples.
5. Depois adicionar modo edicao com drag-and-drop e persistencia de layout.

