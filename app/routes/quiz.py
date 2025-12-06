from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.quiz import (
    QuizGenerationRequest,
    QuizGenerationResponse,
    QuizSessionCreate,
    QuizSessionResponse,
    QuizAnswerCreate
)
from app.controllers.quiz_controller import QuizController
from app.utils.dependencies import get_current_user
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/generate", response_model=QuizGenerationResponse)
async def generate_quiz(
    request: QuizGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genera un quiz basado en flashcards
    """
    questions = await QuizController.generate_quiz(db, request.flashcards, current_user)
    return QuizGenerationResponse(questions=questions)


@router.post("/sessions", response_model=QuizSessionResponse, status_code=201)
def create_quiz_session(
    quiz_data: QuizSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una sesión de quiz
    """
    return QuizController.create_quiz_session(db, quiz_data, current_user)


@router.post("/answer")
def submit_quiz_answer(
    answer_data: QuizAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Registra una respuesta del usuario
    """
    return QuizController.submit_answer(db, answer_data, current_user)


@router.post("/sessions/{quiz_id}/complete", response_model=QuizSessionResponse)
def complete_quiz_session(
    quiz_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Completa un quiz y calcula el puntaje
    """
    return QuizController.complete_quiz(db, quiz_id, current_user)


@router.get("/sessions", response_model=List[QuizSessionResponse])
def get_quiz_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los quizzes del usuario
    """
    return QuizController.get_user_quizzes(db, current_user, skip, limit)