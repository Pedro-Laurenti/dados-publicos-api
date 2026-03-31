import azure.functions as func
import logging
import re
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import INCC_M, IGP_M, IGP_DI, FONTE_FGV, UNIDADE_PERCENTUAL
from Feeders.Fgv.GetIncc import get_hist_incc
from Feeders.Fgv.GetIgpm import get_hist_igpm
from Feeders.Fgv.GetIgpdi import get_hist_igpdi

configure_logging()

INDICES_FGV = {
    INCC_M: get_hist_incc,
    IGP_M: get_hist_igpm,
    IGP_DI: get_hist_igpdi,
}

MESES_PT = {
    "jan": "01", "fev": "02", "mar": "03", "abr": "04",
    "mai": "05", "jun": "06", "jul": "07", "ago": "08",
    "set": "09", "out": "10", "nov": "11", "dez": "12",
}


def _parse_dt_ref(dt_ref):
    dt_ref = str(dt_ref).strip().lower()
    match = re.match(r"(\w{3})/(\d{4})", dt_ref)
    if match:
        mes_abrev, ano = match.groups()
        mes_num = MESES_PT.get(mes_abrev)
        if mes_num:
            return f"{ano}-{mes_num}"
    if re.match(r"\d{4}-\d{2}", dt_ref):
        return dt_ref[:7]
    match = re.match(r"(\d{2})/(\d{4})", dt_ref)
    if match:
        mes, ano = match.groups()
        return f"{ano}-{mes}"
    logging.warning(f"Could not parse dt_ref: {dt_ref}")
    return None


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    for indice_name, fetch_fn in INDICES_FGV.items():
        try:
            logging.info(f"Collecting {indice_name}")
            df = fetch_fn()
            if df is None or df.empty:
                logging.warning(f"No data for {indice_name}")
                continue

            last_row = df.iloc[-1]
            valor = last_row[indice_name]
            try:
                valor = float(valor)
            except (ValueError, TypeError):
                logging.warning(f"{indice_name}: invalid last value {valor}")
                continue

            periodo = _parse_dt_ref(last_row["dt_ref"])
            if not periodo:
                continue

            storage.upsert_indice(
                partition_key=indice_name,
                row_key=today,
                valor=valor,
                periodo=periodo,
                fonte=FONTE_FGV,
                unidade=UNIDADE_PERCENTUAL,
            )
            logging.info(f"{indice_name}: {today} = {valor} (periodo={periodo})")
        except Exception as e:
            logging.error(f"Error collecting {indice_name}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_fgv ran at {utc_timestamp}")
    execute()
