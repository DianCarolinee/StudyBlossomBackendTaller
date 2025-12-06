from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.concept_map import (
    ConceptMapGenerationRequest,
    ConceptMapGenerationResponse,
    ConceptMapCreate,
    ConceptMapResponse
)
from app.services.concept_map_service import concept_map_service
from app.models.concept_map import ConceptMap
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import Optional
import uuid

router = APIRouter()


@router.post("/generate", response_model=ConceptMapGenerationResponse)
async def generate_concept_map(
        request: ConceptMapGenerationRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Genera un mapa conceptual usando IA
    """
    try:
        mermaid_graph = await concept_map_service.generate_concept_map(request.topic)
        return ConceptMapGenerationResponse(mermaid_graph=mermaid_graph)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/save", response_model=ConceptMapResponse, status_code=201)
def save_concept_map(
        map_data: ConceptMapCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Guarda un mapa conceptual generado
    """
    new_map = ConceptMap(
        user_id=current_user.id,
        study_session_id=map_data.study_session_id,
        topic=map_data.topic,
        mermaid_graph=""  # Se llenará después de generar
    )

    db.add(new_map)
    db.commit()
    db.refresh(new_map)

    return ConceptMapResponse.model_validate(new_map)


@router.get("/")
async def get_user_concept_maps(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene los mapas conceptuales del usuario
    """
    maps = db.query(ConceptMap).filter(
        ConceptMap.user_id == current_user.id
    ).order_by(ConceptMap.created_at.desc()).offset(skip).limit(limit).all()

    return [ConceptMapResponse.model_validate(m) for m in maps]