const state = {
    muted: false,
    recognition: null,
    questions: [],
    answers: [],
    index: -1,
    voices: [],
    selectedVoice: null,
    autoInterview: true,
    isListening: false,
    currentAudio: null,
    questionStartedAt: null,
};

const els = {
    form: document.getElementById("quiz-form"),
    topic: document.getElementById("topic"),
    difficulty: document.getElementById("difficulty"),
    count: document.getElementById("count"),
    status: document.getElementById("status"),
    questionTitle: document.getElementById("question-title"),
    answerInput: document.getElementById("answer-input"),
    progressLabel: document.getElementById("progress-label"),
    scoreDisplay: document.getElementById("score-display"),
    sourceBadge: document.getElementById("source-badge"),
    speakToggle: document.getElementById("speak-toggle"),
    repeatBtn: document.getElementById("repeat-btn"),
    listenBtn: document.getElementById("listen-btn"),
    nextBtn: document.getElementById("next-btn"),
    finishBtn: document.getElementById("finish-btn"),
    results: document.getElementById("results"),
    speechSupport: document.getElementById("speech-support"),
    modeDisplay: document.getElementById("mode-display"),
    interviewState: document.getElementById("interview-state"),
    timeDisplay: document.getElementById("time-display"),
};

function getCookie(name) {
    const cookie = document.cookie
        .split("; ")
        .find((row) => row.startsWith(`${name}=`));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

function updateStatus(message) {
    els.status.textContent = message;
}

function updateInterviewState(message) {
    els.interviewState.textContent = message;
}

function pickVoice() {
    const voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    state.voices = voices;
    state.selectedVoice =
        voices.find((voice) => /en(-|_)?(in|gb|us)/i.test(voice.lang) && /female|zira|aria|google/i.test(voice.name)) ||
        voices.find((voice) => /en(-|_)?(in|gb|us)/i.test(voice.lang)) ||
        voices[0] ||
        null;
}

function speak(text) {
    if (state.muted || !("speechSynthesis" in window)) {
        return null;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    if (state.selectedVoice) {
        utterance.voice = state.selectedVoice;
        utterance.lang = state.selectedVoice.lang;
    }
    utterance.rate = 0.96;
    utterance.pitch = 1.02;
    window.speechSynthesis.speak(utterance);
    return utterance;
}

async function playQuestionAudio(text) {
    const response = await fetch("/api/speak-question/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ text }),
    });

    if (!response.ok) {
        return false;
    }

    const blob = await response.blob();
    if (!blob.size) {
        return false;
    }

    if (state.currentAudio) {
        state.currentAudio.pause();
        URL.revokeObjectURL(state.currentAudio.src);
    }

    const audioUrl = URL.createObjectURL(blob);
    const audio = new Audio(audioUrl);
    state.currentAudio = audio;
    audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        if (state.currentAudio === audio) {
            state.currentAudio = null;
        }
        if (state.recognition && state.autoInterview) {
            startListening();
        }
    };
    await audio.play();
    return true;
}

async function askCurrentQuestion() {
    const question = state.questions[state.index];
    if (!question) {
        return;
    }

    state.questionStartedAt = Date.now();
    updateInterviewState("Asking");
    const prompt = `Question ${state.index + 1}. ${question.question}. Please answer after the voice stops.`;

    try {
        const usedRealisticVoice = await playQuestionAudio(prompt);
        if (usedRealisticVoice) {
            updateStatus("The AI interviewer is asking the question in a realistic voice.");
            return;
        }
    } catch (error) {
        updateStatus("OpenAI voice was unavailable, so the browser voice is being used.");
    }

    const utterance = speak(prompt);
    if (utterance && state.recognition && state.autoInterview) {
        utterance.onend = () => startListening();
    }
}

function renderQuestion() {
    const question = state.questions[state.index];
    if (!question) {
        els.questionTitle.textContent = "Your question will appear here.";
        els.progressLabel.textContent = "Question 0 / 0";
        els.answerInput.value = "";
        updateInterviewState("Idle");
        return;
    }

    els.questionTitle.textContent = question.question;
    els.progressLabel.textContent = `Question ${state.index + 1} / ${state.questions.length}`;
    els.answerInput.value = state.answers[state.index]?.user_answer || "";
    askCurrentQuestion();
}

function startListening() {
    if (!state.recognition || state.isListening) {
        return;
    }

    try {
        state.isListening = true;
        els.listenBtn.textContent = "Listening...";
        updateInterviewState("Listening");
        updateStatus("The interviewer has finished speaking. You can answer now.");
        state.recognition.start();
    } catch (error) {
        state.isListening = false;
        updateStatus("The microphone could not start. You can still type your answer.");
        updateInterviewState("Waiting");
    }
}

function setSpeechRecognition() {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!Recognition) {
        els.speechSupport.textContent = "Not available";
        els.listenBtn.disabled = true;
        els.modeDisplay.textContent = "Text only";
        updateInterviewState("Text only");
        return;
    }

    state.recognition = new Recognition();
    state.recognition.lang = "en-IN";
    state.recognition.interimResults = false;
    state.recognition.maxAlternatives = 1;
    els.speechSupport.textContent = "Available";

    state.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        els.answerInput.value = transcript;
        saveCurrentAnswer();
        updateStatus("Your spoken answer was captured. Preparing the next question.");
        updateInterviewState("Answer saved");

        if (state.autoInterview) {
            window.setTimeout(() => {
                moveNext();
            }, 900);
        }
    };

    state.recognition.onerror = () => {
        state.isListening = false;
        updateStatus("There was a problem with voice input. You can type your answer instead.");
        updateInterviewState("Mic issue");
    };

    state.recognition.onend = () => {
        state.isListening = false;
        els.listenBtn.textContent = "Answer by Voice";
        if (state.index >= 0 && !els.answerInput.value.trim()) {
            updateInterviewState("Waiting for answer");
        }
    };
}

function saveCurrentAnswer() {
    if (state.index < 0 || !state.questions[state.index]) {
        return;
    }

    const elapsedSeconds = state.questionStartedAt
        ? Math.max(0.1, Number(((Date.now() - state.questionStartedAt) / 1000).toFixed(1)))
        : null;

    state.answers[state.index] = {
        question: state.questions[state.index].question,
        correct_answer: state.questions[state.index].answer,
        user_answer: els.answerInput.value.trim(),
        response_time_seconds: elapsedSeconds,
    };

    updateAverageTime();
}

function updateAverageTime() {
    const times = state.answers
        .filter(Boolean)
        .map((item) => item.response_time_seconds)
        .filter((value) => typeof value === "number");

    if (!times.length) {
        els.timeDisplay.textContent = "0.0s";
        return;
    }

    const average = times.reduce((total, value) => total + value, 0) / times.length;
    els.timeDisplay.textContent = `${average.toFixed(1)}s`;
}

async function createQuiz(event) {
    event.preventDefault();
    updateStatus("Generating your AI interview...");
    updateInterviewState("Preparing");
    els.results.innerHTML = "";
    els.scoreDisplay.textContent = "0 / 0";
    els.timeDisplay.textContent = "0.0s";

    const response = await fetch("/api/quiz-session/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            topic: els.topic.value,
            difficulty: els.difficulty.value,
            count: Number(els.count.value),
        }),
    });

    const data = await response.json();
    state.questions = data.questions || [];
    state.answers = new Array(state.questions.length).fill(null);
    state.index = state.questions.length ? 0 : -1;
    state.questionStartedAt = null;
    els.sourceBadge.textContent = data.source === "openai" ? "OpenAI live" : "Smart fallback";
    updateStatus(`${data.count} questions are ready on ${data.topic}. The AI interviewer will ask them one by one.`);
    renderQuestion();
}

function moveNext() {
    saveCurrentAnswer();
    if (state.index < state.questions.length - 1) {
        state.index += 1;
        renderQuestion();
        updateStatus("Your answer was saved. Asking the next question.");
        return;
    }

    updateStatus("All questions are complete. Finish the interview to review your results.");
    updateInterviewState("Completed");
}

async function finishQuiz() {
    saveCurrentAnswer();
    const usableAnswers = state.answers.filter(Boolean);
    if (!usableAnswers.length) {
        updateStatus("Answer at least one question before finishing.");
        return;
    }

    const response = await fetch("/api/quiz-session/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            answers: usableAnswers,
        }),
    });

    const data = await response.json();
    els.scoreDisplay.textContent = `${data.score} / ${data.max_score}`;
    els.timeDisplay.textContent = `${data.average_response_time.toFixed(1)}s`;
    els.results.innerHTML = "";

    data.results.forEach((item) => {
        const block = document.createElement("div");
        block.className = "result-item";
        block.innerHTML = `
            <strong>${item.question}</strong>
            <div class="${item.correct ? "result-correct" : "result-wrong"}">
                ${item.correct ? "Correct" : "Needs work"}
            </div>
            <div>Your answer: ${item.user_answer || "No answer"}</div>
            <div>Expected: ${item.correct_answer}</div>
            <div>Response time: ${item.response_time_seconds?.toFixed(1) || "0.0"}s</div>
            <div>Speed score: ${item.time_score} / 2</div>
            <div>Total for this question: ${item.question_score} / 3</div>
        `;
        els.results.appendChild(block);
    });

    updateStatus("Interview complete. Review your performance below.");
    updateInterviewState("Finished");
    speak(`Interview complete. You scored ${data.score} out of ${data.max_score}. Your average response time was ${data.average_response_time.toFixed(1)} seconds.`);
}

els.form.addEventListener("submit", createQuiz);
els.nextBtn.addEventListener("click", moveNext);
els.finishBtn.addEventListener("click", finishQuiz);
els.repeatBtn.addEventListener("click", askCurrentQuestion);
els.speakToggle.addEventListener("click", () => {
    state.muted = !state.muted;
    els.speakToggle.textContent = state.muted ? "Enable Voice" : "Mute Voice";
    els.modeDisplay.textContent = state.muted ? "Mic + Text" : "Auto Voice Interview";
    updateStatus(state.muted ? "Question voice is muted." : "Question voice is enabled.");
});

els.listenBtn.addEventListener("click", () => {
    if (!state.recognition) {
        updateStatus("Speech recognition is not supported in this browser.");
        return;
    }
    startListening();
});

pickVoice();
if ("speechSynthesis" in window) {
    window.speechSynthesis.onvoiceschanged = pickVoice;
}
setSpeechRecognition();
