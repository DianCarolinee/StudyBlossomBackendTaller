from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardResponse,
    FlashcardReviewCreate,
    FlashcardBatchResponse,
    FlashcardGenerationRequest
)
from app.controllers.flashcard_controller import FlashcardController
from app.utils.dependencies import get_current_user
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/generate", response_model=FlashcardBatchResponse)
async def generate_flashcards(
    request: FlashcardGenerationRequest,
    study_session_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera flashcards usando IA
    """
    return await FlashcardController.generate_flashcards(
        db, request.topic, current_user, study_session_id
    )


@router.post("/", response_model=FlashcardResponse, status_code=201)
def create_flashcard(
    flashcard_data: FlashcardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una flashcard manualmente
    """
    return FlashcardController.create_flashcard(db, flashcard_data, current_user)


@router.get("/", response_model=List[FlashcardResponse])
def get_flashcards(
    topic: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las flashcards del usuario
    """
    return FlashcardController.get_user_flashcards(db, current_user, topic, skip, limit)


@router.post("/review")
def review_flashcard(
    review_data: FlashcardReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra una revisión de flashcard
    """
    return FlashcardController.review_flashcard(db, review_data, current_user)


@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una flashcard
    """
    return FlashcardController.delete_flashcard(db, flashcard_id, current_user)