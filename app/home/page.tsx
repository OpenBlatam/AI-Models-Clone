"use client";

import "@/styles/globals.css";
import { HomeHeader } from "@/components/home/HomeHeader";
import { HeroSection } from "@/components/home/HeroSection";
import { Divider } from "@/components/home/Divider";
import { ProblemSolutionSection } from "@/components/home/ProblemSolutionSection";
import { AchievementsSection } from "@/components/home/AchievementsSection";
import { PopularCoursesSection } from "@/components/home/PopularCoursesSection";
import { LogoMarqueeSection } from "@/components/home/LogoMarqueeSection";
import { PlatformSection } from "@/components/home/PlatformSection";
import { FeatureCardsSection } from "@/components/home/FeatureCardsSection";
import { HomeFooter } from "@/components/home/HomeFooter";

export default function HomePage() {
  return (
    <>
      <HomeHeader />
      <main
        className="min-h-screen flex flex-col items-center justify-center px-4 py-20 w-full"
        style={{ background: "linear-gradient(135deg, #F3F7FF 0%, #E3D6FF 100%)" }}
      >
        <HeroSection />
        <Divider />
        <ProblemSolutionSection />
        <AchievementsSection />
        <PopularCoursesSection />
        <LogoMarqueeSection />
        <PlatformSection />
        <FeatureCardsSection />
      </main>
      <HomeFooter />
    </>
  );
}




