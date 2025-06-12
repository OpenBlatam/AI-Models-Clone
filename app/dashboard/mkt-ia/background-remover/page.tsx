"use client";
import { useState, useRef } from "react";
import ToolLayout from "../ToolLayout";
import { X as LucideX } from "lucide-react";
import EditorWithAIChanges from "../EditorWithAIChanges";

export default function BackgroundRemoverPage() {
  const [note, setNote] = useState("");
  const [notes, setNotes] = useState<string[]>([]);
  const [image, setImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const addNote = () => {
    if (note.trim()) {
      setNotes([note, ...notes]);
      setNote("");
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (ev) => setImage(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (ev) => setImage(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  return (
    <ToolLayout
      title="Background Remover"
      description="Effortlessly remove backgrounds from any image"
      sidebar={
        <>
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">Image</label>
            <div
              className="flex flex-col items-center justify-center border-2 border-dashed border-violet-200 rounded-xl bg-violet-50/60 py-10 px-4 text-center cursor-pointer hover:border-violet-400 transition relative"
              onDrop={handleDrop}
              onDragOver={e => { e.preventDefault(); e.stopPropagation(); }}
              onClick={() => fileInputRef.current?.click()}
              style={{ minHeight: 180 }}
            >
              {image ? (
                <div className="relative w-full flex flex-col items-center">
                  <button
                    type="button"
                    aria-label="Remove image"
                    className="absolute top-0 right-0 bg-white/80 hover:bg-violet-100 text-violet-600 rounded-full p-1 shadow transition-all z-10"
                    style={{ transform: 'translate(40%, -40%)' }}
                    onClick={e => { e.stopPropagation(); setImage(null); }}
                  >
                    <LucideX className="w-5 h-5" />
                  </button>
                  <img src={image} alt="Preview" className="max-h-32 mb-2 rounded shadow" />
                </div>
              ) : (
                <>
                  <span className="mb-2 text-violet-400">
                    <svg xmlns='http://www.w3.org/2000/svg' className='mx-auto' width='32' height='32' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M12 16v-4m0 0V8m0 4h4m-4 0H8m12 4v1a3 3 0 01-3 3H7a3 3 0 01-3-3v-1a9 9 0 0118 0z' /></svg>
                  </span>
                  <span className="text-gray-400 text-sm">Drag & drop or <span className="text-violet-600 underline cursor-pointer">browse</span></span>
                  <span className="mt-4 text-xs text-gray-400">IMAGE</span>
                </>
              )}
              <input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
              />
            </div>
          </div>
          <button className="mt-auto bg-violet-600 hover:bg-violet-700 text-white font-semibold w-full py-3 rounded-xl transition">Generate now</button>
        </>
      }
    >
      <div className="flex items-center gap-4 mb-6">
        <h3 className="text-lg font-bold">Untitled Document</h3>
        <span className="bg-gray-100 text-gray-500 text-xs px-2 py-0.5 rounded">Normal text</span>
      </div>
      <div className="flex-1 border border-dashed border-gray-200 rounded-xl bg-white/80 flex flex-col p-6">
        <div className="mb-4 flex gap-2">
          <input
            type="text"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-violet-200"
            placeholder="Add a note..."
            value={note}
            onChange={e => setNote(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') addNote(); }}
          />
          <button
            onClick={addNote}
            className="bg-violet-600 hover:bg-violet-700 text-white px-4 py-2 rounded-lg font-semibold transition"
          >
            Add
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {notes.length === 0 ? (
            <div className="text-gray-400 text-center mt-8">No notes yet. Start by adding one!</div>
          ) : (
            <ul className="space-y-3">
              {notes.map((n, i) => (
                <li key={i} className="bg-violet-50 border border-violet-100 rounded-lg px-4 py-3 text-gray-700 shadow-sm">
                  {n}
                </li>
              ))}
            </ul>
          )}
          <EditorWithAIChanges />
        </div>
      </div>
    </ToolLayout>
  );
} 