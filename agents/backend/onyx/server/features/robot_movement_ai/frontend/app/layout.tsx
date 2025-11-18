import { Inter } from 'next/font/google';
import ThemeProvider from '@/components/ThemeProvider';
import { ErrorBoundary } from '@/lib/utils/errorBoundary';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Robot Movement AI - Control Platform',
  description: 'Plataforma IA de Movimiento Robótico - Control mediante chat',
  manifest: '/manifest.json',
  themeColor: '#0ea5e9',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Robot Movement AI',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
        <meta name="theme-color" content="#0ea5e9" />
      </head>
      <body className={inter.className}>
        <ErrorBoundary>
          <ThemeProvider>{children}</ThemeProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}

