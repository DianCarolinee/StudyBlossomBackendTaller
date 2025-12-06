from app.services.gemini_service import gemini_service
import base64
import io
import wave


class AudioService:
    """
    Servicio para generar audio usando Text-to-Speech
    """

    async def generate_audio(self, text: str) -> str:
        """
        Genera audio a partir de texto y lo devuelve como data URI en base64
        """
        try:
            # Generar audio usando Gemini TTS
            audio_bytes = await gemini_service.generate_audio(text)

            # Convertir a WAV (si es necesario)
            wav_data = self._to_wav(audio_bytes)

            # Convertir a base64
            audio_base64 = base64.b64encode(wav_data).decode('utf-8')

            # Crear data URI
            data_uri = f"data:audio/wav;base64,{audio_base64}"

            return data_uri

        except Exception as e:
            raise Exception(f"Error generando audio: {str(e)}")

    def _to_wav(
            self,
            pcm_data: bytes,
            channels: int = 1,
            sample_rate: int = 24000,
            sample_width: int = 2
    ) -> bytes:
        """
        Convierte datos PCM a formato WAV
        """
        try:
            output = io.BytesIO()

            with wave.open(output, 'wb') as wav_file:
                wav_file.setnchannels(channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(pcm_data)

            output.seek(0)
            return output.read()

        except Exception as e:
            raise Exception(f"Error convirtiendo a WAV: {str(e)}")


# Instancia singleton
audio_service = AudioService()