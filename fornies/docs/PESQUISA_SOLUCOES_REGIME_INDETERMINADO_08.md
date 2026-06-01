# Pesquisa - Solucoes para Regime Fiscal Indeterminado no 08

Data: 2026-05-22

## Objetivo

Investigar solucoes mais amplas para os fornecedores que continuam como `Regime = Indeterminado` depois do `08`, preservando o objetivo original do projeto: estimar impacto de credito de IBS/CBS a partir de 2027.

## Diagnostico local dos pendentes

Base analisada: `output/08_regime_fiscal/04_fornecedores_08_auditoria_simplificada.csv`.

Total pendente: `3.402` CNPJs.

Quebra principal:

| Fila | Qtde | Valor de referencia | Leitura |
|---|---:|---:|---|
| Nao ativa ou nao consultada | 1.622 | R$ 954.823 | Baixa prioridade fiscal operacional; primeiro tratar cadastro/ativo-inativo. |
| Ativa sem movimento | 1.428 | R$ 0 | Nao impacta compra atual; pode ficar em fila fria. |
| Movimento, mas nao empresa operacional classica | 55 | R$ 61.153.277 | Orgaos publicos, fundos, cartorios, condominios etc.; precisam de classificacao fiscal propria, nao so "regime". |
| Movimento, filial de empresa privada | 255 | R$ 67.007.217 | Principal fila de trabalho. Possivel resolver por matriz, XML/NFe ou fonte oficial/comercial. |
| Movimento, matriz de empresa privada | 42 | R$ 4.315.237 | Fila prioritaria menor; testar API/portal/documento fiscal. |

Conclusao: nao faz sentido tratar os `3.402` como uma unica massa. A fila de maior impacto e bem menor: `297` fornecedores privados ativos com movimento (`255` filiais + `42` matrizes), alem dos `55` casos especiais de alto valor.

## Por que Minha Receita/BrasilAPI ainda deixam pendencias

A busca do `08` usou fontes que expõem `opcao_pelo_simples`, `opcao_pelo_mei` e, quando disponivel, `regime_tributario` vindo de ECF.

O problema: a base de `regime_tributario` da Receita existe, mas nao cobre tudo. Segundo a documentacao de modelos de dados do CNPJ.ws, os dados de regime tributario vem da ECF; optantes do Simples, orgaos publicos, autarquias, fundacoes publicas e PJs inativas podem nao aparecer nessa base. Isso explica parte grande dos vazios.

Na propria Receita Federal ha um diretorio oficial de dados abertos de `regime_tributario`, com arquivos de Lucro Real, Lucro Presumido, Lucro Arbitrado e Imunes/Isentas. Portanto, quando uma empresa nao aparece ali, nao quer dizer automaticamente que ela e Simples; pode ser que esteja fora do escopo da ECF, inativa, orgao publico, fundo, filial sem registro proprio, ou dado ainda nao publicado.

## Fontes e estrategias pesquisadas

### 1. Base aberta oficial da Receita - regime_tributario

Fonte: `https://arquivos.receitafederal.gov.br/dados/cnpj/regime_tributario/`

Uso proposto:

1. Baixar os arquivos oficiais `Lucro Real.zip`, `Lucro Presumido.zip`, `Lucro Arbitrado.zip` e `Imunes e Isentas.zip`.
2. Indexar localmente por CNPJ/ano.
3. Cruzar com os `Indeterminado`.
4. Guardar evidencia: ano, regime, forma de tributacao e arquivo de origem.

Vantagem: fonte oficial e reprodutivel.

Limite: provavelmente nao resolvera todos, porque Minha Receita/BrasilAPI ja parecem refletir essa mesma base em muitos casos.

### 2. Base aberta oficial da Receita - Simples.zip

Fonte: `https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/`

Uso proposto:

1. Baixar o `Simples.zip` do ultimo pacote mensal disponivel.
2. Indexar localmente os CNPJs optantes pelo Simples e SIMEI.
3. Cruzar com os pendentes para confirmar `Simples` ou `MEI`.

Vantagem: evita depender de API gratuita com limite.

Limite: em geral confirma quem e optante; para quem nao aparece, ainda precisamos tomar cuidado antes de concluir `Nao Simples`.

### 3. CNPJa API publica ou comercial

Fonte: `https://cnpja.com/api/open`

Teste local feito em CNPJs pendentes de maior valor mostrou retorno com `company.simples.optant=false` e `company.simei.optant=false` para alguns casos em que Minha Receita/OpenCNPJ estavam nulos.

Uso proposto:

1. Usar primeiro em amostra controlada dos `297` fornecedores privados ativos com movimento.
2. Se a taxa de resolucao for boa, decidir entre:
   - API publica: limite de 5 consultas/minuto; viavel para amostra, lento para lote grande.
   - API comercial: maior limite e certificados/consulta em tempo mais proximo da fonte.

Vantagem: pode transformar parte dos `Indeterminado` em `Nao Simples` com evidencia direta de `simples=false` e `simei=false`.

Limite: a API publica tem limite baixo e pode ter defasagem de ate 45 dias para estabelecimentos ativos. A API gratuita nao mostrou `Lucro Real/Presumido`, apenas Simples/SIMEI.

### 4. API oficial Consulta CNPJ / Conecta gov.br / SERPRO

Fonte: `https://www.gov.br/conecta/catalogo/apis/consulta-cnpj`

A API oficial Consulta CNPJ informa campos de `Opcao do SIMEI` e `Opcao Simples Nacional`. A documentacao tambem informa que ha endpoint de producao, controle OAuth e restricao por IP cadastrado.

Uso proposto:

1. Verificar se a empresa pode contratar/usar SERPRO Consulta CNPJ ou algum servico oficial equivalente.
2. Se sim, usar como fonte mais forte para `Simples`, `MEI` e `Nao Simples`.

Vantagem: fonte oficial, mais defensavel para decisao fiscal.

Limite: nao e uma API aberta simples; pode exigir contrato, credenciais, IP liberado e/ou contexto de orgao/entidade autorizada.

### 5. XML da NF-e: campo `emit/CRT`

Fonte tecnica: leiaute NF-e / NTs da NF-e. O campo `CRT` identifica o regime tributario do emitente na nota.

Mapeamento operacional:

| CRT | Interpretacao |
|---:|---|
| 1 | Simples Nacional |
| 2 | Simples Nacional com excesso de sublimite |
| 3 | Regime Normal |
| 4 | MEI |

Uso proposto:

1. Obter XMLs reais das notas de entrada, ou exportacao do ERP/fiscal, ou distribuicao DF-e com certificado da empresa destinataria.
2. Ler `NFe/infNFe/emit/CRT`.
3. Para cada fornecedor com movimento, usar o CRT mais recente como evidencia operacional.

Vantagem: para fornecedor com movimento, e provavelmente a evidencia mais pratica e mais ligada a compra real.

Limite: `data/NFE.csv` atual nao tem XML nem `CRT`; ele tem apenas dados gerenciais de compra, produto, ano, valor e curva. Precisamos dos XMLs/chaves para aplicar esta solucao.

### 6. Matriz/filial

Diagnostico local: `1.965` dos pendentes sao filiais; entre os ativos privados com movimento, `255` sao filiais.

Uso proposto:

1. Identificar CNPJ raiz.
2. Encontrar a matriz pelo arquivo de estabelecimentos da Receita, OpenCNPJ/CNPJa/SERPRO ou calculo do CNPJ `0001` quando aplicavel.
3. Consultar regime/Simples/MEI da matriz.
4. Aplicar na filial apenas como `evidencia por matriz`, nao como certeza cega.

Vantagem: resolve casos em que a fonte registra regime na matriz e a compra aparece em filial.

Limite: matriz e filial podem ter particularidades cadastrais/estaduais; deve aparecer no painel como evidencia, nao como verdade fiscal absoluta.

### 7. Portal oficial do Simples Nacional

Fonte: Portal Consulta Optantes.

Uso proposto:

1. Usar como conferencia manual ou semiautomatizada para os fornecedores mais relevantes.
2. Guardar comprovante/PDF/data da consulta.

Vantagem: fonte oficial para optante/não optante Simples e SIMEI.

Limite: tem hCaptcha/formulario; nao e uma API livre de lote.

### 8. Solicitacao direta ao fornecedor

Uso proposto:

Criar uma fila de solicitacao documental para os casos de maior impacto, pedindo:

- declaracao de regime tributario atual;
- comprovante de optante/nao optante Simples;
- se Simples, indicar se pretende optar pelo regime regular de IBS/CBS em 2027;
- XML de NF-e recente emitida para o grupo, quando aplicavel.

Vantagem: resolve lacuna onde dado publico/API falha.

Limite: precisa governanca interna, prazo e controle de resposta.

## Leitura de credito 2027

Para o objetivo do projeto, o ponto principal nao e apenas saber `Lucro Real` ou `Lucro Presumido`. O primeiro corte de credito e:

1. `Nao Simples`: tende a gerar credito regular no regime nao cumulativo de IBS/CBS, observadas regras da operacao/produto.
2. `Simples`: gera credito limitado ao valor de IBS/CBS devido no proprio Simples, salvo se optar pelo regime regular/hibrido.
3. `MEI`: tende a baixo ou nenhum impacto relevante de credito, exigindo validacao por caso.
4. `Indeterminado`: risco fiscal/comercial; nao deve ser tratado como credito alto ate obter evidencia.

## Recomendacao pratica

### Fila A - resolver com maior urgencia

Fornecedores privados ativos com movimento: `297`.

Ordem:

1. Testar CNPJa em lote controlado.
2. Cruzar matriz/filial.
3. Buscar XML/NFe `CRT` das notas mais recentes.
4. Se continuar pendente e valor alto, solicitar comprovante ao fornecedor.

### Fila B - tratar como caso especial

Orgaos publicos, fundos, cartorios, condominios e semelhantes: `55` com movimento.

Acao:

1. Criar categoria propria no painel: `Regime especial / nao aplicavel`.
2. Encaminhar para fiscal avaliar se ha documento fiscal com credito ou se e pagamento sem credito operacional.

### Fila C - baixa prioridade

Ativos sem movimento e inativos/nao consultados: `3.050`.

Acao:

1. Manter como pendente frio.
2. So pesquisar quando entrar em movimento, contrato ou cotacao.

## Proposta para evoluir o 08

1. Adicionar uma coluna/filtro `Fila fiscal`: `Privado com movimento`, `Especial`, `Sem movimento`, `Inativo`.
2. Trocar o problema de `3.402 pendentes` por uma fila operacional priorizada.
3. Criar novo arquivo de trabalho: `output/08_regime_fiscal/07_fila_resolucao_regime_indeterminado.csv`.
4. Testar CNPJa primeiro nos `297` privados com movimento.
5. Preparar ingestao futura de XMLs NF-e para ler `CRT`.
6. Preparar campo de evidencia: `Fonte`, `Data`, `CNPJ consultado`, `Matriz/Filial`, `Ano`, `CRT`, `Arquivo`.

## Busca executada - CNPJa publica na fila prioritaria

Data/hora: 2026-05-22.

Script criado:

- `scripts/search_regime_indeterminados_cnpja.py`

Arquivos gerados:

- `output/08_regime_fiscal/07_fila_resolucao_regime_indeterminado.csv`
- `output/08_regime_fiscal/08_resultado_busca_cnpja_fila_prioritaria.csv`
- `output/08_regime_fiscal/09_resumo_busca_cnpja_fila_prioritaria.json`
- `output/08_regime_fiscal/09_busca_cnpja_progress.log`
- `output/08_regime_fiscal/cache_cnpja_publica/`

Escopo da busca:

- Foram selecionados fornecedores com `Regime = Indeterminado`, `Situacao = Ativa`, `Movimento = Com movimento`, excluindo a maior parte dos casos especiais por natureza/nome.
- A fila prioritaria final ficou em `276` CNPJs.
- A consulta respeitou intervalo de aproximadamente `13s` entre chamadas, por causa do limite publico de `5 consultas/minuto` informado pela CNPJa.

Resultado:

| Resultado | Quantidade |
|---|---:|
| Consultados | 276 |
| HTTP 200 | 276 |
| Nao Simples | 276 |
| Simples | 0 |
| MEI | 0 |
| Indeterminado | 0 |

Criterio usado:

- `company.simples.optant = false` e `company.simei.optant = false`.

Interpretacao:

- A CNPJa publica resolveu `100%` da fila prioritaria consultada como `Nao Simples`.
- Isso nao traz `Lucro Real` ou `Lucro Presumido`, mas traz uma evidencia direta muito util para o objetivo do projeto: os fornecedores consultados nao sao optantes do Simples nem do SIMEI na leitura da CNPJa.
- Como a fila consultada era de fornecedores ativos com movimento e ainda pendentes, este resultado justifica considerar um `08b` usando a CNPJa como fonte complementar para reduzir os `Indeterminado` mais relevantes.

Ressalva:

- A evidencia deve ser gravada como `CNPJa publica`, com data da consulta e criterio `simples.optant=false e simei.optant=false`.
- Para decisoes fiscais finais, principalmente fornecedores de alto valor, ainda pode ser prudente manter uma trilha de conferencia por XML da NF-e (`CRT`) ou documentacao do fornecedor.

## Fontes pesquisadas

- Receita Federal - dados abertos de regime tributario: `https://arquivos.receitafederal.gov.br/dados/cnpj/regime_tributario/`
- Receita Federal - dados abertos CNPJ e `Simples.zip`: `https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/`
- CNPJa API publica: `https://cnpja.com/api/open`
- Consulta CNPJ no catalogo de APIs governamentais: `https://www.gov.br/conecta/catalogo/apis/consulta-cnpj`
- CNPJ.ws - modelo de dados de regimes tributarios: `https://docs.cnpj.ws/modelos-de-dados/regimes-tributarios`
- Portal NF-e / notas tecnicas e leiaute NF-e para campo `CRT`: `https://www.nfe.fazenda.gov.br/`
