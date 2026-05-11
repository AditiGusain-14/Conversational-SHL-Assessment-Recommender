import json
import chromadb
from sentence_transformers import SentenceTransformer

# ---------------- LOAD MODEL ----------------

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# ---------------- LOAD DATA ----------------

with open("data/catalog_enriched.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# ---------------- CHROMA CLIENT ----------------

client = chromadb.PersistentClient(path="data/chroma_db")

# Drop and recreate to avoid duplicates on re-run
try:
    client.delete_collection("shl_catalog")
except:
    pass

collection = client.create_collection(
    name="shl_catalog",
    metadata={"hnsw:space": "cosine"}
)

# ---------------- EMBED PRODUCTS ----------------

documents = []
metadatas = []
ids = []

for idx, product in enumerate(products):

    retrieval_text = product.get("retrieval_text", "")
    documents.append(retrieval_text)

    metadata = {
        "name": product.get("name", ""),
        "url": product.get("url", ""),
        "test_type": product.get("test_type", ""),
        "test_type_code": product.get("test_type_code", ""),
        "duration": str(product.get("duration", "")),
        "remote_testing": str(product.get("remote_testing", False)),
        "job_levels": ", ".join(product.get("job_levels", [])),
    }

    metadatas.append(metadata)
    ids.append(str(idx))

print("Generating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True,
    normalize_embeddings=True
).tolist()

print("Saving to ChromaDB...")

collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

print("\nDONE.")
print(f"Embedded products: {len(products)}")