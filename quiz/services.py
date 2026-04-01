import json
import random
from urllib import error, request

from django.conf import settings

from .question_bank import FALLBACK_QUESTIONS

ALLOWED_TOPICS = ("python", "java")
ALLOWED_DIFFICULTIES = ("easy", "medium", "hard")


def _normalize_answer(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum() or char.isspace()).strip()


def normalize_topic(topic: str) -> str:
    cleaned = topic.strip().lower()
    if cleaned in ALLOWED_TOPICS:
        return cleaned
    return "python"


def normalize_difficulty(difficulty: str) -> str:
    cleaned = difficulty.strip().lower()
    if cleaned in ALLOWED_DIFFICULTIES:
        return cleaned
    return "medium"


def _difficulty_instruction(difficulty: str) -> str:
    if difficulty == "easy":
        return "Ask beginner-level questions about basic syntax, keywords, and common built-ins only."
    if difficulty == "hard":
        return "Ask advanced questions about deeper language features, runtime behavior, internals, or design concepts."
    return "Ask intermediate questions about practical coding constructs, object-oriented features, or commonly used language features."


def _fallback_questions(topic: str, difficulty: str, count: int) -> list[dict]:
    normalized_topic = normalize_topic(topic)
    normalized_difficulty = normalize_difficulty(difficulty)
    source = FALLBACK_QUESTIONS[normalized_topic][normalized_difficulty]
    shuffled = source[:]
    random.shuffle(shuffled)
    questions = []

    for index in range(count):
        item = shuffled[index % len(shuffled)]
        questions.append(
            {
                "id": index + 1,
                "question": item["question"],
                "answer": item["answer"],
                "hint": item["hint"],
            }
        )

    return questions


def _extract_response_text(payload: dict) -> str:
    if payload.get("output_text"):
        return payload["output_text"]

    fragments = []
    for output_item in payload.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                fragments.append(content_item.get("text", ""))
    return "".join(fragments)


def _openai_questions(topic: str, difficulty: str, count: int) -> list[dict]:
    normalized_topic = normalize_topic(topic)
    normalized_difficulty = normalize_difficulty(difficulty)
    prompt = f"""
Create exactly {count} unique short spoken interview questions about {normalized_topic}.
Difficulty: {normalized_difficulty}.
Return valid JSON only in this shape:
{{
  "questions": [
    {{"question": "...", "answer": "...", "hint": "..."}}
  ]
}}
Rules:
- Use only the topic {normalized_topic}.
- {_difficulty_instruction(normalized_difficulty)}
- Every question must be unique. Do not repeat or rephrase the same idea.
- Keep each question answerable with a short phrase.
- Make the question sound natural when read aloud by an interviewer voice.
- Keep hints short.
- Do not include markdown fences.
"""

    body = json.dumps(
        {
            "model": settings.OPENAI_MODEL,
            "input": prompt,
            "text": {"format": {"type": "json_object"}},
        }
    ).encode("utf-8")

    req = request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))

    data = json.loads(_extract_response_text(payload))
    questions = []
    seen_questions = set()

    for index, item in enumerate(data.get("questions", [])[:count], start=1):
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        hint = str(item.get("hint", "")).strip() or "Try the main keyword."
        normalized_question = _normalize_answer(question)
        if question and answer and normalized_question not in seen_questions:
            seen_questions.add(normalized_question)
            questions.append(
                {
                    "id": len(questions) + 1,
                    "question": question,
                    "answer": answer,
                    "hint": hint,
                }
            )

    if len(questions) < count:
        fallback_items = _fallback_questions(normalized_topic, normalized_difficulty, count * 2)
        for item in fallback_items:
            normalized_question = _normalize_answer(item["question"])
            if normalized_question in seen_questions:
                continue
            seen_questions.add(normalized_question)
            questions.append(
                {
                    "id": len(questions) + 1,
                    "question": item["question"],
                    "answer": item["answer"],
                    "hint": item["hint"],
                }
            )
            if len(questions) == count:
                break

    if len(questions) != count:
        raise ValueError("Unexpected question count.")

    return questions


def generate_questions(topic: str, difficulty: str = "medium", count: int = 12) -> tuple[list[dict], str]:
    normalized_topic = normalize_topic(topic)
    normalized_difficulty = normalize_difficulty(difficulty)
    if settings.OPENAI_API_KEY:
        try:
            return _openai_questions(normalized_topic, normalized_difficulty, count), "openai"
        except (ValueError, KeyError, json.JSONDecodeError, error.URLError, TimeoutError):
            pass

    return _fallback_questions(normalized_topic, normalized_difficulty, count), "fallback"


def is_correct_answer(expected: str, received: str) -> bool:
    if not received:
        return False

    normalized_expected = _normalize_answer(expected)
    normalized_received = _normalize_answer(received)
    return normalized_expected in normalized_received or normalized_received in normalized_expected
