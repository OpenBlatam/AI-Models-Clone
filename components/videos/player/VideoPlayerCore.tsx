"use client";
import React, { useRef, useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize2,
  Minimize,
  RotateCcw,
  RotateCw,
  ChevronsLeft,
  ChevronsRight
} from "lucide-react";

interface VideoPlayerCoreProps {
  videoUrl: string;
  autoPlay?: boolean;
  onTimeUpdate?: (currentTime: number) => void;
  onEnded?: () => void;
  onProgress?: (progress: number) => void;
  onError?: (error: string) => void;
}

const VideoPlayerCore: React.FC<VideoPlayerCoreProps> = ({
  videoUrl,
  autoPlay = true,
  onTimeUpdate,
  onEnded,
  onProgress,
  onError,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const controlsTimeoutRef = useRef<NodeJS.Timeout>();
  const playPromiseRef = useRef<Promise<void> | null>(null);
  const isPlayRequestedRef = useRef(false);
  const [playbackRate, setPlaybackRate] = useState(1);

  useEffect(() => {
    if (videoRef.current) {
      console.log("Loading new video URL:", videoUrl);
      setIsLoading(true);
      setError(null);
      videoRef.current.load();
    }
  }, [videoUrl]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    console.log("Setting up video event listeners");

    const handleLoadStart = () => {
      console.log("Video load started");
      setIsLoading(true);
    };

    const handleLoadedData = () => {
      console.log("Video data loaded");
      setIsLoading(false);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
      onTimeUpdate?.(video.currentTime);
      onProgress?.((video.currentTime / video.duration) * 100);
    };

    const handleDurationChange = () => {
      console.log("Duration changed:", video.duration);
      setDuration(video.duration);
    };

    const handleEnded = () => {
      console.log("Video ended");
      setIsPlaying(false);
      isPlayRequestedRef.current = false;
      onEnded?.();
    };

    const handleError = (e: Event) => {
      const videoElement = e.target as HTMLVideoElement;
      const error = videoElement.error;
      
      console.error("Video error:", error);
      
      let errorMessage = "Error al cargar el video. Por favor, intenta de nuevo.";
      
      if (error) {
        switch (error.code) {
          case MediaError.MEDIA_ERR_ABORTED:
            errorMessage = "La reproducción del video fue interrumpida.";
            break;
          case MediaError.MEDIA_ERR_NETWORK:
            errorMessage = "Error de red al cargar el video. Verifica tu conexión a internet.";
            break;
          case MediaError.MEDIA_ERR_DECODE:
            errorMessage = "El video no se puede reproducir porque está dañado o en un formato no soportado.";
            break;
          case MediaError.MEDIA_ERR_SRC_NOT_SUPPORTED:
            errorMessage = "El formato del video no es soportado por tu navegador.";
            break;
          default:
            errorMessage = `Error desconocido (código: ${error.code}). Por favor, intenta de nuevo.`;
        }
      }
      
      setError(errorMessage);
      onError?.(errorMessage);
      setIsLoading(false);
      setIsPlaying(false);
      isPlayRequestedRef.current = false;
    };

    const handleCanPlay = async () => {
      console.log("Video can play");
      setIsLoading(false);
      if (autoPlay && !isPlayRequestedRef.current) {
        try {
          console.log("Attempting autoplay");
          isPlayRequestedRef.current = true;
          await video.play();
          setIsPlaying(true);
          console.log("Autoplay successful");
        } catch (error) {
          console.error("Error playing video:", error);
          setError("Error al iniciar la reproducción. Por favor, intenta de nuevo.");
          setIsPlaying(false);
        } finally {
          isPlayRequestedRef.current = false;
        }
      }
    };

    const handleWaiting = () => {
      console.log("Video is waiting for data");
      setIsLoading(true);
    };

    const handlePlaying = () => {
      console.log("Video is playing");
      setIsLoading(false);
    };

    video.addEventListener("loadstart", handleLoadStart);
    video.addEventListener("loadeddata", handleLoadedData);
    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("durationchange", handleDurationChange);
    video.addEventListener("ended", handleEnded);
    video.addEventListener("error", handleError);
    video.addEventListener("canplay", handleCanPlay);
    video.addEventListener("waiting", handleWaiting);
    video.addEventListener("playing", handlePlaying);

    return () => {
      console.log("Cleaning up video event listeners");
      video.removeEventListener("loadstart", handleLoadStart);
      video.removeEventListener("loadeddata", handleLoadedData);
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("durationchange", handleDurationChange);
      video.removeEventListener("ended", handleEnded);
      video.removeEventListener("error", handleError);
      video.removeEventListener("canplay", handleCanPlay);
      video.removeEventListener("waiting", handleWaiting);
      video.removeEventListener("playing", handlePlaying);
    };
  }, [autoPlay, onTimeUpdate, onEnded, onProgress, onError]);

  // Add spacebar play/pause support
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" || e.key === " ") {
        e.preventDefault();
        togglePlay();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isPlaying]);

  const togglePlay = async () => {
    if (!videoRef.current) return;

    try {
      if (isPlayRequestedRef.current) {
        return; // Evitar múltiples solicitudes simultáneas
      }

      isPlayRequestedRef.current = true;

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
      isPlayRequestedRef.current = false;
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

  const skip = (seconds: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = Math.max(0, Math.min(duration, videoRef.current.currentTime + seconds));
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const changePlaybackRate = () => {
    const rates = [1, 1.25, 1.5, 2];
    const idx = rates.indexOf(playbackRate);
    const next = rates[(idx + 1) % rates.length];
    setPlaybackRate(next);
    if (videoRef.current) videoRef.current.playbackRate = next;
  };

  return (
    <div 
      className={cn(
        "relative w-full h-full bg-black",
        isFullscreen && "fixed inset-0 z-50"
      )}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setShowControls(false)}
    >
      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/90 text-white p-4">
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
          <p className="text-lg font-semibold mb-2">{error}</p>
          <Button
            variant="secondary"
            onClick={() => {
              setError(null);
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

      {/* Video Element */}
      <video
        ref={videoRef}
        className="w-full h-full"
        playsInline
        preload="auto"
        crossOrigin="anonymous"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      >
        {videoUrl && (
          <source 
            src={videoUrl} 
            type="video/mp4"
          />
        )}
        Tu navegador no soporta el elemento de video.
      </video>

      {/* Overlay Controls */}
      <AnimatePresence>
        {showControls && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none"
          />
        )}
      </AnimatePresence>

      {/* Video Controls */}
      <AnimatePresence>
        {showControls && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 flex flex-col justify-end p-4 z-10"
          >
            {/* Progress Bar */}
            <div className="w-full h-1 bg-white/30 rounded-full mb-2">
              <div 
                className="h-full rounded-full"
                style={{ width: `${(currentTime / duration) * 100}%`, background: '#ff0000' }}
              />
            </div>
            {/* Controls Row */}
            <div className="flex items-center justify-between w-full bg-black/70 rounded-lg px-4 py-2 shadow-lg backdrop-blur-md">
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={() => skip(-15)} className="text-white hover:text-[#ff0000] transition-colors"><RotateCcw className="h-7 w-7" /><span className="text-xs absolute ml-1">15</span></Button>
                <Button variant="ghost" size="icon" onClick={togglePlay} className="text-white hover:text-[#ff0000] transition-colors">{isPlaying ? <Pause className="h-7 w-7" /> : <Play className="h-7 w-7" />}</Button>
                <Button variant="ghost" size="icon" onClick={() => skip(15)} className="text-white hover:text-[#ff0000] transition-colors"><RotateCw className="h-7 w-7" /><span className="text-xs absolute ml-1">15</span></Button>
                <Button variant="ghost" size="icon" onClick={toggleMute} className="text-white hover:text-[#ff0000] transition-colors">{isMuted ? <VolumeX className="h-7 w-7" /> : <Volume2 className="h-7 w-7" />}</Button>
                <span className="text-white text-base font-mono min-w-[70px] text-center">{formatTime(currentTime)} / {formatTime(duration)}</span>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={changePlaybackRate} className="text-white hover:text-[#ff0000] transition-colors">{playbackRate}x</Button>
                <Button variant="ghost" size="icon" onClick={toggleFullscreen} className="text-white hover:text-[#ff0000] transition-colors">{isFullscreen ? <Minimize className="h-7 w-7" /> : <Maximize2 className="h-7 w-7" />}</Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default VideoPlayerCore; 