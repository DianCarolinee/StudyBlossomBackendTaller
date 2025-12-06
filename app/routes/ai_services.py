from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.aida_engagement import AidaEngagementRequest, AidaEngagementResponse
from app.schemas.pomodoro import PomodoroRecommendationsRequest, PomodoroRecommendationsResponse
from app.services.aida_service import aida_service
from app.services.pomodoro_service import pomodoro_service
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/aida-engagement", response_model=AidaEngagementResponse)
async def generate_aida_engagement(
    request: AidaEngagementRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Genera contenido motivacional usando el modelo AIDA
    """
    try:
        content = await aida_service.generate_engagement(request.topic)
        return AidaEngagementResponse(**content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/pomodoro-recommendations", response_model=PomodoroRecommendationsResponse)
async def generate_pomodoro_recommendations(
    request: PomodoroRecommendationsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Genera recomendaciones de estudio para Pomodoro
    """
    try:
        recommendations = await pomodoro_service.generate_recommendations(request.topic)
        return PomodoroRecommendationsResponse(recommendations=recommendations)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )