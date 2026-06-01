# Briefing — BI de Suprimentos

## Produto

Sistema de BI interno para acompanhar compras, fornecedores, produtos, cotações, inflação, impacto financeiro, contas a pagar, adiantamentos e riscos fiscais.

Os dados vêm do Zoho Analytics (workspace `SUPRIMENTOS`), cruzados com a base de fornecedores e regime fiscal do projeto principal.

## Público

| Perfil | O que precisa ver |
|---|---|
| Diretoria | Resumo executivo, alertas, concentração de gastos |
| Compras/Suprimentos | Cotações, impacto, oportunidades de negociação |
| Fiscal | Regime tributário, risco CBS/IBS 2027 |
| Financeiro | CP, adiantamentos, saldo por fornecedor |
| Analistas de BI | Todas as camadas com detalhe operacional |

Essas pessoas precisam tomar decisões rápidas. A tela deve ser densa, clara e orientada à ação.

## Problemas que o BI precisa responder

- Onde está concentrado o dinheiro comprado?
- Quais fornecedores e produtos estão na curva ABC mais relevante?
- Onde compramos acima da menor cotação?
- Quais produtos têm pouca concorrência de cotação?
- Quais itens tiveram inflação ou impacto relevante?
- Quais fornecedores misturam alto volume de compra com risco fiscal?
- Onde há contas a pagar, vencimentos e adiantamentos pendentes?
- Quais dados precisam ser saneados antes de uma decisão?

## Direção de produto

Este BI **não deve parecer uma landing page**. Ele deve parecer uma **ferramenta de trabalho**.

Interface:
- compacta
- confiável
- densa sem ficar confusa
- com filtros sempre visíveis
- com KPIs no topo
- com tabelas fortes e compactas
- com painéis de detalhe expansível
- com chips de status
- com hierarquia visual clara
- com pouco texto explicativo dentro da interface

## Base visual

Tudo segue o `BI Design System.html` e o mock `BI Suprimentos v4.html`:

- fundo cinza claro (`--bg: #f3f6fa`)
- cards brancos com borda discreta
- tipografia Segoe UI / Arial, 13px base
- azul como cor de ação (`--blue: #2563eb`)
- verde/amarelo/vermelho para status
- tabelas compactas com linhas expansivas
- grid de KPIs de 8 colunas

## Primeira tela

Abre direto no **Resumo**. Sem splash, capa ou introdução.

Mostra imediatamente:
- título `BI de Suprimentos`
- busca global
- filtros globais
- abas de navegação
- KPIs principais
- gráficos/tabelas de síntese
- alertas executivos

## Linguagem da interface

Português do Brasil. Exemplos de labels:

- Total comprado
- Impacto R$
- Oportunidade R$
- Fornecedores
- Produtos/IDs
- Compras com cotação
- Risco fiscal
- CP em aberto
- AD pendente
- Curva
- Menor cotação
- PMP 12m
- Prioridade

## Tamanhos alvo

- 1366×768 (notebooks)
- 1440×900
- funcionável em telas largas
