from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class VoiceConversation(Base):
    __tablename__ = "voice_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_message_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="voice_conversations")
    study_session = relationship("StudySession", back_populates="voice_conversations")
    messages = relationship("VoiceConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class VoiceConversationMessage(Base):
    __tablename__ = "voice_conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("voice_conversations.id", ondelete="CASCADE"),
                             nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    audio_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    conversation = relationship("VoiceConversation", back_populates="messages")