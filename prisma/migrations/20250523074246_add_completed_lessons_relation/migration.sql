-- CreateTable
CREATE TABLE "_LessonToUserProgress" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "_LessonToUserProgress_AB_unique" ON "_LessonToUserProgress"("A", "B");

-- CreateIndex
CREATE INDEX "_LessonToUserProgress_B_index" ON "_LessonToUserProgress"("B");

-- AddForeignKey
ALTER TABLE "_LessonToUserProgress" ADD CONSTRAINT "_LessonToUserProgress_A_fkey" FOREIGN KEY ("A") REFERENCES "Lesson"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_LessonToUserProgress" ADD CONSTRAINT "_LessonToUserProgress_B_fkey" FOREIGN KEY ("B") REFERENCES "UserProgress"("id") ON DELETE CASCADE ON UPDATE CASCADE;
