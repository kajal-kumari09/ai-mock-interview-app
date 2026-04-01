import json
import os
import random
from pathlib import Path
from urllib import error, request

ALLOWED_TOPICS = ("python", "java")
ALLOWED_DIFFICULTIES = ("easy", "medium", "hard")

FALLBACK_QUESTIONS = {
    "python": {
        "easy": [
            {"question": "What keyword is used to define a function in Python?", "answer": "def"},
            {"question": "What built-in function prints output to the console in Python?", "answer": "print"},
            {"question": "Which keyword is used to import a module in Python?", "answer": "import"},
            {"question": "What value represents nothing or no value in Python?", "answer": "none"},
            {"question": "Which Python collection stores key value pairs?", "answer": "dictionary"},
            {"question": "Which loop iterates over items in a sequence in Python?", "answer": "for loop"},
        ],
        "medium": [
            {"question": "What built-in Python function returns the length of a list?", "answer": "len"},
            {"question": "Which keyword is used to create a class in Python?", "answer": "class"},
            {"question": "What symbol is commonly used for floor division in Python?", "answer": "double slash"},
            {"question": "Which statement is used to handle exceptions in Python?", "answer": "try except"},
            {"question": "Which keyword creates an anonymous function in Python?", "answer": "lambda"},
            {"question": "What special method initializes a new object in Python?", "answer": "__init__"},
        ],
        "hard": [
            {"question": "Which Python feature allows a function to yield values one at a time?", "answer": "generator"},
            {"question": "What decorator is commonly used to define a method on the class rather than the instance?", "answer": "classmethod"},
            {"question": "What mechanism lets one object customize attribute access dynamically in Python?", "answer": "__getattr__"},
            {"question": "What Python structure is used to manage context with the with statement?", "answer": "context manager"},
            {"question": "Which Python concept lets a nested function remember variables from an outer scope?", "answer": "closure"},
            {"question": "What protocol method makes an object iterable in Python?", "answer": "__iter__"},
        ],
    },
    "java": {
        "easy": [
            {"question": "Which keyword is used to define a class in Java?", "answer": "class"},
            {"question": "What method is commonly used to print text in Java?", "answer": "system out println"},
            {"question": "Which primitive type stores true or false values in Java?", "answer": "boolean"},
            {"question": "Which keyword is used to create an object in Java?", "answer": "new"},
            {"question": "What symbol ends most Java statements?", "answer": "semicolon"},
            {"question": "Which keyword refers to the current object instance in Java?", "answer": "this"},
        ],
        "medium": [
            {"question": "Which keyword is used to inherit from a class in Java?", "answer": "extends"},
            {"question": "What is the entry point method of a Java application?", "answer": "main"},
            {"question": "Which collection in Java does not allow duplicate values?", "answer": "set"},
            {"question": "Which access modifier makes a member available everywhere?", "answer": "public"},
            {"question": "Which keyword prevents a method from being overridden in Java?", "answer": "final"},
            {"question": "What exception handling block is used after try in Java?", "answer": "catch"},
        ],
        "hard": [
            {"question": "Which Java annotation marks a method as intentionally replacing a parent implementation?", "answer": "override"},
            {"question": "What Java mechanism removes the need to manually free memory in most applications?", "answer": "garbage collection"},
            {"question": "Which Java concept allows one interface or class to work with different data types safely?", "answer": "generics"},
            {"question": "What Java keyword is used so only one thread can execute a block or method at a time?", "answer": "synchronized"},
            {"question": "Which Java reference type can represent the absence of an object and often causes runtime errors if used carelessly?", "answer": "null"},
            {"question": "What JVM area stores per-thread method execution frames?", "answer": "stack"},
        ],
    },
}


def load_env_file(base_dir: Path) -> None:
    env_path = base_dir / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def normalize_topic(topic: str) -> str:
    cleaned = topic.strip().lower()
    return cleaned if cleaned in ALLOWED_TOPICS else "python"


def normalize_difficulty(difficulty: str) -> str:
    cleaned = difficulty.strip().lower()
    return cleaned if cleaned in ALLOWED_DIFFICULTIES else "medium"


def _normalize_answer(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum() or char.isspace()).strip()


def is_correct_answer(expected: str, received: str) -> bool:
    if not received:
        return False

    normalized_expected = _normalize_answer(expected)
    normalized_received = _normalize_answer(received)
    return normalized_expected in normalized_received or normalized_received in normalized_expected


def _difficulty_instruction(difficulty: str) -> str:
    if difficulty == "easy":
        return "Ask beginner-level questions about basic syntax, keywords, and common built-ins only."
    if difficulty == "hard":
        return "Ask advanced questions about deeper language features, runtime behavior, internals, or design concepts."
    return "Ask intermediate questions about practical coding constructs, object-oriented features, or commonly used language features."


def fallback_questions(topic: str, difficulty: str, count: int) -> list[dict]:
    normalized_topic = normalize_topic(topic)
    normalized_difficulty = normalize_difficulty(difficulty)
    source = FALLBACK_QUESTIONS[normalized_topic][normalized_difficulty][:]
    random.shuffle(source)
    questions = []

    for index in range(count):
        item = source[index % len(source)]
        questions.append(
            {
                "id": index + 1,
                "question": item["question"],
                "answer": item["answer"],
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


def openai_questions(topic: str, difficulty: str, count: int, api_key: str, model: str) -> list[dict]:
    normalized_topic = normalize_topic(topic)
    normalized_difficulty = normalize_difficulty(difficulty)
    prompt = f"""
Create exactly {count} unique short spoken interview questions about {normalized_topic}.
Difficulty: {normalized_difficulty}.
Return valid JSON only in this shape:
{{
  "questions": [
    {{"question": "...", "answer": "..."}}
  ]
}}
Rules:
- Use only the topic {normalized_topic}.
- {_difficulty_instruction(normalized_difficulty)}
- Every question must be unique. Do not repeat or rephrase the same idea.
- Keep each question answerable with a short phrase.
- Make the question sound natural when read aloud by an interviewer voice.
- Do not include markdown fences.
"""

    body = json.dumps(
        {
            "model": model,
            "input": prompt,
            "text": {"format": {"type": "json_object"}},
        }
    ).encode("utf-8")

    api_request = request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with request.urlopen(api_request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    data = json.loads(_extract_response_text(payload))
    questions = []
    seen = set()

    for item in data.get("questions", []):
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        normalized_question = _normalize_answer(question)
        if question and answer and normalized_question not in seen:
            seen.add(normalized_question)
            questions.append({"id": len(questions) + 1, "question": question, "answer": answer})
        if len(questions) == count:
            break

    if len(questions) < count:
        for item in fallback_questions(normalized_topic, normalized_difficulty, count * 2):
            normalized_question = _normalize_answer(item["question"])
            if normalized_question in seen:
                continue
            seen.add(normalized_question)
            questions.append({"id": len(questions) + 1, "question": item["question"], "answer": item["answer"]})
            if len(questions) == count:
                break

    if len(questions) != count:
        raise ValueError("Unexpected question count from generator.")

    return questions


def generate_questions(topic: str, difficulty: str, count: int, api_key: str = "", model: str = "gpt-4.1-mini") -> tuple[list[dict], str]:
    normalized_topic = normalize_topic(topic)
    normalized_difficulty = normalize_difficulty(difficulty)

    if api_key:
        try:
            return openai_questions(normalized_topic, normalized_difficulty, count, api_key, model), "openai"
        except (ValueError, KeyError, json.JSONDecodeError, error.URLError, TimeoutError):
            pass

    return fallback_questions(normalized_topic, normalized_difficulty, count), "fallback"


def synthesize_speech(text: str, api_key: str, model: str, voice: str) -> bytes | None:
    if not api_key or not text.strip():
        return None

    body = json.dumps(
        {
            "model": model,
            "voice": voice,
            "input": text,
            "instructions": "Sound like a warm, clear, realistic technical interviewer. Speak naturally and confidently.",
            "format": "mp3",
        }
    ).encode("utf-8")

    api_request = request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=30) as response:
            return response.read()
    except error.URLError:
        return None


def review_answers(answers: list[dict]) -> dict:
    results = []
    score = 0
    total_time = 0.0

    for item in answers:
        user_answer = str(item.get("user_answer", "")).strip()
        correct_answer = str(item.get("correct_answer", "")).strip()
        response_time_seconds = float(item.get("response_time_seconds") or 0)
        correct = is_correct_answer(correct_answer, user_answer)
        time_score = 2 if response_time_seconds and response_time_seconds <= 5 else 1 if response_time_seconds and response_time_seconds <= 12 else 0
        question_score = int(correct) + time_score
        score += question_score
        total_time += response_time_seconds
        results.append(
            {
                "question": item.get("question", ""),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "correct": correct,
                "response_time_seconds": response_time_seconds,
                "time_score": time_score,
                "question_score": question_score,
            }
        )

    total_questions = len(results)
    average_response_time = (total_time / total_questions) if total_questions else 0.0
    return {
        "score": score,
        "total": total_questions,
        "max_score": total_questions * 3,
        "average_response_time": average_response_time,
        "results": results,
    }
