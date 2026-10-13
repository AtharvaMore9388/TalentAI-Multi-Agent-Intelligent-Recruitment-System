// TalentAI — API Client

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function fetchSamples() {
  const res = await fetch(`${API_URL}/api/samples`)
  if (!res.ok) throw new Error('Failed to fetch samples')
  return res.json()
}

export async function fetchDemoTrace() {
  const res = await fetch(`${API_URL}/api/trace/demo`)
  if (!res.ok) throw new Error('Failed to fetch demo trace')
  return res.json()
}

export async function fetchHealth() {
  const res = await fetch(`${API_URL}/health`)
  if (!res.ok) throw new Error('API not reachable')
  return res.json()
}

export function createRecruitStream(
  jobDescription: string,
  resumes: string[],
  topN: number,
  onMessage: (msg: object) => void,
  onComplete: () => void,
  onError: (err: string) => void,
): () => void {
  const controller = new AbortController()

  fetch(`${API_URL}/api/recruit/stream`, {
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
      onError(`HTTP ${res.status}: ${res.statusText}`)
      return
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
            if (parsed.type === 'complete') { onComplete(); return }
            if (parsed.type === 'error') { onError(parsed.message); return }
            onMessage(parsed)
          } catch {
            // ignore parse errors
          }
        }
      }
    }
  }).catch((err) => {
    if (err.name !== 'AbortError') onError(String(err))
  })

  return () => controller.abort()
}
