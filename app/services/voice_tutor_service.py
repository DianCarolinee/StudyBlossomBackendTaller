from typing import List, Dict
from app.services.gemini_service import gemini_service
from app.services.audio_service import audio_service


class VoiceTutorService:
    """
    Servicio para el tutor de voz conversacional
    """

    async def ask_tutor(
            self,
            topic: str,
            user_question: str,
            conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        Procesa una pregunta del usuario y genera respuesta en texto y audio
        """
        try:
            # Construir contexto de conversación
            context = ""
            if conversation_history:
                context = "\n".join([
                    f"{'Estudiante' if msg['role'] == 'user' else 'Tutor'}: {msg['content']}"
                    for msg in conversation_history[-10:]  # Últimos 10 mensajes
                ])

            system_instruction = f"""Eres un tutor experto, paciente y motivador especializado en {topic}.
Tu objetivo es ayudar al estudiante a comprender conceptos de manera clara y didáctica."""

            prompt = f"""{'Contexto de la conversación anterior:' + context if context else ''}

El estudiante pregunta: "{user_question}"

Instrucciones:
- Responde de forma clara, didáctica y motivadora
- Usa analogías o ejemplos concretos cuando sea apropiado
- Adapta el nivel de complejidad al estudiante
- Si detectas confusión, simplifica la explicación
- Máximo 150 palabras para que la respuesta en audio no sea muy larga
- Usa un tono conversacional y cercano

Responde SOLO con la explicación, sin mencionar que eres un tutor o una IA."""

            # Generar respuesta de texto
            text_response = await gemini_service.generate_text(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.8
            )

            # Generar audio de la respuesta
            audio_response = await audio_service.generate_audio(text_response)

            # Generar sugerencias de seguimiento
            suggestions_prompt = f"""Basándote en esta pregunta sobre {topic}: "{user_question}"
Y esta respuesta: "{text_response}"

Genera exactamente 3 preguntas de seguimiento que un estudiante podría hacer para profundizar.

Devuelve el resultado en formato JSON:
{{
  "suggestions": [
    "¿Pregunta 1?",
    "¿Pregunta 2?",
    "¿Pregunta 3?"
  ]
}}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

            try:
                suggestions_response = await gemini_service.generate_json(
                    prompt=suggestions_prompt,
                    temperature=0.7
                )
                follow_up_suggestions = suggestions_response.get("suggestions", [])
            except:
                # Fallback si falla la generación
                follow_up_suggestions = [
                    "¿Puedes darme un ejemplo práctico?",
                    "¿Cómo se relaciona esto con otros conceptos?",
                    "¿Cuáles son los errores comunes al aprender esto?"
                ]

            return {
                "text_response": text_response,
                "audio_response": audio_response,
                "follow_up_suggestions": follow_up_suggestions
            }

        except Exception as e:
            raise Exception(f"Error en tutor de voz: {str(e)}")


# Instancia singleton
voice_tutor_service = VoiceTutorService()