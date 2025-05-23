import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  // Create AI Marketing lesson
  const lesson = await prisma.lesson.upsert({
    where: { title: "Análisis de Campaña con IA" },
    update: {},
    create: {
      title: "Análisis de Campaña con IA",
      description: "Analiza una campaña de marketing real utilizando herramientas de IA para identificar patrones y oportunidades.",
      difficulty: "Intermedio",
      category: "Marketing con IA",
      requiredLevel: 1,
      experienceReward: 50,
      exercises: {
        create: [
          {
            type: "multiple_choice",
            question: "¿Cuál es el principal beneficio de usar IA para analizar campañas de marketing?",
            options: [
              "Reducir costos de personal",
              "Identificar patrones complejos y oportunidades ocultas",
              "Automatizar todas las decisiones de marketing",
              "Reemplazar completamente el análisis humano"
            ],
            correctAnswer: "Identificar patrones complejos y oportunidades ocultas",
            points: 25
          },
          {
            type: "multiple_choice",
            question: "¿Qué tipo de datos son más valiosos para el análisis de IA en marketing?",
            options: [
              "Solo datos demográficos",
              "Solo datos de ventas",
              "Datos estructurados y no estructurados combinados",
              "Solo datos de redes sociales"
            ],
            correctAnswer: "Datos estructurados y no estructurados combinados",
            points: 25
          }
        ]
      }
    },
    include: {
      exercises: true
    }
  });

  console.log("Created lesson:", lesson);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  }); 