from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.voice_tutor import (
    VoiceTutorRequest,
    VoiceTutorResponse,
    VoiceConversationCreate,
    VoiceConversationResponse,
    VoiceMessageCreate,
    VoiceMessageResponse
)
from app.services.voice_tutor_service import voice_tutor_service
from app.models.voice_conversation import VoiceConversation, VoiceConversationMessage
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import List
import uuid

router = APIRouter()


@router.post("/ask", response_model=VoiceTutorResponse)
async def ask_voice_tutor(
        request: VoiceTutorRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Hace una pregunta al tutor de voz
    """
    try:
        response = await voice_tutor_service.ask_tutor(
            topic=request.topic,
            user_question=request.user_question,
            conversation_history=[msg.model_dump() for msg in request.conversation_history]
        )
        return VoiceTutorResponse(**response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/conversations", response_model=VoiceConversationResponse, status_code=201)
def create_voice_conversation(
        conversation_data: VoiceConversationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva conversación de voz
    """
    new_conversation = VoiceConversation(
        user_id=current_user.id,
        study_session_id=conversation_data.study_session_id,
        topic=conversation_data.topic
    )

    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)

    return VoiceConversationResponse.model_validate(new_conversation)


@router.post("/conversations/{conversation_id}/messages", response_model=VoiceMessageResponse, status_code=201)
def add_message_to_conversation(
        conversation_id: uuid.UUID,
        message_data: VoiceMessageCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Añade un mensaje a una conversación
    """
    # Verificar que la conversación existe y pertenece al usuario
    conversation = db.query(VoiceConversation).filter(
        VoiceConversation.id == conversation_id,
        VoiceConversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )

    new_message = VoiceConversationMessage(
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        audio_url=message_data.audio_url
    )

    db.add(new_message)

    # Actualizar última fecha de mensaje
    conversation.last_message_at = new_message.created_at

    db.commit()
    db.refresh(new_message)

    return VoiceMessageResponse.model_validate(new_message)


@router.get("/conversations", response_model=List[VoiceConversationResponse])
def get_user_conversations(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene las conversaciones del usuario
    """
    conversations = db.query(VoiceConversation).filter(
        VoiceConversation.user_id == current_user.id
    ).order_by(VoiceConversation.last_message_at.desc()).offset(skip).limit(limit).all()

    return [VoiceConversationResponse.model_validate(c) for c in conversations]


@router.get("/conversations/{conversation_id}/messages", response_model=List[VoiceMessageResponse])
def get_conversation_messages(
        conversation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene los mensajes de una conversación
    """
    # Verificar que la conversación pertenece al usuario
    conversation = db.query(VoiceConversation).filter(
        VoiceConversation.id == conversation_id,
        VoiceConversation.user_id == current_user.id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )

    messages = db.query(VoiceConversationMessage).filter(
        VoiceConversationMessage.conversation_id == conversation_id
    ).order_by(VoiceConversationMessage.created_at.asc()).offset(skip).limit(limit).all()

    return [VoiceMessageResponse.model_validate(m) for m in messages]