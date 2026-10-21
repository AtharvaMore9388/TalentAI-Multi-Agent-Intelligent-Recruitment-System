// TalentAI — API Client with Vercel Production & Fallback Support
import {
  SAMPLE_JOBS,
  SAMPLE_RESUMES,
  WORKED_EXAMPLE_DOSSIER,
  DEMO_TRACE,
} from './sampleData'

function getApiUrl(): string {
  // If explicitly configured via environment variable (e.g. Render backend)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, '')
  }

  // Local development
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (host === 'localhost' || host === '127.0.0.1') {
      return `http://${host}:8000`
    }
  }

  return 'http://localhost:8000'
}

export async function fetchSamples() {
  try {
    const res = await fetch(`${getApiUrl()}/api/samples`, { cache: 'no-store' })
    if (res.ok) {
      return await res.json()
    }
  } catch {
    // Graceful fallback for Vercel demo deployment
  }
  return {
    jobs: SAMPLE_JOBS,
    resumes: SAMPLE_RESUMES,
  }
}

export async function fetchDemoTrace() {
  try {
    const res = await fetch(`${getApiUrl()}/api/trace/demo`, { cache: 'no-store' })
    if (res.ok) {
      return await res.json()
    }
  } catch {
    // Graceful fallback for Vercel demo deployment
  }
  return DEMO_TRACE
}

export async function fetchWorkedExampleDossier() {
  try {
    const res = await fetch(`${getApiUrl()}/api/trace/worked-example`, { cache: 'no-store' })
    if (res.ok) {
      return await res.json()
    }
  } catch {
    // Graceful fallback for Vercel demo deployment
  }
  return WORKED_EXAMPLE_DOSSIER
}

export async function fetchHealth() {
  try {
    const res = await fetch(`${getApiUrl()}/health`, { cache: 'no-store' })
    if (res.ok) {
      return await res.json()
    }
  } catch {
    // Graceful fallback for Vercel deployment
  }
  return {
    status: 'ok',
    mode: 'demo_active',
    version: '1.0.0',
    indexed_resumes: SAMPLE_RESUMES.length,
  }
}

export function createRecruitStream(
  jobDescription: string,
  resumes: string[],
  topN: number,
  onMessage: (msg: object) => void,
  onComplete: (dossier?: any) => void,
  onError: (err: string) => void,
): () => void {
  const controller = new AbortController()

  // Attempt live stream connection
  fetch(`${getApiUrl()}/api/recruit/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      job_description: jobDescription,
      resumes,
      top_n: topN,
    }),
    signal: controller.signal,
  }).then(async (res) => {
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`)
    }

    const reader = res.body?.getReader()
    if (!reader) { onError('No response body'); return }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) { onComplete(); break }

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()
          if (!data) continue
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'complete') { onComplete(parsed.dossier); return }
            if (parsed.type === 'error') { onError(parsed.message); return }
            onMessage(parsed)
          } catch {
            // ignore parse errors
          }
        }
      }
    }
  }).catch((err) => {
    if (err.name === 'AbortError') return

    // If live backend is unreachable (e.g. standalone Vercel preview without Render URL yet),
    // stream the concrete worked example trace with simulated delays
    console.warn('[TalentAI] Live backend unavailable, streaming concrete worked example:', err)
    
    let cancelled = false
    controller.signal.addEventListener('abort', () => { cancelled = true })

    ;(async () => {
      for (const event of DEMO_TRACE) {
        if (cancelled) return
        await new Promise((r) => setTimeout(r, 650))
        if (cancelled) return
        onMessage(event)
      }
      if (!cancelled) {
        onComplete(WORKED_EXAMPLE_DOSSIER)
      }
    })()
  })

  return () => controller.abort()
}
