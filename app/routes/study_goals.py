from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.study_goal import StudyGoalCreate, StudyGoalResponse, StudyGoalUpdate
from app.controllers.study_goal_controller import StudyGoalController
from app.utils.dependencies import get_current_user
from app.models.user import User
import uuid

router = APIRouter()


@router.post("/", response_model=StudyGoalResponse, status_code=201)
def create_study_goal(
    goal_data: StudyGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva meta de estudio
    """
    return StudyGoalController.create_goal(db, goal_data, current_user)


@router.get("/", response_model=List[StudyGoalResponse])
def get_study_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las metas de estudio del usuario
    """
    return StudyGoalController.get_user_goals(db, current_user, skip, limit, completed)


@router.get("/{goal_id}", response_model=StudyGoalResponse)
def get_study_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene una meta de estudio por ID
    """
    return StudyGoalController.get_goal_by_id(db, goal_id, current_user)


@router.put("/{goal_id}", response_model=StudyGoalResponse)
def update_study_goal(
    goal_id: uuid.UUID,
    goal_data: StudyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una meta de estudio
    """
    return StudyGoalController.update_goal(db, goal_id, goal_data, current_user)


@router.delete("/{goal_id}")
def delete_study_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una meta de estudio
    """
    return StudyGoalController.delete_goal(db, goal_id, current_user)