import Link from 'next/link';
import { Music, Bot, Sparkles } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Sparkles className="w-12 h-12 text-purple-400" />
            <h1 className="text-6xl font-bold text-white">Blatam Academy</h1>
          </div>
          <p className="text-xl text-gray-300 mb-8">
            Plataforma de IA para Análisis Musical y Control Robótico
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Music Analyzer Card */}
          <Link
            href="/music"
            className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 p-8 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/50 to-pink-600/50 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative z-10">
              <Music className="w-16 h-16 mb-4" />
              <h2 className="text-3xl font-bold mb-3">Music Analyzer AI</h2>
              <p className="text-purple-100 mb-4">
                Analiza canciones, obtén insights musicales, coaching personalizado y recomendaciones inteligentes con IA.
              </p>
              <ul className="text-sm text-purple-100 space-y-1">
                <li>• Análisis de tonalidad y tempo</li>
                <li>• Coaching musical personalizado</li>
                <li>• Machine Learning avanzado</li>
                <li>• Recomendaciones inteligentes</li>
              </ul>
            </div>
          </Link>

          {/* Robot Movement Card */}
          <Link
            href="/robot"
            className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-600 to-emerald-600 p-8 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-green-600/50 to-emerald-600/50 opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="relative z-10">
              <Bot className="w-16 h-16 mb-4" />
              <h2 className="text-3xl font-bold mb-3">Robot Movement AI</h2>
              <p className="text-green-100 mb-4">
                Controla robots mediante chat, planifica trayectorias, y gestiona movimientos con IA avanzada.
              </p>
              <ul className="text-sm text-green-100 space-y-1">
                <li>• Control mediante chat natural</li>
                <li>• Planificación de trayectorias</li>
                <li>• Sistema de routing inteligente</li>
                <li>• Monitoreo en tiempo real</li>
              </ul>
            </div>
          </Link>
        </div>

        <div className="mt-16 text-center">
          <p className="text-gray-400">
            Selecciona una plataforma para comenzar
          </p>
        </div>
      </div>
    </div>
  );
}

