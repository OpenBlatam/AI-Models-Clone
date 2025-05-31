import React from "react";

const templates = [
  {
    id: 1,
    title: "Educativo Moderno",
    color: "#FF6FA5",
    image: "/template1.jpg",
  },
  {
    id: 2,
    title: "Tecnología Futurista",
    color: "#FFD6E0",
    image: "/template2.jpg",
  },
  {
    id: 3,
    title: "Negocios Minimal",
    color: "#B2F0F0",
    image: "/template3.jpg",
  },
  {
    id: 4,
    title: "Creativo Vibrante",
    color: "#F39AC1",
    image: "/template4.jpg",
  }
];

export function TemplateSelector({ onSelect }: { onSelect: (tpl: any) => void }) {
  return (
    <div className="mt-8">
      <h3 className="text-lg font-semibold mb-4">Elige un template para tu contenido</h3>
      <div className="flex gap-6 overflow-x-auto pb-2">
        {templates.map((tpl) => (
          <div
            key={tpl.id}
            className="rounded-2xl border-2 cursor-pointer min-w-[180px] max-w-[200px] p-2 flex flex-col items-center transition-all border-transparent hover:border-primary hover:shadow-lg"
            style={{ background: tpl.color }}
            onClick={() => onSelect(tpl)}
          >
            <img src={tpl.image} alt={tpl.title} className="rounded-xl w-full h-32 object-cover mb-2" />
            <div className="font-bold text-lg mb-1">{tpl.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
} 