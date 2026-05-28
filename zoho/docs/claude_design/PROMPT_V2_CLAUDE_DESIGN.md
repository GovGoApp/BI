# Prompt v2 para Claude Design - BI de Suprimentos

Voce vai criar uma segunda versao do mock `BI de Suprimentos`.

Importante: nao sobrescreva a versao atual. Gere um novo arquivo chamado:

`BI Suprimentos v2.html`

Use como ponto de partida o arquivo atual:

`BI Suprimentos.html`

## O que deve ser preservado

A primeira versao acertou bem a direcao visual. Preserve:

- visual operacional e compacto;
- fundo cinza claro;
- cards brancos;
- bordas discretas;
- filtros no topo;
- KPIs compactos;
- abas de navegacao;
- tabelas fortes;
- linhas expansivas;
- chips/pills de status;
- badges de empresa;
- modal de metodologia;
- pagina `Oportunidades` como fila de acao;
- linguagem visual proxima ao painel de fornecedores.

Nao transforme isso em landing page. A tela deve continuar parecendo uma ferramenta interna de trabalho.

## Problemas da v1 que precisam ser corrigidos

1. Faltou analise por categoria.
2. Faltou uma visao de `Servicos/Despesas`, que existe no Zoho.
3. A geografia ficou fraca; o Zoho usa bastante UF, regiao, filial e negocio.
4. Os filtros ainda parecem apenas visuais; na v2, simule filtros funcionais com dados ficticios.
5. Faltam filtros por nivel de categoria: `CAT1`, `CAT2`, `CAT3`, `CAT4`, `CAT5`.
6. A responsividade esta limitada por `viewport width=1366`; corrija para `width=device-width`.
7. Algumas regras fiscais ficticias ficaram inconsistentes.
8. Faltou diferenciar melhor:
   - oportunidade economica;
   - risco fiscal;
   - risco financeiro;
   - saneamento de dados.

## Nova estrutura de abas

Crie a v2 com estas abas:

- Resumo Executivo
- Oportunidades
- Categorias
- Fornecedor 360
- Produtos e Precos
- Cotacoes
- Inflacao e Impacto
- Fiscal 2027
- Financeiro / CP
- Adiantamentos
- Servicos
- Qualidade dos Dados

Se ficar apertado, use scroll horizontal nas abas, mas mantenha todas acessiveis.

## Nova aba obrigatoria: Categorias

Crie uma pagina `Categorias` forte, porque categoria e uma dimensao central do BI.

Ela deve mostrar:

- KPIs:
  - Total comprado na categoria filtrada;
  - Categorias ativas;
  - Produtos/IDs;
  - Fornecedores;
  - Impacto R$;
  - Oportunidade R$.
- arvore/drilldown de categorias:
  - `CAT1 > CAT2 > CAT3 > CAT4 > CAT5`;
- ranking por valor em cada nivel;
- `Categoria x UF`;
- `Categoria x Mes`;
- `Categoria x Fornecedor`;
- `Categoria x Produto`;
- alertas da categoria:
  - inflacao;
  - baixa cotacao;
  - compra acima da menor cotacao;
  - risco fiscal;
  - CP/AD pendente.

Use a hierarquia completa de categorias do arquivo:

`CATEGORIAS_I_D_A_ORDENADAS.md`

Regra obrigatoria de ordenacao:

1. Primeiro `I - INSUMOS`.
2. Depois `D - DESPESAS`.
3. Depois `A - ATIVOS`.
4. Dentro de cada grupo, ordenar por codigo, nao por valor comprado.

Exemplos de ordem correta:

- `I0`, `I1`, `I2`, `I3`, `I4`, `I5`, `I6`;
- `D1`, `D2`, `D3`, `D4`, `D5`, `D6`, `D7`, `D8`;
- `A1`, `A2`.

Nao usar `F - FATURAMENTO` nem `V - VENDA BALCAO` nos filtros principais da v2.

Os filtros devem ser em cascata:

- selecionar `CAT1` limita os valores de `CAT2`;
- selecionar `CAT2` limita os valores de `CAT3`;
- selecionar `CAT3` limita os valores de `CAT4`;
- selecionar `CAT4` limita os valores de `CAT5`.

## Nova aba obrigatoria: Servicos

O Zoho tem um `PAINEL SERVICOS` com:

- `DESPESAS por UF`;
- `DESPESAS por UF e CAT`;
- `SERVICOS`;
- `SERVICOS por MES`.

Crie uma aba `Servicos` com:

- KPIs:
  - Total em servicos;
  - Fornecedores de servicos;
  - UFs atendidas;
  - Variacao mensal;
  - maior categoria de servico;
  - CP em aberto relacionado.
- graficos/tabelas:
  - servicos por UF;
  - servicos por categoria;
  - servicos por mes;
  - fornecedores de servicos;
  - tabela detalhada por `CAT5`, valor, %, variacao e fornecedor principal.

## Resumo Executivo v2

Reforce o resumo com blocos que o Zoho realmente tem:

- `SUP por GEO - N e NE`;
- `SUP por GEO - S e SE`;
- `CAT por MES`;
- `CAT por UF`;
- `RESUMO NEGOCIOS`;
- `RESUMO_FILIAL`;
- `RESUMO - FORN`.

Nao precisa usar exatamente esses nomes na UI, mas a tela deve refletir essas analises.

Adicionar no resumo:

- mapa/grade por regiao ou UF;
- ranking `Categoria x UF`;
- ranking por negocio;
- ranking por filial;
- fila curta de alertas.

## Fornecedor 360 v2

O Zoho tem visoes fortes de:

- `FORNECEDORES IMPACTO sobre COTACAO`;
- `FORNECEDORES e PRODUTOS - IMPACTO`;
- `FORNECEDORES INFLACAO`;
- `FORNECEDORES e PRODUTOS - INFLACAO`;
- `FORNECEDORES TOTAL`;
- `FORNECEDORES por CAT`;
- `CP_STATUS`.

Na v2, o detalhe expandido do fornecedor deve mostrar:

- total comprado;
- curva fornecedor;
- categorias compradas;
- produtos principais;
- impacto por cotacao;
- impacto por inflacao;
- CP status;
- AD status;
- regime fiscal;
- credito 2027;
- alertas e acao sugerida.

## Produtos e Precos v2

Melhore a visao de produtos usando:

- `PRODUTOS por ID`;
- `PRODUTOS por PROD`;
- `PRODUTOS por UF`;
- `PRODUTOS por ID e FORN`;
- `PRODUTOS por ID - MIN COT`;
- `PMP_ID_INF_12`;
- `PMP_PROD_INF_12`.

Cada linha de produto deve permitir ver:

- `ID`;
- `Produto oficial`;
- `Produto original`;
- `CAT1` a `CAT5`;
- curva produto;
- curva ID;
- PMP atual;
- PMP 12 meses;
- menor cotacao;
- fornecedor menor preco;
- fornecedor comprado;
- impacto R$;
- UFs/filiais onde aparece.

## Cotacoes v2

Melhore com:

- `QTD_COT`;
- `MIN_COT`;
- `MED_COT`;
- `MAX_COT`;
- `FORN_MENOR_PRECO`;
- `CNPJ_MENOR_PRECO`;
- comparativo com compra real;
- filtro `0 cotacao`, `1 cotacao`, `2 cotacoes`, `3+ cotacoes`;
- destaque para itens curva A com baixa concorrencia.

## Inflacao e Impacto v2

Basear nos paineis:

- `INFLACAO por MES por CAT - %`;
- `INFLACAO por MES por CAT - R$`;
- `TOP INFLACAO`;
- `TOP DEFLACAO`;
- `INFLACAO por PRODUTO e CAT`;
- `INFLACAO NACIONAL`;
- `INFLACAO por UF`.

Adicionar:

- ranking por categoria;
- ranking por UF;
- ranking por produto;
- separacao clara entre variacao percentual e impacto em reais.

## Financeiro / CP v2

O Zoho tem `PAINEL CP` com `CP_STATUS`.

Melhore a aba para mostrar:

- CP aberto;
- CP vencido;
- CP a vencer;
- status;
- faixa de dias;
- fornecedor;
- curva fornecedor;
- categoria comprada;
- relacao com compras recentes.

## Adiantamentos v2

Basear no Zoho:

- `Adiantamento %`;
- `Adiantamento por Mes`;
- `Adiantamento por UF`;
- `AD por UF`;
- `AD por CAT`;
- `AD por PRODUTO %`;
- `AD por PRODUTO e UF`;
- `AD por FORNECEDOR`;
- `AD por FORNECEDOR e UF`.

Adicionar:

- funil/visao de conciliacao;
- tabela nota x AD;
- status conciliacao;
- AD por categoria;
- AD por produto;
- AD por fornecedor.

## Filtros globais v2

Substitua os filtros atuais por filtros mais completos.

Filtros globais:

- Empresa: RC, ME, SU;
- Negocio;
- Regiao;
- UF;
- Filial;
- Periodo;
- CAT1;
- CAT2;
- CAT3;
- CAT4;
- CAT5;
- Curva fornecedor;
- Curva produto;
- Curva ID;
- Fornecedor;
- Produto/ID;
- Regime fiscal;
- Credito 2027;
- Status cotacao;
- Status CP;
- Status AD;
- Tipo de alerta.

Os filtros `CAT1` a `CAT5` devem parecer encadeados/cascata.

Na v2, os filtros devem simular funcionamento real:

- clicar em um filtro deve alterar estado visual;
- busca deve filtrar tabelas visiveis;
- tags devem filtrar a lista da pagina;
- KPIs podem atualizar de forma simples ou mostrar estado filtrado;
- nao precisa ser perfeito, mas nao deve ser apenas decorativo.

## Regras de padronizacao oficial

Explique visualmente, sem texto longo, a diferenca entre dado original e oficial.

Use nos detalhes:

- `Produto original`;
- `Produto oficial`;
- `Fornecedor original`;
- `Fornecedor oficial`.

Motivo:

- o dado original preserva como veio da operacao;
- o dado oficial e a versao padronizada para analise;
- isso evita duplicidade e melhora curva ABC, PMP, cotacao e fiscal.

## Regras fiscais ficticias

Corrija a consistencia dos exemplos:

- `Lucro Real`: credito 2027 tende a `Alto`;
- `Lucro Presumido`: credito 2027 tende a `Alto`;
- `Simples`: credito 2027 tende a `Condicionado`;
- `MEI`: credito 2027 tende a `Baixo`;
- `Indeterminado`: credito 2027 `Pendente` ou `Indeterminado`.

## Regras de design

Manter:

- UI operacional;
- conteudo denso;
- fontes compactas;
- cards com raio pequeno;
- tabelas como centro da experiencia;
- graficos compactos;
- cores de status consistentes.

Evitar:

- hero;
- landing page;
- textos explicativos longos dentro da UI;
- graficos gigantes;
- gradientes decorativos;
- paleta dominada por uma unica cor;
- cards aninhados em excesso.

## Responsividade

Corrija:

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Garanta:

- boa leitura em 1366x768;
- boa leitura em 1440x900;
- tabs com scroll horizontal se necessario;
- tabelas com scroll horizontal quando ficarem largas;
- filtros quebrando para 5, 4, 3 ou 2 colunas conforme largura.

## Entrega

Entregue um novo arquivo:

`BI Suprimentos v2.html`

Nao sobrescreva:

`BI Suprimentos.html`

Inclua no final uma nota curta explicando:

- principais mudancas da v2;
- quais abas novas foram adicionadas;
- como a analise por categoria foi incorporada;
- como a v2 ficou mais proxima dos paineis do Zoho.
