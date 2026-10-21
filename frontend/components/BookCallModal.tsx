'use client'

import { useState } from 'react'
import { X, Calendar, Clock, CheckCircle2, ArrowRight, ExternalLink, Sparkles } from 'lucide-react'

interface BookCallModalProps {
  isOpen: boolean
  onClose: () => void
}

export function BookCallModal({ isOpen, onClose }: BookCallModalProps) {
  const [submitted, setSubmitted] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [role, setRole] = useState('')
  const [teamSize, setTeamSize] = useState('10-50')

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitted(true)
  }

  const handleReset = () => {
    setSubmitted(false)
    setName('')
    setEmail('')
    setRole('')
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 20,
            right: 20,
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '50%',
            width: 32,
            height: 32,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
          }}
        >
          <X size={16} />
        </button>

        {!submitted ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: 'rgba(147, 83, 252, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Calendar size={18} color="#c084fc" />
              </div>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 700,
                  color: 'var(--talent-purple)',
                  letterSpacing: '0.05em',
                  textTransform: 'uppercase',
                }}
              >
                Strategy Consultation
              </span>
            </div>

            <h3 style={{ fontSize: 24, fontWeight: 800, color: '#ffffff', marginBottom: 6 }}>
              Book an AI Recruitment Consultation
            </h3>

            <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', marginBottom: 24, lineHeight: 1.5 }}>
              Discover how our autonomous multi-agent pipeline can replace traditional agency fees,
              cut your time-to-hire by 70%, and source qualified candidates on demand.
            </p>

            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder="e.g. Alex Mercer"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                  Work Email *
                </label>
                <input
                  type="email"
                  required
                  className="input-field"
                  placeholder="alex@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                    Hiring Needs
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="e.g. 2 Senior Engineers"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: 6 }}>
                    Company Size
                  </label>
                  <select
                    className="input-field"
                    value={teamSize}
                    onChange={(e) => setTeamSize(e.target.value)}
                    style={{ cursor: 'pointer' }}
                  >
                    <option value="1-10">1–10 employees</option>
                    <option value="10-50">10–50 employees</option>
                    <option value="50-200">50–200 employees</option>
                    <option value="200+">200+ employees</option>
                  </select>
                </div>
              </div>

              <div style={{ marginTop: 10, display: 'flex', gap: 12 }}>
                <button
                  type="submit"
                  className="btn btn-talent"
                  style={{ flex: 1, padding: '13px', fontSize: 14 }}
                >
                  Confirm & Schedule Call
                  <ArrowRight size={16} />
                </button>
              </div>

              <div style={{ textAlign: 'center', marginTop: 12 }}>
                <a
                  href="https://calendly.com/talent_ai/30min"
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    fontSize: 12,
                    color: 'var(--talent-purple)',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 4,
                    textDecoration: 'none',
                  }}
                >
                  Or schedule directly via Calendly
                  <ExternalLink size={12} />
                </a>
              </div>
            </form>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '24px 8px' }}>
            <div
              style={{
                width: 60,
                height: 60,
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
              }}
            >
              <CheckCircle2 size={32} color="#10b981" />
            </div>

            <h3 style={{ fontSize: 24, fontWeight: 800, color: '#ffffff', marginBottom: 8 }}>
              Consultation Scheduled!
            </h3>

            <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: 440, margin: '0 auto 24px' }}>
              Thank you, <strong style={{ color: '#fff' }}>{name || 'there'}</strong>. We have received your inquiry.
              Our recruitment architecture team will reach out at <strong style={{ color: 'var(--talent-purple)' }}>{email}</strong> within 2 hours.
            </p>

            <button className="btn btn-talent" onClick={handleReset} style={{ padding: '11px 24px' }}>
              Back to TalentAI Platform
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
