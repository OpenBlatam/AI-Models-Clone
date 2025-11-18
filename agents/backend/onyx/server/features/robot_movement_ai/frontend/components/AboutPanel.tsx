'use client';

import { Info, Code, Users, Heart, ExternalLink } from 'lucide-react';

export default function AboutPanel() {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-6">
          <Info className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Acerca de</h3>
        </div>

        {/* App Info */}
        <div className="mb-6">
          <h4 className="text-xl font-bold text-white mb-2">Robot Movement AI</h4>
          <p className="text-gray-300 mb-4">
            Plataforma enterprise completa para el control y monitoreo de robots con capacidades
            avanzadas de IA, visualización 3D, análisis predictivo y mucho más.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-400">Versión</p>
              <p className="text-white font-mono">1.0.0</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">Build</p>
              <p className="text-white font-mono">2024.01.15</p>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-white mb-3">Características Principales</h4>
          <ul className="space-y-2">
            <li className="flex items-center gap-2 text-gray-300">
              <Code className="w-4 h-4 text-primary-400" />
              Control en tiempo real del robot
            </li>
            <li className="flex items-center gap-2 text-gray-300">
              <Code className="w-4 h-4 text-primary-400" />
              Visualización 3D interactiva
            </li>
            <li className="flex items-center gap-2 text-gray-300">
              <Code className="w-4 h-4 text-primary-400" />
              Análisis predictivo con IA
            </li>
            <li className="flex items-center gap-2 text-gray-300">
              <Code className="w-4 h-4 text-primary-400" />
              Colaboración en tiempo real
            </li>
            <li className="flex items-center gap-2 text-gray-300">
              <Code className="w-4 h-4 text-primary-400" />
              Sistema de reportes avanzado
            </li>
            <li className="flex items-center gap-2 text-gray-300">
              <Code className="w-4 h-4 text-primary-400" />
              PWA instalable
            </li>
          </ul>
        </div>

        {/* Tech Stack */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-white mb-3">Stack Tecnológico</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {['Next.js', 'React', 'TypeScript', 'Tailwind CSS', 'Three.js', 'Zustand', 'Recharts', 'Axios'].map((tech) => (
              <div
                key={tech}
                className="p-2 bg-gray-700/50 rounded border border-gray-600 text-center"
              >
                <p className="text-sm text-white">{tech}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Links */}
        <div className="space-y-3">
          <h4 className="text-lg font-semibold text-white">Enlaces</h4>
          <div className="space-y-2">
            <a
              href="#"
              className="flex items-center gap-2 p-3 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-primary-500 transition-colors"
            >
              <ExternalLink className="w-4 h-4 text-primary-400" />
              <span className="text-white">Documentación</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-2 p-3 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-primary-500 transition-colors"
            >
              <Users className="w-4 h-4 text-primary-400" />
              <span className="text-white">Soporte</span>
            </a>
            <a
              href="#"
              className="flex items-center gap-2 p-3 bg-gray-700/50 rounded-lg border border-gray-600 hover:border-primary-500 transition-colors"
            >
              <Heart className="w-4 h-4 text-primary-400" />
              <span className="text-white">Contribuir</span>
            </a>
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-6 pt-6 border-t border-gray-700 text-center">
          <p className="text-sm text-gray-400">
            © 2024 Robot Movement AI. Todos los derechos reservados.
          </p>
        </div>
      </div>
    </div>
  );
}


