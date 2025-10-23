# AI Snippets for Echo (pseudocode)

## Chrome Built-in AI (pseudocode)

// Summarize transcript into key points (markdown)
const resp = await chrome.ai.summarize({
  model: 'summarizer',
  input: transcriptText,
  options: { type: 'key-points', format: 'markdown', maxTokens: 800 }
})

// Translate markdown note
const tr = await chrome.ai.translate({ model: 'translator', input: noteMd, target: 'zh' })

// Writer example (generate action plan)
const plan = await chrome.ai.write({ model: 'writer', input: 'Generate action plan from notes: ' + notes })

// Note: use feature-detection. If chrome.ai is not available, call backend /api/ai/summarize which will call PaLM/Google AI.

## Server-side PaLM fallback (pseudocode)

// POST /api/ai/summarize { transcript, mode }
// Server uses Google AI SDK (Python/Node) with credentials stored on server.

# Python (pseudocode)
from google.ai import SomeClient
client = SomeClient(credentials=SERVICE_ACCOUNT_JSON)
response = client.generate(model='models/text-bison-001', prompt=prompt)

# Return structured markdown to client
