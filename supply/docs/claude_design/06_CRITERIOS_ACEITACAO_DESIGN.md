# Criterios de aceitacao - Mock BI de Suprimentos

Use este checklist para avaliar se o mock esta bom.

## Estrutura

- A primeira tela abre diretamente no `Resumo Executivo`.
- Existe titulo `BI de Suprimentos`.
- Existe busca global.
- Existem filtros globais.
- Existe navegacao por abas ou secoes.
- Existem pelo menos as paginas:
  - Resumo;
  - Fornecedor 360;
  - Oportunidades;
  - Produtos e Precos;
  - Cotacoes;
  - Inflacao e Impacto;
  - Fiscal 2027;
  - Financeiro;
  - Adiantamentos;
  - Qualidade dos Dados.

## Visual

- O design lembra o painel de fornecedores.
- Fundo geral cinza claro.
- Cards e paineis brancos.
- Bordas discretas.
- Tipografia compacta e profissional.
- Cores de status sao consistentes.
- Azul e usado para acao/selecionado.
- Verde, amarelo e vermelho comunicam situacao.
- Nao ha excesso de gradientes.
- Nao ha elementos decorativos sem funcao.

## Experiencia

- A tela parece uma ferramenta de trabalho, nao uma pagina de marketing.
- Os filtros sao faceis de encontrar.
- Os KPIs aparecem antes dos detalhes.
- As tabelas sao centrais na experiencia.
- Existem linhas expansivas ou paineis de detalhe.
- A fila de oportunidades e acionavel.
- O usuario entende qual problema atacar primeiro.
- Nao ha textos longos explicando o produto dentro da interface.

## Conteudo

- O mock usa termos reais do dominio:
  - Curva;
  - ID;
  - PMP;
  - QTD_COT;
  - Menor cotacao;
  - Impacto;
  - Regime fiscal;
  - Credito 2027;
  - CP;
  - AD.
- Os dados ficticios parecem plausiveis.
- Ha pelo menos um exemplo de alerta economico.
- Ha pelo menos um exemplo de alerta fiscal.
- Ha pelo menos um exemplo de alerta financeiro.
- Ha pelo menos um exemplo de adiantamento pendente.

## Componentes obrigatorios

- Filtros em grade.
- KPI cards.
- Abas.
- Tabela principal.
- Chips/pills de status.
- Badges de empresa.
- Grafico compacto de tendencia.
- Barras horizontais ou ranking.
- Linha ou painel expandido.
- Modal ou botao de metodologia.
- Botao de exportacao.

## Responsividade

- Deve funcionar bem em 1366x768.
- Deve funcionar bem em 1440x900.
- A interface pode ser desktop-first.
- Em telas menores, filtros podem quebrar para menos colunas.
- Texto de botao e chip nao deve estourar.
- Tabelas podem usar scroll horizontal se necessario.

## Evitar

- Hero visual.
- Tela inicial vazia.
- Cards gigantes sem funcao.
- Graficos grandes demais.
- Paleta dominada por uma unica cor.
- Gradientes roxos/azuis como tema principal.
- Layout de SaaS marketing.
- Explicacoes longas no meio da tela.
- Cards dentro de cards sem necessidade.
- Texto pequeno demais para leitura.

## Entrega esperada

Idealmente, o Claude Design deve entregar:

- um mock de alta fidelidade;
- HTML/CSS/JS em arquivo unico, se possivel;
- navegacao funcional entre paginas;
- dados ficticios realistas;
- breve descricao dos componentes criados;
- observacao de como aplicou a referencia do painel de fornecedores.
