# Diario de Bordo do Projeto Fornecedores

Este diario e o ponto oficial de retomada do projeto.

## Regra De Retomada

Em uma nova conversa, ler nesta ordem:

1. `docs/DIARIO_DE_BORDO.md`
2. `README.md`
3. `docs/PLANO_DE_ACAO.md`
4. `docs/ESTUDO_CENARIO_FISCAL_2026_2027.md`
5. `docs/LEVANTAMENTO_BASES_INICIAIS.md`

## Regra De Atualizacao

- Toda nova entrada deve ir dentro da data correta em `## Registro Por Data E Assunto`.
- Dentro da data, usar um titulo de assunto (`#### Assunto`) antes das entradas.
- Se a anotacao ficar longa demais, criar um documento especifico em `docs/` e registrar aqui apenas a decisao central e o caminho.
- Nao empilhar entradas soltas no fim do arquivo.
- Registrar tambem descobertas de ambiente, riscos e mudancas de direcao.
- Qualquer modificacao feita no repositorio deve atualizar este diario no mesmo ciclo de trabalho.
- O registro deste diario deve ser tecnico, preciso e detalhado: arquivos alterados, motivacao, decisao, impactos, testes e pendencias.
- Quando um assunto ou frente de trabalho for encerrado, atualizar tambem o `README.md` de forma ampla e generica, para que a retomada futura entenda o estado atual sem precisar reler todos os detalhes tecnicos.

## Registro Por Data E Assunto

### 2026-05-28

#### Padronizacao do design do BI Suprimentos e governanca documental

- Foi definida a pasta `zoho/design/` como local canonico para os modelos visuais do BI.
- O arquivo `zoho/design/BI Suprimentos v4.html` passou a ser o modelo padrao de pagina para o BI de Suprimentos.
- O arquivo `zoho/design/BI Design System.html` passou a ser o sistema de design padrao para todas as novas geracoes de telas, componentes e mockups de BI.
- Os arquivos historicos de design em `zoho/design/` mantem versoes anteriores para comparacao, mas a referencia operacional principal passa a ser a versao `v4`.
- O `README.md` foi atualizado com:
  - regra geral de governanca de documentacao;
  - referencia ao modelo padrao `BI Suprimentos v4.html`;
  - referencia ao sistema padrao `BI Design System.html`;
  - convencao de que novas geracoes de design devem partir dessas referencias, salvo nova decisao registrada neste diario.
- A regra de atualizacao deste diario foi reforcada:
  - qualquer modificacao no repositorio deve gerar registro tecnico no diario;
  - o registro deve conter motivacao, arquivos alterados, decisao, impacto, testes e pendencias quando aplicavel;
  - ao encerrar uma frente de trabalho, o `README.md` deve ser atualizado em linguagem mais ampla e sintetica.

#### Mapa funcional das 15 abas do BI Suprimentos v4

- Foi criado o documento `zoho/docs/MAPA_ABAS_ELEMENTOS_BI_SUPRIMENTOS_V4.md`.
- O documento foi extraido do arquivo canonico `zoho/design/BI Suprimentos v4.html`.
- A nomenclatura das abas foi congelada conforme o design v4:
  - `Resumo`
  - `Oportunidades`
  - `Categorias`
  - `Filiais`
  - `Estoque`
  - `Fornecedor`
  - `Produtos`
  - `Cotações`
  - `Impacto`
  - `Inflação`
  - `Fiscal`
  - `Financeiro`
  - `Adiantamentos`
  - `Serviços`
  - `Dados`
- Para cada aba, foram listados os KPIs, graficos, cards, relatorios, tabelas, controles internos e, quando aplicavel, as origens Zoho explicitadas no design.
- O `README.md` foi atualizado para apontar para esse mapa funcional como referencia de composicao do BI v4.

#### Arquitetura modular, sub-elementos e layout editavel

- Foi criado o documento `zoho/docs/ARQUITETURA_MODULAR_BI_SUPRIMENTOS.md`.
- A arquitetura formaliza a cadeia `Fonte de dado -> Dataset -> Metrica -> Elemento -> Sub-elementos -> Layout -> Aba`.
- Foi adotado grid de `16` colunas para posicionamento de elementos, substituindo a ideia inicial de grid de `12` colunas.
- A decisao pelo grid de 16 colunas foi registrada por facilitar divisoes pares, quartos, oitavos e telas densas de BI.
- Foi previsto um `modo edicao` para reposicionar elementos com arrastar de mouse, resize, snap to grid, rascunho, publicacao, undo/redo e validacao antes de publicar.
- O conceito de `sub-elementos` foi formalizado para permitir modularidade interna dos blocos visuais.
- Exemplos de sub-elementos padronizados:
  - `text.title`
  - `text.subtitle`
  - `text.origin`
  - `metric.primary`
  - `metric.delta`
  - `tag.status`
  - `counter`
  - `sparkline`
  - `legend`
  - `table.column`
  - `table.cell_badge`
  - `table.cell_bar`
  - `action.button`
  - `tooltip`
  - `empty_state`
  - `loading_state`
  - `error_state`
- Foi criado o arquivo `zoho/config/bi_suprimentos_modular_schema.yml` como primeiro contrato conceitual em YAML.
- O schema registra:
  - abas canonicas do BI v4;
  - configuracao de grid de 16 colunas;
  - camadas de fontes, datasets, metricas, elementos e layouts;
  - tipos de fontes;
  - tipos de elementos;
  - tipos de sub-elementos;
  - regras planejadas de modo edicao;
  - exemplo de elemento modular.
- O `README.md` foi atualizado para apontar para a arquitetura modular e para o schema YAML.

#### POC modular da aba Impacto com dados reais do Zoho

- Foi criada uma prova de conceito funcional para testar a arquitetura modular antes de expandir para as 15 abas.
- A aba escolhida foi `Impacto`, por concentrar uma cadeia clara entre fonte real, metrica de negocio, KPI, graficos, tabela e layout editavel.
- Foi criado o arquivo `zoho/config/bi_suprimentos_impacto_poc.yml`.
- O YAML define:
  - fonte real `NFE` do workspace `SUPRIMENTOS`;
  - consulta SQL de extracao com campos de impacto de cotacao;
  - dataset `impacto_cotacao_por_id`;
  - metricas `impacto_cotacao_total`, `impacto_cotacao_liquido`, `percentual_acima_menor` e `ids_com_impacto`;
  - oito elementos modulares: quatro KPIs, dois graficos, uma tabela e uma nota tecnica;
  - layout em grid de 16 colunas para a aba `Impacto`.
- Foi criado o script `zoho/scripts/build_modular_impacto_poc.py`.
- O script gera uma pagina HTML standalone a partir do YAML e do CSV real exportado do Zoho.
- O script tambem pode atualizar a fonte diretamente no Zoho com `--refresh-zoho`, usando `zoho/zoho.env`, sem expor credenciais no repositorio.
- A leitura da fonte foi implementada com `csv` da biblioteca padrao, evitando dependencia de `pandas` nesta POC por causa de conflito local entre `NumPy 2.x` e extensoes compiladas para `NumPy 1.x`.
- Foi adicionada a dependencia `PyYAML>=6,<7` em `requirements.txt`.
- Artefatos gerados localmente, ignorados pelo Git:
  - `zoho/output/modular_test/data/impacto_nfe_limit5000.csv`;
  - `zoho/output/modular_test/data/impacto_modular_poc_data.json`;
  - `zoho/output/modular_test/bi_impacto_modular_poc.html`.
- A execucao local usou `10.000` linhas reais presentes no CSV de impacto.
- Resultado do recorte total:
  - impacto positivo: `R$ 2.745.438`;
  - linhas acima do menor preco: `4.474`;
  - IDs unicos: `1.932`;
  - IDs com impacto positivo: `995`;
  - UF lider: `PE`;
  - categoria lider: `I1 - ESTOCAVEIS`.
- A pagina gerada possui:
  - filtros vivos por `UF`, `Categoria`, `Curva ID` e `Leitura`;
  - recalcule automatico de KPIs, graficos, ranking e nota tecnica no navegador;
  - modo edicao para arrastar modulos pelo cabecalho;
  - persistencia de posicao em `localStorage`;
  - botao de reset de layout;
  - grid responsivo de 16 colunas no desktop e empilhamento em telas menores.
- Validacoes executadas:
  - `python -m py_compile zoho\scripts\build_modular_impacto_poc.py`;
  - `python zoho\scripts\build_modular_impacto_poc.py`;
  - `node --check` sobre o JavaScript extraido do HTML gerado;
  - Microsoft Edge headless com `--dump-dom`, confirmando renderizacao, populacao de filtro real `PE` e textos recalculados no DOM;
  - `python -m unittest discover -s zoho\tests`, com `13` testes aprovados.
- Esta POC confirma que a cadeia `YAML -> dados reais -> elementos -> layout -> HTML interativo` funciona e pode ser expandida para outras abas.

### 2026-05-21

#### Ajustes pontuais do painel de auditoria

- O layout geral de `output/fase_04_visualizacao/04_painel_auditoria_fornecedores.html` foi preservado conforme orientacao expressa do usuario.
- O filtro e a coluna `Credito 2027` passaram a aparecer apenas como `Credito`.
- As tags de credito passaram a usar nomes completos:
  - `Alto`
  - `Condicionado`
  - `Baixo`
  - `Indeterminado`
  - `Sem dado`
- A leitura de regime tambem deixou de usar abreviacoes operacionais na interface, trocando `Indet.` e `S/D` por `Indeterminado` e `Sem dado`.
- Todos os filtros categoricos mantem `Todos` como estado inicial, e o filtro fica destacado visualmente quando o usuario escolhe valores especificos.
- A busca livre tambem passou a ficar destacada quando estiver preenchida.
- O controle de `Campos visiveis` deixou de ser uma janela/modal e foi incorporado como filtro `Campos` na segunda linha de filtros.
- Foram adicionados icones de ajuda `(?)` em filtros e colunas, com tooltip explicando a finalidade de cada controle.
- A janela de metodologia foi ampliada para explicar objetivo da tela, consolidacao por fornecedor, movimento/curva, enriquecimento OpenCNPJ, leitura fiscal 2026/2027, tags de credito e limites da analise.
- Nos detalhes da linha, foram removidas as tags operacionais com `empresa + linha da planilha + codigo J/F`, por serem pouco uteis visualmente naquele ponto.
- As tags dos detalhes foram redistribuidas por assunto:
  - `Cadastro original`: email faltante, inscricao estadual faltante, inscricao municipal faltante, divergencia de razao social, divergencia de fantasia e divergencia de email.
  - `Fiscal e credito`: alertas fiscais que nao sao divergencias cadastrais, como `regime_indeterminado`.
  - `Operacao e saneamento`: sinais ligados aos campos operacionais exibidos no box, como movimento NFe, curva e impacto de compra.
- O HTML foi regenerado pelo script `scripts/build_supplier_audit_panel.py`, mantendo `15.719` fornecedores consolidados no painel.

#### Correcao do comportamento dos filtros e da metodologia

- O comportamento do `Todos` nos filtros de multipla escolha foi corrigido:
  - no estado inicial, `Todos` e todas as opcoes especificas ficam marcados;
  - se todas as opcoes especificas estiverem marcadas, o filtro volta ao estado neutro `Todos`;
  - se o usuario desmarcar uma opcao especifica, `Todos` deixa de estar marcado e o filtro passa a restringir;
  - se o usuario desmarcar `Todos`, todas as opcoes sao desmarcadas e o filtro retorna zero resultados.
- Os textos de ajuda dos filtros e colunas foram ampliados para explicar conceito, origem do dado, opcoes e forma correta de leitura.
- A janela de metodologia recebeu explicacao mais longa sobre fontes, consolidacao por fornecedor, qualidade cadastral, divergencias, movimento/curva, Reforma Tributaria, credito, acoes e limite tecnico da analise.
- O box `Operacao e saneamento` deixou de mostrar tags cadastrais complementares (`telefone_suporte`, `site`, `grupo_fiscal`), pois esses itens nao pertencem aos campos de curva, NFe, UFs e anos exibidos naquele box.
- O box `Operacao e saneamento` passou a mostrar apenas tags ligadas a operacao, como `sem movimento NFe`, `sem curva` ou `alto impacto de compra`.

#### Versoes 04 e 05 do painel de auditoria

- A versao `04` do painel foi mantida como versao principal sem endereco/contato adicional.
- Na versao `04`, o box `Cadastro original` foi reorganizado:
  - removeu `Empresas`, pois a informacao ja aparece na linha principal do fornecedor;
  - manteve `Email`;
  - passou a exibir a situacao interna como `Ativa`, `Inativa` ou `Sem dado`, em vez de `A`/`I`.
- A versao `04` passou a manter fixa a area superior do painel e o cabecalho da tabela durante a rolagem vertical da pagina.
- Foi criado `scripts/build_opencnpj_address_export.py` para materializar no CSV campos de endereco e contato ja existentes no cache bruto da `OpenCNPJ`.
- O novo CSV foi salvo em `output/fase_03_enriquecimento/06_fornecedores_opencnpj_enriquecidos_lote_completo_com_endereco.csv`.
- O novo CSV inclui campos como `endereco_tipo_logradouro`, `endereco_logradouro`, `endereco_numero`, `endereco_complemento`, `endereco_bairro`, `endereco_cep`, `endereco_municipio`, `endereco_uf`, `endereco_completo` e `contatos_qsa`.
- Foi criado `scripts/build_supplier_audit_panel_v05.py` para gerar a nova versao `05` do painel, baseada na `04`.
- A versao `05` foi salva em `output/fase_04_visualizacao/05_painel_auditoria_fornecedores_endereco.html`.
- Na versao `05`, o box `Cadastro original` nao mostra email.
- Na versao `05`, foi incluido o box `Informacoes`, com endereco, cidade, UF, telefones, emails e contato.
- Na versao `05`, foi incluido filtro de multipla escolha `UF` ao lado direito do filtro `Empresa`, usando a UF cadastral/oficial do fornecedor obtida via OpenCNPJ, nao a UF de NFe.

#### Ajuste de layout exclusivo da versao 05

- Por orientacao do usuario, a versao `04` nao deve mais ser alterada nesta etapa.
- A partir deste ponto, os ajustes de layout foram aplicados somente em `scripts/build_supplier_audit_panel_v05.py` e no HTML `output/fase_04_visualizacao/05_painel_auditoria_fornecedores_endereco.html`.
- Na versao `05`, o campo de busca saiu da grade de filtros e foi movido para o cabecalho, ao lado do titulo `Painel de Fornecedores`.
- Com a retirada da busca da grade, os filtros da versao `05` voltaram a caber em duas linhas horizontais, iniciando em `Empresa` e terminando em `Campos`.
- O cabecalho da tabela da versao `05` deixou de usar `position: sticky` diretamente nas celulas `th`, pois isso causava deslocamento visual sobre as linhas expandidas.
- A versao `05` passou a renderizar o cabecalho da tabela em uma tabela separada dentro da area fixa superior, e os dados em outra tabela abaixo, mantendo o scroll vertical da pagina.

### 2026-05-20

#### Estruturacao inicial do projeto

- Foi criado o `README.md` inicial do projeto com escopo, bases, direcao fiscal e ordem oficial de leitura.
- Foi criado este `docs/DIARIO_DE_BORDO.md` como ponto oficial de continuidade.
- Foi criado `docs/PLANO_DE_ACAO.md` com a proposta de fases para o projeto.
- Foi criado `docs/LEVANTAMENTO_BASES_INICIAIS.md` com o inventario inicial das bases locais.
- Foi criado `docs/ESTUDO_CENARIO_FISCAL_2026_2027.md` com a pesquisa regulatoria em fontes oficiais sobre a transicao 2026/2027.
- Foi criado `scripts/inventario_fontes.py` para reproduzir o levantamento das bases locais.

#### Ajuste da estrutura de fontes e entrega da fase 1 cadastral

- O usuario moveu as planilhas operacionais para `data/` e manteve `docs/` apenas para documentacao; os scripts e documentos principais foram ajustados para seguir essa convencao.
- Foi criado `scripts/build_supplier_base.py` para materializar a fase 1 do projeto.
- O novo script gera quatro artefatos em `output/fase_01_cadastro/`:
  - `01_fornecedores_cadastro_normalizado.csv`
  - `02_fornecedores_cadastro_unificado.csv`
  - `03_fornecedores_pendencias_cadastrais.csv`
  - `04_fornecedores_resumo_cadastral.json`
- A base normalizada trabalha em nivel de registro de origem.
- A base unificada consolida o fornecedor por `CNPJ`.
- O relatorio de pendencias destaca o que falta e onde ha divergencia entre empresas/cadastros do grupo.
- O resumo cadastral agrega contagem por faixa de completude, pendencias mais frequentes e divergencias.

#### Regra de completude cadastral implementada

- A fase 1 passou a medir completude com score de `0` a `100`.
- Os componentes considerados no score sao: `CNPJ`, razao social, nome fantasia, email, inscricao estadual, inscricao municipal, telefone de suporte, site, situacao interna ativa, data de cadastro, grupo fiscal e indicador de contribuinte `ICMS`.
- As faixas atuais ficaram definidas como:
  - `alta`: `>= 85`
  - `media`: `>= 60`
  - `baixa`: `< 60`
- O score atual e operacional e foi desenhado para saneamento cadastral; ele ainda nao representa validacao fiscal oficial.
- As pendencias passaram a ser separadas entre `essenciais` e `complementares`, para evitar que a fila de saneamento fique poluida apenas por campos menos criticos.

#### Resultado da primeira geracao da base cadastral

- A primeira geracao da fase 1 produziu `25.554` registros normalizados em `output/fase_01_cadastro/01_fornecedores_cadastro_normalizado.csv`.
- A consolidacao por chave de fornecedor produziu `15.719` registros unificados em `output/fase_01_cadastro/02_fornecedores_cadastro_unificado.csv`.
- Desses `15.719`, `15.718` possuem `CNPJ` valido e `1` ficou identificado explicitamente como caso sem `CNPJ` valido por meio de `chave_unificacao` sintetica.
- O resumo consolidado foi salvo em `output/fase_01_cadastro/04_fornecedores_resumo_cadastral.json`.
- O score medio da base unificada ficou em `68,41`.
- Distribuicao de completude da base unificada:
  - `3.033` fornecedores com completude `alta`
  - `7.793` fornecedores com completude `media`
  - `4.893` fornecedores com completude `baixa`
- `12.791` fornecedores possuem ao menos uma pendencia considerada essencial.
- Pendencias essenciais mais frequentes:
  - inscricao municipal: `10.197`
  - email: `10.040`
  - inscricao estadual: `6.287`
- Pendencias complementares mais frequentes:
  - telefone de suporte: `15.719`
  - site: `15.577`
  - grupo fiscal: `15.016`
- Divergencias detectadas entre registros do mesmo fornecedor:
  - razao social: `959`
  - nome fantasia: `1.091`
  - inscricao estadual: `181`
  - inscricao municipal: `10`
  - status interno: `2`

#### Entrega da fase 2 de reconciliacao com movimento

- Foi criado `scripts/build_supplier_reconciliation.py` para cruzar a base unificada com `data/NFE.csv` e `data/CURVA_FORN_-_TODAS.csv`.
- O script gera quatro artefatos em `output/fase_02_reconciliacao/`:
  - `01_fornecedores_reconciliados_movimento.csv`
  - `02_fornecedores_prioridade_saneamento.csv`
  - `03_fornecedores_movimento_sem_cadastro.csv`
  - `04_fornecedores_reconciliacao_resumo.json`
- A reconciliacao usa os codigos `CDFORNECED`/`CDFORNECED_OFICIAL` como ponte entre cadastro e movimento.
- Ficou explicitado no processo que:
  - prefixo `J` indica pessoa juridica com `CNPJ`;
  - prefixo `F` indica pessoa fisica com `CPF`.
- Foi implementada regra explicita para conflito de codigo: quando o mesmo codigo aponta para mais de uma chave de fornecedor, a reconciliacao prioriza a chave com `CNPJ` valido e melhor completude.
- Foi detectado um conflito real de codigo (`J02113565000100`) entre um registro com `CNPJ` valido e outro sem `CNPJ` valido; o conflito passa a ficar auditavel no resumo da reconciliacao.
- A fase 2 tambem introduziu um `prioridade_saneamento_score` para ordenar fornecedores com movimento real e problema cadastral.

#### Resultado da reconciliacao com NFE e curva

- A reconciliacao gerou `15.719` fornecedores analisados em `output/fase_02_reconciliacao/01_fornecedores_reconciliados_movimento.csv`.
- `2.686` fornecedores aparecem com movimento na `NFE`.
- `1.527` fornecedores aparecem na `CURVA_FORN`.
- `2.649` fornecedores entraram na fila de saneamento prioritario em `output/fase_02_reconciliacao/02_fornecedores_prioridade_saneamento.csv`.
- `594` fornecedores com movimento ficaram fora do cadastro mestre reconciliado e foram listados em `output/fase_02_reconciliacao/03_fornecedores_movimento_sem_cadastro.csv`.
- Entre esses `594`, a distribuicao por prefixo do codigo foi:
  - `F`: `582`
  - `I`: `3`
  - `O`: `9`
- A leitura operacional inicial e que ha um subconjunto relevante de pessoas fisicas e outros codigos fora do padrao `J...`, exigindo tratamento separado no saneamento e no desenho da politica fiscal.
- Pendencias essenciais mais frequentes entre fornecedores com movimento:
  - inscricao municipal: `2.448`
  - email: `2.229`
  - inscricao estadual: `1.535`

#### Entrega inicial do enriquecimento OpenCNPJ

- Foi criado `scripts/enrich_suppliers_opencnpj.py` com cache local em `output/fase_03_enriquecimento/99_cache_opencnpj/`.
- O script consome a fila `output/fase_02_reconciliacao/02_fornecedores_prioridade_saneamento.csv` e gera artefatos de enriquecimento por lote.
- O piloto inicial foi substituido pelo lote completo para evitar ambiguidade de artefatos.

#### Resultado consolidado da fase 3

- A Fase 3 foi executada sobre os `2.649` fornecedores da fila prioritaria PJ/CNPJ.
- Foram gerados os artefatos canonicos:
  - `output/fase_03_enriquecimento/01_fornecedores_opencnpj_enriquecidos_lote_completo.csv`
  - `output/fase_03_enriquecimento/02_fornecedores_opencnpj_enriquecidos_lote_completo_resumo.json`
  - `output/fase_03_enriquecimento/03_fornecedores_classificacao_fiscal_inicial_lote_completo.csv`
  - `output/fase_03_enriquecimento/04_fornecedores_classificacao_fiscal_inicial_lote_completo_resumo.json`
  - `output/fase_03_enriquecimento/05_mapa_comparacao_original_para_fases.csv`
- O cache local da `OpenCNPJ` foi mantido em `output/fase_03_enriquecimento/99_cache_opencnpj/`.
- No lote completo:
  - `2.485` respostas vieram diretamente da API
  - `140` vieram do cache
  - `21` ficaram como `erro_requisicao`
  - `3` ficaram como `http_404`
- Distribuicao de `regime_indiciado`:
  - `simples_nacional`: `972`
  - `regime_nao_simples`: `637`
  - `mei`: `211`
  - `indeterminado`: `829`
- Distribuicao inicial de `potencial_credito_2027_inicial`:
  - `potencial_condicionado`: `972`
  - `alto_potencial`: `637`
  - `baixo_ou_inexistente`: `211`
  - `indeterminado`: `829`
- Na classificacao fiscal inicial:
  - `2.554` fornecedores ficaram com situacao cadastral oficial `ativa`
  - `92` ficaram com situacao oficial `nao_ativa`
  - `3` ficaram `nao_consultados`
- A separacao entre saneamento cadastral e validacao fiscal passou a ser explicita:
  - `2.626` ainda exigem saneamento cadastral
  - `2.145` exigem validacao fiscal
  - `504` ja nao exigem validacao fiscal adicional pelos criterios atuais
- Foi reforcada a leitura de que a `OpenCNPJ` nem sempre devolve `opcao_simples` e `opcao_mei`; isso explica parte relevante dos `829` casos `indeterminados`.

#### Entrega da fase 4 visual

- Foi criado `scripts/build_visual_review_pack.py` para transformar os resultados das fases anteriores em entregaveis visuais e navegaveis.
- A fase 4 foi desenhada para responder a tres necessidades do usuario:
  - enxergar claramente o antes e o depois do cadastro;
  - devolver uma planilha no mesmo formato da original, mas com novos campos analiticos destacados;
  - navegar os dados em uma pagina HTML interativa.
- Foram gerados tres artefatos canonicos em `output/fase_04_visualizacao/`:
  - `01_antes_depois_visual_fornecedores.xlsx`
  - `02_fornecedores_formato_original_com_campos_gvg.xlsx`
  - `03_painel_interativo_fornecedores.html`

#### Caracteristicas da fase 4

- A planilha `01_antes_depois_visual_fornecedores.xlsx` organiza o comparativo em abas por empresa (`IDEAL`, `MELHOR`, `POMME`) e inclui legenda visual.
- O comparativo usa cores para separar:
  - campos originais `ANTES_*`
  - campos enriquecidos `DEPOIS_*`
  - campos de analise operacional/fiscal
  - situacoes de atencao, risco ou ausencia de dados
- A planilha `02_fornecedores_formato_original_com_campos_gvg.xlsx` preserva a estrutura do cadastro mestre e acrescenta colunas `GVG_*` ao final, em cor propria, para facilitar retorno ao BD sem descaracterizar o layout original.
- O arquivo `03_painel_interativo_fornecedores.html` foi gerado como pagina standalone, sem dependencia de servidor local, com filtros de busca, empresa, movimento e potencial de credito.
- A fase 4 consome como insumos a base original em `data/`, o cadastro normalizado da fase 1, a reconciliacao da fase 2 e a classificacao fiscal inicial da fase 3.

#### Ajuste visual pontual no painel HTML

- O layout do arquivo `output/fase_04_visualizacao/03_painel_interativo_fornecedores.html` foi simplificado por solicitacao do usuario.
- A barra lateral fixa foi removida.
- O cabecalho visivel passou a exibir somente o titulo `Painel de Fornecedores`.
- O script gerador `scripts/build_visual_review_pack.py` foi ajustado para preservar essa nova estrutura nas proximas regeneracoes.

#### Redesenho funcional do painel HTML

- O usuario sinalizou que a primeira versao do painel HTML nao resolvia o problema principal de leitura.
- O painel foi redesenhado para que a propria tabela principal mostre, por fornecedor:
  - o cadastro original;
  - os dados incluidos;
  - a analise incluida;
  - as pendencias e acoes;
  - um resumo direto do que mudou.
- O bloco de detalhes dependente de clique foi retirado da versao principal do painel.
- Foi criada uma segunda rotina geradora no script, `build_html_v2`, e o fluxo principal passou a usar essa nova estrutura.

#### Novo painel de auditoria de fornecedores

- Por decisao do usuario, o HTML antigo nao foi sobrescrito.
- Foi criado `scripts/build_supplier_audit_panel.py` para gerar um novo artefato em `output/fase_04_visualizacao/04_painel_auditoria_fornecedores.html`.
- O novo painel preserva todos os `25.554` registros da planilha original.
- A ordenacao inicial segue a curva de fornecedor por valor, usando `curva_classificacao`, `curva_total_fornecedor` e, em seguida, valor de NFe como desempate.
- Foram implementados os filtros solicitados:
  - empresa;
  - tipo;
  - movimento NFe;
  - curva;
  - situacao oficial;
  - regime;
  - credito 2027;
  - dado novo;
  - divergencia;
  - saneamento;
  - validacao fiscal;
  - acao;
  - completude/prioridade;
  - busca livre.
- Os filtros foram organizados em duas linhas horizontais no desktop, com controles compactos.
- A tabela principal foi redesenhada para nao depender de rolagem horizontal: cada fornecedor aparece em linha resumida e pode ser expandido para ver os detalhes completos.
- Foi incluido seletor de campos visiveis no cabecalho.
- Foi incluido botao de metodologia no cabecalho, com explicacao da logica de enriquecimento, leitura fiscal e tags de credito 2027.
- As tags de credito foram encurtadas para `Alto`, `Cond.`, `Baixo`, `Indet.` e `S/D`.

#### Ajustes pontuais no painel de auditoria

- O layout geral do painel de auditoria foi preservado por orientacao expressa do usuario.
- Todos os filtros categorizados passaram a operar como multipla escolha em dropdown compacto.
- A paginacao foi colocada no mesmo box antes ocupado pelo KPI `Valor curva`.
- A paginacao permite escolher `10`, `20`, `30`, `40`, `50` ou `100` fornecedores por pagina.
- A paginacao inclui controles de primeira pagina, pagina anterior, input numerico da pagina, proxima pagina e ultima pagina.
- A lista principal passou a consolidar fornecedor por chave/documento, exibindo uma unica linha por fornecedor.
- Quando um fornecedor aparece em mais de uma empresa, a linha mostra tags coloridas:
  - `IDEAL`: azul;
  - `MELHOR`: verde;
  - `POMME`: vermelho.
- O codigo interno `J...`/`F...` deixou de aparecer na linha principal; o documento passou a aparecer formatado como CNPJ/CPF.
- As ocorrencias originais por empresa e codigo continuam disponiveis dentro do detalhe expandido.
- A interacao de expansao foi alterada para manter no maximo uma linha aberta por vez.

#### Levantamento das bases locais

- O cadastro mestre `data/FORNECEDORES - TODAS AS EMPRESAS.xlsx` possui `25.554` linhas distribuidas nas abas `IDEAL`, `MELHOR` e `POMME`.
- O cadastro mestre possui `15.718` CNPJs unicos, o que mostra duplicidade relevante entre empresas do grupo.
- `9.579` CNPJs aparecem em pelo menos duas empresas do grupo, e `256` aparecem nas tres.
- A base `data/NFE.csv` possui `237.931` linhas e `3.280` fornecedores unicos com movimento.
- A base `data/CURVA_FORN_-_TODAS.csv` possui `1.621` fornecedores classificados em curva.
- Ha `594` fornecedores da NFe que nao aparecem no cadastro mestre atual e `94` fornecedores da curva que tambem nao aparecem no cadastro mestre atual.

#### Qualidade cadastral inicial

- Todos os registros do cadastro mestre lidos no arquivo principal estao marcados como pessoa juridica (`IDTPIJURFORN = J`).
- A maior parte do cadastro esta com situacao `A`, mas existem registros `I` e alguns poucos vazios.
- O volume de campos vazios em email, inscricao estadual e inscricao municipal e alto o bastante para justificar uma trilha formal de saneamento cadastral antes de qualquer comparacao economica mais avancada.

#### Pesquisa fiscal e regulatoria

- Foi confirmado em fontes oficiais da Receita Federal e do CGIBS que `2026` e ano de testes da Reforma Tributaria do Consumo, com destaque de `CBS` e `IBS` nos documentos fiscais e dispensa de recolhimento para quem cumprir as obrigacoes acessorias.
- Foi confirmado em fontes oficiais que a virada material com impacto mais direto para este projeto ocorre em `01/01/2027`, com entrada em vigor da `CBS` e extincao de `PIS/Cofins`.
- Foi confirmado em material oficial que o fornecedor optante pelo `Simples Nacional` pode afetar o credito do adquirente de forma diferente conforme permaneça no regime unico ou opte pela apuracao regular de `IBS/CBS`.
- Foi registrado no estudo que o credito futuro nao depende apenas do fornecedor, mas tambem da classificacao tributaria da operacao e do item no documento fiscal.

#### Referencia tecnica para integracao por CNPJ

- Foi revisada a implementacao local usada no projeto `C:\\Users\\Haroldo Duraes\\Desktop\\Scripts\\GovGo\\v2`, especialmente `src\\backend\\empresas\\core\\select_engine.py` e `src\\backend\\empresas\\core\\company_resolver.py`.
- A referencia atual usa `GET https://api.opencnpj.org/{cnpj}` com `requests.Session`, retry, timeout configuravel e cache/upsert de retorno.
- Foi validado em `2026-05-20` que a API da `OpenCNPJ` retorna campos uteis para este projeto, incluindo `razao_social`, `nome_fantasia`, `situacao_cadastral`, `data_situacao_cadastral`, `matriz_filial`, `natureza_juridica`, `cnae_principal`, `cnaes_secundarios`, `opcao_simples`, `opcao_mei`, `porte_empresa`, `uf`, `municipio`, `email` e `telefones`.

#### Ambiente Python

- A tentativa de usar `pandas` no ambiente atual falhou por incompatibilidade entre modulos compilados em `NumPy 1.x` e o `NumPy 2.4.3` presente no ambiente global.
- Como contorno imediato, o levantamento inicial foi feito com `openpyxl`, `csv` e biblioteca padrao.
- O plano passa a recomendar ambiente virtual dedicado para o projeto e dependencias fixadas antes da etapa de transformacao com `pandas`.

#### Ajuste visual exclusivo da versao 05

- Por orientacao expressa do usuario, a versao `04_painel_auditoria_fornecedores.html` foi preservada sem regeneracao.
- A manutencao passou a ocorrer somente na versao `05_painel_auditoria_fornecedores_endereco.html`.
- A coluna `Fornecedor` foi ampliada na tabela principal para reduzir truncamento de razao social e documento.
- As colunas menos criticas foram ligeiramente comprimidas para manter a soma das larguras em `100%` e evitar rolagem horizontal.
- Os pop-ups de ajuda dos filtros e das colunas tiveram prioridade visual elevada por `z-index`, e os containers da tabela passaram a permitir overflow visivel.
- O objetivo do ajuste foi permitir leitura completa dos helps sem que fiquem escondidos atras de cabecalhos, linhas da tabela ou dropdowns.
- A versao 05 foi regenerada com `15.719` fornecedores consolidados.

#### Correcao da tabela e dos helps da versao 05

- Foi identificado que a largura da coluna `Fornecedor` havia sido aplicada apenas ao cabecalho da tabela.
- Como o painel usa uma tabela separada para o corpo, os `td` das linhas resumidas continuavam sem classe de largura e eram distribuidos de forma quase igual.
- A correcao passou a aplicar as classes `col-*` tambem nas celulas do corpo da tabela.
- A proporcao final adotada para leitura humana foi:
  - `Fornecedor`: `36%`;
  - `Mudou / Incluiu`: `15%`;
  - `Fiscal`: `10%`;
  - `Credito`: `8%`;
  - `Movimento`: `15%`;
  - `Acao`: `9%`;
  - `Score`: `7%`.
- A decisao foi dar prioridade visual a nome do fornecedor, empresas, CNPJ/CPF, mudancas e movimento financeiro; credito, acao e score ficaram mais compactos por serem tags curtas.
- Os helps dos filtros tambem foram corrigidos no nivel do container do filtro, nao apenas no icone, para evitar que caixas de selecao e inputs vizinhos fiquem por cima do pop-up.
- A versao 05 foi regenerada novamente com `15.719` fornecedores, mantendo a versao 04 sem alteracao.

#### Explicacao e exibicao do score na versao 05

- O help da coluna `Score` foi ampliado para explicar a formula de completude cadastral.
- O score foi documentado como uma nota de `0` a `100`, calculada por pesos:
  - CNPJ valido: `20`;
  - razao social: `15`;
  - email: `15`;
  - inscricao estadual: `10`;
  - nome fantasia: `5`;
  - inscricao municipal: `5`;
  - telefone: `5`;
  - site: `5`;
  - situacao interna ativa: `5`;
  - data de cadastro: `5`;
  - grupo fiscal: `5`;
  - indicador de contribuinte ICMS: `5`.
- As faixas foram explicitadas: `Alta` de `85` a `100`, `Media` de `60` a `84` e `Baixa` abaixo de `60`.
- A exibicao da coluna `Score` passou a usar tag colorida: verde para `Alta`, amarelo para `Media` e vermelho para `Baixa`.
- O pop-up de help das ultimas colunas passou a abrir para a esquerda, evitando corte pela borda direita do navegador.
- A versao 05 foi regenerada com `15.719` fornecedores, sem alterar a versao 04.

#### Correcao de camadas visuais na versao 05

- A janela de metodologia passou a usar camada superior dedicada, com `z-index` acima de filtros, helps, tabela e cabecalho fixo.
- Os icones `?` dos helps deixaram de ficar permanentemente elevados acima dos demais componentes.
- Apenas o balao de texto do help e elevado durante o hover, evitando que o icone apareca por cima de listas de selecao abertas.
- Os labels dos filtros passaram a permitir overflow visivel para que os pop-ups de ajuda sejam exibidos sem recorte no proprio container do filtro.
- Os filtros de multipla escolha receberam seta visual no lado direito, centralizada verticalmente.
- A seta indica estado fechado com `baixo` e estado aberto com `cima`, reforcando que o campo abre uma caixa de selecoes.
- A versao 05 foi regenerada com `15.719` fornecedores, mantendo a versao 04 preservada.

#### Ajuste da linha resumida na versao 05

- Na coluna `Fiscal`, a tag de situacao oficial (`Ativa`/`Nao ativa`) foi retirada da linha resumida.
- A coluna `Fiscal` passou a destacar o regime fiscal em tag colorida (`Nao Simples`, `Simples`, `MEI`, `Indeterminado` ou `Sem dado`).
- A situacao oficial continua disponivel nos detalhes do fornecedor e nos filtros.
- Na coluna `Score`, foi retirada a segunda linha de prioridade (`critica`, `alta`, `media`, `baixa`) da linha resumida.
- A coluna `Score` passou a exibir somente a tag da nota e faixa de completude, como `80 | Media`.
- A versao 05 foi regenerada com `15.719` fornecedores, sem alterar a versao 04.

#### Ordenacao e separacao de movimento na versao 05

- A coluna resumida `Movimento` foi substituida por duas colunas:
  - `ABC`, contendo apenas a classificacao de curva (`AAA`, `AA`, `A`, `B`, `BB`, `C`, `CC`, `CCC` ou `Sem curva`);
  - `Valor`, contendo apenas o valor da curva em reais.
- A segunda linha de NFe foi retirada da linha resumida porque, nesta visualizacao, repetia o mesmo papel operacional do valor exibido.
- Foram adicionados controles de ordenacao nos cabecalhos `ABC`, `Valor`, `Fiscal`, `Credito` e `Score`.
- A ordenacao foi implementada sobre todos os registros filtrados antes da paginacao, e nao apenas sobre a pagina visivel.
- Para `Valor` e `Score`, o primeiro clique ordena do maior para o menor; o segundo clique inverte.
- Para `ABC`, `Fiscal` e `Credito`, a ordenacao segue hierarquias operacionais predefinidas e tambem pode ser invertida.
- Os helps com regras e itens passaram a usar formato indexado em multiplas linhas, especialmente `Score`, `Completude`, `Curva`, `Regime`, `Credito`, `ABC` e `Valor`.
- A versao 05 foi regenerada com `15.719` fornecedores, mantendo a versao 04 preservada.

#### Tags visuais nos helps da versao 05

- Os helps que exigem legenda de classificacao deixaram de depender apenas de texto simples no atributo `data-tip`.
- Foi criado um pop-up HTML rico dentro dos icones de help, permitindo exibicao de tags coloridas reais.
- Foram aplicadas tags visuais nos helps de:
  - `Curva`;
  - `Regime`;
  - `Credito`;
  - `Completude`;
  - coluna `Fiscal`;
  - coluna `Credito`;
  - coluna `ABC`;
  - coluna `Valor`;
  - coluna `Score`.
- As tags usam as mesmas familias visuais do painel: verde, amarelo, vermelho, azul, cinza e laranja.
- O restante do layout, filtros, colunas e ordenacao foi preservado.
- A versao 05 foi regenerada com `15.719` fornecedores, mantendo a versao 04 sem alteracao.

#### Ajustes finais de tags e sobreposicao na versao 05

- A camada dos pop-ups de help foi elevada novamente para ficar acima dos filtros e caixas de selecao abertas.
- O filtro ou cabecalho que estiver com help em hover tambem passa a subir de camada, evitando que outro filtro sobreponha o balao.
- O nome visivel `Completude` foi padronizado para `Score de Cadastro` no filtro, no cabecalho da tabela, na selecao de campos e no help.
- O help de `Acao` passou a mostrar tags reais para `Atualizar BD`, `Revisar antes`, `Validar fiscal`, `Sanear cadastro` e `Sem alteracao`.
- As tags dos boxes de detalhe `Fiscal e credito` e `Operacao e saneamento` foram alinhadas com as tags usadas na tabela principal.
- A versao 05 foi regenerada com `15.719` fornecedores, mantendo a versao 04 sem alteracao.

#### Ajuste de paginacao e tags nos detalhes da versao 05

- O box de `Paginacao` passou a mostrar pagina atual e total no formato visual `1/6`, `2/6` etc.
- O numero da pagina atual continua editavel no input, mas agora e acompanhado pelo total de paginas calculado apos filtros e ordenacao.
- Nos detalhes, as tags deixaram de aparecer como repeticao solta ao final dos boxes.
- No box `Fiscal e credito`, as tags passaram a ocupar o proprio valor dos campos `Regime`, `Credito` e `Validacao`.
- No box `Operacao e saneamento`, as tags passaram a ocupar o proprio valor dos campos `Curva`, `NFe` e `Saneamento`, mantendo os complementos operacionais como posicao, valor, linhas, UFs e anos.
- A versao 05 foi regenerada com `15.719` fornecedores, mantendo a versao 04 sem alteracao.

#### Refinamento dos detalhes e paginacao da versao 05

- O card `Paginacao` recebeu largura maior que os demais cards de KPI para evitar compressao dos botoes, input, total de paginas e seletor de tamanho.
- O box `Fiscal e credito` passou a exibir `Simples` e `MEI` como tags `Sim`, `Nao` ou `Indeterminado`.
- O box `Operacao e saneamento` foi renomeado para `Operacao`.
- A tag `Com movimento`/`Sem movimento` foi retirada do campo `NFe` no detalhe, por ser redundante naquele contexto.
- O campo `NFe` manteve apenas quantidade de linhas e valor em reais.
- A versao 05 foi regenerada com `15.719` fornecedores, mantendo a versao 04 sem alteracao.

#### Analise da nova curva ABC total

- Foi analisado o arquivo `data/CURVA_ABC_FORN_-_TOTAL.xlsx`.
- A nova curva possui `3.474` linhas, com colunas `CDFORNECED`, `RAZAO_SOCIAL`, `TOT_FORN`, `PERC`, `TOT_ACUM`, `CURVA` e `POS`.
- A distribuicao da curva e:
  - `AAA`: `29`;
  - `AA`: `25`;
  - `A`: `46`;
  - `B`: `77`;
  - `BB`: `186`;
  - `C`: `238`;
  - `CC`: `346`;
  - `CCC`: `2.527`.
- A curva possui `2.689` CNPJs validos distintos e `594` linhas cujo codigo nao vira CNPJ valido para OpenCNPJ.
- Por prefixo, a curva contem `2.879` codigos `J`, `583` codigos `F`, `9` codigos `O` e `3` codigos `I`.
- Em relacao ao cadastro mestre `data/FORNECEDORES - TODAS AS EMPRESAS.xlsx`, foram identificados:
  - `2.687` CNPJs da curva que tambem estao no cadastro;
  - `2` CNPJs validos da curva que nao estao no cadastro;
  - `13.031` CNPJs do cadastro que nao aparecem na nova curva.
- Por codigo, existem `596` linhas da curva que nao aparecem no cadastro mestre: `583` PF/CPF, `9` outros, `3` prefixo `I` e `1` prefixo `J`.
- O cache local da OpenCNPJ possui `2.646` CNPJs.
- A nova curva possui `43` CNPJs validos sem cache local OpenCNPJ.
- Dos CNPJs validos que estao na curva mas nao estao no cadastro, `2` ainda nao possuem cache local OpenCNPJ.
- Foi concluido que a versao atual do enriquecimento OpenCNPJ nao representa todos os fornecedores do cadastro nem todos os CNPJs validos da nova curva; ela representa a fila priorizada de `2.649` fornecedores usada na fase 3.

#### Comparacao entre curva antiga e curva nova

- Foi criada a pasta `output/fase_05_curva_total` para registrar a comparacao entre:
  - curva antiga: `data/CURVA_FORN_-_TODAS.csv`;
  - curva nova: `data/CURVA_ABC_FORN_-_TOTAL.xlsx`.
- A comparacao foi feita por `CDFORNECED` normalizado, pois esse e o identificador operacional comum entre as duas curvas.
- Foram gerados os arquivos:
  - `00_resumo_comparacao_curvas.json`;
  - `01_fornecedores_nova_curva_nao_antiga.csv`;
  - `02_fornecedores_antiga_curva_nao_nova.csv`;
  - `03_fornecedores_em_ambas_com_mudanca.csv`.
- Resultado por codigo de fornecedor:
  - curva antiga: `1.621` codigos;
  - curva nova: `3.282` codigos unicos;
  - em ambas: `1.621`;
  - na nova e nao na antiga: `1.661`;
  - na antiga e nao na nova: `0`;
  - em ambas com mudanca de posicao, valor ou classe: `1.621`.
- Os `1.661` fornecedores novos na curva nova se distribuem em:
  - `1.161` PJ/CNPJ;
  - `489` PF/CPF;
  - `9` Outros;
  - `2` Inscricao/Outro.
- Observacao metodologica: a planilha nova tem `3.474` linhas, mas `3.282` codigos unicos; para comparacao de fornecedores, foi usada a chave `CDFORNECED`.
- Foi confirmado que nenhum codigo da curva antiga ficou fora da curva nova.

#### Diagnostico da planilha de enderecos

- Foi analisado o arquivo `data/FORNECEDORES ENDEREÇOS - TODAS AS EMPRESAS.xlsx`.
- A planilha possui abas `IDEAL`, `MELHOR` e `POMME`, com campos de endereco, municipio, UF, CEP, telefones, contato e email.
- A planilha de enderecos possui `25.264` linhas e `25.135` combinacoes unicas `EMPRESA + CDFORNECED`.
- Foram identificados `75` casos duplicados por `EMPRESA + CDFORNECED` na planilha de enderecos.
- Comparacao com o cadastro principal:
  - cadastro principal: `25.554` linhas e `25.554` combinacoes unicas `EMPRESA + CDFORNECED`;
  - enderecos: `25.264` linhas;
  - cadastro sem endereco por `EMPRESA + CDFORNECED`: `431`;
  - endereco sem cadastro por `EMPRESA + CDFORNECED`: `12`;
  - divergencia de documento no mesmo `EMPRESA + CDFORNECED`: `0`;
  - divergencia de razao social no mesmo `EMPRESA + CDFORNECED`: `0`.
- Qualidade dos dados de endereco:
  - linhas com algum endereco: `25.264`;
  - linhas com algum contato: `18.043`;
  - linhas com endereco basico completo (`UF`, cidade, endereco/logradouro e CEP): `22.280`.
- Cruzamento com a nova curva:
  - codigos unicos da curva: `3.282`;
  - codigos da curva presentes no cadastro: `2.687`;
  - codigos da curva fora do cadastro: `595`;
  - codigos da curva com endereco: `2.680`;
  - codigos da curva sem endereco: `602`.
- Foi gerado o diagnostico em `output/fase_05_curva_total/04_diagnostico_enderecos_vs_cadastro_curva.json`.
- Foi observado que a nova curva possui codigos duplicados: `188` codigos aparecem mais de uma vez. Nesses casos, a versao consolidada por fornecedor devera agregar por `CDFORNECED` ou preservar as ocorrencias no detalhe.

#### Plano formal da versao 06

- Foi consolidado o plano da versao `06` em `docs/PLANO_VERSAO_06_CURVA_TOTAL.md`.
- A versao `06` sera baseada em uma copia da versao `05`, sem alterar as versoes `04` e `05`.
- O universo da versao `06` sera composto somente pelos fornecedores presentes em `data/CURVA_ABC_FORN_-_TOTAL.xlsx`.
- A versao `06` devera usar primeiro o cache local da OpenCNPJ e consultar na API apenas os CNPJs validos que ainda nao estejam cacheados.
- A versao `06` devera incorporar a planilha `data/FORNECEDORES ENDERECOS - TODAS AS EMPRESAS.xlsx` como fonte interna de endereco, municipio, UF, contato, email e telefones.
- A versao `06` devera comparar municipio e UF internos contra municipio e UF oficiais da OpenCNPJ, marcando `OK`, `Dado novo`, `Divergencia`, `Sem dado interno`, `Sem dado oficial` ou `Nao aplicavel`.
- A implementacao ainda nao foi iniciada nesta etapa; apenas o plano foi registrado.


#### Implementacao da versao 06 - Curva total

- Foi criado o script `scripts/build_supplier_audit_panel_v06.py`.
- A versao `06` parte logicamente da versao `05`, mas gera arquivos proprios e nao altera as versoes `04` e `05`.
- Foram gerados arquivos intermediarios numerados em `output/fase_06_curva_total`.
- O universo considerado foi a curva `data/CURVA_ABC_FORN_-_TOTAL.xlsx`, consolidada por `CDFORNECED`.
- Fornecedores consolidados na versao `06`: `3282`.
- Fornecedores cadastrados no cadastro mestre: `2687`.
- Fornecedores da curva fora do cadastro mestre: `595`.
- CNPJs validos tratados para OpenCNPJ: `2688`.
- A consulta OpenCNPJ usa cache local primeiro e consulta API somente quando o CNPJ valido nao esta cacheado.
- O script exibe uma barra de progresso no terminal durante a resolucao OpenCNPJ, com contadores de `cache`, `api`, `erro` e percentual concluido.
- Foi gerado o painel `output/fase_04_visualizacao/06_painel_auditoria_fornecedores_curva_total.html`.


#### Output 06b - Endereco preferencial do cadastro

- Foi criado o output visual `06b` a partir da base de auditoria do `06`.
- O layout geral do painel foi preservado.
- A regra do box de endereco passou a ser: cadastro atual como fonte principal; OpenCNPJ somente quando o campo correspondente esta vazio no cadastro atual.
- Campos complementados por OpenCNPJ aparecem destacados com tag azul `incluido OpenCNPJ`.
- Registros no `06b`: `3282`.
- Registros com pelo menos um campo de endereco/contato complementado por OpenCNPJ: `1675`.
- Arquivo HTML gerado: `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste do output 06b - Cadastro preferencial

- O box `Cadastro original` foi renomeado para `Cadastro`.
- O box `Dados incluidos` foi removido.
- Os dados antes exibidos em `Dados incluidos` passaram a complementar o box `Cadastro`.
- A regra aplicada e a mesma do endereco: cadastro atual como fonte principal; OpenCNPJ somente quando o campo interno esta vazio.
- Quando um campo cadastral e preenchido pela OpenCNPJ, o valor aparece acompanhado de tag azul `incluido OpenCNPJ`.
- O detalhe do fornecedor voltou a ter quatro boxes: `Cadastro`, `Endereco`, `Fiscal e credito` e `Operacao`.

#### Ajuste do output 06b - Tag unica OpenCNPJ

- A tag de campos complementados pela OpenCNPJ foi padronizada.
- Qualquer dado incluido pela OpenCNPJ agora aparece com uma unica tag azul com icone de check e texto `OpenCNPJ`.
- A regra vale para o box `Cadastro` e para o box `Endereco`.
- As tags especificas por campo, como `porte incluido OpenCNPJ`, `natureza incluida OpenCNPJ`, `telefone incluido OpenCNPJ` e similares, foram substituidas pela tag unica.
- O HTML atualizado foi gerado em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Correcao visual do output 06b - Check sem texto

- A tag azul de dado complementado pela OpenCNPJ foi ajustada para exibir somente o icone de check.
- A palavra `OpenCNPJ` foi removida da tag visual, mantendo a origem apenas no tooltip tecnico da tag.
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste do output 06b - Box de Score de Cadastro

- Foi incluido um quinto box de detalhe, `Score de Cadastro`, no lado direito da linha expandida.
- O box mostra o score final e a abertura dos componentes usados no calculo original:
  CNPJ valido, razao social, email, inscricao estadual, nome fantasia, inscricao municipal,
  telefone, site, situacao interna ativa, data de cadastro, grupo fiscal e indicador contribuinte ICMS.
- Cada componente aparece como pontuacao obtida sobre pontuacao possivel, por exemplo `15/15` ou `0/15`.
- Foi mantida a regra atual: o score exibido e o score cadastral original, calculado antes dos complementos de endereco e OpenCNPJ.
- Foi adicionada observacao no box informando que endereco e complementos OpenCNPJ ainda nao recalculam esta nota.

#### Correcao do output 06b - Check OpenCNPJ por campo de endereco

- O check azul de inclusao OpenCNPJ deixou de aparecer solto no final do box `Endereco`.
- O check agora aparece ao lado do campo especifico complementado pela OpenCNPJ, seguindo a mesma logica visual do box `Cadastro`.
- Foram criados marcadores por campo no output `06b`: `endereco_opencnpj_incluido`, `cidade_opencnpj_incluida`, `uf_opencnpj_incluida`, `telefone_opencnpj_incluido` e `email_opencnpj_incluido`.
- Contagem de campos complementados nesta geracao: endereco `137`, cidade `8`, UF `8`, telefone `1440`, email `1369`.
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste do output 06b - Filtro de Inclusoes

- O filtro visual antes chamado `Divergencia` foi renomeado para `Inclusoes`.
- A lista de multipla escolha passou a filtrar inclusoes especificas: `Razao social`, `Fantasia`, `Situacao`, `Email`, `Porte`, `Natureza juridica`, `Endereco`, `Cidade`, `UF`, `Telefone`, `Qualquer inclusao` e `Sem inclusao`.
- A logica do filtro foi alterada para usar campos efetivamente complementados ou dados oficiais incluidos no painel, e nao mais os campos de divergencia cadastral.
- Contagem de inclusoes nesta geracao: razao social `0`, fantasia `1`, situacao `1`, email `1369`, porte `2685`, natureza juridica `2685`, endereco `137`, cidade `8`, UF `8`, telefone `1440`.
- Registros com qualquer inclusao: `2685`; registros sem inclusao: `597`.
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste visual do output 06b - Checks, telefones e emails

- O check de inclusao OpenCNPJ passou a ser exibido como marcador circular azul pequeno ao lado do campo incluido.
- Os telefones exibidos no box `Endereco` passaram a ser formatados, quando possivel, no padrao brasileiro `(DD) 99999-9999` ou `(DD) 9999-9999`.
- Telefones multiplos continuam separados por ponto e virgula.
- Os emails exibidos no box `Endereco` passaram a ser convertidos para minusculas.
- Emails multiplos separados por ponto e virgula, barra vertical, virgula ou espaco sao exibidos em chips individuais para facilitar leitura.
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste visual do output 06b - Boxes e score agrupado

- O campo `Email` foi removido do box `Cadastro`, permanecendo apenas no box `Endereco`.
- O box `Score de Cadastro` deixou de listar os 12 componentes individuais e passou a exibir 4 grupos: `Identificacao`, `Contato`, `Fiscal cadastral` e `Governanca`.
- Cada grupo mostra a pontuacao obtida sobre a pontuacao possivel daquele bloco.
- A grade dos detalhes foi redistribuida para dar mais largura aos boxes `Cadastro` e `Endereco` e menos largura aos boxes `Fiscal e credito`, `Operacao` e `Score de Cadastro`.
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste visual do output 06b - Score em 3 grupos e check no email

- O check azul ao lado de email incluido foi ajustado para permanecer na mesma linha dos chips de email quando houver espaco horizontal.
- O box `Score de Cadastro` passou a exibir 3 grupos:
  - `Cadastro`: CNPJ valido, razao social, nome fantasia, situacao interna ativa e data de cadastro.
  - `Endereco`: email, telefone e site.
  - `Fiscal`: inscricao estadual, inscricao municipal, grupo fiscal e indicador contribuinte ICMS.
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste textual do output 06b - Nota do score

- A frase longa do box `Score de Cadastro` foi removida.
- A nota passou a ser: `Score = soma dos grupos Cadastro, Endereco e Fiscal.`
- O HTML atualizado foi gerado novamente em `output/04_visualizacao/06b_painel_auditoria_fornecedores_curva_total_endereco_preferencial.html`.

#### Ajuste do output 06b - Filtro de divergencias

- O filtro `Divergencia` passou a listar os tipos de divergencia possiveis na base `06b`.
- Opcoes exibidas: `Razao social`, `Nome fantasia`, `Email`, `Municipio`, `UF`, `Qualquer divergencia` e `Sem divergencia`.
- A funcao do filtro foi ajustada para consultar os flags cadastrais e o campo `divergencias_v06`.
- Contagens desta geracao: razao social `1336`, nome fantasia `955`, email `509`, municipio `206`, UF `31`, qualquer divergencia `1948`, sem divergencia `1334`.
- O help do filtro tambem foi atualizado para explicar cada opcao.


#### Implementacao da versao 07 - Cadastro total OpenCNPJ

- Foi criado o script `scripts/build_supplier_audit_panel_v07.py`.
- A versao `07` usa o universo completo da base reconciliada da versao `05`, com `15719` fornecedores consolidados.
- A versao `07` inclui fornecedores com curva e sem curva.
- Todos os CNPJs validos sao resolvidos via OpenCNPJ, usando cache local primeiro e API apenas para faltantes.
- O script exibe barra de progresso linear no terminal durante a resolucao OpenCNPJ, com contadores de cache, API e erro.
- CNPJs validos tratados para OpenCNPJ: `15718`.
- Fornecedores com curva: `1527`; fornecedores sem curva: `14192`.
- Fornecedores com movimento: `2686`; fornecedores sem movimento: `13033`.
- Fornecedores com endereco completo: `13691`; incompleto: `1732`; sem endereco: `296`.
- Status OpenCNPJ da execucao: `15709` CNPJs resolvidos por cache local, `9` retornos `http_404` e `1` registro nao aplicavel.
- Nesta execucao especifica nao houve chamada nova de API (`api=0`) porque o cache local ja continha os retornos uteis para os CNPJs validos; a barra de progresso foi exibida mesmo assim, percorrendo todos os CNPJs.
- Endereco preferencial no CSV final: `8087` registros usando `Cadastro atual` e `7632` usando `OpenCNPJ complementar` somente onde o cadastro interno estava vazio.
- Inclusoes de complemento identificadas no CSV final: email `6412`, telefone `5173`, endereco `1100`, cidade `294` e UF `294`.
- O layout HTML segue o padrao visual final construido na versao `06b`.
- Arquivo HTML gerado: `output/04_visualizacao/07_painel_auditoria_fornecedores_total_opencnpj.html`.

#### Correcao do output 07 - Conversao de valores da curva e NFe

- Foi identificado erro de escala nos valores exibidos no painel `07`.
- Causa: o script `07` reutilizava a funcao `v06.as_float`, criada para numeros vindos de planilha em formato brasileiro. Essa funcao remove pontos antes de converter, mas a base reconciliada `05` ja traz valores com ponto decimal. Exemplo: `454654.88867` era convertido indevidamente para `45465488867`.
- Foi criada no `scripts/build_supplier_audit_panel_v07.py` a funcao `as_reconciled_float`, especifica para a base reconciliada, preservando decimais com ponto e tratando tambem numeros com virgula quando necessario.
- Campos corrigidos: `curva_total_fornecedor`, `nfe_valor_total`, `curva_percentual`, `sort_curva_valor`, `sort_nfe_valor`, `curva_valor_fmt`, `nfe_valor_fmt` e `curva_pct_fmt`.
- O output `07` foi regenerado.
- Validacoes pontuais apos a correcao: `ANDRE SABAINI ZANETTI HORTIFRUTIGRANJEIROS - ME` passou a exibir `R$ 454.655`; `QUALYLIMP LTDA` passou a exibir `R$ 440.750`; `OTMA SOLUCAO EM ALIMENTACAO LTDA` passou a exibir `R$ 16.678.386`.

#### Ajuste visual do output 07 - Copia rapida de CNPJ/CPF

- Foi adicionado um botao pequeno de copiar ao lado do CNPJ/CPF na linha principal da tabela e no box `Cadastro` do detalhe.
- O botao copia somente os digitos do documento, sem pontos, barras ou hifens.
- O clique no botao nao abre nem fecha a linha de detalhe, pois o evento foi isolado do clique da linha.
- O HTML `output/04_visualizacao/07_painel_auditoria_fornecedores_total_opencnpj.html` foi regenerado e validado com `node --check`.

#### Ajuste visual do output 07 - Box Operacao

- No box `Operacao`, a informacao de NFe foi separada em duas linhas para melhorar leitura:
  - `Total`: valor total de NFe formatado em reais.
  - `NFe`: quantidade de notas.
- O HTML `output/04_visualizacao/07_painel_auditoria_fornecedores_total_opencnpj.html` foi regenerado e validado com `node --check`.

#### Planejamento da versao 08 - Painel simplificado e foco em regime fiscal

- Foi criado o documento `docs/PLANO_VERSAO_08_SIMPLIFICADO.md`.
- A versao `08` foi planejada para reduzir a complexidade visual do painel `07`.
- O foco passa a ser:
  - inclusoes efetivas de cadastro e endereco;
  - regime fiscal pendente;
  - fila objetiva para enriquecimento fiscal complementar.
- Foram retirados do desenho conceitual os marcadores amplos que geraram confusao operacional, como `Revisar antes`, `Validar fiscal`, `Precisa sanear`, `Dado novo`, `Divergencia` e `Prioridade`.
- O plano separa `OpenCNPJ consultado` de `Inclusao efetiva`, evitando tratar qualquer payload OpenCNPJ como dado novo.
- Para regimes fiscais ainda indeterminados, foi definida uma estrategia em camadas:
  - reaproveitar o cache OpenCNPJ local;
  - consultar base local do Simples Nacional via biblioteca `simplesnacional`, quando aplicavel;
  - usar CNPJ.ws apenas como fallback pontual por causa do limite publico de consultas;
  - manter outras APIs gratuitas/freemium como alternativas documentadas, nao como dependencia principal.
- O plano tambem registra que descobrir se um fornecedor e `Simples`, `MEI` ou `Nao Simples` nao resolve sozinho a classificacao completa entre Lucro Real e Lucro Presumido.

#### Teste de fontes para resolver regime fiscal indeterminado

- Foi criado o documento `docs/TESTE_FONTES_REGIME_FISCAL_08.md`.
- Foi selecionada uma amostra de 10 fornecedores PJ/CNPJ classificados no `07` como `Regime = Indeterminado`, priorizando maiores valores de curva/movimento.
- Arquivos gerados:
  - `output/08_regime_fiscal/00_teste_fontes_regime_fiscal.csv`
  - `output/08_regime_fiscal/00_teste_fontes_regime_fiscal_raw.json`
- O OpenCNPJ local nao resolveu os casos testados, pois os campos `opcao_simples` e `opcao_mei` estavam vazios.
- BrasilAPI resolveu 9 de 10 casos da amostra, retornando `regime_tributario` por ano.
- Minha Receita resolveu 9 de 10 casos da amostra, com resultados iguais aos da BrasilAPI.
- ReceitaWS foi testada nos 3 primeiros casos; retornou `simples=false` e `simei=false`, mas nao trouxe `Lucro Real` ou `Lucro Presumido`.
- CNPJ.ws publica foi testada em 1 caso por causa do limite publico; nao retornou regime tributario completo.
- O Portal oficial do Simples Nacional redirecionou para formulario com hCaptcha, sendo adequado como fonte oficial de conferencia, mas nao como API livre para lote automatizado nesta fase.
- Conclusao preliminar: BrasilAPI ou Minha Receita sao as fontes gratuitas mais promissoras para resolver os indeterminados do `07`, porque trazem `Lucro Real` e `Lucro Presumido` por ano.

#### Complemento do teste fiscal - Simples, MEI e Nao Simples

- Foi gerado o arquivo `output/08_regime_fiscal/00_teste_flags_simples_mei_nao_simples.csv`.
- Foram testados casos conhecidos da base `07`: um fornecedor `Simples`, um `MEI`, um `Nao Simples`, um `Indeterminado` com regime tributario e um `Indeterminado` sem resposta fiscal.
- BrasilAPI e Minha Receita retornaram `opcao_pelo_simples=true` e `opcao_pelo_mei=false` para fornecedor Simples.
- BrasilAPI e Minha Receita retornaram `opcao_pelo_simples=true` e `opcao_pelo_mei=true` para fornecedor MEI.
- BrasilAPI e Minha Receita retornaram `opcao_pelo_simples=false` e `opcao_pelo_mei=false` para fornecedor Nao Simples conhecido.
- Para fornecedor antes indeterminado, quando as flags Simples/MEI vieram nulas mas havia `regime_tributario = LUCRO PRESUMIDO`, foi definida a classificacao proposta `Nao Simples`, com origem `inferido por regime tributario`.
- A regra do `08` foi ajustada para preservar o objetivo fiscal original: separar claramente `MEI`, `Simples`, `Nao Simples` e `Indeterminado`.

#### Teste ampliado - 50 maiores indeterminados por valor

- Foi gerado o arquivo `output/08_regime_fiscal/01_teste_lote_50_indeterminados_minhareceita.csv`.
- Foram consultados na Minha Receita os 50 fornecedores de maior valor que estavam como `Regime = Indeterminado` no `07`.
- Resultado da amostra:
  - `34` classificados como `Nao Simples`.
  - `16` permaneceram `Indeterminado`.
- Todos os `34` resolvidos foram classificados pelo criterio `inferido_regime_tributario`, com retorno de regimes anuais como `LUCRO REAL`, `LUCRO PRESUMIDO` ou `IMUNE DE IRPJ`.
- Conclusao: a nova fonte tem vantagem concreta sobre o OpenCNPJ para reduzir indeterminados, especialmente entre fornecedores relevantes por valor, mas a interface deve distinguir `Nao Simples por flag direta` de `Nao Simples inferido por regime tributario`.

#### Organograma da logica fiscal do output 08

- Foi criado o documento `docs/ORGANOGRAMA_LOGICA_REGIME_FISCAL_08.md`.
- O documento formaliza a arvore de decisao para classificar fornecedores em `MEI`, `Simples`, `Nao Simples` ou `Indeterminado`.
- A logica prioriza flags diretas de MEI/Simples e usa `regime_tributario` anual apenas como inferencia rastreavel para `Nao Simples`.
- O documento tambem define que o painel `08` deve exibir `Regime`, `Origem`, `Evidencia` e `Ano`, para evitar confundir classificacao direta com classificacao inferida.

#### Matriz de credito 2027 por regime fiscal

- Foi criado o documento `docs/MATRIZ_CREDITOS_2027_REGIME_FISCAL.md`.
- A matriz traduz os regimes fiscais em potencial operacional de credito de IBS/CBS para o painel `08`.
- Foram definidos tratamentos preliminares:
  - `Nao Simples`, `Lucro Real` e `Lucro Presumido`: alto potencial, desde que a operacao seja tributada e haja pagamento de IBS/CBS.
  - `Simples Nacional`: potencial condicionado, pois o credito do comprador depende de o IBS/CBS estar no Simples ou no regime regular.
  - `MEI/SIMEI`: baixo ou limitado, salvo regra especifica aplicavel.
  - `PF/CPF`: baixo em regra, mas com possivel credito presumido em casos especificos, como produtor rural nao contribuinte.
  - `Imune/Isenta`: nao deve ser classificado automaticamente como alto; precisa validacao fiscal da operacao.
  - `Indeterminado`: pendente de enriquecimento fiscal.
- O documento registra que a diferenca entre `Lucro Real` e `Lucro Presumido` nao e, por si so, o principal fator para credito IBS/CBS do comprador; o fator principal e se a operacao esta no regime regular e se houve pagamento dos novos tributos.

#### Consolidacao do plano operacional do output 08

- O documento `docs/PLANO_VERSAO_08_SIMPLIFICADO.md` foi atualizado com o plano operacional completo do `08`.
- O plano foi organizado em quatro blocos:
  - busca e enriquecimento de dados;
  - filtros;
  - funcionalidades;
  - UI.
- A busca de dados do `08` parte do CSV consolidado do `07` e consulta fonte complementar apenas para fornecedores PJ/CNPJ ainda indeterminados.
- O plano define cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- A interface do `08` foi definida como uma versao simplificada do `07`, removendo marcadores confusos e mantendo foco em inclusoes, regime fiscal, origem da evidencia, potencial de credito 2027, curva e valor.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples inferido': 2822, 'Nao Simples': 5181, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


### 2026-05-22 15:53:37 - Pesquisa ampliada para regimes indeterminados no 08

#### Objetivo

- Investigar solucoes praticas para os `3.402` fornecedores que continuam com `Regime = Indeterminado` no output `08`.
- Separar o problema em filas acionaveis, em vez de tratar todos os pendentes como um unico bloco.

#### Analise local realizada

- Base analisada: `output/08_regime_fiscal/04_fornecedores_08_auditoria_simplificada.csv`.
- Pendentes totais: `3.402`.
- Quebra encontrada:
  - `1.622` nao ativos ou nao consultados.
  - `1.428` ativos sem movimento.
  - `55` com movimento, mas com natureza de orgao publico, fundo, cartorio, condominio ou caso especial.
  - `255` ativos com movimento e filial de empresa privada.
  - `42` ativos com movimento e matriz de empresa privada.

#### Pesquisa externa realizada

- Receita Federal - dados abertos de `regime_tributario`.
- Receita Federal - dados abertos CNPJ e `Simples.zip`.
- CNPJa API publica.
- Consulta CNPJ / Conecta gov.br / SERPRO.
- Campo `CRT` no XML da NF-e como evidencia operacional do regime do emitente.

#### Resultado

- Foi criado o documento `docs/PESQUISA_SOLUCOES_REGIME_INDETERMINADO_08.md`.
- A recomendacao principal e priorizar os `297` fornecedores privados ativos com movimento (`255` filiais + `42` matrizes).
- Para estes casos, a ordem tecnica proposta e: CNPJa/SERPRO para Simples/SIMEI, matriz/filial, XML da NF-e via `CRT`, e comprovante/documentacao do fornecedor quando necessario.


### 2026-05-22 18:13:06 - Busca CNPJa publica na fila prioritaria de regimes indeterminados

#### Objetivo

- Executar uma nova busca fiscal nos fornecedores ainda `Indeterminado`, priorizando fornecedores ativos, com movimento e sem natureza especial evidente.
- Avaliar se a CNPJa publica vale como fonte complementar para uma futura versao `08b`.

#### Implementacao

- Foi criado o script `scripts/search_regime_indeterminados_cnpja.py`.
- O script seleciona a fila prioritaria a partir de `output/08_regime_fiscal/04_fornecedores_08_auditoria_simplificada.csv`.
- A consulta usa `https://open.cnpja.com/office/{cnpj}`.
- O script grava cache em `output/08_regime_fiscal/cache_cnpja_publica/`.
- O progresso foi registrado em `output/08_regime_fiscal/09_busca_cnpja_progress.log`.

#### Arquivos gerados

- `output/08_regime_fiscal/07_fila_resolucao_regime_indeterminado.csv`
- `output/08_regime_fiscal/08_resultado_busca_cnpja_fila_prioritaria.csv`
- `output/08_regime_fiscal/09_resumo_busca_cnpja_fila_prioritaria.json`

#### Resultado

- Fila prioritaria consultada: `276` CNPJs.
- Consultas HTTP `200`: `276`.
- Classificados como `Nao Simples`: `276`.
- Classificados como `Simples`: `0`.
- Classificados como `MEI`: `0`.
- Permaneceram `Indeterminado`: `0`.
- Criterio encontrado: `simples.optant=false e simei.optant=false`.

#### Conclusao

- A CNPJa publica resolveu `100%` da fila prioritaria consultada.
- O resultado justifica estudar uma versao `08b` usando CNPJa como fonte complementar para reduzir pendencias relevantes de regime fiscal.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples': 8003, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples': 8003, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples': 8003, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples': 8003, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples': 8003, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


#### Implementacao do output 08 - Regime fiscal simplificado

- Foi criado o script `scripts/build_supplier_panel_v08.py`.
- A versao `08` parte do CSV consolidado do `07`, sem alterar o `07`.
- A consulta fiscal complementar e executada somente para CNPJs PJ ainda sem classificacao pelo OpenCNPJ.
- Foi criado cache proprio em `output/08_regime_fiscal/cache_regime_fiscal/`.
- Registros gerados: `15719`.
- Distribuicao de regime `08`: `{'Nao Simples': 8003, 'Indeterminado': 3402, 'Simples': 3837, 'MEI': 477}`.
- Distribuicao de credito 2027: `{'Alto': 7853, 'Pendente': 3402, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477}`.
- Fornecedores com pelo menos uma inclusao de cadastro/endereco: `15709`.
- HTML gerado: `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`.


### 2026-05-22 18:25:08 - Output 08b com CNPJa publica

#### Objetivo

- Criar uma copia evolutiva do `08`, chamada `08b`, incorporando os fornecedores resolvidos pela busca CNPJa publica.
- Manter o `08` original intacto.

#### Resultado

- Registros totais: `15719`.
- Fornecedores atualizados por CNPJa: `276`.
- Distribuicao de regime no `08b`: `{'Nao Simples': 8279, 'Simples': 3837, 'MEI': 477, 'Indeterminado': 3126}`.
- Distribuicao de credito 2027 no `08b`: `{'Alto': 8129, 'Validar': 150, 'Condicionado': 3837, 'Baixo': 477, 'Pendente': 3126}`.

#### Arquivos gerados

- `output/08_regime_fiscal/10_resumo_versao_08b.json`
- `output/08_regime_fiscal/11_fornecedores_08b_auditoria_simplificada.csv`
- `output/08_regime_fiscal/12_regimes_resolvidos_cnpja_08b.csv`
- `output/08_regime_fiscal/13_regimes_ainda_indeterminados_08b.csv`
- `output/08_regime_fiscal/14_comparativo_08_para_08b.csv`
- `output/04_visualizacao/08b_painel_fornecedores_regime_fiscal.html`
