# Prompt v3 para Claude Design - BI de Suprimentos

Voce vai criar a terceira versao do mock `BI de Suprimentos`.

Importante: nao sobrescreva as versoes anteriores.

Gere um novo arquivo:

`BI Suprimentos v3.html`

Use como base:

- `BI Suprimentos v2.html`
- `ANALISE_V3_ZOHO_VS_CLAUDE.md`
- `CATEGORIAS_I_D_A_ORDENADAS.md`

## Objetivo da v3

A v3 precisa ficar mais proxima dos paineis reais do Zoho Analytics.

Nao quero apenas uma tela bonita. Quero que os graficos, tabelas, KPIs, cards e pivots que existem no Zoho aparecam no BI criado por voce, organizados em uma experiencia melhor.

Preserve o que ficou bom na v2:

- visual operacional e compacto;
- cards brancos;
- fundo cinza claro;
- filtros no topo;
- abas navegaveis;
- chips de status;
- tabelas fortes;
- linha expandida;
- fila de oportunidades;
- aba Categorias;
- aba Servicos;
- busca global filtrando tabelas.

Mas corrija e expanda conforme as instrucoes abaixo.

## Entrega obrigatoria

Criar:

`BI Suprimentos v3.html`

Nao sobrescrever:

- `BI Suprimentos.html`
- `BI Suprimentos v2.html`

## Abas obrigatorias da v3

Use estas abas, nesta ordem:

1. Resumo Executivo
2. Oportunidades
3. Categorias
4. Filiais
5. Estoque por Filial
6. Fornecedor 360
7. Produtos e Precos
8. Cotacoes
9. Inflacao e Impacto
10. Fiscal
11. Financeiro
12. Adiantamentos
13. Servicos
14. Dados

Se as abas nao couberem, usar scroll horizontal.

## Regra de categorias obrigatoria

Corrija a categoria em cascata.

Use o arquivo:

`CATEGORIAS_I_D_A_ORDENADAS.md`

Ordem correta:

1. `I - INSUMOS`
2. `D - DESPESAS`
3. `A - ATIVOS`

Nao usar nos filtros principais:

- `F - FATURAMENTO`
- `V - VENDA BALCAO`

Dentro de cada nivel, ordenar por codigo, nunca por valor comprado.

Exemplos:

- `I0`, `I1`, `I2`, `I3`, `I4`, `I5`, `I6`.
- `D1`, `D2`, `D3`, `D4`, `D5`, `D6`, `D7`, `D8`.
- `A1`, `A2`.

Filtros em cascata:

- `CAT1` limita `CAT2`;
- `CAT2` limita `CAT3`;
- `CAT3` limita `CAT4`;
- `CAT4` limita `CAT5`.

Sempre manter opcao `Todas`.

## Filtros globais v3

Manter duas linhas de filtro:

Linha 1:

- Empresa
- Negocio
- Regiao
- UF
- Filial
- Periodo
- Fornecedor
- Produto/ID

Linha 2:

- CAT1
- CAT2
- CAT3
- CAT4
- CAT5
- ABC fornecedor
- ABC produto
- ABC ID
- Status cotacao
- Status CP
- Status AD
- Tipo de alerta

Filtros devem simular funcionamento:

- alterar estado visual;
- atualizar chips aplicados;
- filtrar tabelas visiveis;
- resetar filhos em cascata nas categorias.

## Resumo Executivo v3

Representar estes componentes do Zoho:

- `SUP por GEO - N e NE`
- `SUP por GEO - S e SE`
- `CAT por MES`
- `CAT por UF`
- `CAT_UF`
- `RESUMO NEGOCIOS`
- `RESUMO_FILIAL`
- `RESUMO - FORN`

Criar blocos:

- KPIs executivos;
- Geografia N/NE;
- Geografia S/SE;
- Categoria x Mes;
- Categoria x UF;
- Tabela `CAT_UF`;
- Tabela `RESUMO NEGOCIOS`;
- Tabela `RESUMO_FILIAL`;
- Tabela `RESUMO - FORN`;
- Alertas executivos.

## Oportunidades v3

Manter a fila de oportunidades da v2, mas separar tipo de risco:

- oportunidade economica;
- risco fiscal;
- risco financeiro;
- risco de estoque;
- saneamento de dados.

Adicionar filtros/chips:

- acima da menor cotacao;
- cotacoes <= 3;
- inflacao curva A;
- estoque baixo;
- estoque excessivo;
- CP vencido;
- AD pendente;
- fiscal pendente.

## Categorias v3

Transformar a aba em centro de comando da hierarquia.

Adicionar cards/pivots inspirados no Zoho:

- `TOTAL POR CAT`
- `Resumo CAT`
- `RESUMO CATEGORIAS`
- `PMP por CAT`
- `CONTAGEM DE COTACOES por CAT`
- `INFLACAO POR CAT`
- `AD por CAT`
- `CAT por MES`
- `CAT por UF`
- `CAT_UF`

Componentes:

- arvore CAT1 > CAT2 > CAT3 > CAT4 > CAT5;
- ranking por valor;
- ranking por impacto;
- ranking por inflacao;
- cotacoes por categoria;
- AD por categoria;
- CP por categoria;
- categoria x UF;
- categoria x mes;
- categoria x fornecedor;
- categoria x produto.

## Nova aba Filiais

Criar uma aba propria para gestao de compra por filial.

Base Zoho:

- `RESUMO_FILIAL`
- `RESUMO FILIAL`
- `SUP por FILIAL`
- `SUP_x_CMV`
- campos de `NFE`: `CDFILIAL`, `NMFILIAL`, `UF`, `FI.NEGOCIO`, `FI.SIGLA`, `TOTAL`, `QTDE_EST`, `CAT1` a `CAT5`.

KPIs:

- total comprado;
- filiais ativas;
- compra media por filial;
- maior filial;
- maior UF;
- maior negocio;
- impacto por filial;
- oportunidade por filial.

Visualizacoes:

- ranking de filiais;
- filial x categoria;
- filial x fornecedor;
- filial x produto;
- filial x mes;
- filial x UF/negocio;
- drilldown filial -> categoria -> produto -> fornecedor.

## Nova aba Estoque por Filial

Estoque nao esta no workspace `SUPRIMENTOS`.

Foi encontrado no workspace `APURACAO DE RESULTADOS`.

Views:

- `MOV.ESTOQUE - SINTETICO (RC)` - 3.174 linhas
- `MOV.ESTOQUE - SINTETICO (ME)` - 400 linhas
- `MOV.ESTOQUE - SINTETICO (SU)` - 1.119 linhas
- `ANALISE DE ESTOQUE - IDEAL`
- `ANALISE DE ESTOQUE - MELHOR`
- `ANALISE DE ESTOQUE - POMME VITA`
- `MOV. DE ESTOQUE ANALITICO - IDEAL`
- `MOV. DE ESTOQUE ANALITICO - MELHOR`
- `MOV. DE ESTOQUE SINTETICO - IDEAL`

Colunas de estoque:

- `FILIAL`
- `MES`
- `ANO`
- `GRUPO PRODUTO`
- `Estoque Inicial`
- `Entradas`
- `Saidas`
- `Ajustes`
- `Implantacao`
- `Estoque Final`
- `Total do Consumo (CMV)`
- `Consumo/Dia`
- `Dias de Estoque`

Criar KPIs:

- estoque final;
- entradas;
- saidas;
- consumo/CMV;
- consumo por dia;
- dias de estoque medio;
- filiais com estoque baixo;
- filiais com estoque excessivo;
- estoque negativo;
- ajustes relevantes.

Visualizacoes:

- estoque por filial;
- estoque por grupo produto;
- dias de estoque por filial;
- estoque final x consumo/dia;
- entradas x saidas x ajustes;
- compras x consumo/CMV;
- ranking de filiais criticas;
- matriz filial x grupo produto;
- detalhe mensal por filial.

Regras visuais:

- `Dias de Estoque < 7`: vermelho, risco de ruptura.
- `7 a 15`: amarelo, atencao.
- `15 a 45`: verde, saudavel.
- `> 60`: azul/cinza, possivel excesso.
- `Estoque Final negativo`: vermelho forte.

## Fornecedor 360 v3

Representar estes componentes Zoho:

- `FORNECEDORES IMPACTO sobre COTACAO`
- `FORNECEDORES e PRODUTOS - IMPACTO`
- `FORNECEDORES INFLACAO`
- `FORNECEDORES e PRODUTOS - INFLACAO`
- `FORNECEDORES TOTAL`
- `FORNECEDORES por CAT`
- `FORNECEDORES por CAT 2`
- `FORNECEDORES por UF e CAT`
- `FORNECEDORES TOTAL - POR ANO`
- `FORNECEDORES_25_26`
- `PMP_FORN`
- `CP_STATUS`

Criar subtabs:

- Total
- Impacto Cotacao
- Inflacao
- Categorias
- UF/CAT
- Ano
- CP
- Fiscal

## Produtos e Precos v3

Representar estas views Zoho:

- `PRODUTOS por CAT`
- `PRODUTOS por ID`
- `PRODUTOS por ID - MIN COT`
- `PRODUTOS por ID e FORN`
- `PRODUTOS por PROD`
- `PRODUTOS por UF`
- `PADRONIZACAO PRODUTOS`
- `PMP_PROD_ABC`
- `PMP_PROD_ID`
- `PMP_PROD_INF_12_x`
- `PMP_ID_INF_12_x`
- `PMP_UF`
- `TOTAL por PROD`
- `PMP por PROD`
- `PMP por UF`

Obrigatorio mostrar:

- produto original;
- produto oficial;
- fornecedor original;
- fornecedor oficial;
- codigo original;
- codigo oficial;
- aliases/duplicidades;
- curva produto;
- curva ID;
- PMP atual;
- PMP 12 meses;
- menor cotacao;
- fornecedor menor preco;
- fornecedor comprado;
- impacto R$;
- UFs/filiais.

## Cotacoes v3

Representar estas views Zoho:

- `CONTAGEM de COTACOES`
- `CONTAGEM de COTACOES por ABC`
- `CONTAGEM DE COTACOES por CAT`
- `CONTAGEM de COTACOES por UF`
- `COTACOES DE PRECOS - TODOS`
- `COTACOES por PRODUTO`
- `RELATORIO DE COTACOES`
- `MIN COTACAO por FORN`
- `MIN COTACAO por FORN - COTACOES <= 3`
- `NUMERO de COTACOES por PRODUTO`
- `IMPACTO de COTACAO NACIONAL`
- `IMPACTO de COTACAO por UF`

Obrigatorio:

- distribuicao 0, 1, 2, 3, 4+ cotacoes;
- cotacoes por ABC;
- cotacoes por categoria;
- cotacoes por UF;
- produtos com cotacoes <= 3;
- fornecedor menor preco;
- comparativo compra real x menor cotacao;
- impacto nacional;
- impacto por UF.

## Inflacao e Impacto v3

Representar estas views Zoho:

- `INFLACAO por MES por CAT - %`
- `INFLACAO por MES por CAT - R$`
- `TOP INFLACAO`
- `TOP DEFLACAO`
- `INFLACAO por PRODUTO e CAT`
- `INFLACAO NACIONAL`
- `INFLACAO NACIONAL por CATEGORIA`
- `INFLACAO por UF`
- `INFLACAO por UF e por CAT`
- `INFLACAO por RESUMO de UF`
- `INFLACAO total`
- `INF_ID`
- `INF_ID_PMP`
- `INF_PROD_PMP`

Separar:

- variacao percentual;
- impacto em reais;
- nacional;
- UF;
- categoria;
- produto;
- ID.

## Fiscal 2027 v3

Essa aba nao existe no Zoho como painel proprio, mas e diferencial do nosso BI.

Manter e melhorar:

- cruzamento fornecedor x valor comprado;
- regime fiscal;
- credito 2027;
- evidencia;
- fila fiscal;
- impacto potencial por categoria/filial.

Regras:

- Lucro Real -> credito alto.
- Lucro Presumido -> credito alto.
- Simples -> condicionado.
- MEI -> baixo.
- Indeterminado -> pendente/indeterminado.

## Financeiro / CP v3

Representar:

- `CP_STATUS`
- `CP_STATUS-TOTAL`
- `CP_SALDO_26`
- `CP_SALDO_DIVIDA_2026`
- `CP_SEMANA`

Mostrar:

- CP aberto;
- CP vencido;
- CP a vencer;
- status;
- faixa de dias;
- fornecedor;
- filial;
- categoria;
- curva fornecedor;
- relacao com compras recentes.

## Adiantamentos v3

Representar:

- `Adiantamento %`
- `Adiantamento por Mes`
- `Adiantamento por UF`
- `AD por UF`
- `AD por CAT`
- `AD por PRODUTO %`
- `AD por PRODUTO e UF`
- `AD por FORNECEDOR`
- `AD por FORNECEDOR e UF`
- `AD por MES e CAT`
- `CONCILIACAO_ AD`
- `CONCILIACAO_UF`
- `ADIANTAMENTO_CONC`

Mostrar:

- funil de conciliacao;
- AD por mes;
- AD por UF;
- AD por categoria;
- AD por produto;
- AD por fornecedor;
- AD por fornecedor e UF;
- nota x AD;
- status conciliacao.

## Servicos v3

Representar:

- `DESPESAS por UF`
- `DESPESAS por UF e CAT`
- `SERVICOS`
- `SERVICOS por MES`
- `DESPESAS`
- `DESPESAS FIN`
- `Despesas_2v2v2`

Servicos deve conversar com categoria `D - DESPESAS`.

Mostrar:

- total servicos;
- servicos por UF;
- servicos por UF e categoria;
- servicos por mes;
- fornecedores de servicos;
- CP em aberto de servicos;
- detalhamento por CAT5.

## Qualidade dos Dados v3

Adicionar:

- cobertura de fontes Zoho;
- origem das views;
- objetos exportados x nao exportados;
- padronizacao produto/fornecedor;
- categorias sem mapeamento;
- fornecedores sem CNPJ oficial;
- produtos sem codigo oficial;
- cotacoes incompletas;
- estoque fora do workspace SUPRIMENTOS.

## Nota final na interface

No rodape ou modal de metodologia, incluir uma nota curta:

`Estoque vem do workspace APURACAO DE RESULTADOS; compras, cotacoes, fornecedor, inflacao, CP e AD vem do workspace SUPRIMENTOS.`

## Estilo

Manter estilo v2:

- operacional;
- compacto;
- denso;
- sem hero;
- sem landing page;
- sem gradientes decorativos;
- tabelas no centro;
- graficos compactos;
- cards pequenos;
- filtros fortes.

## Resumo final esperado

Ao final da resposta, explique brevemente:

- o que mudou da v2 para v3;
- quais paineis do Zoho foram incorporados;
- como a gestao por filial foi incluida;
- como estoque por filial foi incluido;
- como a categoria em cascata foi corrigida.

