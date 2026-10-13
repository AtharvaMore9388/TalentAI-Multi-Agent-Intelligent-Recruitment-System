import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TalentAI — Multi-Agent Recruitment System',
  description: 'AI-powered multi-agent recruitment platform using RAG, semantic search, and autonomous agent orchestration to intelligently match candidates with job requirements.',
  keywords: 'AI recruitment, multi-agent, RAG, semantic search, talent matching',
  openGraph: {
    title: 'TalentAI — Multi-Agent Recruitment System',
    description: 'AI-powered recruitment platform with 5 specialized agents',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  )
}
