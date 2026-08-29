import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CyberOS — Intelligent Cybersecurity Platform',
  description: 'AI-Driven Phishing, Scam & Cyber-Fraud Detection',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-black text-slate-50 min-h-screen font-sans antialiased selection:bg-blue-500/30">
        {children}
      </body>
    </html>
  )
}
