from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.study_goal import StudyGoal
from app.models.user import User
from app.schemas.study_goal import StudyGoalCreate, StudyGoalResponse, StudyGoalUpdate
from datetime import datetime
import uuid


class StudyGoalController:
    """
    Controlador para metas de estudio
    """

    @staticmethod
    def create_goal(
            db: Session,
            goal_data: StudyGoalCreate,
            current_user: User
    ) -> StudyGoalResponse:
        """
        Crea una nueva meta de estudio
        """
        new_goal = StudyGoal(
            user_id=current_user.id,
            goal_name=goal_data.goal_name.strip(),
            topic=goal_data.topic.strip(),
            study_time=goal_data.study_time
        )

        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)

        return StudyGoalResponse.model_validate(new_goal)

    @staticmethod
    def get_user_goals(
            db: Session,
            current_user: User,
            skip: int = 0,
            limit: int = 100,
            completed: bool = None
    ) -> List[StudyGoalResponse]:
        """
        Obtiene las metas de estudio del usuario
        """
        query = db.query(StudyGoal).filter(StudyGoal.user_id == current_user.id)

        if completed is not None:
            query = query.filter(StudyGoal.is_completed == completed)

        goals = query.order_by(StudyGoal.created_at.desc()).offset(skip).limit(limit).all()

        return [StudyGoalResponse.model_validate(goal) for goal in goals]

    @staticmethod
    def get_goal_by_id(
            db: Session,
            goal_id: uuid.UUID,
            current_user: User
    ) -> StudyGoalResponse:
        """
        Obtiene una meta de estudio por ID
        """
        goal = db.query(StudyGoal).filter(
            StudyGoal.id == goal_id,
            StudyGoal.user_id == current_user.id
        ).first()

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta de estudio no encontrada"
            )

        return StudyGoalResponse.model_validate(goal)

    @staticmethod
    def update_goal(
            db: Session,
            goal_id: uuid.UUID,
            goal_data: StudyGoalUpdate,
            current_user: User
    ) -> StudyGoalResponse:
        """
        Actualiza una meta de estudio
        """
        goal = db.query(StudyGoal).filter(
            StudyGoal.id == goal_id,
            StudyGoal.user_id == current_user.id
        ).first()

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta de estudio no encontrada"
            )

        # Actualizar campos
        update_data = goal_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                setattr(goal, field, value)

        # Si se marca como completada, guardar la fecha
        if goal_data.is_completed and not goal.is_completed:
            goal.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(goal)

        return StudyGoalResponse.model_validate(goal)

    @staticmethod
    def delete_goal(
            db: Session,
            goal_id: uuid.UUID,
            current_user: User
    ) -> dict:
        """
        Elimina una meta de estudio
        """
        goal = db.query(StudyGoal).filter(
            StudyGoal.id == goal_id,
            StudyGoal.user_id == current_user.id
        ).first()

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta de estudio no encontrada"
            )

        db.delete(goal)
        db.commit()

        return {"message": "Meta de estudio eliminada exitosamente"}