import json
import os

from agent.recommender import (
    recommend_from_conversation
)

from evaluation.metrics import recall_at_k


TRACE_DIR = "evaluation/public_traces"


def load_traces():

    traces = []

    for file in os.listdir(TRACE_DIR):

        if file.endswith(".json"):

            path = os.path.join(
                TRACE_DIR,
                file
            )

            with open(path, "r", encoding="utf-8") as f:
                traces.append(json.load(f))

    return traces


def evaluate():

    traces = load_traces()

    scores = []

    for trace in traces:

        messages = trace["messages"]

        expected = trace["expected_assessments"]

        response = recommend_from_conversation(
            messages
        )

        predicted = [
            r["name"]
            for r in response["recommendations"]
        ]

        score = recall_at_k(
            expected,
            predicted,
            k=6
        )

        scores.append(score)

        print("\nTRACE:")
        print(trace.get("id", "unknown"))

        print("Recall@10:", round(score, 3))

    avg_score = sum(scores) / max(len(scores), 1)

    print("\nAVERAGE RECALL@10:")
    print(round(avg_score, 3))


if __name__ == "__main__":

    evaluate()