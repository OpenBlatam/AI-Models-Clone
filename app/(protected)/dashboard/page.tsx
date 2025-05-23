import { getCurrentUser } from "@/lib/session";
import { constructMetadata } from "@/lib/utils";
import { DashboardHeader } from "@/components/dashboard/header";
import { prisma } from "@/lib/db";
import { DashboardContent } from "@/components/dashboard/dashboard-content";

export const metadata = constructMetadata({
  title: "Dashboard – Learning Progress",
  description: "Track your learning progress and achievements.",
});

async function getWeeklyProgress(userId: string) {
  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay());

  const weeklyProgress = await prisma.userProgress.findMany({
    where: {
      userId,
      lastActive: {
        gte: startOfWeek,
      },
    },
    orderBy: {
      lastActive: 'asc',
    },
  });

  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  return days.map(day => {
    const progress = weeklyProgress.find(p => 
      new Date(p.lastActive).toLocaleDateString('en-US', { weekday: 'short' }) === day
    );
    return {
      day,
      xp: progress ? progress.experience : 0,
    };
  });
}

export default async function DashboardPage() {
  const user = await getCurrentUser();
  if (!user?.id) return null;

  const userProgress = await prisma.userProgress.findUnique({
    where: { userId: user.id },
    include: {
      achievements: true,
    },
  });

  const weeklyProgress = await getWeeklyProgress(user.id);

  const gameStats = {
    currentStreak: userProgress?.streak || 0,
    totalXP: userProgress?.experience || 0,
    level: userProgress?.level || 1,
    lessonsCompleted: userProgress?.achievements?.length || 0,
    dailyGoal: 50,
    dailyProgress: weeklyProgress[new Date().getDay()].xp,
    weeklyProgress,
  };

  return (
    <>
      <DashboardHeader
        heading="Learning Dashboard"
        text={`Welcome back, ${user?.name}! Track your progress and achievements.`}
      />
      <DashboardContent 
        gameStats={gameStats}
        achievements={userProgress?.achievements || []}
      />
    </>
  );
}
