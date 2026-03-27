import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import IPCA, INPC, SINAPI, FONTE_IBGE, UNIDADE_PERCENTUAL
from Feeders.Ibge.GetIndicadores import get_indicador

configure_logging()

INDICES_IBGE = {
    IPCA: UNIDADE_PERCENTUAL,
    INPC: UNIDADE_PERCENTUAL,
    SINAPI: UNIDADE_PERCENTUAL,
}


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    for indice_name, unidade in INDICES_IBGE.items():
        try:
            logging.info(f"Collecting {indice_name}")
            result = get_indicador(indice_name, today)
            if not result:
                logging.warning(f"No data for {indice_name}")
                continue
            storage.upsert_indice(
                partition_key=indice_name,
                row_key=result["periodo"],
                valor=result["valor"],
                data_divulgacao=today,
                fonte=FONTE_IBGE,
                unidade=unidade,
            )
            logging.info(f"{indice_name} collected successfully")
        except Exception as e:
            logging.error(f"Error collecting {indice_name}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_ibge ran at {utc_timestamp}")
    execute()
