---
description: Step-by-step guide to add a new economic indicator to dados-publicos-api.
applyTo: "**/*.py"
---

# How to Add a New Indicator

## Architecture Overview

```
AzureFunctions/
├── Constants/Indices.py          ← all indicator keys and constants
├── config.py                     ← all env vars (DADPUBAPI_* prefix)
├── Storage/TableStorageClient.py ← Azure Table Storage (upsert/query)
├── Feeders/<Source>/             ← data fetching logic per source
│   └── Get<Indicator>.py
├── downloader_<source>/          ← timer trigger (scheduled)
│   ├── __init__.py
│   └── function.json
└── downloader_http/__init__.py   ← HTTP trigger (manual/on-demand)
```

**Storage schema** — Azure Table Storage `IndicesPublicos`:
| Field | Type | Example |
|---|---|---|
| PartitionKey | string | `"ipca"` |
| RowKey | string | `"2026-01"` (YYYY-MM) |
| valor | float | `0.33` |
| data_divulgacao | string | `"2026-03-27"` |
| fonte | string | `"IBGE"` |
| unidade | string | `"%"` |

**RowKey rule**: must be `YYYY-MM`. Never use `/` or special chars — Azure Table Storage rejects them.

---

## Step-by-Step

### 1. Add constants in `Constants/Indices.py`

```python
MY_INDICATOR = "my-indicator"           # partition key in Table Storage
FONTE_MY_SOURCE = "My Source Name"      # source label
UNIDADE_MY_UNIT = "unit"               # e.g. "%", "R$", "% a.a.", "pts"
```

### 2. Create the Feeder in `Feeders/<Source>/Get<Indicator>.py`

The feeder must expose a single function: `get_<indicator>(date_ref: str) -> dict | None`

```python
def get_my_indicator(date_ref):
    # date_ref format: "YYYY-MM-DD"
    # returns: {"periodo": "YYYY-MM", "valor": float} or None
```

Rules:
- Handle HTTP errors, timeouts, and empty responses gracefully (return `None`)
- Add retry with backoff for external HTTP calls (see `Feeders/Ibge/GetIndicadores.py`)
- Try previous months if current month data is not yet published
- Log progress with `logging.info/warning/error`

### 3. Create the Timer Trigger `downloader_<source>/`

**`function.json`**:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "mytimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 10 * * 1"
    }
  ]
}
```
Schedule examples: `"0 0 10 1 * *"` (1st of month), `"0 0 10 * * 1"` (every Monday).

**`__init__.py`**:
```python
import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import MY_INDICATOR, FONTE_MY_SOURCE, UNIDADE_MY_UNIT
from Feeders.MySource.GetMyIndicator import get_my_indicator

configure_logging()

def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")
    try:
        result = get_my_indicator(today)
        if result:
            storage.upsert_indice(
                partition_key=MY_INDICATOR,
                row_key=result["periodo"],
                valor=result["valor"],
                data_divulgacao=today,
                fonte=FONTE_MY_SOURCE,
                unidade=UNIDADE_MY_UNIT,
            )
            logging.info(f"{MY_INDICATOR}: upserted {result['periodo']} = {result['valor']}")
    except Exception as e:
        logging.error(f"Error collecting {MY_INDICATOR}: {e}")

def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_<source> ran at {utc_timestamp}")
    execute()
```

### 4. Register in `downloader_http/__init__.py`

Add the new module to the `MODULES` dict:

```python
from downloader_<source> import execute as execute_<source>

MODULES = {
    ...
    "<source>": execute_<source>,
}
```

### 5. Add env vars to `config.py` (if needed)

Only if the feeder requires credentials or config:

```python
DADPUBAPI_MYSOURCE_USER = os.environ.get("DADPUBAPI_MYSOURCE_USER", "")
DADPUBAPI_MYSOURCE_PASSWORD = os.environ.get("DADPUBAPI_MYSOURCE_PASSWORD", "")
```

Then set them in Azure:
```bash
az functionapp config appsettings set \
  --name func-dados-publicos-api \
  --resource-group rg-dados-publicos-api \
  --settings DADPUBAPI_MYSOURCE_USER="..." DADPUBAPI_MYSOURCE_PASSWORD="..."
```

### 6. Deploy

```bash
cd /home/pedro/DEV/dados-publicos-api/AzureFunctions
func azure functionapp publish func-dados-publicos-api --python
```

### 7. Test via HTTP endpoint

```
GET https://func-dados-publicos-api.azurewebsites.net/api/downloader_http?modulo=<source>&data=YYYY-MM-DD
```

Then query the result:
```
GET https://func-dados-publicos-api.azurewebsites.net/api/indices?nome=my-indicator
```

---

## Available Data Sources (Public APIs)

| Source | Base URL | Auth |
|---|---|---|
| BACEN SGS | `https://api.bcb.gov.br/dados/serie/bcdata.sgs.{id}/dados` | None |
| IBGE SIDRA | `https://servicodados.ibge.gov.br/api/v3/agregados` | None |
| FGV/IBRE | session-based scraping | `DADPUBAPI_FGV_USER` + `DADPUBAPI_FGV_PASSWORD` |
| ANP | `https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/` | None |
| B3 Quotation | `https://cotacao.b3.com.br/mds/api/v1/InstrumentQuotation/{symbol}` | None (headers required) |

### BACEN SGS — Confirmed Series IDs

| Indicator | Series ID | Unit | Frequency |
|---|---|---|---|
| Selic diária acumulada | 11 | % a.a. | daily |
| CDI mensal acumulado | 4391 | % a.m. | monthly |
| PTAX USD (média mensal) | 3696 | R$/USD | monthly |
| Taxa financ. imob. PF | 25497 | % a.m. | monthly |

**Note on SBPE series:** SBPE housing finance series (poupança saldo, contratações valor/unidades) do not appear to be publicly available in SGS. Tested IDs 20004, 7445, 7444, 7681, 7682 — all returned 404. The BACEN public series catalog mixes SBPE data with regional credit aggregates under different IDs that are not easily discoverable via API.

### IBGE SIDRA — Confirmed Aggregates

| Indicator | Aggregate | Variable | Classification | Period Format | Unit |
|---|---|---|---|---|---|
| IPCA | 1737 | 2266 | — | YYYYMM | % |
| INPC | 1736 | 44 | — | YYYYMM | % |
| SINAPI | 2296 | 1198 | — | YYYYMM | % |
| PIB Trimestral (YoY) | 5932 | 6561 | `11255[90707]` | `YYYY0Q` (e.g. `202404` = Q4) | % |

**PIB period → RowKey mapping:** Quarter last month — Q1→03, Q2→06, Q3→09, Q4→12. Published with ~2 month lag.

Example PIB URL:
```
https://servicodados.ibge.gov.br/api/v3/agregados/5932/periodos/202404/variaveis/6561?localidades=N1[all]&classificacao=11255[90707]
```

### B3 InstrumentQuotation — Confirmed Symbols

Returns current-day closing price. **Must be called after market close (after 21:00 UTC)**.

| Indicator | Symbol | Unit |
|---|---|---|
| IFIX (FII index) | `IFIX` | pts |
| IBOVESPA | `IBOV` | pts |
| IMOB (real estate index) | `IMOB` | pts |

Required HTTP headers:
```python
{"User-Agent": "Mozilla/5.0 ...", "Referer": "https://www.b3.com.br/", "Accept": "application/json"}
```

Response path for value: `data["Trad"][0]["scty"]["SctyQtn"]["curPrc"]`

### B3 Timer — Last-Day-of-Month Pattern

B3 indices represent end-of-month closing values. Use this schedule + guard:

```python
# function.json schedule: "0 0 22 28,29,30,31 * *"
# __init__.py guard:
def _is_last_day_of_month(dt):
    return (dt + timedelta(days=1)).day == 1
```

---

## Checklist

- [ ] Constant added to `Constants/Indices.py`
- [ ] Feeder returns `{"periodo": "YYYY-MM", "valor": float}` or `None`
- [ ] Timer trigger created with correct schedule
- [ ] Module registered in `downloader_http/__init__.py`
- [ ] Env vars added to `config.py` and set in Azure (if applicable)
- [ ] Deployed and tested via HTTP endpoint
