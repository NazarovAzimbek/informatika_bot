import json
import random
from pathlib import Path
import config


def load_all_questions() -> list[dict]:
    """questions.json faylidan barcha test savollarini o'qish"""
    try:
        with open(config.QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


ALL_QUESTIONS = load_all_questions()


def get_random_quiz(count: int = 10) -> list[dict]:
    """Tasodifiy tartibda test savollari to'plamini shakllantirish"""
    questions = load_all_questions()
    if not questions:
        return []
    sample_count = min(count, len(questions))
    return random.sample(questions, sample_count)


def get_question_by_id(q_id: int) -> dict | None:
    """Savol ID si bo'yicha savolni topish"""
    for q in ALL_QUESTIONS:
        if q.get("id") == q_id:
            return q
    return None
