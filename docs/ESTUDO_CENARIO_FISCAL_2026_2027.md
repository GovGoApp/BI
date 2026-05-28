# Estudo Inicial do Cenario Fiscal 2026-2027

Data da pesquisa: `2026-05-20`

## 1. Escopo deste estudo

Este documento resume apenas o que e mais relevante para o projeto de analise de fornecedores.

Ele nao substitui validacao com contador, tributarista ou area fiscal da empresa.

## 2. O que ja e realidade em 2026

### 2.1 2026 e ano de teste da Reforma Tributaria do Consumo

Fontes oficiais consultadas confirmam que:

- `2026` e o ano inicial de testes de `CBS` e `IBS`;
- os principais documentos fiscais eletronicos passam a destacar `CBS` e `IBS`;
- o foco de `2026` e adaptacao de sistemas, documentos e rotinas;
- cumpridas as obrigacoes acessorias, ha dispensa de recolhimento no periodo de testes.

Sintese pratica para o projeto:

- ja devemos olhar para os novos campos e regras dos documentos fiscais em `2026`;
- a base de fornecedores precisa ficar pronta antes de `2027`, quando o efeito economico do enquadramento passa a ser mais direto.

### 2.2 Documentos fiscais e classificacao tributaria passam a ganhar peso

Em `2026`, avancou a publicacao tecnica para preenchimento de documentos fiscais eletronicos com:

- `cClassTrib`;
- `CST` do `IBS/CBS`;
- classificacoes de credito presumido;
- regras de preenchimento e validacao dos campos.

Sintese pratica para o projeto:

- a analise futura do fornecedor nao podera depender apenas do CNPJ;
- sera necessario cruzar tambem o tratamento tributario da operacao e do item.

## 3. O que muda materialmente em 2027

### 3.1 Virada de `01/01/2027`

As fontes oficiais consultadas indicam que em `01/01/2027`:

- a `CBS` entra em vigor;
- `PIS` e `Cofins` sao extintos;
- o `IPI` vai a zero para quase todos os produtos, com excecoes ligadas a `ZFM`;
- o `Imposto Seletivo` passa a vigorar.

Sintese pratica para o projeto:

- a partir de 2027, o desenho economico das compras muda;
- comparar fornecedor apenas por preco historico fica ainda mais perigoso;
- o projeto precisa incorporar a logica de credito tributario no comparativo.

## 4. Regimes de fornecedor e impacto no credito do adquirente

### 4.1 Regra geral

No novo modelo, o direito ao credito do adquirente no regime regular depende de fatores combinados:

- enquadramento do fornecedor;
- tratamento tributario da operacao;
- classificacao do item;
- documento fiscal idoneo e corretamente preenchido;
- efetivo pagamento/apuracao segundo as regras aplicaveis.

### 4.2 Fornecedor no Simples Nacional

Ponto central para este projeto:

- o optante pelo `Simples Nacional` pode permanecer no regime unico; ou
- pode optar pela apuracao regular de `IBS/CBS` em situacoes previstas pela legislacao e regulamentacao.

Do material oficial pesquisado, ficam duas ideias-chave:

1. se o fornecedor do `Simples Nacional` nao optar pela apuracao regular de `IBS/CBS`, a logica de credito do adquirente nao sera a mesma de um fornecedor totalmente no regime regular;
2. ainda assim, a legislacao e os resumos tecnicos oficiais indicam possibilidade de apropriacao, pelo adquirente em regime regular, de creditos equivalentes aos valores de `IBS/CBS` pagos na aquisicao de bens e servicos de optante pelo `Simples Nacional`, em montante equivalente ao devido por meio desse regime.

Conclusao de projeto:

- nao basta marcar um fornecedor como `Simples = sim/nao`;
- sera necessario diferenciar, no minimo:
  - `regime regular`;
  - `Simples sem opcao regular IBS/CBS`;
  - `Simples com opcao regular IBS/CBS`, quando aplicavel;
  - `MEI`, quando aplicavel;
  - situacoes especiais, imunes, isentas ou com tratamento especifico.

### 4.3 Impacto direto na comparacao de fornecedores

Para compras futuras, dois fornecedores com o mesmo preco bruto podem ter custo liquido diferente para a empresa se:

- um gerar credito aproveitavel maior;
- outro estiver em condicao fiscal menos favoravel;
- a operacao do item tiver tratamento tributario diferente.

Por isso, o comparativo futuro deve ter pelo menos estas metricas:

- preco historico;
- regularidade cadastral;
- enquadramento/regime do fornecedor;
- potencial de credito estimado;
- custo liquido estimado apos credito;
- risco de documentacao fiscal inadequada.

## 5. Consequencias tecnicas para o projeto

### 5.1 Campos minimos a capturar por CNPJ

Com base na validacao feita na `OpenCNPJ`, os campos abaixo sao prioritarios:

- `razao_social`
- `nome_fantasia`
- `situacao_cadastral`
- `data_situacao_cadastral`
- `matriz_filial`
- `natureza_juridica`
- `cnae_principal`
- `cnaes_secundarios`
- `opcao_simples`
- `data_opcao_simples`
- `opcao_mei`
- `data_opcao_mei`
- `porte_empresa`
- `uf`
- `municipio`
- `email`
- `telefones`

### 5.2 Regras de classificacao sugeridas para a fase inicial

Na fase 1, o projeto pode classificar o fornecedor em tres eixos separados:

1. `cadastro_interno`
2. `cadastro_oficial_cnpj`
3. `potencial_credito_2027`

Exemplo de abordagem inicial para `potencial_credito_2027`:

- `alto_potencial`
- `potencial_condicionado`
- `baixo_ou_inexistente`
- `indeterminado`

Importante:

- essa classificacao nao deve ser fechada apenas por CNPJ;
- ela deve ser tratada como uma estimativa operacional, validada pela area fiscal.

## 6. Fontes oficiais utilizadas

### Receita Federal

- Orientacoes da Reforma Tributaria para 2026  
  https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/reforma-tributaria-do-consumo/orientacoes-2026

- Entenda a Reforma Tributaria do Consumo  
  https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/acoes-e-programas/programas-e-atividades/reforma-tributaria-do-consumo/entenda

- Receita Federal e Comitê Gestor do IBS definem regras relativas a obrigacoes acessorias da Reforma Tributaria para inicio de 2026  
  https://www.gov.br/receitafederal/pt-br/assuntos/noticias/2025/dezembro/receita-federal-e-comite-gestor-do-ibs-definem-regras-relativas-a-obrigacoes-acessorias-da-reforma-tributaria-para-inicio-de-2026

### Ministerio da Fazenda

- Comitê define prazos de opcao pelo Simples Nacional e pelo regime regular do IBS e da CBS para 2027  
  https://www.gov.br/fazenda/pt-br/assuntos/noticias/2026/abril/comite-define-prazos-de-opcao-pelo-simples-nacional-e-pelo-regime-regular-do-ibs-e-da-cbs-para-2027

- Regulamento detalha regras que apresentam sistema mais simples, transparente e previsivel a cidadaos e empresas  
  https://www.gov.br/fazenda/pt-br/assuntos/noticias/2026/abril/regulamento-detalha-as-regras-que-apresentam-sistema-mais-simples-transparente-e-previsivel-para-cidadaos-e-empresas

- Receita Federal lanca nova versao do Portal Nacional de Tributacao sobre o Consumo da Reforma Tributaria  
  https://www.gov.br/fazenda/pt-br/assuntos/noticias/2026/maio/receita-federal-lanca-nova-versao-do-portal-nacional-de-tributacao-sobre-o-consumo-da-reforma-tributaria

- Resumo tecnico oficial sobre `IBS` e `CBS` sobre operacoes  
  https://www.gov.br/fazenda/pt-br/acesso-a-informacao/acoes-e-programas/reforma-tributaria/regulamentacao-da-reforma-tributaria/lei-geral-do-ibs-da-cbs-e-do-imposto-seletivo/resumos-tecnicos/plp-68-2024_resumo-ibs-e-cbs-sobre-operacoes.pdf

### CGIBS

- Orientacoes sobre a entrada em vigor da CBS e do IBS em 1 de janeiro de 2026  
  https://cgibs.gov.br/comite-gestor-do-ibs-e-receita-federal-divulgam-orientacoes-sobre-a-entrada-em-vigor-da-cbs-e-do-ibs-em-1-de-janeiro-de-2026

### Legislacao

- Lei Complementar `214`, de `16/01/2025`  
  https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp214.htm

- Lei Complementar `227`, de `2026`, com ajustes relevantes para `Simples Nacional` x `IBS/CBS`  
  https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp227.htm

## 7. Conclusao objetiva

1. `2026` e o ano para preparar dados, documentos e sistemas.
2. `2027` e o ano em que a comparacao de fornecedores precisa incorporar credito tributario de forma estruturada.
3. O regime do fornecedor, especialmente no `Simples Nacional`, precisa virar atributo analitico de primeira classe no projeto.
4. O comparativo final nao pode ser apenas por fornecedor; ele precisa considerar fornecedor + operacao + item.
