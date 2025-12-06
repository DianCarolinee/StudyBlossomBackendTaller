from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.audio import (
    AudioGenerationRequest,
    AudioGenerationResponse,
    AudioGenerationCreate,
    AudioGenerationDBResponse
)
from app.services.audio_service import audio_service
from app.models.audio_generation import AudioGeneration
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/generate", response_model=AudioGenerationResponse)
async def generate_audio(
        request: AudioGenerationRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Genera audio a partir de texto usando TTS
    """
    try:
        audio_data_uri = await audio_service.generate_audio(request.text)
        return AudioGenerationResponse(media=audio_data_uri)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/save", response_model=AudioGenerationDBResponse, status_code=201)
def save_audio_generation(
        audio_data: AudioGenerationCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Guarda una generación de audio en la base de datos
    """
    new_audio = AudioGeneration(
        user_id=current_user.id,
        study_session_id=audio_data.study_session_id,
        text_content=audio_data.text_content,
        audio_data=audio_data.audio_data.encode() if audio_data.audio_data else None,
        duration_seconds=audio_data.duration_seconds
    )

    db.add(new_audio)
    db.commit()
    db.refresh(new_audio)

    return AudioGenerationDBResponse.model_validate(new_audio)


@router.get("/history")
def get_audio_history(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene el historial de generaciones de audio
    """
    audios = db.query(AudioGeneration).filter(
        AudioGeneration.user_id == current_user.id
    ).order_by(AudioGeneration.created_at.desc()).offset(skip).limit(limit).all()

    return [AudioGenerationDBResponse.model_validate(a) for a in audios]