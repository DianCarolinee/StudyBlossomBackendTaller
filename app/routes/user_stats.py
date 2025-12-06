from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_stats import UserStatsResponse
from app.controllers.user_stats_controller import UserStatsController
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=UserStatsResponse)
def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las estadísticas del usuario actual
    """
    return UserStatsController.get_user_stats(db, current_user.id)


@router.get("/dashboard")
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene estadísticas completas para el dashboard
    """
    return UserStatsController.get_dashboard_stats(db, current_user.id)