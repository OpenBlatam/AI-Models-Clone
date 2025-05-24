"use client"

import { Card } from "@/components/ui/card"
import { motion } from "framer-motion"
import {
  Brain,
  Gamepad2,
  Puzzle,
  BarChart2,
  Layers,
  Target,
  Zap,
  Trophy,
  Lightbulb,
  Rocket
} from "lucide-react"
import Link from "next/link"

const gameCategories = [
  {
    title: "Juegos de Conocimiento",
    games: [
      {
        title: "Marketing Trivia",
        description: "Pon a prueba tus conocimientos de marketing con preguntas desafiantes",
        icon: Brain,
        color: "text-blue-500",
        href: "/dashboard/games/trivia"
      },
      {
        title: "Juego de Memoria",
        description: "Encuentra pares de conceptos de marketing",
        icon: Puzzle,
        color: "text-purple-500",
        href: "/dashboard/games/memory"
      },
      {
        title: "Juego de Relaciones",
        description: "Relaciona conceptos con sus definiciones",
        icon: Layers,
        color: "text-green-500",
        href: "/dashboard/games/match"
      }
    ]
  },
  {
    title: "Juegos de Habilidad",
    games: [
      {
        title: "Marketing Flappy",
        description: "Evita obstáculos mientras aprendes conceptos de marketing",
        icon: Gamepad2,
        color: "text-yellow-500",
        href: "/dashboard/games/flappy"
      },
      {
        title: "Simulador de Marketing",
        description: "Toma decisiones estratégicas como CMO y ve su impacto",
        icon: BarChart2,
        color: "text-red-500",
        href: "/dashboard/games/simulator"
      }
    ]
  },
  {
    title: "Juegos de Estrategia",
    games: [
      {
        title: "Drag & Drop",
        description: "Organiza elementos de marketing en el orden correcto",
        icon: Target,
        color: "text-indigo-500",
        href: "/dashboard/games/drag-drop"
      },
      {
        title: "Constructor de Productos",
        description: "Crea y personaliza productos virtuales",
        icon: Rocket,
        color: "text-pink-500",
        href: "/dashboard/games/product-builder"
      }
    ]
  }
]

export function GamesMenu() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Juegos de Marketing</h1>
        <p className="text-muted-foreground">
          Aprende marketing de forma divertida con estos juegos interactivos
        </p>
      </div>

      <div className="space-y-12">
        {gameCategories.map((category, categoryIndex) => (
          <div key={category.title}>
            <h2 className="text-2xl font-semibold mb-6">{category.title}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {category.games.map((game, gameIndex) => (
                <Link key={game.title} href={game.href}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: (categoryIndex * 3 + gameIndex) * 0.1 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-lg ${game.color} bg-opacity-10`}>
                          <game.icon className={`h-6 w-6 ${game.color}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg mb-1">{game.title}</h3>
                          <p className="text-sm text-muted-foreground">
                            {game.description}
                          </p>
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
} 