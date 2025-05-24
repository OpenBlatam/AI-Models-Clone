'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Icons } from "@/components/shared/icons";
import { cn } from "@/lib/utils";

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

interface LessonContentProps {
  lesson: Lesson;
  onComplete: () => void;
}

export function LessonContent({ lesson, onComplete }: LessonContentProps) {
  const [currentExercise, setCurrentExercise] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [score, setScore] = useState(0);
  const [isCompleted, setIsCompleted] = useState(false);

  const handleAnswerSelect = (answer: string) => {
    setSelectedAnswer(answer);
  };

  const handleNext = () => {
    if (selectedAnswer === lesson.exercises[currentExercise].correctAnswer) {
      setScore(score + lesson.exercises[currentExercise].points);
    }

    if (currentExercise < lesson.exercises.length - 1) {
      setCurrentExercise(currentExercise + 1);
      setSelectedAnswer(null);
    } else {
      setIsCompleted(true);
      onComplete();
    }
  };

  const exercise = lesson.exercises[currentExercise];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="space-y-6"
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-xl">{lesson.title}</CardTitle>
          <p className="text-sm text-muted-foreground">{lesson.description}</p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span>Ejercicio {currentExercise + 1} de {lesson.exercises.length}</span>
              <span>Puntuación: {score} XP</span>
            </div>

            <div className="space-y-4">
              <h3 className="font-medium">{exercise.question}</h3>
              <div className="grid gap-2">
                {exercise.options.map((option, index) => (
                  <Button
                    key={index}
                    variant={selectedAnswer === option ? "default" : "outline"}
                    className={cn(
                      "justify-start",
                      selectedAnswer === option && "bg-primary text-primary-foreground"
                    )}
                    onClick={() => handleAnswerSelect(option)}
                  >
                    {option}
                  </Button>
                ))}
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                onClick={handleNext}
                disabled={!selectedAnswer}
              >
                {currentExercise < lesson.exercises.length - 1 ? "Siguiente" : "Finalizar"}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <AnimatePresence>
        {isCompleted && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="text-center space-y-4"
          >
            <Icons.trophy className="h-12 w-12 text-yellow-500 mx-auto" />
            <h2 className="text-2xl font-bold">¡Felicidades!</h2>
            <p>Has completado la lección y ganado {score} XP</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
} 