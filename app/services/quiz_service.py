from typing import List, Dict
from app.services.gemini_service import gemini_service


class QuizService:
    """
    Servicio para generar quizzes basados en flashcards
    """

    async def generate_quiz(
            self,
            flashcards: List[Dict[str, str]],
            num_questions: int = 5
    ) -> List[Dict]:
        """
        Genera un quiz de opción múltiple basado en flashcards
        """
        try:
            system_instruction = """Eres un profesor experto creando evaluaciones. 
Crea preguntas de opción múltiple desafiantes pero justas."""

            # Preparar las flashcards para el prompt
            flashcards_text = "\n".join([
                f"- Pregunta: {card['question']}\n  Respuesta: {card['answer']}"
                for card in flashcards
            ])

            prompt = f"""A partir de las siguientes tarjetas de estudio, crea un quiz de opción múltiple en español.

Tarjetas de estudio:
{flashcards_text}

Reglas:
- Genera exactamente {num_questions} preguntas.
- Cada pregunta debe tener 4 opciones de respuesta.
- Solo una de las opciones debe ser correcta.
- Las preguntas y opciones deben basarse ÚNICAMENTE en la información proporcionada en las tarjetas.
- Las opciones incorrectas (distractores) deben ser plausibles pero claramente incorrectas.

Devuelve el quiz en formato JSON:
{{
  "questions": [
    {{
      "question": "¿Qué es...?",
      "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
      "correct_answer": "Opción B"
    }}
  ]
}}

IMPORTANTE: El 'correct_answer' debe coincidir exactamente con una de las 'options'.
Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.8
            )

            questions = response.get("questions", [])

            if len(questions) != num_questions:
                raise Exception(f"Se esperaban {num_questions} preguntas, pero se generaron {len(questions)}")

            # Validar estructura de cada pregunta
            for q in questions:
                if not all(key in q for key in ["question", "options", "correct_answer"]):
                    raise Exception("Estructura de pregunta inválida")
                if len(q["options"]) != 4:
                    raise Exception("Cada pregunta debe tener exactamente 4 opciones")
                if q["correct_answer"] not in q["options"]:
                    raise Exception("La respuesta correcta debe estar en las opciones")

            return questions

        except Exception as e:
            raise Exception(f"Error generando quiz: {str(e)}")


# Instancia singleton
quiz_service = QuizService()