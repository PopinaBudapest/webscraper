import asyncio
import json
from typing import Dict, List
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)


async def _fetch_pizzahut_json(url: str) -> Dict:

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        result = {}

        async def handle_response(response):

            DEBUG = False

            try:
                if "/menu/TAKEAWAY/" in response.url and response.status == 200:
                    text = await response.text()
                    if not text.strip().startswith("{"):
                        return
                    full_json = json.loads(text)

                    if DEBUG:  # Save JSON to file
                        with open("pizzahut_raw.json", "w", encoding="utf-8") as f:
                            json.dump(full_json, f, ensure_ascii=False, indent=2)

                    if "menu" in full_json:
                        result.update(full_json["menu"])
            except Exception as e:
                logger.warning("Error in response handler: %s", e)

        page.on("response", handle_response)

        await page.goto(url, wait_until="networkidle")

        await page.wait_for_timeout(5000)
        await browser.close()

        if not result:
            raise RuntimeError("No menu data found")

        return result


def fetch_menu_data(url: str) -> Dict:
    return asyncio.run(_fetch_pizzahut_json(url))


def parse(html: str, metadata: Dict[str, str]) -> List[Dict[str, any]]:

    data = fetch_menu_data(html)

    records = []
    for category in data.get("categories", []):
        cat_id = category.get("id")
        if cat_id not in {3, 2388}:
            continue

        product_type = "pizza" if cat_id == 3 else "pasta"

        for item in category.get("products", {}).values():

            if "price" in item:
                try:
                    price = int(float(item["price"]))
                except (ValueError, TypeError):
                    price = 0

            if price < 2000:
                continue

            record = {
                "Restaurant": metadata["restaurant"],
                "Type": product_type,
                "Name": item.get("name", "").title().strip(),
                "Price": price,
                "Description": item.get("description", "").strip(),
            }
            records.append(record)

    return records
