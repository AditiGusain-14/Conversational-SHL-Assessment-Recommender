import os
import re

from dotenv import load_dotenv
load_dotenv()

# ── HuggingFace auth (must happen before SentenceTransformer loads) ───────────
hf_token = os.environ.get("HF_TOKEN", "")
if hf_token:
    from huggingface_hub import login
    login(token=hf_token, add_to_git_credential=False)

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

# ---------------- HYBRID SEARCH ----------------

def hybrid_search(
    query,
    skills=None,
    personality_required=False,
    top_k=6
):

    if skills is None:
        skills = []

    # ---------------- SEMANTIC SEARCH ----------------

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=25
    )

    ranked_results = []

    if not results:
        return []

    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    for doc, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Lower distance = better similarity
        semantic_score = 1 / (1 + distance)

        # ---------------- KEYWORD MATCH ----------------

        keyword_hits = 0

        doc_words = set(
            re.findall(r"\b\w+\b", doc.lower())
        )

        for skill in skills:

            skill_words = re.findall(
                r"\b\w+\b",
                skill.lower()
            )

            if all(word in doc_words for word in skill_words):
                keyword_hits += 1

        keyword_score = (
            keyword_hits / max(len(skills), 1)
        )

        # ---------------- RULE BOOSTS ----------------

        boost = 0

        if (
            personality_required
            and metadata["test_type"]
            == "Personality & Behavior"
        ):
            boost += 0.25

        # ---------------- FINAL SCORE ----------------

        final_score = (
            0.85 * semantic_score
            + 0.15 * keyword_score
            + boost
        )

        ranked_results.append({
            "name":      metadata["name"],
            "url":       metadata["url"],
            "test_type": metadata["test_type"],
            "duration":  metadata["duration"],
            "score":     final_score
            
        })
        
    # ---------------- SORT ----------------

    ranked_results = sorted(
        ranked_results,
        key=lambda x: x["score"],
        reverse=True
    )

    # ---------------- DIVERSIFICATION ----------------

    if personality_required:

        personality_results = [
            r for r in ranked_results
            if r["test_type"] == "Personality & Behavior"
        ]

        technical_results = [
            r for r in ranked_results
            if r["test_type"] != "Personality & Behavior"
        ]

        ranked_results = (
            personality_results[:3]
            + technical_results[:7]
        )

    return ranked_results[:top_k]


# ---------------- TEST ----------------

if __name__ == "__main__":

    results = hybrid_search(
        query="Java developer assessment",
        skills=["Java", "Programming"],
        personality_required=False
    )

    print("\nRESULTS:\n")

    for idx, result in enumerate(results):

        print(f"{idx+1}. {result['name']}")
        print(f"Type: {result['test_type']}")
        print(f"Score: {round(result['score'], 4)}")
        print(result["url"])

        print("-" * 80)