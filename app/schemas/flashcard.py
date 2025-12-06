from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


class FlashcardBase(BaseModel):
    question: str
    answer: str
    topic: Optional[str] = None


class FlashcardCreate(FlashcardBase):
    study_session_id: Optional[uuid.UUID] = None


class FlashcardResponse(FlashcardBase):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    times_reviewed: int
    times_correct: int
    created_at: datetime

    class Config:
        from_attributes = True


class FlashcardBatchResponse(BaseModel):
    flashcards: List[FlashcardResponse]


class FlashcardReviewCreate(BaseModel):
    flashcard_id: uuid.UUID
    learned: bool


class FlashcardGenerationRequest(BaseModel):
    topic: str


class FlashcardGenerationResponse(BaseModel):
    flashcards: List[dict]  # [{question: str, answer: str}]