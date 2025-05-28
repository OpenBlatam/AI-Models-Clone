import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChevronLeft, ChevronRight, Languages, Flag, PlayCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface VideoHeaderProps {
  title: string;
  subtitle: string;
  onNextVideo: () => void;
  onPreviousVideo: () => void;
  isFirstVideo?: boolean;
  onShowSidebar?: () => void;
}

export function VideoHeader({
  title,
  subtitle,
  onNextVideo,
  onPreviousVideo,
  isFirstVideo = false,
  onShowSidebar,
}: VideoHeaderProps) {
  return (
    <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-950 gap-2">
      <div className="flex items-center gap-3 min-w-0">
        <div className="flex-shrink-0">
          <Image src="/ai-logo.png" alt="AI Logo" width={40} height={40} className="rounded-full border-2 border-green-400 bg-zinc-900" />
        </div>
        <div className="min-w-0">
          <div className="text-xs text-zinc-300 truncate">{subtitle}</div>
          <div className="text-lg sm:text-xl font-bold truncate">{title}</div>
        </div>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        <button className="rounded bg-zinc-800 hover:bg-zinc-700 p-2 text-zinc-300" title="Idioma"><Languages className="w-5 h-5" /></button>
        <button className="rounded bg-zinc-800 hover:bg-zinc-700 p-2 text-zinc-300" title="Reportar"><Flag className="w-5 h-5" /></button>
        <button onClick={onShowSidebar} className="rounded bg-zinc-800 hover:bg-zinc-700 px-3 py-2 text-sm font-medium text-zinc-100 flex items-center gap-2"><PlayCircle className="w-4 h-4" />Ver clases</button>
        {!isFirstVideo && (
          <button 
            onClick={onPreviousVideo} 
            className="rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-100 px-4 py-2 text-sm font-semibold flex items-center gap-2"
          >
            <ChevronLeft className="w-4 h-4" /> Clase anterior
          </button>
        )}
        <button onClick={onNextVideo} className="rounded bg-white text-zinc-900 px-4 py-2 text-sm font-semibold flex items-center gap-2">Siguiente clase <span className="ml-1">→</span></button>
      </div>
    </div>
  );
} 