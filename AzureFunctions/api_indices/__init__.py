import azure.functions as func
import json
import logging
from Util.logging_config import configure_logging
from Storage.TableStorageClient import TableStorageClient

configure_logging()


def _entity_to_dict(entity):
    return {
        "nome": entity["PartitionKey"],
        "periodo": entity["RowKey"],
        "valor": entity.get("valor"),
        "data_divulgacao": entity.get("data_divulgacao"),
        "fonte": entity.get("fonte"),
        "unidade": entity.get("unidade"),
    }


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    storage = TableStorageClient()
    nome = req.params.get("nome")
    data_inicio = req.params.get("data_inicio")
    data_fim = req.params.get("data_fim")

    if not nome:
        indices = storage.list_indices()
        if not indices:
            return func.HttpResponse(
                json.dumps({"indices": []}),
                status_code=200,
                mimetype="application/json",
            )
        result = []
        for idx in sorted(indices):
            historico = storage.get_historico(idx)
            if historico:
                latest = max(historico, key=lambda e: e["RowKey"])
                result.append(_entity_to_dict(latest))
        return func.HttpResponse(
            json.dumps({"indices": result}),
            status_code=200,
            mimetype="application/json",
        )

    if data_inicio or data_fim:
        historico = storage.get_historico(nome, data_inicio, data_fim)
        if not historico:
            return func.HttpResponse(
                json.dumps({"error": f"Index '{nome}' not found"}),
                status_code=404,
                mimetype="application/json",
            )
        return func.HttpResponse(
            json.dumps({"indices": [_entity_to_dict(e) for e in historico]}),
            status_code=200,
            mimetype="application/json",
        )

    historico = storage.get_historico(nome)
    if not historico:
        return func.HttpResponse(
            json.dumps({"error": f"Index '{nome}' not found"}),
            status_code=404,
            mimetype="application/json",
        )
    latest = max(historico, key=lambda e: e["RowKey"])
    return func.HttpResponse(
        json.dumps({"indices": [_entity_to_dict(latest)]}),
        status_code=200,
        mimetype="application/json",
    )
