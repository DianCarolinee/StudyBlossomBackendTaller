from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid


class ConversationMessage(BaseModel):
    role: str  # user, assistant
    content: str


class VoiceTutorRequest(BaseModel):
    topic: str
    user_question: str
    conversation_history: Optional[List[ConversationMessage]] = []


class VoiceTutorResponse(BaseModel):
    text_response: str
    audio_response: str  # data URI base64
    follow_up_suggestions: List[str]


class VoiceConversationCreate(BaseModel):
    topic: str
    study_session_id: Optional[uuid.UUID] = None


class VoiceConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    topic: str
    created_at: datetime
    last_message_at: datetime

    class Config:
        from_attributes = True


class VoiceMessageCreate(BaseModel):
    conversation_id: uuid.UUID
    role: str
    content: str
    audio_url: Optional[str] = None


class VoiceMessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    audio_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True