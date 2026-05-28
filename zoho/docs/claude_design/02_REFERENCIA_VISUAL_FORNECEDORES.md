# Referencia visual - Painel de Fornecedores

## Arquivo de referencia

Painel atual:

`output/04_visualizacao/08b_painel_fornecedores_regime_fiscal.html`

Este painel deve ser a base visual do novo BI.

## Personalidade visual

O painel atual e:

- operacional;
- compacto;
- de leitura rapida;
- centrado em filtros, KPIs e tabela;
- mais proximo de uma ferramenta de analise do que de um dashboard decorativo.

O novo BI deve preservar essa personalidade.

## Tokens visuais principais

Fonte:

- `Segoe UI, Arial, sans-serif`

Cores:

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

Uso recomendado:

- `--bg`: fundo geral da aplicacao.
- `--card`: paineis, cards, tabelas e menus.
- `--ink`: textos principais.
- `--muted`: labels, metadados e textos secundarios.
- `--line`: bordas e divisorias.
- `--blue`: acao principal, filtros ativos, links e destaque positivo de navegacao.
- `--green`: sucesso, credito alto resolvido, conciliado.
- `--yellow`: atencao, condicionado, validacao.
- `--red`: risco, vencido, impacto negativo, divergencia.
- `--gray`: neutro, sem dado, baixo impacto.

## Estrutura visual atual

Casca:

```text
+----------------------------------------------------------------------------------+
| Titulo                                 [Busca global.........................] [?] |
+----------------------------------------------------------------------------------+
| Filtros em grade compacta                                                        |
+----------------------------------------------------------------------------------+
| KPI cards compactos                                                              |
+----------------------------------------------------------------------------------+
| Tabela principal com cabecalho fixo visual, linhas compactas e expandiveis        |
+----------------------------------------------------------------------------------+
```

## Medidas e componentes que devem ser reutilizados

Pagina:

- padding de aproximadamente `14px 16px 24px`;
- fundo `#f3f6fa`;
- fonte base `13px`.

Topo:

- titulo com `24px`, peso forte;
- busca global com altura `38px`;
- botao de metodologia/ajuda com aproximadamente `42px`.

Filtros:

- grade com 5 colunas no desktop;
- gap de `8px`;
- labels em uppercase, `10px`, negrito;
- botoes com altura aproximada `31px`;
- borda `#c9d5e3`;
- borda arredondada de `7px`;
- filtro ativo com fundo `#eff6ff` e borda azul.

KPIs:

- cards brancos;
- borda `#dbe2eb`;
- raio `8px`;
- padding compacto;
- label uppercase pequena;
- valor forte com aproximadamente `20px`.

Tabelas:

- container branco com borda e raio de `10px`;
- cabecalho com fundo `#e9eff7`;
- labels uppercase;
- linhas com `padding` compacto;
- hover suave;
- colunas com larguras planejadas;
- linhas expansivas para detalhe.

Paineis de detalhe:

- aparecem dentro da linha expandida;
- usam grid;
- cards internos brancos;
- borda discreta;
- titulos pequenos;
- pares chave/valor;
- chips de status.

## Componentes de status

Chips/pills:

```css
.tag, .pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 22px;
  border-radius: 999px;
  padding: 0 8px;
  font-weight: 800;
  font-size: 11px;
  white-space: nowrap;
}
```

Tons:

- verde: resolvido, alto potencial, conciliado.
- amarelo: condicionado, pendente de validacao, atencao.
- vermelho: vencido, divergencia, risco alto, impacto negativo.
- azul: ativo, selecionado, informativo, curva relevante.
- cinza: neutro, sem dado, indeterminado.

## Elementos que devem migrar para o BI

Reutilizar:

- busca global;
- filtros compactos;
- KPIs no topo;
- tabela com linhas expansivas;
- chips de status;
- badges de empresa;
- modal de metodologia;
- paginacao compacta;
- paineis de detalhe em grid;
- tabela como centro da experiencia.

Adaptar:

- trocar "Painel de Fornecedores" por "BI de Suprimentos";
- adicionar navegacao por abas;
- adicionar graficos compactos;
- expandir fornecedor para incluir compras, cotacoes, fiscal, financeiro e adiantamentos;
- criar fila de oportunidades como componente principal.

Evitar:

- layout de marketing;
- hero grande;
- graficos gigantes sem tabela;
- visual com excesso de gradiente;
- cards aninhados demais;
- espacos vazios excessivos.

