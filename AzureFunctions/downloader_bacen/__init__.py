import azure.functions as func
import logging
from datetime import datetime, timezone
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import (
    SELIC, CDI, PTAX_USD, TAXA_FINANC_IMOB, TR, TJLP, SELIC_META, IPCA_ACUM_12M, POUPANCA, JUROS_REAL,
    SBPE_VALOR, SBPE_UNIDADES, SBPE_SALDO,
    FONTE_BACEN,
    UNIDADE_TAXA, UNIDADE_TAXA_MENSAL, UNIDADE_REAIS_USD, UNIDADE_PERCENTUAL,
    UNIDADE_REAIS_MIL, UNIDADE_UNIDADES, UNIDADE_REAIS_BI,
)
from Feeders.Bacen.GetSelic import get_selic
from Feeders.Bacen.GetSeries import get_sgs_series
from Feeders.Bacen.GetJurosReal import get_juros_real

configure_logging()

SGS_CDI = 4391
SGS_PTAX_USD = 3696
SGS_TAXA_FINANC_IMOB = 25497
SGS_TR = 226
SGS_TJLP = 7811
SGS_SELIC_META = 432
SGS_IPCA_ACUM_12M = 13522
SGS_POUPANCA = 433
SGS_SBPE_VALOR = 20631
SGS_SBPE_UNIDADES = 20632
SGS_SBPE_SALDO = 7481

INDICES_BACEN = [
    (SELIC,            lambda d: get_selic(d),                             UNIDADE_TAXA),
    (CDI,              lambda d: get_sgs_series(SGS_CDI, d),               UNIDADE_TAXA_MENSAL),
    (PTAX_USD,         lambda d: get_sgs_series(SGS_PTAX_USD, d),          UNIDADE_REAIS_USD),
    (TAXA_FINANC_IMOB, lambda d: get_sgs_series(SGS_TAXA_FINANC_IMOB, d), UNIDADE_TAXA_MENSAL),
    (TR,               lambda d: get_sgs_series(SGS_TR, d),                UNIDADE_TAXA_MENSAL),
    (TJLP,             lambda d: get_sgs_series(SGS_TJLP, d),              UNIDADE_TAXA),
    (SELIC_META,       lambda d: get_sgs_series(SGS_SELIC_META, d),         UNIDADE_TAXA),
    (IPCA_ACUM_12M,    lambda d: get_sgs_series(SGS_IPCA_ACUM_12M, d),     UNIDADE_PERCENTUAL),
    (POUPANCA,         lambda d: get_sgs_series(SGS_POUPANCA, d),           UNIDADE_TAXA_MENSAL),
    (JUROS_REAL,       lambda d: get_juros_real(d),                         UNIDADE_TAXA),
    (SBPE_VALOR,       lambda d: get_sgs_series(SGS_SBPE_VALOR, d),         UNIDADE_REAIS_MIL),
    (SBPE_UNIDADES,    lambda d: get_sgs_series(SGS_SBPE_UNIDADES, d),      UNIDADE_UNIDADES),
    (SBPE_SALDO,       lambda d: get_sgs_series(SGS_SBPE_SALDO, d),        UNIDADE_REAIS_BI),
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
