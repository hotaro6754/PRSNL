import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Sentinel-26145',
  description: 'Passive threat detection for one-way (tap / data-diode) IP traffic — NTRO SIH problem statement 26145',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  )
}
