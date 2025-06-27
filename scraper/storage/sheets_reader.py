import json
import logging
import os
import gspread
from typing import Any, Dict, List
from gspread import Spreadsheet, Worksheet
from google.oauth2.service_account import Credentials
from scraper.storage.sheet_constants import (
    PASTA_SHEET,
    PIZZA_SHEET,
    DIFFERENCES_SHEET,
    AVERAGES_SHEET,
)
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _init_workbook() -> Spreadsheet:
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    key_json = os.getenv("GCP_SA_KEY_JSON")
    if not sheet_id or not key_json:
        raise RuntimeError("Missing GOOGLE_SHEET_ID or GCP_SA_KEY_JSON")

    info = json.loads(key_json)
    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    wb = client.open_by_key(sheet_id)
    logger.info("Google Sheet opened successfully")
    return wb


def get_workbook() -> Spreadsheet:
    return _init_workbook()


def get_pizza_ws() -> Worksheet:
    return get_workbook().worksheet(PIZZA_SHEET)


def get_pasta_ws() -> Worksheet:
    return get_workbook().worksheet(PASTA_SHEET)


def get_products_ws() -> List[Worksheet]:
    return [get_pizza_ws(), get_pasta_ws()]


def get_differences_ws() -> Worksheet:
    return get_workbook().worksheet(DIFFERENCES_SHEET)


def get_averages_ws() -> Worksheet:
    return get_workbook().worksheet(AVERAGES_SHEET)


def get_product_records(
    start_cell: str, end_cell: str, header_row: int = 2
) -> List[Dict[str, Any]]:

    cell_range = f"{start_cell}:{end_cell}"
    combined_records: List[Dict[str, Any]] = []

    try:
        for ws in get_products_ws():
            headers = ws.row_values(header_row)
            values = ws.get_values(cell_range)
            records = [dict(zip(headers, row)) for row in values if any(row)]
            combined_records.extend(records)
            logger.info(
                f"Loaded {len(records)} products from '{ws.title}' in range {cell_range}"
            )
        return combined_records
    except gspread.APIError:
        logger.error("Failed to fetch products from one of the sheets", exc_info=True)
        raise
