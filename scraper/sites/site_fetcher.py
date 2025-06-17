import logging
import requests
from typing import Any, Dict, List
from requests.exceptions import RequestException
from scraper.sites import bellozzo
from scraper.storage.sheet_constants import *

logger = logging.getLogger(__name__)

_SITES = [
    {
        "id": "bellozzo_pizza",
        "restaurant": "Bellozzo",
        "product_type": "pizza",
        "url": "https://www.bellozzo.hu/menunk/pizzak.html",
        "parser": bellozzo.parse,
    },
    {
        "id": "bellozzo_pasta",
        "restaurant": "Bellozzo",
        "product_type": "pasta",
        "url": "https://www.bellozzo.hu/menunk/tesztak.html",
        "parser": bellozzo.parse,
    },
]


def _fetch_html(url: str) -> str:
    """Fetch HTML content from a given URL."""

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def get_site_records() -> List[Dict[str, Any]]:
    """Fetch and parse new records from all configured sites."""

    raw_site_records = []

    for site in _SITES:

        try:
            html = _fetch_html(site["url"])
        except RequestException as e:
            logger.error("Network error fetching %s: %s", site["url"], e, exc_info=True)
            raise

        try:
            parsed = site["parser"](
                html,
                {
                    "restaurant": site["restaurant"],
                    "product_type": site["product_type"],
                },
            )
        except Exception as e:
            logger.error("Parse error on %s: %s", site["id"], e, exc_info=True)
            raise

        if not isinstance(parsed, list):
            raise ValueError(f"Parser {site['id']} returned non-list: {type(parsed)}")
        
        try:
            raw_site_records.extend(parsed)
        except Exception as e:
            logger.error(
                "Failed to accumulate records for %s: %s",
                site["id"], e,
                exc_info=True
            )
            raise

    logger.info("Total new records fetched: %d", len(raw_site_records))

    return raw_site_records
