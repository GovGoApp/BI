# Briefing - Mockup do BI de Suprimentos

## Produto

Criar o primeiro mock visual do `BI de Suprimentos`, uma aplicacao interna para acompanhar compras, fornecedores, produtos, cotacoes, inflacao, impacto financeiro, contas a pagar, adiantamentos e riscos fiscais.

O BI deve aproveitar a mesma linguagem visual do painel de fornecedores ja criado no projeto.

## Publico

Usuarios principais:

- diretoria;
- compras;
- suprimentos;
- fiscal;
- financeiro;
- analistas de BI.

Essas pessoas precisam tomar decisoes rapidas. A tela deve ser densa, clara e orientada a acao.

## Problemas que o BI precisa responder

- Onde esta concentrado o dinheiro comprado?
- Quais fornecedores e produtos estao na curva ABC mais relevante?
- Onde compramos acima da menor cotacao?
- Quais produtos tem pouca concorrencia de cotacao?
- Quais itens tiveram inflacao ou impacto relevante?
- Quais fornecedores misturam alto volume de compra com risco fiscal?
- Onde ha contas a pagar, vencimentos e adiantamentos pendentes?
- Quais dados precisam ser saneados antes de uma decisao?

## Direcao de produto

Este BI nao deve parecer uma landing page. Ele deve parecer uma ferramenta de trabalho.

Use uma interface:

- compacta;
- confiavel;
- densa sem ficar confusa;
- com filtros sempre visiveis;
- com KPIs no topo;
- com tabelas fortes;
- com paineis de detalhe expandido;
- com chips de status;
- com hierarquia visual clara;
- com pouco texto explicativo dentro da interface.

## Base visual

Base principal:

- painel de fornecedores `08b`;
- fundo cinza claro;
- cards brancos;
- bordas discretas;
- Segoe UI/Arial;
- azul como cor de acao;
- verde/amarelo/vermelho para status;
- tabelas compactas com linhas expansivas.

## Tipo de mock desejado

Preferencia:

- mock navegavel em HTML/CSS/JS, arquivo unico;
- navegacao por abas/paginas;
- dados ficticios realistas;
- sem backend;
- sem conexao real ao Zoho;
- layout desktop-first com adaptacao razoavel para notebook.

Tamanho alvo:

- 1366x768;
- 1440x900;
- deve continuar utilizavel em telas largas.

## Primeira tela

A primeira tela deve abrir no `Resumo Executivo`.

Ela deve mostrar imediatamente:

- titulo `BI de Suprimentos`;
- busca global;
- filtros;
- abas de navegacao;
- KPIs principais;
- graficos/tabelas de sintese;
- alertas executivos.

Nao criar capa, hero, texto institucional ou introducao.

## Linguagem da interface

Usar portugues do Brasil.

Exemplos de labels:

- Total comprado
- Impacto R$
- Oportunidade R$
- Fornecedores
- Produtos/IDs
- Compras com cotacao
- Risco fiscal
- CP em aberto
- AD pendente
- Curva
- Menor cotacao
- PMP 12m
- Prioridade
