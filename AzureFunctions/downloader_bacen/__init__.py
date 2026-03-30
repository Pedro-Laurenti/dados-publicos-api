import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import (
    SELIC, CDI, PTAX_USD, TAXA_FINANC_IMOB,
    FONTE_BACEN,
    UNIDADE_TAXA, UNIDADE_TAXA_MENSAL, UNIDADE_REAIS_USD,
)
from Feeders.Bacen.GetSelic import get_selic
from Feeders.Bacen.GetSeries import get_sgs_series

configure_logging()

SGS_CDI = 4391
SGS_PTAX_USD = 3696
SGS_TAXA_FINANC_IMOB = 25497

INDICES_BACEN = [
    (SELIC,           lambda d: get_selic(d),                          UNIDADE_TAXA),
    (CDI,             lambda d: get_sgs_series(SGS_CDI, d),            UNIDADE_TAXA_MENSAL),
    (PTAX_USD,        lambda d: get_sgs_series(SGS_PTAX_USD, d),       UNIDADE_REAIS_USD),
    (TAXA_FINANC_IMOB, lambda d: get_sgs_series(SGS_TAXA_FINANC_IMOB, d), UNIDADE_TAXA_MENSAL),
]


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    for indice_name, fetch_fn, unidade in INDICES_BACEN:
        try:
            logging.info(f"Collecting {indice_name}")
            result = fetch_fn(today)
            if not result:
                logging.warning(f"No data available for {indice_name}")
                continue
            storage.upsert_indice(
                partition_key=indice_name,
                row_key=result["periodo"],
                valor=result["valor"],
                data_divulgacao=today,
                fonte=FONTE_BACEN,
                unidade=unidade,
            )
            logging.info(f"{indice_name}: upserted {result['periodo']} = {result['valor']}")
        except Exception as e:
            logging.error(f"Error collecting {indice_name}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_bacen ran at {utc_timestamp}")
    execute()
