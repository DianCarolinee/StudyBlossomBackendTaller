from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class ConceptMapCreate(BaseModel):
    topic: str
    study_session_id: Optional[uuid.UUID] = None


class ConceptMapResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    study_session_id: Optional[uuid.UUID]
    topic: str
    mermaid_graph: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConceptMapGenerationRequest(BaseModel):
    topic: str


class ConceptMapGenerationResponse(BaseModel):
    mermaid_graph: str