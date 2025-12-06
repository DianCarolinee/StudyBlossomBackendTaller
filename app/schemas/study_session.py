from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class StudySessionBase(BaseModel):
    study_goal_id: Optional[uuid.UUID] = None
    goal_name: str
    topic: str
    mode: str = Field(..., pattern="^(text|visual|audio|map|pomodoro|voice-tutor|video)$")
    study_time: Optional[int] = None


class StudySessionCreate(StudySessionBase):
    pass


class StudySessionResponse(StudySessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    xp_earned: int
    created_at: datetime

    class Config:
        from_attributes = True