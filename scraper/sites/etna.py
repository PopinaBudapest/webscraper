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


def pizzaparse(html: str, site_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the Pizza menu HTML into a list of product records.
    Cleans whitespace, skips duplicates, and extracts price, name, description.
    Handles split price components (e.g., '28' and '00.-' => 2800).
    Ensures the primary (non-GM) price is selected correctly.
    """
    soup = BeautifulSoup(html, "html.parser")
    items: List[Dict[str, Any]] = []
    seen_names = set()

    for header in soup.select('p.MsoNormal[align="center"], div[align="center"]'):
        header_text = header.get_text(separator=" ", strip=True)
        gm_pos = header_text.find("GM")

        # Attempt to extract primary price (exclude any after 'GM')
        price = None
        for match in re.finditer(r"(\d+)(?=\.-)", header_text):
            val = int(match.group(1))
            if val <= 0:
                continue
            if gm_pos != -1 and match.start() > gm_pos:
                # Skip prices in the GM section
                continue
            price = val
            break

        # Fallback: combine split price parts before any 'GM' marker
        if price is None:
            part = header_text.split("GM")[0]
            nums = re.findall(r"\d+", part)
            if len(nums) >= 2:
                high, low = nums[-2], nums[-1]
                factor = 10 ** len(low)
                price = int(high) * factor + int(low)

        if price is None or price <= 0:
            continue

        # Extract product name: prefer colored span, fallback to first non-numeric span
        name = None
        colored = header.select_one('span[style*="rgb(189, 148, 0)"]')
        if colored:
            name = colored.get_text(strip=True)
        else:
            for span in header.find_all("span"):
                txt = span.get_text(strip=True)
                if txt and not re.search(r"[\d\.\-]", txt):
                    name = txt
                    break
        name = re.sub(r"\s+", " ", name or "N/A").strip()
        if name in seen_names:
            continue
        seen_names.add(name)

        # Find next sibling for description
        desc_tag = header.find_next_sibling(
            lambda tag: tag.name in ("p", "div") and tag.get("align") == "center"
        )
        description = ""
        if desc_tag:
            desc_raw = desc_tag.get_text(separator=" ", strip=True)
            description = re.sub(r"\s+", " ", desc_raw).strip()

        items.append(
            {
                COL_RESTAURANT: site_meta.get("restaurant"),
                COL_TYPE: site_meta.get("product_type"),
                COL_NAME: name,
                COL_PRICE: price,
                COL_DESCRIPTION: description,
            }
        )

    return items


def pastaparse(html: str, site_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse the Pasta menu HTML into a list of pasta product records."""
    soup = BeautifulSoup(html, "html.parser")
    items: List[Dict[str, Any]] = []
    seen_names = set()

    # Iterate over centered paragraphs/divs that contain prices
    for header in soup.find_all(['p', 'div'], attrs={'align': 'center'}):
        header_text = header.get_text(separator=" ", strip=True)

        # Skip group headings and footers
        if re.search(r'alapú', header_text, re.I) or re.search(r"©|all rights|web by|design by", header_text, re.I):
            continue

        # Locate first price before any 'GM' marker
        gm_pos = header_text.find('GM')
        price_match = None
        for m in re.finditer(r"(\d{3,4})", header_text):
            if gm_pos != -1 and m.start() > gm_pos:
                continue
            price_match = m
            break
        if not price_match:
            continue
        price = int(price_match.group(1))

        # Extract name
        name_part = header_text[:price_match.start()].strip()
        name_part = re.sub(r'\bN\.\s*', '', name_part)
        name_part = re.sub(r'\s+N\.?$', '', name_part).strip()
        name = re.sub(r"\s+", " ", name_part)
        if not name or name in seen_names:
            continue
        seen_names.add(name)

        # Description via sibling tag
        description = ''
        sib = header.find_next_sibling()
        while sib:
            if getattr(sib, 'get', None) and sib.get('align') == 'center':
                txt = sib.get_text(separator=' ', strip=True)
                # Normalize any residual line breaks
                txt = txt.replace('\r', ' ').replace('\n', ' ')
                # Skip footers or price markers
                if re.search(r"\d{3,4}", txt) or re.search(r"\.-", txt) or re.search(r"GM", txt) or re.search(r"Nem elérhető", txt, re.I):
                    break
                # Remove sauce label and collapse whitespace
                desc = re.sub(r'^(?:paradicsom alapú|tejszín alapú)\s*:?', '', txt, flags=re.I)
                desc = re.sub(r"\s+", " ", desc).strip()
                description = desc
                break
            sib = sib.find_next_sibling()

        # Inline fallback if no sibling description
        if not description:
            post_price = header_text[price_match.end():]
            post_price = post_price.replace('\r', ' ').replace('\n', ' ')
            inline_desc = re.sub(r'^(?:paradicsom alapú|tejszín alapú)\s*:?', '', post_price, flags=re.I)
            inline_desc = re.sub(r"\s+", " ", inline_desc).strip()
            description = inline_desc

        items.append({
            COL_RESTAURANT: site_meta.get('restaurant'),
            COL_TYPE: site_meta.get('product_type'),
            COL_NAME: name,
            COL_PRICE: price,
            COL_DESCRIPTION: description,
        })

    return items