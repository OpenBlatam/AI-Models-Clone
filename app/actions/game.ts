'use server';

import { auth } from "@/auth";
import { prisma } from "@/lib/db";
import { revalidatePath } from "next/cache";

export async function updateProgress(exerciseId: string, points: number) {
  try {
    const session = await auth();
    if (!session?.user?.id) {
      throw new Error("Unauthorized");
    }

    // Get current user progress
    const userProgress = await prisma.userProgress.findUnique({
      where: { userId: session.user.id },
    });

    if (!userProgress) {
      // Create new user progress if it doesn't exist
      await prisma.userProgress.create({
        data: {
          userId: session.user.id,
          experience: points,
          level: 1,
          streak: 1,
          lastActive: new Date(),
        },
      });
    } else {
      // Calculate new experience and level
      const newExperience = userProgress.experience + points;
      const newLevel = Math.floor(newExperience / 1000) + 1;

      // Update streak
      const lastActive = new Date(userProgress.lastActive);
      const today = new Date();
      const isConsecutiveDay =
        lastActive.getDate() === today.getDate() - 1 &&
        lastActive.getMonth() === today.getMonth() &&
        lastActive.getFullYear() === today.getFullYear();

      const newStreak = isConsecutiveDay ? userProgress.streak + 1 : 1;

      // Update user progress
      await prisma.userProgress.update({
        where: { userId: session.user.id },
        data: {
          experience: newExperience,
          level: newLevel,
          streak: newStreak,
          lastActive: new Date(),
        },
      });
    }

    // Revalidate the dashboard page to show updated data
    revalidatePath('/dashboard');
    
    return { success: true };
  } catch (error) {
    console.error("[PROGRESS_UPDATE]", error);
    return { success: false, error: "Failed to update progress" };
  }
} 