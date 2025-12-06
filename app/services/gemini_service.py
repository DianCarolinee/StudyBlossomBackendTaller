import google.generativeai as genai
from typing import Optional, Dict, Any
from app.config import get_settings
import json

settings = get_settings()


class GeminiService:
    """
    Servicio para interactuar con Google Gemini AI
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Solo guardamos el nombre del modelo
        self.model_name = 'gemini-2.0-flash-exp'
        self.tts_model = genai.GenerativeModel(self.model_name)

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

            # 🔹 AQUÍ UNIMOS system_instruction + prompt
            if system_instruction:
                full_prompt = system_instruction.strip() + "\n\n" + prompt
            else:
                full_prompt = prompt

            # 🔹 NUNCA usamos system_instruction en el constructor
            model = genai.GenerativeModel(
                self.model_name,
                generation_config=generation_config
            )

            response = model.generate_content(full_prompt)
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
            text_response = await self.generate_text(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature
            )

            cleaned_text = text_response.strip()

            # Eliminar bloques ```json ``` si vienen
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            return json.loads(cleaned_text)

        except json.JSONDecodeError as e:
            raise Exception(f"Error parseando JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generando JSON con Gemini: {str(e)}")

    async def generate_audio(
        self,
        text: str,
        voice_name: str = "Algenib"
    ) -> bytes:
        """
        Genera audio usando Gemini TTS (implementación conceptual)
        """
        try:
            generation_config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": voice_name
                        }
                    }
                }
            }

            response = self.tts_model.generate_content(
                text,
                generation_config=generation_config
            )

            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data'):
                        return part.inline_data.data

            raise Exception("No se pudo extraer audio de la respuesta")

        except Exception as e:
            raise Exception(f"Error generando audio con Gemini: {str(e)}")


# Instancia singleton
gemini_service = GeminiService()
