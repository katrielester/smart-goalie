# src/study_text.py
import os

def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default

# CONFIG
STUDY_DURATION_DAYS = _int_env("STUDY_DURATION_DAYS", 14)  # 14 for full run, e.g. 3 for pilot
REFLECTIONS_PER_WEEK = _int_env("REFLECTIONS_PER_WEEK", 2) # keep “2” for your design

def study_period_phrase() -> str:
    """Human-friendly phrase for the consent, screens, and chatbot."""
    d = STUDY_DURATION_DAYS
    if d <= 3:
        return "the next few days"
    if d == 7:
        return "the next week"
    if d == 14:
        return "the next two weeks"
    return f"the next {d} days"

def reflection_invite_phrase() -> str:
    """Human-friendly reflection frequency (used only for treatment copy)."""
    # Map 2/week → “roughly twice a week”; 1/week → “about once a week”, etc.
    per_wk = REFLECTIONS_PER_WEEK
    if per_wk <= 0:
        return "occasionally"
    if per_wk == 1:
        return "about once a week"
    if per_wk == 2:
        return "roughly twice a week"
    return f"about {per_wk} times a week"