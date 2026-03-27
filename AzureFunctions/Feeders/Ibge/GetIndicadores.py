import logging
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

SIDRA_BASE = "https://servicodados.ibge.gov.br/api/v3/agregados"

INDICADORES = {
    "ipca": {"agregado": "1737", "variavel": "2266"},
    "inpc": {"agregado": "1736", "variavel": "44"},
    "sinapi": {"agregado": "2296", "variavel": "1198"},
}

MAX_MONTHS_BACK = 6


def _build_url(config, periodo):
    return (
        f"{SIDRA_BASE}/{config['agregado']}/periodos/{periodo}"
        f"/variaveis/{config['variavel']}?localidades=N1[all]"
    )


def _try_fetch(config, nome, dt):
    periodo = dt.strftime("%Y%m")
    url = _build_url(config, periodo)
    logging.info(f"Fetching {nome}: {url}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data or not isinstance(data, list) or len(data) == 0:
        return None

    try:
        resultados = data[0]["resultados"][0]["series"][0]["serie"]
    except (KeyError, IndexError):
        return None

    if periodo not in resultados:
        return None

    valor_str = resultados[periodo]
    if valor_str in ("...", "-", "", None):
        return None

    return {
        "periodo": dt.strftime("%Y-%m"),
        "valor": float(valor_str),
    }


def get_indicador(nome, date_ref):
    if nome not in INDICADORES:
        raise ValueError(f"Indicador desconhecido: {nome}")

    config = INDICADORES[nome]
    dt = datetime.strptime(date_ref, "%Y-%m-%d")

    for i in range(MAX_MONTHS_BACK):
        target = dt - relativedelta(months=i)
        result = _try_fetch(config, nome, target)
        if result:
            return result
        logging.info(f"{nome}: no data for {target.strftime('%Y-%m')}, trying previous month")

    logging.warning(f"No data found for {nome} in the last {MAX_MONTHS_BACK} months")
    return None
