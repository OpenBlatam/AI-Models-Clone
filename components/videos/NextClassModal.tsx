import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { CheckCircle } from "lucide-react";

interface NextClassModalProps {
  open: boolean;
  onClose: () => void;
  onNext: () => void;
  currentTitle: string;
  nextTitle?: string;
  nextThumbnail?: string;
  countdownSeconds?: number;
}

export default function NextClassModal({
  open,
  onClose,
  onNext,
  currentTitle,
  nextTitle,
  nextThumbnail,
  countdownSeconds = 5,
}: NextClassModalProps) {
  const [seconds, setSeconds] = useState(countdownSeconds);

  useEffect(() => {
    if (!open) return;
    setSeconds(countdownSeconds);
    if (!nextTitle) return;
    const interval = setInterval(() => {
      setSeconds((s) => {
        if (s <= 1) {
          clearInterval(interval);
          onNext();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [open, nextTitle, countdownSeconds, onNext]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
      <div className="bg-zinc-900 rounded-2xl p-8 max-w-lg w-full flex flex-col items-center shadow-2xl border border-zinc-800 relative animate-fade-in">
        <div className="flex items-center gap-2 mb-2 w-full">
          <CheckCircle className="w-6 h-6 text-green-400" />
          <span className="text-lg font-bold text-white">Ya viste:</span>
        </div>
        <div className="w-full text-left mb-2 text-white text-base font-semibold truncate">{currentTitle}</div>
        {nextTitle && (
          <div className="w-full text-left text-zinc-300 mb-2">
            Próxima clase en <span className="font-bold text-white">{seconds}</span>
          </div>
        )}
        {nextThumbnail && (
          <img src={nextThumbnail} alt={nextTitle} className="w-full rounded-xl mb-4 object-cover aspect-video bg-zinc-800" />
        )}
        <div className="flex gap-4 w-full mt-4">
          <Button onClick={onClose} variant="secondary" className="flex-1">Detener</Button>
          {nextTitle && (
            <Button onClick={onNext} className="flex-1 bg-white text-zinc-900 font-bold">Ver siguiente clase</Button>
          )}
        </div>
      </div>
      <style jsx global>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(24px);}
          to { opacity: 1; transform: translateY(0);}
        }
        .animate-fade-in { animation: fade-in 0.5s; }
      `}</style>
    </div>
  );
} 