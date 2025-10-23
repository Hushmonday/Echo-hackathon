FastAPI server for Echo demo

Quick start (Windows PowerShell):

# create a virtualenv
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# install
pip install -r requirements.txt

# run
uvicorn main:app --reload --port 8000

This server provides demo endpoints:
- POST /api/meetings/{meeting_id}/audio  (multipart file)
- GET  /api/transcribe/{job_id}  (mocked result)
- POST /api/meetings/{meeting_id}/summaries  (mocked summary)

Replace mocks with real STT and AI calls as you integrate Google Cloud Speech-to-Text and PaLM or use Chrome Built-in AI in the extension/web UI.

## Integrating Google Cloud Speech-to-Text (example)

- Install optional deps (uncomment in requirements.txt): google-cloud-speech, google-cloud-storage
- Use `google_stt_example.py` as a reference for uploading audio to GCS and calling longRunningRecognize.
- Set environment variable: `GOOGLE_APPLICATION_CREDENTIALS` to your service account JSON before running server.

## PaLM / Google AI fallback (server-side)

- Keep credentials on the server and never commit them to source control.
- The `ai_examples.py` file shows a placeholder `/api/ai/summarize` endpoint. Replace the mock implementation with calls to the Google AI client SDK (PaLM) and return structured markdown.

Example (pseudocode):

```python
from google.ai import SomeClient
client = SomeClient(credentials=SERVICE_ACCOUNT_JSON)
response = client.generate(model='models/text-bison-001', prompt=prompt)
```

Return the generated markdown or structured JSON to the web client.