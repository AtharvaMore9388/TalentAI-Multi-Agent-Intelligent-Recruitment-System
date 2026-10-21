'use client'

import { Bot, Heart, Sparkles, ExternalLink } from 'lucide-react'

export function Footer() {
  const scrollTo = (id: string) => {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <footer
      style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(5, 7, 18, 0.95)',
        padding: '60px 0 32px',
        color: 'var(--text-secondary)',
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 40,
            marginBottom: 48,
          }}
        >
          {/* Brand Col */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 10,
                  background: 'linear-gradient(135deg, #9353fc, #6366f1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Bot size={20} color="#fff" />
              </div>
              <span style={{ fontSize: 18, fontWeight: 800, color: '#fff' }}>
                Talent<span style={{ color: 'var(--talent-purple)' }}>AI</span> Agency
              </span>
            </div>

            <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, maxWidth: 300 }}>
              AI-powered recruitment solutions for inbound talent acquisition. Deploying 5 autonomous
              agents that challenge, evaluate, and dynamically replan candidate matching.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
              Platform Navigation
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13 }}>
              <li>
                <button
                  onClick={() => scrollTo('advantage')}
                  style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0 }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#fff')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
                >
                  The Talent AI Advantage
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollTo('compare')}
                  style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0 }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#fff')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
                >
                  The Old Way vs The New Way
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollTo('roadmap')}
                  style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0 }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#fff')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
                >
                  AI Talent Partner Model
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollTo('studio')}
                  style={{ background: 'none', border: 'none', color: '#c084fc', cursor: 'pointer', padding: 0, fontWeight: 600 }}
                >
                  Live Multi-Agent Studio
                </button>
              </li>
              <li>
                <button
                  onClick={() => scrollTo('tiers')}
                  style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', padding: 0 }}
                  onMouseEnter={(e) => (e.currentTarget.style.color = '#fff')}
                  onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
                >
                  Service Offerings
                </button>
              </li>
            </ul>
          </div>

          {/* Architecture Stack */}
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
              Technology Architecture
            </div>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12.5, color: 'var(--text-muted)' }}>
              <li>🤖 CrewAI Multi-Agent Coordination</li>
              <li>⚡ Groq LLaMA 3.3 70B Fast Inference</li>
              <li>🔍 ChromaDB Vector Store & Sentence-Transformers</li>
              <li>⚖️ Independent Evaluation Agent & Conflict Resolution</li>
              <li>🌐 FastAPI Backend & SSE Live Streaming</li>
              <li>💻 Next.js 14 App Router & TypeScript</li>
            </ul>
          </div>

          {/* Reference Attribution */}
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>
              Design Benchmark
            </div>
            <p style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 12 }}>
              UI aesthetics, structure, and marketing layout refined with inspiration from:
            </p>
            <a
              href="https://talent-ai.agency/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '6px 14px',
                borderRadius: 999,
                background: 'rgba(147, 83, 252, 0.12)',
                border: '1px solid rgba(147, 83, 252, 0.3)',
                color: '#c084fc',
                fontSize: 12,
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              talent-ai.agency
              <ExternalLink size={12} />
            </a>
          </div>
        </div>

        {/* Bottom Bar */}
        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12,
            fontSize: 12,
            color: 'var(--text-dim)',
          }}
        >
          <div>
            © {new Date().getFullYear()} TalentAI — Multi-Agent Intelligent Recruitment and Talent Matching System.
          </div>
          <div>
            CA3 Project · Agentic AI Architecture
          </div>
        </div>
      </div>
    </footer>
  )
}
