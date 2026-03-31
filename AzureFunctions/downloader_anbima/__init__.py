import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import (
    NTNB_2035, ETTJ_IPCA_5A, ETTJ_IPCA_10A,
    FONTE_ANBIMA, UNIDADE_TAXA,
)
from Feeders.Anbima.GetEttj import get_ettj, get_ntnb_2035

configure_logging()


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    try:
        logging.info("Collecting ETTJ IPCA vertices")
        ettj_results = get_ettj(today)
        if ettj_results:
            for item in ettj_results:
                storage.upsert_indice(
                    partition_key=item["nome"],
                    row_key=today,
                    valor=item["valor"],
                    periodo=item["periodo"],
                    fonte=FONTE_ANBIMA,
                    unidade=UNIDADE_TAXA,
                )
                logging.info(f"{item['nome']}: {today} = {item['valor']}")
        else:
            logging.warning("No ETTJ data available")
    except Exception as e:
        logging.error(f"Error collecting ETTJ: {e}")

    try:
        logging.info(f"Collecting {NTNB_2035}")
        result = get_ntnb_2035(today)
        if result:
            storage.upsert_indice(
                partition_key=NTNB_2035,
                row_key=today,
                valor=result["valor"],
                periodo=result["periodo"],
                fonte=FONTE_ANBIMA,
                unidade=UNIDADE_TAXA,
            )
            logging.info(f"{NTNB_2035}: {today} = {result['valor']}")
        else:
            logging.warning(f"No data available for {NTNB_2035}")
    except Exception as e:
        logging.error(f"Error collecting {NTNB_2035}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_anbima ran at {utc_timestamp}")
    execute()
