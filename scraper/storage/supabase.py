import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

def insert_products(items: list[dict], restaurant: str, product_type: str):
    url = f"{SUPABASE_URL}/rest/v1/products"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    payload = []
    for item in items:
        payload.append({
            "restaurant": restaurant,
            "product_type": product_type,
            "product_name": item["product_name"],
            "price": item["price"],
            "description": item["description"],
            "fetched_at": datetime.utcnow().date().isoformat()
        })

    response = requests.post(url, json=payload, headers=headers)
    if not response.ok:
        print("Failed to insert:", response.text)
    else:
        print(f"Inserted {len(payload)} items successfully.")
