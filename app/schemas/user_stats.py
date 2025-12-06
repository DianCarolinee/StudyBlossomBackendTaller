from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid


class UserStatsResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    total_xp: int
    current_level: int
    current_streak: int
    longest_streak: int
    total_sessions: int
    total_study_time: int
    last_study_date: Optional[date]
    plant_stage: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStatsUpdate(BaseModel):
    total_xp: Optional[int] = None
    current_level: Optional[int] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    total_sessions: Optional[int] = None
    total_study_time: Optional[int] = None
    last_study_date: Optional[date] = None
    plant_stage: Optional[int] = None