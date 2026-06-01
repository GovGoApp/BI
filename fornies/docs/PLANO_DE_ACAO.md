# Plano de Acao

Data-base: `2026-05-20`

## 1. Objetivo do projeto

Construir uma base analitica de fornecedores que permita:

1. medir qualidade cadastral;
2. enriquecer o cadastro com dados oficiais por `CNPJ`;
3. classificar enquadramento fiscal relevante para `2027`;
4. comparar fornecedores de mesmos produtos considerando preco e potencial de credito.

## 2. Principios de execucao

- `CNPJ normalizado` como chave canonica do fornecedor.
- `CDFORNECED` preservado como chave operacional do ERP/base interna.
- Separar claramente:
  - dado interno;
  - dado oficial externo;
  - inferencia analitica.
- Toda regra fiscal inferida deve ficar documentada e marcada como dependente de validacao da area fiscal.
- Primeiro saneamento e conciliacao. Depois comparacao economica.

## 3. Fases propostas

### Fase 0 - Preparacao de ambiente e governanca

Objetivo:

garantir ambiente reproduzivel e trilha de documentacao.

Entregas:

- ambiente virtual Python do projeto;
- dependencias fixadas;
- convencao de pastas com `data/` para fontes brutas oficiais e `output/` para artefatos gerados;
- diario de bordo atualizado a cada frente concluida.

Observacao:

- o ambiente global atual apresentou incompatibilidade `pandas` x `NumPy`, portanto o projeto deve nascer com ambiente isolado.

### Fase 1 - Normalizacao do cadastro mestre

Objetivo:

transformar o arquivo mestre em uma tabela canonica de fornecedores.

Entregas:

- parser do `FORNECEDORES - TODAS AS EMPRESAS.xlsx`;
- normalizacao de `CNPJ`, email, datas e codigos;
- consolidacao por empresa de origem;
- score de completude cadastral;
- sinalizacao do que falta por fornecedor.

Campos iniciais de interesse:

- empresa de origem;
- codigo interno do fornecedor;
- CNPJ;
- razao social;
- nome fantasia;
- inscricao estadual;
- inscricao municipal;
- data de cadastro;
- situacao cadastral interna;
- emails;
- indicadores internos ligados a fiscal, contribuicao e atividade.

### Fase 2 - Conciliacao entre cadastro, NFe e curva

Objetivo:

entender quem esta comprando, quem esta cadastrado e onde ha desalinhamento.

Entregas:

- tabela de cruzamento `cadastro x nfe x curva`;
- lista de fornecedores com movimento sem cadastro confiavel;
- lista de fornecedores cadastrados sem movimento;
- consolidacao de compra historica por fornecedor e por produto;
- conciliacao de codigos oficiais e internos.

Perguntas respondidas nesta fase:

- quais fornecedores mais relevantes nao estao bem cadastrados;
- quais fornecedores da curva nao possuem cadastro mestre reconciliado;
- quais fornecedores da NFe precisam de saneamento urgente.

### Fase 3 - Enriquecimento externo por CNPJ

Objetivo:

complementar o cadastro com dados oficiais externos.

Referencia tecnica local:

- `C:\\Users\\Haroldo Duraes\\Desktop\\Scripts\\GovGo\\v2\\src\\backend\\empresas\\core\\select_engine.py`
- `C:\\Users\\Haroldo Duraes\\Desktop\\Scripts\\GovGo\\v2\\src\\backend\\empresas\\core\\company_resolver.py`

Entregas:

- modulo local de consulta `OpenCNPJ`;
- retry, timeout e cache local;
- tabela de enriquecimento por `CNPJ`;
- captura de campos como situacao cadastral, natureza juridica, matriz/filial, CNAE, porte, `opcao_simples` e `opcao_mei`.

Risco:

- `OpenCNPJ` nao deve ser a unica fonte de decisao final; ela deve ser a camada inicial de enriquecimento.

### Fase 4 - Classificacao fiscal operacional para 2027

Objetivo:

transformar os dados enriquecidos em uma visao operacional para compras.

Entregas:

- tabela de enquadramento fiscal do fornecedor;
- classificacao preliminar de potencial de credito;
- sinalizacao de casos que exigem validacao fiscal manual;
- dicionario de regras fiscais adotadas.

Saidas sugeridas:

- `situacao_cadastral_oficial`
- `regime_indiciado`
- `simples_nacional`
- `mei`
- `matriz_filial`
- `potencial_credito_2027`
- `nivel_confianca_fiscal`
- `pendencias_para_validacao`

Importante:

- o potencial de credito nao deve ser calculado apenas pelo fornecedor; ele devera evoluir para fornecedor + operacao + item.

### Fase 5 - Comparativo de fornecedores por produto

Objetivo:

comparar fornecedores concorrentes do mesmo item/produto com visao economico-tributaria.

Entregas:

- base historica por `fornecedor x produto`;
- indicadores de preco medio, dispersao, recorrencia e cobertura geografica;
- ranking por produto considerando preco bruto e custo liquido estimado;
- destaque para fornecedores mais competitivos e para fornecedores com risco cadastral/fiscal.

Metricas sugeridas:

- preco medio historico;
- ultimo preco;
- desvio de preco;
- frequencia de compra;
- curva do fornecedor;
- potencial de credito;
- custo liquido estimado;
- score final ponderado.

## 4. Ordem recomendada de execucao

1. estabilizar ambiente Python;
2. implementar ingestao e normalizacao do cadastro mestre;
3. cruzar com `NFE` e `CURVA_FORN`;
4. adaptar a integracao `OpenCNPJ`;
5. criar classificacao fiscal operacional;
6. montar comparativos por produto.

## 5. Primeiras entregas tecnicas recomendadas

### Sprint 1

- parser do cadastro mestre;
- tabela normalizada de fornecedores;
- score de completude;
- relatorio de faltas cadastrais;
- relatorio de conciliacao inicial com `NFE` e `CURVA`.

### Sprint 2

- modulo `OpenCNPJ`;
- cache local das respostas;
- enriquecimento em lote dos fornecedores prioritarios;
- classificacao preliminar de enquadramento.

### Sprint 3

- comparativo por produto;
- calculo preliminar de impacto de credito;
- painel ou relatorio executivo por fornecedor.

## 6. Criterios de pronto da primeira etapa

A fase inicial pode ser considerada pronta quando existir:

1. uma base unica de fornecedores normalizados;
2. um score de completude por fornecedor;
3. uma lista objetiva do que falta em cada cadastro;
4. um cruzamento funcional entre cadastro, curva e NFe;
5. uma trilha documentada para enriquecimento e classificacao fiscal.
