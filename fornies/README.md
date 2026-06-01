# Projeto Fornecedores

Repositorio inicial para analise cadastral, fiscal e economica da base de fornecedores das empresas do grupo.

O foco deste projeto e transformar as bases atuais em uma camada analitica confiavel para responder, entre outras, estas perguntas:

1. como esta a qualidade do cadastro de cada fornecedor;
2. qual e o enquadramento fiscal de cada fornecedor;
3. qual fornecedor tende a gerar ou nao gerar credito tributario relevante a partir da virada operacional de 2027;
4. como comparar fornecedores do mesmo produto considerando preco, historico de compra e potencial de credito.

## 1. Visao executiva

As tres bases informadas pelo negocio ja permitem iniciar um trabalho forte de estruturacao:

- `data/FORNECEDORES - TODAS AS EMPRESAS.xlsx`: cadastro mestre dos fornecedores;
- `data/CURVA_FORN_-_TODAS.csv`: curva de fornecedor por compra;
- `data/NFE.csv`: historico de notas fiscais de entrada.

O levantamento inicial mostrou:

- `25.554` linhas de cadastro distribuidas entre `IDEAL`, `MELHOR` e `POMME`;
- `15.718` CNPJs unicos no cadastro mestre;
- `237.931` linhas na base de NFe;
- `3.280` fornecedores unicos com movimento na base de NFe;
- `1.621` fornecedores na curva;
- `9.579` CNPJs compartilhados por pelo menos duas empresas do grupo.

Isso indica que o primeiro trabalho nao deve ser "comparar preco". O primeiro trabalho deve ser:

1. normalizar a identidade do fornecedor;
2. medir completude cadastral;
3. reconciliar cadastro x NFe x curva;
4. enriquecer o cadastro com dados externos por CNPJ;
5. so depois calcular comparativos economico-tributarios.

## 2. Direcao fiscal 2026-2027

Com base em fontes oficiais consultadas em `2026-05-20`:

- `2026` e ano de teste da Reforma Tributaria do Consumo;
- a partir de `01/01/2026`, os documentos fiscais eletronicos passam a destacar `CBS` e `IBS`;
- em `2026`, quem cumprir as obrigacoes acessorias fica dispensado do recolhimento de `CBS` e `IBS` no periodo de testes;
- em `01/01/2027`, a `CBS` entra em vigor, `PIS/Cofins` sao extintos e o tratamento do fornecedor passa a impactar diretamente o credito do adquirente;
- no `Simples Nacional`, o fornecedor pode permanecer no regime unico ou optar pela apuracao regular de `IBS/CBS`, e essa escolha altera a logica de credito para o comprador.

Ponto central para este projeto:

o potencial de credito em 2027 nao depende apenas do produto e do preco. Ele depende tambem:

- do regime do fornecedor;
- da situacao cadastral e fiscal do fornecedor;
- da classificacao tributaria da operacao;
- do tratamento do item no documento fiscal.

## 3. Documentos de continuidade

Em uma nova retomada, ler nesta ordem:

1. `docs/DIARIO_DE_BORDO.md`
2. `README.md`
3. `docs/PLANO_DE_ACAO.md`
4. `docs/ESTUDO_CENARIO_FISCAL_2026_2027.md`
5. `docs/LEVANTAMENTO_BASES_INICIAIS.md`

## 4. Governanca de documentacao

Este repositorio deve preservar continuidade entre conversas, decisoes tecnicas e entregas visuais.

- Toda modificacao relevante deve atualizar `docs/DIARIO_DE_BORDO.md` no mesmo momento em que a alteracao for feita.
- O diario deve registrar detalhes tecnicos, arquivos alterados, decisoes, riscos, resultados de testes e proximos passos.
- Quando um assunto, ciclo ou frente de trabalho for concluido, o `README.md` deve ser atualizado de forma ampla e generica, deixando claro o estado atual do projeto para uma nova retomada.
- O `README.md` nao deve substituir o diario: ele resume a direcao do projeto; o diario preserva o historico tecnico.

## 5. BI Suprimentos e design padrao

A frente de BI de Suprimentos vive dentro de `zoho/` e usa o Zoho Analytics como fonte de dados de referencia.

Referencias canonicas de design:

- `zoho/design/BI Suprimentos v4.html`: modelo padrao de pagina para o BI de Suprimentos.
- `zoho/design/BI Design System.html`: sistema de design padrao para novas geracoes de telas, mockups e componentes de BI.
- `zoho/docs/MAPA_ABAS_ELEMENTOS_BI_SUPRIMENTOS_V4.md`: mapa funcional das 15 abas do BI v4, com KPIs, graficos, relatorios e tabelas por guia.
- `zoho/docs/ARQUITETURA_MODULAR_BI_SUPRIMENTOS.md`: arquitetura modular do BI, cobrindo fontes, datasets, metricas, elementos, sub-elementos, layout em 16 colunas e modo edicao.
- `zoho/config/bi_suprimentos_modular_schema.yml`: primeiro contrato conceitual em YAML para padronizar elementos, sub-elementos e posicionamento.
- `zoho/config/bi_suprimentos_impacto_poc.yml`: primeira configuracao funcional de POC modular, usando dados reais do Zoho para a aba `Impacto`.
- `zoho/scripts/build_modular_impacto_poc.py`: gerador HTML standalone da POC modular de impacto, com filtros vivos, KPIs, graficos, tabela, grid de 16 colunas e modo edicao.

Todo novo design de BI deve partir dessas referencias canonicas, salvo decisao explicita registrada no diario.

Primeira POC funcional:

- A POC modular da aba `Impacto` gera `zoho/output/modular_test/bi_impacto_modular_poc.html` a partir de dados reais exportados do Zoho.
- Os artefatos em `zoho/output/` sao locais e ignorados pelo Git; para regerar, usar `python zoho/scripts/build_modular_impacto_poc.py`.
- Para atualizar a fonte diretamente no Zoho antes de gerar a pagina, usar `python zoho/scripts/build_modular_impacto_poc.py --refresh-zoho`, com `zoho/zoho.env` configurado localmente.
- Esta POC serve como referencia tecnica para expandir a arquitetura modular para as demais abas do BI v4.

## 6. Scripts iniciais

- `scripts/inventario_fontes.py`: gera um inventario reproduzivel das tres bases e mede cobertura entre cadastro, curva e NFe.
- `scripts/build_supplier_base.py`: gera base cadastral normalizada, base unificada por CNPJ, relatorio de pendencias e resumo cadastral.
- `scripts/build_supplier_reconciliation.py`: cruza cadastro unificado com `NFE` e `CURVA_FORN`, gera fila de saneamento prioritario e lista fornecedores com movimento fora do cadastro reconciliado.
- `scripts/enrich_suppliers_opencnpj.py`: consulta `OpenCNPJ` com cache local e produz enriquecimento cadastral/fiscal inicial da fila prioritaria.
- `scripts/build_comparison_bridge.py`: monta a ponte entre a linha original do cadastro e os resultados produzidos nas fases seguintes.
- `scripts/build_visual_review_pack.py`: gera planilhas visuais de antes/depois, planilha de retorno no formato original e painel HTML interativo.
- `scripts/build_supplier_audit_panel.py`: gera um novo painel HTML de auditoria, preservando todos os registros da planilha original, com filtros completos, linhas compactas e detalhe expansivel.
- `scripts/build_opencnpj_address_export.py`: materializa campos de endereco e contato existentes no cache bruto da `OpenCNPJ` em novo CSV enriquecido.
- `scripts/build_supplier_audit_panel_v05.py`: gera a versao 05 do painel de auditoria, baseada na versao 04 e adicionando endereco/contato e filtro por UF cadastral.

## 7. Estrutura de dados

- `data/`: fontes brutas oficiais do projeto.
- `docs/`: diario, estudos e plano.
- `zoho/`: frente de BI Suprimentos, integracao Zoho Analytics, estudos, scripts, testes e materiais de design.
- `zoho/design/`: referencias canonicas de design do BI; inclui o modelo de pagina e o sistema de design padrao.
- `output/fase_01_cadastro/`: artefatos da fase cadastral.
  - `01_fornecedores_cadastro_normalizado.csv`
  - `02_fornecedores_cadastro_unificado.csv`
  - `03_fornecedores_pendencias_cadastrais.csv`
  - `04_fornecedores_resumo_cadastral.json`
- `output/fase_02_reconciliacao/`: artefatos da fase de cruzamento entre cadastro, NFe e curva.
  - `01_fornecedores_reconciliados_movimento.csv`
  - `02_fornecedores_prioridade_saneamento.csv`
  - `03_fornecedores_movimento_sem_cadastro.csv`
  - `04_fornecedores_reconciliacao_resumo.json`
- `output/fase_03_enriquecimento/`: artefatos da fase de enriquecimento externo e cache da `OpenCNPJ`.
  - `01_fornecedores_opencnpj_enriquecidos_lote_completo.csv`
  - `02_fornecedores_opencnpj_enriquecidos_lote_completo_resumo.json`
  - `03_fornecedores_classificacao_fiscal_inicial_lote_completo.csv`
  - `04_fornecedores_classificacao_fiscal_inicial_lote_completo_resumo.json`
  - `05_mapa_comparacao_original_para_fases.csv`
  - `06_fornecedores_opencnpj_enriquecidos_lote_completo_com_endereco.csv`
  - `99_cache_opencnpj/`
- `output/fase_04_visualizacao/`: artefatos visuais para leitura humana e retorno ao BD.
  - `01_antes_depois_visual_fornecedores.xlsx`
  - `02_fornecedores_formato_original_com_campos_gvg.xlsx`
  - `03_painel_interativo_fornecedores.html`
  - `04_painel_auditoria_fornecedores.html`
  - `05_painel_auditoria_fornecedores_endereco.html`

## 8. Convencoes importantes

- codigos iniciados por `J` representam fornecedor pessoa juridica e carregam `CNPJ` no restante do codigo.
- codigos iniciados por `F` representam fornecedor pessoa fisica e carregam `CPF` no restante do codigo.
- codigos com outros prefixos devem ser tratados como excecao operacional ate melhor classificacao.

## 9. Proximo passo

Com a Fase 4 consolidada, o proximo passo oficial do projeto e transformar a classificacao inicial em regra fiscal operacional:

- revisar os `813` casos ainda com `regime_indiciado = indeterminado`;
- separar fila fiscal de PJ/CNPJ da fila operacional de PF/CPF;
- definir regra final de `potencial_credito_2027` por regime e qualidade do dado;
- construir a camada de comparacao economico-tributaria por produto.

## 10. Como enxergar o antes e depois

- Para leitura visual de saneamento e enriquecimento, abrir `output/fase_04_visualizacao/01_antes_depois_visual_fornecedores.xlsx`.
- Para devolver ao BD uma planilha no mesmo formato do cadastro original, abrir `output/fase_04_visualizacao/02_fornecedores_formato_original_com_campos_gvg.xlsx`.
- Para navegacao interativa com filtros, abrir `output/fase_04_visualizacao/03_painel_interativo_fornecedores.html`.
- Para auditoria operacional mais completa, abrir `output/fase_04_visualizacao/04_painel_auditoria_fornecedores.html`.
- Para auditoria com endereco/contato da OpenCNPJ e filtro por UF cadastral, abrir `output/fase_04_visualizacao/05_painel_auditoria_fornecedores_endereco.html`.

Na versao atual do painel de auditoria:

- os filtros categorizados sao de multipla escolha, com `Todos` como estado inicial;
- em filtros de multipla escolha, `Todos` marca todas as opcoes; ao retirar uma opcao, o filtro passa a restringir; ao desmarcar `Todos`, nenhuma opcao fica ativa;
- filtros em uso ficam destacados visualmente;
- o seletor de `Campos` fica junto dos filtros, sem modal separado;
- os icones `(?)` explicam filtros, colunas, escolhas e tags;
- a paginacao fica no box antes usado por `Valor curva`;
- a linha principal exibe fornecedor consolidado, tags de empresa e CNPJ/CPF formatado;
- o detalhe expansivel organiza tags por assunto: cadastro original, dados incluidos, fiscal/credito e operacao/saneamento;
- o box de operacao mostra apenas sinais ligados a movimento, curva e impacto de compra, nao pendencias cadastrais como telefone, site ou grupo fiscal;
- os codigos internos e ocorrencias por empresa continuam preservados nos dados, mas nao poluem a leitura principal do detalhe.

Regra visual usada nos entregaveis da fase 4:

- colunas `ANTES_*`: laranja;
- colunas `DEPOIS_*`: azul;
- colunas de analise: verde claro;
- campos novos `GVG_*` na planilha de retorno: azul;
- alertas de risco ou validacao: amarelo, vermelho ou cinza conforme o caso.
