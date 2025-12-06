from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class AudioGeneration(Base):
    __tablename__ = "audio_generations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    text_content = Column(Text, nullable=False)
    audio_url = Column(Text, nullable=True)
    audio_data = Column(LargeBinary, nullable=True)  # Para almacenar base64
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audio_generations")
    study_session = relationship("StudySession", back_populates="audio_generations")