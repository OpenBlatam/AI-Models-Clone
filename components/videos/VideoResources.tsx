import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileText, BookOpen, Download, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Resource {
  id: string;
  title: string;
  type: "file" | "reading";
  url: string;
  description?: string;
}

interface VideoResourcesProps {
  files: Resource[];
  readings: Resource[];
}

export function VideoResources({ files, readings }: VideoResourcesProps) {
  return (
    <div className="w-full max-w-5xl space-y-6">
      {/* Archivos */}
      <Card className="bg-zinc-900 border-zinc-800">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold">Archivos</h2>
          </div>
          
          <ScrollArea className="h-[200px] pr-4">
            <div className="space-y-4">
              {files.map((file) => (
                <div
                  key={file.id}
                  className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-blue-400" />
                    <div>
                      <h3 className="font-medium">{file.title}</h3>
                      {file.description && (
                        <p className="text-sm text-zinc-400">{file.description}</p>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="hover:bg-zinc-700"
                    onClick={() => window.open(file.url, "_blank")}
                  >
                    <Download className="w-5 h-5" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Lecturas */}
      <Card className="bg-zinc-900 border-zinc-800">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold">Lecturas</h2>
          </div>
          
          <ScrollArea className="h-[200px] pr-4">
            <div className="space-y-4">
              {readings.map((reading) => (
                <div
                  key={reading.id}
                  className="flex items-center justify-between p-3 bg-zinc-800 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <BookOpen className="w-5 h-5 text-blue-400" />
                    <div>
                      <h3 className="font-medium">{reading.title}</h3>
                      {reading.description && (
                        <p className="text-sm text-zinc-400">{reading.description}</p>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="hover:bg-zinc-700"
                    onClick={() => window.open(reading.url, "_blank")}
                  >
                    <ExternalLink className="w-5 h-5" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
} 