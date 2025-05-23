import { getCurrentUser } from "@/lib/session";
import { constructMetadata } from "@/lib/utils";
import { DashboardHeader } from "@/components/dashboard/header";
import { AcademyContent } from "@/components/dashboard/academy-content";
import { Icons } from "@/components/shared/icons";

export const metadata = constructMetadata({
  title: "Academy – Learning Platform",
  description: "Explora rutas de aprendizaje y cursos especializados.",
});

const learningPaths = [
  {
    id: "beginner",
    title: "Principiante",
    description: "Comienza tu viaje de aprendizaje con los conceptos básicos.",
    icon: "bookOpen" as keyof typeof Icons,
    color: "text-blue-500",
    lessons: 10,
    xp: 1000,
  },
  {
    id: "intermediate",
    title: "Intermedio",
    description: "Mejora tus habilidades con ejercicios más desafiantes.",
    icon: "target" as keyof typeof Icons,
    color: "text-green-500",
    lessons: 15,
    xp: 2000,
  },
  {
    id: "advanced",
    title: "Avanzado",
    description: "Domina conceptos avanzados y técnicas especializadas.",
    icon: "trophy" as keyof typeof Icons,
    color: "text-purple-500",
    lessons: 20,
    xp: 3000,
  },
];

export default async function AcademyPage() {
  const user = await getCurrentUser();
  if (!user?.id) return null;

  return (
    <>
      <DashboardHeader
        heading="Academy"
        text="Explora rutas de aprendizaje y cursos especializados."
      />
      <AcademyContent learningPaths={learningPaths} />
    </>
  );
} 