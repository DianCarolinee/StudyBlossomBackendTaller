from app.services.gemini_service import gemini_service
from typing import Dict


class FeynmanService:
    """
    Servicio para implementar la técnica de aprendizaje Feynman
    """

    async def get_explanation(self, topic: str) -> str:
        """
        Genera una explicación simple del tema (paso 1 de Feynman)
        """
        try:
            system_instruction = """Eres un experto en la técnica Feynman. 
Tu objetivo es explicar conceptos complejos de manera simple y comprensible."""

            prompt = f"""Para el tema "{topic}", genera una explicación muy simple y concisa, 
como si se la estuvieras explicando a un niño de 12 años. 

Usa analogías si es posible. 
No excedas las 100 palabras.

Devuelve el resultado en formato JSON:
{{
  "explanation": "Tu explicación aquí..."
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )

            explanation = response.get("explanation", "")

            if not explanation:
                raise Exception("No se generó la explicación")

            return explanation

        except Exception as e:
            raise Exception(f"Error generando explicación Feynman: {str(e)}")

    async def analyze_explanation(
            self,
            topic: str,
            user_explanation: str
    ) -> Dict[str, str]:
        """
        Analiza la explicación del usuario e identifica brechas (paso 2 de Feynman)
        """
        try:
            system_instruction = """Eres un profesor experto en la técnica Feynman. 
Tu objetivo es ayudar a los estudiantes a identificar brechas en su comprensión."""

            prompt = f"""El tema de estudio es "{topic}".
La explicación del estudiante es: "{user_explanation}"

Analiza su explicación y divídela en dos partes:
1. **gaps**: Identifica 1-2 brechas clave o conceptos erróneos. Sé directo.
2. **simplifications**: Sugiere 1-2 formas de simplificar las partes complejas.

Usa guiones (-) para cada punto. Dirígete al estudiante en segunda persona.

Devuelve el resultado en formato JSON:
{{
  "gaps": "- No mencionaste el rol del núcleo en la célula.\\n- Confundiste mitocondria con cloroplasto.",
  "simplifications": "- En lugar de 'orgánulo membranoso', prueba 'el centro de control'.\\n- Compara la célula con una pequeña fábrica."
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )

            gaps = response.get("gaps", "")
            simplifications = response.get("simplifications", "")

            if not gaps or not simplifications:
                raise Exception("No se generó el análisis completo")

            return {
                "gaps": gaps,
                "simplifications": simplifications
            }

        except Exception as e:
            raise Exception(f"Error analizando explicación Feynman: {str(e)}")


# Instancia singleton
feynman_service = FeynmanService()