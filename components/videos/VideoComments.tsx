import { useState, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { MessageSquare, Send } from "lucide-react";

export interface Comment {
  id: string;
  user: {
    name: string;
    image?: string | null;
  };
  content: string;
  createdAt: string;
}

interface VideoCommentsProps {
  comments: Comment[];
  onAddComment: (content: string) => void;
}

export function VideoComments({ comments, onAddComment }: VideoCommentsProps) {
  const [newComment, setNewComment] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newComment.trim()) {
      onAddComment(newComment);
      setNewComment("");
      if (textareaRef.current) textareaRef.current.style.height = "40px";
    }
  };

  // Auto-resize textarea
  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setNewComment(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = "40px";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <Card className="w-full max-w-5xl bg-transparent border-none shadow-none">
      <CardContent className="p-0">
        <div className="flex items-center gap-2 mb-4">
          <MessageSquare className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold">Comentarios</h2>
        </div>
        <ScrollArea className="h-[340px] pr-2 mb-4">
          <div className="space-y-4">
            {comments.map((comment) => (
              <div
                key={comment.id}
                className="flex gap-4 p-4 bg-zinc-800/80 rounded-xl border border-zinc-700 shadow-sm"
              >
                <Avatar className="w-12 h-12">
                  <AvatarImage src={comment.user.image || undefined} />
                  <AvatarFallback>
                    {(comment.user?.name?.slice(0, 2) || "??").toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-base text-white truncate">{comment.user.name}</span>
                    <span className="text-xs text-zinc-400">{new Date(comment.createdAt).toLocaleDateString()}</span>
                  </div>
                  <p className="mt-1 text-zinc-200 whitespace-pre-line break-words text-base leading-relaxed">{comment.content}</p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
        <form onSubmit={handleSubmit} className="flex gap-2 items-end bg-zinc-800/80 border border-zinc-700 rounded-xl p-3 mt-2 shadow-lg">
          <Avatar className="w-10 h-10">
            <AvatarImage src={undefined} />
            <AvatarFallback>YO</AvatarFallback>
          </Avatar>
          <div className="flex-1 flex items-end">
            <textarea
              ref={textareaRef}
              value={newComment}
              onChange={handleInput}
              placeholder="Comparte tu opinión o pregunta…"
              className="flex-1 resize-none bg-transparent outline-none text-white placeholder-zinc-400 text-base py-2 px-3 rounded-xl border-none min-h-[40px] max-h-[120px]"
              rows={1}
              maxLength={800}
              required
            />
            <Button
              type="submit"
              className="ml-2 bg-blue-600 hover:bg-blue-700 rounded-full p-3 shadow-lg flex-shrink-0"
              disabled={!newComment.trim()}
              aria-label="Enviar comentario"
            >
              <Send className="w-5 h-5" />
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
} 