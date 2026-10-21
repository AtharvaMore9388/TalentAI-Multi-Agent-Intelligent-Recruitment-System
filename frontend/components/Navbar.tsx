'use client'

import { useState } from 'react'
import { Bot, Sparkles, Calendar, Radio, Play, RotateCcw } from 'lucide-react'

interface NavbarProps {
  apiOnline: boolean | null
  onOpenBooking: () => void
  onRunDemoTrace: () => void
  onReset: () => void
  hasTrace: boolean
  isRunning: boolean
}

export function Navbar({
  apiOnline,
  onOpenBooking,
  onRunDemoTrace,
  onReset,
  hasTrace,
  isRunning,
}: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const scrollTo = (id: string) => {
    setMobileMenuOpen(false)
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <header
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        backgroundColor: 'var(--bg-glass)',
        borderBottom: '1px solid var(--border-subtle)',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: 72,
        }}
      >
        {/* Brand Logo */}
        <div
          onClick={() => scrollTo('hero')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            cursor: 'pointer',
            userSelect: 'none',
          }}
        >
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: 12,
              background: 'linear-gradient(135deg, #9353fc 0%, #6366f1 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(147, 83, 252, 0.4)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
            }}
          >
            <Bot size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span
                style={{
                  fontSize: 20,
                  fontWeight: 800,
                  letterSpacing: '-0.03em',
                  color: '#ffffff',
                }}
              >
                Talent<span style={{ color: 'var(--talent-purple)' }}>AI</span>
              </span>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  padding: '2px 7px',
                  borderRadius: 999,
                  background: 'rgba(147, 83, 252, 0.18)',
                  color: '#c084fc',
                  border: '1px solid rgba(147, 83, 252, 0.3)',
                  textTransform: 'uppercase',
                }}
              >
                Agency
              </span>
            </div>
            <p style={{ fontSize: 10.5, color: 'var(--text-muted)', marginTop: -2 }}>
              Multi-Agent Intelligent Recruitment and Talent Matching System
            </p>
          </div>
        </div>

        {/* Desktop Navigation Links */}
        <nav
          style={{
            display: 'none',
            alignItems: 'center',
            gap: 28,
            fontSize: 13,
            fontWeight: 500,
          }}
          className="desktop-nav"
        >
          <button
            onClick={() => scrollTo('advantage')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
              transition: 'color 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#ffffff')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          >
            Advantage
          </button>
          <button
            onClick={() => scrollTo('compare')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
              transition: 'color 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#ffffff')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          >
            Old vs New Way
          </button>
          <button
            onClick={() => scrollTo('roadmap')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
              transition: 'color 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#ffffff')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          >
            Partner Model
          </button>
          <button
            onClick={() => scrollTo('studio')}
            style={{
              background: 'none',
              border: 'none',
              color: '#c084fc',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 5,
            }}
          >
            <Sparkles size={14} />
            Live AI Studio
          </button>
          <button
            onClick={() => scrollTo('tiers')}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
              transition: 'color 0.2s',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#ffffff')}
            onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-secondary)')}
          >
            Service Tiers
          </button>
        </nav>

        {/* Right CTA / Action Area */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {/* API Health Status Pill */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 11,
              padding: '5px 12px',
              borderRadius: 999,
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-subtle)',
            }}
            title="FastAPI Backend Health"
          >
            <div
              style={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                backgroundColor:
                  apiOnline === null
                    ? '#94a3b8'
                    : apiOnline
                    ? 'var(--talent-emerald)'
                    : 'var(--talent-rose)',
                boxShadow:
                  apiOnline
                    ? '0 0 10px var(--talent-emerald)'
                    : '0 0 8px rgba(239, 68, 68, 0.5)',
              }}
            />
            <span style={{ color: 'var(--text-secondary)' }}>
              {apiOnline === null ? 'Connecting' : apiOnline ? 'API Active' : 'API Standby'}
            </span>
          </div>

          {/* Quick Demo Trace Trigger */}
          <button
            className="btn btn-outline"
            onClick={onRunDemoTrace}
            style={{ fontSize: 12, padding: '7px 14px' }}
            title="Run simulated CrewAI recruitment trace"
          >
            <Play size={13} />
            Demo Trace
          </button>

          {/* Reset if active */}
          {(hasTrace || isRunning) && (
            <button
              className="btn btn-ghost"
              onClick={onReset}
              style={{ fontSize: 12, padding: '7px 12px' }}
              title="Reset state"
            >
              <RotateCcw size={13} />
            </button>
          )}

          {/* Primary Action Button (talent-ai.agency style) */}
          <button
            className="btn btn-talent"
            onClick={onOpenBooking}
            style={{ fontSize: 13, padding: '10px 20px', letterSpacing: '0.02em' }}
          >
            <Calendar size={14} />
            BOOK A CALL
          </button>
        </div>
      </div>

      <style jsx>{`
        @media (min-width: 900px) {
          .desktop-nav {
            display: flex !important;
          }
        }
      `}</style>
    </header>
  )
}
