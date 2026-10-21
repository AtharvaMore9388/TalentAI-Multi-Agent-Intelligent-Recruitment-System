'use client'

import { Sparkles, ArrowRight, Play, Calendar, Zap, ShieldCheck, CheckCircle2, Bot } from 'lucide-react'

interface HeroSectionProps {
  onOpenBooking: () => void
  onRunDemoTrace: () => void
  onScrollToStudio: () => void
}

export function HeroSection({
  onOpenBooking,
  onRunDemoTrace,
  onScrollToStudio,
}: HeroSectionProps) {
  return (
    <section
      id="hero"
      style={{
        position: 'relative',
        paddingTop: '64px',
        paddingBottom: '72px',
        textAlign: 'center',
        overflow: 'hidden',
      }}
    >
      <div className="container" style={{ position: 'relative', zIndex: 2 }}>
        {/* Top Floating Badge */}
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '7px 18px',
            borderRadius: 999,
            background: 'rgba(147, 83, 252, 0.1)',
            border: '1px solid rgba(147, 83, 252, 0.3)',
            color: '#c084fc',
            fontSize: 13,
            fontWeight: 600,
            marginBottom: 28,
            backdropFilter: 'blur(10px)',
            boxShadow: '0 0 20px rgba(147, 83, 252, 0.15)',
          }}
        >
          <Sparkles size={15} color="#c084fc" />
          <span>TalentAI: Multi-Agent Intelligent Recruitment and Talent Matching System</span>
        </div>

        {/* Dynamic Main Headline */}
        <h1
          style={{
            fontSize: 'clamp(34px, 5.2vw, 64px)',
            fontWeight: 900,
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            maxWidth: 980,
            margin: '0 auto 24px',
            color: '#ffffff',
          }}
        >
          Revolutionising Recruitment with{' '}
          <span className="highlight-pill">Multi-Agent AI</span>
        </h1>

        {/* Subtitle with official description */}
        <p
          style={{
            fontSize: 'clamp(15px, 1.6vw, 18px)',
            color: 'var(--text-secondary)',
            maxWidth: 820,
            margin: '0 auto 28px',
            lineHeight: 1.65,
          }}
        >
          A multi-agent AI recruitment platform connecting candidates and companies using 6 specialized AI agents, Retrieval-Augmented Generation (RAG), semantic search, and an Orchestrator with dynamic conflict replanning.
        </p>

        {/* 6 Named Agents Pills */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'center',
            gap: 8,
            maxWidth: 880,
            margin: '0 auto 36px',
          }}
        >
          {[
            { name: '1. Orchestrator Agent', tag: 'Coordinator & Replanning', color: '#c084fc' },
            { name: '2. Job Analysis Agent', tag: 'Mandatory / Preferred', color: '#60a5fa' },
            { name: '3. Resume Analysis Agent', tag: 'ChromaDB Ingestion', color: '#a78bfa' },
            { name: '4. Matching & Ranking Agent', tag: 'RAG Semantic Scoring', color: '#38bdf8' },
            { name: '5. Candidate Evaluation Agent', tag: 'Critic Disagreement', color: '#f87171' },
            { name: '6. Recruitment Communication Agent', tag: 'Outreach & Invites', color: '#34d399' },
          ].map((ag, idx) => (
            <div
              key={idx}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
                padding: '4px 10px',
                borderRadius: 999,
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--border-subtle)',
                fontSize: 11.5,
                color: 'var(--text-secondary)',
              }}
            >
              <span style={{ fontWeight: 700, color: ag.color }}>{ag.name}</span>
              <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>({ag.tag})</span>
            </div>
          ))}
        </div>

        {/* CTA Buttons */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 16,
            flexWrap: 'wrap',
            marginBottom: 56,
          }}
        >
          <button
            className="btn btn-talent"
            onClick={onScrollToStudio}
            style={{
              fontSize: 15,
              padding: '14px 28px',
              gap: 10,
            }}
          >
            <Zap size={18} />
            LAUNCH AI STUDIO
            <ArrowRight size={16} />
          </button>

          <button
            className="btn btn-outline"
            onClick={onRunDemoTrace}
            style={{
              fontSize: 15,
              padding: '14px 26px',
              gap: 10,
            }}
          >
            <Play size={16} />
            RUN DEMO TRACE
          </button>

          <button
            className="btn btn-ghost"
            onClick={onOpenBooking}
            style={{
              fontSize: 14,
              padding: '14px 22px',
              gap: 8,
              color: '#c084fc',
            }}
          >
            <Calendar size={16} />
            Book A Strategy Call
          </button>
        </div>

        {/* Key Performance Indicators Bar */}
        <div
          style={{
            maxWidth: 1040,
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 16,
            padding: '20px',
            background: 'rgba(15, 20, 42, 0.55)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-xl)',
            backdropFilter: 'blur(16px)',
          }}
        >
          <div style={{ textAlign: 'center', padding: '12px' }}>
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                color: 'var(--talent-purple)',
                letterSpacing: '-0.02em',
              }}
            >
              60–70%
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              Lower Hiring Cost vs Agencies
            </div>
          </div>

          <div
            style={{
              textAlign: 'center',
              padding: '12px',
              borderLeft: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                color: 'var(--talent-cyan)',
                letterSpacing: '-0.02em',
              }}
            >
              100+
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              Semantic Vectors & Criteria Points
            </div>
          </div>

          <div
            style={{
              textAlign: 'center',
              padding: '12px',
              borderLeft: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                color: 'var(--talent-emerald)',
                letterSpacing: '-0.02em',
              }}
            >
              5 Agents
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              Autonomous Collaborative Pipeline
            </div>
          </div>

          <div
            style={{
              textAlign: 'center',
              padding: '12px',
              borderLeft: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            <div
              style={{
                fontSize: 28,
                fontWeight: 900,
                color: '#f59e0b',
                letterSpacing: '-0.02em',
              }}
            >
              Zero Bias
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
              Deterministic & RAG Verification
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
