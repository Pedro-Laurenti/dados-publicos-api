import logging
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

FEDNY_URL = "https://markets.newyorkfed.org/api/rates/secured/all/search.json"
MAX_MONTHS_BACK = 3


def get_sofr(date_ref):
    """Fetches the latest SOFR rate from the NY Fed API for the given month.

    Tries current month and up to MAX_MONTHS_BACK previous months.
    Returns {"periodo": "YYYY-MM", "valor": float} or None.
    """
    dt = datetime.strptime(date_ref, "%Y-%m-%d")

    for i in range(MAX_MONTHS_BACK):
        target = dt - relativedelta(months=i)
        start = target.replace(day=1).strftime("%Y-%m-%d")
        end = target.strftime("%Y-%m-%d") if i == 0 else target.strftime("%Y-%m-28")

        try:
            response = requests.get(
                FEDNY_URL,
                params={"startDate": start, "endDate": end, "type": "rate"},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            rates = data.get("refRates", [])
            sofr_rates = [r for r in rates if r.get("type") == "SOFR"]
            if not sofr_rates:
                logging.info(f"SOFR: no data for {target.strftime('%Y-%m')}")
                continue

            last = sofr_rates[-1]
            valor = float(last["percentRate"])
            return {
                "periodo": target.strftime("%Y-%m"),
                "valor": round(valor, 4),
            }
        except Exception as e:
            logging.warning(f"SOFR error for {target.strftime('%Y-%m')}: {e}")

    logging.warning(f"No SOFR data found in the last {MAX_MONTHS_BACK} months")
    return None
