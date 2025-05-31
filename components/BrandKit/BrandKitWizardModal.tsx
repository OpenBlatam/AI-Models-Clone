import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

const templates = [
  {
    id: 1,
    title: "Transformación y Oportunidades con IA",
    subtitle: "Explora el futuro de la IA en educación",
    color: "#FF6FA5",
    image: "/template1.jpg",
    cta: "Únete hoy"
  },
  {
    id: 2,
    title: "Únete a la revolución educativa",
    subtitle: "",
    color: "#FFD6E0",
    image: "/template2.jpg",
    cta: "Prepárate ya"
  },
  {
    id: 3,
    title: "Prepárate para el futuro con AI.",
    subtitle: "",
    color: "#B2F0F0",
    image: "/template3.jpg",
    cta: "Únete a Bitam hoy."
  },
  {
    id: 4,
    title: "¡Participa! Descubre las ventajas.",
    subtitle: "",
    color: "#F39AC1",
    image: "/template4.jpg",
    cta: "Únete ahora mismo!"
  }
];

export function BrandKitWizardModal({ open, onClose, onGenerate, brandKit }) {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Refine post details</DialogTitle>
          <div className="text-muted-foreground mb-2">Suggestions are based on your brand kit</div>
        </DialogHeader>
        <div className="mb-4">
          <div className="font-medium mb-2">Select a design you'd like to start with <span className="text-red-500">*</span></div>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {templates.map((tpl, idx) => (
              <div
                key={tpl.id}
                className={`rounded-2xl border-2 cursor-pointer min-w-[180px] max-w-[200px] p-2 flex flex-col items-center transition-all ${
                  selected === idx ? "border-primary shadow-lg" : "border-transparent"
                }`}
                style={{ background: tpl.color }}
                onClick={() => setSelected(idx)}
              >
                <img src={tpl.image} alt={tpl.title} className="rounded-xl w-full h-32 object-cover mb-2" />
                <div className="font-bold text-lg mb-1">{tpl.title}</div>
                <div className="text-sm mb-2">{tpl.subtitle}</div>
                <div className="text-xs font-medium mt-auto">{tpl.cta}</div>
              </div>
            ))}
          </div>
          <div className="text-right mt-2">
            <button className="text-primary text-sm font-medium hover:underline">See All Templates</button>
          </div>
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button
            disabled={selected === null}
            onClick={() => onGenerate(templates[selected!])}
          >
            Generate Post
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 