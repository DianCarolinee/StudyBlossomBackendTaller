#!/usr/bin/env python3
"""
Script para probar la conexión con Gemini y verificar que todo funciona
"""
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.gemini_service import gemini_service


async def test_text_generation():
    """Prueba generación de texto simple"""
    print("\n🔍 Probando generación de texto...")
    try:
        result = await gemini_service.generate_text(
            prompt="Di 'Hola mundo' en español",
            temperature=0.7
        )
        print(f"✅ Texto generado: {result[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Error en texto: {e}")
        return False


async def test_json_generation():
    """Prueba generación de JSON"""
    print("\n🔍 Probando generación de JSON...")
    try:
        result = await gemini_service.generate_json(
            prompt='Genera un JSON con esta estructura: {"mensaje": "hola", "numero": 42}',
            temperature=0.7
        )
        print(f"✅ JSON generado: {result}")
        return True
    except Exception as e:
        print(f"❌ Error en JSON: {e}")
        return False


async def test_flashcards_generation():
    """Prueba generación de flashcards (caso real)"""
    print("\n🔍 Probando generación de flashcards...")
    try:
        system_instruction = """Eres un experto en la técnica Feynman. 
Genera tarjetas de estudio en español que ayuden a aprender mediante explicaciones simples."""

        prompt = """Genera una serie de tarjetas de estudio en español para el tema: Python básico.

Cada tarjeta debe tener una 'question' y una 'answer'.
- La pregunta debe estar en el anverso.
- La respuesta debe estar en el reverso.
- Tanto la pregunta como la respuesta deben tener un máximo de 15 palabras.
- Explica el concepto en términos sencillos.
- Genera exactamente 5 tarjetas de estudio.

Devuelve las tarjetas como un objeto JSON con la siguiente estructura:
{
  "flashcards": [
    {
      "question": "¿Qué es la fotosíntesis?",
      "answer": "El proceso que usan las plantas para convertir la energía luminosa en energía química."
    }
  ]
}

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional ni markdown."""

        result = await gemini_service.generate_json(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.8
        )

        if "flashcards" in result and len(result["flashcards"]) == 5:
            print(f"✅ Flashcards generadas correctamente:")
            for i, card in enumerate(result["flashcards"], 1):
                print(f"   {i}. {card['question'][:50]}...")
            return True
        else:
            print(f"⚠️  Flashcards generadas pero con formato incorrecto: {result}")
            return False

    except Exception as e:
        print(f"❌ Error en flashcards: {e}")
        return False


async def test_audio_generation():
    """Prueba generación de audio"""
    print("\n🔍 Probando generación de audio...")
    try:
        audio_bytes = await gemini_service.generate_audio(
            text="Hola, esto es una prueba de audio"
        )
        if len(audio_bytes) > 0:
            print(f"✅ Audio generado: {len(audio_bytes)} bytes")
            return True
        else:
            print("⚠️  Audio vacío")
            return False
    except Exception as e:
        print(f"❌ Error en audio: {e}")
        print("   Nota: Asegúrate de tener instalado gTTS: pip install gTTS")
        return False


async def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DE CONEXIÓN CON GEMINI")
    print("=" * 60)

    tests = [
        ("Generación de Texto", test_text_generation),
        ("Generación de JSON", test_json_generation),
        ("Generación de Flashcards", test_flashcards_generation),
        ("Generación de Audio", test_audio_generation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error crítico en {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! Gemini está funcionando correctamente.")
        return 0
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)