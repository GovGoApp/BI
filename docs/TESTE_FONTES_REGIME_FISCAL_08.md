# Teste de Fontes para Regime Fiscal - Versao 08

## Objetivo

Testar, antes da escolha da fonte principal do `08`, quais portais ou APIs conseguem resolver fornecedores que aparecem no painel `07` como `Regime = Indeterminado`.

O teste foi feito com fornecedores reais da base `output/07_cadastro_total_opencnpj/04_fornecedores_total_auditoria.csv`, priorizando CNPJs com maior valor de curva/movimento.

## Amostra

Foram selecionados 10 fornecedores PJ/CNPJ com regime indeterminado:

| CNPJ | Fornecedor | Valor |
|---|---|---:|
| 51142623000130 | FONTE VIVA ALIMENTOS LTDA | R$ 54.288.573 |
| 13884131000120 | OTMA SOLUCAO EM ALIMENTACAO LTDA | R$ 16.678.386 |
| 65941775000107 | HORTCLEAN DIST. PROD. ALIM. LTDA | R$ 13.064.379 |
| 04603630000373 | IND E COM. CARNES E DERIV. BOI BRASIL LTDA | R$ 10.290.686 |
| 29541660000161 | PRIME CARNES INDUSTRIA E COMERCIO LTDA | R$ 9.693.964 |
| 01797454000106 | NUTRII LIFFE COMERCIO LTDA. | R$ 9.139.492 |
| 17793806000187 | DUARTE ALIMENTOS ATACADISTA EIRELI | R$ 5.638.892 |
| 07738468000127 | A AZEVEDO DA SILVA | R$ 4.797.704 |
| 05880726000180 | SUDESTE INDUSTRIA E COMERCIO LTDA | R$ 4.573.436 |
| 12464051000153 | BASTO MESQUITA DISTRIBUICAO E LOGITICA | R$ 4.293.331 |

## Fontes testadas

### OpenCNPJ local

Resultado: nao resolveu estes casos.

Nos CNPJs testados, o cache OpenCNPJ tinha dados cadastrais, endereco e contato, mas `opcao_simples` e `opcao_mei` estavam vazios. Portanto, o OpenCNPJ continua util para cadastro/endereco, mas nao deve ser a unica fonte para regime fiscal.

### BrasilAPI

Endpoint testado:

`https://brasilapi.com.br/api/cnpj/v1/{cnpj}`

Resultado: resolveu 9 de 10 casos da amostra.

A BrasilAPI retornou `regime_tributario`, com `forma_de_tributacao` por ano, em 9 fornecedores. Exemplos encontrados:

| CNPJ | Resultado BrasilAPI |
|---|---|
| 51142623000130 | 2023: LUCRO PRESUMIDO; 2024: LUCRO PRESUMIDO |
| 13884131000120 | 2018 a 2022: LUCRO REAL; 2023 e 2024: LUCRO PRESUMIDO |
| 65941775000107 | 2016 a 2024: LUCRO REAL |
| 29541660000161 | 2019 e 2020: LUCRO PRESUMIDO; 2021 a 2024: LUCRO REAL |
| 01797454000106 | 2019 a 2023: LUCRO PRESUMIDO; 2024: LUCRO REAL |

Observacao importante: quando `regime_tributario` existe, ele vem de informacoes anuais de ECF/regimes tributarios. Isso e melhor do que apenas classificar como `Nao Simples`, porque permite distinguir `Lucro Real`, `Lucro Presumido`, `Lucro Arbitrado` e `Imunes/Isentas`, quando disponivel.

### Minha Receita

Endpoint testado:

`https://minhareceita.org/{cnpj}`

Resultado: resolveu 9 de 10 casos da amostra, com os mesmos resultados da BrasilAPI.

A documentacao da Minha Receita informa que os campos `opcao_pelo_simples`, `opcao_pelo_mei` e `regime_tributario` sao derivados de arquivos publicos da Receita Federal, incluindo `Simples.zip` e arquivos anuais de regime tributario.

### ReceitaWS

Endpoint testado:

`https://www.receitaws.com.br/v1/cnpj/{cnpj}`

Resultado: testado apenas nos 3 primeiros CNPJs para evitar abuso de limite gratuito.

Nos 3 casos, retornou `simples.optante = false` e `simei.optante = false`, mas nao retornou a forma de tributacao completa, como `Lucro Real` ou `Lucro Presumido`.

Conclusao: pode ajudar a confirmar Simples/SIMEI em alguns casos, mas e inferior a BrasilAPI/Minha Receita para o objetivo do `08`.

### CNPJ.ws publica

Endpoint testado:

`https://publica.cnpj.ws/cnpj/{cnpj}`

Resultado: testado em 1 CNPJ por causa do limite publico.

Para o CNPJ testado, `simples = null`. A documentacao informa que o registro de Simples/MEI so e preenchido quando a empresa e, ou ja foi, Simples/MEI. A propria documentacao tambem informa que dados completos de regimes tributarios ficam disponiveis apenas na API comercial.

Conclusao: a API publica pode ajudar em Simples/MEI, mas nao parece ser a melhor fonte gratuita para resolver os 6.229 indeterminados em lote.

### Portal oficial do Simples Nacional

URL testada:

`https://consopt.www8.receita.fazenda.gov.br/consultaoptantes/Home/ConsultarCnpj?vc={cnpj}`

Resultado: o portal redireciona para formulario com hCaptcha.

Conclusao: e uma fonte oficial de conferencia, mas nao e uma API livre para processamento em lote nesta etapa.

### Biblioteca simplesnacional

Status local: nao instalada neste ambiente no momento do teste.

A documentacao informa que a biblioteca baixa uma base local do Simples Nacional e permite consultar `opcao_simples`, `data_opcao_simples`, `opcao_mei` e datas de exclusao. Continua sendo uma candidata importante para resolver Simples/MEI em lote, mas nao foi testada operacionalmente nesta rodada.

## Arquivos gerados

- `output/08_regime_fiscal/00_teste_fontes_regime_fiscal.csv`
- `output/08_regime_fiscal/00_teste_fontes_regime_fiscal_raw.json`

## Conclusao preliminar

A melhor fonte gratuita testada para a versao `08` foi `BrasilAPI` ou `Minha Receita`.

Motivo:

- resolveram 9 de 10 fornecedores indeterminados da amostra;
- trouxeram `Lucro Real` e `Lucro Presumido` por ano, nao apenas Simples/MEI;
- retornaram os mesmos dados nos testes, sugerindo origem comum ou compatibilidade forte;
- sao mais uteis para o objetivo fiscal do que OpenCNPJ, ReceitaWS e CNPJ.ws publica neste caso especifico.

Recomendacao tecnica preliminar:

1. Usar OpenCNPJ como fonte principal de cadastro/endereco.
2. Usar BrasilAPI ou Minha Receita para resolver `regime_tributario` dos indeterminados.
3. Guardar cache local dos retornos do `08`.
4. Para fornecedores que continuarem sem `regime_tributario`, testar a biblioteca `simplesnacional` ou gerar fila de conferencia oficial no Portal do Simples Nacional.

## Ressalvas fiscais

Os dados de regime tributario retornam por ano de apuracao. Na amostra, o ano mais recente observado foi 2024. Para uma leitura operacional em 2026, o painel deve mostrar o ultimo regime conhecido e o respectivo ano, sem afirmar que ele e necessariamente o regime corrente de 2026 se a fonte ainda nao disponibilizou anos mais recentes.

## Complemento - Simples, MEI e Nao Simples

Foi feito um teste adicional para confirmar explicitamente se BrasilAPI e Minha Receita retornam as informacoes centrais para o objetivo fiscal de 2027: `Simples`, `MEI` e `Nao Simples`.

Arquivo gerado:

- `output/08_regime_fiscal/00_teste_flags_simples_mei_nao_simples.csv`

Resultado:

| Caso | CNPJ | Fonte | `opcao_pelo_simples` | `opcao_pelo_mei` | Classificacao proposta no 08 |
|---|---|---|---:|---:|---|
| Simples | 28722523000160 | BrasilAPI/Minha Receita | true | false | Simples |
| MEI | 43634640000166 | BrasilAPI/Minha Receita | true | true | MEI |
| Nao Simples | 19780714000198 | BrasilAPI/Minha Receita | false | false | Nao Simples |
| Indeterminado com regime tributario | 51142623000130 | BrasilAPI/Minha Receita | null | null | Nao Simples inferido por Lucro Presumido |
| Indeterminado sem regime tributario | 04603630000373 | BrasilAPI/Minha Receita | null | null | Indeterminado |

Regra correta para o `08`:

1. Se `opcao_pelo_mei = true`, classificar como `MEI`.
2. Se `opcao_pelo_simples = true` e `opcao_pelo_mei != true`, classificar como `Simples`.
3. Se `opcao_pelo_simples = false`, classificar como `Nao Simples`.
4. Se `opcao_pelo_simples` e `opcao_pelo_mei` vierem nulos, mas existir `regime_tributario` com `Lucro Real`, `Lucro Presumido`, `Lucro Arbitrado` ou `Imune/Isenta`, classificar como `Nao Simples`, com origem `inferido por regime tributario`.
5. Se nao houver flags Simples/MEI nem `regime_tributario`, manter como `Indeterminado`.

Esta regra atende melhor ao objetivo original do projeto: separar fornecedores que tendem a gerar credito regular no regime nao cumulativo daqueles em Simples/MEI, que exigem tratamento fiscal especifico no cenario da Reforma Tributaria a partir de 2027.

## Complemento - Amostra ampliada de 50 indeterminados

Para validar se havia vantagem real em consultar uma nova fonte, foi feito um teste adicional com os 50 fornecedores de maior valor que estavam como `Regime = Indeterminado` no `07`.

Fonte testada nesta rodada:

- Minha Receita.

Arquivo gerado:

- `output/08_regime_fiscal/01_teste_lote_50_indeterminados_minhareceita.csv`

Resultado:

| Classificacao apos Minha Receita | Quantidade |
|---|---:|
| Nao Simples | 34 |
| Indeterminado | 16 |

Todos os 34 resolvidos como `Nao Simples` foram classificados por criterio `inferido_regime_tributario`, ou seja, a fonte retornou um regime anual como `LUCRO REAL`, `LUCRO PRESUMIDO` ou `IMUNE DE IRPJ`.

Interpretacao:

- OpenCNPJ nao havia resolvido esses 50 porque os campos `opcao_simples` e `opcao_mei` estavam vazios.
- A nova busca trouxe vantagem concreta em 34 de 50 casos testados.
- A vantagem nao e descobrir `opcao_pelo_simples=false` explicitamente nesses casos; a vantagem e encontrar `regime_tributario`, que permite classificar o fornecedor como `Nao Simples` com criterio rastreavel.
- Ainda restaram 16 de 50 sem resposta fiscal; esses devem permanecer como `Indeterminado` ou ir para uma fonte complementar.

Conclusao desta rodada: a nova busca se justifica principalmente para reduzir o bloco `Indeterminado` dos fornecedores mais relevantes por valor, mas o painel deve deixar claro quando a classificacao `Nao Simples` veio por flag direta e quando veio por inferencia a partir de `regime_tributario`.
