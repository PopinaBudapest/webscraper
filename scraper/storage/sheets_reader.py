import json
import logging
import os
import gspread
from gspread import Spreadsheet, Worksheet
from google.oauth2.service_account import Credentials
from scraper.storage.sheet_constants import (
    PRODUCTS_SHEET,
    DIFFERENCES_SHEET,
    LAST_RUN_SHEET,
)
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _init_workbook() -> Spreadsheet:
    sheet_id    = os.getenv("GOOGLE_SHEET_ID")
    key_json    = os.getenv("GCP_SA_KEY_JSON")
    if not sheet_id or not key_json:
        raise RuntimeError("Missing GOOGLE_SHEET_ID or GCP_SA_KEY_JSON")

    info = json.loads(key_json)
    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    wb     = client.open_by_key(sheet_id)
    logger.info("Google Sheet opened successfully")
    return wb


def get_workbook() -> Spreadsheet:
    return _init_workbook()


def get_products_ws() -> Worksheet:
    return get_workbook().worksheet(PRODUCTS_SHEET)


def get_differences_ws() -> Worksheet:
    return get_workbook().worksheet(DIFFERENCES_SHEET)


def get_last_run_ws() -> Worksheet:
    return get_workbook().worksheet(LAST_RUN_SHEET)


def get_product_records() -> dict:
    try:
        raw = get_products_ws().get_all_records()
        logger.info(f"Loaded {len(raw)} products from '{PRODUCTS_SHEET}'")
        return raw
    except gspread.APIError:
        logger.error("Failed to fetch existing products", exc_info=True)
        raise
