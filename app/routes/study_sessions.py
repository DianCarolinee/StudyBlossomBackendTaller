from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.study_session import StudySessionCreate, StudySessionResponse
from app.controllers.study_session_controller import StudySessionController
from app.utils.dependencies import get_current_user
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/", response_model=StudySessionResponse, status_code=201)
def create_study_session(
    session_data: StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva sesión de estudio
    """
    return StudySessionController.create_session(db, session_data, current_user)


@router.get("/", response_model=List[StudySessionResponse])
def get_study_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    mode: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las sesiones de estudio del usuario
    """
    return StudySessionController.get_user_sessions(db, current_user, skip, limit, mode)


@router.get("/{session_id}", response_model=StudySessionResponse)
def get_study_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una sesión de estudio por ID
    """
    return StudySessionController.get_session_by_id(db, session_id, current_user)


@router.delete("/{session_id}")
def delete_study_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una sesión de estudio
    """
    return StudySessionController.delete_session(db, session_id, current_user)