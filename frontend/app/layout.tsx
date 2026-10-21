import type { Metadata } from 'next'
import { Plus_Jakarta_Sans, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const sans = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-sans',
  display: 'swap',
})

const mono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  variable: '--font-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'TalentAI — Revolutionising Recruitment with AI | Multi-Agent Platform',
  description: 'AI-powered recruitment solutions for inbound talent acquisition. Powered by 5 autonomous agents, RAG semantic resume matching, and dynamic conflict replanning.',
  keywords: 'Talent AI, AI recruitment, multi-agent hiring, CrewAI, ChromaDB, RAG talent matching',
  openGraph: {
    title: 'TalentAI — Revolutionising Recruitment with AI',
    description: 'AI-powered recruitment solutions for inbound talent acquisition & autonomous agent orchestration',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <body className={sans.className}>{children}</body>
    </html>
  )
}
