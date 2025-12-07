import google.generativeai as genai
from typing import Optional, Dict, Any
from app.config import get_settings
import json
import re

settings = get_settings()


class GeminiService:
    """
    Servicio para interactuar con Google Gemini AI
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Usar modelo estable compatible
        self.model_name = 'gemini-2.5-flash'

    async def generate_text(
            self,
            prompt: str,
            system_instruction: Optional[str] = None,
            temperature: float = 0.7
    ) -> str:
        """
        Genera texto usando Gemini
        """
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }

            # Construir el prompt completo SIEMPRE combinando ambos
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                full_prompt = prompt

            # Crear modelo SIN parámetros adicionales
            model = genai.GenerativeModel(
                model_name=self.model_name
            )

            # Generar contenido con la configuración
            response = model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            # Verificar que hay respuesta
            if not response or not response.text:
                raise Exception("No se recibió respuesta del modelo")

            return response.text

        except Exception as e:
            raise Exception(f"Error generando texto con Gemini: {str(e)}")

    async def generate_json(
            self,
            prompt: str,
            system_instruction: Optional[str] = None,
            temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Genera respuesta en formato JSON
        """
        try:
            # Agregar instrucción explícita para JSON al final del prompt
            json_instruction = "\n\nIMPORTANTE: Devuelve ÚNICAMENTE un objeto JSON válido. No incluyas texto adicional, no uses bloques de código markdown (```json o ```), no agregues explicaciones. Solo el JSON puro comenzando con { y terminando con }."

            full_prompt = prompt + json_instruction

            text_response = await self.generate_text(
                prompt=full_prompt,
                system_instruction=system_instruction,
                temperature=temperature
            )

            cleaned_text = text_response.strip()

            # Eliminar bloques de markdown si existen
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]

            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            # Intentar parsear el JSON
            try:
                return json.loads(cleaned_text)
            except json.JSONDecodeError:
                # Si falla, intentar extraer JSON del texto
                json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass

                # Si aún falla, intentar encontrar un array JSON
                array_match = re.search(r'\[.*\]', cleaned_text, re.DOTALL)
                if array_match:
                    try:
                        return {"data": json.loads(array_match.group(0))}
                    except json.JSONDecodeError:
                        pass

                raise Exception(f"No se pudo extraer JSON válido. Respuesta recibida: {cleaned_text[:500]}...")

        except json.JSONDecodeError as e:
            raise Exception(
                f"Error parseando JSON de Gemini. Respuesta recibida: {cleaned_text[:200]}... Error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generando JSON con Gemini: {str(e)}")

    async def generate_audio(
            self,
            text: str,
            voice_name: str = "es-ES-Standard-A"
    ) -> bytes:
        """
        Genera audio usando Google Cloud TTS
        """
        try:
            # Usar gTTS como solución
            from gtts import gTTS
            import io

            # Crear TTS
            tts = gTTS(text=text, lang='es', slow=False)

            # Guardar en bytes
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)

            return audio_fp.read()

        except ImportError:
            raise Exception("gTTS no está instalado. Ejecuta: pip install gTTS")
        except Exception as e:
            raise Exception(f"Error generando audio: {str(e)}")


# Instancia singleton
gemini_service = GeminiService()