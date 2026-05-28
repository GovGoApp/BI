# Prompt inicial para Claude Design

Voce e um designer de produto senior. Quero que voce crie o primeiro mock visual do `BI de Suprimentos`, uma aplicacao interna para analise de compras, fornecedores, produtos, cotacoes, inflacao, impacto financeiro, fiscal 2027, contas a pagar e adiantamentos.

Use como base os documentos anexados, principalmente:

- `01_BRIEFING_MOCKUP_BI_SUPRIMENTOS.md`
- `02_REFERENCIA_VISUAL_FORNECEDORES.md`
- `04_MAPA_PAGINAS_E_COMPONENTES.md`
- `05_DADOS_E_DOMINIOS_SUPRIMENTOS.md`
- `06_CRITERIOS_ACEITACAO_DESIGN.md`

Use a linguagem visual do painel atual de fornecedores como referencia principal: fundo cinza claro, cards brancos, bordas discretas, filtros compactos, KPIs no topo, tabelas fortes, linhas expansivas, chips de status e visual operacional.

Crie um mock navegavel em HTML/CSS/JS, preferencialmente em arquivo unico, sem backend e sem conexao real com dados. Use dados ficticios realistas, baseados nos termos e exemplos dos documentos.

A primeira tela deve abrir diretamente no `Resumo Executivo`. Nao crie landing page, hero, tela comercial ou apresentacao institucional. O resultado deve parecer uma ferramenta de trabalho para diretoria, compras, suprimentos, fiscal, financeiro e BI.

O BI deve conter estas paginas/abas:

- Resumo Executivo
- Fornecedor 360
- Oportunidades
- Produtos e Precos
- Cotacoes
- Inflacao e Impacto
- Fiscal 2027
- Financeiro Operacional
- Adiantamentos
- Qualidade dos Dados

A casca global deve ter:

- titulo `BI de Suprimentos`;
- busca global;
- botoes de metodologia e exportacao;
- data de atualizacao;
- filtros globais;
- navegacao por abas;
- conteudo denso e escaneavel.

Filtros globais esperados:

- Empresa;
- Negocio;
- UF;
- Filial;
- Periodo;
- Categoria;
- Curva;
- Regime fiscal;
- Tipo de alerta.

Termos de dominio que devem aparecer na interface:

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

O mock precisa priorizar decisao e acao. Ele deve mostrar onde esta o dinheiro, onde esta o risco, onde ha oportunidade de economia e qual fila de acao o time deve atacar primeiro.

Evite:

- visual de landing page;
- hero;
- gradientes decorativos;
- cards gigantes sem funcao;
- textos explicativos longos dentro da interface;
- graficos que ocupam espaco demais e escondem a tabela;
- paleta dominada por uma unica cor.

Entregue:

- mock de alta fidelidade;
- HTML/CSS/JS navegavel;
- dados ficticios realistas;
- abas funcionando;
- linhas ou paineis de detalhe;
- breve explicacao de como aplicou a referencia visual do painel de fornecedores.

