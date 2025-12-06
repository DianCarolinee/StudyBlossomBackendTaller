from datetime import date, timedelta
from typing import Dict, List
from app.config import get_settings

settings = get_settings()


def calculate_xp(mode: str) -> int:
    """
    Calcula el XP ganado por un modo de estudio
    """
    return settings.XP_MAP.get(mode, 5)


def calculate_level(total_xp: int) -> Dict[str, any]:
    """
    Calcula el nivel actual basado en el XP total
    """
    levels = settings.LEVELS

    # Encontrar el nivel actual
    current_level = levels[0]
    for level in reversed(levels):
        if total_xp >= level["xp_threshold"]:
            current_level = level
            break

    # Encontrar el siguiente nivel
    next_level = None
    for level in levels:
        if level["level"] == current_level["level"] + 1:
            next_level = level
            break

    # Calcular progreso al siguiente nivel
    if next_level:
        level_xp_range = next_level["xp_threshold"] - current_level["xp_threshold"]
        current_xp_in_level = total_xp - current_level["xp_threshold"]
        progress_percentage = round((current_xp_in_level / level_xp_range) * 100)
    else:
        progress_percentage = 100

    return {
        "current_level": current_level["level"],
        "level_name": current_level["name"],
        "plant_stage": current_level["stage"],
        "progress_percentage": progress_percentage,
        "current_xp": total_xp,
        "next_level_xp": next_level["xp_threshold"] if next_level else total_xp,
        "xp_for_next_level": next_level["xp_threshold"] - total_xp if next_level else 0
    }


def calculate_streak(
        last_study_date: date,
        current_date: date = None
) -> int:
    """
    Calcula la racha de estudio
    """
    if current_date is None:
        current_date = date.today()

    if last_study_date is None:
        return 0

    # Calcular diferencia de días
    days_diff = (current_date - last_study_date).days

    # Si estudió hoy o ayer, la racha continúa
    if days_diff <= 1:
        return 1  # Se incrementará en el controlador
    else:
        return 0  # La racha se rompió


def get_unique_study_days(study_dates: List[date]) -> List[date]:
    """
    Obtiene los días únicos de estudio ordenados
    """
    unique_dates = sorted(set(study_dates), reverse=True)
    return unique_dates


def calculate_full_streak(study_dates: List[date]) -> int:
    """
    Calcula la racha completa desde una lista de fechas de estudio
    """
    if not study_dates:
        return 0

    unique_dates = get_unique_study_days(study_dates)
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Verificar si estudió hoy o ayer
    if unique_dates[0] not in [today, yesterday]:
        return 0

    streak = 1
    for i in range(1, len(unique_dates)):
        current_date = unique_dates[i - 1]
        previous_date = unique_dates[i]

        days_diff = (current_date - previous_date).days

        if days_diff == 1:
            streak += 1
        else:
            break

    return streak