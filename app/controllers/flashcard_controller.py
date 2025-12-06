from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from app.models.flashcard import Flashcard, FlashcardReview
from app.models.user import User
from app.schemas.flashcard import (
    FlashcardCreate,
    FlashcardResponse,
    FlashcardReviewCreate,
    FlashcardBatchResponse
)
from app.services.flashcard_service import flashcard_service
from app.config import get_settings
import uuid

settings = get_settings()


class FlashcardController:
    """
    Controlador para flashcards
    """

    @staticmethod
    async def generate_flashcards(
            db: Session,
            topic: str,
            current_user: User,
            study_session_id: uuid.UUID = None
    ) -> FlashcardBatchResponse:
        """
        Genera flashcards usando IA
        """
        try:
            # Generar flashcards con IA
            flashcards_data = await flashcard_service.generate_flashcards(
                topic=topic,
                count=settings.MAX_FLASHCARDS_PER_TOPIC
            )

            # Guardar en base de datos
            saved_flashcards = []
            for card_data in flashcards_data:
                new_flashcard = Flashcard(
                    user_id=current_user.id,
                    study_session_id=study_session_id,
                    question=card_data["question"],
                    answer=card_data["answer"],
                    topic=topic
                )
                db.add(new_flashcard)
                saved_flashcards.append(new_flashcard)

            db.commit()

            # Refrescar para obtener IDs
            for card in saved_flashcards:
                db.refresh(card)

            return FlashcardBatchResponse(
                flashcards=[FlashcardResponse.model_validate(card) for card in saved_flashcards]
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generando flashcards: {str(e)}"
            )

    @staticmethod
    def create_flashcard(
            db: Session,
            flashcard_data: FlashcardCreate,
            current_user: User
    ) -> FlashcardResponse:
        """
        Crea una flashcard manualmente
        """
        new_flashcard = Flashcard(
            user_id=current_user.id,
            study_session_id=flashcard_data.study_session_id,
            question=flashcard_data.question,
            answer=flashcard_data.answer,
            topic=flashcard_data.topic
        )

        db.add(new_flashcard)
        db.commit()
        db.refresh(new_flashcard)

        return FlashcardResponse.model_validate(new_flashcard)

    @staticmethod
    def get_user_flashcards(
            db: Session,
            current_user: User,
            topic: str = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[FlashcardResponse]:
        """
        Obtiene las flashcards del usuario
        """
        query = db.query(Flashcard).filter(Flashcard.user_id == current_user.id)

        if topic:
            query = query.filter(Flashcard.topic.ilike(f"%{topic}%"))

        flashcards = query.order_by(Flashcard.created_at.desc()).offset(skip).limit(limit).all()

        return [FlashcardResponse.model_validate(card) for card in flashcards]

    @staticmethod
    def review_flashcard(
            db: Session,
            review_data: FlashcardReviewCreate,
            current_user: User
    ) -> dict:
        """
        Registra una revisión de flashcard
        """
        # Verificar que la flashcard existe y pertenece al usuario
        flashcard = db.query(Flashcard).filter(
            Flashcard.id == review_data.flashcard_id,
            Flashcard.user_id == current_user.id
        ).first()

        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flashcard no encontrada"
            )

        # Crear registro de revisión
        review = FlashcardReview(
            flashcard_id=review_data.flashcard_id,
            user_id=current_user.id,
            learned=review_data.learned
        )

        db.add(review)
        db.commit()

        return {"message": "Revisión registrada exitosamente"}

    @staticmethod
    def delete_flashcard(
            db: Session,
            flashcard_id: uuid.UUID,
            current_user: User
    ) -> dict:
        """
        Elimina una flashcard
        """
        flashcard = db.query(Flashcard).filter(
            Flashcard.id == flashcard_id,
            Flashcard.user_id == current_user.id
        ).first()

        if not flashcard:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Flashcard no encontrada"
            )

        db.delete(flashcard)
        db.commit()

        return {"message": "Flashcard eliminada exitosamente"}