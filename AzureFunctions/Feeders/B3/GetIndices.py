import logging
import requests
from datetime import datetime

B3_QUOTATION_URL = "https://cotacao.b3.com.br/mds/api/v1/InstrumentQuotation/{symbol}"
B3_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.b3.com.br/",
    "Accept": "application/json",
}


def get_b3_index(symbol, date_ref):
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    url = B3_QUOTATION_URL.format(symbol=symbol)
    logging.info(f"Fetching B3 index {symbol}: {url}")

    response = requests.get(url, headers=B3_HEADERS, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("BizSts", {}).get("cd") != "OK":
        logging.warning(f"B3 API returned non-OK status for {symbol}: {data}")
        return None

    trades = data.get("Trad", [])
    if not trades:
        logging.warning(f"No quotation data for B3 symbol {symbol}")
        return None

    try:
        valor = float(trades[0]["scty"]["SctyQtn"]["curPrc"])
    except (KeyError, ValueError, TypeError) as e:
        logging.warning(f"Could not extract price for {symbol}: {e}")
        return None

    return {
        "periodo": dt.strftime("%Y-%m"),
        "valor": round(valor, 2),
    }
