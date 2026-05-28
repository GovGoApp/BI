# Matriz de Creditos 2027 por Regime Fiscal

## Objetivo

Traduzir o regime fiscal do fornecedor em uma leitura operacional de potencial de credito de IBS/CBS a partir da Reforma Tributaria do Consumo.

Esta matriz nao substitui parecer fiscal. Ela serve para orientar o painel `08` e priorizar fornecedores para compra, saneamento e validacao.

## Premissas

- A leitura e feita do ponto de vista da empresa compradora.
- O credito depende de haver IBS/CBS pago na operacao de compra.
- O regime do fornecedor ajuda, mas nao e o unico fator.
- Produto, documento fiscal, aliquota, isencao, imunidade, aliquota zero, diferimento, suspensao e regras especificas tambem podem alterar o credito.
- Em 2027, a CBS substitui PIS/Cofins e o IBS entra em transicao. A logica de credito deve ser tratada dentro da sistematica IBS/CBS.

## Regra geral do novo sistema

No regime regular, o IBS e a CBS seguem logica de IVA nao cumulativo. Em termos praticos, quando a empresa compra bens ou servicos tributados e o imposto e pago, ela tende a poder se creditar desses valores, salvo vedacoes legais.

As principais vedacoes e limitacoes aparecem em operacoes de uso/consumo pessoal, isencao, imunidade, alguns regimes especificos e casos em que nao houve pagamento do imposto.

## Matriz operacional

| Regime do fornecedor | Como ler para credito 2027 | Potencial de credito | Como mostrar no painel |
|---|---|---|---|
| Nao Simples - regime regular | Fornecedor apura IBS/CBS fora do Simples. Em operacao tributada, o adquirente sujeito ao regime regular tende a tomar credito do IBS/CBS pago. | Alto | `Alto`, origem `Regime regular` |
| Lucro Real | E uma forma de tributacao fora do Simples. Para IBS/CBS, deve ser lido como fornecedor em regime regular, se a operacao for tributada. | Alto | `Alto`, evidencia `Lucro Real` |
| Lucro Presumido | Tambem e fora do Simples. Para IBS/CBS, a diferenca Lucro Real versus Presumido nao e o principal fator do credito do comprador; ambos indicam nao Simples. | Alto | `Alto`, evidencia `Lucro Presumido` |
| Lucro Arbitrado | Fora do Simples. Deve ser tratado como nao Simples, mas com alerta fiscal pela natureza excepcional do regime. | Alto com alerta | `Alto`, alerta `Lucro Arbitrado` |
| Imune/Isenta de IRPJ | Nao significa automaticamente que a operacao de IBS/CBS gera credito. Precisa verificar a natureza da operacao, imunidade/isencao e documento fiscal. | Validar | `Validar`, evidencia `Imune/Isenta` |
| Simples Nacional recolhendo IBS/CBS dentro do Simples | O fornecedor paga IBS/CBS dentro do regime simplificado. O comprador pode tomar credito correspondente ao valor desses tributos devido por esse regime, normalmente menor que o credito de um fornecedor no regime regular. | Condicionado/menor | `Condicionado`, origem `Simples no DAS` |
| Simples Nacional optante pelo regime regular de IBS/CBS | A empresa continua no Simples para os demais tributos, mas apura IBS/CBS pelo regime regular. Nessa hipotese, a tendencia e permitir credito mais semelhante ao fornecedor nao Simples. | Alto/regular | `Alto`, origem `Simples com IBS/CBS regular` |
| MEI/SIMEI | O MEI tem regime proprio. Em regra operacional, deve ser tratado como baixo potencial ou credito muito limitado, salvo regra especifica aplicavel. | Baixo/limitado | `Baixo`, origem `SIMEI` |
| PF/CPF nao contribuinte | Em regra, pessoa fisica nao contribuinte nao destaca IBS/CBS e nao gera credito comum. Pode haver excecoes, como credito presumido para produtor rural nao contribuinte e outros casos especificos. | Baixo ou presumido | `Validar`, subtipo `PF/produtor rural` |
| Produtor rural nao contribuinte | A LC 214/2025 preve credito presumido em aquisicoes de produtor rural ou produtor rural integrado nao contribuinte, conforme regras especificas. | Presumido | `Presumido`, origem `Produtor rural` |
| Indeterminado | Nao ha evidencia suficiente para classificar. Deve ir para fila de enriquecimento fiscal. | Pendente | `Pendente` |

## Regras propostas para o painel 08

1. `MEI` deve prevalecer sobre `Simples`, porque MEI tambem pode aparecer como optante do Simples.
2. `Simples` deve ser classificado como `Condicionado`, nao como `Alto`, ate sabermos se o fornecedor optou pelo regime regular de IBS/CBS.
3. `Nao Simples` por flag direta deve receber `Alto`, desde que a operacao seja tributada.
4. `Nao Simples` inferido por `Lucro Real` ou `Lucro Presumido` deve receber `Alto`, mas com origem `inferido por regime tributario`.
5. `Imune/Isenta` nao deve cair automaticamente em `Alto`; deve ir para validacao fiscal.
6. `PF/CPF` deve separar produtor rural de outros tipos de pessoa fisica.
7. `Indeterminado` deve continuar pendente, priorizado por valor de compra ou curva ABC.

## O que ainda precisa ser descoberto por fornecedor

Para transformar a matriz em decisao final de compra, o `08` deve buscar ou receber:

- se o fornecedor Simples optou ou nao pelo regime regular de IBS/CBS;
- se o fornecedor PF e produtor rural, transportador autonomo ou outro tipo;
- se a operacao/produto tem aliquota zero, isencao, imunidade, reducao ou regime especifico;
- se ha documento fiscal valido com campos IBS/CBS;
- se houve pagamento do tributo, pois o credito esta ligado ao pagamento;
- qual o ano do regime tributario usado como evidencia, quando a classificacao for inferida.

## Leitura pratica para compras

Fornecedores `Nao Simples` tendem a ser melhores para credito no novo modelo, mas nao devem ser escolhidos apenas por isso. O preco liquido apos credito, regularidade fiscal, capacidade de entrega, qualidade, risco operacional e produto comprado continuam importantes.

Fornecedores `Simples` podem continuar competitivos, mas precisam ser comparados pelo preco liquido considerando o credito menor ou condicionado. Se optarem pelo regime regular de IBS/CBS, podem se aproximar dos fornecedores nao Simples em termos de creditamento.

Fornecedores `MEI`, `PF` e `Indeterminado` devem ser tratados com mais cuidado fiscal antes de entrar em uma decisao automatica de compra.

## Fontes normativas e tecnicas consultadas

- Receita Federal - Entenda a Reforma Tributaria do Consumo.
- Ministerio da Fazenda - Resumos tecnicos da Lei Geral do IBS, da CBS e do Imposto Seletivo.
- Ministerio da Fazenda - Resolucao CGSN nº 186/2026 e opcao pelo regime regular de IBS/CBS para 2027.
- Lei Complementar nº 214/2025.

