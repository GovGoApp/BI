# Mapa de paginas e componentes - BI de Suprimentos

## Casca global

Todas as paginas compartilham a mesma casca:

```text
+--------------------------------------------------------------------------------------+
| BI de Suprimentos                           [Busca global.........................]  |
| [Metodologia] [Exportar CSV] [Atualizado em: yyyy-mm-dd hh:mm]                       |
+--------------------------------------------------------------------------------------+
| Empresa | Negocio | UF | Filial | Periodo | Categoria | Curva | Regime | Alerta     |
+--------------------------------------------------------------------------------------+
| Resumo | Fornecedores | Oportunidades | Produtos | Cotacoes | Inflacao | Fiscal | ...|
+--------------------------------------------------------------------------------------+
| Conteudo da pagina selecionada                                                       |
+--------------------------------------------------------------------------------------+
```

Filtros globais:

- Empresa;
- Negocio;
- UF;
- Filial;
- Periodo;
- Categoria;
- Curva;
- Regime fiscal;
- Tipo de alerta.

## Pagina 1 - Resumo Executivo

Objetivo:

Mostrar rapidamente onde esta o dinheiro, o risco e a oportunidade.

Componentes:

- KPIs de topo:
  - Total comprado;
  - Fornecedores;
  - Produtos/IDs;
  - Impacto R$;
  - Oportunidade R$;
  - Compras com cotacao;
  - Fornecedores com risco fiscal;
  - CP em aberto.
- grafico compacto de tendencia mensal;
- barras por negocio;
- tabela de top categorias;
- tabela de top fornecedores;
- lista de alertas executivos.

Layout sugerido:

```text
+--------------------------------------------------------------------------------------+
| KPIs compactos                                                                        |
+--------------------------------------------------------------------------------------+
| Tendencia mensal de compras                  | Compras por negocio                    |
+--------------------------------------------------------------------------------------+
| Top categorias                               | Top fornecedores                       |
+--------------------------------------------------------------------------------------+
| Alertas executivos / fila curta de prioridades                                        |
+--------------------------------------------------------------------------------------+
```

## Pagina 2 - Fornecedor 360

Objetivo:

Transformar a pagina atual de fornecedores em uma visao economica, operacional e fiscal.

Componentes:

- tabela principal de fornecedores;
- linha expandida com:
  - identidade e cadastro;
  - compras;
  - fiscal 2027;
  - financeiro;
  - produtos comprados;
  - cotacoes relacionadas;
  - adiantamentos.

Colunas da tabela:

- Fornecedor;
- CNPJ;
- Empresas;
- Curva;
- Valor;
- Regime;
- Credito 2027;
- Alertas.

Detalhe expandido:

```text
+----------------------------------------------------------------------------------+
| Identidade       | Compras          | Fiscal 2027       | Financeiro              |
+----------------------------------------------------------------------------------+
| Produtos comprados: ID, produto, categoria, valor, PMP, menor cotacao, impacto    |
+----------------------------------------------------------------------------------+
| Cotacoes e fornecedores alternativos                                              |
+----------------------------------------------------------------------------------+
```

## Pagina 3 - Oportunidades

Objetivo:

Ser a fila de acao do time de suprimentos.

Tipos de oportunidade:

- compra acima da menor cotacao;
- item curva A com inflacao;
- produto com apenas uma cotacao;
- fornecedor atual nao e menor preco;
- item com alto impacto em reais;
- fornecedor alto valor com regime fiscal pendente.

Componentes:

- KPIs de oportunidade;
- matriz de prioridade;
- fila de oportunidades;
- detalhe da oportunidade.

Tabela:

- Tipo;
- Prioridade;
- ID;
- Produto;
- Fornecedor atual;
- Menor cotacao;
- Impacto R$;
- Evidencia;
- Acao sugerida;
- Status.

## Pagina 4 - Produtos e Precos

Objetivo:

Investigar preco por produto e por ID.

Componentes:

- busca por produto/ID;
- tabela de produtos;
- linha expandida com:
  - serie PMP 0 a 12;
  - cotacoes min/media/max;
  - fornecedores;
  - compras por UF/filial.

Colunas:

- Produto;
- ID;
- Categoria;
- Curva ID;
- Curva Produto;
- PMP atual;
- Variacao 12m;
- Impacto R$.

## Pagina 5 - Cotacoes

Objetivo:

Medir disciplina de cotacao e competitividade.

Componentes:

- KPIs:
  - produtos cotados;
  - media cotacoes/produto;
  - itens com 1 cotacao;
  - itens sem cotacao;
  - potencial por menor preco.
- distribuicao de quantidade de cotacoes;
- tabela de cotacoes;
- detalhe com lista de fornecedores cotados.

Colunas:

- ID;
- Produto;
- Mes;
- UF;
- Empresa;
- QTD_COT;
- MIN;
- MED;
- MAX;
- Fornecedor menor preco;
- Compra realizada.

## Pagina 6 - Inflacao e Impacto

Objetivo:

Explicar aumentos de preco e perdas em reais.

Componentes:

- KPIs:
  - impacto total;
  - inflacao media;
  - top inflacao;
  - top deflacao;
  - itens afetados.
- ranking de impacto em R$;
- ranking de variacao percentual;
- tabela detalhada;
- detalhe com serie PMP 12 meses.

Colunas:

- ID;
- Produto;
- Categoria;
- Mes;
- PMP_0;
- PMP_1;
- PMP_12;
- INF_ID;
- IMP_ID;
- Curva.

## Pagina 7 - Fiscal 2027

Objetivo:

Unir suprimentos com regime fiscal e credito 2027.

Componentes:

- KPIs:
  - compra com credito alto;
  - compra condicionada;
  - compra pendente;
  - fornecedores indeterminados;
  - valor em risco.
- matriz valor comprado x regime fiscal;
- fila fiscal priorizada;
- detalhe do fornecedor.

Colunas:

- Fornecedor;
- CNPJ;
- Valor comprado;
- Curva;
- Regime fiscal;
- Credito 2027;
- Evidencia;
- Acao fiscal.

## Pagina 8 - Financeiro Operacional

Objetivo:

Unir compras com contas a pagar.

Componentes:

- KPIs:
  - CP aberto;
  - CP vencido;
  - vencimento 7 dias;
  - fornecedores com pressao de caixa;
  - valor em negociacao.
- timeline semanal;
- tabela por fornecedor;
- detalhe com titulos.

Colunas:

- Fornecedor;
- CP aberto;
- Vencido;
- A vencer;
- Faixa de dias;
- Ultima compra;
- Curva;
- Acao.

## Pagina 9 - Adiantamentos

Objetivo:

Controlar adiantamentos, conciliacao e pendencias.

Componentes:

- KPIs:
  - AD total;
  - AD conciliado;
  - AD pendente;
  - fornecedores com AD;
  - notas vinculadas.
- funil de conciliacao;
- tabela de adiantamentos;
- detalhe nota x AD.

Colunas:

- Fornecedor;
- Nota fiscal;
- AD;
- Valor AD;
- Valor conciliado;
- Status conciliacao;
- Mes entrada;
- Mes pagamento.

## Pagina 10 - Qualidade dos Dados

Objetivo:

Mostrar confianca, lacunas e saneamento necessario.

Componentes:

- KPIs:
  - linhas analisadas;
  - fontes OK;
  - fornecedores sem CNPJ;
  - itens sem ID;
  - cotacoes incompletas;
  - fiscal pendente.
- tabela por fonte;
- fila de saneamento.

Colunas:

- Fonte;
- Linhas;
- Cobertura;
- Campo critico;
- Problema;
- Impacto;
- Acao.

