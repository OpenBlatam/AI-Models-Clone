import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { BookOpen } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface VideoResumenProps {
  resumen: string;
}

export function VideoResumen({ resumen }: VideoResumenProps) {
  return (
    <Card className="w-full max-w-5xl bg-zinc-900 border-zinc-800">
      <CardContent className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold">Resumen de la clase</h2>
        </div>
        
        <ScrollArea className="h-[400px] pr-4">
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown>{resumen}</ReactMarkdown>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
} 