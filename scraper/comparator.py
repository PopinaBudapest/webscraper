import logging
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from statistics import mean
from scraper.storage.sheet_constants import *

logger = logging.getLogger(__name__)


def get_product_changes(
    site_records: List[Dict[str, Any]],
    sheet_records: List[Dict[str, Any]],
) -> List[Dict[str, Optional[Any]]]:
    """Compare two inventories (site vs sheet) and return a list of change-rows"""

    today = date.today().isoformat()

    def key(rec: Dict[str, Any]) -> Tuple[str, str, str]:
        return (rec["Restaurant"], rec["Type"], rec["Name"])

    site_map = {key(r): r for r in site_records}
    sheet_map = {key(r): r for r in sheet_records}
    changes: List[Dict[str, Optional[Any]]] = []

    # 1) New products & updates
    for k, site_r in site_map.items():
        if k not in sheet_map:
            changes.append(
                {
                    COL_DATE: today,
                    COL_RESTAURANT: k[0],
                    COL_TYPE: k[1],
                    COL_NAME: k[2],
                    COL_OLD_PRICE: None,
                    COL_NEW_PRICE: site_r["Price"],
                    COL_OLD_DESCRIPTION: None,
                    COL_NEW_DESCRIPTION: site_r["Description"],
                    COL_COMMENT: "New Product",
                }
            )
        else:
            sheet_r = sheet_map[k]

            old_p = int(sheet_r["Price"])
            new_p = int(site_r["Price"])

            old_d = sheet_r["Description"].strip()
            new_d = site_r["Description"].strip()

            price_changed = old_p != new_p
            desc_changed = old_d != new_d

            if price_changed or desc_changed:
                row = {
                    COL_DATE: today,
                    COL_RESTAURANT: k[0],
                    COL_TYPE: k[1],
                    COL_NAME: k[2],
                    COL_COMMENT: "",
                }
                # Fill price columns only if price changed
                if price_changed:
                    row[COL_OLD_PRICE] = old_p
                    row[COL_NEW_PRICE] = new_p
                else:
                    row[COL_OLD_PRICE] = None
                    row[COL_NEW_PRICE] = None
                # Fill description columns only if description changed
                if desc_changed:
                    row[COL_OLD_DESCRIPTION] = old_d
                    row[COL_NEW_DESCRIPTION] = new_d
                else:
                    row[COL_OLD_DESCRIPTION] = None
                    row[COL_NEW_DESCRIPTION] = None

                # Build comment
                parts = []
                if price_changed:
                    parts.append("Price")
                if desc_changed:
                    parts.append("Description")
                row[COL_COMMENT] = " & ".join(parts) + " Changed"

                changes.append(row)

    # 2) Deleted products
    for k, sheet_r in sheet_map.items():
        if k not in site_map:
            changes.append(
                {
                    COL_DATE: today,
                    COL_RESTAURANT: k[0],
                    COL_TYPE: k[1],
                    COL_NAME: k[2],
                    COL_OLD_PRICE: sheet_r["Price"],
                    COL_NEW_PRICE: None,
                    COL_OLD_DESCRIPTION: sheet_r["Description"],
                    COL_NEW_DESCRIPTION: None,
                    COL_COMMENT: "Deleted Product",
                }
            )

    return changes


def get_type_averages(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate average, min, and max prices per (restaurant, type), with pizzas listed before pastas."""

    buckets: Dict[Tuple[str, str], List[int]] = defaultdict(list)

    for rec in records:
        key = (rec[COL_RESTAURANT], rec[COL_TYPE])
        buckets[key].append(rec[COL_PRICE])

    summary: List[Dict[str, Any]] = []

    def sort_key(item: Tuple[str, str]):
        restaurant, type_ = item
        return (0 if type_ == "pizza" else 1, restaurant, type_)

    for restaurant, product_type in sorted(buckets, key=sort_key):
        prices = buckets[(restaurant, product_type)]
        if not prices:
            continue

        summary.append(
            {
                COL_RESTAURANT: restaurant,
                COL_TYPE: product_type,
                COL_COUNT: len(prices),
                COL_AVERAGE: int(mean(prices)),
                COL_LOWEST: min(prices),
                COL_HIGHEST: max(prices),
            }
        )

    return summary
