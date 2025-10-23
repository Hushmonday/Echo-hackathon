from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, FileResponse
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

router = APIRouter()


def generate_pdf(path: str, title: str, body_text: str):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setFont('Helvetica-Bold', 16)
    c.drawString(72, height - 72, title)
    c.setFont('Helvetica', 12)
    textobj = c.beginText(72, height - 100)
    for line in body_text.split('\n'):
        textobj.textLine(line)
    c.drawText(textobj)
    c.showPage()
    c.save()


@router.post('/api/exports/{format}')
async def create_export(format: str, request: Request):
    body = await request.json()
    source_id = body.get('sourceId')
    if not source_id:
        return JSONResponse({"error": "missing sourceId"}, status_code=400)

    export_id = uuid.uuid4().hex
    filename = f"{export_id}.{format}"
    exports_dir = os.path.join(os.path.dirname(__file__), 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    path = os.path.join(exports_dir, filename)

    # Simple PDF content: use provided 'content' or a placeholder
    content = body.get('content', f'Export for {source_id}')
    # Only support pdf for now
    if format != 'pdf':
        return JSONResponse({"error": "only pdf export supported in demo"}, status_code=400)

    generate_pdf(path, f'Export: {source_id}', content)

    # Return public URL served by StaticFiles mounted at /exports
    url = f"http://localhost:8000/exports/{filename}"
    return JSONResponse({"exportId": export_id, "url": url})


@router.post('/api/integrations/{provider}')
async def integration(provider: str, request: Request):
    body = await request.json()
    if not body:
        return JSONResponse({"error": "missing payload"}, status_code=400)
    external_link = f"https://{provider}.example.com/item/{uuid.uuid4().hex}"
    return JSONResponse({"status": "ok", "link": external_link})
