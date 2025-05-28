"use client";
import { useState, useRef } from "react";
import { cn } from "@/lib/utils";
import { Flag, Languages, PlayCircle, ChevronDown, ChevronUp, Download, Link2, X, Video as VideoIcon, UploadCloud, Camera } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { VideoHeader } from "@/components/videos/VideoHeader";
import { VideoResumen } from "@/components/videos/VideoResumen";
import { VideoResources } from "@/components/videos/VideoResources";
import { VideoComments, Comment } from "@/components/videos/VideoComments";
import { VideoQuestionBar } from "@/components/videos/VideoQuestionBar";
import { useSession } from "next-auth/react";
import { VideoSidebar } from "@/components/videos/VideoSidebar";
import { CongratsModal } from "@/components/videos/CongratsModal";
import dynamic from "next/dynamic";
import NextClassModal from "@/components/videos/NextClassModal";

interface Video {
  id: string;
  title: string;
  subtitle: string;
  src: string;
  files: { name: string; url: string; }[];
  readings: { name: string; url: string; }[];
  resumen: {
    intro: string;
    body: string;
    extraTitle: string;
    extraBody: string;
  };
  comments: Comment[];
}

const videos: Video[] = [
  {
    id: "1",
    title: "Uso de Inteligencia Artificial en Finanzas Personales",
    subtitle: "Clase 1 de 15 • Curso Gratis de Introducción a la Inteligencia Artificial",
    src: "https://www.w3schools.com/html/mov_bbb.mp4",
    files: [
      { name: "glosario-curso-intro-ai.pdf", url: "/files/glosario-curso-intro-ai.pdf" },
    ],
    readings: [
      { name: "Curso de ChatGPT - Platzi", url: "https://platzi.com/cursos/chatgpt/" },
      { name: "¿Es seguro usar ChatGPT? | Curso de ChatGPT", url: "https://platzi.com/blog/seguridad-chatgpt/" },
      { name: "New ways to manage your data in ChatGPT | OpenAI", url: "https://openai.com/blog/new-ways-to-manage-your-data-in-chatgpt" },
    ],
    resumen: {
      intro: "¿Por qué la inteligencia artificial es imprescindible en el mundo actual?",
      body: "La inteligencia artificial (IA) es esencial en sectores como salud y finanzas. Su capacidad para analizar datos mejorando la eficiencia y la toma de decisiones. Su accesibilidad permite a profesionales potenciar su desarrollo personal y laboral.",
      extraTitle: "¿Qué cambio trajo noviembre del 2022 con ChatGPT?",
      extraBody: "En noviembre de 2022, ChatGPT revolucionó el acceso a la IA, permitiendo a millones de personas interactuar con modelos avanzados de lenguaje natural, democratizando el uso de la inteligencia artificial y acelerando su adopción en múltiples industrias."
    },
    comments: [
      {
        id: "1",
        user: {
          name: "Cesar Ortiz",
          image: null
        },
        content: "Me gusta este formato del curso, no es teoria y mas teoria , es explicar a traves de situaciones de la vida real , genial",
        createdAt: new Date(Date.now() - 6 * 30 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "2",
        user: {
          name: "Juan Carlos Quishpe",
          image: null
        },
        content: "• Propósito del curso:\n- Está dirigido a personas que creen que la IA es difícil, responsabilidad de otros o una moda pasajera.\n- Busca cambiar esa perspectiva, mostrando que la IA es accesible y no es temporal.",
        createdAt: new Date(Date.now() - 6 * 30 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ],
  },
  {
    id: "2",
    title: "Aplicaciones de IA en la Medicina Moderna",
    subtitle: "Clase 2 de 15 • Curso Gratis de Introducción a la Inteligencia Artificial",
    src: "https://www.w3schools.com/html/movie.mp4",
    files: [
      { name: "apuntes-medicina-ia.pdf", url: "/files/apuntes-medicina-ia.pdf" },
    ],
    readings: [
      { name: "IA en salud - OMS", url: "https://www.who.int/es/news-room/fact-sheets/detail/artificial-intelligence" },
      { name: "Machine Learning in Healthcare", url: "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6616181/" },
    ],
    resumen: {
      intro: "¿Cómo está revolucionando la IA la medicina moderna?",
      body: "La IA permite diagnósticos más precisos, tratamientos personalizados y una gestión eficiente de datos médicos. Está transformando la atención al paciente y la investigación clínica.",
      extraTitle: "¿Qué avances recientes destacan en IA médica?",
      extraBody: "El uso de IA en imágenes médicas, asistentes virtuales y análisis predictivo ha mejorado la detección temprana de enfermedades y la toma de decisiones clínicas en hospitales de todo el mundo."
    },
    comments: [
      {
        id: "3",
        user: {
          name: "Ana López",
          image: null
        },
        content: "Impresionante cómo la IA ayuda a los médicos a diagnosticar enfermedades más rápido.",
        createdAt: new Date(Date.now() - 2 * 30 * 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: "4",
        user: {
          name: "Carlos Pérez",
          image: null
        },
        content: "Me gustaría ver ejemplos prácticos de IA en hospitales latinoamericanos.",
        createdAt: new Date(Date.now() - 1 * 30 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ],
  },
];

const VideoPlayer = dynamic(() => import("@/components/videos/VideoPlayer"), { ssr: false });

export default function VideosPage() {
  const [tab, setTab] = useState("all");
  const [showMore, setShowMore] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [recording, setRecording] = useState(false);
  const [videoURL, setVideoURL] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunks = useRef<Blob[]>([]);
  const [videoIndex, setVideoIndex] = useState(0);
  const currentVideo = videos[videoIndex];
  const [comments, setComments] = useState<Comment[]>(currentVideo.comments);
  const { data: session } = useSession();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showCongrats, setShowCongrats] = useState(false);
  const [showNextModal, setShowNextModal] = useState(false);

  // WebRTC video recording logic
  const startRecording = async () => {
    setRecording(true);
    recordedChunks.current = [];
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    if (videoRef.current) videoRef.current.srcObject = stream;
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) recordedChunks.current.push(e.data);
    };
    mediaRecorder.onstop = () => {
      const blob = new Blob(recordedChunks.current, { type: "video/webm" });
      setVideoURL(URL.createObjectURL(blob));
      if (videoRef.current) videoRef.current.srcObject = null;
      stream.getTracks().forEach((track) => track.stop());
    };
    mediaRecorder.start();
  };
  const stopRecording = () => {
    setRecording(false);
    mediaRecorderRef.current?.stop();
  };
  const resetRecording = () => {
    setVideoURL(null);
    setShowUpload(false);
  };
  const handleUpload = () => {
    // Here you would upload the video blob to your backend
    alert("Video subido (simulado)");
    resetRecording();
  };
  const handleNextVideo = () => {
    setShowMore(false);
    setTab("all");
    setVideoIndex((idx) => (idx + 1) % videos.length);
  };
  const handlePreviousVideo = () => {
    setShowMore(false);
    setTab("all");
    setVideoIndex((idx) => (idx - 1 + videos.length) % videos.length);
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageUrl = canvas.toDataURL('image/jpeg');
        setCapturedImage(imageUrl);
      }
    }
  };

  const handleUploadPhoto = () => {
    if (capturedImage) {
      // Aquí podrías subir la imagen al backend
      // Por ahora solo la usaremos en los comentarios
      setShowUpload(false);
    }
  };

  const handleAddComment = async (content: string) => {
    const tempComment: Comment = {
      id: Math.random().toString(36).substr(2, 9),
      content,
      createdAt: new Date().toISOString(),
      user: {
        name: session?.user?.name || "Tú",
        image: session?.user?.image || null,
      },
    };
    setComments((prev) => [tempComment, ...prev]);

    // Send to API
    const res = await fetch(`/api/videos/${currentVideo.id}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, image: capturedImage }),
    });
    if (res.ok) {
      const newComment = await res.json();
      setComments((prev) => [newComment, ...prev.filter((c) => c.id !== tempComment.id)]);
    } else {
      // Remove temp comment on error
      setComments((prev) => prev.filter((c) => c.id !== tempComment.id));
      alert("Error al guardar el comentario");
    }
  };

  // Handler para cuando termina el video
  const handleVideoEnded = () => {
    if (videoIndex < videos.length - 1) {
      setShowNextModal(true);
    } else {
      setShowCongrats(true);
    }
  };

  const handleNextClass = () => {
    setShowNextModal(false);
    setVideoIndex(videoIndex + 1);
  };

  return (
    <div className="flex flex-col bg-zinc-900 min-h-screen text-white">
      <VideoHeader
        title={currentVideo.title}
        subtitle={currentVideo.subtitle}
        onNextVideo={handleNextVideo}
        onPreviousVideo={handlePreviousVideo}
        isFirstVideo={videoIndex === 0}
        onShowSidebar={() => setSidebarOpen(true)}
      />
      {/* Sidebar de clases */}
      <VideoSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        videos={videos}
        currentIndex={videoIndex}
        onSelect={(idx) => {
          setVideoIndex(idx);
          setSidebarOpen(false);
        }}
      />
      {/* Main Content */}
      <div className="flex flex-col md:flex-row flex-1">
        {/* Video Section */}
        <div className="w-full md:w-3/5 p-6 flex flex-col gap-4 justify-center">
          <div className="rounded-2xl overflow-hidden bg-black aspect-video w-full max-w-4xl mx-auto shadow-xl border border-zinc-800">
            <VideoPlayer
              src={currentVideo.src}
              onEnded={handleVideoEnded}
            />
            <NextClassModal
              open={showNextModal}
              onClose={() => setShowNextModal(false)}
              onNext={handleNextClass}
              currentTitle={currentVideo.title}
              nextTitle={videos[videoIndex + 1]?.title}
              nextThumbnail={videos[videoIndex + 1]?.thumbnail}
            />
          </div>
          <div className="flex items-center gap-2 mt-4">
            <button className="bg-green-500 text-black px-4 py-1 rounded font-semibold shadow">Ver planes</button>
            <span className="text-zinc-400 text-sm">Suscríbete para ver el curso completo</span>
          </div>
        </div>
        {/* Comments Section */}
        <div className="w-full md:w-2/5 p-4 border-l border-zinc-800 bg-zinc-950 flex flex-col">
          <div className="flex items-center gap-2 mb-2">
            <button onClick={() => setTab('all')}
              className={cn('px-2 py-1 rounded text-sm', tab === 'all' ? 'bg-zinc-800 text-white' : 'text-zinc-400')}>Todo</button>
            <button onClick={() => setTab('questions')}
              className={cn('px-2 py-1 rounded text-sm', tab === 'questions' ? 'bg-zinc-800 text-white' : 'text-zinc-400')}>Preguntas</button>
            <button onClick={() => setTab('contributions')}
              className={cn('px-2 py-1 rounded text-sm', tab === 'contributions' ? 'bg-zinc-800 text-white' : 'text-zinc-400')}>Aportes</button>
          </div>
          <VideoComments comments={comments} onAddComment={handleAddComment} />
        </div>
      </div>
      {/* Question Input Bar */}
      <div className="max-w-3xl w-full self-center mt-6 mb-2 px-4">
        <form className="flex items-center bg-zinc-900 border border-gradient-to-r from-purple-400 to-blue-400 rounded-2xl px-4 py-2 shadow-sm" onSubmit={e => { e.preventDefault(); }}>
          <input
            type="text"
            placeholder="¿Tienes preguntas sobre la clase? Obtén respuesta inmediata"
            className="flex-1 bg-transparent outline-none text-white placeholder-zinc-400 text-base py-2"
          />
          <button
            type="submit"
            className="ml-2 bg-white text-zinc-900 font-semibold px-5 py-2 rounded-xl hover:bg-zinc-200 transition"
          >
            Preguntar
          </button>
        </form>
      </div>
      {/* Resumen Section */}
      <div className="bg-zinc-800 rounded-xl mx-4 my-6 p-6 max-w-3xl w-full self-center shadow-lg">
        <div className="font-bold text-lg mb-2">Resumen</div>
        <div className="mb-4">
          <div className="font-semibold text-base mb-1">{currentVideo.resumen.intro}</div>
          <div className="text-zinc-200 text-lg mb-4">{currentVideo.resumen.body}</div>
        </div>
        <div className={cn("transition-all", showMore ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0 overflow-hidden")}> 
          <div className="font-bold text-lg mb-1">{currentVideo.resumen.extraTitle}</div>
          <div className="text-zinc-200 text-lg">{currentVideo.resumen.extraBody}</div>
        </div>
        <button
          className="mt-4 text-blue-400 hover:underline flex items-center gap-1 text-base"
          onClick={() => setShowMore((v) => !v)}
        >
          Continuar leyendo
          {showMore ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>
      {/* Resources Section */}
      <div className="bg-zinc-800 rounded-xl mx-4 my-6 p-6 max-w-3xl w-full self-center shadow-lg">
        <div className="font-bold text-lg mb-4">Archivos de la clase</div>
        {currentVideo.files.map((file) => (
          <div key={file.name} className="flex items-center gap-4 mb-4">
            <div className="bg-zinc-700 rounded-full p-3"><Download className="w-6 h-6 text-zinc-300" /></div>
            <span className="flex-1 text-base text-zinc-100">{file.name}</span>
            <a href={file.url} download className="ml-auto p-2 rounded-full hover:bg-zinc-700 transition" title="Descargar">
              <Download className="w-5 h-5 text-zinc-300" />
            </a>
          </div>
        ))}
        <div className="font-bold text-lg mt-8 mb-4">Lecturas recomendadas</div>
        {currentVideo.readings.map((reading) => (
          <div key={reading.url} className="flex items-center gap-4 mb-4">
            <div className="bg-zinc-700 rounded-full p-3"><Link2 className="w-6 h-6 text-zinc-300" /></div>
            <span className="flex-1 text-base text-zinc-100">{reading.name}</span>
            <a href={reading.url} target="_blank" rel="noopener noreferrer" className="ml-auto p-2 rounded-full hover:bg-zinc-700 transition" title="Abrir enlace">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 text-zinc-300">
                <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75V3.75a.75.75 0 00-.75-.75h-12a.75.75 0 00-.75.75v12a.75.75 0 00.75.75h3" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m0 0v3.75A.75.75 0 0015.75 21h6a.75.75 0 00.75-.75v-6a.75.75 0 00-.75-.75H18" />
              </svg>
            </a>
          </div>
        ))}
      </div>
      {/* Video Upload Section */}
      <div className="fixed bottom-8 right-8 z-50">
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full shadow-lg font-semibold"
        >
          <VideoIcon className="w-5 h-5" /> Subir video
        </button>
      </div>
      {showUpload && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70">
          <div className="bg-zinc-900 rounded-xl p-6 w-full max-w-md shadow-2xl relative flex flex-col items-center">
            <button onClick={resetRecording} className="absolute top-2 right-2 p-2 rounded-full hover:bg-zinc-800"><X className="w-5 h-5" /></button>
            <div className="mb-4 text-lg font-bold flex items-center gap-2">
              {capturedImage ? <Camera className="w-6 h-6" /> : <VideoIcon className="w-6 h-6" />} 
              {capturedImage ? "Foto capturada" : "Graba o sube tu video"}
            </div>
            <video ref={videoRef} autoPlay muted className="w-full rounded mb-4 bg-black aspect-video" src={videoURL || undefined} controls={!!videoURL} />
            <canvas ref={canvasRef} className="hidden" />
            {capturedImage && (
              <img src={capturedImage} alt="Captured" className="w-full rounded mb-4 aspect-video object-cover" />
            )}
            {!videoURL && !recording && !capturedImage && (
              <div className="flex gap-2">
                <button onClick={startRecording} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2">
                  <VideoIcon className="w-5 h-5" /> Iniciar grabación
                </button>
                <button onClick={capturePhoto} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2">
                  <Camera className="w-5 h-5" /> Tomar foto
                </button>
              </div>
            )}
            {recording && (
              <button onClick={stopRecording} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2">
                <VideoIcon className="w-5 h-5" /> Detener grabación
              </button>
            )}
            {videoURL && (
              <>
                <button onClick={handleUpload} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2">
                  <UploadCloud className="w-5 h-5" /> Subir video
                </button>
                <button onClick={resetRecording} className="bg-zinc-700 hover:bg-zinc-800 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2">
                  <X className="w-5 h-5" /> Cancelar
                </button>
              </>
            )}
            {capturedImage && (
              <>
                <button onClick={handleUploadPhoto} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2 mb-2">
                  <UploadCloud className="w-5 h-5" /> Usar foto
                </button>
                <button onClick={() => setCapturedImage(null)} className="bg-zinc-700 hover:bg-zinc-800 text-white px-4 py-2 rounded-full font-semibold flex items-center gap-2">
                  <X className="w-5 h-5" /> Cancelar
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 