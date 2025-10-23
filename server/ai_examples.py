from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import uuid

router = APIRouter()


@router.post('/api/ai/summarize')
async def ai_summarize(request: Request):
    body = await request.json()
    transcript = body.get('transcript', '')
    mode = body.get('mode', 'meeting')
    if not transcript:
        return JSONResponse({"error": "missing transcript in request body"}, status_code=400)
    summary = f"# {mode.capitalize()} Summary\n\n- Generated summary for provided transcript (length {len(transcript)})."
    return JSONResponse({"noteId": uuid.uuid4().hex, "contentMd": summary})


@router.post('/api/ai/paLMFallback')
async def paLM_fallback(request: Request):
    # Placeholder: show how server-side code would handle PaLM call (pseudocode style)
    body = await request.json()
    # Attempt to call Google AI if available; otherwise return a helpful message
    try:
        # The real implementation would look like this (pseudocode):
        # from google.ai import generativelanguage as gl
        # client = gl.YourClient()
        # response = client.generate(...)
        # For demo, we just echo back
        transcript = body.get('transcript', '')
        if not transcript:
            return JSONResponse({"error": "missing transcript"}, status_code=400)
        generated = f"(paLM fallback simulated) Summary for transcript length {len(transcript)}"
        return JSONResponse({"status": "ok", "contentMd": f"# Summary\n\n- {generated}"})
    except Exception as e:
        return JSONResponse({"error": "PaLM client not available. Install Google AI client and set credentials.", "details": str(e)}, status_code=500)
