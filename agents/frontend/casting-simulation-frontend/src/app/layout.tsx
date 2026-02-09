import type { Metadata } from "next";
import { Inter } from 'next/font/google';
import "./globals.css";
import { AppLayout } from "@/components/layout/AppLayout";

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: "CastSim AI | Casting Simulation",
  description: "AI-powered casting simulation based on PoligonCast modules",
  keywords: ["casting", "simulation", "AI", "foundry", "mesh", "solidification"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppLayout>
          {children}
        </AppLayout>
      </body>
    </html>
  );
}
