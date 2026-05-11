def recall_at_k(expected, predicted, k=6):

    predicted_k = predicted[:k]

    hits = len(
        set(expected) & set(predicted_k)
    )

    return hits / max(len(expected), 1)