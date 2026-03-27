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
