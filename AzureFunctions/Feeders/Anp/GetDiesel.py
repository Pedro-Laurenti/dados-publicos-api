import logging
import requests
import pandas as pd
from io import StringIO
from datetime import datetime
from bs4 import BeautifulSoup

ANP_PAGE_URL = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
    "serie-historica-de-precos-de-combustiveis"
)

DIESEL_CSV_KEYWORDS = ["diesel", "ca-", "combustiveis-automotivos"]


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
        if any(kw in href_lower for kw in DIESEL_CSV_KEYWORDS):
            csv_links.append(href)

    if not csv_links:
        all_csvs = [a["href"] for a in soup.find_all("a", href=True) if a["href"].endswith(".csv")]
        logging.warning(f"No diesel-specific CSV found. All CSVs: {all_csvs[:10]}")
        raise Exception("No diesel CSV found on ANP page")

    csv_links.sort(reverse=True)
    return csv_links[0]


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

    df = pd.read_csv(StringIO(text), sep=";", decimal=",")
    logging.info(f"ANP CSV columns: {list(df.columns)}, rows: {len(df)}")

    col_produto = next((c for c in df.columns if "produto" in c.lower()), None)
    col_data = next((c for c in df.columns if "data" in c.lower()), None)
    col_preco = next((c for c in df.columns if "valor de venda" in c.lower()), None)
    if not col_preco:
        col_preco = next((c for c in df.columns if "valor" in c.lower() and "compra" not in c.lower()), None)

    if not all([col_produto, col_preco, col_data]):
        logging.error(f"Missing columns. Need produto/data/preco. Found: {list(df.columns)}")
        return None

    logging.info(f"Using columns: produto={col_produto}, data={col_data}, preco={col_preco}")

    diesel = df[df[col_produto].str.contains("DIESEL", case=False, na=False)].copy()
    if diesel.empty:
        logging.warning(f"No DIESEL rows found. Products: {df[col_produto].unique()[:10]}")
        return None

    diesel[col_data] = pd.to_datetime(diesel[col_data], dayfirst=True, errors="coerce")
    diesel = diesel.dropna(subset=[col_data])
    diesel = diesel[diesel[col_data].dt.strftime("%Y-%m") == periodo]

    if diesel.empty:
        logging.warning(f"No ANP diesel data for {periodo}")
        return None

    preco_medio = pd.to_numeric(
        diesel[col_preco].astype(str).str.replace(",", "."), errors="coerce"
    ).dropna().mean()

    if pd.isna(preco_medio):
        logging.warning(f"Could not compute mean price for {periodo}")
        return None

    return {
        "periodo": periodo,
        "valor": round(preco_medio, 4),
    }
