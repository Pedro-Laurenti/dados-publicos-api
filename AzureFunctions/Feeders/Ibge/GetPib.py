import logging
import time
import requests
from datetime import datetime

SIDRA_PIB_URL = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/5932/periodos/{periodo}"
    "/variaveis/6561?localidades=N1[all]&classificacao=11255[90707]"
)

MAX_QUARTERS_BACK = 6
MAX_RETRIES = 3


def _quarter_of(dt):
    return (dt.month - 1) // 3 + 1


def _prev_quarter(year, quarter):
    quarter -= 1
    if quarter == 0:
        return year - 1, 4
    return year, quarter


def _periodo_code(year, quarter):
    return f"{year}0{quarter}"


def _row_key(year, quarter):
    last_month = quarter * 3
    return f"{year}-{last_month:02d}"


def _fetch_pib(periodo):
    url = SIDRA_PIB_URL.format(periodo=periodo)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            serie = data[0]["resultados"][0]["series"][0]["serie"]
            valor_str = serie.get(periodo)
            if valor_str and valor_str not in ("..", "...", "-", "", None):
                return float(valor_str)
            return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            logging.warning(f"PIB request attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(3 * attempt)
        except (KeyError, IndexError, ValueError):
            return None
    return None


def get_pib(date_ref):
    """Fetches PIB trimestral (taxa YoY %) from IBGE SIDRA aggregate 5932.

    Tries the current quarter and up to MAX_QUARTERS_BACK previous ones.
    Returns {"periodo": "YYYY-MM", "valor": float} or None.
    The periodo RowKey is the last month of the quarter (Q1→03, Q2→06, Q3→09, Q4→12).
    """
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    year, quarter = dt.year, _quarter_of(dt)

    for _ in range(MAX_QUARTERS_BACK):
        periodo = _periodo_code(year, quarter)
        logging.info(f"Fetching PIB for {periodo}")
        valor = _fetch_pib(periodo)
        if valor is not None:
            return {"periodo": _row_key(year, quarter), "valor": round(valor, 2)}
        logging.info(f"PIB: no data for {periodo}, trying previous quarter")
        year, quarter = _prev_quarter(year, quarter)

    logging.warning(f"No PIB data found in the last {MAX_QUARTERS_BACK} quarters")
    return None
