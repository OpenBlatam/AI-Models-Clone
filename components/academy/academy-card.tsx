"use client";

import { Academy } from "@/lib/types/academy";
import Link from "next/link";
import { motion } from "framer-motion";
import { Thumbnail } from "./thumbnail";
import { InstructorInfo } from "./instructor-info";
import { CourseMeta } from "./course-meta";

interface AcademyCardProps {
  academy: Academy;
  onSelect?: (academy: Academy) => void;
  variant?: "grid" | "list";
}

export function AcademyCard({ academy, onSelect, variant = "grid" }: AcademyCardProps) {
  const handleClick = () => {
    if (onSelect) {
      onSelect(academy);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className="group"
    >
      <Link href={`/academy/${academy.id}`} className="block">
        <div className={variant === "grid" ? "space-y-3" : "flex gap-4"}>
          <div className={variant === "grid" ? "w-full" : "w-64 flex-shrink-0"}>
            <Thumbnail
              src={academy.thumbnail}
              alt={academy.name}
              duration={academy.totalDuration}
            />
          </div>

          <div className={variant === "grid" ? "space-y-2" : "flex-1 space-y-3"}>
            <div className="space-y-1">
              <h3 className="font-semibold line-clamp-2 text-base">
                {academy.name}
              </h3>
              <p className="text-sm text-muted-foreground line-clamp-2">
                {academy.description}
              </p>
            </div>

            <InstructorInfo name={academy.instructor} />

            <CourseMeta
              level={academy.level}
              category={academy.category}
              totalClasses={academy.totalClasses}
              experience={academy.experience}
            />
          </div>
        </div>
      </Link>
    </motion.div>
  );
} 