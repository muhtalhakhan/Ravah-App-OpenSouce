import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Ravah — Turn what you ship into social content',
  description:
    'Generate a week of platform-optimized social media posts from what you\'re building. Bring your own Google API key.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  )
}
