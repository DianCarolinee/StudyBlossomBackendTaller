from typing import Dict, List
from app.services.gemini_service import gemini_service


class AidaService:
    """
    Servicio para generar contenido motivacional usando el modelo AIDA
    """

    async def generate_engagement(self, topic: str) -> Dict[str, any]:
        """
        Genera contenido AIDA (Atención, Interés, Deseo)
        """
        try:
            system_instruction = """Eres un experto en marketing educativo y motivación. 
Tu objetivo es crear contenido que inspire a los estudiantes a aprender."""

            prompt = f"""Para el tema "{topic}", genera contenido motivacional siguiendo el modelo AIDA.

Reglas:
- **Atención:** Una pregunta contraintuitiva o un dato sorprendente. Máximo 15 palabras.
- **Interés:** Un párrafo corto que despierte interés conectando el tema con algo familiar. Máximo 50 palabras.
- **Deseo:** Una lista de exactamente 3 beneficios directos y accionables.
- Todo el contenido debe ser en español.

Devuelve el resultado en formato JSON:
{{
  "attention": "¿Sabías que la IA que elige tu música usa matemáticas similares a las que predicen el clima?",
  "interest": "No es magia. Es la capacidad de encontrar patrones en millones de datos. Entenderlo es entender una de las fuerzas que moldean nuestro futuro.",
  "desire": [
    "Crea pequeñas automatizaciones para simplificar tu día a día.",
    "Entiende las noticias sobre tecnología a un nivel que pocos pueden.",
    "Añade una habilidad fundamental y demandada a tu perfil profesional."
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.9
            )

            attention = response.get("attention", "")
            interest = response.get("interest", "")
            desire = response.get("desire", [])

            if not attention or not interest or len(desire) != 3:
                raise Exception("Contenido AIDA incompleto")

            return {
                "attention": attention,
                "interest": interest,
                "desire": desire
            }

        except Exception as e:
            raise Exception(f"Error generando contenido AIDA: {str(e)}")


# Instancia singleton
aida_service = AidaService()