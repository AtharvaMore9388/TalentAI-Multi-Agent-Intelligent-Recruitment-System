'use client'

import { Check, Sparkles, Zap, ArrowRight } from 'lucide-react'

interface PricingTiersSectionProps {
  onOpenBooking: () => void
  onScrollToStudio: () => void
}

export function PricingTiersSection({
  onOpenBooking,
  onScrollToStudio,
}: PricingTiersSectionProps) {
  const tiers = [
    {
      name: 'Starter',
      badge: 'Early Stage',
      desc: 'Ideal for startups hiring key technical founding members without agency markups.',
      slots: 'Up to 3 job slots per month',
      candidates: 'Up to 100 targeted candidates',
      features: [
        'Job & Resume automated parsing',
        'RAG semantic search & skill match',
        'Deterministic candidate scoring',
        'Standard shortlist exports',
        'Standard LLM latency',
      ],
      featured: false,
      cta: 'Get Started',
    },
    {
      name: 'Professional',
      badge: 'Most Popular',
      desc: 'Complete autonomous multi-agent pipeline for growing engineering & product teams.',
      slots: 'Up to 5 job slots per month',
      candidates: 'Up to 250 targeted candidates',
      features: [
        'All Starter capabilities',
        'Full 5-Agent Collaborative Network',
        'Independent Evaluation & Conflict Rejection',
        'Dynamic requirement relaxation & replanning',
        'Personalized interview invite generation',
        'Priority high-throughput Groq inference',
        'Live streaming execution telemetry',
      ],
      featured: true,
      cta: 'Launch Pro Pipeline',
    },
    {
      name: 'Custom Enterprise',
      badge: 'Full Automation',
      desc: 'Dedicated multi-agent infrastructure with bespoke company knowledge bases.',
      slots: 'Custom job slots (Unlimited)',
      candidates: 'Unlimited candidate database',
      features: [
        'All Professional capabilities',
        'Custom ChromaDB vector index deployment',
        'Tailored agent personas & scoring rubrics',
        'ATS / HRIS webhook integrations',
        'Dedicated AI agent engineer & SLA support',
        'Audit-ready compliance logging',
      ],
      featured: false,
      cta: 'Contact Enterprise',
    },
  ]

  return (
    <section id="tiers" style={{ padding: '80px 0', position: 'relative' }}>
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
            PREDICTABLE RETAINERS, NOT PLACEMENT COMMISSIONS
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
            Tailored <span className="highlight-pill">Service Offerings</span>
          </h2>

          <p
            style={{
              fontSize: 16,
              color: 'var(--text-secondary)',
              maxWidth: 640,
              margin: '0 auto',
            }}
          >
            Pay monthly for access to your AI hiring engine, not $15,000–$20,000+ per hire.
            You own the pipeline and candidate relationship.
          </p>
        </div>

        {/* Tiers Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: 24,
            alignItems: 'stretch',
          }}
        >
          {tiers.map((tier, idx) => (
            <div
              key={idx}
              className={`tier-card ${tier.featured ? 'featured' : ''}`}
            >
              {tier.featured && (
                <div
                  style={{
                    position: 'absolute',
                    top: -14,
                    right: 28,
                    background: 'linear-gradient(135deg, #9353fc, #6366f1)',
                    color: '#ffffff',
                    padding: '4px 14px',
                    borderRadius: 999,
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: '0.05em',
                    boxShadow: '0 4px 15px rgba(147, 83, 252, 0.5)',
                  }}
                >
                  RECOMMENDED
                </div>
              )}

              <div style={{ marginBottom: 20 }}>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: tier.featured ? 'var(--talent-purple)' : 'var(--text-muted)',
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase',
                  }}
                >
                  {tier.badge}
                </span>
                <h3 style={{ fontSize: 26, fontWeight: 800, color: '#ffffff', marginTop: 4 }}>
                  {tier.name}
                </h3>
                <p
                  style={{
                    fontSize: 13.5,
                    color: 'var(--text-secondary)',
                    marginTop: 8,
                    lineHeight: 1.5,
                  }}
                >
                  {tier.desc}
                </p>
              </div>

              {/* Slot / Candidate specs (highlighted like talent-ai.agency) */}
              <div
                style={{
                  padding: '14px 16px',
                  borderRadius: 'var(--radius-md)',
                  background: tier.featured
                    ? 'rgba(147, 83, 252, 0.12)'
                    : 'rgba(255, 255, 255, 0.03)',
                  border: `1px solid ${
                    tier.featured ? 'rgba(147, 83, 252, 0.3)' : 'var(--border-subtle)'
                  }`,
                  marginBottom: 24,
                }}
              >
                <div style={{ fontWeight: 700, fontSize: 14, color: '#ffffff' }}>
                  {tier.slots}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                  {tier.candidates}
                </div>
              </div>

              {/* Features List */}
              <ul
                style={{
                  listStyle: 'none',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 12,
                  marginBottom: 32,
                  flex: 1,
                }}
              >
                {tier.features.map((feat, fIdx) => (
                  <li
                    key={fIdx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      fontSize: 13.5,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    <div
                      style={{
                        width: 18,
                        height: 18,
                        borderRadius: '50%',
                        background: 'rgba(16, 185, 129, 0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <Check size={12} color="#10b981" />
                    </div>
                    <span>{feat}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <button
                className={`btn ${tier.featured ? 'btn-talent' : 'btn-outline'}`}
                onClick={tier.featured ? onScrollToStudio : onOpenBooking}
                style={{
                  width: '100%',
                  padding: '13px',
                  fontSize: 14,
                  fontWeight: 700,
                }}
              >
                {tier.cta}
                <ArrowRight size={15} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
