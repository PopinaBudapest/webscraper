import logging
import gspread
from typing import Any, List, Dict
from datetime import datetime
from scraper.storage.sheet_constants import (
    PRODUCTS_HEADER,
    DIFFERENCES_HEADER,
    AVERAGES_HEADER,
)
from scraper.storage.sheets_reader import (
    get_averages_ws,
    get_products_ws,
    get_differences_ws,
    get_last_run_ws,
)

logger = logging.getLogger(__name__)


def _clear_worksheet(ws) -> None:
    """Clear parameter worksheet (assumes headers in row 1)"""

    try:
        ws.batch_clear(["A2:Z"])
        logger.info("Cleared rows from '%s'", ws.title)
    except Exception as e:
        logger.error("Failed to clear rows: %s", e, exc_info=True)
        raise


def _bulk_append(
    ws, records: List[List[Any]]) -> None:
    """Use server‐side append to avoid reading the sheet and race conditions."""

    try:
        ws.append_rows(records, value_input_option="USER_ENTERED")
        logger.info(f"Successfully appended {len(records)} rows to '{ws.title}'")
    except Exception as e:
        logger.error(f"Failed to append rows to '{ws.title}': {e}", exc_info=True)
        raise


def bulk_append_products(records: List[List[Any]]) -> None:
    """Bulk‐append new product rows to PRODUCTS_SHEET."""

    ws = get_products_ws()

    _clear_worksheet(ws) 

    # Transform List[Dict] into List[List] in header order
    rows: List[List[Any]] = [
        [rec.get(col, "") for col in PRODUCTS_HEADER] for rec in records
    ]

    _bulk_append(ws, rows)


def bulk_append_differences(records: List[List[Any]]) -> None:
    """Bulk‐append diff rows to DIFFERENCES_SHEET."""

    ws = get_differences_ws()

    # Transform List[Dict] into List[List] in header order
    rows: List[List[Any]] = [
        [rec.get(col, "") for col in DIFFERENCES_HEADER] for rec in records
    ]

    _bulk_append(ws, rows)


def bulk_replace_averages(records: List[Dict[str, Any]]) -> None:
    """Bulk‐append diff rows to AVERAGES_SHEET."""

    ws = get_averages_ws()

    _clear_worksheet(ws)

    # Transform List[Dict] into List[List] in header order
    rows: List[List[Any]] = [
        [rec.get(col, "") for col in AVERAGES_HEADER] for rec in records
    ]

    _bulk_append(ws, rows)


def set_execution_date() -> None:
    """Set execution date when the scraper ends"""

    ws = get_last_run_ws()
    timestamp = datetime.now().isoformat()

    try:
        ws.update(
            range_name="A1", values=[[timestamp]], value_input_option="USER_ENTERED"
        )
        logger.info(f"Set execution date to {timestamp}")
    except gspread.exceptions.APIError:
        logger.error("Failed to set execution date", exc_info=True)
        raise
