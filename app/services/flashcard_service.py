from typing import List, Dict
from app.services.gemini_service import gemini_service


class FlashcardService:
    """
    Servicio para generar flashcards usando IA
    """

    async def generate_flashcards(self, topic: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Genera flashcards basadas en la técnica Feynman
        """
        try:
            system_instruction = """Eres un experto en la técnica Feynman. 
Genera tarjetas de estudio en español que ayuden a aprender mediante explicaciones simples."""

            prompt = f"""Genera una serie de tarjetas de estudio en español para el tema: {topic}.

Cada tarjeta debe tener una 'question' y una 'answer'.
- La pregunta debe estar en el anverso.
- La respuesta debe estar en el reverso.
- Tanto la pregunta como la respuesta deben tener un máximo de 15 palabras.
- Explica el concepto en términos sencillos.
- Genera exactamente {count} tarjetas de estudio.

Devuelve las tarjetas como un objeto JSON con la siguiente estructura:
{{
  "flashcards": [
    {{
      "question": "¿Qué es la fotosíntesis?",
      "answer": "El proceso que usan las plantas para convertir la energía luminosa en energía química."
    }}
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.8
            )

            flashcards = response.get("flashcards", [])

            # Validar que tenemos exactamente el número correcto
            if len(flashcards) != count:
                raise Exception(f"Se esperaban {count} flashcards, pero se generaron {len(flashcards)}")

            return flashcards

        except Exception as e:
            raise Exception(f"Error generando flashcards: {str(e)}")


# Instancia singleton
flashcard_service = FlashcardService()