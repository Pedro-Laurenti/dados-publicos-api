import azure.functions as func
import logging
import json
from datetime import datetime
from Util.logging_config import configure_logging

configure_logging()

DOWNLOADER_MAP = {
    "fgv": "downloader_fgv",
    "ibge": "downloader_ibge",
    "bacen": "downloader_bacen",
    "anp": "downloader_anp",
}


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    downloader_name = req.params.get("downloader")
    date_ref = req.params.get("date")

    if not downloader_name or not date_ref:
        return func.HttpResponse(
            json.dumps({"error": "Missing 'downloader' or 'date' query parameter", "usage": "/api/downloader_http?downloader=ibge&date=2026-03-27"}),
            status_code=400,
            mimetype="application/json",
        )

    if downloader_name not in DOWNLOADER_MAP:
        return func.HttpResponse(
            json.dumps({"error": f"Invalid downloader: {downloader_name}", "valid": list(DOWNLOADER_MAP.keys())}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        datetime.strptime(date_ref, "%Y-%m-%d")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid date format. Use YYYY-MM-DD"}),
            status_code=400,
            mimetype="application/json",
        )

    module_name = DOWNLOADER_MAP[downloader_name]

    try:
        module = __import__(module_name)
        module.execute(date_ref=date_ref)
        return func.HttpResponse(
            json.dumps({"success": True, "downloader": downloader_name, "date": date_ref}),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.error(f"Error executing downloader {downloader_name}: {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
