import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { Navigation } from '@/components/navigation'
import { SkipLink } from '@/components/skip-link'
import { ScrollToTop } from '@/components/scroll-to-top'
import { KeyboardShortcuts } from '@/components/keyboard-shortcuts'
import { PageTracker } from '@/components/page-tracker'
import { OfflineBanner } from '@/components/offline-banner'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Physical Store Designer AI',
  description: 'Diseña locales físicos completos con IA',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <Providers>
          <SkipLink />
          <KeyboardShortcuts />
          <PageTracker />
          <Navigation />
          <OfflineBanner />
          <main id="main-content">{children}</main>
          <ScrollToTop />
        </Providers>
      </body>
    </html>
  )
}

