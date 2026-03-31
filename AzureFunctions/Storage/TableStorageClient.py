import logging
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from config import DADPUBAPI_STORAGE_TABLE_URL

TABLE_NAME = "IndicesPublicos"


class TableStorageClient:
    def __init__(self):
        service = TableServiceClient(
            endpoint=DADPUBAPI_STORAGE_TABLE_URL,
            credential=DefaultAzureCredential(),
        )
        self._table = service.get_table_client(TABLE_NAME)

    def upsert_indice(self, partition_key, row_key, valor, periodo, fonte, unidade):
        entity = {
            "PartitionKey": partition_key,
            "RowKey": row_key,
            "valor": float(valor),
            "periodo": periodo,
            "fonte": fonte,
            "unidade": unidade,
        }
        self._table.upsert_entity(entity)
        logging.info(f"Upsert: {partition_key} | {row_key} | periodo={periodo} | {valor}")

    def get_indice(self, partition_key, row_key):
        try:
            return self._table.get_entity(partition_key, row_key)
        except Exception:
            return None

    def get_historico(self, partition_key, data_inicio=None, data_fim=None):
        filters = [f"PartitionKey eq '{partition_key}'"]
        if data_inicio:
            filters.append(f"RowKey ge '{data_inicio}'")
        if data_fim:
            filters.append(f"RowKey le '{data_fim}'")
        query = " and ".join(filters)
        return list(self._table.query_entities(query))

    def get_latest(self, partition_key):
        """Retorna a entidade mais recente de um índice (último RowKey)."""
        entities = self._table.query_entities(
            f"PartitionKey eq '{partition_key}'",
            results_per_page=1,
        )
        latest = None
        for e in entities:
            if latest is None or e["RowKey"] > latest["RowKey"]:
                latest = e
        return latest
