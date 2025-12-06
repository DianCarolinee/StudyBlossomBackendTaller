from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class EducationalVideo(Base):
    __tablename__ = "educational_videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(255), nullable=False)
    duration = Column(String(20), nullable=False)  # short, medium, long
    script = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    key_points = Column(JSONB, nullable=True)
    video_url = Column(Text, nullable=False)
    video_id = Column(String(255), nullable=False, index=True)
    thumbnail_url = Column(Text, nullable=True)
    estimated_duration = Column(String(50), nullable=True)
    status = Column(String(50), default='done')  # created, processing, done, error
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="educational_videos")
    study_session = relationship("StudySession", back_populates="educational_videos")