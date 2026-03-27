import azure.functions as func
import logging
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


def execute(date_ref=None):
    storage = TableStorageClient()
    today = date_ref or datetime.now().strftime("%Y-%m-%d")

    for indice_name, fetch_fn in INDICES_FGV.items():
        try:
            logging.info(f"Collecting {indice_name}")
            df = fetch_fn()
            for _, row in df.iterrows():
                dt_ref = str(row["dt_ref"]).strip()
                valor = row[indice_name]
                try:
                    float(valor)
                except (ValueError, TypeError):
                    continue
                periodo = dt_ref[:7] if len(dt_ref) >= 7 else dt_ref
                storage.upsert_indice(
                    partition_key=indice_name,
                    row_key=periodo,
                    valor=valor,
                    data_divulgacao=today,
                    fonte=FONTE_FGV,
                    unidade=UNIDADE_PERCENTUAL,
                )
            logging.info(f"{indice_name} collected successfully")
        except Exception as e:
            logging.error(f"Error collecting {indice_name}: {e}")


def main(mytimer: func.TimerRequest, context: func.Context) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info("The timer is past due!")
    logging.info(f"downloader_fgv ran at {utc_timestamp}")
    execute()
