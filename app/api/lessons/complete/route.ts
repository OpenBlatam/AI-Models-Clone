import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session?.user) {
      return new NextResponse("No autorizado", { status: 401 });
    }

    const { lessonId, score, experienceReward } = await req.json();

    // Obtener el progreso actual del usuario
    const userProgress = await prisma.userProgress.findUnique({
      where: { userId: session.user.id },
      include: {
        completedLessons: true
      }
    });

    if (!userProgress) {
      return new NextResponse("Progreso de usuario no encontrado", { status: 404 });
    }

    // Verificar si la lección ya fue completada
    const lessonAlreadyCompleted = userProgress.completedLessons.some(
      cl => cl.lessonId === lessonId
    );

    if (lessonAlreadyCompleted) {
      return new NextResponse("Lección ya completada", { status: 400 });
    }

    // Calcular la experiencia total y el nuevo nivel
    const currentExperience = userProgress.experience || 0;
    const newExperience = currentExperience + experienceReward;
    const currentLevel = userProgress.level || 1;
    const experienceForNextLevel = currentLevel * 1000; // 1000 XP por nivel
    const levelUp = newExperience >= experienceForNextLevel;
    const newLevel = levelUp ? currentLevel + 1 : currentLevel;

    // Actualizar el progreso del usuario
    const updatedProgress = await prisma.userProgress.update({
      where: { userId: session.user.id },
      data: {
        experience: newExperience,
        level: newLevel,
        completedLessons: {
          create: {
            lessonId: lessonId,
            completedAt: new Date(),
            score: score
          }
        }
      },
      include: {
        completedLessons: true
      }
    });

    return NextResponse.json({
      success: true,
      levelUp,
      newLevel,
      newExperience,
      completedLessons: updatedProgress.completedLessons.length
    });

  } catch (error) {
    console.error('Error al completar la lección:', error);
    return new NextResponse("Error interno del servidor", { status: 500 });
  }
} 