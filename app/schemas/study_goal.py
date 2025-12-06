from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import uuid
import re


class StudyGoalBase(BaseModel):
    goal_name: str = Field(..., min_length=1, max_length=30)
    topic: str = Field(..., min_length=25, max_length=200)
    study_time: Optional[int] = None

    @validator('goal_name')
    def validate_goal_name(cls, v):
        v = v.strip()

        # Caracteres especiales peligrosos
        forbidden_chars = r'[@/\\*<>\[\]{}$%^&|`~]'
        if re.search(forbidden_chars, v):
            raise ValueError('El nombre de la meta no puede incluir caracteres especiales como @, /, *, <>')

        # No solo repetición de caracteres
        if re.match(r'^(.)\1{2,}$', v.lower()):
            raise ValueError('El nombre de la meta debe ser algo que puedas reconocer fácilmente')

        return v

    @validator('topic')
    def validate_topic(cls, v):
        v = v.strip()

        # Caracteres especiales peligrosos
        forbidden_chars = r'[@/\\*<>\[\]{}$%^&|`~]'
        if re.search(forbidden_chars, v):
            raise ValueError('Evita usar caracteres especiales. Describe tu tema con palabras claras')

        # Patrones de prompt injection
        injection_patterns = [
            r'ignora todas las instrucciones',
            r'ignora las instrucciones anteriores',
            r'act[úu]a como',
            r'como modelo de lenguaje',
            r'prompt',
        ]

        for pattern in injection_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Usa este campo solo para describir qué quieres aprender')

        # Patrones vagos
        ambiguous_patterns = [
            r'cosas de',
            r'algo de',
            r'no se que poner',
            r'no s[eé]',
            r'no tengo idea',
        ]

        for pattern in ambiguous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Ingresa un tema claro para generar tu ruta de estudio')

        # Verificar que tiene suficientes palabras
        words = v.split()
        if len(words) < 4:
            raise ValueError('Ingresa un tema claro para generar tu ruta de estudio')

        return v


class StudyGoalCreate(StudyGoalBase):
    pass


class StudyGoalUpdate(BaseModel):
    goal_name: Optional[str] = None
    topic: Optional[str] = None
    study_time: Optional[int] = None
    is_completed: Optional[bool] = None


class StudyGoalResponse(StudyGoalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True