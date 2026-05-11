import chromadb

from sentence_transformers import SentenceTransformer

# ---------------- LOAD MODEL ----------------

model = SentenceTransformer(
    "BAAI/bge-base-en-v1.5"
)

# ---------------- LOAD CHROMADB ----------------

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_collection(
    name="shl_catalog"
)

# ---------------- SEARCH FUNCTION ----------------

def semantic_search(query, top_k=6):

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results


# ---------------- TEST QUERY ----------------

query = "Java developer assessment"

results = semantic_search(query)

print("\nQUERY:")
print(query)

print("\nRESULTS:\n")

documents = results.get("documents", [[]])
metadatas = results.get("metadatas", [[]])

if not documents or not documents[0]:
    print("No results found.")
else:

    for i in range(len(documents[0])):

        metadata = metadatas[0][i]

        print(f"{i+1}. {metadata['name']}")
        print(f"Type: {metadata['test_type']}")
        print(f"Duration: {metadata['duration']}")
        print(metadata["url"])

        print("-" * 80)