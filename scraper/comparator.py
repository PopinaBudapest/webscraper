import logging
from datetime import date
from typing import Any, Dict, List, Tuple
from scraper.storage.sheet_constants import (
    PRODUCT_HEADERS,
    COL_DATE,
    COL_RESTAURANT,
    COL_TYPE,
    COL_NAME,
    COL_PRICE,
    COL_DESCRIPTION,
)

logger = logging.getLogger(__name__)


def _normalize_records(
    raw_records: List[Dict[str, Any]], include_row: bool = False
) -> Dict[Tuple[str, str, str], Any]:
    """
    Common normalization for site and sheet records.
    If include_row is True, returns {key: {"record": rec, "row": idx}}, else {key: rec}.
    """
    formatted: Dict[Tuple[str, str, str], Any] = {}
    required = set(PRODUCT_HEADERS)
    start_index = 2 if include_row else 0

    for idx, rec in enumerate(raw_records, start=start_index):
        rec_mod = rec.copy()
        rec_mod[COL_DATE] = date.today().isoformat()

        # Validate presence of all needed keys
        missing = required - rec_mod.keys()
        if missing:
            raise ValueError(f"Record missing keys {missing}: {rec}")

        key = (
            rec_mod[COL_RESTAURANT],
            rec_mod[COL_TYPE],
            rec_mod[COL_NAME],
        )

        if include_row:
            formatted[key] = {"record": rec_mod, "row": idx}
        else:
            formatted[key] = rec_mod

    logger.info(
        f"Normalized {len(formatted)} {'sheet' if include_row else 'site'} records"
    )
    return formatted


def normalize_site_records(
    raw_records: List[Dict[str, Any]],
) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    return _normalize_records(raw_records, include_row=False)


def normalize_sheet_records(
    raw_records: List[Dict[str, Any]],
) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    return _normalize_records(raw_records, include_row=True)


def get_product_changes(
    site_records: Dict[Tuple[str, str, str], dict],
    sheet_records: Dict[Tuple[str, str, str], dict],
) -> Tuple[List[List[Any]], List[dict], List[List[Any]], List[List[Any]]]:
    append_rows: List[List[Any]] = []
    update_rows: List[dict] = []
    diff_rows: List[List[Any]] = []
    is_delete: bool = False

    # Compare site → sheet
    for key, rec in site_records.items():

        if key in sheet_records:

            old_rec = sheet_records[key]["record"]
            row = sheet_records[key]["row"]

            if rec != old_rec:
                update_rows.append(
                    {
                        "range": f"A{row}:F{row}",
                        "values": [[rec[h] for h in PRODUCT_HEADERS]],
                    }
                )

            # Price change
            old_price = old_rec.get(COL_PRICE)
            new_price = rec.get(COL_PRICE)
            if new_price != old_price:
                diff_rows.append(
                    [
                        rec.get(COL_DATE, ""),
                        rec[COL_RESTAURANT],
                        rec[COL_TYPE],
                        rec[COL_NAME],
                        old_price,
                        new_price,
                        "",
                        "",
                        "Price change",
                    ]
                )

            # Description change
            old_desc = old_rec.get(COL_DESCRIPTION)
            new_desc = rec.get(COL_DESCRIPTION)
            if new_desc != old_desc:
                diff_rows.append(
                    [
                        rec.get(COL_DATE, ""),
                        rec[COL_RESTAURANT],
                        rec[COL_TYPE],
                        rec[COL_NAME],
                        "",
                        "",
                        old_desc,
                        new_desc,
                        "Description change",
                    ]
                )
        else:
            # New product
            append_rows.append([rec[h] for h in PRODUCT_HEADERS])
            diff_rows.append(
                [
                    rec.get(COL_DATE, ""),
                    rec[COL_RESTAURANT],
                    rec[COL_TYPE],
                    rec[COL_NAME],
                    "",
                    rec[COL_PRICE],
                    "",
                    rec[COL_DESCRIPTION],
                    "New product",
                ]
            )

    # Check for deletions: sheet → site
    for key, sheet_entry in sheet_records.items():

        if key not in site_records:

            is_delete = True

            old = sheet_entry["record"]
            diff_rows.append(
                [
                    old.get(COL_DATE, ""),
                    old.get(COL_RESTAURANT, ""),
                    old.get(COL_TYPE, ""),
                    old.get(COL_NAME, ""),
                    old.get(COL_PRICE, ""),
                    "",
                    old.get(COL_DESCRIPTION, ""),
                    "",
                    "Removed product",
                ]
            )

    logger.info(
        f"compare_products: {len(append_rows)} new, "
        f"{len(update_rows)} updates, {len(diff_rows)} diffs"
    )
    return append_rows, update_rows, diff_rows, is_delete


def get_rows_to_delete(
    site_records: Dict[Tuple[str, str, str], dict],
    sheet_records: Dict[Tuple[str, str, str], dict],
) -> List[int]:
    """
    Get rows to delete from the sheet based on site records
    """
    del_rows: List[int] = []

    # Check for deletions: sheet → site
    for key, sheet_entry in sheet_records.items():
        if key not in site_records:
            row = sheet_entry["row"]
            del_rows.append(row)

    return del_rows
