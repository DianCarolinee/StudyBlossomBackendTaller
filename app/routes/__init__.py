from fastapi import APIRouter
from app.routes import (
    auth,
    study_goals,
    study_sessions,
    flashcards,
    quiz,
    ai_services,
    voice_tutor,
    video,
    audio,
    concept_map,
    feynman,
    user_stats
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(study_goals.router, prefix="/study-goals", tags=["Study Goals"])
api_router.include_router(study_sessions.router, prefix="/study-sessions", tags=["Study Sessions"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
api_router.include_router(ai_services.router, prefix="/ai", tags=["AI Services"])
api_router.include_router(voice_tutor.router, prefix="/voice-tutor", tags=["Voice Tutor"])
api_router.include_router(video.router, prefix="/video", tags=["Educational Video"])
api_router.include_router(audio.router, prefix="/audio", tags=["Audio Generation"])
api_router.include_router(concept_map.router, prefix="/concept-map", tags=["Concept Map"])
api_router.include_router(feynman.router, prefix="/feynman", tags=["Feynman Technique"])
api_router.include_router(user_stats.router, prefix="/stats", tags=["User Statistics"])

__all__ = ["api_router"]