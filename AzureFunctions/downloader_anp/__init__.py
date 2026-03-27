import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import ANP_DIESEL, FONTE_ANP, UNIDADE_REAIS_LITRO
from Feeders.Anp.GetDiesel import get_diesel

configure_logging()


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    try:
        logging.info("Collecting ANP Diesel")
        result = get_diesel(today)
        if not result:
            logging.warning("No ANP diesel data available")
            return
        storage.upsert_indice(
            partition_key=ANP_DIESEL,
            row_key=result["periodo"],
            valor=result["valor"],
            data_divulgacao=today,
            fonte=FONTE_ANP,
            unidade=UNIDADE_REAIS_LITRO,
        )
        logging.info("ANP Diesel collected successfully")
    except Exception as e:
        logging.error(f"Error collecting ANP Diesel: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_anp ran at {utc_timestamp}")
    execute()
