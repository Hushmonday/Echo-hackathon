
# Echo — Intelligent Meeting & Classroom Notes

This repository contains the product spec, architecture notes, API examples, and integration patterns for Echo — a web + Chrome extension product that converts meeting and classroom audio into transcripts, structured AI-generated notes, action items, translations, and one-click exports.

## Local development (scaffold)

This repo now contains a minimal scaffold to get started:

- `web/` — Next.js web app (demo recorder UI). Run with:

```powershell
cd web; npm install; npm run dev
```

- `server/` — FastAPI demo server (mock STT & summarize endpoints). Run with:

```powershell
cd server; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn main:app --reload --port 8000
```

- `extension/` — MV3 extension shell (popup + background). Load `extension/` as unpacked in chrome://extensions.

The web recorder uploads to `http://localhost:8000/api/meetings/demo/audio` by default. The server returns mocked transcript segments and a mocked summary endpoint for development.

The project is designed for a hackathon using Chrome Built-in AI (Summarizer / Writer / Translator) where available, with fallbacks to Google-provided AI APIs when necessary. The spec below is written in English and includes example snippets, MV3 hints, and guidance for STT options (Web Speech API, cloud STT, or local WASM Whisper).

## 1. Product Overview

Echo is a Web App + Chrome extension that bundles:
- Real-time or uploaded audio recording (MediaRecorder / file upload)
- Speech-to-text (STT): streaming or batch (cloud STT or local WASM Whisper tiny)
- Structured AI notes: outline, key points, summary, Q&A, and action items
- Keyword & action-item extraction (assignees & due date placeholders)
- Multi-language translation (English ↔ Chinese)
- Post-meeting Q&A (RAG-lite retrieval + prompt orchestration)
- One-click export and integrations: PDF, .docx, Notion, Google Docs, Jira, Trello

Target scenarios: classroom lectures, meetings, interviews — reduce note-taking cost and improve review efficiency.

Form factors:
- Chrome Extension (Manifest V3) for in-browser recording, real-time captions and Built-in AI calls
- Web App (React / Next.js) for uploads, management, exports, and deeper post-processing

Key AI capabilities (competition emphasis): use Chrome Built-in AI APIs (Summarizer, Writer, Translator). STT is implemented using browser or external services; the Built-in AI provides summarization, writing, and translation.

Theme colors: Echo blue & white. Recommended brand: Gemini Nano where applicable.

## 2. Goals & Value

- Reduce recording burden: automated transcripts and structured notes (outline, key points, conclusions, action items).
- Improve review efficiency: one-click exports to common tools (Word/PDF/Notion/Google Docs/Jira/Trello).
- Cross-language collaboration: built-in translations for students and international meetings.
- Post-meeting Q&A: natural language question answering on notes and transcripts.

## 3. Users & Use Cases

- Students / TAs — lecture notes, knowledge extraction, study outlines
- Professionals (PMs, engineers, sales) — meeting minutes, decisions, action management
- Journalists & researchers — interview transcripts, Q&A extraction, summaries

## 4. Chrome Built-in AI Usage (Competition Alignment)

- Summarizer API: convert transcripts to structured notes (modes: class/meeting/interview). Support output types (key-points / paragraphs) and markdown format.
- Writer API: generate plans, action items, or reports from notes and goals.
- Translator API: translate notes and summaries between English and Chinese while preserving structure.
- Optional Prompt API: control prompt templates and style for post-meeting Q&A.

Note: STT is not part of Chrome Built-in AI. Use browser Web Speech API or a cloud STT service for transcribing audio. For demo/offline fallback, a local WASM Whisper (tiny) build can be provided.

## 5. Scope

MVP (3–4 weeks):
- Recording: client-side MediaRecorder; single-channel; sample rates 16k or 48k.
- STT: upload file batch transcription + simple streaming (cloud STT preferred; WASM fallback optional).
- Transcript: timestamped segments (start/end ms; optional speaker id).
- Smart notes: three modes — Class, Meeting, Interview.
	- Class: course outline, knowledge points, examples
	- Meeting: topics, takeaways, conclusions, action items
	- Interview: Q&A extraction + summary
- Keywords & action items extraction (assignee/dueDate placeholders)
- Multi-language translation (EN↔ZH)
- Exports: PDF/.docx, Notion, Google Docs
- Basic Q&A: retrieval-augmented QA (RAG-lite)
- Account: email signup/login; local/cloud storage toggle

V1 (+4–6 weeks):
- Calendar integration (Google Calendar read-only)
- Speaker diarization (cloud STT or simple local clustering)
- More exports: Jira/Trello task creation
- Team sharing & permissions
- Enhanced post-meeting Q&A with embeddings

Stretch features:
- Local offline STT with downloadable WASM Whisper models
- Custom prompt templates marketplace
- Speaker identity mapping with contacts

## 6. User Stories & Acceptance Criteria

1) Real-time class capture
- As a student I click "Start Recording" → stop after class → get transcript + course outline + knowledge points + examples.
- AC: transcript playable; click a segment to jump playback; generated outline/points are Markdown and exportable.

2) Meeting notes & action items
- As a PM I upload audio → system outputs topics/discussions/conclusions/action items and can push actions to Jira/Trello.
- AC: each action item contains title/assignee/dueDate (optional) and returns third-party links after successful creation.

3) Post-meeting Q&A
- As an attendee I ask "What are today's conclusions?"
- AC: system returns conclusions within 3s with source segment citations and timestamps.

4) Multi-language translation
- As an international student I translate notes EN→ZH
- AC: translation completes in 3s and preserves list/heading structure.

## 7. Flows

- Recording → segment STT → aggregate transcript → Summarizer → Writer → Translator → export/share
- Post-meeting QA: select session → load notes/transcript → construct prompt with relevant segments → return answer + citations

## 8. Architecture

Frontend
- React + Next.js for Web App
- Chrome MV3 extension for in-page recording & quick flows
- UI components: recorder, live captions, transcript player, note editor, export modal

Backend (optional for MVP but recommended)
- FastAPI (Python) or Spring Boot (Java) for APIs
- Auth: JWT
- Transcription queue: upload → job queue → STT provider
- Persistence: PostgreSQL (metadata) + S3-compatible storage (audio/export files)
- Export generation (docx/pdf) and third-party integrators
- Optional vector DB for embeddings (Weaviate / Pinecone / FAISS)

Security & Privacy
- HTTPS/TLS, server-side encryption, minimal retention policy, consent prompt before recording

Offline options
- WASM-based Whisper tiny for demo/offline transcription; run in worker/worklet

## 9. API Design (examples)

Below are example endpoints for the backend. Adjust authentication and payloads to your project needs.

POST /api/meetings
- Create a meeting record
Request body: { title, mode: "class|meeting|interview", startTime? }

POST /api/meetings/{id}/audio
- Upload audio chunk or file
Response: { transcribeJobId }

GET /api/transcribe/{jobId}
- Polling endpoint for transcription status and segments
Response: { status: "pending|processing|done", segments: [{ startMs, endMs, speaker, text }] }

POST /api/meetings/{id}/summaries
- Request structured notes
Request body: { mode: "class|meeting|interview", options: { summaryType:"key-points|paragraph" } }
Response: { noteId }

POST /api/notes/{id}/translate
- Translate a note
Request body: { targetLang: "en|zh" }

POST /api/exports/{format}
- Export notes/transcripts
Request body: { sourceId, format: "pdf|docx" }

POST /api/integrations/{provider}
- Provider: notion|gdocs|jira|trello
Request body: { payload }

## 10. Data Model (simplified)

- User(id, email, name, locale)
- Meeting(id, userId, title, mode, startedAt, endedAt)
- Recording(id, meetingId, url, duration, sampleRate)
- TranscriptSegment(id, meetingId, startMs, endMs, speaker, text)
- Note(id, meetingId, type:{outline,summary,qa,action_items}, contentMd, lang)
- ActionItem(id, meetingId, title, assignee, dueDate, sourceSegmentId)
- Export(id, meetingId, type, url, createdAt)

## 11. Non-functional Requirements

- Latency targets: real-time transcript segments visible < 1s; summary generation 3–8s; translation < 3s; QA first answer < 3s.
- Availability: 99.5% (MVP)
- Security: TLS, encrypted storage, minimal retention
- Privacy: consent before recording; data deletion support

# Echo-hackathon

## What is Echo?
Echo is a productivity tool for meetings, classes, and interviews. It helps you:
- Record audio and convert it to text (speech-to-text)
- Generate smart notes, summaries, and action items using AI
- Translate notes between English and Chinese
- Export notes to PDF, Word, Notion, Google Docs, Jira, Trello
- Use Chrome's built-in AI (Writer, Summarizer, Translator) if available, or fallback to backend AI

## Main Features
- Real-time or uploaded audio recording
- Automatic transcription (STT)
- AI-powered note generation (outline, summary, Q&A, action items)
- Multi-language translation
- One-click export and integration

## Quick Start (Local Development)
1. **Start the backend (FastAPI):**
	```powershell
	cd server
	.\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	uvicorn main:app --reload --port 8000
	```
2. **Start the web app (Next.js):**
	```powershell
	cd web
	npm install
	npm run dev
	```
3. **Load the Chrome extension:**
	- Go to `chrome://extensions` → Enable Developer mode → Load unpacked → select `extension` folder.

## Chrome AI API Usage
- If your Chrome supports built-in AI, you can use `chrome.ai.write`, `chrome.ai.summarize`, and `chrome.ai.translate` directly in the extension or web app.
- If not available, the app will fallback to backend AI endpoints.
- To check if available, open DevTools Console and enter:
  ```javascript
  window.chrome.ai
  ```
- If it returns `undefined`, the API is not yet available in your browser.

## Backend AI Fallback
- The backend (FastAPI) provides endpoints for summarization, writing, translation, and export using server-side AI (Google Cloud, PaLM, Gemini, etc.).
- You can extend the backend to use your own AI provider if needed.

## Export & Integration
- Export notes and transcripts to PDF, Word, Notion, Google Docs, Jira, Trello.
- PDF export is implemented using ReportLab and served from `/exports`.

## Contributing
Feel free to fork, submit issues, or open pull requests!

## Contact
For questions or collaboration, open an issue or contact the repo owner.
	input: transcriptText,

	options: { type: 'key-points', format: 'markdown', maxTokens: 800 }
