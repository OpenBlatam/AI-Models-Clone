'use client';

import { useState } from 'react';
import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Icons } from "@/components/shared/icons";
import { cn } from "@/lib/utils";
import { LessonContent } from "./lesson-content";

interface Exercise {
  id: string;
  type: string;
  question: string;
  options: string[];
  correctAnswer: string;
  points: number;
}

interface Lesson {
  id: string;
  title: string;
  description: string;
  requiredLevel: number;
  experienceReward: number;
  exercises: Exercise[];
}

interface LessonsContentProps {
  lessons: Lesson[];
  userLevel: number;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export function LessonsContent({ lessons, userLevel }: LessonsContentProps) {
  const [selectedLesson, setSelectedLesson] = useState<Lesson | null>(null);

  const handleLessonClick = (lesson: Lesson) => {
    if (lesson.requiredLevel <= userLevel) {
      setSelectedLesson(lesson);
    }
  };

  const handleLessonComplete = () => {
    setSelectedLesson(null);
  };

  if (selectedLesson) {
    return (
      <div className="p-8 pt-6">
        <LessonContent lesson={selectedLesson} onComplete={handleLessonComplete} />
      </div>
    );
  }

  return (
    <motion.div 
      className="space-y-4 p-8 pt-6"
      variants={container}
      initial="hidden"
      animate="show"
    >
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {lessons.map((lesson) => {
          const isLocked = lesson.requiredLevel > userLevel;
          
          return (
            <motion.div key={lesson.id} variants={item}>
              <Card 
                className={cn(
                  "relative overflow-hidden cursor-pointer transition-all hover:shadow-md",
                  isLocked && "opacity-50 cursor-not-allowed"
                )}
                onClick={() => handleLessonClick(lesson)}
              >
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {lesson.title}
                  </CardTitle>
                  {isLocked ? (
                    <Icons.lock className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Icons.bookOpen className="h-4 w-4 text-primary" />
                  )}
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground mb-4">
                    {lesson.description}
                  </p>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <Icons.target className="h-3 w-3 text-muted-foreground" />
                      <span>Nivel {lesson.requiredLevel}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Icons.star className="h-3 w-3 text-yellow-500" />
                      <span>{lesson.experienceReward} XP</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
} 