'use client';

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Icons } from "@/components/shared/icons";
import { cn } from "@/lib/utils";

interface LearningPath {
  id: string;
  title: string;
  description: string;
  icon: keyof typeof Icons;
  color: string;
  lessons: number;
  xp: number;
}

interface AcademyContentProps {
  learningPaths: LearningPath[];
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

export function AcademyContent({ learningPaths }: AcademyContentProps) {
  return (
    <motion.div 
      className="space-y-4 p-8 pt-6"
      variants={container}
      initial="hidden"
      animate="show"
    >
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {learningPaths.map((path) => {
          const Icon = Icons[path.icon];
          
          return (
            <motion.div key={path.id} variants={item}>
              <Card className="relative overflow-hidden">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {path.title}
                  </CardTitle>
                  <Icon className={cn("h-4 w-4", path.color)} />
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground mb-4">
                    {path.description}
                  </p>
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <Icons.bookOpen className="h-3 w-3 text-muted-foreground" />
                      <span>{path.lessons} lecciones</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Icons.star className="h-3 w-3 text-yellow-500" />
                      <span>{path.xp} XP</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <motion.div variants={item} className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Recomendaciones</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <Icons.target className="h-5 w-5 text-primary" />
                <div>
                  <h4 className="text-sm font-medium">Objetivos Diarios</h4>
                  <p className="text-xs text-muted-foreground">
                    Completa al menos 3 lecciones al día para mantener tu racha.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Icons.trophy className="h-5 w-5 text-yellow-500" />
                <div>
                  <h4 className="text-sm font-medium">Logros</h4>
                  <p className="text-xs text-muted-foreground">
                    Desbloquea logros especiales completando rutas de aprendizaje.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Icons.star className="h-5 w-5 text-blue-500" />
                <div>
                  <h4 className="text-sm font-medium">Experiencia</h4>
                  <p className="text-xs text-muted-foreground">
                    Gana XP completando lecciones y sube de nivel.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
} 