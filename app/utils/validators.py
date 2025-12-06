import re
from typing import Optional


def validate_topic(topic: str) -> tuple[bool, Optional[str]]:
    """
    Valida un tema de estudio
    Returns: (is_valid, error_message)
    """
    topic = topic.strip()

    if not topic:
        return False, "El tema no puede estar vacío"

    if len(topic) < 25:
        return False, "El tema debe tener al menos 25 caracteres"

    if len(topic) > 200:
        return False, "El tema no puede exceder 200 caracteres"

    # Caracteres especiales peligrosos
    forbidden_chars = r'[@/\\*<>\[\]{}$%^&|`~]'
    if re.search(forbidden_chars, topic):
        return False, "Evita usar caracteres especiales como @, /, *, <>"

    # Patrones de prompt injection
    injection_patterns = [
        r'ignora todas las instrucciones',
        r'ignora las instrucciones anteriores',
        r'act[úu]a como',
        r'como modelo de lenguaje',
    ]

    for pattern in injection_patterns:
        if re.search(pattern, topic, re.IGNORECASE):
            return False, "Usa este campo solo para describir qué quieres aprender"

    # Patrones vagos
    ambiguous_patterns = [
        r'cosas de',
        r'algo de',
        r'no se que poner',
        r'no s[eé]',
    ]

    for pattern in ambiguous_patterns:
        if re.search(pattern, topic, re.IGNORECASE):
            return False, "Ingresa un tema claro para generar tu ruta de estudio"

    # Verificar suficientes palabras
    words = topic.split()
    if len(words) < 4:
        return False, "El tema debe contener al menos 4 palabras"

    return True, None


def sanitize_text(text: str) -> str:
    """
    Limpia texto de caracteres potencialmente peligrosos
    """
    # Remover caracteres de control
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # Normalizar espacios en blanco
    text = re.sub(r'\s+', ' ', text)

    return text.strip()