import type { Metadata } from "next";
import "./globals.css";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { generateMetaTags } from "@/lib/utils/seo";

const metaTags = generateMetaTags();

export const metadata: Metadata = {
  title: metaTags.title,
  description: metaTags.description,
  keywords: metaTags.keywords,
  authors: [{ name: metaTags.author }],
  openGraph: {
    title: metaTags['og:title'],
    description: metaTags['og:description'],
    images: [metaTags['og:image']],
    type: metaTags['og:type'] as 'website',
  },
  twitter: {
    card: metaTags['twitter:card'] as 'summary_large_image',
    title: metaTags['twitter:title'],
    description: metaTags['twitter:description'],
  },
  viewport: 'width=device-width, initial-scale=1',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="antialiased">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}

