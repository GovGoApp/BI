# Dados e dominios - BI de Suprimentos

## Contexto geral

O BI sera construido a partir de dados hoje extraidos do Zoho Analytics, workspace `SUPRIMENTOS`, cruzados com a base de fornecedores/regime fiscal ja criada neste repositorio.

O mock nao precisa conectar dados reais. Ele deve apenas refletir a estrutura e os conceitos abaixo.

## Fontes principais

Compras / notas:

- `NFE`
- `NF COM ITENS - CONSOLIDADO`
- `ENTRADA DE NOTAS - [TODAS]`
- `NFE - IDEAL`
- `NFE - MELHOR`
- `NFE - SUPERA`

Cotacoes:

- `COT`
- `COT_MIN_FORN`
- `NUM_COT`
- `COT - IDEAL`
- `COT - MELHOR`
- `COT - SUPERA`

Curvas ABC:

- `CURVA FORN - TODAS`
- `CURVA ABC FORN - TOTAL`
- `CURVA PROD - TODAS`
- `CURVA PROD - IDEAL`
- `CURVA PROD - MELHOR`
- `CURVA PROD - SUPERA`
- `CURVA ID - TODAS`

Preco medio, inflacao e impacto:

- `PMP_ID`
- `PMP_ID_INF`
- `PMP_ID_INF_12`
- `PMP_PROD`
- `PMP_PROD_INF`
- `PMP_PROD_INF_12`
- `INFLACAO`

Financeiro:

- `CP`
- `CP_MOV`
- `CP_SEMANA`
- `CP_SALDO_2025`
- `CP_SALDO_2026`
- `TODAS - CONTAS A PAGAR`

Adiantamentos:

- `ADIANTAMENTO_NFE`
- `AD_v1`
- `AD_v2`
- `AD_v3`
- `NF ADT - IDEAL`
- `NF ADT - MELHOR`
- `NF ADT - POMME VITA`

Cadastro/fiscal:

- base do painel de fornecedores 08b;
- regime fiscal;
- credito 2027;
- situacao cadastral;
- saneamento cadastral.

## Empresas

No Zoho aparecem principalmente:

- `RC`
- `ME`
- `SU`

Relacao operacional observada:

- `RC`: ligado a Ideal/RC;
- `ME`: ligado a Melhor;
- `SU`: ligado a Supera/Pomme Vita, conforme nomenclatura da base.

No mock, pode usar badges:

- RC
- ME
- SU

Se quiser manter a linguagem do painel de fornecedores, tambem pode exibir:

- IDEAL
- MELHOR
- POMME/SUPERA

## Tipos de negocio

Dominios identificados:

- CD
- COZINHA
- ESCOLA
- HOSPITAL
- MERENDA
- PRESIDIO
- MATRIZ

Use esses valores nos filtros e exemplos.

## UFs

UFs identificadas:

- DF
- ES
- MA
- PA
- PB
- PE
- PI
- RJ
- RN
- SE
- SP

## Campos de fornecedor

Exemplos de campos:

- `CDFORNECED`
- `NMRAZSOCFORN`
- `NMFANTFORN`
- `CDFORNECED_OFICIAL`
- `FANTASIA_OFICIAL`
- `RAZAO_OFICIAL`
- CNPJ/documento;
- regime fiscal;
- credito 2027;
- curva fornecedor;
- posicao na curva;
- valor comprado;
- produtos unicos;
- UFs atendidas.

## Campos de produto

Exemplos:

- `ID`
- `CDPRODUTO`
- `NMPRODUTO`
- `CDPRODESTO`
- `NMPRODUTO_EST`
- `CDPRODUTO_OFICIAL`
- `NMPRODUTO_OFICIAL`
- `CAT1`
- `CAT2`
- `CAT3`
- `CAT4`
- `CAT5`
- curva produto;
- curva ID;
- PMP;
- impacto;
- cotacoes.

## O que e ID

`ID` e uma chave analitica de produto/contexto. Ele parece combinar empresa, UF e codigo padronizado de produto.

Exemplo de formato observado:

- `RCSPI105201000`

No BI, o `ID` deve ser tratado como chave de analise mais especifica que o produto generico. Ele permite comparar preco, cotacao, inflacao e impacto dentro de um contexto operacional.

## Curvas ABC

As curvas ABC classificam fornecedores, produtos ou IDs por relevancia economica.

A logica inferida:

- ordenar por valor total decrescente;
- calcular percentual individual;
- calcular percentual acumulado;
- classificar conforme faixa acumulada.

Faixas observadas/inferidas:

- `AAA`: ate 50% acumulado;
- `AA`: 50% a 60%;
- `A`: 60% a 70%;
- `B`: 70% a 80%;
- `BB`: 80% a 90%;
- `C`: 90% a 95%;
- `CC`: 95% a 98%;
- `CCC`: 98% a 100%.

Tipos de curva:

- curva de fornecedor;
- curva de produto;
- curva de ID.

No design, curvas devem aparecer como chips/pills.

## Cotacoes e minimo de cotacao

Fontes principais:

- `COT_MIN_FORN`
- `NUM_COT`
- campos de cotacao dentro de `NFE`

Campos importantes:

- `QTD_COT`
- `MIN_COT`
- `MED_COT`
- `MAX_COT`
- `PRE_MIN_COT`
- `FORN_MIN_COT`
- `FORN_MENOR_PRECO`
- `CNPJ_MENOR_PRECO`

Uso no BI:

- mostrar quantas cotacoes existem por produto/ID;
- comparar preco comprado x menor cotacao;
- calcular oportunidade em reais;
- apontar fornecedor alternativo de menor preco.

## Impacto

Impacto e uma medida de diferenca economica convertida para reais.

Principais leituras:

- impacto de cotacao: diferenca entre preco comprado e menor cotacao multiplicada pela quantidade;
- impacto de inflacao: efeito da variacao do preco medio ponderado ao longo do tempo;
- impacto por ID: efeito em reais no nivel do ID.

Campos observados:

- `IMP_COT`
- `IMP_ID`
- `IMP_PRODT`
- `INF_ID`
- `SOMA_INF_*`
- `PERC_INF_*`

No mock, use impacto como uma das medidas principais de prioridade.

## PMP_ID_INF_12

`PMP_ID_INF_12` representa uma visao de preco medio ponderado por ID em janela de 12 meses.

Campos tipicos:

- `PMP_0`
- `PMP_1`
- `PMP_2`
- ...
- `PMP_12`

Uso no BI:

- serie historica compacta;
- variacao de preco em 12 meses;
- deteccao de alta ou queda;
- comparacao com cotacoes.

## Numero de cotacoes por produto

Medido principalmente em `NUM_COT`, com o campo:

- `QTD_COT`

Dimensoes usuais:

- `ID`
- `MESANO`
- `UF`
- `NMEMP`

Uso no BI:

- indicar baixa concorrencia;
- destacar produtos com apenas uma cotacao;
- priorizar itens curva A com poucas cotacoes.

## AD / Adiantamentos

`AD` significa adiantamento.

Fonte principal:

- `AD_v3`

Outras fontes:

- `ADIANTAMENTO_NFE`
- `NF ADT - IDEAL`
- `NF ADT - MELHOR`
- `NF ADT - POMME VITA`

Campos de analise:

- `STATUS_CONC`
- `STATUS_CONCILIACAO`
- `VALOR_CONCILIADO`
- `NRONOTA_NF`
- `NRONOTA_AD`
- fornecedor;
- produto;
- filial;
- mes de entrada;
- mes de pagamento.

Uso no BI:

- mostrar adiantamentos pendentes;
- conciliar nota x adiantamento;
- priorizar fornecedores com alto AD em aberto;
- cruzar AD com compras e CP.

## Dados ficticios recomendados para o mock

Fornecedores exemplo:

- FONTE VIVA ALIMENTOS LTDA
- SELECT NUTRI ALIMENTOS E LOGISTICA LTDA
- J. J. FOODS LTDA
- ALIBER FOODS LTDA
- FF INDUSTRIA E COMERCIO DE POLPAS LTDA

Produtos exemplo:

- Arroz tipo 1
- Feijao carioca
- Leite UHT
- Carne bovina
- Frango congelado
- Polpa de fruta
- Oleo de soja

Categorias exemplo:

- Alimentos secos
- Proteinas
- Hortifruti
- Laticinios
- Bebidas
- Embalagens

Status exemplo:

- Comprado acima da menor cotacao
- Baixa concorrencia
- Inflacao alta
- Fiscal pendente
- CP vencido
- AD pendente
- Conciliado

