import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Header } from '@/src/components/layout/Header';
import { Footer } from '@/src/components/layout/Footer';
import { QueryProvider, ToastProvider } from '@/src/providers';

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
});

export const metadata: Metadata = {
    title: 'ShopAI - AI-Powered Shopping Engine',
    description: 'Analyze products, compare prices, and find the best deals with AI-powered shopping assistance.',
    keywords: ['shopping', 'AI', 'product analysis', 'price comparison', 'recommendations'],
    authors: [{ name: 'ShopAI Team' }],
    openGraph: {
        title: 'ShopAI - AI-Powered Shopping Engine',
        description: 'Analyze products, compare prices, and find the best deals with AI-powered shopping assistance.',
        type: 'website',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className={inter.variable}>
            <body className="min-h-screen flex flex-col">
                <QueryProvider>
                    <ToastProvider />
                    <Header />
                    <main className="flex-1">
                        {children}
                    </main>
                    <Footer />
                </QueryProvider>
            </body>
        </html>
    );
}

