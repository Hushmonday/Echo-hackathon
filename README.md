
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

## 12. Metrics / KPIs

- DAU/WAU, session completion rate, median time from recording to summary, export/integration conversion, QA success rate, D7/D30 retention
- Note satisfaction (1–5 stars)

## 13. Milestones

- W1: project scaffold (Web + Ext + backend), recording & upload, STT pipeline
- W2: transcript aggregation, summarizer-based structured notes, translation, PDF/Word export
- W3: three templates polishing, action item structuring & Notion/Docs integration
- W4: RAG-lite QA, accessibility & polish, 3-minute demo video + Devpost submission

## 14. Risks & Mitigations

- STT cost/latency: prefer high-ROI cloud STT for MVP; keep WASM as demo fallback
- Built-in AI availability: detect availability() and fallback to Google AI endpoints or server LLMs
- Long audio memory: chunk uploads & chunked summarization

## 15. 3-minute Demo Script

1) Open extension; Start Recording (Class) — show live captions
2) Stop → show transcript; click segment to play
3) Click "Generate Class Notes" → show outline, knowledge points, examples
4) Upload meeting audio → generate meeting notes + action items → push one to Trello
5) Ask: "What are today's conclusions?" → return answer with timestamped citation
6) Click Translate → English notes become Chinese → Export PDF

## Examples & Implementation Notes

1) MV3 manifest (skeleton)

manifest.json (Manifest V3 skeleton):

{
	"manifest_version": 3,
	"name": "Echo — AI Notes",
	"version": "0.1.0",
	"permissions": ["storage", "activeTab", "scripting", "tabs", "notifications", "microphone"],
	"host_permissions": ["*://*/*"],
	"background": { "service_worker": "dist/background.js" },
	"action": { "default_popup": "popup.html", "default_icon": "icons/icon.png" }
}

2) Recording & STT options

- Browser Web Speech API (simple demo, limited browser support)
- MediaRecorder capture then upload slices to cloud STT (recommended)
- WASM Whisper tiny in a WebWorker/AudioWorklet for offline demo

3) Example: calling Chrome Built-in Summarizer / Writer / Translator

Note: The exact client call pattern will follow the competition's Chrome Built-in AI documentation. Below is a pseudocode sketch.

// Pseudocode: use Summarizer to convert transcript to keypoints
const response = await chrome.ai.summarize({
	model: 'summarizer',
	input: transcriptText,
	options: { type: 'key-points', format: 'markdown', maxTokens: 800 }
});

// Pseudocode: translate a markdown note
const tr = await chrome.ai.translate({ model: 'translator', input: noteMd, target: 'zh' });

// If built-in APIs are unavailable, fallback to Google AI endpoints (or other LLM providers)

4) Fallback: Google AI / PaLM endpoints

When Built-in AI isn't available, call Google AI or PaLM endpoints from backend with proper keys. Keep secrets on server-side and not in the extension.

Example flow: generate structured note via backend PaLM call

POST /api/ai/summarize
Request: { transcriptText, mode }
Server: use Google AI client to call PaLM/Model.generate with a prompt template matching mode

5) STT Integration examples

- Cloud STT (Google Cloud Speech-to-Text): client uploads audio to backend → backend calls Speech-to-Text longRunningRecognize or streamingRecognize
- Web Speech API: navigator.mediaDevices.getUserMedia + SpeechRecognition (on supported browsers)
- WASM Whisper: run inference in a WebWorker; suitable only for short-demo audio due to model size/perf

## How to Run (dev)

- Web App (Next.js)
	- Install dependencies: npm install
	- Dev server: npm run dev

- Chrome Extension
	- Build extension: npm run build:ext
	- Load unpacked extension in chrome://extensions → Load unpacked → select dist/

## Notes on Competition Requirements

- Use Chrome Built-in AI (Summarizer/Writer/Translator) for core features where possible.
- Provide clear fallback to Google AI/PaLM when built-in is unavailable. Keep API keys on server side and ensure the Manifest & privacy wording explain what data is sent to external services.

## Next Steps (implementation suggestions)

1) Scaffold Next.js app + MV3 extension shell that shares UI components
2) Implement MediaRecorder + upload pipeline
3) Integrate cloud STT for stable transcription
4) Call Built-in Summarizer for structured notes; add backend PaLM fallback
5) Add exports (PDF/docx) and Notion/Google Docs connectors

---

If you want, I can:
- Add example Next.js + MV3 starter files (recorder, background worker, manifest) ready to run
- Create a small backend example (FastAPI) with endpoints for uploads, STT orchestration, and PaLM fallback
- Add unit smoke tests and a 3-minute demo script in a README-friendly checklist

Tell me which of these you'd like me to implement next and I'll create a todo and start coding.

