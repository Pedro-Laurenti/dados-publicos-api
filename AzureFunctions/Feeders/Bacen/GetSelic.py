import logging
import requests
from datetime import datetime

SELIC_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"


def get_selic(date_ref):
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    data_inicio = dt.strftime("01/%m/%Y")
    data_fim = dt.strftime("%d/%m/%Y")

    params = {
        "formato": "json",
        "dataInicial": data_inicio,
        "dataFinal": data_fim,
    }

    logging.info(f"Fetching Selic: {data_inicio} to {data_fim}")
    response = requests.get(SELIC_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data:
        logging.warning(f"No Selic data for {date_ref}")
        return None

    acumulado = sum(float(d["valor"]) for d in data)
    periodo = dt.strftime("%Y-%m")

    return {
        "periodo": periodo,
        "valor": round(acumulado, 4),
    }
