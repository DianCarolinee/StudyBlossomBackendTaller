from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.educational_video import (
    EducationalVideoRequest,
    EducationalVideoResponse,
    EducationalVideoCreate,
    EducationalVideoDBResponse
)
from app.services.video_service import video_service
from app.models.educational_video import EducationalVideo
from app.utils.dependencies import get_current_user
from app.models.user import User
from typing import List
import uuid

router = APIRouter()


@router.post("/generate", response_model=EducationalVideoResponse)
async def generate_educational_video(
        request: EducationalVideoRequest,
        current_user: User = Depends(get_current_user)
):
    """
    Genera un video educativo con D-ID
    """
    try:
        video_data = await video_service.generate_educational_video(
            topic=request.topic,
            duration=request.duration
        )
        return EducationalVideoResponse(**video_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/save", response_model=EducationalVideoDBResponse, status_code=201)
def save_educational_video(
        video_data: EducationalVideoCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Guarda un video educativo en la base de datos
    """
    new_video = EducationalVideo(
        user_id=current_user.id,
        study_session_id=video_data.study_session_id,
        topic=video_data.topic,
        duration=video_data.duration,
        script=video_data.script,
        title=video_data.title,
        key_points=video_data.key_points,
        video_url=video_data.video_url,
        video_id=video_data.video_id,
        thumbnail_url=video_data.thumbnail_url,
        estimated_duration=video_data.estimated_duration,
        status=video_data.status
    )

    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return EducationalVideoDBResponse.model_validate(new_video)


@router.get("/", response_model=List[EducationalVideoDBResponse])
def get_user_videos(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene los videos educativos del usuario
    """
    videos = db.query(EducationalVideo).filter(
        EducationalVideo.user_id == current_user.id
    ).order_by(EducationalVideo.created_at.desc()).offset(skip).limit(limit).all()

    return [EducationalVideoDBResponse.model_validate(v) for v in videos]

@router.get("/test-connection")
async def test_did_connection(
        current_user: User = Depends(get_current_user)
):
    """
    Prueba la conexión con D-ID
    """
    result = await video_service.test_connection()
    return result

@router.get("/{video_id}", response_model=EducationalVideoDBResponse)
def get_video_by_id(
        video_id: uuid.UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Obtiene un video educativo por ID
    """
    video = db.query(EducationalVideo).filter(
        EducationalVideo.id == video_id,
        EducationalVideo.user_id == current_user.id
    ).first()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no encontrado"
        )

    return EducationalVideoDBResponse.model_validate(video)

