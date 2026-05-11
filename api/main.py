from fastapi import FastAPI

from api.schemas import (
    RecommendationRequest,
    RecommendationResponse
)

from agent.recommender import (
    recommend_from_conversation
)

app = FastAPI(
    title="SHL Assessment Recommender"
)


@app.get("/")
def root():

    return {
        "message": (
            "SHL Recommendation API Running"
        )
    }


@app.post(
    "/chat",
    response_model=RecommendationResponse
)
def recommend(
    request: RecommendationRequest
):

    response = recommend_from_conversation(
        [
            {
                "role": m.role,
                "content": m.content
            }
            for m in request.messages
        ]
    )

    return response


@app.get("/health")
def health():

    return {
        "status": "ok"
    }