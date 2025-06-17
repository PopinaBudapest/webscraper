import re
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from scraper.storage.sheet_constants import (
    COL_RESTAURANT,
    COL_TYPE,
    COL_NAME,
    COL_PRICE,
    COL_DESCRIPTION,
)


def parse(html: str, site_meta: Dict[str, Any]) -> List[Dict[str, Any]]:

    soup = BeautifulSoup(html, "html.parser")
    items = []

    for box in soup.select(".menu-item-box"):

        # Name
        name_tag = box.select_one(".menu-item-maintitle span")
        product_name = name_tag.get_text(strip=True) if name_tag else "N/A"

        # Description
        desc_tag = box.select_one(".menu-item-component")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        # Find all price blocks
        price_tags = box.select(".menu-item-price")
        all_price_text = " ".join(tag.get_text() for tag in price_tags)

        # Extract all numbers from combined price text
        numbers = re.findall(r"\d+", all_price_text)
        price = int(numbers[-1]) if numbers else 0

        items.append(
            {
                COL_RESTAURANT: site_meta.get("restaurant"),
                COL_TYPE: site_meta.get("product_type"),
                COL_NAME: product_name,
                COL_PRICE: price,
                COL_DESCRIPTION: description,
            }
        )

    return items
