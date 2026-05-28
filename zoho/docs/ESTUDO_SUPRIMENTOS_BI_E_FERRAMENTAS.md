# Estudo - BI de Suprimentos a partir do Zoho Analytics

Gerado em: `2026-05-27`.

## Objetivo

Analisar o inventario do workspace `SUPRIMENTOS` do Zoho Analytics, entender a estrutura de dados disponivel e propor ferramentas/paineis que podem ser construidos a partir dela, aproveitando o trabalho ja feito no projeto de fornecedores.

## Artefatos analisados

- `zoho/docs/INVENTARIO_ZOHO_ANALYTICS_WORKSPACES.md`
- `zoho/output/zoho_analytics_inventory/zoho_views_inventory.csv`
- `zoho/output/suprimentos_profile/suprimentos_sources_profile.csv`
- `zoho/output/suprimentos_profile/suprimentos_source_row_counts.csv`
- `zoho/docs/PERFIL_DADOS_SUPRIMENTOS.md`
- `data/NFE.csv`
- `data/CURVA_FORN_-_TODAS.csv`
- `data/CURVA_ABC_FORN_-_TOTAL.xlsx`
- `output/08_regime_fiscal/11_fornecedores_08b_auditoria_simplificada.csv`

## Resumo executivo

O workspace `SUPRIMENTOS` ja contem um BI operacional relevante. Ele nao e apenas um conjunto de graficos: possui uma camada de dados estruturada com `21` tabelas base, `32` query tables, `72` pivots, `31` analysis views, `8` dashboards e `1` summary view.

O ponto mais importante: as `QueryTable` do Zoho ja funcionam como uma camada semantica intermediaria. Elas consolidam empresas, enriquecem compras com curvas ABC, PMP, inflacao, cotacoes, fornecedores oficiais, filiais e dimensoes gerenciais. Portanto, o melhor caminho nao e reconstruir tudo do zero; e usar essas query tables como fonte transacional inicial, testar a qualidade delas e cruzar com a base fiscal/cadastral enriquecida que ja construimos neste repositorio.

Diagnostico central:

- O Zoho tem a camada operacional/economica de suprimentos.
- O projeto atual tem a camada cadastral/fiscal/credito 2027 dos fornecedores.
- A oportunidade esta em unir as duas camadas por fornecedor, produto, filial, periodo e categoria.

## Inventario de SUPRIMENTOS

Distribuicao de objetos:

| Tipo | Quantidade |
|---|---:|
| Table | 21 |
| QueryTable | 32 |
| Pivot | 72 |
| AnalysisView | 31 |
| Dashboard | 8 |
| SummaryView | 1 |
| Total | 165 |

Dashboards existentes no Zoho:

- `PAINEL RESUMO`
- `PAINEL FORNECEDOR`
- `PAINEL PRODUTOS`
- `PAINEL COTAÇÃO`
- `PAINEL INFLAÇÃO`
- `PAINEL ADIANTAMENTO`
- `PAINEL CP`
- `PAINEL SERVIÇOS`

Isso sugere que o BI atual ja se organiza em oito temas principais: resumo executivo, fornecedor, produto, cotacao, inflacao/preco, adiantamento, contas a pagar e servicos.

## Fontes de dados amostradas

Foram amostradas `53` fontes (`Table` e `QueryTable`) com `limit 5`; todas retornaram com sucesso.

Tambem foi executado `count(*)` para medir o volume de cada fonte.

Maiores fontes por volume:

| Fonte | Tipo | Linhas |
|---|---|---:|
| `NFE` | QueryTable | 239.694 |
| `ENTRADA DE NOTAS - [TODAS]` | QueryTable | 238.866 |
| `NFE - IDEAL` | Table | 163.759 |
| `COT` | QueryTable | 159.886 |
| `NF COM ITENS - CONSOLIDADO` | QueryTable | 118.176 |
| `CP` | Table | 116.933 |
| `PMP_ID` | QueryTable | 115.190 |
| `INFLAÇÃO` | QueryTable | 115.190 |
| `PMP_ID_INF` | QueryTable | 115.190 |
| `COT - IDEAL` | Table | 113.960 |
| `NF ADT - IDEAL` | Table | 81.666 |
| `PMP_PROD_INF` | QueryTable | 79.844 |
| `NF COM ITENS - IDEAL` | Table | 78.466 |
| `NUM_COT` | QueryTable | 66.491 |
| `COT_MIN_FORN` | QueryTable | 66.311 |

## Dominios de dados identificados

### 1. Compras / notas fiscais

Fontes principais:

- `NFE`
- `ENTRADA DE NOTAS - [TODAS]`
- `NF COM ITENS - CONSOLIDADO`
- `NFE - IDEAL`
- `NFE - MELHOR`
- `NFE - SUPERA`
- `NF COM ITENS - IDEAL`
- `NF COM ITENS - ME`
- `NF COM ITENS - SU`

Campos recorrentes:

- Empresa/filial: `NMEMP`, `UF`, `CDFILIAL`, `NMFILIAL`, `FI.NEGOCIO`, `FI.SIGLA`.
- Fornecedor: `CDFORNECED`, `NMRAZSOCFORN`, `NMFANTFORN`, `CDFORNECED_OFICIAL`, `FANTASIA_OFICIAL`, `RAZAO_OFICIAL`.
- Produto: `ID`, `CDPRODUTO`, `NMPRODUTO`, `CDPRODESTO`, `NMPRODUTO_EST`, `CDPRODUTO_OFICIAL`, `NMPRODUTO_OFICIAL`.
- Categoria: `CAT1` a `CAT5`.
- Tempo: `MESANO`, `MES`, `SGMES`, `ANO`, e em notas com itens tambem `DTENTRADA`, `DTEMISSAO`.
- Valor/quantidade: `VLRUNITPOND`, `VLRUNIT`, `QTDE_EST`, `TOTAL`.
- Enriquecimento analitico: `CURVA_PROD`, `POS_PROD`, `CURVA_FORN`, `POS_FORN`, `CURVA_ID`, `POS_ID`, `PMP_*`, `IMP_*`, `INF_*`, `PRE_MIN_COT`, `FORN_MIN_COT`.

Leitura: `NFE` e `NF COM ITENS - CONSOLIDADO` sao os principais fatos de compras. A diferenca provavel e que `NFE` esta mais agregada/analitica por item-mes/produto, enquanto `NF COM ITENS - CONSOLIDADO` preserva dados de nota, chave, numero e datas.

### 2. Cotacoes

Fontes:

- `COT`
- `COT - IDEAL`
- `COT - MELHOR`
- `COT - SUPERA`
- `COT_MIN_FORN`
- `NUM_COT`
- `[RC] COTAÇÃO DE PREÇOS - OLD`

Campos principais:

- Produto/categoria: `ID`, `CDPRODUTO`, `NMPRODUTO`, `CDPRODUTO_EST`, `NMPRODUTO_EST`, `CAT1` a `CAT5`.
- Fornecedor: `CDFORNECED`, `NMRAZSOCFORN`, `NMFANTFORN`.
- Preco: `PRECOUNIT`, `PRECOUNIT_EST`, `PRECOUNIT_COT`, `MIN_COT`, `MED_COT`, `MAX_COT`.
- Competitividade: `FORN_MENOR_PRECO`, `CNPJ_MENOR_PRECO`, `QTD_COT`.
- Curvas: `CURVA_PROD`, `CURVA_FORN`, `CURVA_ID`, respectivas posicoes.

Leitura: aqui mora o potencial de ferramenta de negociacao. Da para comparar preco comprado x menor cotacao x preco medio historico x fornecedor atual.

### 3. Curva ABC e consumo

Fontes:

- `CURVA ABC FORN - TOTAL`
- `CURVA FORN - TODAS`
- `CURVA PROD - TODAS`
- `CURVA PROD - IDEAL`
- `CURVA PROD - MELHOR`
- `CURVA PROD - SUPERA`
- `CURVA ID - TODAS`

Campos:

- Fornecedor/produto/id: `CDFORNECED`, `RAZAO_SOCIAL`, `CDPRODESTO`, `NMPRODUTO_OFICIAL`, `TE.ID`.
- Valor: `TOT_FORN`, `TOT_ITEM`.
- Ranking: `PERC`, `TOT_ACUM`, `CURVA`, `POS`.

Leitura: essas fontes sao a espinha dorsal de priorizacao. Elas definem o que e material para compras, fornecedor, produto e ID.

### 4. Preco medio, impacto e inflacao

Fontes:

- `INFLAÇÃO`
- `PMP_ID`
- `PMP_ID_INF`
- `PMP_ID_INF_12`
- `PMP_PROD`
- `PMP_PROD_INF`
- `PMP_PROD_INF_12`

Campos:

- Produto/ID: `ID`, `NMPRODUTO_EST`, `CDPRODUTO_OFICIAL`, `NMPRODUTO_OFICIAL`.
- Periodo: `MESANO`, `ANO`.
- Curva/categoria: `CAT1`, `CAT2`, `CAT3`, `CURVA_ID`, `CURVA_PROD`.
- Precos: `PMP_0` a `PMP_12`, `PMP_ID`, `PMP_PROD`.
- Inflacao/impacto: `SOMA_INF_*`, `PERC_INF_*`, `IMP_ID`, `IMP_COT`, `IMP_PRODT`.

Leitura: essa camada permite detectar alta de preco por produto/ID/categoria e diferenciar aumento real de mix, fornecedor ou falta de cotacao.

### 5. Contas a pagar

Fontes:

- `CP`
- `CP_MOV`
- `CP_SEMANA`
- `CP_SALDO_2025`
- `CP_SALDO_2026`
- `CP_SALDO_2026_v2`
- `TODAS - CONTAS A PAGAR`

Campos:

- Fornecedor: `CDFORNECED`, `NMFANTFORN`, `NMRAZSOCFORN`.
- Datas: `DTEMISSAO`, `DTENTRSAID`, `DTORIGVENPAG`, `DTATUAVENPAG`, `DTBAIXAPAG`.
- Valores: `VRATUAPAG`, `VRBAIXAPAG`, `VRORIGPAG`, `ENTRA_DIVIDA_SEMANA`, `SAI_DIVIDA_SEMANA`, `SALDO_DIVIDA_SEMANA`.
- Status: `IDSTATUS`, `STATUSPAG`, `STATUS_VENC`, `FAIXA_DIAS`.
- Tipo: `CDTPCTPAGAR`, `DSTPCTPAGAR`.

Leitura: permite unir desempenho de suprimentos com pressao de caixa, risco de vencimento e negociacao de prazo.

### 6. Adiantamentos

Fontes:

- `ADIANTAMENTO_NFE`
- `AD_v1`
- `AD_v2`
- `AD_v3`
- `NF ADT - IDEAL`
- `NF ADT - MELHOR`
- `NF ADT - POMME VITA`

Campos:

- Conciliacao: `STATUS_CONC`, `STATUS_CONCILIACAO`, `VALOR_CONCILIADO`.
- Nota/adiantamento: `NRONOTA_NF`, `NRONOTA_AD`.
- Produto/fornecedor/periodo: mesmas dimensoes de NFE.

Leitura: e uma ferramenta natural para reconciliar nota x adiantamento, identificar valores pendentes e concentracao por fornecedor/produto/filial.

### 7. Filiais e geografia

Fontes:

- `FILIAIS`
- `FILIAIS_DRO`
- `FILIAIS_NEW`
- `FILIAIS_SUPPLY`

Campos:

- `EMPRESA`, `S_EMP`, `CDFILIAL`, `LOCAL`, `CLIENTE`, `SIGLA`, `NOME`, `ATIVA`, `NEGOCIO`, `REGIAO`, `AREA`, `CONTROLE`.
- Nas versoes DRO/NEW: endereco e coordenadas.

Leitura: camada de dimensao para segmentacao por filial, negocio, regiao, area e mapa.

### 8. Resultado gerencial / SUP x CMV

Fontes:

- `FAT_SUP`
- `TODAS - DRO SUM`
- `TIPOCONTA`

Campos:

- `SUP`, `CMV`, `FAT`.
- `VALOR_REAL`, `FAT_`, `CMV_`, `MDO_`, `ADM_`, `NOP_`, `INV_`, `RES_`.
- Classificacao financeira: `CDCLASSFINANC`, `NMCLASSFINANC`, `CDTPCTPAGAR`, `NMTPCTPAGAR`.

Leitura: conecta suprimentos com resultado economico, margem e participacao no CMV/faturamento.

## Modelo analitico recomendado

### Camada Bronze

Extrair do Zoho, sem transformar, as fontes principais:

- `NFE`
- `NF COM ITENS - CONSOLIDADO`
- `COT`
- `COT_MIN_FORN`
- `NUM_COT`
- `CURVA ABC FORN - TOTAL`
- `CURVA FORN - TODAS`
- `CURVA PROD - TODAS`
- `CURVA ID - TODAS`
- `INFLAÇÃO`
- `PMP_ID_INF_12`
- `PMP_PROD_INF_12`
- `CP`
- `CP_MOV`
- `CP_SEMANA`
- `AD_v3`
- `FILIAIS_SUPPLY`
- `TAB_PROD`
- `FAT_SUP`

### Camada Silver

Normalizar chaves e tipos:

- Fornecedor: `CDFORNECED`, nome fantasia, razao, documento/CNPJ quando disponivel.
- Produto: `ID`, `CDPRODESTO`, `CDPRODUTO_OFICIAL`, `NMPRODUTO_OFICIAL`.
- Filial: `NMEMP`, `CDFILIAL`, `SIGLA`, `NEGOCIO`, `REGIAO`.
- Tempo: `ANO`, `MES`, `MESANO`, datas reais quando existirem.
- Categoria: `CAT1` a `CAT5`.
- Medidas: quantidade, total, preco unitario, PMP, inflacao, impacto, cotacao minima.

### Camada Gold

Criar tabelas de consumo para os paineis:

- `fato_compras_item_mes`
- `fato_notas_item`
- `fato_cotacoes`
- `fato_contas_pagar`
- `fato_adiantamentos`
- `dim_fornecedor`
- `dim_produto`
- `dim_filial`
- `dim_tempo`
- `dim_categoria`
- `mart_fornecedor_360`
- `mart_produto_preco`
- `mart_oportunidades_negociacao`
- `mart_credito_fiscal_2027`

## Ferramentas possiveis

### 1. Control Tower de Suprimentos

Tela executiva com:

- Total comprado.
- Evolucao mensal.
- SUP x CMV x FAT.
- Top categorias.
- Top fornecedores.
- Inflacao/deflacao por categoria.
- Produtos com maior impacto.
- Filiais/regioes mais relevantes.
- Alertas de cotacao e preco.

Fonte principal: `NFE`, `FAT_SUP`, `INFLAÇÃO`, curvas ABC.

### 2. Fornecedor 360

Painel por fornecedor:

- Compras totais por periodo.
- Curva ABC e posicao.
- Categorias/produtos fornecidos.
- UFs/filiais atendidas.
- Historico de preco e inflacao.
- Cotacoes ganhas/perdidas.
- Menor cotacao comparada ao fornecedor comprado.
- Contas a pagar, saldo, vencidos e pagos.
- Adiantamentos conciliados/pendentes.
- Regime fiscal e potencial de credito 2027, vindo do projeto atual.
- Status cadastral/endereco/contato e inclusoes OpenCNPJ.

Este e o paralelo mais direto com o painel de fornecedores `08b`: o painel atual responde "quem e o fornecedor e qual seu risco fiscal/cadastral"; o Fornecedor 360 responderia "quanto compro, o que compro, como compro, quanto pago, qual risco e qual oportunidade".

### 3. Inteligencia de precos e inflacao

Ferramenta por produto/ID:

- PMP atual x 1, 3, 6, 12 meses.
- Inflacao por produto, ID, categoria, UF e fornecedor.
- Ranking de produtos com maior impacto em reais.
- Top deflacao.
- Itens com aumento sem suporte de cotacao.
- Itens em curva A com alta acima de limite.
- Comparacao entre empresa/UF/filial.

Fonte principal: `NFE`, `PMP_*`, `INFLAÇÃO`, `NUM_COT`, `COT_MIN_FORN`.

### 4. Motor de oportunidades de negociacao

Lista priorizada de oportunidades:

- Produto comprado acima da menor cotacao disponivel.
- Fornecedor atual nao e o menor cotado.
- Itens com poucas cotacoes.
- Curva A/AA/AAA com inflacao positiva.
- Fornecedor com alto valor e baixa concorrencia.
- Itens onde ha fornecedor alternativo recorrente.
- Compras concentradas em um unico fornecedor.

Essa ferramenta deve gerar uma fila: oportunidade, valor estimado, fornecedor atual, fornecedor alternativo, produto, categoria, periodo, justificativa e evidencia.

### 5. Auditoria de cotacoes

Controles:

- Numero de cotacoes por produto/periodo.
- Produtos sem cotacao.
- Cotacoes com apenas 1 fornecedor.
- Compras fora da menor cotacao.
- Comparativo por comprador, filial ou categoria, se a fonte tiver essa dimensao.
- Historico de fornecedores participantes.

Fonte principal: `COT`, `NUM_COT`, `COT_MIN_FORN`, `NFE`.

### 6. Analise de tail spend

Baseada no conceito de cauda longa: muitos itens e fornecedores pequenos representam baixo percentual do gasto, mas consomem complexidade operacional.

Aplicacao no nosso dado:

- Usar curva ABC de fornecedor/produto/ID.
- Separar curva A/AA/AAA do tail spend.
- Medir quantidade de fornecedores, produtos, notas e cotacoes na cauda.
- Propor consolidacao de fornecedores/produtos equivalentes.
- Identificar itens de baixa relevancia com alto custo operacional.

### 7. Contas a pagar + suprimentos

Ferramenta cruzando compras com financeiro:

- Saldo por fornecedor.
- Vencidos e a vencer por semana.
- Valor pago por semana.
- Fornecedores com alto saldo e alta criticidade de compras.
- Risco de ruptura por atraso de pagamento.
- Prazos e comportamento de pagamento por categoria.

Fonte principal: `CP`, `CP_MOV`, `CP_SEMANA`, `CP_SALDO_*`, curvas.

### 8. Conciliação de adiantamentos

Painel operacional:

- Valor adiantado x nota recebida.
- Status de conciliacao.
- Divergencia por fornecedor/produto/filial.
- Tempo entre adiantamento e entrada.
- Pendencias por valor e idade.

Fonte principal: `AD_v3`, `ADIANTAMENTO_NFE`, `NF ADT-*`.

### 9. Mapa geografico de suprimentos

Ferramenta geografica:

- Compras por UF/regiao.
- Fornecedores por UF.
- Produtos/categorias por regiao.
- Inflacao por UF.
- Concentracao geografica e risco logistico.
- Filiais com maior exposicao a determinado fornecedor/produto.

Fonte principal: `NFE`, `FILIAIS_DRO`, `FILIAIS_NEW`, `FILIAIS_SUPPLY`.

### 10. Simulador fiscal/economico 2027

Cruzar:

- Compras e produtos do Zoho.
- Regime fiscal e potencial de credito do projeto `08b`.
- Cadastro/endereco/risco cadastral.
- Valor comprado por fornecedor/produto/categoria.

Saida:

- Potencial de credito 2027 por fornecedor.
- Potencial por categoria/produto.
- Fornecedores `Indeterminado` com alto valor de compra.
- Simples/MEI com impacto relevante.
- Fila de validacao fiscal priorizada por valor comprado.

Esse e provavelmente o produto mais valioso por conectar o projeto atual com suprimentos.

### 11. Monitor de qualidade de dados

Testes automatizados:

- Fonte existe e exporta.
- Colunas esperadas presentes.
- Linha count nao caiu anormalmente.
- Chaves nulas em fornecedor/produto/filial.
- Meses recentes presentes.
- Duplicidades suspeitas por nota/item/produto.
- Divergencia entre `NFE` local e `NFE` Zoho.
- Cobertura de fornecedor no cadastro enriquecido.

### 12. Catálogo semantico do BI

Documento vivo:

- O que cada fonte representa.
- Nivel de granularidade.
- Colunas-chave.
- Medidas confiaveis.
- Dependencias entre tabelas/query tables.
- Dono/responsavel.
- Frequencia de atualizacao.
- Ultima validacao.

## Paralelos com o que ja temos

### O que ja existe neste repositorio

O projeto atual montou uma camada forte de fornecedor:

- Cadastro normalizado.
- Reconciliacao cadastro x NFE x curva.
- Enriquecimento OpenCNPJ.
- Endereco/contato preferencial.
- Regime fiscal e potencial de credito 2027.
- Painel HTML de auditoria com filtros, tags e detalhe expansivel.

Arquivos-chave:

- `output/08_regime_fiscal/11_fornecedores_08b_auditoria_simplificada.csv`
- `output/04_visualizacao/08b_painel_fornecedores_regime_fiscal.html`

### O que o Zoho adiciona

O Zoho traz a camada economica/operacional que faltava:

- Mais colunas analiticas em `NFE`: local tem `37` colunas; Zoho `NFE` tem `63`.
- Volume semelhante, mas ligeiramente atualizado: local `NFE.csv` tem `237.931` linhas; Zoho `NFE` tem `239.694`.
- Curva de fornecedor local tem `1.621` linhas; Zoho `CURVA FORN - TODAS` tem `1.642`.
- Nova camada de cotacao, PMP, inflacao, contas a pagar, adiantamentos, filial/geo e SUP x CMV.

### A uniao ideal

Chaves provaveis:

- `CDFORNECED` do Zoho com `codigo` ou codigo interno do cadastro.
- Documento/CNPJ da camada atual para enriquecer fornecedor.
- `CDPRODESTO`, `ID`, `CDPRODUTO_OFICIAL` para produto.
- `CDFILIAL`, `NMEMP`, `SIGLA` para filial.
- `MESANO`/`ANO` para tempo.

Tabela ponte necessaria:

- `bridge_fornecedor_zoho_cadastro`
  - `empresa`
  - `CDFORNECED`
  - `documento`
  - `codigo_interno`
  - `nome_zoho`
  - `nome_cadastro`
  - `status_match`

Essa ponte e critica. Sem ela, o BI economico fica separado do diagnostico fiscal/cadastral.

## Observacoes de arquitetura

O Zoho usa muitas QueryTables. Isso e bom porque ja existe logica de negocio codificada, mas tambem pode criar dependencia opaca. A propria documentacao da Zoho recomenda cuidado com muitas query tables, query table sobre query table, `SELECT *`, joins com duplicidade e excesso de colunas no `GROUP BY`, porque isso pode afetar performance e qualidade.

Para nosso BI, a recomendacao e:

1. Usar as QueryTables consolidadas como fonte inicial.
2. Exportar e testar localmente.
3. Criar uma camada propria documentada.
4. Evitar depender da estrutura visual dos dashboards do Zoho.
5. Preservar linhagem: qual tabela/query table originou cada indicador.

## Roadmap sugerido

### Fase 1 - Data lake local do Zoho

Criar script:

- `zoho/scripts/export_suprimentos_core.py`

Exportar periodicamente:

- `NFE`
- `NF COM ITENS - CONSOLIDADO`
- `COT`
- `COT_MIN_FORN`
- `NUM_COT`
- `CURVA ABC FORN - TOTAL`
- `CURVA FORN - TODAS`
- `CURVA PROD - TODAS`
- `CURVA ID - TODAS`
- `INFLAÇÃO`
- `PMP_ID_INF_12`
- `PMP_PROD_INF_12`
- `CP`
- `CP_MOV`
- `CP_SEMANA`
- `AD_v3`
- `FILIAIS_SUPPLY`
- `TAB_PROD`
- `FAT_SUP`

### Fase 2 - Testes de dados

Criar testes para:

- Colunas obrigatorias.
- Linha minima por fonte.
- Mes mais recente.
- Chaves nulas.
- Duplicidade.
- Cobertura fornecedor x cadastro.
- Cobertura produto x tabela produto.

### Fase 3 - Modelo unificado fornecedor + suprimentos

Criar:

- `mart_fornecedor_360.csv`
- `mart_produto_preco.csv`
- `mart_oportunidades_negociacao.csv`
- `mart_credito_fiscal_2027.csv`

### Fase 4 - Primeiro painel HTML

Usar a formatacao do painel de fornecedores, mas com navegacao por abas:

- Resumo.
- Fornecedores.
- Produtos.
- Cotacoes.
- Inflacao.
- Fiscal 2027.
- Contas a pagar.
- Adiantamentos.

### Fase 5 - Alertas e filas de acao

Gerar arquivos acionaveis:

- `fila_negociacao_preco.csv`
- `fila_fornecedor_alto_valor_indeterminado.csv`
- `fila_produto_curva_a_sem_cotacao.csv`
- `fila_adiantamento_pendente.csv`
- `fila_cp_fornecedor_critico.csv`

## Priorizacao das primeiras ferramentas

1. `Fornecedor 360 + Fiscal 2027`
   - Maior sinergia com o que ja temos.
   - Usa dados economicos do Zoho e dados fiscais/cadastrais do projeto.

2. `Oportunidades de negociacao`
   - Usa `NFE`, `COT`, `COT_MIN_FORN`, `NUM_COT`, `PMP`, `INFLAÇÃO`.
   - Gera fila objetiva com valor estimado.

3. `Produto / Preco / Inflacao`
   - Ataca um problema tipico de suprimentos: entender alta de preco por item/categoria.

4. `Curva ABC + tail spend`
   - Facil de construir e util para racionalizar fornecedor/produto.

5. `CP + Suprimentos`
   - Conecta risco operacional de fornecedor com caixa e pagamento.

## Fontes externas consultadas

- APQC - Procurement Key Benchmarks: https://www.apqc.org/resource-library/resource-collection/procurement-key-benchmarks
- APQC - Cycle time to issue a purchase order: https://www.apqc.org/resources/benchmarking/open-standards-benchmarking/measures/average-days-issue-purchase-order
- McKinsey - Category Analytics Solution: https://www.mckinsey.com/capabilities/operations/how-we-help-clients/category-analytics-solution
- McKinsey - Next generation operating model in procurement: https://www.mckinsey.com/capabilities/operations/our-insights/where-procurement-is-going-next
- McKinsey - Use procurement's data to power your performance: https://www.mckinsey.com/capabilities/operations/our-insights/use-procurements-data-to-power-your-performance
- McKinsey - Long tail, big savings: https://www.mckinsey.com.br/en/capabilities/operations/our-insights/long-tail-big-savings-digital-unlocks-hidden-value-in-procurement/pt-br
- McKinsey - Driving superior value through digital procurement: https://www.mckinsey.com/capabilities/operations/our-insights/driving-superior-value-through-digital-procurement
- Zoho Analytics - Query Tables: https://www.zoho.com/analytics/help/query-tables.html

## Conclusao

O workspace `SUPRIMENTOS` ja contem quase tudo que precisamos para construir um BI proprio mais inteligente que uma replica do Zoho. O caminho mais forte e combinar:

- a profundidade operacional/economica do Zoho;
- a camada fiscal/cadastral enriquecida deste projeto;
- testes automatizados para dar confianca;
- uma interface HTML no mesmo padrao visual do painel de fornecedores.

O primeiro produto recomendado e o `Fornecedor 360 + Fiscal 2027`, porque ele aproveita diretamente o trabalho ja validado e transforma fornecedores em uma visao economica, operacional, fiscal e acionavel.
