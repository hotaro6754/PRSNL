import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'NTRO Sentinel-26145 | Unidirectional IP Cyber Threat Detection',
  description: 'AI-Based Detection of Cyber Threats in Unidirectional IP Traffic across Data Diodes (NTRO Problem Statement #26145)',
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
