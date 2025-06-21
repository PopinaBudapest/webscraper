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
    output = []

    stop_section = soup.find(
        lambda tag: tag.name == "h2" and "olasz ízvilágú salátáink" in tag.text.lower()
    )
    stop_parent = stop_section.find_parent("section") if stop_section else None

    for section in soup.select("section"):
        if section == stop_parent:
            break

        for card in section.select("div.eael-infobox"):
            name_tag = card.select_one("h2.title")
            desc_tag = card.select_one(".infobox-content p")
            price_tag = card.select_one(".infobox-button-text")

            if not (name_tag and desc_tag and price_tag):
                continue

            name = name_tag.get_text(strip=True).title()
            if "pisztácia" in name.lower():
                continue

            description = desc_tag.get_text(" ", strip=True)
            price_text = (
                price_tag.get_text(strip=True)
                .replace("Ft", "")
                .replace(".", "")
                .replace(" ", "")
            )
            try:
                price = int(price_text)
            except ValueError:
                continue

            output.append(
                {
                    COL_RESTAURANT: site_meta["restaurant"],
                    COL_TYPE: site_meta["product_type"],
                    COL_NAME: name,
                    COL_PRICE: price,
                    COL_DESCRIPTION: description,
                }
            )

    return output
