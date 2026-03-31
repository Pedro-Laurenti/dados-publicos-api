import logging
import requests
from datetime import datetime

ANBIMA_CZ_URL = "https://anbima.com.br/informacoes/est-termo/CZ-down.asp"
ANBIMA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*",
}

BIZ_DAYS_PER_YEAR = 252
NTNB_2035_MATURITY = datetime(2035, 5, 15)


def _parse_ettj_ipca(text):
    """Extrai vertices da tabela 'ETTJ Inflacao Implicita (IPCA)' do CSV ANBIMA.

    O CSV usa Latin-1, separador ';', decimais com ',', e milhares com '.' nos vertices.
    Retorna lista de dicts: [{"du": int, "ipca": float}, ...]
    """
    lines = text.replace("\r", "").split("\n")
    in_ipca_table = False
    vertices = []

    for line in lines:
        stripped = line.strip()

        if "ETTJ" in stripped and "IPCA" in stripped:
            in_ipca_table = True
            continue

        if in_ipca_table and stripped.startswith("Vertices"):
            continue

        if in_ipca_table and stripped == "":
            if vertices:
                break
            continue

        if in_ipca_table and "PREFIXADOS" in stripped:
            break

        if in_ipca_table:
            parts = stripped.split(";")
            if len(parts) >= 2 and parts[0].strip():
                try:
                    du_str = parts[0].strip().replace(".", "")
                    du = int(du_str)
                    ipca_str = parts[1].strip().replace(",", ".")
                    if not ipca_str:
                        continue
                    ipca = float(ipca_str)
                    vertices.append({"du": du, "ipca": ipca})
                except (ValueError, IndexError):
                    continue

    return vertices


def _find_nearest_vertex(vertices, target_du):
    if not vertices:
        return None
    return min(vertices, key=lambda v: abs(v["du"] - target_du))


def _biz_days_to_maturity(dt_ref, maturity):
    years = (maturity - dt_ref).days / 365.25
    return int(years * BIZ_DAYS_PER_YEAR)


def _fetch_ettj_csv():
    response = requests.get(ANBIMA_CZ_URL, headers=ANBIMA_HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = "latin-1"
    return response.text


def get_ettj(date_ref):
    """Busca ETTJ IPCA em vertices-chave (5a e 10a) da ANBIMA.

    Nota: CZ-down.asp retorna a curva do dia corrente, nao historica.
    """
    dt = datetime.strptime(date_ref, "%Y-%m-%d")
    periodo = dt.strftime("%Y-%m")

    try:
        csv_text = _fetch_ettj_csv()
    except Exception as e:
        logging.error(f"ETTJ: error fetching ANBIMA: {e}")
        return None

    vertices = _parse_ettj_ipca(csv_text)
    if not vertices:
        logging.warning("ETTJ: no vertices parsed from ANBIMA CSV")
        return None

    logging.info(f"ETTJ: parsed {len(vertices)} vertices (DU range: {vertices[0]['du']}-{vertices[-1]['du']})")

    target_5a = 5 * BIZ_DAYS_PER_YEAR
    target_10a = 10 * BIZ_DAYS_PER_YEAR

    v5 = _find_nearest_vertex(vertices, target_5a)
    v10 = _find_nearest_vertex(vertices, target_10a)

    results = []
    if v5:
        logging.info(f"ETTJ 5a: DU={v5['du']} rate={v5['ipca']}%")
        results.append({"nome": "ettj-ipca-5a", "periodo": periodo, "valor": round(v5["ipca"], 4)})
    if v10:
        logging.info(f"ETTJ 10a: DU={v10['du']} rate={v10['ipca']}%")
        results.append({"nome": "ettj-ipca-10a", "periodo": periodo, "valor": round(v10["ipca"], 4)})

    return results


def get_ntnb_2035(date_ref):
    """Busca taxa indicativa NTN-B 2035 via ETTJ IPCA da ANBIMA.

    Interpola a curva no vertice mais proximo da maturidade 15/05/2035.
    Nota: CZ-down.asp retorna a curva do dia corrente.
    """
    dt = datetime.strptime(date_ref, "%Y-%m-%d")

    try:
        csv_text = _fetch_ettj_csv()
    except Exception as e:
        logging.error(f"NTN-B 2035: error fetching ANBIMA: {e}")
        return None

    vertices = _parse_ettj_ipca(csv_text)
    if not vertices:
        logging.warning("NTN-B 2035: no vertices parsed")
        return None

    target_du = _biz_days_to_maturity(dt, NTNB_2035_MATURITY)
    vertex = _find_nearest_vertex(vertices, target_du)

    if not vertex:
        return None

    logging.info(f"NTN-B 2035: DU={vertex['du']} (target={target_du}), rate={vertex['ipca']}%")

    return {
        "periodo": dt.strftime("%Y-%m"),
        "valor": round(vertex["ipca"], 4),
    }
