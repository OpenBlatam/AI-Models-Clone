import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { QueryProvider } from '@/components/providers/query-provider';
import { ConditionalLayout } from '@/components/layout/conditional-layout';
import { Toaster } from '@/components/ui/toaster';
import { Analytics } from '@/components/analytics';
import '@/styles/globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'Blatam Academy - Next.js Platform',
    template: '%s | Blatam Academy',
  },
  description: 'Modern Next.js platform built with best practices, TypeScript, and modern UI frameworks.',
  keywords: [
    'Next.js',
    'React',
    'TypeScript',
    'Tailwind CSS',
    'Modern Web Development',
    'Blatam Academy',
  ],
  authors: [{ name: 'Blatam Academy Team' }],
  creator: 'Blatam Academy',
  publisher: 'Blatam Academy',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'Blatam Academy - Next.js Platform',
    description: 'Modern Next.js platform built with best practices, TypeScript, and modern UI frameworks.',
    siteName: 'Blatam Academy',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Blatam Academy - Next.js Platform',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Blatam Academy - Next.js Platform',
    description: 'Modern Next.js platform built with best practices, TypeScript, and modern UI frameworks.',
    images: ['/og-image.jpg'],
    creator: '@blatamacademy',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} font-sans antialiased bg-background text-foreground`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <QueryProvider>
            <ConditionalLayout>
              {children}
            </ConditionalLayout>
            <Toaster />
            <Analytics />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
