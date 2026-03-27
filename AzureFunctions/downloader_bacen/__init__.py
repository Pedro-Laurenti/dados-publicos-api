import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import SELIC, FONTE_BACEN, UNIDADE_TAXA
from Feeders.Bacen.GetSelic import get_selic

configure_logging()


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    try:
        logging.info("Collecting Selic")
        result = get_selic(today)
        if not result:
            logging.warning("No Selic data available")
            return
        storage.upsert_indice(
            partition_key=SELIC,
            row_key=result["periodo"],
            valor=result["valor"],
            data_divulgacao=today,
            fonte=FONTE_BACEN,
            unidade=UNIDADE_TAXA,
        )
        logging.info("Selic collected successfully")
    except Exception as e:
        logging.error(f"Error collecting Selic: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_bacen ran at {utc_timestamp}")
    execute()
