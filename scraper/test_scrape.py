import requests
from bs4 import BeautifulSoup

url = "https://www.shl.com/solutions/products/product-catalog/"

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

# Search for possible catalog containers
keywords = [
    "product",
    "catalog",
    "assessment",
    "json",
    "api"
]

print("\nMATCHING TAGS:\n")

for tag in soup.find_all():
    tag_text = str(tag).lower()

    if any(keyword in tag_text for keyword in keywords):
        print("=" * 80)
        print(tag.name)

        snippet = str(tag)[:1000]
        print(snippet)
        print("\n")