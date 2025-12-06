from pydantic import BaseModel
from typing import List


class AidaEngagementRequest(BaseModel):
    topic: str


class AidaEngagementResponse(BaseModel):
    attention: str
    interest: str
    desire: List[str]