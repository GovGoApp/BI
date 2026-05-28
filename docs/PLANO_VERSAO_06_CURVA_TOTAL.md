# Plano da Versao 06 - Fornecedores da Curva Total

Data-base: `2026-05-21`

## 1. Objetivo

Criar uma nova versao do output e do painel HTML, chamada `06`, contendo somente fornecedores presentes na nova curva:

`data/CURVA_ABC_FORN_-_TOTAL.xlsx`

Essa versao sera focada em fornecedores com movimentacao desde `2024`, conforme a curva total recebida.

A versao `06` deve partir de uma copia funcional da versao `05`, preservando o layout e os comportamentos aprovados, mas trocando o universo de fornecedores e incorporando a nova planilha interna de enderecos.

## 2. Principio de Escopo

A versao `06` nao e a visao de todos os fornecedores cadastrados.

Ela deve conter:

- todos os fornecedores da nova curva total;
- fornecedores da curva que tambem estao no cadastro mestre;
- fornecedores da curva que nao estao no cadastro mestre, marcados explicitamente como `Fora do cadastro`;
- fornecedores PJ/CNPJ enriquecidos com OpenCNPJ sempre que houver CNPJ valido;
- fornecedores PF/CPF, `O` e `I` sem consulta OpenCNPJ, pois OpenCNPJ e uma fonte de CNPJ.

A versao `07`, em momento posterior, sera a visao de todos os fornecedores do cadastro mestre.

## 3. Fontes de Dados

### 3.1 Curva total

Arquivo:

`data/CURVA_ABC_FORN_-_TOTAL.xlsx`

Campos observados:

- `CDFORNECED`;
- `RAZAO_SOCIAL`;
- `TOT_FORN`;
- `PERC`;
- `TOT_ACUM`;
- `CURVA`;
- `POS`.

Papel na versao `06`:

- define o universo principal da pagina;
- define valor de compra;
- define curva ABC;
- define posicao original da curva;
- define fornecedores com movimentacao.

### 3.2 Cadastro mestre

Arquivo:

`data/FORNECEDORES - TODAS AS EMPRESAS.xlsx`

Abas:

- `IDEAL`;
- `MELHOR`;
- `POMME`.

Papel na versao `06`:

- informar se o fornecedor da curva existe no cadastro interno;
- trazer razao social, fantasia, documento, IE, IM, emails internos, situacao interna e demais campos cadastrais;
- permitir tags de empresa;
- permitir comparacao com os enderecos internos.

### 3.3 Enderecos internos

Arquivo:

`data/FORNECEDORES ENDEREÇOS - TODAS AS EMPRESAS.xlsx`

Campos observados:

- `EMPRESA`;
- `CDFORNECED`;
- `NRINSJURFORN`;
- `NMRAZSOCFORN`;
- `NMFANTFORN`;
- `SGESTADO`;
- `CDMUNICIPIO`;
- `NMMUNICIPIO`;
- `CDMUNICIBGE`;
- `DSENDEFORN`;
- `NMBAIRFORN`;
- `NRCEPFORN`;
- `DSCOMPENDFOR`;
- `NRENDEFORNSEP`;
- `DSENDEFORNSEP`;
- `NRTELEFORN`;
- `NRRAMALFORN`;
- `NRTELEXFORN`;
- `NRFAXFORN`;
- `NMCONTFORN`;
- `DSEMAILFORN`;
- `NRTELEFORN1`;
- `NRRAMALFORN1`;
- `NRCELULARFOR`;
- `NRTELRESIFOR`.

Papel na versao `06`:

- trazer endereco interno;
- trazer cidade e UF internas;
- trazer contatos internos;
- trazer telefones internos;
- trazer email interno de endereco/contato;
- permitir comparacao com OpenCNPJ;
- identificar dados internos faltantes.

### 3.4 OpenCNPJ

Fonte:

`https://api.opencnpj.org/{cnpj}`

Cache local:

`output/fase_03_enriquecimento/99_cache_opencnpj`

Papel na versao `06`:

- reaproveitar todos os CNPJs ja cacheados;
- consultar apenas CNPJs validos da curva que ainda nao estejam no cache;
- trazer dados oficiais de razao social, fantasia, situacao cadastral, regime, Simples, MEI, municipio, UF, endereco, email e telefones;
- comparar dados oficiais com dados internos.

## 4. Chaves de Cruzamento

### 4.1 Chave operacional principal

`CDFORNECED`

Uso:

- cruzar curva com cadastro mestre;
- cruzar curva com enderecos;
- preservar a leitura operacional usada no ERP.

### 4.2 Chave de linha interna

`EMPRESA + CDFORNECED`

Uso:

- cruzar cadastro mestre com planilha de enderecos;
- evitar misturar enderecos de empresas diferentes quando o mesmo fornecedor aparece em mais de uma empresa;
- explicar divergencias de cobertura por empresa.

### 4.3 Chave fiscal/oficial

`CNPJ normalizado`

Uso:

- consultar OpenCNPJ;
- consolidar dados oficiais;
- comparar municipio/UF internos com municipio/UF oficial;
- identificar fornecedores PJ/CNPJ da curva que nao estao no cadastro.

### 4.4 Chaves nao consultaveis na OpenCNPJ

Prefixos:

- `F`: PF/CPF;
- `O`: outros;
- `I`: inscricao/outro.

Uso:

- entram no painel `06` porque estao na curva;
- nao recebem OpenCNPJ;
- devem ser marcados como `Nao aplicavel OpenCNPJ` ou equivalente.

## 5. Tratamento da Curva Total

A curva total possui linhas duplicadas por `CDFORNECED`.

Regra proposta para a versao `06`:

1. Consolidar por `CDFORNECED`.
2. Somar `TOT_FORN`.
3. Somar ou recalcular `PERC` sobre o total consolidado da curva.
4. Recalcular `TOT_ACUM`.
5. Recalcular `POS`.
6. Reclassificar `CURVA` depois da consolidacao.
7. Preservar no detalhe as linhas originais da curva que formaram o fornecedor consolidado.

Motivo:

se um mesmo fornecedor aparece em mais de uma linha na curva, usar apenas a primeira linha distorce valor, posicao e classe ABC. Para a pagina de auditoria, o fornecedor deve aparecer uma vez, com seu valor total consolidado.

## 6. Tratamento de Cadastro Interno

Para cada fornecedor da curva:

1. Procurar no cadastro mestre por `CDFORNECED`.
2. Se encontrar:
   - consolidar empresas onde aparece;
   - trazer razao social interna;
   - trazer fantasia interna;
   - trazer documento interno;
   - trazer IE, IM, emails e situacao interna;
   - marcar `Origem cadastro = Cadastrado`.
3. Se nao encontrar:
   - manter razao social da curva;
   - manter codigo da curva;
   - marcar `Origem cadastro = Fora do cadastro`;
   - nao inventar dados cadastrais internos;
   - deixar pendencias internas explicitamente marcadas.

## 7. Tratamento de Enderecos Internos

Para cada ocorrencia cadastrada:

1. Cruzar com a planilha de enderecos por `EMPRESA + CDFORNECED`.
2. Se houver uma linha:
   - trazer endereco, bairro, CEP, cidade, UF, telefones, contato e email.
3. Se houver mais de uma linha:
   - escolher a linha mais completa para o resumo;
   - preservar todas as ocorrencias no detalhe;
   - marcar `Endereco duplicado`.
4. Se nao houver linha:
   - marcar `Sem endereco interno`.

Campos de qualidade de endereco:

- `endereco_interno_status`;
- `endereco_interno_completo`;
- `tem_uf_interna`;
- `tem_municipio_interno`;
- `tem_cep_interno`;
- `tem_telefone_interno`;
- `tem_email_contato_interno`;
- `tem_contato_interno`.

## 8. OpenCNPJ na Versao 06

### 8.1 Reuso de cache

Para cada fornecedor da curva com CNPJ valido:

1. verificar se existe arquivo no cache `99_cache_opencnpj`;
2. se existir, usar o payload local;
3. se nao existir, consultar a API OpenCNPJ;
4. salvar no cache;
5. registrar status da consulta.

Status previstos:

- `cache`;
- `api`;
- `http_404`;
- `erro_requisicao`;
- `sem_cnpj`;
- `nao_aplicavel_pf`;
- `nao_aplicavel_outro`.

### 8.2 CNPJs faltantes

Na analise preliminar, a nova curva possui CNPJs validos ainda sem cache local.

Na execucao da versao `06`, esses CNPJs devem ser consultados.

O script deve ser retomavel:

- se parar, a proxima execucao usa o cache ja salvo;
- nao repete consultas desnecessarias;
- gera resumo de quantos vieram de cache e quantos vieram da API.

## 9. Comparacao de Municipio e UF

Comparar:

- municipio interno da planilha de enderecos: `NMMUNICIPIO`;
- UF interna da planilha de enderecos: `SGESTADO`;
- municipio oficial OpenCNPJ;
- UF oficial OpenCNPJ.

Regras:

1. Normalizar texto para comparar sem acento, caixa e espacos duplicados.
2. Comparar UF por sigla.
3. Comparar municipio por nome normalizado.
4. Quando houver codigo IBGE interno e algum codigo equivalente oficial disponivel, preferir comparacao por codigo.
5. Se o dado interno estiver vazio e o oficial existir, marcar como `Dado novo`.
6. Se ambos existirem e forem diferentes, marcar como `Divergencia`.
7. Se ambos existirem e baterem, marcar como `OK`.
8. Se ambos faltarem, marcar como `Sem dado`.

Campos propostos:

- `uf_interna`;
- `uf_oficial`;
- `uf_status`;
- `municipio_interno`;
- `municipio_oficial`;
- `municipio_status`;
- `endereco_interno`;
- `endereco_oficial`;
- `endereco_status`;
- `telefone_interno`;
- `telefone_oficial`;
- `telefone_status`;
- `email_contato_interno`;
- `email_oficial`;
- `email_status`.

Status propostos:

- `OK`;
- `Dado novo`;
- `Divergencia`;
- `Sem dado interno`;
- `Sem dado oficial`;
- `Nao aplicavel`.

## 10. Dados Novos

Um dado sera marcado como novo quando:

- existe na OpenCNPJ e nao existe no cadastro/endereco interno;
- existe na planilha de enderecos e nao existe no cadastro mestre;
- existe na curva e nao existe no cadastro mestre;
- existe telefone/contato/email na planilha de enderecos e o cadastro principal nao possui equivalente util.

Categorias de dado novo:

- `endereco`;
- `municipio`;
- `uf`;
- `cep`;
- `telefone`;
- `email`;
- `contato`;
- `razao_social_oficial`;
- `fantasia_oficial`;
- `situacao_oficial`;
- `regime`;
- `simples`;
- `mei`;
- `credito`;
- `curva_total`;
- `fornecedor_fora_cadastro`.

## 11. Outputs Propostos

Criar uma nova pasta:

`output/fase_06_curva_total`

Arquivos:

1. `00_resumo_versao_06.json`
2. `01_fornecedores_curva_total_base.csv`
3. `02_fornecedores_curva_total_com_cadastro_endereco.csv`
4. `03_fornecedores_curva_total_opencnpj.csv`
5. `04_fornecedores_curva_total_auditoria.csv`
6. `05_fornecedores_curva_total_pendencias.csv`
7. `06_painel_auditoria_fornecedores_curva_total.html`

O HTML deve ser gerado a partir de uma copia da versao `05`.

Script proposto:

`scripts/build_supplier_audit_panel_v06.py`

## 12. Painel HTML 06

Partir de copia da versao `05` e preservar:

- layout geral;
- filtros em duas linhas;
- busca no cabecalho;
- paginacao;
- linha unica expansivel;
- tags coloridas;
- helps ricos;
- ordenacao por ABC, Valor, Fiscal, Credito e Score de Cadastro;
- detalhes em boxes.

Alteracoes especificas:

- universo passa a ser a curva total;
- adicionar status `Cadastrado` / `Fora do cadastro`;
- adicionar status de endereco interno;
- adicionar comparacao UF/municipio;
- nos detalhes, incluir box claro de:
  - `Endereco interno`;
  - `Endereco oficial OpenCNPJ`;
  - `Comparacao endereco`;
  - `Ocorrencias na curva`;
  - `Ocorrencias no cadastro`.

Filtros novos sugeridos:

- `Origem cadastro`: `Cadastrado`, `Fora do cadastro`;
- `Endereco interno`: `Completo`, `Incompleto`, `Sem endereco`, `Duplicado`;
- `UF bate`: `OK`, `Divergencia`, `Dado novo`, `Sem dado`;
- `Municipio bate`: `OK`, `Divergencia`, `Dado novo`, `Sem dado`;
- `OpenCNPJ`: `cache`, `api`, `sem cnpj`, `nao aplicavel`, `erro`.

## 13. Metodologia de Atualizacao Fiscal

Manter a logica ja usada na versao `05`:

- `Nao Simples` tende a `Credito Alto`;
- `Simples` tende a `Credito Condicionado`;
- `MEI` tende a `Credito Baixo`;
- `Indeterminado` exige validacao;
- `Sem dado` permanece sem classificacao.

Observacao:

essa classificacao e operacional e preliminar. Nao substitui validacao fiscal formal.

## 14. Decisoes que Devem Ficar Explicitas na Tela

1. A versao `06` mostra fornecedores da curva, nao todos os fornecedores.
2. Fornecedores PF/CPF nao passam por OpenCNPJ.
3. Fornecedores fora do cadastro devem ser tratados como alerta operacional.
4. Endereco interno e endereco oficial podem divergir por causa de filial, matriz, cadastro antigo ou dado incompleto.
5. Divergencia nao significa automaticamente erro; significa necessidade de revisao antes de atualizar banco.

## 15. Ordem de Implementacao

1. Criar script de leitura da curva total.
2. Consolidar curva por `CDFORNECED`.
3. Recalcular curva ABC consolidada.
4. Ler cadastro mestre.
5. Ler planilha de enderecos.
6. Cruzar curva x cadastro x enderecos.
7. Montar fila OpenCNPJ somente para CNPJs validos da curva.
8. Reusar cache local.
9. Consultar CNPJs faltantes.
10. Gerar base enriquecida da versao `06`.
11. Gerar auditoria de divergencias e dados novos.
12. Copiar a versao `05` para base da `06`.
13. Adaptar o HTML ao novo universo e novos campos.
14. Gerar resumo JSON.
15. Atualizar `DIARIO_DE_BORDO.md`.

## 16. Validacoes Antes de Considerar Concluido

- Total de fornecedores da versao `06` deve bater com a curva consolidada por `CDFORNECED`.
- Total de valor consolidado deve bater com a soma da curva original.
- Quantidade de fornecedores fora do cadastro deve ser informada.
- Quantidade de fornecedores sem endereco interno deve ser informada.
- Quantidade de CNPJs consultados na OpenCNPJ deve separar `cache` e `api`.
- Quantidade de divergencias de UF e municipio deve ser informada.
- A versao `05` nao deve ser alterada.

## 17. Status do Plano

Este documento registra o plano da versao `06`.

Ainda nao e a implementacao.

A implementacao deve comecar somente depois deste desenho, seguindo estes limites:

- partir de uma copia da versao `05`;
- nao alterar a versao `04`;
- nao alterar a versao `05`;
- usar somente fornecedores presentes em `data/CURVA_ABC_FORN_-_TOTAL.xlsx`;
- usar cache OpenCNPJ primeiro;
- consultar na OpenCNPJ somente CNPJs validos que ainda nao estejam cacheados;
- incluir enderecos, contatos e telefones da planilha interna de enderecos;
- comparar UF e municipio internos contra UF e municipio oficiais da OpenCNPJ;
- marcar dados faltantes, dados novos e divergencias de forma auditavel.
