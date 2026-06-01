# Levantamento Inicial das Bases

Data do levantamento: `2026-05-20`

## 1. Arquivos analisados

- `data/FORNECEDORES - TODAS AS EMPRESAS.xlsx`
- `data/CURVA_FORN_-_TODAS.csv`
- `data/NFE.csv`

## 2. Cadastro mestre

### 2.1 Abas encontradas

- `IDEAL`
- `MELHOR`
- `POMME`

### 2.2 Volume por aba

| Aba | Linhas |
| --- | ---: |
| `IDEAL` | 12.941 |
| `MELHOR` | 2.244 |
| `POMME` | 10.369 |
| **Total** | **25.554** |

### 2.3 Chaves e identidade

- `15.718` CNPJs unicos no cadastro mestre.
- `15.718` codigos unicos `CDFORNECED` no cadastro mestre.
- `6.139` CNPJs aparecem em apenas uma empresa.
- `9.323` CNPJs aparecem em duas empresas.
- `256` CNPJs aparecem nas tres empresas.

Leitura de negocio:

- o grupo tem um volume alto de fornecedores compartilhados;
- a chave de trabalho deve ser o `CNPJ normalizado`;
- o codigo `CDFORNECED` continua importante como chave operacional interna por empresa/sistema.

### 2.4 Completude inicial de campos relevantes

| Aba | Email vazio | IE vazia | IM vazia |
| --- | ---: | ---: | ---: |
| `IDEAL` | 7.453 | 4.967 | 7.658 |
| `MELHOR` | 2.153 | 1.021 | 2.131 |
| `POMME` | 5.655 | 3.521 | 5.271 |
| **Total** | **15.261** | **9.509** | **15.060** |

Percentuais consolidados sobre o total do cadastro:

- email vazio: `59,72%`
- inscricao estadual vazia: `37,21%`
- inscricao municipal vazia: `58,93%`

### 2.5 Situacao cadastral interna

| Situacao | Quantidade |
| --- | ---: |
| `A` | 25.341 |
| `I` | 206 |
| vazio | 7 |

Observacao:

- o status interno da planilha nao substitui a situacao cadastral oficial do CNPJ; ele deve ser reconciliado com fonte externa.

## 3. Base de curva

### 3.1 Volume

- `1.621` fornecedores classificados.

### 3.2 Distribuicao da curva

| Curva | Quantidade |
| --- | ---: |
| `AAA` | 22 |
| `AA` | 17 |
| `A` | 26 |
| `B` | 43 |
| `BB` | 88 |
| `C` | 99 |
| `CC` | 152 |
| `CCC` | 1.174 |

Leitura de negocio:

- a base de curva esta fortemente concentrada em `CCC`;
- ela parece refletir apenas o subconjunto de fornecedores efetivamente movimentados/comprados.

## 4. Base de NFe

### 4.1 Volume

- `237.931` linhas.
- `3.280` fornecedores unicos.
- `6.259` produtos unicos.

### 4.2 Distribuicao por empresa

| Empresa | Linhas |
| --- | ---: |
| `RC` | 162.375 |
| `SU` | 46.412 |
| `ME` | 29.144 |

### 4.3 Principais UFs

| UF | Linhas |
| --- | ---: |
| `SP` | 89.509 |
| `PE` | 63.993 |
| `ES` | 37.761 |
| `DF` | 12.386 |
| `MA` | 8.735 |
| `PI` | 8.223 |
| `PA` | 6.818 |
| `RJ` | 4.059 |
| `PB` | 2.636 |
| `RN` | 2.083 |

### 4.4 Distribuicao da curva do fornecedor na NFe

| Curva | Linhas |
| --- | ---: |
| `AAA` | 73.294 |
| `AA` | 12.376 |
| `A` | 24.855 |
| `B` | 34.050 |
| `BB` | 28.570 |
| `C` | 16.814 |
| `CC` | 13.975 |
| `CCC` | 17.256 |
| vazio | 16.741 |

Observacao:

- existem linhas de NFe sem classificacao de curva preenchida, o que precisara ser tratado na conciliacao.

## 5. Cobertura entre as bases

### 5.1 Cadastro x NFe

- `2.686` fornecedores da NFe aparecem no cadastro mestre.
- `594` fornecedores da NFe nao aparecem no cadastro mestre atual.
- `13.032` fornecedores do cadastro mestre nao aparecem na base de NFe analisada.

Leitura:

- ha fornecedores com compra sem cadastro mestre reconciliado;
- ha tambem muitos fornecedores cadastrados sem movimento na janela atual da NFe.

### 5.2 Cadastro x Curva

- `1.527` fornecedores da curva aparecem no cadastro mestre.
- `94` fornecedores da curva nao aparecem no cadastro mestre atual.
- `14.191` fornecedores do cadastro mestre nao aparecem na base de curva.

## 6. Conclusoes operacionais

1. A primeira entidade canonica do projeto deve ser `fornecedor_unificado`, ancorada em `CNPJ normalizado`.
2. O cadastro mestre precisa de uma trilha explicita de completude cadastral.
3. A conciliacao entre cadastro, NFe e curva deve acontecer antes de qualquer ranking de fornecedor.
4. O enriquecimento por `OpenCNPJ` e necessario para obter situacao cadastral oficial, natureza juridica, porte, matriz/filial e indicios de enquadramento.
5. A comparacao por produto devera usar ao mesmo tempo:
   - preco historico da NFe;
   - presenca e peso na curva;
   - situacao cadastral/fiscal do fornecedor;
   - potencial de credito tributario no cenario 2027.
