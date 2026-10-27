'use client'

import { Brain, DollarSign, Award, Cpu, ShieldCheck, Sparkles } from 'lucide-react'

export function AdvantageSection() {
  const advantages = [
    {
      icon: <Brain size={28} color="#c084fc" />,
      title: 'Advanced Multi-Agent AI',
      subtitle: 'Autonomous Teamwork',
      desc: 'Five specialized agents collaborate, critique, and negotiate. From job analysis to independent evaluation, no single model makes an unchecked hiring decision.',
      badge: '5 CrewAI Agents',
    },
    {
      icon: <DollarSign size={28} color="#34d399" />,
      title: 'Significant Savings',
      subtitle: '60–70% Lower Cost',
      desc: 'Eliminate $15k–$20k per placement agency commissions. Scale inbound hiring pipelines on demand without inflating headhunter overheads.',
      badge: 'Predictable Retainers',
    },
    {
      icon: <Award size={28} color="#38bdf8" />,
      title: 'Exceptional Talent Fit',
      subtitle: 'Deterministic & Semantic RAG',
      desc: 'Sentence-transformer embeddings in ChromaDB paired with deterministic skill scoring guarantee exact technical and cultural alignment without hallucination.',
      badge: 'Zero Guesswork',
    },
  ]

  return (
    <section id="advantage" style={{ padding: '80px 0', position: 'relative' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: 52 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 14px',
              borderRadius: 999,
              background: 'rgba(147, 83, 252, 0.1)',
              border: '1px solid rgba(147, 83, 252, 0.3)',
              color: '#c084fc',
              fontSize: 12,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 16,
            }}
          >
            <Sparkles size={14} />
            CUTTING-EDGE TECHNOLOGY
          </div>

          <h2
            style={{
              fontSize: 'clamp(28px, 4vw, 44px)',
              fontWeight: 800,
              color: '#ffffff',
              letterSpacing: '-0.02em',
              marginBottom: 16,
            }}
          >
            The Talent <span className="highlight-pill">AI Advantage</span>
          </h2>

          <p
            style={{
              fontSize: 16,
              color: 'var(--text-secondary)',
              maxWidth: 640,
              margin: '0 auto',
            }}
          >
            Powered by modern agentic architectures: CrewAI, Groq LLM inference, ChromaDB vector stores,
            and an adaptive Orchestrator with conflict replanning.
          </p>
        </div>

        {/* 3 Grid Advantage Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 24,
          }}
        >
          {advantages.map((item, i) => (
            <div key={i} className="advantage-card">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: 16,
                }}
              >
                <div className="icon-glow-container">{item.icon}</div>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    padding: '4px 10px',
                    borderRadius: 999,
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-secondary)',
                  }}
                >
                  {item.badge}
                </span>
              </div>

              <div
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: 'var(--talent-purple)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  marginBottom: 4,
                }}
              >
                {item.subtitle}
              </div>

              <
                style={{
                  fontSize: 20,
                  fontWeight: 700,
                  color: '#ffffff',
                  marginBottom: 12,
                }}
              >
                {item.title}
              </h3>

              <p
                style={{
                  fontSize: 14,
                  color: 'var(--text-secondary)',
                  lineHeight: 1.65,
                }}
              >
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
