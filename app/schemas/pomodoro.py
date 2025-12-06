from pydantic import BaseModel
from typing import List


class Source(BaseModel):
    title: str
    url: str
    type: str  # video, article, book, documentation


class Recommendation(BaseModel):
    sub_topic: str
    sources: List[Source]


class PomodoroRecommendationsRequest(BaseModel):
    topic: str


class PomodoroRecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]