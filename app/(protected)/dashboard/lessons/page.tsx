import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { DashboardHeader } from "@/components/dashboard/header";
import { LessonsContent } from "@/components/dashboard/lessons-content";
import { createLessonCompletedNotification } from "@/lib/notifications";

export default async function LessonsPage() {
  const session = await auth();
  const user = session?.user;

  if (!user) {
    return null;
  }

  // Get user progress
  const userProgress = await prisma.userProgress.findUnique({
    where: { userId: user.id },
    include: {
      completedLessons: true
    }
  });

  // Get all lessons with their exercises
  const lessons = await prisma.lesson.findMany({
    include: {
      exercises: true
    }
  });

  // Create notifications for completed lessons
  if (userProgress) {
    for (const lesson of userProgress.completedLessons) {
      await createLessonCompletedNotification({ userId: user.id!, lessonTitle: lesson.title });
    }
  }

  return (
    <div className="flex flex-col gap-8 p-8">
      <DashboardHeader 
        heading="Lecciones"
        text="Explora y completa lecciones para ganar experiencia y subir de nivel."
      />
      <LessonsContent 
        lessons={lessons} 
        userLevel={userProgress?.level || 1} 
      />
    </div>
  );
} 