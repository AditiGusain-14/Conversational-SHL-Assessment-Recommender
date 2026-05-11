import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

TYPE_MAPPING = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

all_products = []

start = 0

while True:

    page_url = f"{CATALOG_URL}?start={start}&type=1"

    print(f"\nScraping: {page_url}")

    response = requests.get(page_url, headers=HEADERS)

    if response.status_code != 200:
        print("FAILED:", response.status_code)
        break

    soup = BeautifulSoup(response.text, "lxml")

    rows = soup.find_all("tr", attrs={"data-entity-id": True})

    if not rows:
        print("No more products found.")
        break

    print(f"Found {len(rows)} products")

    for row in rows:

        title_cell = row.find("td", class_="custom__table-heading__title")

        if not title_cell:
            continue

        link = title_cell.find("a")

        if not link:
            continue

        name = link.get_text(strip=True)

        relative_url = str(link.get("href", ""))
        full_url = BASE_URL + relative_url

        key_span = row.find("span", class_="product-catalogue__key")

        test_key = key_span.get_text(strip=True) if key_span else ""

        test_type = TYPE_MAPPING.get(test_key, "Unknown")

        product = {
            "name": name,
            "url": full_url,
            "test_type_code": test_key,
            "test_type": test_type
        }

        all_products.append(product)

    start += 12

    time.sleep(1)

print(f"\nTOTAL PRODUCTS SCRAPED: {len(all_products)}")

with open("data/catalog.json", "w", encoding="utf-8") as f:
    json.dump(all_products, f, indent=2, ensure_ascii=False)

print("\nSaved to data/catalog.json")