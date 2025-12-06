from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class FeynmanExplanationRequest(BaseModel):
    topic: str


class FeynmanExplanationResponse(BaseModel):
    explanation: str


class FeynmanAnalysisRequest(BaseModel):
    topic: str
    user_explanation: str


class FeynmanAnalysisResponse(BaseModel):
    gaps: str
    simplifications: str


class FeynmanSessionCreate(BaseModel):
    topic: str
    study_session_id: Optional[uuid.UUID] = None
    ai_explanation: str
    user_explanation: Optional[str] = None
    feedback_gaps: Optional[str] = None
    feedback_simplifications: Optional[str] = None


class FeynmanSessionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    topic: str
    ai_explanation: str
    user_explanation: Optional[str]
    feedback_gaps: Optional[str]
    feedback_simplifications: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True