'use client'

import { Search, Mail, CheckCircle2, BarChart3, ArrowRight, Sparkles } from 'lucide-react'

export function PartnerModelSection() {
  const steps = [
    {
      num: '1',
      title: 'Find',
      label: 'AI Semantic Sourcing',
      desc: 'ResumeAnalysisAgent and JobAnalysisAgent parse unstructured texts into standardized skill schemas and index them into high-dimensional vector spaces.',
      icon: <Search size={22} color="#38bdf8" />,
      color: '#38bdf8',
    },
    {
      num: '2',
      title: 'Engage',
      label: 'Personalized Outreach',
      desc: 'CommunicationAgent crafts personalized interview invites or candidate feedback tailored to specific strengths, ensuring high response rates.',
      icon: <Mail size={22} color="#c084fc" />,
      color: '#c084fc',
    },
    {
      num: '3',
      title: 'Qualify',
      label: 'Multi-Agent Verification',
      desc: 'MatchingAgent scores candidates using hybrid RAG + skill matching. EvaluationAgent independently audits the shortlist and rejects poor fits.',
      icon: <CheckCircle2 size={22} color="#34d399" />,
      color: '#34d399',
    },
    {
      num: '4',
      title: 'Track',
      label: 'Real-Time Intelligence',
      desc: 'Orchestrator tracks state telemetry, live agent execution trace, replanning loops, and presents a complete candidate dossier in seconds.',
      icon: <BarChart3 size={22} color="#fbbf24" />,
      color: '#fbbf24',
    },
  ]

  return (
    <section id="roadmap" style={{ padding: '80px 0', position: 'relative' }}>
      <div className="container">
        {/* Section Header */}
        <div style={{ textAlign: 'center', marginBottom: 54 }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 14px',
              borderRadius: 999,
              background: 'rgba(6, 182, 212, 0.1)',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              color: '#38bdf8',
              fontSize: 12,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 16,
            }}
          >
            <Sparkles size={14} />
            HOW IT WORKS
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
            Our <span className="highlight-pill">AI Talent</span> Partner Model
          </h2>

          <p
            style={{
              fontSize: 16,
              color: 'var(--text-secondary)',
              maxWidth: 640,
              margin: '0 auto',
            }}
          >
            A 4-step autonomous pipeline that takes you from raw job descriptions to verified,
            interview-ready candidate shortlists.
          </p>
        </div>

        {/* 4 Steps Horizontal Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
            gap: 20,
          }}
        >
          {steps.map((step, idx) => (
            <div key={idx} className="step-card">
              <div className="step-num">{step.num}</div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginTop: 10,
                  marginBottom: 16,
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 12,
                    background: `${step.color}15`,
                    border: `1px solid ${step.color}35`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  {step.icon}
                </div>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: step.color,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                  }}
                >
                  {step.label}
                </span>
              </div>

              <h3
                style={{
                  fontSize: 22,
                  fontWeight: 800,
                  color: '#ffffff',
                  marginBottom: 10,
                }}
              >
                {step.title}
              </h3>

              <p
                style={{
                  fontSize: 13.5,
                  color: 'var(--text-secondary)',
                  lineHeight: 1.6,
                }}
              >
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
