from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.quiz import QuizSession, QuizQuestion, QuizAnswer
from app.models.user import User
from app.schemas.quiz import (
    QuizSessionCreate,
    QuizSessionResponse,
    QuizAnswerCreate,
    QuizQuestionSchema
)
from app.services.quiz_service import quiz_service
from app.config import get_settings
import uuid

settings = get_settings()


class QuizController:
    """
    Controlador para quizzes
    """

    @staticmethod
    async def generate_quiz(
            db: Session,
            flashcards: List[dict],
            current_user: User
    ) -> List[QuizQuestionSchema]:
        """
        Genera un quiz basado en flashcards
        """
        try:
            questions = await quiz_service.generate_quiz(
                flashcards=flashcards,
                num_questions=settings.MAX_QUIZ_QUESTIONS
            )

            return [QuizQuestionSchema(**q) for q in questions]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generando quiz: {str(e)}"
            )

    @staticmethod
    def create_quiz_session(
            db: Session,
            quiz_data: QuizSessionCreate,
            current_user: User
    ) -> QuizSessionResponse:
        """
        Crea una sesión de quiz
        """
        # Crear sesión de quiz
        new_quiz = QuizSession(
            user_id=current_user.id,
            study_session_id=quiz_data.study_session_id,
            topic=quiz_data.topic,
            total_questions=len(quiz_data.questions)
        )

        db.add(new_quiz)
        db.flush()

        # Crear preguntas
        for idx, question_data in enumerate(quiz_data.questions):
            new_question = QuizQuestion(
                quiz_session_id=new_quiz.id,
                question=question_data.question,
                correct_answer=question_data.correct_answer,
                options=question_data.options,
                question_order=idx + 1
            )
            db.add(new_question)

        db.commit()
        db.refresh(new_quiz)

        return QuizSessionResponse.model_validate(new_quiz)

    @staticmethod
    def submit_answer(
            db: Session,
            answer_data: QuizAnswerCreate,
            current_user: User
    ) -> dict:
        """
        Registra una respuesta del usuario
        """
        # Verificar que la pregunta existe
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == answer_data.quiz_question_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregunta no encontrada"
            )

        # Verificar que el quiz pertenece al usuario
        quiz_session = db.query(QuizSession).filter(
            QuizSession.id == question.quiz_session_id,
            QuizSession.user_id == current_user.id
        ).first()

        if not quiz_session:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para responder esta pregunta"
            )

        # Crear respuesta
        answer = QuizAnswer(
            quiz_question_id=answer_data.quiz_question_id,
            user_id=current_user.id,
            user_answer=answer_data.user_answer,
            is_correct=answer_data.is_correct
        )

        db.add(answer)

        # Actualizar contador de respuestas correctas
        if answer_data.is_correct:
            quiz_session.correct_answers += 1

        db.commit()

        return {"message": "Respuesta registrada exitosamente"}

    @staticmethod
    def complete_quiz(
            db: Session,
            quiz_id: uuid.UUID,
            current_user: User
    ) -> QuizSessionResponse:
        """
        Completa un quiz y calcula el puntaje final
        """
        quiz_session = db.query(QuizSession).filter(
            QuizSession.id == quiz_id,
            QuizSession.user_id == current_user.id
        ).first()

        if not quiz_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz no encontrado"
            )

        # Calcular puntaje
        if quiz_session.total_questions > 0:
            score = (quiz_session.correct_answers / quiz_session.total_questions) * 100
            quiz_session.score = round(score, 2)

        db.commit()
        db.refresh(quiz_session)

        return QuizSessionResponse.model_validate(quiz_session)

    @staticmethod
    def get_user_quizzes(
            db: Session,
            current_user: User,
            skip: int = 0,
            limit: int = 100
    ) -> List[QuizSessionResponse]:
        """
        Obtiene los quizzes del usuario
        """
        quizzes = db.query(QuizSession).filter(
            QuizSession.user_id == current_user.id
        ).order_by(QuizSession.completed_at.desc()).offset(skip).limit(limit).all()

        return [QuizSessionResponse.model_validate(quiz) for quiz in quizzes]