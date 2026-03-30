# dados-publicos-api

Azure Function App Python para coleta e consulta de índices públicos para precificação de obras de engenharia civil e acompanhamento de mercado imobiliário.

## Infraestrutura Azure

| Recurso | Nome | Detalhes |
|---|---|---|
| Resource Group | `rg-dados-publicos-api` | Brazil South |
| Storage Account | `stdadospublicosapi` | Standard_LRS |
| Table Storage | `IndicesPublicos` | Armazenamento dos índices |
| Function App | `func-dados-publicos-api` | Flex Consumption, Python 3.11 |
| Application Insights | `func-dados-publicos-api` | Monitoramento |

## Autenticação

100% Managed Identity (System-Assigned) com RBAC. Nenhuma connection string de storage.

| RBAC Role | Finalidade |
|---|---|
| Storage Blob Data Owner | Runtime Azure Functions + deployment |
| Storage Queue Data Contributor | Runtime Azure Functions |
| Storage Table Data Contributor | Aplicação (tabela IndicesPublicos) |

## Índices coletados

### Construção civil e inflação

| Índice | Fonte | Periodicidade | Unidade | Trigger |
|---|---|---|---|---|
| INCC-M | FGV/IBRE | Mensal | % | `downloader_fgv` (diário 08h UTC) |
| IGP-M | FGV/IBRE | Mensal | % | `downloader_fgv` (diário 08h UTC) |
| IGP-DI | FGV/IBRE | Mensal | % | `downloader_fgv` (diário 08h UTC) |
| IPCA | IBGE SIDRA | Mensal | % | `downloader_ibge` (diário 09h UTC) |
| INPC | IBGE SIDRA | Mensal | % | `downloader_ibge` (diário 09h UTC) |
| SINAPI | IBGE SIDRA | Mensal | % | `downloader_ibge` (diário 09h UTC) |
| PIB Trimestral | IBGE SIDRA | Trimestral | % a.a. | `downloader_ibge` (diário 09h UTC) |
| ANP Diesel | ANP | Semanal | R$/litro | `downloader_anp` (segunda 10h UTC) |

### Taxas e câmbio (BACEN)

| Índice | Fonte | Periodicidade | Unidade | Trigger |
|---|---|---|---|---|
| Selic | BACEN SGS 11 | Mensal acumulado | % a.a. | `downloader_bacen` (diário 18h UTC) |
| CDI | BACEN SGS 4391 | Mensal acumulado | % a.m. | `downloader_bacen` (diário 18h UTC) |
| PTAX USD | BACEN SGS 3696 | Mensal (fim período) | R$/USD | `downloader_bacen` (diário 18h UTC) |
| Taxa Financ. Imob. PF | BACEN SGS 25497 | Mensal | % a.m. | `downloader_bacen` (diário 18h UTC) |

### Mercado de capitais (B3)

| Índice | Fonte | Periodicidade | Unidade | Trigger |
|---|---|---|---|---|
| IFIX | B3 | Mensal (último dia) | pts | `downloader_b3` (dias 28–31 às 22h UTC) |
| IBOVESPA | B3 | Mensal (último dia) | pts | `downloader_b3` (dias 28–31 às 22h UTC) |
| IMOB | B3 | Mensal (último dia) | pts | `downloader_b3` (dias 28–31 às 22h UTC) |

### Não implementados (dependência de API privada ou fonte sem API pública)

| Índice | Fonte | Motivo |
|---|---|---|
| NTN-B 2035 (taxa indicativa) | ANBIMA | API requer autenticação OAuth (`api.anbima.com.br`) |
| SBPE — saldo poupança | BACEN SGS | Série SGS pública não identificada (IDs testados retornam séries regionais ou de crédito geral, não SBPE habitacional) |
| SBPE — contratações valor | BACEN SGS | Mesma razão; série SBPE específica não encontrada na API pública |
| SBPE — contratações unidades | BACEN SGS | Mesma razão |
| Consumo de cimento | SNIC | Apenas via relatório PDF mensal (sem API pública) |
| Consumo de aço longo | Instituto Aço Brasil | Apenas via relatório PDF mensal (sem API pública) |

## Endpoints HTTP (públicos, sem autenticação)

### GET `/api/indices`

Consulta de índices armazenados.

```
https://func-dados-publicos-api.azurewebsites.net/api/indices
https://func-dados-publicos-api.azurewebsites.net/api/indices?nome=ipca
https://func-dados-publicos-api.azurewebsites.net/api/indices?nome=incc-m&data_inicio=2025-01&data_fim=2025-12
```

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `nome` | Não | Nome do índice (ex: `incc-m`, `ipca`, `cdi`, `ifix`) |
| `data_inicio` | Não | Período inicial `YYYY-MM` |
| `data_fim` | Não | Período final `YYYY-MM` |

Sem parâmetros retorna o último valor de cada índice. Com `nome` retorna o último valor daquele índice. Com `nome` + datas retorna o histórico no intervalo.

### GET `/api/downloader_http`

Disparo forçado de coleta por data.

```
https://func-dados-publicos-api.azurewebsites.net/api/downloader_http?downloader=bacen&date=2026-03-27
https://func-dados-publicos-api.azurewebsites.net/api/downloader_http?downloader=b3&date=2026-03-31
```

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `downloader` | Sim | Nome do downloader: `fgv`, `ibge`, `bacen`, `anp`, `b3` |
| `date` | Sim | Data de referência `YYYY-MM-DD` |

> **Atenção:** `downloader=b3` só coleta dados se `date` for o último dia do mês (guard automático).

## Variáveis de ambiente

Centralizadas em `config.py`. Padrão: `DADPUBAPI_[FUNCAO]_[NOME]`.

| Variável | Descrição |
|---|---|
| `AzureWebJobsStorage__accountName` | Storage Account (identity-based, runtime) |
| `DADPUBAPI_STORAGE_TABLE_URL` | URL do Table endpoint (identity-based, aplicação) |
| `DADPUBAPI_FGV_USER` | Usuário FGV/IBRE |
| `DADPUBAPI_FGV_PASSWORD` | Senha FGV/IBRE |

## Glossário dos índices

### INCC-M — Índice Nacional de Custo da Construção (Mensal)
**O que é:** Mede a variação dos custos de construção civil no Brasil. Composto por mão de obra e materiais de construção.
**Feeder:** `downloader_fgv` → `Feeders/Fgv/GetIncc.py`
**Aplicação real:** Reajuste de contratos de obras e incorporações imobiliárias (ex.: contratos de compra de imóvel na planta — o saldo devedor é corrigido mensalmente pelo INCC-M até a entrega das chaves).

### IGP-M — Índice Geral de Preços do Mercado
**O que é:** Média ponderada de três sub-índices: IPA-M (60% — preços no atacado), IPC-M (30% — preços ao consumidor) e INCC-M (10% — custo da construção).
**Feeder:** `downloader_fgv` → `Feeders/Fgv/GetIgpm.py`
**Aplicação real:** Reajuste de aluguéis residenciais e comerciais, tarifas de energia elétrica e contratos de longo prazo com cláusula de correção monetária.

### IGP-DI — Índice Geral de Preços — Disponibilidade Interna
**O que é:** Mesma metodologia do IGP-M, mas com coleta em período diferente (dia 1 ao dia 30 do mês). Reflete melhor o preço "dentro" do mercado doméstico.
**Feeder:** `downloader_fgv` → `Feeders/Fgv/GetIgpdi.py`
**Aplicação real:** Correção de contratos de obras públicas de infraestrutura, debêntures e alguns financiamentos do BNDES.

### IPCA — Índice Nacional de Preços ao Consumidor Amplo
**O que é:** Inflação oficial do Brasil. Mede a variação de preços de uma cesta de bens e serviços consumidos por famílias com renda de 1 a 40 salários mínimos.
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetIndicadores.py`
**Aplicação real:** Meta de inflação do Banco Central, correção do Tesouro IPCA+ (NTN-B), reajuste de planos de saúde.

### INPC — Índice Nacional de Preços ao Consumidor
**O que é:** Similar ao IPCA, mas focado em famílias de menor renda (1 a 5 salários mínimos).
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetIndicadores.py`
**Aplicação real:** Reajuste do salário mínimo, benefícios previdenciários e dissídios coletivos.

### SINAPI — Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil
**O que é:** Pesquisa mensal do IBGE/CEF com preços de insumos e mão de obra na construção civil, por estado.
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetIndicadores.py`
**Aplicação real:** Referência obrigatória para orçamentos de obras financiadas com recursos públicos federais.

### Selic — Taxa do Sistema Especial de Liquidação e Custódia
**O que é:** Taxa básica de juros da economia brasileira, definida pelo COPOM a cada 45 dias.
**Feeder:** `downloader_bacen` → `Feeders/Bacen/GetSelic.py`
**Aplicação real:** Referência para toda a cadeia de crédito, correção de dívidas tributárias e rendimento do Tesouro Selic.

### CDI — Certificado de Depósito Interbancário
**O que é:** Taxa de juros das operações de crédito entre bancos. Praticamente igual à Selic, usada como benchmark do mercado financeiro.
**Feeder:** `downloader_bacen` → `Feeders/Bacen/GetSeries.py` (SGS 4391)
**Aplicação real:** Rentabilidade de CDBs, fundos de renda fixa, LCIs e debêntures atreladas ao CDI.

### PTAX USD — Taxa de Câmbio Dólar (PTAX)
**O que é:** Média das cotações do dólar americano apuradas pelo Banco Central no mercado interbancário ao longo do mês.
**Feeder:** `downloader_bacen` → `Feeders/Bacen/GetSeries.py` (SGS 3696)
**Aplicação real:** Contratos de câmbio, precificação de importações, correção de dívidas em moeda estrangeira.

### Taxa de Financiamento Imobiliário PF
**O que é:** Taxa média de juros dos financiamentos imobiliários concedidos a pessoas físicas pelo sistema financeiro nacional.
**Feeder:** `downloader_bacen` → `Feeders/Bacen/GetSeries.py` (SGS 25497)
**Aplicação real:** Referência para análise de viabilidade de empreendimentos imobiliários e custo de aquisição de imóveis.

### PIB Trimestral — Produto Interno Bruto
**O que é:** Taxa de variação do PIB a preços de mercado em relação ao mesmo período do ano anterior.
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetPib.py`
**Aplicação real:** Indicador macroeconômico de crescimento econômico; referência para análise de viabilidade de projetos e projeção de demanda imobiliária.
**Observação:** RowKey usa o último mês do trimestre (Q1→03, Q2→06, Q3→09, Q4→12). IBGE publica com ~2 meses de defasagem.

### ANP Diesel — Preço médio do Diesel
**O que é:** Levantamento semanal da ANP com o preço médio de revenda do diesel ao consumidor.
**Feeder:** `downloader_anp` → `Feeders/Anp/GetDiesel.py`
**Aplicação real:** Reajuste de contratos de transporte, BDI em orçamentos de engenharia e composição de custos rodoviários.

### IFIX — Índice de Fundos de Investimento Imobiliário
**O que é:** Índice da B3 que mede a performance dos FIIs (Fundos de Investimento Imobiliário) negociados em bolsa.
**Feeder:** `downloader_b3` → `Feeders/B3/GetIndices.py`
**Aplicação real:** Benchmark para investidores em FIIs, análise de retorno do mercado imobiliário listado.

### IBOVESPA — Índice Bovespa
**O que é:** Principal índice do mercado de ações brasileiro, composto pelas ações mais negociadas na B3.
**Feeder:** `downloader_b3` → `Feeders/B3/GetIndices.py`
**Aplicação real:** Benchmark para renda variável, análise de custo de oportunidade para empreendimentos imobiliários.

### IMOB — Índice Imobiliário B3
**O que é:** Índice da B3 que mede a performance das empresas do setor imobiliário listadas em bolsa (incorporadoras, construtoras, administradoras de shoppings).
**Feeder:** `downloader_b3` → `Feeders/B3/GetIndices.py`
**Aplicação real:** Monitoramento do desempenho do setor imobiliário no mercado de capitais.

---

## Deploy

```bash
cd AzureFunctions
func azure functionapp publish func-dados-publicos-api --python
```

## Setup local

```bash
cd AzureFunctions
pip install -r requirements.txt
func start
```
