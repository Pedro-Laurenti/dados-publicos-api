import logging
import requests
import pandas as pd
from io import StringIO
from io import BytesIO
from datetime import datetime
from bs4 import BeautifulSoup

ANP_PAGE_URL = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
    "serie-historica-de-precos-de-combustiveis"
)

DIESEL_CSV_KEYWORDS = ["diesel", "ca-", "combustiveis-automotivos", "combustivel"]


def _find_diesel_csv_url(page_url):
    logging.info(f"Fetching ANP page: {page_url}")
    response = requests.get(page_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    csv_links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if not href.endswith(".csv"):
            continue
        href_lower = href.lower()
        for keyword in DIESEL_CSV_KEYWORDS:
            if keyword in href_lower:
                csv_links.append(href)
                break

    if not csv_links:
        raise Exception(f"No diesel CSV found on ANP page. Available CSVs: {[a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.csv')][:10]}")

    csv_links.sort(reverse=True)
    return csv_links[0]


def _try_parse_csv(content, encoding="utf-8"):
    for sep in [";", ",", "\t"]:
        try:
            df = pd.read_csv(StringIO(content), sep=sep, decimal=",", encoding=encoding)
            if len(df.columns) > 3:
                return df
        except Exception:
            continue
    raise Exception("Failed to parse ANP CSV with any separator")


def get_diesel(date_ref):
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    periodo = dt.strftime("%Y-%m")

    csv_url = _find_diesel_csv_url(ANP_PAGE_URL)
    logging.info(f"Downloading ANP CSV: {csv_url}")

    response = requests.get(csv_url, timeout=120)
    response.raise_for_status()

    try:
        text = response.content.decode("utf-8")
    except UnicodeDecodeError:
        text = response.content.decode("latin-1")

    df = _try_parse_csv(text)
    logging.info(f"ANP CSV columns: {list(df.columns)}")

    col_produto = next((c for c in df.columns if "produto" in c.lower()), None)
    col_preco = next((c for c in df.columns if "revenda" in c.lower() and ("edio" in c.lower() or "media" in c.lower())), None)
    col_data = next((c for c in df.columns if "data" in c.lower()), None)

    if not all([col_produto, col_preco, col_data]):
        logging.error(f"Missing expected columns. Found: {list(df.columns)}")
        return None

    diesel = df[df[col_produto].str.contains("DIESEL", case=False, na=False)].copy()
    diesel[col_data] = pd.to_datetime(diesel[col_data], dayfirst=True, errors="coerce")
    diesel = diesel.dropna(subset=[col_data])
    diesel = diesel[diesel[col_data].dt.strftime("%Y-%m") == periodo]

    if diesel.empty:
        available_periods = df[col_data].dropna().unique()[:5]
        logging.warning(f"No ANP diesel data for {periodo}. Sample periods in CSV: {available_periods}")
        return None

    preco_medio = pd.to_numeric(diesel[col_preco], errors="coerce").dropna().mean()

    return {
        "periodo": periodo,
        "valor": round(preco_medio, 4),
    }
