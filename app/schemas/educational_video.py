from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class EducationalVideoRequest(BaseModel):
    topic: str
    duration: str = Field(..., pattern="^(short|medium|long)$")


class EducationalVideoResponse(BaseModel):
    video_url: str
    video_id: str
    script: str
    title: str
    key_points: List[str]
    estimated_duration: str
    thumbnail_url: Optional[str] = None
    status: str


class EducationalVideoCreate(BaseModel):
    topic: str
    duration: str
    study_session_id: Optional[uuid.UUID] = None
    script: str
    title: str
    key_points: Optional[List[str]] = None
    video_url: str
    video_id: str
    thumbnail_url: Optional[str] = None
    estimated_duration: str
    status: str = "done"


class EducationalVideoDBResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    topic: str
    duration: str
    script: str
    title: str
    key_points: Optional[List[str]]
    video_url: str
    video_id: str
    thumbnail_url: Optional[str]
    estimated_duration: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True