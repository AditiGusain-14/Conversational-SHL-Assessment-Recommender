import requests
from bs4 import BeautifulSoup
import json
import time

BASE_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean_text(text):
    return " ".join(text.split())

def scrape_detail(url: str) -> dict:
    response = requests.get(url, headers=BASE_HEADERS)
    soup = BeautifulSoup(response.text, "lxml")

    result = {
        "description": "",
        "duration": None,
        "remote_testing": False,
        "job_levels": [],
        "languages": [],
        "raw_page_text": "",
    }

    # Description
    for h4 in soup.find_all("h4"):
        if "Description" in h4.get_text():
            next_p = h4.find_next_sibling("p")
            if next_p:
                result["description"] = clean_text(next_p.get_text(" ", strip=True))
            break

    # Duration + Remote Testing
    for p in soup.find_all("p"):
        text = clean_text(p.get_text(" ", strip=True))

        if "Approximate Completion Time in minutes" in text:
            try:
                result["duration"] = int(text.split("=")[-1].strip())
            except ValueError:
                result["duration"] = text.split("=")[-1].strip()

        if "Remote Testing:" in text:
            span = p.find("span", class_="-yes")
            result["remote_testing"] = span is not None

    # Job levels
    for h4 in soup.find_all("h4"):
        if "Job levels" in h4.get_text():
            next_el = h4.find_next_sibling()
            if next_el:
                result["job_levels"] = [
                    clean_text(s)
                    for s in next_el.get_text(separator=",").split(",")
                    if s.strip()
                ]
            break

    # Languages
    for h4 in soup.find_all("h4"):
        if "Languages" in h4.get_text():
            next_el = h4.find_next_sibling()
            if next_el:
                result["languages"] = [
                    clean_text(s)
                    for s in next_el.get_text(separator=",").split(",")
                    if s.strip()
                ]
            break

    # Full page text for embeddings
    result["raw_page_text"] = clean_text(soup.get_text(" ", strip=True))

    return result


def make_retrieval_text(product: dict) -> str:
    return clean_text(f"""
Assessment: {product['name']}
Type: {product['test_type']}
Duration: {product.get('duration', 'Unknown')} minutes

Description:
{product.get('description', '')}

Job Levels: {', '.join(product.get('job_levels', []))}
Languages: {', '.join(product.get('languages', []))}
""")


if __name__ == "__main__":
    with open("data/catalog.json") as f:
        catalog = json.load(f)

    print(f"Enriching {len(catalog)} products...")

    for i, product in enumerate(catalog):
        print(f"[{i+1}/{len(catalog)}] {product['name']}")
        try:
            details = scrape_detail(product["url"])
            product.update(details)
            product["retrieval_text"] = make_retrieval_text(product)
        except Exception as e:
            print(f"  ERROR: {e}")
            product["retrieval_text"] = make_retrieval_text(product)

        time.sleep(0.8)

    with open("data/catalog_enriched.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print("\nDone. Saved to data/catalog_enriched.json")