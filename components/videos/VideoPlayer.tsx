"use client";
import React, { useEffect, useState, useRef } from "react";
import dynamic from "next/dynamic";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import * as Tooltip from "@radix-ui/react-tooltip";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as Slider from "@radix-ui/react-slider";
import { 
  ListVideo, 
  Maximize2, 
  Volume2, 
  VolumeX, 
  Settings, 
  Clock, 
  ChevronLeft, 
  ChevronRight, 
  Play, 
  Pause, 
  Minimize,
  ThumbsUp,
  Share2,
  BookmarkPlus,
  MoreVertical,
  Flag,
  MessageSquare,
  Trophy,
  Star
} from "lucide-react";
import { Button } from "@/components/ui/button";
import ClassesModal from "./ClassesModal";
import VideoHeader from "./VideoHeader";
import VideoComments from "./VideoComments";
import { VideoResources } from "./VideoResources";
import { VideoQuestionBar } from "./VideoQuestionBar";
import VideoSidebar from "./VideoSidebar";
import { toast } from "sonner";
import { Progress } from "@/components/ui/progress";
import { S3_CLIENT_BUCKET_URL } from '@/lib/aws-config';
import { Academy, AcademyClass } from '@/lib/types/academy';
import { getAcademyById } from '@/lib/academies';
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Dynamically import Plyr with no SSR
const Plyr = dynamic(() => import("plyr-react"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-zinc-900">
      <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
  ),
});

// Import Plyr CSS only on client side
if (typeof window !== "undefined") {
  require("plyr-react/plyr.css");
}

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
  const [isLoading, setIsLoading] = useState(true);
  const [isHovered, setIsHovered] = useState(false);
  const [showClasses, setShowClasses] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [academy, setAcademy] = useState<Academy | undefined>(undefined);
  const [classes, setClasses] = useState<AcademyClass[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [showResources, setShowResources] = useState(false);
  const [showQuestions, setShowQuestions] = useState(false);
  const playerRef = useRef<any>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [playbackRate, setPlaybackRate] = useState(1);
  const controlsTimeoutRef = useRef<NodeJS.Timeout>();
  const [isPlayRequested, setIsPlayRequested] = useState(false);
  const playPromiseRef = useRef<Promise<void> | null>(null);
  const [activeTab, setActiveTab] = useState("comments");
  const [videoError, setVideoError] = useState<string | null>(null);
  const [isVideoLoading, setIsVideoLoading] = useState(true);
  const [showExperienceGained, setShowExperienceGained] = useState(false);
  const [gainedExperience, setGainedExperience] = useState(0);

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
        setIsVideoLoading(true);
        setVideoError(null);
        
        if (videoRef.current) {
          if (!currentClass.videoUrl) {
            setVideoError("No se encontró la URL del video");
            setIsVideoLoading(false);
            return;
          }

          videoRef.current.src = currentClass.videoUrl;
          videoRef.current.load();

          videoRef.current.onerror = () => {
            setVideoError("Error al cargar el video. Por favor, intenta de nuevo.");
            setIsVideoLoading(false);
          };

          videoRef.current.onloadeddata = () => {
            setIsVideoLoading(false);
            if (autoPlay) {
              setIsPlayRequested(true);
            }
          };
        }
      }
    }
  }, [classId, classes, autoPlay]);

  useEffect(() => {
    if (playerRef.current) {
      setIsLoading(false);
      if (autoPlay) {
        playerRef.current.play();
        setIsPlaying(true);
      }
    }
  }, [autoPlay]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
      onTimeUpdate?.(video.currentTime);
      onProgress?.((video.currentTime / video.duration) * 100);
    };

    const handleDurationChange = () => {
      setDuration(video.duration);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      onEnded?.();
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("durationchange", handleDurationChange);
    video.addEventListener("ended", handleEnded);

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("durationchange", handleDurationChange);
      video.removeEventListener("ended", handleEnded);
    };
  }, [onTimeUpdate, onEnded, onProgress]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !isPlayRequested) return;

    const playVideo = async () => {
      try {
        if (playPromiseRef.current) {
          await playPromiseRef.current;
        }
        playPromiseRef.current = video.play();
        await playPromiseRef.current;
      } catch (error) {
        console.error("Error playing video:", error);
        setIsPlayRequested(false);
      } finally {
        playPromiseRef.current = null;
      }
    };

    playVideo();
  }, [isPlayRequested]);

  const handleNextVideo = () => {
    if (currentIndex < classes.length - 1) {
      setCurrentIndex(currentIndex + 1);
      if (onSelectClass) onSelectClass(classes[currentIndex + 1].id);
    }
  };

  const handlePreviousVideo = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      if (onSelectClass) onSelectClass(classes[currentIndex - 1].id);
    }
  };

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

    // Ocultar el mensaje después de 3 segundos
    setTimeout(() => {
      setShowExperienceGained(false);
    }, 3000);
  };

  const handlePlayerReady = (player: any) => {
    playerRef.current = player;
    setIsLoading(false);
    if (autoPlay) {
      player.play();
      setIsPlaying(true);
    }
  };

  const togglePlay = async () => {
    if (!videoRef.current) return;

    try {
      if (isPlaying) {
        await videoRef.current.pause();
        setIsPlaying(false);
      } else {
        if (playPromiseRef.current) {
          await playPromiseRef.current;
        }
        playPromiseRef.current = videoRef.current.play();
        await playPromiseRef.current;
        setIsPlaying(true);
      }
    } catch (error) {
      console.error("Error toggling play state:", error);
      setIsPlaying(false);
    } finally {
      playPromiseRef.current = null;
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0];
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setVolume(newVolume);
      setIsMuted(newVolume === 0);
    }
  };

  const handleSeek = (value: number[]) => {
    const newTime = value[0];
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      videoRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  const handleMouseMove = () => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false);
      }
    }, 3000);
  };

  if (!isMounted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-5xl aspect-video rounded-2xl overflow-hidden bg-zinc-900 shadow-xl border border-zinc-800"
      >
        <Image
          src={classes[currentIndex]?.thumbnail || "/images/default-thumbnail.jpg"}
          alt="Video thumbnail"
          fill
          className="object-cover"
          priority
        />
      </motion.div>
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
            className={cn(
              "w-full aspect-video rounded-xl overflow-hidden bg-background shadow-xl border border-border relative transition-all duration-300",
              isFullscreen && "fixed inset-0 z-50 max-w-none rounded-none"
            )}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            <video
              ref={videoRef}
              src={classes[currentIndex]?.videoUrl}
              poster={classes[currentIndex]?.thumbnail}
              className={cn(
                "w-full h-full object-cover",
                (isLoading || videoError) && "hidden"
              )}
              onClick={togglePlay}
              playsInline
              preload="metadata"
              onError={() => {
                setVideoError("Error al cargar el video. Por favor, intenta de nuevo.");
                setIsLoading(false);
              }}
              onLoadedData={() => {
                setIsLoading(false);
                if (autoPlay) {
                  setIsPlayRequested(true);
                }
              }}
            />

            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-zinc-900">
                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            )}

            {videoError && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-900 text-white p-4">
                <div className="text-red-500 mb-2">
                  <svg
                    className="w-12 h-12"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>
                <p className="text-lg font-semibold mb-2">{videoError}</p>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setVideoError(null);
                    setIsLoading(true);
                    if (videoRef.current) {
                      videoRef.current.load();
                    }
                  }}
                >
                  Reintentar
                </Button>
              </div>
            )}

            {/* Overlay Controls */}
            <AnimatePresence>
              {isHovered && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none"
                />
              )}
            </AnimatePresence>

            {/* Video Controls */}
            <div 
              className="absolute inset-0 flex flex-col justify-end p-4 z-10"
              onMouseMove={handleMouseMove}
            >
              {/* Progress Bar */}
              <div className="w-full mb-4">
                <Slider.Root
                  value={[currentTime]}
                  max={duration}
                  step={1}
                  onValueChange={handleSeek}
                  className="w-full"
                >
                  <Slider.Track className="relative h-2 bg-zinc-700 rounded-full">
                    <Slider.Range className="absolute h-full bg-primary rounded-full" />
                  </Slider.Track>
                  <Slider.Thumb className="block w-4 h-4 bg-white rounded-full hover:bg-zinc-100 focus:outline-none focus:ring-2 focus:ring-primary" />
                </Slider.Root>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={togglePlay}
                    className="text-white hover:text-white/80"
                  >
                    {isPlaying ? (
                      <Pause className="w-6 h-6" />
                    ) : (
                      <Play className="w-6 h-6" />
                    )}
                  </Button>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={toggleMute}
                      className="text-white hover:text-white/80"
                    >
                      {isMuted ? (
                        <VolumeX className="w-5 h-5" />
                      ) : (
                        <Volume2 className="w-5 h-5" />
                      )}
                    </Button>

                    <div className="w-24">
                      <Slider.Root
                        value={[volume]}
                        max={1}
                        step={0.1}
                        onValueChange={handleVolumeChange}
                        className="w-full"
                      >
                        <Slider.Track className="relative h-2 bg-zinc-700 rounded-full">
                          <Slider.Range className="absolute h-full bg-primary rounded-full" />
                        </Slider.Track>
                        <Slider.Thumb className="block w-4 h-4 bg-white rounded-full hover:bg-zinc-100 focus:outline-none focus:ring-2 focus:ring-primary" />
                      </Slider.Root>
                    </div>
                  </div>

                  <div className="text-sm text-white">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <DropdownMenu.Root>
                    <DropdownMenu.Trigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-white hover:text-white/80"
                      >
                        <Settings className="w-5 h-5" />
                      </Button>
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Content>
                      <DropdownMenu.Label>Velocidad de reproducción</DropdownMenu.Label>
                      {[0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2].map((rate) => (
                        <DropdownMenu.Item
                          key={rate}
                          onClick={() => setPlaybackRate(rate)}
                          className={cn(
                            "cursor-pointer",
                            playbackRate === rate && "bg-accent"
                          )}
                        >
                          {rate}x
                        </DropdownMenu.Item>
                      ))}
                    </DropdownMenu.Content>
                  </DropdownMenu.Root>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleFullscreen}
                    className="text-white hover:text-white/80"
                  >
                    {isFullscreen ? (
                      <Minimize className="w-5 h-5" />
                    ) : (
                      <Maximize2 className="w-5 h-5" />
                    )}
                  </Button>
                </div>
              </div>
            </div>

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

            {/* Experience Gained Animation */}
            <AnimatePresence>
              {showExperienceGained && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-background/90 backdrop-blur-sm p-6 rounded-xl shadow-lg border border-border z-50"
                >
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                      <Trophy className="w-8 h-8 text-primary" />
                    </div>
                    <div className="text-center">
                      <h3 className="text-xl font-bold mb-2">¡Felicidades!</h3>
                      <p className="text-muted-foreground mb-4">
                        Has completado esta clase
                      </p>
                      <div className="flex items-center gap-2 text-primary font-semibold">
                        <Star className="w-5 h-5" />
                        <span>+{gainedExperience} XP</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
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
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 mr-4">
                  {currentIndex > 0 && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="gap-2"
                      onClick={() => {
                        if (onSelectClass) {
                          onSelectClass(classes[currentIndex - 1].id);
                        }
                      }}
                    >
                      <ChevronLeft className="w-4 h-4" />
                      Clase Anterior
                    </Button>
                  )}
                  {currentIndex < classes.length - 1 && (
                    <Button 
                      variant="default" 
                      size="sm" 
                      className="gap-2"
                      onClick={() => {
                        if (onSelectClass) {
                          onSelectClass(classes[currentIndex + 1].id);
                        }
                      }}
                    >
                      Siguiente Clase
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  )}
                </div>
                <Button variant="outline" size="sm" className="gap-2">
                  <ThumbsUp className="w-4 h-4" />
                  Me gusta
                </Button>
                <Button variant="outline" size="sm" className="gap-2">
                  <Share2 className="w-4 h-4" />
                  Compartir
                </Button>
                <Button variant="outline" size="sm" className="gap-2">
                  <BookmarkPlus className="w-4 h-4" />
                  Guardar
                </Button>
                <DropdownMenu.Root>
                  <DropdownMenu.Trigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenu.Trigger>
                  <DropdownMenu.Content>
                    <DropdownMenu.Item className="gap-2">
                      <Flag className="w-4 h-4" />
                      Reportar
                    </DropdownMenu.Item>
                  </DropdownMenu.Content>
                </DropdownMenu.Root>
              </div>
            </div>

            <Separator />

            {/* Instructor Info */}
            <div className="flex items-start gap-4">
              <Avatar className="w-12 h-12">
                <AvatarImage src={academy?.instructorAvatar} />
                <AvatarFallback>
                  {academy?.instructor?.charAt(0)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">{academy?.instructor}</h3>
                    <p className="text-sm text-muted-foreground">
                      {academy?.instructorSubscribers || 0} suscriptores
                    </p>
                  </div>
                  <Button variant="secondary">Suscribirse</Button>
                </div>
                <p className="text-sm text-muted-foreground">
                  {classes[currentIndex]?.description}
                </p>
              </div>
            </div>

            {/* Progress and Navigation */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Badge variant="secondary">
                  Clase {currentIndex + 1} de {classes.length}
                </Badge>
                <div className="text-sm text-muted-foreground">
                  {classes[currentIndex]?.experience || 0} XP
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handlePreviousVideo}
                  disabled={currentIndex === 0}
                  className="rounded-full hover:bg-accent"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleNextVideo}
                  disabled={currentIndex === classes.length - 1}
                  className="rounded-full hover:bg-accent"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${classes[currentIndex]?.progress || 0}%` }}
              />
            </div>

            {/* Interactive Sections */}
            <Tabs defaultValue="comments" className="w-full">
              <TabsList className="w-full justify-start">
                <TabsTrigger value="comments" className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Comentarios
                </TabsTrigger>
                <TabsTrigger value="resources" className="flex items-center gap-2">
                  <ListVideo className="w-4 h-4" />
                  Recursos
                </TabsTrigger>
                <TabsTrigger value="questions" className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
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