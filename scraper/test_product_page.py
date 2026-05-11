import requests
from bs4 import BeautifulSoup

url = "https://www.shl.com/solutions/products/product-catalog/view/ado-net-new/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers)

print("STATUS:", response.status_code)

soup = BeautifulSoup(response.text, "lxml")

# ---------------- HEADINGS ----------------

print("\n========== HEADINGS ==========\n")

for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
    text = tag.get_text(strip=True)

    if text:
        print(f"{tag.name}: {text}")

# ---------------- PARAGRAPHS ----------------

print("\n========== IMPORTANT PARAGRAPHS ==========\n")

keywords = [
    "minutes",
    "duration",
    "job",
    "skill",
    "test",
    "assessment",
    "remote",
    "adaptive"
]

for p in soup.find_all("p"):

    text = p.get_text(" ", strip=True)

    if any(keyword.lower() in text.lower() for keyword in keywords):

        print(text)
        print("-" * 80)

# ---------------- TABLES ----------------

print("\n========== TABLES ==========\n")

tables = soup.find_all("table")

print(f"TOTAL TABLES: {len(tables)}")

for table in tables[:3]:

    print(table.get_text(" ", strip=True)[:2000])

    print("=" * 80)