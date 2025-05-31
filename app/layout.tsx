import "@/styles/globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { fontGeist, fontHeading, fontSans, fontUrban } from "@/assets/fonts";
import { cn, constructMetadata } from "@/lib/utils";
import { Toaster } from "@/components/ui/sonner";
import { Analytics } from "@/components/analytics";
import ModalProvider from "@/components/modals/providers";
import { TailwindIndicator } from "@/components/tailwind-indicator";
import { ChatLayout } from "@/components/chat-layout";
import { AuthProvider } from "@/components/auth-provider";
import { ThemeProvider } from "next-themes";
import { MetaMaskProvider } from "@/components/web3/MetaMaskProvider";
import { AblySpacesProvider } from "@/components/providers/ably-provider";

const inter = Inter({ subsets: ["latin"] });

interface RootLayoutProps {
  children: React.ReactNode;
}

export const metadata: Metadata = constructMetadata({
  title: "Blatam Academy",
  description: "Empowering the next generation of tech leaders through innovative education and practical experience.",
});

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          fontSans.variable,
          fontUrban.variable,
          fontHeading.variable,
          fontGeist.variable,
          inter.className,
        )}
        suppressHydrationWarning
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <AblySpacesProvider>
            <MetaMaskProvider>
              <AuthProvider>
                {/* Custom widgets as raw HTML to avoid React/JSX errors */}
                <div
                  suppressHydrationWarning
                  dangerouslySetInnerHTML={{
                    __html: `
                      <elevenlabs-convai agent-id="agent_01jw2hqjcmf5js8yr208bavbaq"></elevenlabs-convai>
                      <script src="https://elevenlabs.io/convai-widget/index.js" async type="text/javascript"></script>
                      <d-id-chatbot
                        chat-title="Asistente IA"
                        auth="TU_API_KEY"
                        agent-id="TU_AGENT_ID"
                        style="position: fixed; bottom: 20px; right: 100px; z-index: 9999;">
                      </d-id-chatbot>
                      <script src="https://unpkg.com/@d-id/chatbot@latest/dist/vanilla/index.js"></script>
                    `,
                  }}
                />
                <ChatLayout>
                  <ModalProvider>{children}</ModalProvider>
                </ChatLayout>
                <Analytics />
                <Toaster richColors closeButton />
                <TailwindIndicator />
              </AuthProvider>
            </MetaMaskProvider>
          </AblySpacesProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
