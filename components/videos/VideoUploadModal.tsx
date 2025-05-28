import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Video as VideoIcon, UploadCloud, X } from "lucide-react";
import { useRef } from "react";

interface VideoUploadModalProps {
  open: boolean;
  onClose: () => void;
  recording: boolean;
  videoURL: string | null;
  videoRef: React.RefObject<HTMLVideoElement>;
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
  onUpload: () => void;
}

export function VideoUploadModal({ open, onClose, recording, videoURL, videoRef, onStart, onStop, onReset, onUpload }: VideoUploadModalProps) {
  return (
    <Dialog open={open} onOpenChange={v => !v && onClose()}>
      <DialogContent className="bg-zinc-900 rounded-xl p-6 w-full max-w-md shadow-2xl flex flex-col items-center">
        <DialogHeader>
          <DialogTitle className="mb-4 text-lg font-bold flex items-center gap-2"><VideoIcon className="w-6 h-6" /> Graba o sube tu video</DialogTitle>
        </DialogHeader>
        <video ref={videoRef} autoPlay muted className="w-full rounded mb-4 bg-black aspect-video" src={videoURL || undefined} controls={!!videoURL} />
        {!videoURL && !recording && (
          <Button onClick={onStart} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2"><VideoIcon className="w-5 h-5" /> Iniciar grabación</Button>
        )}
        {recording && (
          <Button onClick={onStop} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2"><VideoIcon className="w-5 h-5" /> Detener grabación</Button>
        )}
        {videoURL && (
          <>
            <Button onClick={onUpload} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2"><UploadCloud className="w-5 h-5" /> Subir video</Button>
            <Button onClick={onReset} className="bg-zinc-700 hover:bg-zinc-800 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2"><X className="w-5 h-5" /> Cancelar</Button>
          </>
        )}
        <DialogClose asChild>
          <Button variant="ghost" size="icon" className="absolute top-2 right-2 p-2 rounded-full hover:bg-zinc-800"><X className="w-5 h-5" /></Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  );
} 