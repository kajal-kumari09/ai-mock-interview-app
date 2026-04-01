import base64
import os
import time
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from quiz.streamlit_engine import generate_questions, load_env_file, review_answers, synthesize_speech

BASE_DIR = Path(__file__).resolve().parent
load_env_file(BASE_DIR)


def get_setting(name: str, default: str = "") -> str:
    try:
        if name in st.secrets:
            return str(st.secrets[name])
    except Exception:
        pass
    return os.getenv(name, default)


def autoplay_audio(audio_bytes: bytes) -> None:
    encoded = base64.b64encode(audio_bytes).decode("utf-8")
    components.html(
        f"""
        <audio autoplay controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{encoded}" type="audio/mp3">
        </audio>
        """,
        height=54,
    )


def init_state() -> None:
    defaults = {
        "questions": [],
        "answers": [],
        "current_index": 0,
        "session_started": False,
        "question_started_at": None,
        "review": None,
        "source": "waiting",
        "audio_cache": {},
        "autoplay": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def start_interview(topic: str, difficulty: str, count: int) -> None:
    questions, source = generate_questions(
        topic=topic,
        difficulty=difficulty,
        count=count,
        api_key=get_setting("OPENAI_API_KEY"),
        model=get_setting("OPENAI_MODEL", "gpt-4.1-mini"),
    )
    st.session_state.questions = questions
    st.session_state.answers = [None] * len(questions)
    st.session_state.current_index = 0
    st.session_state.session_started = True
    st.session_state.question_started_at = None
    st.session_state.review = None
    st.session_state.source = source
    st.session_state.audio_cache = {}
    st.session_state.autoplay = True


def save_current_answer(current_answer: str) -> None:
    if not st.session_state.questions:
        return

    question = st.session_state.questions[st.session_state.current_index]
    elapsed = 0.0
    if st.session_state.question_started_at:
        elapsed = max(0.1, round(time.time() - st.session_state.question_started_at, 1))

    st.session_state.answers[st.session_state.current_index] = {
        "question": question["question"],
        "correct_answer": question["answer"],
        "user_answer": current_answer.strip(),
        "response_time_seconds": elapsed,
    }


def average_time() -> float:
    valid_times = [
        item["response_time_seconds"]
        for item in st.session_state.answers
        if item and isinstance(item.get("response_time_seconds"), (int, float))
    ]
    if not valid_times:
        return 0.0
    return sum(valid_times) / len(valid_times)


def current_prompt(question: dict, index: int) -> str:
    return f"Question {index + 1}. {question['question']}. Please answer after the voice finishes."


st.set_page_config(page_title="Voice Quiz Arena", page_icon="🎙️", layout="wide")
init_state()

st.title("Voice Quiz Arena")
st.caption("Streamlit edition: AI-generated Java and Python interview questions with realistic voice playback.")

with st.sidebar:
    st.header("Interview Setup")
    topic = st.selectbox("Topic", ["python", "java"], format_func=str.title)
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1, format_func=str.title)
    count = st.slider("Number of questions", min_value=5, max_value=25, value=12)
    if st.button("Start Interview", use_container_width=True, type="primary"):
        start_interview(topic, difficulty, count)
        st.rerun()
    st.markdown("**Voice source**")
    if get_setting("OPENAI_API_KEY"):
        st.success("OpenAI realistic voice is enabled.")
    else:
        st.warning("Set `OPENAI_API_KEY` to enable realistic voice playback on Streamlit.")

left, right = st.columns([1.7, 1])

with right:
    st.subheader("Session")
    if st.session_state.session_started:
        st.metric("Progress", f"{st.session_state.current_index + 1} / {len(st.session_state.questions)}")
        st.metric("Question source", "OpenAI live" if st.session_state.source == "openai" else "Smart fallback")
        st.metric("Average response time", f"{average_time():.1f}s")
    else:
        st.metric("Progress", "0 / 0")
        st.metric("Question source", "Waiting")
        st.metric("Average response time", "0.0s")

with left:
    if not st.session_state.session_started:
        st.info("Choose a topic and difficulty from the sidebar, then start the interview.")
    elif st.session_state.current_index >= len(st.session_state.questions):
        st.success("All questions are complete. Review your results below.")
    else:
        question = st.session_state.questions[st.session_state.current_index]
        st.subheader(f"Question {st.session_state.current_index + 1}")
        st.markdown(f"### {question['question']}")

        if st.session_state.question_started_at is None:
            st.session_state.question_started_at = time.time()
            st.session_state.autoplay = True

        prompt = current_prompt(question, st.session_state.current_index)
        audio_key = prompt
        if audio_key not in st.session_state.audio_cache:
            st.session_state.audio_cache[audio_key] = synthesize_speech(
                text=prompt,
                api_key=get_setting("OPENAI_API_KEY"),
                model=get_setting("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
                voice=get_setting("OPENAI_TTS_VOICE", "coral"),
            )

        audio_bytes = st.session_state.audio_cache.get(audio_key)
        if audio_bytes and st.session_state.autoplay:
            autoplay_audio(audio_bytes)
            st.session_state.autoplay = False
        elif audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.caption("Voice playback is unavailable until an OpenAI API key is configured.")

        answer_key = f"answer_{st.session_state.current_index}"
        default_answer = ""
        if st.session_state.answers[st.session_state.current_index]:
            default_answer = st.session_state.answers[st.session_state.current_index]["user_answer"]
        st.session_state.setdefault(answer_key, default_answer)
        current_answer = st.text_area("Your answer", key=answer_key, height=150, placeholder="Type your answer here...")

        action_col1, action_col2, action_col3 = st.columns(3)
        if action_col1.button("Replay Question", use_container_width=True):
            st.session_state.autoplay = True
            st.rerun()
        if action_col2.button("Save and Next", use_container_width=True, type="primary"):
            save_current_answer(current_answer)
            st.session_state.current_index += 1
            st.session_state.question_started_at = None
            st.session_state.autoplay = True
            st.rerun()
        if action_col3.button("Finish Interview", use_container_width=True):
            save_current_answer(current_answer)
            st.session_state.review = review_answers([item for item in st.session_state.answers if item])
            st.session_state.current_index = len(st.session_state.questions)
            st.session_state.question_started_at = None
            st.rerun()

if st.session_state.review:
    review = st.session_state.review
    st.divider()
    st.subheader("Review")
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Score", f"{review['score']} / {review['max_score']}")
    metric2.metric("Average response time", f"{review['average_response_time']:.1f}s")
    metric3.metric("Questions answered", str(review["total"]))

    for item in review["results"]:
        with st.container(border=True):
            st.markdown(f"**{item['question']}**")
            st.write(f"Your answer: {item['user_answer'] or 'No answer'}")
            st.write(f"Expected answer: {item['correct_answer']}")
            st.write(f"Response time: {item['response_time_seconds']:.1f}s")
            st.write(f"Speed score: {item['time_score']} / 2")
            st.write(f"Question score: {item['question_score']} / 3")
            st.write("Result: Correct" if item["correct"] else "Result: Needs work")
