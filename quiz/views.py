import json
from urllib import error, request as urllib_request

from django.conf import settings
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .services import generate_questions, is_correct_answer, normalize_topic


@ensure_csrf_cookie
@require_GET
def home(request):
    return render(request, "quiz/home.html")


@require_POST
def quiz_session(request):
    payload = json.loads(request.body.decode("utf-8") or "{}")

    if "answers" in payload:
        results = []
        score = 0
        total_time = 0.0
        for item in payload.get("answers", []):
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
        return JsonResponse(
            {
                "score": score,
                "total": total_questions,
                "max_score": total_questions * 3,
                "average_response_time": average_response_time,
                "results": results,
            }
        )

    topic = normalize_topic(str(payload.get("topic", "python")))
    difficulty = str(payload.get("difficulty", "medium")).strip() or "medium"
    count = min(max(int(payload.get("count", 12)), 5), 25)
    questions, source = generate_questions(topic=topic, difficulty=difficulty, count=count)

    return JsonResponse(
        {
            "topic": topic,
            "difficulty": difficulty,
            "count": count,
            "source": source,
            "questions": questions,
        }
    )


@require_POST
def speak_question(request):
    if not settings.OPENAI_API_KEY:
        return HttpResponse(status=204)

    payload = json.loads(request.body.decode("utf-8") or "{}")
    text = str(payload.get("text", "")).strip()
    if not text:
        return HttpResponse(status=400)

    body = json.dumps(
        {
            "model": settings.OPENAI_TTS_MODEL,
            "voice": settings.OPENAI_TTS_VOICE,
            "input": text,
            "instructions": "Sound like a warm, clear, realistic technical interviewer. Speak naturally and confidently.",
            "format": "mp3",
        }
    ).encode("utf-8")

    api_request = urllib_request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=body,
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(api_request, timeout=30) as response:
            audio_bytes = response.read()
    except error.URLError:
        return HttpResponse(status=502)

    return HttpResponse(audio_bytes, content_type="audio/mpeg")
