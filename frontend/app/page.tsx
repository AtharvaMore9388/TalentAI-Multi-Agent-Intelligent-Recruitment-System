'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { AgentMessage, SamplesResponse, AGENT_CONFIG, ROLE_LABELS } from '@/lib/types'
import { fetchSamples, fetchHealth, createRecruitStream, fetchDemoTrace } from '@/lib/api'

// ─── Agent Pipeline Visualization ────────────────────────────────────────────

const PIPELINE_AGENTS = [
  { id: 'JobAnalysisAgent', label: 'Job Analysis', icon: '📋', desc: 'Extracts mandatory & preferred requirements' },
  { id: 'ResumeAnalysisAgent', label: 'Resume Analysis', icon: '📄', desc: 'Parses resumes into structured data' },
  { id: 'MatchingAgent', label: 'Matching & Ranking', icon: '🔍', desc: 'RAG semantic search + scoring' },
  { id: 'EvaluationAgent', label: 'Evaluation', icon: '⚖️', desc: 'Independent verification + conflict' },
  { id: 'CommunicationAgent', label: 'Communication', icon: '📧', desc: 'Interview invites & rejections' },
]

function AgentPipelineNode({
  agent,
  status,
  messageCount,
}: {
  agent: typeof PIPELINE_AGENTS[0]
  status: 'idle' | 'active' | 'complete' | 'error'
  messageCount: number
}) {
  const cfg = AGENT_CONFIG[agent.id] || AGENT_CONFIG.System
  const dotClass = `node-dot ${status}`

  return (
    <div className={`pipeline-node ${status}`} style={{ transition: 'all 0.3s ease' }}>
      <div className={dotClass} />
      <span style={{ fontSize: 20 }}>{agent.icon}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 13, color: cfg.color }}>{agent.label}</div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{agent.desc}</div>
      </div>
      {messageCount > 0 && (
        <span style={{
          background: `${cfg.color}22`,
          color: cfg.color,
          border: `1px solid ${cfg.color}44`,
          borderRadius: 999,
          fontSize: 11,
          fontWeight: 700,
          padding: '2px 8px',
        }}>
          {messageCount}
        </span>
      )}
    </div>
  )
}

// ─── Message Log Entry ────────────────────────────────────────────────────────

function MessageEntry({ msg, index }: { msg: AgentMessage; index: number }) {
  const cfg = AGENT_CONFIG[msg.agent] || AGENT_CONFIG.System
  const roleLabel = ROLE_LABELS[msg.role] || msg.role
  const badgeClass = `badge badge-${msg.role}`

  return (
    <div
      className="animate-slide-in"
      style={{
        display: 'flex',
        gap: 12,
        padding: '14px 16px',
        borderRadius: 'var(--radius-md)',
        background: msg.role === 'conflict'
          ? 'rgba(239,68,68,0.05)'
          : msg.role === 'replan'
          ? 'rgba(245,158,11,0.05)'
          : msg.role === 'result'
          ? 'rgba(16,185,129,0.05)'
          : 'var(--bg-card)',
        border: `1px solid ${
          msg.role === 'conflict' ? 'rgba(239,68,68,0.2)'
          : msg.role === 'replan' ? 'rgba(245,158,11,0.2)'
          : msg.role === 'result' ? 'rgba(16,185,129,0.2)'
          : 'var(--border-subtle)'
        }`,
        animationDelay: `${index * 20}ms`,
      }}
    >
      {/* Agent icon */}
      <div style={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        background: `${cfg.color}1a`,
        border: `1px solid ${cfg.color}33`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 16,
        flexShrink: 0,
      }}>
        {cfg.icon}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
          <span style={{ fontWeight: 700, fontSize: 12, color: cfg.color }}>{cfg.label || msg.agent}</span>
          <span className={badgeClass}>{roleLabel}</span>
          {msg.timestamp && (
            <span style={{ fontSize: 10, color: 'var(--text-muted)', marginLeft: 'auto' }}>
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          {msg.content}
        </p>
      </div>
    </div>
  )
}

// ─── Score Ring Component ─────────────────────────────────────────────────────

function ScoreRing({ score }: { score: number }) {
  const r = 28
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  const color = score >= 70 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'

  return (
    <div style={{ position: 'relative', width: 72, height: 72 }}>
      <svg width="72" height="72" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="36" cy="36" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4" />
        <circle
          cx="36" cy="36" r={r} fill="none"
          stroke={color} strokeWidth="4"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexDirection: 'column',
      }}>
        <span style={{ fontSize: 14, fontWeight: 800, color }}>{Math.round(score)}</span>
        <span style={{ fontSize: 8, color: 'var(--text-muted)' }}>/ 100</span>
      </div>
    </div>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function Home() {
  const [jobDescription, setJobDescription] = useState('')
  const [resumeTexts, setResumeTexts] = useState<string[]>(['', ''])
  const [topN, setTopN] = useState(3)
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [samples, setSamples] = useState<SamplesResponse | null>(null)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [activeTab, setActiveTab] = useState<'input' | 'trace' | 'results'>('input')
  const [agentCounts, setAgentCounts] = useState<Record<string, number>>({})
  const [agentStatus, setAgentStatus] = useState<Record<string, 'idle' | 'active' | 'complete' | 'error'>>({})
  const [replanCount, setReplanCount] = useState(0)
  const [stopStream, setStopStream] = useState<(() => void) | null>(null)
  const logEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll log
  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // Check API health
  useEffect(() => {
    fetchHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false))
  }, [])

  // Load samples
  useEffect(() => {
    fetchSamples()
      .then(setSamples)
      .catch(console.error)
  }, [])

  const loadSampleJob = (idx: number) => {
    if (samples?.jobs[idx]) {
      setJobDescription(samples.jobs[idx].raw_jd)
    }
  }

  const loadSampleResumes = () => {
    if (samples?.resumes) {
      setResumeTexts(samples.resumes.map(r => r.raw_resume))
    }
  }

  const addResume = () => setResumeTexts(prev => [...prev, ''])
  const removeResume = (i: number) => setResumeTexts(prev => prev.filter((_, idx) => idx !== i))
  const updateResume = (i: number, val: string) => {
    setResumeTexts(prev => { const n = [...prev]; n[i] = val; return n })
  }

  const handleMessage = useCallback((raw: object) => {
    const msg = raw as AgentMessage
    setMessages(prev => [...prev, msg])

    // Update agent status
    setAgentCounts(prev => ({
      ...prev,
      [msg.agent]: (prev[msg.agent] || 0) + 1,
    }))

    setAgentStatus(prev => {
      const next = { ...prev }
      // Mark the current agent as active
      PIPELINE_AGENTS.forEach(a => {
        if (a.id === msg.agent) {
          next[a.id] = 'active'
        }
      })
      return next
    })

    if (msg.role === 'replan') {
      setReplanCount(c => c + 1)
    }
  }, [])

  const handleComplete = useCallback(() => {
    setIsRunning(false)
    setIsComplete(true)
    setAgentStatus(prev => {
      const next: Record<string, 'idle' | 'active' | 'complete' | 'error'> = {}
      PIPELINE_AGENTS.forEach(a => {
        next[a.id] = (prev[a.id] === 'active' || prev[a.id] === 'complete') ? 'complete' : prev[a.id] || 'idle'
      })
      return next
    })
    setActiveTab('trace')
  }, [])

  const handleError = useCallback((err: string) => {
    setError(err)
    setIsRunning(false)
  }, [])

  const loadDemoTrace = async () => {
    try {
      const trace = await fetchDemoTrace()
      setMessages(trace)
      const counts: Record<string, number> = {}
      const statuses: Record<string, 'idle' | 'active' | 'complete' | 'error'> = {}
      trace.forEach((m: AgentMessage) => {
        counts[m.agent] = (counts[m.agent] || 0) + 1
        statuses[m.agent] = 'complete'
      })
      setAgentCounts(counts)
      setAgentStatus(statuses)
      setReplanCount(trace.filter((m: AgentMessage) => m.role === 'replan').length)
      setIsComplete(true)
      setActiveTab('trace')
    } catch {
      setError('Failed to load demo trace')
    }
  }

  const runPipeline = () => {
    const validResumes = resumeTexts.filter(r => r.trim().length > 50)
    if (!jobDescription.trim()) { setError('Please enter a job description'); return }
    if (validResumes.length === 0) { setError('Please enter at least one resume'); return }

    setMessages([])
    setAgentCounts({})
    setAgentStatus({})
    setReplanCount(0)
    setError(null)
    setIsRunning(true)
    setIsComplete(false)
    setActiveTab('trace')

    const stop = createRecruitStream(
      jobDescription,
      validResumes,
      topN,
      handleMessage,
      handleComplete,
      handleError,
    )
    setStopStream(() => stop)
  }

  const stopPipeline = () => {
    stopStream?.()
    setIsRunning(false)
    setError('Pipeline stopped by user')
  }

  const reset = () => {
    setMessages([])
    setAgentCounts({})
    setAgentStatus({})
    setReplanCount(0)
    setError(null)
    setIsRunning(false)
    setIsComplete(false)
    setActiveTab('input')
  }

  // Extract shortlisted candidates from messages
  const shortlistedFromMessages = messages
    .filter(m => m.agent === 'MatchingAgent')
    .slice(-1)

  const conflictMessages = messages.filter(m => m.role === 'conflict')
  const replanMessages = messages.filter(m => m.role === 'replan')
  const commsMessages = messages.filter(m => m.agent === 'CommunicationAgent')

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* ── HEADER ── */}
      <header style={{
        borderBottom: '1px solid var(--border-subtle)',
        backdropFilter: 'blur(20px)',
        background: 'var(--bg-glass)',
        position: 'sticky', top: 0, zIndex: 100,
      }}>
        <div className="container" style={{
          display: 'flex', alignItems: 'center',
          justifyContent: 'space-between', height: 64,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 36, height: 36,
              background: 'var(--gradient-primary)',
              borderRadius: 10,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18,
              boxShadow: '0 4px 12px rgba(99,102,241,0.3)',
            }}>🤖</div>
            <div>
              <h1 style={{ fontSize: 18, fontWeight: 800, letterSpacing: -0.5 }}>
                <span className="shimmer-text">TalentAI</span>
              </h1>
              <p style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: -2 }}>
                Multi-Agent Recruitment System
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {/* API Status */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
              <div style={{
                width: 7, height: 7, borderRadius: '50%',
                background: apiOnline === null ? 'var(--text-muted)'
                  : apiOnline ? 'var(--accent-success)' : 'var(--accent-danger)',
                boxShadow: apiOnline ? '0 0 8px rgba(16,185,129,0.5)' : 'none',
              }} />
              <span style={{ color: 'var(--text-muted)' }}>
                {apiOnline === null ? 'Connecting...' : apiOnline ? 'API Online' : 'API Offline'}
              </span>
            </div>

            <button className="btn btn-ghost" onClick={loadDemoTrace} style={{ fontSize: 12 }}>
              ▶ Demo Trace
            </button>

            {(isRunning || isComplete) && (
              <button className="btn btn-ghost" onClick={reset} style={{ fontSize: 12 }}>
                ↺ Reset
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="container" style={{ flex: 1, paddingTop: 32, paddingBottom: 48 }}>

        {/* ── HERO ── */}
        <div className="animate-fade-in-up" style={{ textAlign: 'center', marginBottom: 48 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: 999, padding: '6px 16px', marginBottom: 20, fontSize: 12,
            color: '#a5b4fc',
          }}>
            <span>✨</span>
            <span>5 Specialized AI Agents · RAG Semantic Search · Dynamic Replanning</span>
          </div>

          <h1 style={{ fontSize: 'clamp(32px, 5vw, 56px)', fontWeight: 900, lineHeight: 1.1, marginBottom: 16 }}>
            <span className="shimmer-text">Intelligent Recruitment</span>
            <br />
            <span style={{ color: 'var(--text-primary)' }}>Powered by Multi-Agent AI</span>
          </h1>

          <p style={{ fontSize: 16, color: 'var(--text-secondary)', maxWidth: 600, margin: '0 auto' }}>
            Upload job descriptions and resumes. Watch 5 specialized agents collaborate,
            challenge each other, and intelligently match candidates in real-time.
          </p>
        </div>

        {/* ── PIPELINE VISUALIZATION ── */}
        <div className="animate-fade-in-up glass-card" style={{ padding: 24, marginBottom: 32, animationDelay: '0.1s' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <span style={{ fontSize: 20 }}>🧠</span>
            <h2 style={{ fontSize: 15, fontWeight: 700 }}>Orchestrator-Worker Pipeline</h2>
            {isRunning && (
              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8 }}>
                <div className="spinner" />
                <span style={{ fontSize: 12, color: 'var(--accent-primary)' }}>Pipeline running...</span>
              </div>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 10 }}>
            {PIPELINE_AGENTS.map(agent => (
              <AgentPipelineNode
                key={agent.id}
                agent={agent}
                status={agentStatus[agent.id] || 'idle'}
                messageCount={agentCounts[agent.id] || 0}
              />
            ))}
          </div>

          {/* Stats row */}
          {(isRunning || isComplete) && (
            <div style={{
              marginTop: 20,
              padding: '12px 16px',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-md)',
              display: 'flex', gap: 32, flexWrap: 'wrap',
            }}>
              <Stat label="Messages" value={messages.length} color="var(--accent-primary)" />
              <Stat label="Conflicts" value={conflictMessages.length} color="var(--accent-danger)" />
              <Stat label="Replan Rounds" value={replanCount} color="var(--accent-warning)" />
              <Stat label="Status" value={isComplete ? '✅ Complete' : '⏳ Running'} color="var(--accent-success)" />
            </div>
          )}
        </div>

        {/* ── MAIN CONTENT TABS ── */}
        <div style={{ display: 'flex', gap: 0, marginBottom: 24, borderBottom: '1px solid var(--border-subtle)' }}>
          {[
            { id: 'input', label: '📝 Input', desc: 'Job & Resumes' },
            { id: 'trace', label: '🔄 Execution Trace', desc: `${messages.length} events` },
            { id: 'results', label: '🏆 Results', desc: commsMessages.length > 0 ? 'Available' : 'Pending' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              style={{
                padding: '12px 20px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab.id ? '2px solid var(--accent-primary)' : '2px solid transparent',
                color: activeTab === tab.id ? 'var(--accent-primary)' : 'var(--text-muted)',
                fontWeight: activeTab === tab.id ? 700 : 400,
                cursor: 'pointer',
                fontSize: 13,
                transition: 'all 0.2s ease',
                display: 'flex', flexDirection: 'column', alignItems: 'flex-start',
                gap: 2,
              }}
            >
              <span>{tab.label}</span>
              <span style={{ fontSize: 10, opacity: 0.7 }}>{tab.desc}</span>
            </button>
          ))}
        </div>

        {/* ── INPUT TAB ── */}
        {activeTab === 'input' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, alignItems: 'start' }}>

            {/* Job Description */}
            <div className="glass-card" style={{ padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <h3 style={{ fontSize: 14, fontWeight: 700, color: '#22d3ee' }}>📋 Job Description</h3>
                <div style={{ display: 'flex', gap: 8 }}>
                  {samples?.jobs.map((j, i) => (
                    <button
                      key={i}
                      className="btn btn-ghost"
                      onClick={() => loadSampleJob(i)}
                      style={{ fontSize: 11, padding: '4px 10px' }}
                    >
                      Sample {i + 1}
                    </button>
                  ))}
                </div>
              </div>
              <textarea
                id="job-description-input"
                className="input-field"
                rows={14}
                placeholder="Paste job description here...&#10;&#10;e.g. We are looking for a Senior Full Stack Engineer with React, Node.js, TypeScript and AWS experience..."
                value={jobDescription}
                onChange={e => setJobDescription(e.target.value)}
              />
              <div style={{ marginTop: 8, display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)' }}>
                <span>{jobDescription.length} chars</span>
                <span>Min. 100 chars recommended</span>
              </div>
            </div>

            {/* Resumes */}
            <div>
              <div className="glass-card" style={{ padding: 24, marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                  <h3 style={{ fontSize: 14, fontWeight: 700, color: '#a78bfa' }}>
                    📄 Resumes ({resumeTexts.filter(r => r.trim().length > 50).length} valid)
                  </h3>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn btn-ghost" onClick={loadSampleResumes} style={{ fontSize: 11, padding: '4px 10px' }}>
                      Load Samples
                    </button>
                    <button className="btn btn-ghost" onClick={addResume} style={{ fontSize: 11, padding: '4px 10px' }}>
                      + Add
                    </button>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 12, maxHeight: 400, overflowY: 'auto' }}>
                  {resumeTexts.map((text, i) => (
                    <div key={i} style={{ position: 'relative' }}>
                      <textarea
                        id={`resume-input-${i}`}
                        className="input-field"
                        rows={5}
                        placeholder={`Candidate ${i + 1} resume text...`}
                        value={text}
                        onChange={e => updateResume(i, e.target.value)}
                      />
                      <button
                        onClick={() => removeResume(i)}
                        style={{
                          position: 'absolute', top: 8, right: 8,
                          background: 'rgba(239,68,68,0.1)',
                          border: '1px solid rgba(239,68,68,0.2)',
                          color: '#f87171', borderRadius: 6,
                          padding: '2px 8px', cursor: 'pointer', fontSize: 11,
                        }}
                      >✕</button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Settings */}
              <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
                <label style={{ fontSize: 13, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span>Top N candidates to shortlist:</span>
                  <select
                    id="top-n-select"
                    value={topN}
                    onChange={e => setTopN(Number(e.target.value))}
                    style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-subtle)',
                      color: 'var(--text-primary)',
                      borderRadius: 8, padding: '6px 12px',
                      fontFamily: 'var(--font-sans)', fontSize: 13,
                    }}
                  >
                    {[2,3,4,5,6].map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                </label>
              </div>

              {/* Error */}
              {error && (
                <div style={{
                  padding: 12, marginBottom: 16,
                  background: 'rgba(239,68,68,0.1)',
                  border: '1px solid rgba(239,68,68,0.2)',
                  borderRadius: 'var(--radius-md)',
                  color: '#fca5a5', fontSize: 13,
                }}>{error}</div>
              )}

              {/* Run Button */}
              <button
                id="run-pipeline-btn"
                className="btn btn-primary"
                onClick={isRunning ? stopPipeline : runPipeline}
                disabled={apiOnline === false}
                style={{ width: '100%', justifyContent: 'center', fontSize: 15, padding: '14px 24px' }}
              >
                {isRunning ? (
                  <><div className="spinner" /> Stop Pipeline</>
                ) : (
                  <><span>🚀</span> Run Recruitment Pipeline</>
                )}
              </button>

              {apiOnline === false && (
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8, textAlign: 'center' }}>
                  Backend API is offline. Start the FastAPI server at localhost:8000
                </p>
              )}
            </div>
          </div>
        )}

        {/* ── TRACE TAB ── */}
        {activeTab === 'trace' && (
          <div>
            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
                <p>No agent messages yet. Run the pipeline or load the demo trace.</p>
              </div>
            ) : (
              <div>
                {/* Filter bar */}
                <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 12, color: 'var(--text-muted)', alignSelf: 'center' }}>
                    {messages.length} messages
                  </span>
                  {['conflict', 'replan', 'result'].map(role => {
                    const count = messages.filter(m => m.role === role).length
                    return count > 0 ? (
                      <span key={role} className={`badge badge-${role}`}>
                        {ROLE_LABELS[role]}: {count}
                      </span>
                    ) : null
                  })}
                </div>

                {/* Messages */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {messages.map((msg, i) => (
                    <MessageEntry key={i} msg={msg} index={i} />
                  ))}
                </div>

                {isRunning && (
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '16px', marginTop: 8,
                    background: 'rgba(99,102,241,0.05)',
                    border: '1px solid rgba(99,102,241,0.2)',
                    borderRadius: 'var(--radius-md)',
                  }}>
                    <div className="spinner" />
                    <span style={{ fontSize: 13, color: 'var(--accent-primary)' }}>
                      Agents are working...
                    </span>
                  </div>
                )}
                <div ref={logEndRef} />
              </div>
            )}
          </div>
        )}

        {/* ── RESULTS TAB ── */}
        {activeTab === 'results' && (
          <div>
            {!isComplete && messages.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>🏆</div>
                <p>Results will appear here after the pipeline completes.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

                {/* Summary Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
                  <SummaryCard icon="📊" label="Total Agents" value="5" color="var(--accent-primary)" />
                  <SummaryCard icon="💬" label="Agent Messages" value={String(messages.length)} color="var(--accent-secondary)" />
                  <SummaryCard icon="⚔️" label="Conflicts" value={String(conflictMessages.length)} color="var(--accent-danger)" />
                  <SummaryCard icon="🔄" label="Replan Rounds" value={String(replanCount)} color="var(--accent-warning)" />
                  <SummaryCard icon="📧" label="Communications" value={String(commsMessages.length)} color="var(--accent-success)" />
                </div>

                {/* Inter-agent conflict timeline */}
                {conflictMessages.length > 0 && (
                  <div className="glass-card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, color: '#f87171' }}>
                      ⚔️ Agent Conflicts & Replanning
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {[...conflictMessages, ...replanMessages]
                        .sort((a, b) => (a.timestamp || '').localeCompare(b.timestamp || ''))
                        .map((msg, i) => (
                          <MessageEntry key={i} msg={msg} index={i} />
                        ))
                      }
                    </div>
                  </div>
                )}

                {/* Communications */}
                {commsMessages.length > 0 && (
                  <div className="glass-card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, color: '#34d399' }}>
                      📧 Recruitment Communications
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {commsMessages.map((msg, i) => (
                        <MessageEntry key={i} msg={msg} index={i} />
                      ))}
                    </div>
                  </div>
                )}

                {/* All result messages */}
                {messages.filter(m => m.role === 'result').length > 0 && (
                  <div className="glass-card" style={{ padding: 24 }}>
                    <h3 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16, color: '#34d399' }}>
                      ✅ Final Results
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {messages.filter(m => m.role === 'result').map((msg, i) => (
                        <MessageEntry key={i} msg={msg} index={i} />
                      ))}
                    </div>
                  </div>
                )}

              </div>
            )}
          </div>
        )}

      </main>

      {/* ── FOOTER ── */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '20px 0',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: 12,
      }}>
        <div className="container">
          <p>TalentAI — Multi-Agent Intelligent Recruitment System · Built with CrewAI, Groq, ChromaDB, FastAPI & Next.js</p>
          <p style={{ marginTop: 4 }}>CA3 Project · Agentic AI Course</p>
        </div>
      </footer>

    </div>
  )
}

// ─── Small helper components ──────────────────────────────────────────────────

function Stat({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div>
      <div style={{ fontSize: 18, fontWeight: 800, color }}>{value}</div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</div>
    </div>
  )
}

function SummaryCard({ icon, label, value, color }: { icon: string; label: string; value: string; color: string }) {
  return (
    <div className="glass-card" style={{ padding: 20, textAlign: 'center' }}>
      <div style={{ fontSize: 28, marginBottom: 8 }}>{icon}</div>
      <div style={{ fontSize: 28, fontWeight: 900, color }}>{value}</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>{label}</div>
    </div>
  )
}
