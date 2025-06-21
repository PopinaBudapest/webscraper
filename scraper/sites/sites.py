from typing import Dict, List

from scraper.parsers import bellozzo
from scraper.parsers import etna
from scraper.parsers import donnamamma


SITES: List[Dict[str,any]] = [
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
    {
        "id": "etna_pizza",
        "restaurant": "Etna",
        "product_type": "pizza",
        "url": "https://pastapizzatogo.hu/?n=view&sec=mypizza",
        "parser": etna.pizzaparse,
    },
    {
        "id": "etna_pasta",
        "restaurant": "Etna",
        "product_type": "pasta",
        "url": "https://pastapizzatogo.hu/?n=view&sec=pasta",
        "parser": etna.pastaparse,
    },
    {
        "id": "donnamamma_pizza",
        "restaurant": "Donna Mamma",
        "product_type": "pizza",
        "url": "https://www.donnamamma.hu/etlap/",
        "parser": donnamamma.parse,
    },
]


SITES_TO_TEST: List[Dict[str,any]] = [
    {
        "id": "donnamamma_pizza",
        "restaurant": "Donna Mamma",
        "product_type": "pizza",
        "url": "https://www.donnamamma.hu/etlap/",
        "parser": donnamamma.parse,
    },
]