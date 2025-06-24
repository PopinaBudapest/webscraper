import os
import logging
import requests
from typing import Any, Dict, List
from requests.exceptions import RequestException
from .sites import SITES, SITES_TO_TEST

logger = logging.getLogger(__name__)


def _fetch_html(site: Dict[str, any]) -> str:

    DEBUG = False

    response = requests.get(site["url"], timeout=10)
    response.raise_for_status()
    html = response.text

    if DEBUG:
        _save_html(html, "site.html")

    return html


def get_site_records(scope: str = "prod") -> List[Dict[str, Any]]:
    """Fetch and parse new records from all configured sites."""

    raw_site_records = []

    if scope == "test":
        sites = SITES_TO_TEST
    elif scope == "prod":
        sites = SITES
    else:
        raise ValueError(f"Invalid scope: {scope!r}. Use 'prod' or 'test'.")

    for site in sites:

        try:

            if site.get("needs_playwright"):
                html = site["url"]  # No html, url is needed
            else:
                html = _fetch_html(site)

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

        raw_site_records.extend(parsed)

    logger.info("Total new records fetched: %d", len(raw_site_records))

    return raw_site_records


def _save_html(html: str, filename: str) -> None:
    """Save HTML content to a file."""

    base_dir = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
    out_path = os.path.join(base_dir, filename)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info("Saved HTML to %s", out_path)
    except Exception as e:
        logger.warning("Could not save HTML to disk: %s", e)
