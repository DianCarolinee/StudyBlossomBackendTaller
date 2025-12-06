# app/controllers/user_stats_controller.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_stats import UserStats
from app.schemas.user_stats import UserStatsResponse
from app.utils.xp_calculator import calculate_level
from datetime import date, timedelta
import uuid


class UserStatsController:
    """
    Controlador para estadísticas de usuario
    """

    @staticmethod
    def get_user_stats(db: Session, user_id: uuid.UUID) -> UserStatsResponse:
        """
        Obtiene las estadísticas del usuario
        """
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Estadísticas no encontradas"
            )

        return UserStatsResponse.model_validate(stats)

    @staticmethod
    def _ensure_defaults(stats: UserStats) -> None:
        """
        Asegura que los campos numéricos no sean None
        """
        if stats.total_xp is None:
            stats.total_xp = 0
        if stats.current_level is None:
            stats.current_level = 1
        if stats.current_streak is None:
            stats.current_streak = 0
        if stats.longest_streak is None:
            stats.longest_streak = 0
        if stats.total_sessions is None:
            stats.total_sessions = 0
        if stats.total_study_time is None:
            stats.total_study_time = 0
        if stats.plant_stage is None:
            stats.plant_stage = 1

    @staticmethod
    def update_stats_after_session(
        db: Session,
        user_id: uuid.UUID,
        xp_earned: int,
        study_time: int,
    ):
        """
        Actualiza las estadísticas después de una sesión de estudio
        """
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

        if not stats:
            # Crear estadísticas si no existen, con valores iniciales
            stats = UserStats(
                user_id=user_id,
                total_xp=0,
                current_level=1,
                current_streak=0,
                longest_streak=0,
                total_sessions=0,
                total_study_time=0,
                plant_stage=1,
                last_study_date=None,
            )
            db.add(stats)
            db.flush()  # para que SQLAlchemy conozca el objeto

        # Normalizar valores (por si en la BD hay nulos antiguos)
        UserStatsController._ensure_defaults(stats)

        # ===== XP y nivel =====
        stats.total_xp += xp_earned

        level_info = calculate_level(stats.total_xp)
        stats.current_level = level_info["current_level"]
        stats.plant_stage = level_info["plant_stage"]

        # ===== Sesiones y tiempo =====
        stats.total_sessions += 1
        stats.total_study_time += study_time

        # ===== Racha de estudio =====
        today: date = date.today()
        yesterday: date = today - timedelta(days=1)

        last_date = stats.last_study_date

        if last_date == today:
            # Ya estudió hoy, racha se mantiene tal cual
            pass
        elif last_date == yesterday:
            # Estudió ayer, aumentar racha
            stats.current_streak += 1
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
        else:
            # Primera vez o racha rota
            stats.current_streak = 1
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak

        stats.last_study_date = today

        db.commit()

    @staticmethod
    def get_dashboard_stats(db: Session, user_id: uuid.UUID) -> dict:
        """
        Obtiene estadísticas para el dashboard
        """
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

        if not stats:
            return {
                "total_xp": 0,
                "current_level": 1,
                "level_name": "Semilla",
                "plant_stage": 1,
                "progress_percentage": 0,
                "xp_for_next_level": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "total_sessions": 0,
                "total_study_time": 0,
                "last_study_date": None,
            }

        UserStatsController._ensure_defaults(stats)
        level_info = calculate_level(stats.total_xp)

        return {
            "total_xp": stats.total_xp,
            "current_level": level_info["current_level"],
            "level_name": level_info["level_name"],
            "plant_stage": level_info["plant_stage"],
            "progress_percentage": level_info["progress_percentage"],
            "xp_for_next_level": level_info["xp_for_next_level"],
            "current_streak": stats.current_streak,
            "longest_streak": stats.longest_streak,
            "total_sessions": stats.total_sessions,
            "total_study_time": stats.total_study_time,
            "last_study_date": stats.last_study_date,
        }
