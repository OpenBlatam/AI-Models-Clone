"use client";
import { motion, AnimatePresence } from "framer-motion";
import { PlayCircle, Lock, CheckCircle2, Award, Clock } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

interface Class {
  id: string;
  title: string;
  duration: string;
  thumbnail: string;
  isLocked: boolean;
  isCompleted: boolean;
  progress: number;
  experience: number;
}

interface VideoSidebarProps {
  open: boolean;
  onClose: () => void;
  currentIndex: number;
  onSelect: (index: number) => void;
}

export default function VideoSidebar({ open, onClose, currentIndex, onSelect, classes }: VideoSidebarProps & { classes: any[] }) {
  return (
    <div className="bg-background rounded-xl border border-border p-4">
      <h2 className="text-lg font-semibold text-foreground mb-4">Lista de Clases</h2>
      <div className="space-y-4">
        {classes.map((classItem, index) => (
          <motion.div
            key={classItem.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`p-4 rounded-lg border border-border hover:bg-muted transition-all duration-300 cursor-pointer ${
              index === currentIndex ? "bg-muted" : ""
            }`}
            onClick={() => !classItem.isLocked && onSelect(index)}
          >
            <div className="flex items-center gap-4">
              {/* Thumbnail */}
              <motion.div 
                className="relative w-24 h-16 rounded-lg overflow-hidden flex-shrink-0"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              >
                <Image
                  src={classItem.thumbnail}
                  alt={classItem.title}
                  fill
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
                  {classItem.isLocked ? (
                    <Lock className="w-6 h-6 text-foreground" />
                  ) : (
                    <PlayCircle className="w-6 h-6 text-foreground" />
                  )}
                </div>
              </motion.div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-medium text-foreground truncate">
                    {classItem.title}
                  </h3>
                  {classItem.isCompleted && (
                    <CheckCircle2 className="w-4 h-4 text-primary flex-shrink-0" />
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <p className="text-xs text-muted-foreground">
                    Duración: {classItem.duration}
                  </p>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${classItem.progress}%` }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      className="bg-primary h-2 rounded-full"
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">{classItem.progress}%</span>
                </div>
                <motion.p 
                  className="text-xs text-primary mt-1 flex items-center gap-1"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                >
                  <Award className="w-4 h-4" />
                  +{classItem.experience} XP
                </motion.p>
              </div>

              {/* Status */}
              <div className="flex-shrink-0">
                {classItem.isLocked ? (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-muted text-muted-foreground">
                    Bloqueado
                  </span>
                ) : classItem.isCompleted ? (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-primary/20 text-primary">
                    Completado
                  </span>
                ) : (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-primary/20 text-primary">
                    Disponible
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
} 