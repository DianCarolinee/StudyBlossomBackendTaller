from typing import List, Dict
from app.services.gemini_service import gemini_service


class PomodoroService:
    """
    Servicio para generar recomendaciones de estudio Pomodoro
    """

    async def generate_recommendations(self, topic: str) -> List[Dict]:
        """
        Genera recomendaciones de subtemas y fuentes para estudio Pomodoro
        """
        try:
            system_instruction = """Eres un asistente de investigación experto. 
Tu objetivo es proporcionar recursos de alta calidad para el estudio."""

            prompt = f"""Para el tema de estudio principal "{topic}", genera una lista de subtemas clave 
y fuentes de alta calidad para investigar durante una sesión de estudio Pomodoro.

Reglas:
- Genera entre 3 y 5 subtemas importantes.
- Para cada subtema, proporciona exactamente 3 fuentes de investigación.
- Las fuentes deben ser de alta calidad, relevantes y accesibles.
- Incluye diferentes tipos: artículos, videos, documentación, etc.
- Las URLs deben ser reales y accesibles.

Devuelve el resultado en formato JSON:
{{
  "recommendations": [
    {{
      "sub_topic": "Fundamentos de Python",
      "sources": [
        {{
          "title": "Python para principiantes - Tutorial oficial",
          "url": "https://docs.python.org/es/3/tutorial/",
          "type": "documentation"
        }},
        {{
          "title": "Curso Python en YouTube",
          "url": "https://www.youtube.com/watch?v=example",
          "type": "video"
        }},
        {{
          "title": "Artículo: Mejores prácticas en Python",
          "url": "https://realpython.com/tutorials/best-practices/",
          "type": "article"
        }}
      ]
    }}
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            response = await gemini_service.generate_json(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7
            )

            recommendations = response.get("recommendations", [])

            if not recommendations or len(recommendations) < 3:
                raise Exception("Se necesitan al menos 3 recomendaciones")

            # Validar estructura
            for rec in recommendations:
                if not all(key in rec for key in ["sub_topic", "sources"]):
                    raise Exception("Estructura de recomendación inválida")
                if len(rec["sources"]) != 3:
                    raise Exception("Cada subtema debe tener exactamente 3 fuentes")

            return recommendations

        except Exception as e:
            raise Exception(f"Error generando recomendaciones Pomodoro: {str(e)}")


# Instancia singleton
pomodoro_service = PomodoroService()