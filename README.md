# dados-publicos-api

Azure Function App para coleta automatizada de índices econômicos públicos. Focada em precificação de obras, financiamento imobiliário e acompanhamento de mercado.

**34 índices** coletados de 7 fontes oficiais: BACEN, IBGE, FGV/IBRE, B3, ANBIMA, ANP e FedNY.

Para descrição detalhada de cada índice, veja o [Glossário](GLOSSARIO.md).

---

## Consultar dados — `GET /api/indices`

| Endpoint | Descrição |
|---|---|
| `/api/indices` | Último valor de todos os índices |
| `/api/indices?nome=ipca` | Último dado do IPCA |
| `/api/indices?nome=ipca&data=2026-03-30` | IPCA coletado em 30/03/2026 (404 se não existir) |
| `/api/indices?nome=ipca&data_inicio=2026-01-01&data_fim=2026-03-31` | Histórico diário do IPCA no período |


| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `nome` | Não | Identificador do índice (tabela abaixo) |
| `data` | Não | Data exata de coleta `YYYY-MM-DD` (retorna 404 se não coletado) |
| `data_inicio` | Não | Data inicial `YYYY-MM-DD` |
| `data_fim` | Não | Data final `YYYY-MM-DD` |

### Todos os índices disponíveis

| Índice | `nome` | Unidade | Fonte |
|---|---|---|---|
| INCC-M | `incc-m` | % | FGV/IBRE |
| IGP-M | `igp-m` | % | FGV/IBRE |
| IGP-DI | `igp-di` | % | FGV/IBRE |
| IPCA | `ipca` | % | IBGE |
| INPC | `inpc` | % | IBGE |
| SINAPI | `sinapi` | % | IBGE |
| IPCA-15 | `ipca-15` | % | IBGE |
| IPCA Acumulado 12M | `ipca-acumulado-12m` | % | BACEN |
| Selic (acumulada) | `selic` | % a.a. | BACEN |
| Selic Meta | `selic-meta` | % a.a. | BACEN |
| CDI | `cdi` | % a.m. | BACEN |
| Juros Real | `juros-real` | % a.a. | BACEN |
| TR | `tr` | % a.m. | BACEN |
| TJLP | `tjlp` | % a.a. | BACEN |
| Poupança (rendimento) | `poupanca` | % a.m. | BACEN |
| PTAX USD | `ptax-usd` | R$/USD | BACEN |
| Taxa Financ. Imob. PF | `taxa-financ-imob-pf` | % a.m. | BACEN |
| SBPE contratações valor | `sbpe-contratacoes-valor` | R$ mil | BACEN |
| SBPE contratações unidades | `sbpe-contratacoes-unidades` | unidades | BACEN |
| SBPE saldo poupança | `sbpe-saldo-poupanca` | R$ bi | BACEN |
| NTN-B 2035 | `ntn-b-2035` | % a.a. | ANBIMA |
| ETTJ IPCA 5 anos | `ettj-ipca-5a` | % a.a. | ANBIMA |
| ETTJ IPCA 10 anos | `ettj-ipca-10a` | % a.a. | ANBIMA |
| IFIX | `ifix` | pts | B3 |
| IBOVESPA | `ibovespa` | pts | B3 |
| IMOB | `imob` | pts | B3 |
| SMLL | `smll` | pts | B3 |
| IDIV | `idiv` | pts | B3 |
| IFNC | `ifnc` | pts | B3 |
| PIB Trimestral | `pib-trimestral` | % | IBGE |
| Insumos Construção Civil | `insumos-construcao-civil` | índice (2022=100) | IBGE |
| Metalurgia | `metalurgia` | índice (2022=100) | IBGE |
| ANP Diesel | `anp-diesel` | R$/litro | ANP |
| SOFR | `sofr` | % a.a. | FedNY |

---

## Forçar coleta — `GET /api/downloader_http`

```
/api/downloader_http?downloader=bacen&date=2026-03-30
```

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `downloader` | Sim | Nome do downloader (tabela abaixo) |
| `date` | Sim | Data de referência `YYYY-MM-DD` |

### Qual downloader usar para cada índice

| Índice | `nome` | `downloader` | Observação |
|---|---|---|---|
| INCC-M | `incc-m` | `fgv` | |
| IGP-M | `igp-m` | `fgv` | |
| IGP-DI | `igp-di` | `fgv` | |
| IPCA | `ipca` | `ibge` | |
| INPC | `inpc` | `ibge` | |
| SINAPI | `sinapi` | `ibge` | |
| IPCA-15 | `ipca-15` | `ibge` | |
| PIB Trimestral | `pib-trimestral` | `ibge` | RowKey = último mês do trimestre |
| Insumos Construção Civil | `insumos-construcao-civil` | `ibge` | Proxy cimento (IBGE PIM-PF) |
| Metalurgia | `metalurgia` | `ibge` | Proxy aço longo (IBGE PIM-PF) |
| Selic (acumulada) | `selic` | `bacen` | |
| Selic Meta | `selic-meta` | `bacen` | |
| CDI | `cdi` | `bacen` | |
| Juros Real | `juros-real` | `bacen` | Calculado: CDI 12M deflac. IPCA |
| TR | `tr` | `bacen` | |
| TJLP | `tjlp` | `bacen` | |
| Poupança (rendimento) | `poupanca` | `bacen` | |
| PTAX USD | `ptax-usd` | `bacen` | |
| Taxa Financ. Imob. PF | `taxa-financ-imob-pf` | `bacen` | |
| IPCA Acumulado 12M | `ipca-acumulado-12m` | `bacen` | |
| SBPE contratações valor | `sbpe-contratacoes-valor` | `bacen` | |
| SBPE contratações unidades | `sbpe-contratacoes-unidades` | `bacen` | |
| SBPE saldo poupança | `sbpe-saldo-poupanca` | `bacen` | Defasagem ~6-9 meses |
| NTN-B 2035 | `ntn-b-2035` | `anbima` | Via ETTJ IPCA |
| ETTJ IPCA 5 anos | `ettj-ipca-5a` | `anbima` | Curva do dia corrente |
| ETTJ IPCA 10 anos | `ettj-ipca-10a` | `anbima` | Curva do dia corrente |
| IFIX | `ifix` | `b3` | Apenas último dia do mês |
| IBOVESPA | `ibovespa` | `b3` | Apenas último dia do mês |
| IMOB | `imob` | `b3` | Apenas último dia do mês |
| SMLL | `smll` | `b3` | Apenas último dia do mês |
| IDIV | `idiv` | `b3` | Apenas último dia do mês |
| IFNC | `ifnc` | `b3` | Apenas último dia do mês |
| ANP Diesel | `anp-diesel` | `anp` | |
| SOFR | `sofr` | `sofr` | |

---

## Infraestrutura Azure

| Recurso | Nome |
|---|---|
| Resource Group | `rg-dados-publicos-api` |
| Function App | `func-dados-publicos-api` (Flex Consumption, Python 3.11) |
| Storage Account | `stdadospublicosapi` (Standard_LRS) |
| Table Storage | `IndicesPublicos` |

### Autenticação

100% Managed Identity (System-Assigned) com RBAC. Nenhuma connection string.

| Role | Finalidade |
|---|---|
| Storage Blob Data Owner | Runtime Azure Functions |
| Storage Queue Data Contributor | Runtime Azure Functions |
| Storage Table Data Contributor | Leitura/escrita na tabela IndicesPublicos |

### Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `AzureWebJobsStorage__accountName` | Storage Account (identity-based) |
| `DADPUBAPI_STORAGE_TABLE_URL` | URL do Table endpoint |
| `DADPUBAPI_FGV_USER` | Usuário FGV/IBRE |
| `DADPUBAPI_FGV_PASSWORD` | Senha FGV/IBRE |

---

## Timers automáticos

| Downloader | Schedule (CRON UTC) | Índices |
|---|---|---|
| `downloader_fgv` | `0 0 8 * * *` (diário 08h) | INCC-M, IGP-M, IGP-DI |
| `downloader_ibge` | `0 0 9 * * *` (diário 09h) | IPCA, INPC, SINAPI, IPCA-15, PIB, Insumos, Metalurgia |
| `downloader_bacen` | `0 0 18 * * *` (diário 18h) | Selic, CDI, PTAX, TR, TJLP, SBPE, Juros Real, etc. |
| `downloader_anp` | `0 0 10 * * 1` (segunda 10h) | ANP Diesel |
| `downloader_b3` | `0 0 22 28,29,30,31 * *` (dias 28-31 22h) | IFIX, IBOV, IMOB, SMLL, IDIV, IFNC |
| `downloader_anbima` | `0 0 18 * * *` (diário 18h) | NTN-B 2035, ETTJ IPCA 5a, ETTJ IPCA 10a |
| `downloader_sofr` | `0 0 18 * * *` (diário 18h) | SOFR |
