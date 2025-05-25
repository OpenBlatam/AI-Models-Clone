"use client";

import { DashboardNav } from "@/components/dashboard/dashboard-nav";
import dynamic from 'next/dynamic';
import React from "react";
import FloatingStatusWidget from "@/components/FloatingStatusWidget";

const InteractiveTTSPanel = dynamic(() => import("@/agents/InteractiveTTSPanel"), {
  ssr: false
});

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  React.useEffect(() => {
    const script = document.createElement('script');
    script.src = "https://elevenlabs.io/convai-widget/index.js";
    script.async = true;
    script.type = "text/javascript";
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="relative min-h-screen">
      <header className="sticky top-0 z-40 border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <DashboardNav />
        </div>
      </header>
      <div className="container py-6">
        <InteractiveTTSPanel />
        <FloatingStatusWidget
          message="Llamando a IA"
          color="purple"
          visible={true}
          onCancel={() => {}}
        />
        <main className="mt-6">
          {children}
        </main>
      </div>
      {/* ElevenLabs Convai Widget */}
      <elevenlabs-convai agent-id="agent_01jw2hqjcmf5js8yr208bavbaq"></elevenlabs-convai>
    </div>
  );
} 