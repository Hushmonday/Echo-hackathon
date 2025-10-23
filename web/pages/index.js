import { useEffect, useRef, useState } from 'react'

export default function Home() {
  const [recording, setRecording] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioRef = useRef(null)
  const [aiResult, setAiResult] = useState('')

  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mr = new MediaRecorder(stream)
    mediaRecorderRef.current = mr
    audioChunksRef.current = []

    mr.ondataavailable = e => {
      if (e.data.size > 0) audioChunksRef.current.push(e.data)
    }

    mr.onstop = () => {
      const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
      const url = URL.createObjectURL(blob)
      setAudioUrl(url)
    }

    mr.start()
    setRecording(true)
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) mediaRecorderRef.current.stop()
    setRecording(false)
  }

  const uploadAudio = async () => {
    if (!audioUrl) return
    const blob = await fetch(audioUrl).then(r => r.blob())
    const fd = new FormData()
    fd.append('file', blob, 'recording.webm')

    const res = await fetch('http://localhost:8000/api/meetings/demo/audio', {
      method: 'POST',
      body: fd
    })
    const json = await res.json()
    alert('Uploaded: ' + JSON.stringify(json))
  }

  const generateSummary = async () => {
    // For demo, call server-side summarize with a mock transcript or real transcript
    const body = { transcript: 'Demo transcript text', mode: 'meeting' }
    const res = await fetch('http://localhost:8000/api/ai/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const json = await res.json()
    alert('Summary: ' + json.contentMd)
  }

  const createExport = async () => {
    const body = { sourceId: 'demo-note', format: 'pdf', content: 'This is a demo PDF exported from Echo.' }
    const res = await fetch('http://localhost:8000/api/exports/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const json = await res.json()
    if (json.url) {
      // open the generated PDF in a new tab
      window.open(json.url, '_blank')
    } else if (json.error) {
      alert('Export error: ' + JSON.stringify(json))
    }
  }

  // Chrome AI Writer demo
  const runWriterDemo = async () => {
    setAiResult('Calling Writer API...');
    if (window.chrome && window.chrome.ai && window.chrome.ai.write) {
      try {
        const resp = await window.chrome.ai.write({
          model: 'writer',
          input: 'Generate a meeting action plan for: Discuss project milestones and assign tasks.'
        });
        setAiResult('Writer result:\n' + (resp.output || JSON.stringify(resp)));
      } catch (e) {
        setAiResult('Error: ' + e.message);
      }
    } else {
      setAiResult('chrome.ai.write is not available in this browser.');
    }
  };

  // Chrome AI Summarizer demo
  const runSummarizerDemo = async () => {
    setAiResult('Calling Summarizer API...');
    if (window.chrome && window.chrome.ai && window.chrome.ai.summarize) {
      try {
        const resp = await window.chrome.ai.summarize({
          model: 'summarizer',
          input: 'Project kickoff meeting transcript: Discussed goals, assigned tasks, set deadlines.',
          options: { type: 'key-points', format: 'markdown', maxTokens: 400 }
        });
        setAiResult('Summarizer result:\n' + (resp.output || JSON.stringify(resp)));
      } catch (e) {
        setAiResult('Error: ' + e.message);
      }
    } else {
      setAiResult('chrome.ai.summarize is not available in this browser.');
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h1>Echo — Demo Recorder</h1>
      <div>
        {!recording && <button onClick={startRecording}>Start Recording</button>}
        {recording && <button onClick={stopRecording}>Stop Recording</button>}
        {audioUrl && (
          <div style={{ marginTop: 12 }}>
            <audio ref={audioRef} src={audioUrl} controls />
            <div style={{ marginTop: 8 }}>
              <button onClick={uploadAudio}>Upload to Server (demo)</button>
              <button style={{ marginLeft: 8 }} onClick={generateSummary}>Generate Summary</button>
              <button style={{ marginLeft: 8 }} onClick={createExport}>Export PDF</button>
            </div>
          </div>
        )}
      </div>
      <hr style={{ margin: '24px 0' }} />
      <div>
        <button onClick={runWriterDemo}>Writer API Demo</button>
        <button style={{ marginLeft: 8 }} onClick={runSummarizerDemo}>Summarizer API Demo</button>
      </div>
      <div style={{ marginTop: 16, whiteSpace: 'pre-wrap', background: '#f6f8fa', padding: 12, borderRadius: 6, minHeight: 40 }}>
        {aiResult}
      </div>
    </div>
  )
}
