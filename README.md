# Voice Quiz Arena

This repository now includes a Streamlit version of the AI interview app for deployment.

## Streamlit App

Main entrypoint:

```text
streamlit_app.py
```

Features:

- Python and Java interview modes
- Easy, medium, and hard difficulty levels
- OpenAI-backed question generation when `OPENAI_API_KEY` is set
- Built-in fallback question banks when no API key is available
- Realistic AI voice playback with OpenAI TTS
- Response-time-based scoring and review

## Run Locally

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the Streamlit app:

```powershell
streamlit run streamlit_app.py
```

## Environment

Set these values in `.env` for local development:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=coral
```

If `OPENAI_API_KEY` is empty, the app still works with the built-in fallback interview questions, but realistic voice playback will be unavailable.

## Deploy To Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from your repository.
4. Set the entrypoint file to `streamlit_app.py`.
5. Add these secrets in the Streamlit app settings:

```toml
OPENAI_API_KEY="your_api_key_here"
OPENAI_MODEL="gpt-4.1-mini"
OPENAI_TTS_MODEL="gpt-4o-mini-tts"
OPENAI_TTS_VOICE="coral"
```

6. Deploy.
