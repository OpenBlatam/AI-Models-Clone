import { ScrollArea } from "@/components/ui/scroll-area";
import { X, PlayCircle, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface Video {
  id: string;
  title: string;
  subtitle?: string;
  duration?: string;
  isLocked?: boolean;
  thumbnail?: string;
}

interface VideoSidebarProps {
  open: boolean;
  onClose: () => void;
  videos: Video[];
  currentIndex: number;
  onSelect: (idx: number) => void;
}

export function VideoSidebar({ open, onClose, videos, currentIndex, onSelect }: VideoSidebarProps) {
  const globalProgress = Math.round(((currentIndex + 1) / videos.length) * 100);
  return (
    <div className={cn(
      "fixed inset-0 z-50 flex",
      open ? "" : "pointer-events-none"
    )} style={{ display: open ? 'flex' : 'none' }}>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/60" onClick={onClose} />
      {/* Drawer */}
      <aside className="relative w-full max-w-sm bg-zinc-900 border-l border-zinc-800 shadow-2xl h-full ml-auto flex flex-col">
        <button onClick={onClose} className="absolute top-4 right-4 p-2 rounded-full hover:bg-zinc-800 z-10">
          <X className="w-6 h-6 text-zinc-400" />
        </button>
        <div className="p-6 pb-2">
          <h2 className="text-lg font-bold mb-2 flex items-center gap-2">
            Progreso del curso
            <span className="ml-auto text-base font-bold text-green-400">{globalProgress}%</span>
          </h2>
          <div className="h-2 bg-zinc-800 rounded-full mb-4 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-green-400 to-blue-500 transition-all" style={{ width: `${globalProgress}%` }} />
          </div>
        </div>
        <ScrollArea className="flex-1 px-6 pb-6">
          <div className="flex">
            {/* Timeline vertical */}
            <div className="flex flex-col items-center mr-4 relative">
              {/* Línea vertical con gradiente */}
              <div className="absolute top-4 bottom-4 left-1/2 w-1 -translate-x-1/2 bg-gradient-to-b from-green-400 via-blue-400 to-zinc-700 z-0" style={{ minHeight: videos.length * 56 }} />
              {videos.map((_, idx) => {
                const percent = Math.round(((idx + 1) / videos.length) * 100);
                const completed = idx < currentIndex;
                const isCurrent = idx === currentIndex;
                return (
                  <div key={idx} className="relative z-10 group">
                    <div
                      className={cn(
                        "w-12 h-12 flex flex-col items-center justify-center rounded-full border-2 text-lg font-bold mb-4 transition-all duration-300 relative",
                        completed
                          ? "bg-green-400 text-zinc-900 border-green-400 animate-pulse"
                          : isCurrent
                          ? "bg-white text-blue-600 border-blue-400 shadow-lg ring-2 ring-blue-400 scale-110 animate-glow"
                          : "bg-zinc-700 text-zinc-300 border-zinc-500"
                      )}
                    >
                      {completed ? (
                        <Check className="w-6 h-6 text-green-700 animate-bounce" />
                      ) : (
                        idx + 1
                      )}
                      <span className={cn(
                        "text-xs font-semibold mt-0.5",
                        completed ? "text-green-700" : isCurrent ? "text-blue-500" : "text-zinc-400"
                      )}>
                        {percent}%
                      </span>
                      {/* Tooltip */}
                      <span className="absolute left-1/2 -bottom-7 -translate-x-1/2 bg-zinc-800 text-xs text-white px-2 py-1 rounded shadow opacity-0 group-hover:opacity-100 transition pointer-events-none z-20">
                        {completed ? "Clase completada" : isCurrent ? "Clase actual" : "Pendiente"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Lista de videos */}
            <div className="flex-1 space-y-4">
              {videos.map((video, idx) => (
                <button
                  key={video.id}
                  onClick={() => onSelect(idx)}
                  className={cn(
                    "flex items-center gap-3 w-full p-3 rounded-lg transition-colors text-left",
                    idx === currentIndex ? "bg-zinc-800 text-green-400" : "bg-transparent text-zinc-100",
                    "hover:bg-zinc-800"
                  )}
                >
                  <div className="flex-shrink-0 w-12 h-12 bg-zinc-700 rounded overflow-hidden">
                    {video.thumbnail ? (
                      <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover" />
                    ) : (
                      <PlayCircle className="w-8 h-8 mx-auto my-2 text-blue-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0 text-left">
                    <div className="font-semibold text-sm truncate">
                      {video.title}
                    </div>
                    <div className="text-xs text-zinc-400 truncate">
                      {video.subtitle}
                    </div>
                    <div className="text-xs text-zinc-500 mt-1">
                      {video.duration || "00:00"}
                    </div>
                    {idx < currentIndex && (
                      <span className="text-green-400 text-xs font-bold ml-1">✓ Clase vista</span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </ScrollArea>
        <style jsx global>{`
          @keyframes glow {
            0% { box-shadow: 0 0 0 0 #60a5fa44; }
            50% { box-shadow: 0 0 16px 4px #60a5fa88; }
            100% { box-shadow: 0 0 0 0 #60a5fa44; }
          }
          .animate-glow { animation: glow 1.5s infinite; }
        `}</style>
      </aside>
    </div>
  );
} 