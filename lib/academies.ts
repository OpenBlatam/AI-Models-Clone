import { Academy, Resource } from "./types/academy";

export const academies: Academy[] = [
  {
    id: "ai-fundamentals",
    name: "Fundamentos de IA",
    description: "Aprende los conceptos básicos de la Inteligencia Artificial y sus aplicaciones prácticas.",
    thumbnail: "/images/academies/ai-fundamentals.jpg",
    instructor: "Dr. Ana Martínez",
    category: "Inteligencia Artificial",
    level: "beginner",
    totalClasses: 12,
    totalDuration: "8 horas",
    experience: 1000,
    s3Config: {
      bucketName: process.env.AWS_S3_AI_BUCKET_NAME!,
      clientKey: process.env.AWS_S3_AI_CLIENT_KEY!,
      region: process.env.AWS_REGION!,
    },
    classes: [
      {
        id: "ai-fundamentals-1",
        academyId: "ai-fundamentals",
        title: "Introducción a la IA",
        description: "Conceptos básicos y evolución de la Inteligencia Artificial",
        videoUrl: "/videos/ai-fundamentals/intro.mp4",
        thumbnail: "/images/academies/ai-fundamentals/intro.jpg",
        duration: "45:00",
        order: 1,
        isCompleted: false,
        progress: 0,
        experience: 100,
        resources: [
          {
            id: "ai-fundamentals-1-resource-1",
            type: "pdf",
            title: "Guía de Introducción a la IA",
            url: "/resources/ai-fundamentals/intro-guide.pdf"
          },
          {
            id: "ai-fundamentals-1-resource-2",
            type: "link",
            title: "Artículo: Historia de la IA",
            url: "https://example.com/ai-history"
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: "ai-fundamentals-2",
        academyId: "ai-fundamentals",
        title: "Machine Learning Básico",
        description: "Fundamentos de Machine Learning y sus aplicaciones",
        videoUrl: "/videos/ai-fundamentals/ml-basics.mp4",
        thumbnail: "/images/academies/ai-fundamentals/ml-basics.jpg",
        duration: "60:00",
        order: 2,
        isCompleted: false,
        progress: 0,
        experience: 150,
        resources: [
          {
            id: "ai-fundamentals-2-resource-1",
            type: "pdf",
            title: "Guía de Machine Learning",
            url: "/resources/ai-fundamentals/ml-guide.pdf"
          },
          {
            id: "ai-fundamentals-2-resource-2",
            type: "code",
            title: "Ejemplos de ML",
            url: "https://github.com/example/ml-examples"
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "chatgpt-mastery",
    name: "Dominando ChatGPT",
    description: "Aprende a aprovechar al máximo ChatGPT para mejorar tu productividad y creatividad.",
    thumbnail: "/images/academies/chatgpt-mastery.jpg",
    instructor: "Carlos Rodríguez",
    category: "ChatGPT",
    level: "intermediate",
    totalClasses: 15,
    totalDuration: "10 horas",
    experience: 1500,
    s3Config: {
      bucketName: process.env.AWS_S3_CHATGPT_BUCKET_NAME!,
      clientKey: process.env.AWS_S3_CHATGPT_CLIENT_KEY!,
      region: process.env.AWS_REGION!,
    },
    classes: [
      {
        id: "chatgpt-mastery-1",
        academyId: "chatgpt-mastery",
        title: "Introducción a ChatGPT",
        description: "Conoce las capacidades y limitaciones de ChatGPT",
        videoUrl: "/videos/chatgpt-mastery/intro.mp4",
        thumbnail: "/images/academies/chatgpt-mastery/intro.jpg",
        duration: "30:00",
        order: 1,
        isCompleted: false,
        progress: 0,
        experience: 100,
        resources: [
          {
            id: "chatgpt-mastery-1-resource-1",
            type: "pdf",
            title: "Guía de ChatGPT",
            url: "/resources/chatgpt-mastery/chatgpt-guide.pdf"
          },
          {
            id: "chatgpt-mastery-1-resource-2",
            type: "link",
            title: "Documentación Oficial",
            url: "https://platform.openai.com/docs"
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: "chatgpt-mastery-2",
        academyId: "chatgpt-mastery",
        title: "Prompt Engineering",
        description: "Aprende a escribir prompts efectivos",
        videoUrl: "/videos/chatgpt-mastery/prompt-engineering.mp4",
        thumbnail: "/images/academies/chatgpt-mastery/prompt-engineering.jpg",
        duration: "45:00",
        order: 2,
        isCompleted: false,
        progress: 0,
        experience: 150,
        resources: [
          {
            id: "chatgpt-mastery-2-resource-1",
            type: "pdf",
            title: "Guía de Prompt Engineering",
            url: "/resources/chatgpt-mastery/prompt-guide.pdf"
          },
          {
            id: "chatgpt-mastery-2-resource-2",
            type: "code",
            title: "Ejemplos de Prompts",
            url: "https://github.com/example/prompt-examples"
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: "midjourney-creator",
    name: "Creación con Midjourney",
    description: "Domina la creación de imágenes con IA usando Midjourney.",
    thumbnail: "/images/academies/midjourney-creator.jpg",
    instructor: "Laura Sánchez",
    category: "Generación de Imágenes",
    level: "beginner",
    totalClasses: 10,
    totalDuration: "6 horas",
    experience: 1200,
    s3Config: {
      bucketName: process.env.AWS_S3_MIDJOURNEY_BUCKET_NAME!,
      clientKey: process.env.AWS_S3_MIDJOURNEY_CLIENT_KEY!,
      region: process.env.AWS_REGION!,
    },
    classes: [
      {
        id: "midjourney-creator-1",
        academyId: "midjourney-creator",
        title: "Introducción a Midjourney",
        description: "Conoce la interfaz y comandos básicos",
        videoUrl: "/videos/midjourney-creator/intro.mp4",
        thumbnail: "/images/academies/midjourney-creator/intro.jpg",
        duration: "30:00",
        order: 1,
        isCompleted: false,
        progress: 0,
        experience: 100,
        resources: [
          {
            id: "midjourney-creator-1-resource-1",
            type: "pdf",
            title: "Guía de Midjourney",
            url: "/resources/midjourney-creator/midjourney-guide.pdf"
          },
          {
            id: "midjourney-creator-1-resource-2",
            type: "link",
            title: "Documentación Oficial",
            url: "https://docs.midjourney.com"
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: "midjourney-creator-2",
        academyId: "midjourney-creator",
        title: "Prompting Avanzado",
        description: "Técnicas avanzadas de prompting para mejores resultados",
        videoUrl: "/videos/midjourney-creator/advanced-prompting.mp4",
        thumbnail: "/images/academies/midjourney-creator/advanced-prompting.jpg",
        duration: "45:00",
        order: 2,
        isCompleted: false,
        progress: 0,
        experience: 150,
        resources: [
          {
            id: "midjourney-creator-2-resource-1",
            type: "pdf",
            title: "Guía de Prompting Avanzado",
            url: "/resources/midjourney-creator/advanced-prompting-guide.pdf"
          },
          {
            id: "midjourney-creator-2-resource-2",
            type: "code",
            title: "Ejemplos de Prompts",
            url: "https://github.com/example/midjourney-examples"
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export function getAcademyById(id: string): Academy | undefined {
  return academies.find((academy) => academy.id === id);
}

export function getAcademiesByCategory(category: string): Academy[] {
  return academies.filter((academy) => academy.category === category);
}

export function getAcademiesByLevel(level: string): Academy[] {
  return academies.filter((academy) => academy.level === level);
} 