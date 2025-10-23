from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uuid
import os
from ai_examples import router as ai_router
from exports_integration import router as exports_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), 'exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)

app = FastAPI()

# CORS: allow local dev web app and extension origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include AI example routes
app.include_router(ai_router)
app.include_router(exports_router)

# Serve generated exports (PDFs) under /exports
app.mount('/exports', StaticFiles(directory=EXPORTS_DIR), name='exports')

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post('/api/meetings/{meeting_id}/audio')
async def upload_audio(meeting_id: str, file: UploadFile = File(...)):
    # Simple demo: save the upload and return a fake transcribe job id
    filename = f"{meeting_id}-{uuid.uuid4().hex}-{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, 'wb') as f:
        content = await file.read()
        f.write(content)

    # For demo, return a mock transcription result
    mock_segments = [
        {"startMs": 0, "endMs": 12000, "speaker": "Speaker 1", "text": "This is a demo transcript segment."},
        {"startMs": 12000, "endMs": 24000, "speaker": "Speaker 2", "text": "This is another part of the demo transcript."}
    ]

    return JSONResponse({"transcribeJobId": uuid.uuid4().hex, "uploaded": filename, "mockSegments": mock_segments})

@app.get('/api/transcribe/{job_id}')
async def get_transcribe(job_id: str):
    # Demo: return done with mock segments
    return JSONResponse({"status": "done", "segments": [
        {"startMs": 0, "endMs": 12000, "speaker": "Speaker 1", "text": "This is a demo transcript segment."},
        {"startMs": 12000, "endMs": 24000, "speaker": "Speaker 2", "text": "This is another part of the demo transcript."}
    ]})

@app.post('/api/meetings/{meeting_id}/summaries')
async def summarize(meeting_id: str, body: dict):
    mode = body.get('mode', 'meeting')
    # Return a mocked summary
    summary_md = "# Summary\n\n- Key point 1\n- Key point 2\n"
    return JSONResponse({"noteId": uuid.uuid4().hex, "contentMd": summary_md, "mode": mode})
