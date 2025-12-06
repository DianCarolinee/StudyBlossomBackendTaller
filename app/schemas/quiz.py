from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


class QuizQuestionSchema(BaseModel):
    question: str
    options: List[str]
    correct_answer: str


class QuizGenerationRequest(BaseModel):
    flashcards: List[dict]  # [{question: str, answer: str}]


class QuizGenerationResponse(BaseModel):
    questions: List[QuizQuestionSchema]


class QuizSessionCreate(BaseModel):
    study_session_id: Optional[uuid.UUID] = None
    topic: str
    questions: List[QuizQuestionSchema]


class QuizSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    topic: str
    total_questions: int
    correct_answers: int
    score: Optional[float]
    completed_at: datetime

    class Config:
        from_attributes = True


class QuizAnswerCreate(BaseModel):
    quiz_question_id: uuid.UUID
    user_answer: Optional[str]
    is_correct: bool