'use client'

import { useState, useEffect } from 'react'
import { fetchHealth } from '@/lib/api'
import { Navbar } from '@/components/Navbar'
import { HeroSection } from '@/components/HeroSection'
import { BeforeAfterSection } from '@/components/BeforeAfterSection'
import { AdvantageSection } from '@/components/AdvantageSection'
import { PartnerModelSection } from '@/components/PartnerModelSection'
import { TalentStudio } from '@/components/TalentStudio'
import { PricingTiersSection } from '@/components/PricingTiersSection'
import { TestimonialsSection } from '@/components/TestimonialsSection'
import { BookCallModal } from '@/components/BookCallModal'
import { Footer } from '@/components/Footer'

export default function Home() {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [bookingModalOpen, setBookingModalOpen] = useState(false)
  const [demoTraceTrigger, setDemoTraceTrigger] = useState(0)

  // Verify backend health
  useEffect(() => {
    fetchHealth()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false))
  }, [])

  const scrollToStudio = () => {
    const el = document.getElementById('studio')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleRunDemoTrace = () => {
    setDemoTraceTrigger((prev) => prev + 1)
    scrollToStudio()
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ── Top Agency Navbar ── */}
      <Navbar
        apiOnline={apiOnline}
        onOpenBooking={() => setBookingModalOpen(true)}
        onRunDemoTrace={handleRunDemoTrace}
        onReset={() => {
          // Triggers reload or resets state
          setDemoTraceTrigger(0)
        }}
        hasTrace={demoTraceTrigger > 0}
        isRunning={false}
      />

      <main style={{ flex: 1 }}>
        {/* ── Hero Section (talent-ai.agency dynamic animated style) ── */}
        <HeroSection
          onOpenBooking={() => setBookingModalOpen(true)}
          onRunDemoTrace={handleRunDemoTrace}
          onScrollToStudio={scrollToStudio}
        />

        {/* ── The Old Way vs The New Way (Before / After) ── */}
        <BeforeAfterSection />

        {/* ── The Talent AI Advantage (Cutting-Edge Tech) ── */}
        <AdvantageSection />

        {/* ── AI Talent Partner Model (Find, Engage, Qualify, Track) ── */}
        <PartnerModelSection />

        {/* ── LIVE MULTI-AGENT STUDIO (Interactive Cockpit) ── */}
        <TalentStudio
          apiOnline={apiOnline}
          externalTraceTrigger={demoTraceTrigger}
        />

        {/* ── Tailored Service Offerings (Pricing Tiers) ── */}
        <PricingTiersSection
          onOpenBooking={() => setBookingModalOpen(true)}
          onScrollToStudio={scrollToStudio}
        />

        {/* ── Client Testimonials & Social Proof ── */}
        <TestimonialsSection />
      </main>

      {/* ── Agency Footer ── */}
      <Footer />

      {/* ── Book A Call Modal ── */}
      <BookCallModal
        isOpen={bookingModalOpen}
        onClose={() => setBookingModalOpen(false)}
      />
    </div>
  )
}
