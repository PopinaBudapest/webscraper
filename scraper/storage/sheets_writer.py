import logging
import gspread
from typing import Any, List, Dict
from datetime import date
from scraper.storage.sheet_constants import (
    PRODUCTS_HEADER,
    DIFFERENCES_HEADER,
    AVERAGES_HEADER,
)
from scraper.storage.sheets_reader import (
    get_averages_ws,
    get_products_ws,
    get_differences_ws,
)

logger = logging.getLogger(__name__)


def _clear_worksheet(ws, start_cell: str, end_cell: str) -> None:
    """Clear only the rectangle from start_cell to end_cell (inclusive),"""

    # build a single range string
    cell_range = f"{start_cell}:{end_cell}"

    try:
        ws.batch_clear([cell_range])
        logger.info("Cleared cells %s on '%s'", cell_range, ws.title)
    except Exception as e:
        logger.error("Failed to clear %s: %s", cell_range, e, exc_info=True)
        raise


def _bulk_append(ws, records: List[List[Any]], start_cell) -> None:
    """Use server‐side append to avoid reading the sheet and race conditions."""

    try:
        ws.append_rows(
            records,
            value_input_option="USER_ENTERED",
            table_range=start_cell,
        )
        logger.info(f"Successfully appended {len(records)} rows to '{ws.title}'")
    except Exception as e:
        logger.error(f"Failed to append rows to '{ws.title}': {e}", exc_info=True)
        raise


def bulk_append_products(
    records: List[List[Any]], start_cell: str, end_cell: str
) -> None:
    """Bulk‐append new product rows to PRODUCTS_SHEET."""

    ws = get_products_ws()

    _clear_worksheet(ws, start_cell, end_cell)

    # Transform List[Dict] into List[List] in header order
    rows: List[List[Any]] = [
        [rec.get(col, "") for col in PRODUCTS_HEADER] for rec in records
    ]

    _bulk_append(ws, rows, start_cell)


def bulk_append_differences(records: List[List[Any]], start_cell: str) -> None:
    """Bulk‐append diff rows to DIFFERENCES_SHEET."""

    ws = get_differences_ws()

    # Transform List[Dict] into List[List] in header order
    rows: List[List[Any]] = [
        [rec.get(col, "") for col in DIFFERENCES_HEADER] for rec in records
    ]

    _bulk_append(ws, rows, start_cell)


def bulk_replace_averages(
    records: List[Dict[str, Any]], start_cell: str, end_cell: str
) -> None:
    """Bulk‐append diff rows to AVERAGES_SHEET."""

    ws = get_averages_ws()

    _clear_worksheet(ws, start_cell, end_cell)

    # Transform List[Dict] into List[List] in header order
    rows: List[List[Any]] = [
        [rec.get(col, "") for col in AVERAGES_HEADER] for rec in records
    ]

    _bulk_append(ws, rows, start_cell)


def set_execution_date(date_cell: str) -> None:
    """Set execution date when the scraper ends"""

    ws = get_products_ws()
    today = date.today().isoformat()

    try:
        ws.update(
            range_name=date_cell,
            values=[[today]],
            value_input_option="USER_ENTERED",
        )
        logger.info(f"Set execution date to {today}")
    except gspread.exceptions.APIError:
        logger.error("Failed to set execution date", exc_info=True)
        raise
