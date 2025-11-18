/**
 * Home page component.
 * Landing page with navigation to Music Analyzer AI and Robot Movement AI.
 * Enhanced with better accessibility, SEO, and responsive design.
 */

import Link from 'next/link';
import { Music, Bot, Sparkles, ArrowRight } from 'lucide-react';
import { ROUTES } from '@/lib/constants';
import { ResponsiveContainer, ResponsiveGrid } from '@/components/ui';

/**
 * Feature card interface.
 */
interface FeatureCardProps {
  href: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  features: string[];
  gradientFrom: string;
  gradientTo: string;
  hoverGradientFrom: string;
  hoverGradientTo: string;
}

/**
 * Feature card component.
 */
function FeatureCard({
  href,
  title,
  description,
  icon: Icon,
  features,
  gradientFrom,
  gradientTo,
  hoverGradientFrom,
  hoverGradientTo,
}: FeatureCardProps) {
  return (
    <Link
      href={href}
      className="group relative overflow-hidden rounded-2xl bg-gradient-to-br p-8 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl focus:outline-none focus:ring-4 focus:ring-purple-400 focus:ring-offset-2 focus:ring-offset-purple-900"
      style={{
        background: `linear-gradient(to bottom right, ${gradientFrom}, ${gradientTo})`,
      }}
      aria-label={`Ir a ${title}`}
    >
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{
          background: `linear-gradient(to bottom right, ${hoverGradientFrom}, ${hoverGradientTo})`,
        }}
      />
      <div className="relative z-10">
        <Icon className="w-16 h-16 mb-4" aria-hidden="true" />
        <h2 className="text-3xl font-bold mb-3">{title}</h2>
        <p className="mb-4 opacity-90">{description}</p>
        <ul className="text-sm space-y-1 mb-6 opacity-90">
          {features.map((feature, index) => (
            <li key={index}>• {feature}</li>
          ))}
        </ul>
        <div className="flex items-center gap-2 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
          <span>Explorar</span>
          <ArrowRight className="w-4 h-4" aria-hidden="true" />
        </div>
      </div>
    </Link>
  );
}

/**
 * Home page component.
 * Provides landing page with feature cards.
 *
 * @returns Home page component
 */
export default function HomePage() {
  const features = [
    {
      href: ROUTES.MUSIC,
      title: 'Music Analyzer AI',
      description:
        'Analiza canciones, obtén insights musicales, coaching personalizado y recomendaciones inteligentes con IA.',
      icon: Music,
      features: [
        'Análisis de tonalidad y tempo',
        'Coaching musical personalizado',
        'Machine Learning avanzado',
        'Recomendaciones inteligentes',
      ],
      gradientFrom: '#9333ea',
      gradientTo: '#ec4899',
      hoverGradientFrom: '#7c3aed',
      hoverGradientTo: '#db2777',
    },
    {
      href: ROUTES.ROBOT,
      title: 'Robot Movement AI',
      description:
        'Controla robots mediante chat, planifica trayectorias, y gestiona movimientos con IA avanzada.',
      icon: Bot,
      features: [
        'Control mediante chat natural',
        'Planificación de trayectorias',
        'Sistema de routing inteligente',
        'Monitoreo en tiempo real',
      ],
      gradientFrom: '#16a34a',
      gradientTo: '#10b981',
      hoverGradientFrom: '#15803d',
      hoverGradientTo: '#059669',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <ResponsiveContainer className="py-16">
        <div className="text-center mb-16">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Sparkles
              className="w-12 h-12 text-purple-400"
              aria-hidden="true"
            />
            <h1 className="text-5xl sm:text-6xl font-bold text-white">
              Blatam Academy
            </h1>
          </div>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Plataforma de IA para Análisis Musical y Control Robótico
          </p>
        </div>

        <ResponsiveGrid
          cols={{ default: 1, md: 2 }}
          gap="lg"
          className="max-w-4xl mx-auto"
        >
          {features.map((feature) => (
            <FeatureCard key={feature.href} {...feature} />
          ))}
        </ResponsiveGrid>

        <div className="mt-16 text-center">
          <p className="text-gray-400" role="status">
            Selecciona una plataforma para comenzar
          </p>
        </div>
      </ResponsiveContainer>
    </div>
  );
}
