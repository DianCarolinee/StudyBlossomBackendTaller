from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class AudioGenerationRequest(BaseModel):
    text: str


class AudioGenerationResponse(BaseModel):
    media: str  # data URI base64


class AudioGenerationCreate(BaseModel):
    text_content: str
    study_session_id: Optional[uuid.UUID] = None
    audio_data: Optional[str] = None  # base64
    duration_seconds: Optional[int] = None


class AudioGenerationDBResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    text_content: str
    audio_url: Optional[str]
    duration_seconds: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True