import logging
import gspread
from typing import Any, List, Dict
from string import ascii_uppercase
from datetime import datetime
from scraper.storage.sheet_constants import PRODUCT_HEADERS, DIFFERENCE_HEADERS
from scraper.storage.sheets_reader import (
    get_products_ws,
    get_differences_ws,
    get_last_run_ws,
)

logger = logging.getLogger(__name__)


def _range_for(
    rows: List[List], headers: List[str], start_col: str = "A", start_row: int = 1
):

    col_count = len(headers)
    start_idx = ascii_uppercase.index(start_col)
    end_col = ascii_uppercase[start_idx + col_count - 1]
    end_row = start_row + len(rows) - 1
    return f"{start_col}{start_row}:{end_col}{end_row}"


# Bulk transaction to sheets


def _bulk_append(
    ws, records: List[List[Any]], value_input_option: str = "USER_ENTERED"
) -> None:
    """Use server‐side append to avoid reading the sheet and race conditions."""
    try:
        ws.append_rows(records, value_input_option=value_input_option)
        logger.info(f"Successfully appended {len(records)} rows to '{ws.title}'")
    except Exception as e:
        logger.error(f"Failed to append rows to '{ws.title}': {e}", exc_info=True)
        raise


def bulk_append_products(records: List[List[Any]]) -> None:
    """Bulk‐append new product rows to PRODUCTS_SHEET."""
    ws = get_products_ws()
    _bulk_append(ws, records)


def bulk_append_differences(records: List[List[Any]]) -> None:
    """Bulk‐append diff rows to DIFFERENCES_SHEET."""
    ws = get_differences_ws()
    _bulk_append(ws, records)


def bulk_update_products(
    records: List[Dict[str, Any]], value_input_option: str = "USER_ENTERED"
) -> None:
    """Bulk update product rows in PRODUCTS_SHEET."""
    ws = get_products_ws()
    try:
        ws.batch_update(records, value_input_option=value_input_option)
        logger.info(f"Successfully updated {len(records)} products")
    except Exception as e:
        logger.error(f"Failed to bulk update products: {e}", exc_info=True)
        raise


def bulk_delete_products(records: List[int]) -> None:
    """
    Bulk‐delete product rows in the PRODUCTS_SHEET.
    `row_numbers` should be the 1-based row indices to delete (e.g. [5, 10, 12]).
    Rows are deleted in descending order to avoid index shifts.
    """
    ws = get_products_ws()
    sheet_id = ws._properties["sheetId"]

    # Build one deleteDimension request per contiguous block
    # Sort rows descending so earlier deletions don't affect later indices
    requests = []
    for row in sorted(records, reverse=True):
        requests.append({
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": "ROWS",
                    "startIndex": row - 1,  # zero‐based, inclusive
                    "endIndex": row         # exclusive
                }
            }
        })

    body = {"requests": requests}
    try:
        # Send a single batchUpdate to delete all requested rows
        ws.spreadsheet.batch_update(body)
        logger.info(f"Successfully deleted {len(records)} rows from '{ws.title}'")
    except Exception as e:
        logger.error(f"Failed to bulk delete rows from '{ws.title}': {e}", exc_info=True)
        raise



# Methods to append and update individual product and difference rows
# Only for testing if needed


def append_product(record) -> None:
    """Append a product row to the PRODUCTS_SHEET."""

    ws = get_products_ws()
    values = [record[h] for h in PRODUCT_HEADERS]

    try:
        ws.append_row(values)
        logger.info(
            f"Successfully appended product: {record['product_name']} "
            f"({record['restaurant']} / {record['product_type']})"
        )
    except gspread.exceptions.APIError as e:
        logger.error(f"Failed to append product row {values!r}: {e}", exc_info=True)
        raise


def update_product(row: int, record: Dict[str, Any]) -> None:
    """Update a product row in PRODUCTS_SHEET."""

    ws = get_products_ws()
    values = [record[h] for h in PRODUCT_HEADERS]

    # wrap values in a list-of-lists so _range_for can compute rows correctly
    rng = _range_for([values], PRODUCT_HEADERS, start_col="A", start_row=row)

    try:
        ws.update(rng, [values])
        logger.info(
            f"Successfully updated product: {record['product_name']} "
            f"({record['restaurant']} / {record['product_type']})"
        )
    except gspread.exceptions.APIError as e:
        logger.error(f"Failed to update product row {values!r}: {e}", exc_info=True)
        raise


def append_difference(record) -> None:
    """Append a difference row to the DIFFERENCES_SHEET."""

    ws = get_differences_ws()
    diff_row = [record.get(h) for h in DIFFERENCE_HEADERS]

    try:
        ws.append_row(diff_row)
        logger.info(
            f"Successfully appended difference: {record['product_name']} "
            f"({record['restaurant']} / {record['product_type']})"
        )
    except gspread.exceptions.APIError as e:
        logger.error(
            f"Failed to append difference row {diff_row!r}: {e}", exc_info=True
        )
        raise

    # Set the execution date in the last run worksheet


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
