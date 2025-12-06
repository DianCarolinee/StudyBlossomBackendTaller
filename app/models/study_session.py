from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    study_goal_id = Column(UUID(as_uuid=True), ForeignKey("study_goals.id", ondelete="SET NULL"), nullable=True)
    goal_name = Column(String(100), nullable=False)
    topic = Column(Text, nullable=False)
    mode = Column(String(50), nullable=False, index=True)  # text, visual, audio, map, pomodoro, voice-tutor, video
    study_time = Column(Integer, nullable=True)
    xp_earned = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="study_sessions")
    study_goal = relationship("StudyGoal", back_populates="study_sessions")
    flashcards = relationship("Flashcard", back_populates="study_session")
    quiz_sessions = relationship("QuizSession", back_populates="study_session")
    concept_maps = relationship("ConceptMap", back_populates="study_session")
    feynman_sessions = relationship("FeynmanSession", back_populates="study_session")
    audio_generations = relationship("AudioGeneration", back_populates="study_session")
    educational_videos = relationship("EducationalVideo", back_populates="study_session")
    voice_conversations = relationship("VoiceConversation", back_populates="study_session")