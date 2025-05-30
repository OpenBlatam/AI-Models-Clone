"use client";
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import VideoPlayerCore from "./player/VideoPlayerCore";
import { Academy, AcademyClass } from '@/lib/types/academy';
import { getAcademyById } from '@/lib/academies';
import { Button } from "@/components/ui/button";
import { ListVideo } from "lucide-react";
import ClassesModal from "./ClassesModal";
import VideoSidebar from "./VideoSidebar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import VideoComments from "./VideoComments";
import { VideoResources } from "./VideoResources";
import { VideoQuestionBar } from "./VideoQuestionBar";
import { toast } from "sonner";

interface VideoPlayerProps {
  courseId: string;
  classId?: string;
  onTimeUpdate?: (currentTime: number) => void;
  onEnded?: () => void;
  onProgress?: (progress: number) => void;
  autoPlay?: boolean;
  onSelectClass?: (classId: string) => void;
}

const VideoPlayer = ({ 
  courseId,
  classId,
  onTimeUpdate,
  onEnded,
  onProgress,
  autoPlay = true,
  onSelectClass,
}: VideoPlayerProps) => {
  const [isMounted, setIsMounted] = useState(false);
  const [showClasses, setShowClasses] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [academy, setAcademy] = useState<Academy | undefined>(undefined);
  const [classes, setClasses] = useState<AcademyClass[]>([]);
  const [showExperienceGained, setShowExperienceGained] = useState(false);
  const [gainedExperience, setGainedExperience] = useState(0);
  const [currentVideoUrl, setCurrentVideoUrl] = useState<string>("");

  useEffect(() => {
    setIsMounted(true);
    const currentAcademy = getAcademyById(courseId);
    if (currentAcademy) {
      setAcademy(currentAcademy);
      setClasses(currentAcademy.classes || []);
    }
  }, [courseId]);

  useEffect(() => {
    if (classId) {
      const currentClass = classes.find(c => c.id === classId);
      if (currentClass) {
        setCurrentIndex(classes.indexOf(currentClass));
        setCurrentVideoUrl(currentClass.videoUrl);
      }
    }
  }, [classId, classes]);

  const handleVideoEnded = () => {
    const currentClass = classes[currentIndex];
    const experience = currentClass.experience || 0;
    
    setGainedExperience(experience);
    setShowExperienceGained(true);

    const updatedClasses = classes.map((c, index) => {
      if (index === currentIndex) {
        return {
          ...c,
          progress: 100,
          isCompleted: true
        };
      }
      return c;
    });

    setClasses(updatedClasses);

    if (onEnded) {
      onEnded();
    }

    setTimeout(() => {
      setShowExperienceGained(false);
    }, 3000);
  };

  if (!isMounted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-5xl aspect-video rounded-xl overflow-hidden bg-black"
      />
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4">
      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Video Player Section */}
        <div className="lg:col-span-3 space-y-4">
          {/* Video Player */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full aspect-video rounded-xl overflow-hidden bg-black relative"
          >
            <VideoPlayerCore
              videoUrl={currentVideoUrl}
              autoPlay={autoPlay}
              onTimeUpdate={onTimeUpdate}
              onEnded={handleVideoEnded}
              onProgress={onProgress}
            />

            {/* Classes Button */}
            {classes.length > 0 && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="absolute top-4 right-4 z-10"
              >
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowClasses(true)}
                  className="bg-black/50 hover:bg-black/70 backdrop-blur-sm text-foreground border border-border transition-all duration-300 hover:scale-105"
                >
                  <ListVideo className="w-4 h-4 mr-2" />
                  Ver Clases
                </Button>
              </motion.div>
            )}
          </motion.div>

          {/* Video Info */}
          <div className="space-y-4">
            {/* Video Header */}
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <h1 className="text-2xl font-bold">
                  {classes[currentIndex]?.title || "Video"}
                </h1>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <span>{classes[currentIndex]?.views || 0} visualizaciones</span>
                  <span>•</span>
                  <span>{classes[currentIndex]?.duration || "00:00"}</span>
                  <span>•</span>
                  <span>{academy?.instructor || "Instructor"}</span>
                </div>
              </div>
            </div>

            {/* Interactive Sections */}
            <Tabs defaultValue="comments" className="w-full">
              <TabsList className="w-full justify-start">
                <TabsTrigger value="comments">
                  Comentarios
                </TabsTrigger>
                <TabsTrigger value="resources">
                  Recursos
                </TabsTrigger>
                <TabsTrigger value="questions">
                  Preguntas
                </TabsTrigger>
              </TabsList>

              <TabsContent value="comments" className="mt-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-background rounded-xl p-4 border border-border"
                >
                  <VideoComments videoId={classId || ""} courseId={courseId} />
                </motion.div>
              </TabsContent>

              <TabsContent value="resources" className="mt-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-background rounded-xl p-4 border border-border"
                >
                  <VideoResources 
                    videoId={classId || ""}
                    courseId={courseId}
                  />
                </motion.div>
              </TabsContent>

              <TabsContent value="questions" className="mt-4">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-background rounded-xl p-4 border border-border"
                >
                  <VideoQuestionBar 
                    onAsk={(question) => {
                      toast.success("Pregunta enviada correctamente");
                    }} 
                  />
                </motion.div>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <VideoSidebar
            open={true}
            onClose={() => {}}
            currentIndex={currentIndex}
            onSelect={(index) => {
              if (onSelectClass) {
                onSelectClass(classes[index].id);
              }
            }}
            classes={classes}
          />
        </div>
      </div>

      {/* Classes Modal */}
      <ClassesModal
        open={showClasses}
        onClose={() => setShowClasses(false)}
        classes={classes.map(c => ({
          id: c.id,
          title: c.title,
          duration: c.duration,
          thumbnail: c.thumbnail,
          isLocked: false,
          isCompleted: c.isCompleted,
          progress: c.progress,
          experience: c.experience
        }))}
        currentClassId={classId || ""}
        onSelectClass={(classId) => {
          if (onSelectClass) {
            onSelectClass(classId);
            setShowClasses(false);
          }
        }}
      />
    </div>
  );
};

export default VideoPlayer; 