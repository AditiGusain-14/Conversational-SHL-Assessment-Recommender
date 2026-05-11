from pydantic import BaseModel
from typing import List


# ---------------- MESSAGE ----------------

class Message(BaseModel):

    role: str
    content: str


# ---------------- REQUEST ----------------

class RecommendationRequest(BaseModel):

    messages: List[Message]


# ---------------- RECOMMENDATION ----------------

class RecommendationItem(BaseModel):

    name: str
    url: str
    test_type: str
    duration: str | int | None


# ---------------- RESPONSE ----------------

class RecommendationResponse(BaseModel):

    reply: str
    compare_table: str
    recommendations: List[RecommendationItem]
    end_of_conversation: bool