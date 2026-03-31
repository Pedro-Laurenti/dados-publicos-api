import azure.functions as func
import json
import logging
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient
from Constants.Indices import (
    INCC_M, IGP_M, IGP_DI, IPCA, INPC, SINAPI, SELIC, ANP_DIESEL,
    CDI, PTAX_USD, TAXA_FINANC_IMOB, TR, TJLP, SELIC_META, IPCA_ACUM_12M,
    POUPANCA, JUROS_REAL, PIB, IPCA_15, IFIX, IBOVESPA, IMOB, SMLL, IDIV, IFNC,
    NTNB_2035, ETTJ_IPCA_5A, ETTJ_IPCA_10A, SBPE_VALOR, SBPE_UNIDADES, SBPE_SALDO,
    INSUMOS_CONSTRUCAO, METALURGIA, SOFR,
)

configure_logging()

ALL_INDICES = [
    INCC_M, IGP_M, IGP_DI, IPCA, INPC, SINAPI, SELIC, ANP_DIESEL,
    CDI, PTAX_USD, TAXA_FINANC_IMOB, TR, TJLP, SELIC_META, IPCA_ACUM_12M,
    POUPANCA, JUROS_REAL, PIB, IPCA_15, IFIX, IBOVESPA, IMOB, SMLL, IDIV, IFNC,
    NTNB_2035, ETTJ_IPCA_5A, ETTJ_IPCA_10A, SBPE_VALOR, SBPE_UNIDADES, SBPE_SALDO,
    INSUMOS_CONSTRUCAO, METALURGIA, SOFR,
]


def _entity_to_dict(entity):
    return {
        "nome": entity["PartitionKey"],
        "data": entity["RowKey"],
        "valor": entity.get("valor"),
        "periodo": entity.get("periodo"),
        "fonte": entity.get("fonte"),
        "unidade": entity.get("unidade"),
    }


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    storage = TableStorageClient()
    nome = req.params.get("nome")
    data = req.params.get("data")
    data_inicio = req.params.get("data_inicio")
    data_fim = req.params.get("data_fim")

    # GET /api/indices → último valor de cada índice
    if not nome:
        result = []
        for idx in ALL_INDICES:
            try:
                latest = storage.get_latest(idx)
                if latest:
                    result.append(_entity_to_dict(latest))
            except Exception as e:
                logging.warning(f"Error fetching latest for {idx}: {e}")
        return func.HttpResponse(
            json.dumps({"indices": result}),
            status_code=200,
            mimetype="application/json",
        )

    # GET /api/indices?nome=ipca&data=2026-03-30 → valor exato do dia
    if data:
        entity = storage.get_indice(nome, data)
        if not entity:
            return func.HttpResponse(
                json.dumps({"error": f"Sem dados para '{nome}' na data '{data}'"}),
                status_code=404,
                mimetype="application/json",
            )
        return func.HttpResponse(
            json.dumps({"indices": [_entity_to_dict(entity)]}),
            status_code=200,
            mimetype="application/json",
        )

    # GET /api/indices?nome=ipca&data_inicio=2026-01-01&data_fim=2026-03-31 → histórico
    if data_inicio or data_fim:
        historico = storage.get_historico(nome, data_inicio, data_fim)
        if not historico:
            return func.HttpResponse(
                json.dumps({"error": f"Sem dados para '{nome}' no período informado"}),
                status_code=404,
                mimetype="application/json",
            )
        return func.HttpResponse(
            json.dumps({"indices": [_entity_to_dict(e) for e in historico]}),
            status_code=200,
            mimetype="application/json",
        )

    # GET /api/indices?nome=ipca → último valor
    latest = storage.get_latest(nome)
    if not latest:
        return func.HttpResponse(
            json.dumps({"error": f"Índice '{nome}' não encontrado"}),
            status_code=404,
            mimetype="application/json",
        )
    return func.HttpResponse(
        json.dumps({"indices": [_entity_to_dict(latest)]}),
        status_code=200,
        mimetype="application/json",
    )
