import { Card, CardContent } from '@/components/ui/card'
import { Sparkles, Zap, Shield, TrendingUp } from 'lucide-react'

const features = [
  {
    icon: Sparkles,
    title: 'IA Avanzada',
    description: 'Generación inteligente de diseños con IA',
  },
  {
    icon: Zap,
    title: 'Rápido',
    description: 'Diseños completos en minutos',
  },
  {
    icon: Shield,
    title: 'Seguro',
    description: 'Tus datos están protegidos',
  },
  {
    icon: TrendingUp,
    title: 'Análisis',
    description: 'Métricas y análisis detallados',
  },
]

export function FeatureHighlights() {
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
      {features.map((feature, idx) => {
        const Icon = feature.icon
        return (
          <Card key={idx} className="text-center">
            <CardContent className="p-6">
              <Icon className="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}


