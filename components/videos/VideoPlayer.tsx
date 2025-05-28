"use client";
import React from "react";
import Plyr from "plyr-react";
import "plyr-react/plyr.css";

interface VideoPlayerProps {
  src: string;
  poster?: string;
  onEnded?: () => void;
}

const VideoPlayer = ({ src, poster, onEnded }: VideoPlayerProps) => {
  return (
    <div className="w-full max-w-5xl aspect-video rounded-2xl overflow-hidden bg-zinc-900 shadow-xl border border-zinc-800 animate-fade-in">
      <Plyr
        source={{
          type: "video",
          sources: [
            { src, type: "video/mp4" },
          ],
          poster,
        }}
        options={{
          controls: [
            'play', 'rewind', 'fast-forward', 'progress', 'current-time',
            'mute', 'volume', 'settings', 'pip', 'airplay', 'fullscreen'
          ],
          settings: ['quality', 'speed', 'loop'],
          i18n: { speed: 'Velocidad', quality: 'Calidad', loop: 'Repetir' },
        }}
        onEnded={onEnded}
      />
      <style jsx global>{`
        .plyr--video {
          --plyr-color-main: #4ade80;
          background: #18181b;
        }
        .plyr__controls {
          border-radius: 0 0 1.5rem 1.5rem;
          background: rgba(24, 24, 27, 0.85);
          backdrop-filter: blur(8px);
          box-shadow: 0 4px 32px 0 #0004;
        }
        .plyr__progress {
          height: 8px !important;
        }
        .plyr__progress--played, .plyr__progress__buffer {
          background: linear-gradient(90deg, #4ade80 0%, #38bdf8 100%) !important;
          transition: width 0.2s;
        }
        .plyr__control {
          border-radius: 0.75rem;
          background: rgba(39, 39, 42, 0.7);
          transition: background 0.2s;
        }
        .plyr__control:focus, .plyr__control:hover {
          background: #4ade80 !important;
          color: #18181b !important;
        }
        .plyr__menu__container {
          border-radius: 1rem;
          background: #23272f;
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(24px);}
          to { opacity: 1; transform: translateY(0);}
        }
        .animate-fade-in { animation: fade-in 0.7s; }
      `}</style>
    </div>
  );
};

export default VideoPlayer; 