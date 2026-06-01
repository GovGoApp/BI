# Pacote para Claude Design - BI de Suprimentos

Este pacote foi criado para orientar o Claude Design na geracao do primeiro mock visual do `BI de Suprimentos`.

O objetivo e dar contexto suficiente para ele criar uma tela operacional, bonita e utilizavel, sem precisar conhecer todo o historico do repositorio.

## Como usar

1. Abra o arquivo `PROMPT_COMPLETO_CLAUDE_DESIGN.md`.
2. Cole o conteudo no Claude Design.
3. Anexe, se possivel, uma captura ou o HTML do painel atual de fornecedores:
   - `output/04_visualizacao/08b_painel_fornecedores_regime_fiscal.html`
4. Peca para gerar um mock navegavel em HTML/CSS/JS ou um design de alta fidelidade com as paginas separadas.

## Ordem recomendada dos documentos

1. `PROMPT_COMPLETO_CLAUDE_DESIGN.md`
2. `01_BRIEFING_MOCKUP_BI_SUPRIMENTOS.md`
3. `02_REFERENCIA_VISUAL_FORNECEDORES.md`
4. `04_MAPA_PAGINAS_E_COMPONENTES.md`
5. `05_DADOS_E_DOMINIOS_SUPRIMENTOS.md`
6. `06_CRITERIOS_ACEITACAO_DESIGN.md`
7. `07_REFERENCIAS_LOCAIS.md`

## Resultado esperado

O resultado ideal e um mock inicial do BI com:

- casca de aplicacao;
- filtros globais;
- navegacao por paginas/abas;
- resumo executivo;
- fornecedor 360;
- fila de oportunidades;
- produto/preco;
- cotacoes;
- inflacao e impacto;
- fiscal 2027;
- financeiro;
- adiantamentos;
- qualidade dos dados.

O mock nao precisa estar conectado a dados reais. Ele deve usar dados ficticios, mas plausiveis, baseados nos nomes de campos e conceitos descritos neste pacote.
