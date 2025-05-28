import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState, FormEvent } from "react";

interface VideoQuestionBarProps {
  onAsk: (question: string) => void;
}

export function VideoQuestionBar({ onAsk }: VideoQuestionBarProps) {
  const [value, setValue] = useState("");
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onAsk(value);
      setValue("");
    }
  };
  return (
    <form onSubmit={handleSubmit} className="flex items-center bg-zinc-900 border border-gradient-to-r from-purple-400 to-blue-400 rounded-2xl px-4 py-2 shadow-sm max-w-3xl w-full self-center mt-6 mb-2">
      <Input
        type="text"
        placeholder="¿Tienes preguntas sobre la clase? Obtén respuesta inmediata"
        className="flex-1 bg-transparent outline-none text-white placeholder-zinc-400 text-base py-2 border-none shadow-none"
        value={value}
        onChange={e => setValue(e.target.value)}
      />
      <Button type="submit" className="ml-2 bg-white text-zinc-900 font-semibold px-5 py-2 rounded-xl hover:bg-zinc-200 transition">
        Preguntar
      </Button>
    </form>
  );
} 