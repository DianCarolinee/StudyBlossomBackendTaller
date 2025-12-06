import httpx
import asyncio
import base64
from typing import Dict, List
from app.config import get_settings
from app.services.gemini_service import gemini_service

settings = get_settings()


class VideoService:
    """
    Servicio para generar videos educativos con D-ID
    """

    def __init__(self):
        self.api_key = settings.D_ID_API_KEY
        self.base_url = "https://api.d-id.com"

    async def generate_educational_video(
            self,
            topic: str,
            duration: str  # short, medium, long
    ) -> Dict[str, any]:
        """
        Genera un video educativo completo con avatar y voz
        """
        try:
            # 1. Generar el guión con Gemini
            script_data = await self._generate_script(topic, duration)

            # 2. Crear el video con D-ID
            video_data = await self._create_video_with_did(
                script=script_data["script"],
                duration=duration
            )

            # 3. Esperar a que el video esté listo
            completed_video = await self._wait_for_video_completion(
                video_id=video_data["id"]
            )

            return {
                "video_url": completed_video["result_url"],
                "video_id": video_data["id"],
                "script": script_data["script"],
                "title": script_data["title"],
                "key_points": script_data["key_points"],
                "estimated_duration": self._get_duration_text(duration),
                "thumbnail_url": completed_video.get("thumbnail_url"),
                "status": "done"
            }

        except Exception as e:
            raise Exception(f"Error generando video educativo: {str(e)}")

    async def _generate_script(self, topic: str, duration: str) -> Dict[str, any]:
        """
        Genera el guión del video usando Gemini
        """
        word_limits = {
            "short": {"words": 200, "duration": "1-2 minutos", "max_chars": 1000},
            "medium": {"words": 400, "duration": "3-5 minutos", "max_chars": 2000},
            "long": {"words": 700, "duration": "5-10 minutos", "max_chars": 3500},
        }

        limit = word_limits.get(duration, word_limits["medium"])

        system_instruction = """Eres un guionista experto en contenido educativo. 
Crea guiones concisos y directos para videos educativos."""

        prompt = f"""Crea un guión CONCISO y DIRECTO para un video educativo sobre "{topic}".

IMPORTANTE: El guión debe ser CORTO y CLARO para narración de voz.

Características:
- Duración objetivo: {limit['duration']}
- Palabras aproximadas: {limit['words']}
- Máximo de caracteres: {limit['max_chars']}

Estructura:
1. Introducción (15-20 segundos): Hook atractivo
2. Desarrollo (60-70% del tiempo): Explicación clara con 2-3 puntos principales
3. Conclusión (10-15 segundos): Resumen breve

Estilo de narración:
- Tono conversacional y cercano
- Frases cortas y directas
- Sin jerga innecesaria
- Ritmo ágil y dinámico
- Usar "tú" para conectar con el espectador

Devuelve el resultado en formato JSON:
{{
  "title": "Título conciso y atractivo (máximo 60 caracteres)",
  "script": "Guión completo en un solo párrafo fluido, sin secciones marcadas",
  "key_points": ["Punto 1", "Punto 2", "Punto 3"]
}}

CRÍTICO: El "script" debe ser un texto continuo, natural para lectura en voz alta, 
SIN marcadores de sección, SIN títulos internos, SOLO el texto que se narrará.

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

        response = await gemini_service.generate_json(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.8
        )

        script = response.get("script", "")
        title = response.get("title", f"Video Educativo: {topic}")
        key_points = response.get("key_points", [])

        # Limitar el script al máximo de caracteres
        if len(script) > limit["max_chars"]:
            script = script[:limit["max_chars"]] + "..."

        return {
            "script": script,
            "title": title,
            "key_points": key_points
        }

    async def _create_video_with_did(self, script: str, duration: str) -> Dict[str, any]:
        """
        Crea el video usando la API de D-ID
        """
        try:
            auth_header = base64.b64encode(f"{self.api_key}:".encode()).decode()

            request_body = {
                "script": {
                    "type": "text",
                    "input": script,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "es-ES-ElviraNeural"
                    }
                },
                "source_url": "https://d-id-public-bucket.s3.amazonaws.com/alice.jpg"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/talks",
                    headers={
                        "Authorization": f"Basic {auth_header}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json=request_body,
                    timeout=30.0
                )

                if response.status_code != 201:
                    error_text = response.text
                    raise Exception(f"Error de D-ID ({response.status_code}): {error_text}")

                return response.json()

        except Exception as e:
            raise Exception(f"Error creando video con D-ID: {str(e)}")

    async def _wait_for_video_completion(
            self,
            video_id: str,
            max_attempts: int = 60
    ) -> Dict[str, any]:
        """
        Espera a que el video esté completamente procesado
        """
        auth_header = base64.b64encode(f"{self.api_key}:".encode()).decode()

        async with httpx.AsyncClient() as client:
            for attempt in range(max_attempts):
                response = await client.get(
                    f"{self.base_url}/talks/{video_id}",
                    headers={
                        "Authorization": f"Basic {auth_header}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )

                if response.status_code != 200:
                    raise Exception(f"Error verificando estado del video: {response.status_code}")

                data = response.json()
                status = data.get("status")

                print(f"[D-ID] Intento {attempt + 1}/{max_attempts} - Estado: {status}")

                if status == "done":
                    return data
                elif status == "error":
                    error_msg = data.get("error", "Error desconocido")
                    raise Exception(f"Error al generar el video: {error_msg}")

                # Esperar 3 segundos antes del siguiente intento
                await asyncio.sleep(3)

        raise Exception("El video tardó demasiado en generarse. Por favor, intenta de nuevo.")

    def _get_duration_text(self, duration: str) -> str:
        """
        Obtiene el texto descriptivo de la duración
        """
        duration_map = {
            "short": "1-2 minutos",
            "medium": "3-5 minutos",
            "long": "5-10 minutos"
        }
        return duration_map.get(duration, "3-5 minutos")

    async def test_connection(self) -> Dict[str, any]:
        """
        Prueba la conexión con D-ID
        """
        try:
            auth_header = base64.b64encode(f"{self.api_key}:".encode()).decode()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/credits",
                    headers={
                        "Authorization": f"Basic {auth_header}",
                        "Accept": "application/json"
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    return {
                        "success": False,
                        "message": f"Error {response.status_code}: {response.text}"
                    }

                data = response.json()
                return {
                    "success": True,
                    "message": "Conexión exitosa con D-ID",
                    "credits": data.get("remaining")
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error de conexión: {str(e)}"
            }


# Instancia singleton
video_service = VideoService()