'use client'

import { Star, Quote, Building2, Sparkles } from 'lucide-react'

export function TestimonialsSection() {
  const testimonials = [
    {
      name: 'Tyler Morgan',
      role: 'Founder & CEO, XpeedStudio',
      quote:
        'TalentAI helped us fill critical engineering leadership roles swiftly by providing verified talent that matched our stack. The autonomous multi-agent verification and conflict resolution set them completely apart from traditional recruiters.',
      stars: 5,
      impact: 'Filled 4 Senior Roles in 9 Days',
    },
    {
      name: 'Joshua Lane',
      role: 'COO, Pine Ridge Construction & RJB Group',
      quote:
        'They consistently brought high-quality talent for our teams to review. From senior project leads to cloud architects, the team spent the time to calibrate requirements and the AI agent pipeline delivered with extreme precision.',
      stars: 5,
      impact: '68% Reduction in Cost-Per-Hire',
    },
  ]

  return (
    <section style={{ padding: '80px 0', position: 'relative' }}>
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
            EXECUTIVE PROOF & SUCCESS STORIES
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
            What Our <span className="highlight-pill">Clients</span> Say
          </h2>

          <p
            style={{
              fontSize: 16,
              color: 'var(--text-secondary)',
              maxWidth: 640,
              margin: '0 auto',
            }}
          >
            Real stories of hiring speed and cost optimization with our AI-driven recruitment pipeline.
          </p>
        </div>

        {/* 2 Testimonial Cards */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 24,
          }}
        >
          {testimonials.map((t, idx) => (
            <div
              key={idx}
              className="glass-card"
              style={{
                padding: '32px 28px',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                {/* 5 Stars & Impact Badge */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: 18,
                  }}
                >
                  <div style={{ display: 'flex', gap: 4 }}>
                    {[...Array(t.stars)].map((_, i) => (
                      <Star key={i} size={16} fill="#f59e0b" color="#f59e0b" />
                    ))}
                  </div>

                  <span
                    style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: 'var(--talent-emerald)',
                      background: 'rgba(16, 185, 129, 0.12)',
                      padding: '3px 10px',
                      borderRadius: 999,
                      border: '1px solid rgba(16, 185, 129, 0.25)',
                    }}
                  >
                    {t.impact}
                  </span>
                </div>

                <p
                  style={{
                    fontSize: 15,
                    color: 'var(--text-secondary)',
                    lineHeight: 1.7,
                    fontStyle: 'italic',
                    marginBottom: 24,
                  }}
                >
                  &ldquo;{t.quote}&rdquo;
                </p>
              </div>

              {/* Author Bio */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 14,
                  borderTop: '1px solid var(--border-subtle)',
                  paddingTop: 18,
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #9353fc, #6366f1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#ffffff',
                    fontWeight: 800,
                    fontSize: 16,
                    boxShadow: '0 0 15px rgba(147, 83, 252, 0.4)',
                  }}
                >
                  {t.name[0]}
                </div>

                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, color: '#ffffff' }}>
                    {t.name}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {t.role}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
