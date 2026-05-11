import json

with open("data/catalog_enriched.json", encoding="utf-8") as f:
    catalog = json.load(f)

remote_true = sum(1 for p in catalog if p.get("remote_testing"))
no_desc = sum(1 for p in catalog if not p.get("description"))
no_duration = sum(1 for p in catalog if p.get("duration") is None)

print(f"Total: {len(catalog)}")
print(f"Remote testing = True: {remote_true}")
print(f"Missing description: {no_desc}")
print(f"Missing duration: {no_duration}")

# Spot check one entry
print("\nSample entry:")
import json
print(json.dumps(catalog[127], indent=2, ensure_ascii=False))