import logging
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

SGS_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series}/dados"
SGS_CDI_MENSAL = 4391
SGS_IPCA_ACUM_12M = 13522


def _fetch_sgs_range(series_id, dt_start, dt_end):
    url = SGS_BASE.format(series=series_id)
    params = {
        "formato": "json",
        "dataInicial": dt_start.strftime("01/%m/%Y"),
        "dataFinal": dt_end.strftime("%d/%m/%Y"),
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data or not isinstance(data, list):
        return []
    return data


def _fetch_sgs_last(series_id, dt_start, dt_end):
    data = _fetch_sgs_range(series_id, dt_start, dt_end)
    if not data:
        return None
    return float(data[-1]["valor"])


def get_juros_real(date_ref):
    """Calcula Juros Real = ((1+CDI_12m) / (1+IPCA_12m) - 1) * 100.

    Compoe os ultimos 12 meses de CDI mensal (SGS 4391) e usa
    IPCA acumulado 12M (SGS 13522) para deflacionar.
    Metodologia REMO: CDI a.a. deflacionado pelo IPCA.
    Retorna {"periodo": "YYYY-MM", "valor": float} ou None.
    """
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    dt_start = dt - relativedelta(months=11)

    try:
        cdi_data = _fetch_sgs_range(SGS_CDI_MENSAL, dt_start, dt)
        ipca_12m = _fetch_sgs_last(SGS_IPCA_ACUM_12M, dt_start, dt)
    except Exception as e:
        logging.error(f"Juros Real: error fetching SGS data: {e}")
        return None

    if len(cdi_data) < 10:
        logging.warning(f"Juros Real: insufficient CDI data ({len(cdi_data)} months)")
        return None

    if ipca_12m is None:
        logging.warning("Juros Real: no IPCA 12M data available")
        return None

    cdi_compound = 1.0
    for item in cdi_data:
        cdi_compound *= 1 + float(item["valor"]) / 100

    juros_real = (cdi_compound / (1 + ipca_12m / 100) - 1) * 100

    return {
        "periodo": dt.strftime("%Y-%m"),
        "valor": round(juros_real, 2),
    }
