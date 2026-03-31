import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import (
    IPCA, INPC, SINAPI, IPCA_15, PIB, INSUMOS_CONSTRUCAO, METALURGIA,
    FONTE_IBGE, UNIDADE_PERCENTUAL, UNIDADE_INDICE,
)
from Feeders.Ibge.GetIndicadores import get_indicador
from Feeders.Ibge.GetPib import get_pib

configure_logging()

INDICES_IBGE = {
    IPCA: UNIDADE_PERCENTUAL,
    INPC: UNIDADE_PERCENTUAL,
    SINAPI: UNIDADE_PERCENTUAL,
    IPCA_15: UNIDADE_PERCENTUAL,
    INSUMOS_CONSTRUCAO: UNIDADE_INDICE,
    METALURGIA: UNIDADE_INDICE,
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
                row_key=today,
                valor=result["valor"],
                periodo=result["periodo"],
                fonte=FONTE_IBGE,
                unidade=unidade,
            )
            logging.info(f"{indice_name}: {today} = {result['valor']} (periodo={result['periodo']})")
        except Exception as e:
            logging.error(f"Error collecting {indice_name}: {e}")

    try:
        logging.info(f"Collecting {PIB}")
        result = get_pib(today)
        if not result:
            logging.warning(f"No data for {PIB}")
        else:
            storage.upsert_indice(
                partition_key=PIB,
                row_key=today,
                valor=result["valor"],
                periodo=result["periodo"],
                fonte=FONTE_IBGE,
                unidade=UNIDADE_PERCENTUAL,
            )
            logging.info(f"{PIB}: {today} = {result['valor']} (periodo={result['periodo']})")
    except Exception as e:
        logging.error(f"Error collecting {PIB}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_ibge ran at {utc_timestamp}")
    execute()
