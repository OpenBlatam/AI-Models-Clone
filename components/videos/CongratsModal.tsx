import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { CheckCircle, ArrowRight } from "lucide-react";
import ReactConfetti from "react-confetti";
import { useEffect, useState } from "react";

const PHRASES = [
  "¡Sigue así, vas genial!",
  "¡Un paso más cerca de tu meta!",
  "¡Aprender es crecer!",
  "¡Eres imparable!",
  "¡Cada clase cuenta!",
];

export function CongratsModal({
  open,
  onClose,
  onNext,
  progress,
  currentTitle,
  nextTitle,
}: {
  open: boolean;
  onClose: () => void;
  onNext: () => void;
  progress: number;
  currentTitle: string;
  nextTitle?: string;
}) {
  const [phrase, setPhrase] = useState(PHRASES[0]);
  useEffect(() => {
    if (open) setPhrase(PHRASES[Math.floor(Math.random() * PHRASES.length)]);
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      {open && (
        <ReactConfetti
          width={window.innerWidth}
          height={window.innerHeight}
          recycle={false}
          numberOfPieces={180}
          gravity={0.25}
        />
      )}
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
        <div className="bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 border-2 border-blue-500/40 shadow-2xl rounded-3xl p-8 max-w-md w-full flex flex-col items-center relative animate-fade-in">
          <div className="relative mb-4">
            <CheckCircle className="w-20 h-20 text-green-400 drop-shadow-lg animate-bounce" />
            <div className="absolute -top-2 -right-2 bg-white text-blue-600 font-bold rounded-full w-10 h-10 flex items-center justify-center border-4 border-zinc-900 shadow">
              {progress}%
            </div>
          </div>
          <h2 className="text-3xl font-extrabold mb-2 text-center text-green-400 drop-shadow">¡Felicidades!</h2>
          <p className="text-lg text-zinc-200 mb-2 text-center">
            Completaste la clase:
            <br />
            <span className="font-semibold text-blue-400">{currentTitle}</span>
          </p>
          <div className="italic text-blue-300 mb-4 text-center">{phrase}</div>
          <div className="w-full mb-4">
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-400 to-blue-500 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="text-xs text-zinc-400 mt-1 text-right">{progress}% completado</div>
          </div>
          {nextTitle && (
            <Button
              onClick={onNext}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-green-500 hover:from-blue-700 hover:to-green-600 text-white font-bold py-2 rounded-xl mt-2 shadow-lg animate-pulse"
            >
              Siguiente clase <ArrowRight className="w-5 h-5 animate-move-right" />
            </Button>
          )}
          <Button variant="ghost" onClick={onClose} className="w-full mt-2">
            Cerrar
          </Button>
        </div>
      </div>
      <style jsx global>{`
        @keyframes fade-in {
          from { opacity: 0; transform: scale(0.95);}
          to { opacity: 1; transform: scale(1);}
        }
        .animate-fade-in { animation: fade-in 0.5s; }
        @keyframes move-right {
          0% { transform: translateX(0);}
          50% { transform: translateX(6px);}
          100% { transform: translateX(0);}
        }
        .animate-move-right { animation: move-right 1.2s infinite; }
      `}</style>
    </Dialog>
  );
} 