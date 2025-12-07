from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.feynman import (
    FeynmanExplanationRequest,
    FeynmanExplanationResponse,
    FeynmanAnalysisRequest,
    FeynmanAnalysisResponse,
    FeynmanSessionCreate,
    FeynmanSessionResponse
)
from app.services.feynman_service import feynman_service
from app.models.feynman_session import FeynmanSession
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


from fastapi import HTTPException, status

@router.post("/explanation", response_model=FeynmanExplanationResponse)
async def get_feynman_explanation(
        request: FeynmanExplanationRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Genera una explicación simple del tema (Paso 1 de Feynman)
    """
    if not request.topic or not request.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El tema no puede estar vacío"
        )

    try:
        explanation = await feynman_service.get_explanation(request.topic)
        return FeynmanExplanationResponse(explanation=explanation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@router.post("/analyze", response_model=FeynmanAnalysisResponse)
async def analyze_feynman_explanation(
        request: FeynmanAnalysisRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Analiza la explicación del usuario (Paso 2 de Feynman)
    """
    if not request.user_explanation or not request.user_explanation.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La explicación del usuario no puede estar vacía"
        )

    # Validar topic también:
    # if not request.topic or not request.topic.strip():
    #     raise HTTPException(
    #         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #         detail="El tema no puede estar vacío"
    #     )

    try:
        analysis = await feynman_service.analyze_explanation(
            request.topic,
            request.user_explanation
        )
        return FeynmanAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sessions", response_model=FeynmanSessionResponse, status_code=201)
def save_feynman_session(
        session_data: FeynmanSessionCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Guarda una sesión de Feynman
    """
    new_session = FeynmanSession(
        user_id=current_user.id,
        study_session_id=session_data.study_session_id,
        topic=session_data.topic,
        ai_explanation=session_data.ai_explanation,
        user_explanation=session_data.user_explanation,
        feedback_gaps=session_data.feedback_gaps,
        feedback_simplifications=session_data.feedback_simplifications
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return FeynmanSessionResponse.model_validate(new_session)


@router.get("/sessions")
def get_feynman_sessions(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene las sesiones de Feynman del usuario
    """
    sessions = db.query(FeynmanSession).filter(
        FeynmanSession.user_id == current_user.id
    ).order_by(FeynmanSession.created_at.desc()).offset(skip).limit(limit).all()

    return [FeynmanSessionResponse.model_validate(s) for s in sessions]