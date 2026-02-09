import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import { Toaster } from "sonner";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Prompt Compiler | AI SAM3",
  description: "AI-powered prompt compiler and analyzer with quality scoring, multi-dimensional analysis, and actionable recommendations",
  keywords: ["prompt engineering", "AI", "prompt analyzer", "quality scoring", "LLM"],
  authors: [{ name: "Blatam Academy" }],
  openGraph: {
    title: "Prompt Compiler | AI SAM3",
    description: "Analyze and improve your prompts with AI-powered quality scoring",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased min-h-screen`}>
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Toast notifications */}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "#1e293b",
              border: "1px solid #475569",
              color: "#e2e8f0",
            },
          }}
          richColors
        />

        {/* Background decoration */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl animate-pulse-glow" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse-glow" style={{ animationDelay: "1s" }} />
        </div>
      </body>
    </html>
  );
}
