import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import SOFR, FONTE_FEDNY, UNIDADE_TAXA
from Feeders.FedNy.GetSofr import get_sofr

configure_logging()


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    try:
        logging.info(f"Collecting {SOFR}")
        result = get_sofr(today)
        if not result:
            logging.warning(f"No data available for {SOFR}")
            return
        storage.upsert_indice(
            partition_key=SOFR,
            row_key=today,
            valor=result["valor"],
            periodo=result["periodo"],
            fonte=FONTE_FEDNY,
            unidade=UNIDADE_TAXA,
        )
        logging.info(f"{SOFR}: {today} = {result['valor']} (periodo={result['periodo']})")
    except Exception as e:
        logging.error(f"Error collecting {SOFR}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_sofr ran at {utc_timestamp}")
    execute()
