import logging
import requests
from datetime import datetime

SGS_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados"


def get_sgs_series(series_id, date_ref):
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    data_inicio = dt.strftime("01/%m/%Y")
    data_fim = dt.strftime("%d/%m/%Y")

    url = SGS_BASE.format(series=series_id)
    params = {"formato": "json", "dataInicial": data_inicio, "dataFinal": data_fim}

    logging.info(f"Fetching SGS series {series_id}: {data_inicio} to {data_fim}")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data or not isinstance(data, list):
        logging.warning(f"No data for SGS series {series_id} on {date_ref}")
        return None

    try:
        valor = float(data[-1]["valor"])
    except (KeyError, ValueError, TypeError):
        logging.warning(f"Invalid value in SGS series {series_id}: {data[-1]}")
        return None

    return {
        "periodo": dt.strftime("%Y-%m"),
        "valor": round(valor, 6),
    }
