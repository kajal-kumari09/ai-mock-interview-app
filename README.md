# Voice Quiz Arena

A Django project that generates quiz questions and asks them in voice using browser speech features.

## Features

- Topic-based quiz generation
- OpenAI-backed question creation when `OPENAI_API_KEY` is set
- Built-in fallback questions when no API key is available
- Browser text-to-speech for reading questions aloud
- Browser speech-to-text for spoken answers when supported
- Instant scoring at the end of the session

## Run locally

```powershell
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`

## Environment

Set these values in `.env` if you want live AI-generated questions:

```env
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=coral
# DATABASE_PATH=C:\path\to\db.sqlite3
```

If `OPENAI_API_KEY` is empty, the app uses the built-in fallback quiz bank.
If OneDrive causes SQLite locking issues on your machine, set `DATABASE_PATH` in `.env` to a folder outside the synced project directory.
The realistic interviewer voice uses OpenAI TTS when your API key is set; otherwise the app falls back to the browser voice.
