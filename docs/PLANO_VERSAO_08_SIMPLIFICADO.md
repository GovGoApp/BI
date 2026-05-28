# Plano da Versao 08 - Painel simplificado com foco em inclusoes e regime fiscal pendente

## Objetivo

Criar uma versao `08` mais simples que o `07`, retirando marcadores operacionais confusos e concentrando a leitura em dois temas:

1. Inclusoes reais feitas por enriquecimento, principalmente OpenCNPJ, em cadastro e endereco.
2. Regime fiscal pendente, especialmente fornecedores ainda classificados como `Indeterminado`.

A versao `08` nao deve repetir a logica de `Acao`, `Revisar antes`, `Validar fiscal`, `Precisa sanear` e outros marcadores que misturavam diagnostico, risco e fila operacional. Esses conceitos podem voltar depois, mas somente se forem redesenhados como filas separadas e claramente explicadas.

## Situacao atual herdada do 07

- Universo: `15719` fornecedores.
- Regime `Indeterminado`: `6229` registros.
- Regime `Nao Simples`: `5180` registros.
- Regime `Simples`: `3835` registros.
- Regime `MEI`: `475` registros.
- Registros com dado novo: `15717`.
- Registros sem dado novo: `2`.

O problema central identificado: a coluna `Acao` do `07` era uma decisao priorizada e conservadora, nao um indicador direto de inclusao. Por isso, muitos fornecedores com inclusoes OpenCNPJ nao apareciam como `Atualizar BD`, pois cairam antes em regras de divergencia, validacao fiscal ou saneamento.

## O que sai no 08

Remover ou esconder do painel principal:

- `Acao`.
- `Revisar antes`.
- `Validar fiscal`.
- `Precisa sanear`.
- `Dado novo` como filtro principal.
- `Divergencia` como filtro principal.
- `Prioridade`.
- Marcadores de risco operacional amplos que nao apontam uma tarefa especifica.

Esses campos poderao continuar no CSV tecnico se forem uteis para auditoria, mas nao devem comandar a interface do `08`.

## O que fica no 08

Manter como leitura principal:

- Fornecedor.
- Empresas do grupo.
- CNPJ/CPF com botao de copiar somente numeros.
- Regime fiscal.
- Status de regime fiscal:
  - `Resolvido OpenCNPJ`.
  - `Resolvido Simples Nacional`.
  - `Pendente`.
  - `Nao aplicavel PF`.
  - `Erro/nao encontrado`.
- Credito fiscal inicial, mas somente como derivado do regime.
- Inclusoes de cadastro.
- Inclusoes de endereco.
- Movimento/curva/valor, para priorizacao economica.

## Filtros propostos

O `08` deve ter poucos filtros:

- Busca.
- Empresa.
- UF.
- Movimento NFe.
- Curva.
- Regime fiscal: `Nao Simples`, `Simples`, `MEI`, `Indeterminado`, `Nao aplicavel`.
- Status do regime: `Pendente`, `Resolvido OpenCNPJ`, `Resolvido Simples Nacional`, `Erro`.
- Inclusao: `Com inclusao`, `Sem inclusao`.
- Campo incluido: `Razao`, `Fantasia`, `Situacao`, `Porte`, `Natureza`, `Endereco`, `Cidade`, `UF`, `Telefone`, `Email`.

Nao incluir filtros de acao operacional nesta versao.

## Layout proposto

Tabela principal:

- `Fornecedor`: nome, tags de empresa, CNPJ/CPF com copia.
- `Regime`: tag do regime e origem da informacao.
- `Pendencia fiscal`: mostra se ainda precisa descobrir Simples/MEI.
- `Inclusoes`: resumo curto das inclusoes por grupo.
- `ABC`.
- `Valor`.

Detalhe expandido:

- Box `Cadastro`: dados finais preferenciais, mantendo check azul ao lado dos campos preenchidos por fonte externa.
- Box `Endereco`: dados finais preferenciais, mantendo check azul ao lado dos campos preenchidos por fonte externa.
- Box `Fiscal`: regime, origem, Simples, MEI, datas de opcao/exclusao quando existirem, status da consulta e observacao.
- Box `Operacao`: curva, posicao, total de NFe, quantidade de notas, UFs e anos.

## Como descobrir regimes fiscais pendentes

### Fonte 1 - OpenCNPJ

Ja utilizada no projeto.

Uso no `08`:

- Continuar usando `opcao_simples` e `opcao_mei` do cache OpenCNPJ.
- Se `opcao_mei = S`, classificar como `MEI`.
- Se `opcao_simples = S`, classificar como `Simples`.
- Se `opcao_simples = N`, classificar como `Nao Simples`.
- Se campos ausentes, nulos ou inconsistentes, marcar como pendente para segunda fonte.

Referencia: https://opencnpj.org/

### Teste real de fontes em fornecedores indeterminados

Antes da escolha definitiva da fonte do `08`, foi feito um teste com 10 fornecedores reais classificados no `07` como `Regime = Indeterminado`, priorizando os maiores valores de curva/movimento.

Resultado resumido:

- OpenCNPJ local: nao resolveu os casos testados, pois `opcao_simples` e `opcao_mei` estavam vazios.
- BrasilAPI: resolveu 9 de 10 casos, trazendo `regime_tributario` por ano.
- Minha Receita: resolveu 9 de 10 casos, com os mesmos resultados da BrasilAPI.
- ReceitaWS: testado nos 3 primeiros casos; confirmou `simples=false` e `simei=false`, mas nao trouxe Lucro Real ou Lucro Presumido.
- CNPJ.ws publica: testado em 1 caso por limite publico; nao trouxe regime tributario completo.
- Portal oficial do Simples Nacional: redirecionou para formulario com hCaptcha, util para conferencia oficial, mas nao para lote automatizado nesta fase.

Arquivos do teste:

- `docs/TESTE_FONTES_REGIME_FISCAL_08.md`
- `output/08_regime_fiscal/00_teste_fontes_regime_fiscal.csv`
- `output/08_regime_fiscal/00_teste_fontes_regime_fiscal_raw.json`

Conclusao preliminar do teste: para resolver os `Indeterminados` do `07`, BrasilAPI ou Minha Receita sao as fontes gratuitas mais promissoras, porque trouxeram `Lucro Real` e `Lucro Presumido` por ano, e nao apenas o status Simples/MEI.

Complemento importante para o objetivo fiscal de 2027: BrasilAPI e Minha Receita tambem retornam explicitamente `opcao_pelo_simples` e `opcao_pelo_mei` quando a informacao existe no arquivo `Simples.zip`.

Regra de classificacao fiscal proposta para o `08`:

1. `opcao_pelo_mei = true`: `MEI`.
2. `opcao_pelo_simples = true` e `opcao_pelo_mei != true`: `Simples`.
3. `opcao_pelo_simples = false`: `Nao Simples`.
4. flags Simples/MEI nulos, mas com `regime_tributario`: `Nao Simples`, inferido pelo ultimo regime tributario conhecido.
5. sem flags e sem `regime_tributario`: `Indeterminado`.

Essa regra preserva a leitura fiscal necessaria para a Reforma Tributaria: fornecedores `Nao Simples` tendem a ser analisados como maior potencial de credito, enquanto `Simples` e `MEI` precisam de tratamento especifico.

### Fonte 2 - Base local do Simples Nacional via biblioteca `simplesnacional`

Esta e a melhor candidata gratuita para volume alto.

Motivo:

- A biblioteca baixa e atualiza uma base local publica do Simples Nacional.
- Permite consultar CNPJ via CLI, biblioteca Python ou servidor local.
- Retorna `opcao_simples`, `data_opcao_simples`, `data_exclusao_simples`, `opcao_mei`, `data_opcao_mei` e `data_exclusao_mei`.
- Evita chamar milhares de vezes uma API publica limitada.

Plano de uso:

1. Criar script `scripts/enrich_regime_simples_v08.py`.
2. Rodar uma etapa de preparacao da base local:
   - `simplesnacional atualizar`
3. Consultar apenas os CNPJs ainda `Indeterminado`.
4. Gravar cache proprio em `output/08_regime_fiscal/cache_simples_nacional/`.
5. Reclassificar regime e origem:
   - `Resolvido Simples Nacional`.
   - `Pendente nao encontrado`.
   - `Erro consulta`.

Referencia: https://pypi.org/project/simplesnacional/

### Fonte 3 - Portal oficial do Simples Nacional

Fonte oficial de consulta de optantes pelo Simples Nacional e SIMEI.

Uso no projeto:

- Deve ser tratado como fonte oficial de conferencia.
- Pode ser usado para amostragem, validacao manual ou eventual automacao cuidadosa se tecnicamente permitido.
- Nao deve ser assumido como API livre de alto volume sem validar termos, limites e eventuais mecanismos anti-robo.

Referencia: https://www8.receita.fazenda.gov.br/Simplesnacional/

### Fonte 4 - CNPJ.ws publica

API publica gratuita com campo `simples`, mas limitada.

Pontos importantes:

- Endpoint publico: `https://publica.cnpj.ws/cnpj/{cnpj}`.
- Documentacao informa limite de `3 consultas por minuto` por IP.
- Retorno possui objeto `simples` com dados de Simples e MEI quando disponivel.
- Para `6229` pendentes, seria lenta demais como fonte principal.

Uso recomendado:

- Fallback pontual.
- Auditoria/amostragem.
- Nao usar como fonte principal de lote grande.

Referencias:

- https://docs.cnpj.ws/referencia-de-api/api-publica/consultando-cnpj
- https://docs.cnpj.ws/referencia-de-api/api-publica/limitacoes

### Fontes complementares com API/token/plano gratuito limitado

Podem ser avaliadas, mas nao devem ser primeira escolha para o projeto porque podem exigir cadastro, token, credito ou ter limite comercial:

- CNPJota: informa Simples/MEI com datas, mas cadastro inicial gratuito traz poucos creditos.
  - https://www.cnpjota.com.br/
- NextAPI: informa plano gratuito e Bearer Token, mas exige cadastro e limites.
  - https://www.nextapi.com.br/
- CNPJ API: informa token gratuito e endpoint com Simples Nacional.
  - https://docs.cnpj-api.com/
- Infosimples: tem API especifica Receita Federal/Simples Nacional, mas aparenta ser servico comercial/RPA.
  - https://infosimples.com/consultas/receita-federal-simples/

## Recomendacao tecnica

Para o `08`, seguir esta hierarquia:

1. Usar OpenCNPJ cacheado.
2. Para `Indeterminado`, usar base local `simplesnacional`.
3. Para o que continuar pendente, gerar fila `regime_fiscal_pendente.csv`.
4. Usar CNPJ.ws apenas para amostra/fallback pequeno, respeitando limite de 3 consultas por minuto.
5. Manter Portal do Simples Nacional como fonte oficial de conferencia, nao como dependencia automatica de alto volume nesta fase.

## Outputs previstos

Criar pasta:

- `output/08_regime_fiscal/`

Arquivos:

- `00_resumo_versao_08.json`
- `01_fornecedores_08_base.csv`
- `02_regimes_pendentes_para_consulta.csv`
- `03_regimes_resolvidos_simples_nacional.csv`
- `04_fornecedores_08_auditoria_simplificada.csv`
- `05_inclusoes_cadastro_endereco_previa_bd.csv`

HTML:

- `output/04_visualizacao/08_painel_fornecedores_regime_fiscal.html`

Scripts:

- `scripts/enrich_regime_simples_v08.py`
- `scripts/build_supplier_panel_v08.py`

## Plano operacional do 08

### 1. Busca e enriquecimento de dados

O `08` deve partir do output consolidado do `07`, porque ele ja contem:

- cadastro consolidado;
- enderecos preferenciais;
- inclusoes OpenCNPJ ja marcadas campo a campo;
- movimento NFe;
- curva ABC;
- cache OpenCNPJ.

Etapas:

1. Ler `output/07_cadastro_total_opencnpj/04_fornecedores_total_auditoria.csv`.
2. Reaproveitar todos os dados de cadastro e endereco ja enriquecidos pelo OpenCNPJ.
3. Separar fornecedores PJ/CNPJ com regime fiscal ainda `Indeterminado`.
4. Consultar fonte complementar, preferencialmente Minha Receita ou BrasilAPI, somente para CNPJs ainda indeterminados.
5. Gravar cache proprio do `08` para essa nova fonte em `output/08_regime_fiscal/cache_regime_fiscal/`.
6. Para cada fornecedor consultado, capturar:
   - `opcao_pelo_simples`;
   - `opcao_pelo_mei`;
   - `data_opcao_pelo_simples`;
   - `data_exclusao_do_simples`;
   - `data_opcao_pelo_mei`;
   - `data_exclusao_do_mei`;
   - `regime_tributario` anual;
   - ano mais recente do regime tributario;
   - fonte da informacao;
   - status da consulta.
7. Classificar o regime usando a arvore de decisao documentada em `docs/ORGANOGRAMA_LOGICA_REGIME_FISCAL_08.md`.
8. Gerar uma coluna de potencial de credito 2027 com base em `docs/MATRIZ_CREDITOS_2027_REGIME_FISCAL.md`.
9. Manter `Indeterminado` apenas quando nao houver flag Simples/MEI nem regime tributario anual.

Regra de classificacao:

1. `opcao_pelo_mei = true`: `MEI`.
2. `opcao_pelo_simples = true`: `Simples`.
3. `opcao_pelo_simples = false`: `Nao Simples`.
4. flags nulas, mas `regime_tributario` anual existente: `Nao Simples inferido`.
5. sem evidencias: `Indeterminado`.

### 2. Filtros

O `08` deve ter poucos filtros, todos diretamente ligados a decisao operacional.

Filtros principais:

- `Busca`: fornecedor, CNPJ/CPF, email ou cidade.
- `Empresa`: IDEAL, MELHOR, POMME.
- `UF`: UF do endereco preferencial.
- `Movimento`: com movimento, sem movimento.
- `Curva`: AAA, AA, A, B, BB, C, CC, CCC, sem curva.
- `Regime fiscal`: Nao Simples, Nao Simples inferido, Simples, MEI, Indeterminado, Nao aplicavel.
- `Credito 2027`: Alto, Condicionado, Baixo, Presumido, Validar, Pendente.
- `Origem fiscal`: OpenCNPJ, Minha Receita, BrasilAPI, Inferido por regime tributario, Sem evidencia.
- `Inclusoes`: com inclusao, sem inclusao.
- `Campo incluido`: cadastro, endereco, telefone, email, cidade, UF, porte, natureza.

Filtros que nao devem voltar no `08`:

- `Acao`.
- `Revisar antes`.
- `Validar fiscal`.
- `Precisa sanear`.
- `Divergencia`.
- `Prioridade`.
- `Completude`.
- `Dado novo` como marcador amplo.

### 3. Funcionalidades

Funcionalidades obrigatorias:

- Barra de progresso linear durante consulta fiscal complementar, mostrando total, cache, API, erro e pendentes.
- Cache incremental para permitir retomar a consulta se parar no meio.
- Botao de copiar CNPJ/CPF somente com numeros.
- Ordenacao por valor, curva ABC, regime fiscal e potencial de credito.
- Expandir uma linha por vez, mantendo o comportamento do `07`.
- Exportar CSV tecnico completo do `08`.
- Exportar previa de atualizacao cadastral/endereco para BD, ainda sem gravar no BD.
- Exportar lista de fornecedores ainda indeterminados para investigacao fiscal.
- Manter rastreabilidade da origem de cada inclusao e de cada classificacao fiscal.

Funcionalidades para etapa posterior:

- Gerar arquivo final de retorno ao BD no layout exato da planilha original.
- Permitir selecionar quais inclusoes vao para o arquivo de atualizacao.
- Marcar fornecedor como revisado manualmente.
- Salvar comentarios de revisao.

### 4. UI

O `08` deve ser visualmente mais simples que o `07`.

Tabela principal:

- `Fornecedor`: nome, tags das empresas, CNPJ/CPF com botao copiar.
- `Regime fiscal`: tag do regime e origem curta.
- `Credito 2027`: tag de potencial.
- `Inclusoes`: resumo curto por grupo, por exemplo `Cadastro 2 | Endereco 3`.
- `ABC`: curva.
- `Valor`: valor total da curva/NFe.

Detalhe expandido:

- Box `Cadastro`: dados finais preferenciais; check azul somente ao lado do campo incluido.
- Box `Endereco`: dados finais preferenciais; check azul somente ao lado do campo incluido.
- Box `Fiscal`: regime, origem, evidencia, ano, Simples/MEI, datas de opcao/exclusao e potencial de credito.
- Box `Operacao`: curva, posicao, total comprado, quantidade de notas, UFs e anos.

Principios visuais:

- Nao usar marcadores operacionais confusos.
- Toda tag deve representar uma informacao acionavel.
- O usuario deve conseguir responder rapidamente:
  - Quem e o fornecedor?
  - O que foi incluido no cadastro/endereco?
  - Qual o regime fiscal?
  - Qual a origem da classificacao fiscal?
  - Qual o potencial de credito em 2027?
  - Quanto esse fornecedor representa em compras?

Tags previstas:

- Regime: `Nao Simples`, `Simples`, `MEI`, `Indeterminado`.
- Credito: `Alto`, `Condicionado`, `Baixo`, `Presumido`, `Validar`, `Pendente`.
- Origem: `OpenCNPJ`, `Minha Receita`, `BrasilAPI`, `Regime tributario`, `CNPJa publica`, `Sem evidencia`.

O titulo do HTML deve permanecer simplesmente:

`Painel de Fornecedores`

## Regra de inclusoes para futuro arquivo de BD

No `08`, ainda nao gerar arquivo definitivo para salvar no BD. Gerar apenas uma previa.

Cada inclusao deve ter:

- CNPJ/CPF.
- Codigo(s) interno(s).
- Empresa(s).
- Campo.
- Valor atual.
- Valor sugerido.
- Fonte da sugestao.
- Status: `sugerido`, `confirmado`, `ignorado` ou `pendente`.

O HTML deve manter os checks azuis ao lado dos campos incluidos, mas a exportacao para BD so deve ser feita depois de validarmos visualmente a regra de inclusao.

## Etapas de execucao

1. Criar inventario dos `6229` regimes indeterminados.
2. Testar biblioteca `simplesnacional` em poucos CNPJs.
3. Se funcionar, baixar/atualizar base local.
4. Enriquecer todos os CNPJs pendentes com barra de progresso.
5. Reclassificar regime e credito inicial.
6. Gerar CSV simplificado do `08`.
7. Gerar HTML simplificado.
8. Validar contagens:
   - quantos continuam pendentes;
   - quantos foram resolvidos;
   - quantos mudaram de `Indeterminado` para `Simples`, `MEI` ou `Nao Simples`;
   - quantas inclusoes de cadastro/endereco existem.
9. Documentar no Diario de Bordo.

## Observacao fiscal importante

Resolver `Simples`, `MEI` e `Nao Simples` nao identifica automaticamente se o fornecedor `Nao Simples` e Lucro Real ou Lucro Presumido. Para a analise de credito 2027, o `08` deve tratar `Nao Simples` como uma melhora em relacao ao desconhecido, mas nao como classificacao fiscal definitiva de apuracao.

## Complemento 08b - CNPJa publica

Depois da execucao inicial do `08`, restaram `3.402` fornecedores com `Regime = Indeterminado`.

Foi feita uma busca complementar com CNPJa publica para a fila prioritaria:

- fornecedores PJ/CNPJ;
- situacao ativa;
- com movimento NFe;
- ainda `Indeterminado`;
- excluindo casos especiais evidentes como orgaos publicos, fundos, cartorios e semelhantes.

Resultado da busca:

- Fila prioritaria consultada: `276` CNPJs.
- Resolvidos como `Nao Simples`: `276`.
- Criterio: `simples.optant=false` e `simei.optant=false`.
- Fonte: `CNPJa publica`.

A versao `08b` foi criada como copia evolutiva do `08`, sem alterar o `08` original.

Arquivos do `08b`:

- `output/08_regime_fiscal/10_resumo_versao_08b.json`
- `output/08_regime_fiscal/11_fornecedores_08b_auditoria_simplificada.csv`
- `output/08_regime_fiscal/12_regimes_resolvidos_cnpja_08b.csv`
- `output/08_regime_fiscal/13_regimes_ainda_indeterminados_08b.csv`
- `output/08_regime_fiscal/14_comparativo_08_para_08b.csv`
- `output/04_visualizacao/08b_painel_fornecedores_regime_fiscal.html`

Resultado consolidado do `08b`:

- Registros totais: `15.719`.
- Fornecedores atualizados por CNPJa: `276`.
- `Nao Simples`: `8.279`.
- `Simples`: `3.837`.
- `MEI`: `477`.
- `Indeterminado`: `3.126`.
