# Prompt completo para Claude Design

Voce e um designer de produto senior. Crie o primeiro mock de alta fidelidade do `BI de Suprimentos`, uma aplicacao interna para analise de compras, fornecedores, produtos, cotacoes, inflacao, impacto financeiro, fiscal 2027, contas a pagar e adiantamentos.

## Objetivo

Quero um mock visual navegavel, preferencialmente em HTML/CSS/JS em arquivo unico, sem backend e sem conexao real com dados. Use dados ficticios, mas realistas.

A primeira tela deve ser a aplicacao em uso, aberta no `Resumo Executivo`. Nao crie landing page, hero, tela comercial ou apresentacao institucional.

## Referencias visuais

Referencia principal: painel atual de fornecedores.

Caracteristicas que devem ser preservadas:

- ferramenta operacional compacta;
- fundo cinza claro;
- cards brancos;
- bordas discretas;
- Segoe UI/Arial;
- busca global no topo;
- filtros em grade;
- KPI cards compactos;
- tabela forte como elemento central;
- linhas expansivas;
- chips/pills de status;
- badges de empresa;
- modal de metodologia;
- visual sobrio e profissional.

Tokens sugeridos:

```css
:root {
  --bg: #f3f6fa;
  --ink: #0f172a;
  --muted: #64748b;
  --line: #d8e0ea;
  --card: #ffffff;
  --blue: #2563eb;
  --green: #16a34a;
  --yellow: #a16207;
  --red: #b91c1c;
  --gray: #475569;
}
```

## Produto

O `BI de Suprimentos` precisa responder:

- onde esta concentrado o dinheiro comprado;
- quais fornecedores e produtos sao mais relevantes;
- onde compramos acima da menor cotacao;
- quais produtos tem baixa concorrencia;
- quais itens sofreram inflacao ou impacto;
- quais fornecedores misturam alto valor com risco fiscal;
- onde ha contas a pagar ou adiantamentos pendentes;
- quais dados precisam ser saneados.

## Usuarios

Usuarios:

- diretoria;
- compras;
- suprimentos;
- fiscal;
- financeiro;
- analistas de BI.

A tela deve ajudar essas pessoas a decidir o que fazer primeiro.

## Estrutura global

Crie uma casca comum para todas as paginas:

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

Valores exemplo:

- Empresas: RC, ME, SU.
- Negocios: CD, COZINHA, ESCOLA, HOSPITAL, MERENDA, PRESIDIO, MATRIZ.
- UFs: DF, ES, MA, PA, PB, PE, PI, RJ, RN, SE, SP.
- Curvas: AAA, AA, A, B, BB, C, CC, CCC.

## Paginas obrigatorias

### 1. Resumo Executivo

Mostrar:

- KPIs: Total comprado, Fornecedores, Produtos/IDs, Impacto R$, Oportunidade R$, Compras com cotacao, Risco fiscal, CP em aberto.
- tendencia mensal de compras;
- compras por negocio;
- top categorias;
- top fornecedores;
- alertas executivos.

### 2. Fornecedor 360

Criar tabela de fornecedores com linha expandida.

Colunas:

- Fornecedor;
- CNPJ;
- Empresas;
- Curva;
- Valor;
- Regime;
- Credito 2027;
- Alertas.

Detalhe expandido:

- identidade;
- compras;
- fiscal 2027;
- financeiro;
- produtos comprados;
- cotacoes relacionadas;
- adiantamentos.

### 3. Oportunidades

Criar fila de acao.

Tipos:

- compra acima da menor cotacao;
- item curva A com inflacao;
- produto com apenas uma cotacao;
- fornecedor atual nao e menor preco;
- item com alto impacto em reais;
- fornecedor alto valor com regime fiscal pendente.

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

### 4. Produtos e Precos

Criar busca por produto/ID e tabela.

Colunas:

- Produto;
- ID;
- Categoria;
- Curva ID;
- Curva Produto;
- PMP atual;
- Variacao 12m;
- Impacto R$.

Linha expandida:

- serie PMP 0 a 12;
- cotacoes min/media/max;
- fornecedores;
- compras por UF/filial.

### 5. Cotacoes

Mostrar disciplina de cotacao.

Componentes:

- KPIs: produtos cotados, media cotacoes/produto, itens com 1 cotacao, itens sem cotacao, potencial por menor preco.
- distribuicao de QTD_COT;
- tabela de cotacoes;
- detalhe com fornecedores cotados.

### 6. Inflacao e Impacto

Mostrar:

- impacto total;
- inflacao media;
- top inflacao;
- top deflacao;
- itens afetados;
- ranking por impacto em reais;
- ranking por variacao percentual;
- tabela com ID, produto, PMP_0, PMP_1, PMP_12, INF_ID, IMP_ID, curva.

### 7. Fiscal 2027

Unir compras com regime fiscal.

Mostrar:

- compra com credito alto;
- compra condicionada;
- compra pendente;
- fornecedores indeterminados;
- valor em risco;
- matriz valor comprado x regime fiscal;
- fila fiscal priorizada.

### 8. Financeiro Operacional

Unir compras com contas a pagar.

Mostrar:

- CP aberto;
- CP vencido;
- vencimento 7 dias;
- fornecedores com pressao de caixa;
- timeline semanal;
- tabela por fornecedor.

### 9. Adiantamentos

Controlar AD.

Mostrar:

- AD total;
- AD conciliado;
- AD pendente;
- fornecedores com AD;
- notas vinculadas;
- funil de conciliacao;
- tabela nota x AD.

### 10. Qualidade dos Dados

Mostrar:

- linhas analisadas;
- fontes OK;
- fornecedores sem CNPJ;
- itens sem ID;
- cotacoes incompletas;
- fiscal pendente;
- tabela por fonte;
- fila de saneamento.

## Termos de dominio

Use estes termos na interface:

- Curva;
- ID;
- PMP;
- PMP 12m;
- QTD_COT;
- Menor cotacao;
- Impacto;
- Regime fiscal;
- Credito 2027;
- CP;
- AD;
- Conciliacao;
- Fiscal pendente;
- Oportunidade R$.

Definicoes resumidas:

- `ID`: chave analitica de produto/contexto, mais especifica que produto generico.
- `Curva ABC`: classificacao de relevancia economica por valor acumulado.
- `PMP`: preco medio ponderado.
- `QTD_COT`: numero de cotacoes por produto/ID.
- `Impacto`: diferenca economica convertida em reais.
- `AD`: adiantamento.
- `CP`: contas a pagar.

## Dados ficticios sugeridos

Fornecedores:

- FONTE VIVA ALIMENTOS LTDA
- SELECT NUTRI ALIMENTOS E LOGISTICA LTDA
- J. J. FOODS LTDA
- ALIBER FOODS LTDA
- FF INDUSTRIA E COMERCIO DE POLPAS LTDA

Produtos:

- Arroz tipo 1
- Feijao carioca
- Leite UHT
- Carne bovina
- Frango congelado
- Polpa de fruta
- Oleo de soja

Status:

- Comprado acima da menor cotacao
- Baixa concorrencia
- Inflacao alta
- Fiscal pendente
- CP vencido
- AD pendente
- Conciliado

## Regras de design

Fazer:

- layout operacional;
- informacao densa e escaneavel;
- KPIs compactos;
- tabelas fortes;
- filtros claros;
- chips de status;
- grafico compacto;
- detalhe expandido;
- contraste adequado;
- labels em portugues.

Evitar:

- hero;
- landing page;
- gradientes decorativos;
- elementos sem funcao;
- cards gigantes;
- excesso de texto explicativo dentro da UI;
- paleta dominada por uma unica cor;
- graficos enormes que escondem a tabela;
- layout que pareca comercial em vez de ferramenta.

## Responsividade

Prioridade:

- desktop 1366x768;
- desktop 1440x900.

Tambem deve funcionar razoavelmente em telas menores, com filtros quebrando linha e tabelas podendo ter scroll horizontal.

## Entrega

Entregue:

- mock de alta fidelidade;
- preferencialmente HTML/CSS/JS em arquivo unico;
- abas navegaveis;
- dados ficticios realistas;
- descricao curta dos componentes;
- nota dizendo como aplicou a referencia do painel de fornecedores.
