import azure.functions as func
import logging
from datetime import datetime, timezone, timedelta
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import IFIX, IBOVESPA, IMOB, SMLL, IDIV, IFNC, FONTE_B3, UNIDADE_PONTOS
from Feeders.B3.GetIndices import get_b3_index

configure_logging()

INDICES_B3 = [
    (IFIX,     "IFIX"),
    (IBOVESPA, "IBOV"),
    (IMOB,     "IMOB"),
    (SMLL,     "SMLL"),
    (IDIV,     "IDIV"),
    (IFNC,     "IFNC"),
]


def _is_last_day_of_month(dt):
    return (dt + timedelta(days=1)).day == 1


def execute(date_ref=None):
    today_str = date_ref or datetime.now().strftime("%Y-%m-%d")
    dt = datetime.strptime(today_str, "%Y-%m-%d")

    if not _is_last_day_of_month(dt):
        logging.info(f"Skipping B3: {today_str} is not the last day of the month")
        return

    storage = TableStorageClient()

    for indice_name, symbol in INDICES_B3:
        try:
            logging.info(f"Collecting B3 {indice_name} ({symbol})")
            result = get_b3_index(symbol, today_str)
            if not result:
                logging.warning(f"No data available for {indice_name}")
                continue
            storage.upsert_indice(
                partition_key=indice_name,
                row_key=result["periodo"],
                valor=result["valor"],
                data_divulgacao=today_str,
                fonte=FONTE_B3,
                unidade=UNIDADE_PONTOS,
            )
            logging.info(f"{indice_name}: upserted {result['periodo']} = {result['valor']}")
        except Exception as e:
            logging.error(f"Error collecting {indice_name}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_b3 ran at {utc_timestamp}")
    execute()
