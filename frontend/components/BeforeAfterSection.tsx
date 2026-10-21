'use client'

import { AlertTriangle, CheckCircle2, ArrowRight, XCircle, Zap, TrendingDown, Clock, ShieldAlert, Sparkles } from 'lucide-react'

export function BeforeAfterSection() {
  return (
    <section id="compare" style={{ padding: '80px 0', position: 'relative' }}>
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
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              color: '#f87171',
              fontSize: 12,
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: 16,
            }}
          >
            <ShieldAlert size={14} />
            SAY GOODBYE TO HIGH PLACEMENT FEES!
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
            From Traditional Hiring Struggles to{' '}
            <span className="highlight-pill">AI-Powered</span> Success
          </h2>

          <p
            style={{
              fontSize: 16,
              color: 'var(--text-secondary)',
              maxWidth: 640,
              margin: '0 auto',
            }}
          >
            Traditional staffing agencies charge 15-20% per placement while locking you into opaque,
            slow pipelines. TalentAI transforms talent acquisition into an autonomous high-velocity engine.
          </p>
        </div>

        {/* Comparison Cards Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 28,
            alignItems: 'stretch',
          }}
        >
          {/* THE OLD WAY (Before) */}
          <div className="compare-card-old">
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 20,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: 10,
                    background: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid rgba(239, 68, 68, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <AlertTriangle size={20} color="#f87171" />
                </div>
                <div>
                  <div
                    style={{
                      fontSize: 11,
                      fontWeight: 800,
                      color: '#f87171',
                      letterSpacing: '0.08em',
                      textTransform: 'uppercase',
                    }}
                  >
                    The Old Way
                  </div>
                  <h3 style={{ fontSize: 18, fontWeight: 700, color: '#ffffff' }}>
                    Traditional Agency Model
                  </h3>
                </div>
              </div>
              <span
                style={{
                  background: 'rgba(239, 68, 68, 0.12)',
                  color: '#fca5a5',
                  padding: '4px 10px',
                  borderRadius: 999,
                  fontSize: 11,
                  fontWeight: 700,
                }}
              >
                BEFORE
              </span>
            </div>

            <div
              style={{
                fontSize: 22,
                fontWeight: 900,
                color: '#f87171',
                padding: '12px 16px',
                background: 'rgba(239, 68, 68, 0.08)',
                borderRadius: 'var(--radius-md)',
                marginBottom: 24,
                border: '1px solid rgba(239, 68, 68, 0.15)',
              }}
            >
              $15,000 – $20,000+
              <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-muted)', marginLeft: 8 }}>
                per placement
              </span>
            </div>

            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 16 }}>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <XCircle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    Overspending on traditional agency commissions
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Paying 15% to 20% on the first year candidate salary every single hire.
                  </div>
                </div>
              </li>

              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <Clock size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    Slow, inefficient hiring processes
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Weeks spent waiting for recruiters to manually skim resumes.
                  </div>
                </div>
              </li>

              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <XCircle size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    Limited data on only 5–10 candidates
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Zero transparency on why other applicants were filtered out.
                  </div>
                </div>
              </li>

              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <TrendingDown size={18} color="#ef4444" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    No owned candidate pipeline
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Agency keeps all candidate data and relationship equity.
                  </div>
                </div>
              </li>
            </ul>
          </div>

          {/* THE NEW WAY (After) */}
          <div className="compare-card-new">
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 20,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div
                  style={{
                    width: 38,
                    height: 38,
                    borderRadius: 10,
                    background: 'rgba(147, 83, 252, 0.2)',
                    border: '1px solid rgba(147, 83, 252, 0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Zap size={20} color="#c084fc" />
                </div>
                <div>
                  <div
                    style={{
                      fontSize: 11,
                      fontWeight: 800,
                      color: 'var(--talent-purple)',
                      letterSpacing: '0.08em',
                      textTransform: 'uppercase',
                    }}
                  >
                    The New Way
                  </div>
                  <h3 style={{ fontSize: 18, fontWeight: 700, color: '#ffffff' }}>
                    TalentAI Autonomous Pipeline
                  </h3>
                </div>
              </div>
              <span
                style={{
                  background: 'rgba(147, 83, 252, 0.2)',
                  color: '#e9d5ff',
                  border: '1px solid rgba(147, 83, 252, 0.4)',
                  padding: '4px 10px',
                  borderRadius: 999,
                  fontSize: 11,
                  fontWeight: 700,
                }}
              >
                AFTER
              </span>
            </div>

            <div
              style={{
                fontSize: 22,
                fontWeight: 900,
                color: 'var(--talent-purple)',
                padding: '12px 16px',
                background: 'rgba(147, 83, 252, 0.1)',
                borderRadius: 'var(--radius-md)',
                marginBottom: 24,
                border: '1px solid rgba(147, 83, 252, 0.25)',
              }}
            >
              Predictable Retainer Model
              <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-muted)', marginLeft: 8 }}>
                (Save 60–70%)
              </span>
            </div>

            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 16 }}>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    You own the entire talent pipeline
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Continuous ingestion of candidate resumes with instant vector search access.
                  </div>
                </div>
              </li>

              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    Advanced AI matching across 100+ criteria
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    ChromaDB semantic embeddings combined with deterministic skill scoring.
                  </div>
                </div>
              </li>

              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    Real-time verification & conflict replanning
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Independent Evaluation Agent critiques the shortlist and triggers replanning.
                  </div>
                </div>
              </li>

              <li style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: 3 }} />
                <div>
                  <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: 14 }}>
                    Personalized outreach generated autonomously
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Communication Agent drafts bespoke interview invitations and constructive updates.
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
