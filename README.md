# dados-publicos-api

Azure Function App Python para coleta e consulta de índices públicos para precificação de obras de engenharia civil.

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

| Índice | Fonte | Periodicidade | Trigger |
|---|---|---|---|
| INCC-M | FGV/IBRE | Mensal | `downloader_fgv` (diário 08h UTC) |
| IGP-M | FGV/IBRE | Mensal | `downloader_fgv` (diário 08h UTC) |
| IGP-DI | FGV/IBRE | Mensal | `downloader_fgv` (diário 08h UTC) |
| IPCA | IBGE SIDRA | Mensal | `downloader_ibge` (diário 09h UTC) |
| INPC | IBGE SIDRA | Mensal | `downloader_ibge` (diário 09h UTC) |
| SINAPI | IBGE SIDRA | Mensal | `downloader_ibge` (diário 09h UTC) |
| Selic | BACEN SGS | Diária/Mensal | `downloader_bacen` (diário 18h UTC) |
| ANP Diesel | ANP | Semanal | `downloader_anp` (segunda 10h UTC) |

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
| `nome` | Não | Nome do índice (ex: `incc-m`, `ipca`, `selic`) |
| `data_inicio` | Não | Período inicial `YYYY-MM` |
| `data_fim` | Não | Período final `YYYY-MM` |

Sem parâmetros retorna o último valor de cada índice. Com `nome` retorna o último valor daquele índice. Com `nome` + datas retorna o histórico no intervalo.

### GET `/api/downloader_http`

Disparo forçado de coleta por data.

```
https://func-dados-publicos-api.azurewebsites.net/api/downloader_http?downloader=ibge&date=2026-03-27
```

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `downloader` | Sim | Nome do downloader: `fgv`, `ibge`, `bacen`, `anp` |
| `date` | Sim | Data de referência `YYYY-MM-DD` |

## Variáveis de ambiente

Centralizadas em `config.py`. Padrão: `DADPUBAPI_[FUNCAO]_[NOME]`.

| Variável | Descrição |
|---|---|
| `AzureWebJobsStorage__accountName` | Storage Account (identity-based, runtime) |
| `DADPUBAPI_STORAGE_TABLE_URL` | URL do Table endpoint (identity-based, aplicação) |
| `DADPUBAPI_FGV_USER` | Usuário FGV/IBRE |
| `DADPUBAPI_FGV_PASSWORD` | Senha FGV/IBRE |

## Glossário dos índices

> Seção educativa — o que é cada índice, quem o coleta e onde é usado na prática.

### INCC-M — Índice Nacional de Custo da Construção (Mensal)
**O que é:** Mede a variação dos custos de construção civil no Brasil. Composto por mão de obra e materiais de construção.  
**Feeder:** `downloader_fgv` → `Feeders/Fgv/GetIncc.py`  
**Aplicação real:** Reajuste de contratos de obras e incorporações imobiliárias (ex.: contratos de compra de imóvel na planta — o saldo devedor é corrigido mensalmente pelo INCC-M até a entrega das chaves).

### IGP-M — Índice Geral de Preços do Mercado
**O que é:** Média ponderada de três sub-índices: IPA-M (60% — preços no atacado), IPC-M (30% — preços ao consumidor) e INCC-M (10% — custo da construção).  
**Feeder:** `downloader_fgv` → `Feeders/Fgv/GetIgpm.py`  
**Aplicação real:** Reajuste de aluguéis residenciais e comerciais, tarifas de energia elétrica e contratos de longo prazo com cláusula de correção monetária.

### IGP-DI — Índice Geral de Preços — Disponibilidade Interna
**O que é:** Mesma metodologia do IGP-M, mas com coleta em período diferente (dia 1 ao dia 30 do mês, enquanto o IGP-M vai do dia 21 ao 20). Reflete melhor o preço "dentro" do mercado doméstico.  
**Feeder:** `downloader_fgv` → `Feeders/Fgv/GetIgpdi.py`  
**Aplicação real:** Correção de contratos de obras públicas de infraestrutura, debêntures e alguns financiamentos do BNDES.

### IPCA — Índice Nacional de Preços ao Consumidor Amplo
**O que é:** Inflação oficial do Brasil. Mede a variação de preços de uma cesta de bens e serviços consumidos por famílias com renda de 1 a 40 salários mínimos.  
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetIndicadores.py`  
**Aplicação real:** Meta de inflação do Banco Central, correção do Tesouro IPCA+ (NTN-B), reajuste de planos de saúde e referência para contratos indexados à inflação.

### INPC — Índice Nacional de Preços ao Consumidor
**O que é:** Similar ao IPCA, mas focado em famílias de menor renda (1 a 5 salários mínimos). Tende a ser mais sensível a alimentos e transporte público.  
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetIndicadores.py`  
**Aplicação real:** Reajuste do salário mínimo, benefícios previdenciários e dissídios coletivos de trabalhadores.

### SINAPI — Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil
**O que é:** Pesquisa mensal do IBGE em parceria com a Caixa Econômica Federal que apura preços de insumos e custos de mão de obra na construção civil, por estado.  
**Feeder:** `downloader_ibge` → `Feeders/Ibge/GetIndicadores.py`  
**Aplicação real:** Referência obrigatória para orçamentos e medições de obras financiadas com recursos públicos federais (PAC, Minha Casa Minha Vida, licitações da Lei 14.133/2021).

### Selic — Taxa do Sistema Especial de Liquidação e Custódia
**O que é:** Taxa básica de juros da economia brasileira, definida pelo COPOM (Banco Central) a cada 45 dias. Remunera títulos públicos federais.  
**Feeder:** `downloader_bacen` → `Feeders/Bacen/GetSelic.py`  
**Aplicação real:** Referência para toda a cadeia de crédito (CDI, juros bancários, financiamentos), correção de dívidas tributárias e rendimento de aplicações como Tesouro Selic.

### ANP Diesel — Preço médio do Diesel (ANP)
**O que é:** Levantamento semanal da Agência Nacional do Petróleo com o preço médio de revenda do diesel (ao consumidor) por estado e município.  
**Feeder:** `downloader_anp` → `Feeders/Anp/GetDiesel.py`  
**Aplicação real:** Reajuste de contratos de transporte de cargas e obras, cálculo de BDI (Benefícios e Despesas Indiretas) em orçamentos de engenharia e planilhas de composição de custos rodoviários.

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
