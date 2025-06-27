import logging
import gspread
from typing import Any, List, Dict
from datetime import date
from scraper.storage.sheet_constants import (
    PIZZA_HEADER,
    PASTA_HEADER,
    DIFFERENCES_HEADER,
    AVERAGES_HEADER,
)
from scraper.storage.sheets_reader import (
    get_pasta_ws,
    get_pizza_ws,
    get_differences_ws,
    get_averages_ws,
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
    records: List[Dict[str, Any]], start_cell: str, end_cell: str
) -> None:
    """Bulk‐append new product rows to the appropriate sheets based on Type."""

    pizza_ws = get_pizza_ws()
    pasta_ws = get_pasta_ws()

    pizza_records = [rec for rec in records if rec.get("Type", "").lower() == "pizza"]
    pasta_records = [rec for rec in records if rec.get("Type", "").lower() == "pasta"]

    if pizza_records:
        _clear_worksheet(pizza_ws, start_cell, end_cell)
        pizza_rows = [
            [rec.get(col, "") for col in PIZZA_HEADER] for rec in pizza_records
        ]
        _bulk_append(pizza_ws, pizza_rows, start_cell)

    if pasta_records:
        _clear_worksheet(pasta_ws, start_cell, end_cell)
        pasta_rows = [
            [rec.get(col, "") for col in PASTA_HEADER] for rec in pasta_records
        ]
        _bulk_append(pasta_ws, pasta_rows, start_cell)


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
    """Bulk‐append avg rows to AVERAGES_SHEET with a blank line separating pizza and pasta."""

    ws = get_averages_ws()
    _clear_worksheet(ws, start_cell, end_cell)

    rows: List[List[Any]] = []
    pasta_found = False

    for rec in records:
        if not pasta_found and rec.get("Type", "").lower() == "pasta":
            rows.append([""] * len(AVERAGES_HEADER))
            pasta_found = True
        rows.append([rec.get(col, "") for col in AVERAGES_HEADER])

    _bulk_append(ws, rows, start_cell)


def set_execution_date(date_cell: str) -> None:
    """Set execution date when the scraper ends"""

    pizza_ws = get_pizza_ws()
    pasta_ws = get_pasta_ws()
    today = date.today().isoformat()

    try:
        pizza_ws.update(
            range_name=date_cell,
            values=[[today]],
            value_input_option="USER_ENTERED",
        )

        pasta_ws.update(
            range_name=date_cell,
            values=[[today]],
            value_input_option="USER_ENTERED",
        )

        logger.info(f"Set execution date to {today}")
    except gspread.exceptions.APIError:
        logger.error("Failed to set execution date", exc_info=True)
        raise
