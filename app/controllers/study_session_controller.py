from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.study_session import StudySession
from app.models.user import User
from app.schemas.study_session import StudySessionCreate, StudySessionResponse
from app.controllers.user_stats_controller import UserStatsController
from app.utils.xp_calculator import calculate_xp
from datetime import datetime
import uuid


class StudySessionController:
    """
    Controlador para sesiones de estudio
    """

    @staticmethod
    def create_session(
            db: Session,
            session_data: StudySessionCreate,
            current_user: User
    ) -> StudySessionResponse:
        """
        Crea una nueva sesión de estudio
        """
        # Calcular XP ganado
        xp_earned = calculate_xp(session_data.mode)

        new_session = StudySession(
            user_id=current_user.id,
            study_goal_id=session_data.study_goal_id,
            goal_name=session_data.goal_name,
            topic=session_data.topic,
            mode=session_data.mode,
            study_time=session_data.study_time,
            xp_earned=xp_earned
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        # Actualizar estadísticas del usuario
        UserStatsController.update_stats_after_session(
            db=db,
            user_id=current_user.id,
            xp_earned=xp_earned,
            study_time=session_data.study_time or 0
        )

        return StudySessionResponse.model_validate(new_session)

    @staticmethod
    def get_user_sessions(
            db: Session,
            current_user: User,
            skip: int = 0,
            limit: int = 100,
            mode: str = None
    ) -> List[StudySessionResponse]:
        """
        Obtiene las sesiones de estudio del usuario
        """
        query = db.query(StudySession).filter(StudySession.user_id == current_user.id)

        if mode:
            query = query.filter(StudySession.mode == mode)

        sessions = query.order_by(StudySession.created_at.desc()).offset(skip).limit(limit).all()

        return [StudySessionResponse.model_validate(session) for session in sessions]

    @staticmethod
    def get_session_by_id(
            db: Session,
            session_id: uuid.UUID,
            current_user: User
    ) -> StudySessionResponse:
        """
        Obtiene una sesión de estudio por ID
        """
        session = db.query(StudySession).filter(
            StudySession.id == session_id,
            StudySession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión de estudio no encontrada"
            )

        return StudySessionResponse.model_validate(session)

    @staticmethod
    def delete_session(
            db: Session,
            session_id: uuid.UUID,
            current_user: User
    ) -> dict:
        """
        Elimina una sesión de estudio
        """
        session = db.query(StudySession).filter(
            StudySession.id == session_id,
            StudySession.user_id == current_user.id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sesión de estudio no encontrada"
            )

        db.delete(session)
        db.commit()

        return {"message": "Sesión de estudio eliminada exitosamente"}