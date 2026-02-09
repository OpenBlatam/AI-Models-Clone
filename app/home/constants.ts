export const NAV_LINKS = [
  { href: "/juegos", label: "Juegos" },
  { href: "/mkt-ia", label: "MKT IA" },
  { href: "/colab-ia", label: "Colab IA" },
  { href: "/ads-ia", label: "ADS IA" },
  { href: "/logros", label: "Logros" },
] as const;

export const PROFILE_MENU_LINKS = [
  {
    href: "/dashboard",
    label: "Dashboard",
    icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6",
  },
  {
    href: "/settings",
    label: "Configuración",
    icon: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z",
  },
  {
    href: "/billing",
    label: "Facturación",
    icon: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z",
  },
] as const;

export const ACHIEVEMENTS = [
  {
    icon: "M12 2L15.09 8.26L22 9.27L17 12.91L18.18 21L12 17.27L5.82 21L7 12.91L2 9.27L8.91 8.26L12 2Z",
    value: "10K+",
    description: "Estudiantes formados en IA",
  },
  {
    icon: "M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11ZM23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13ZM16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88",
    value: "3K+",
    description: "Empresas confían en nosotros",
  },
  {
    icon: "M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22ZM12 6V12L16 14",
    value: "98%",
    description: "Tasa de satisfacción",
  },
] as const;

export const POPULAR_COURSES = [
  {
    title: "Introducción a la IA",
    description: "Aprende los conceptos básicos de la inteligencia artificial y sus aplicaciones.",
    href: "/cursos/intro-ia",
  },
  {
    title: "IA para Negocios",
    description: "Descubre cómo la IA puede transformar tu empresa y tus procesos.",
    href: "/cursos/ia-negocios",
  },
  {
    title: "Prompt Engineering",
    description: "Domina la creación de prompts efectivos para modelos de lenguaje.",
    href: "/cursos/prompt-engineering",
  },
] as const;

export const FEATURE_CARDS = [
  {
    title: "b Studio",
    icon: (
      <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
        <rect x="4" y="4" width="16" height="16" rx="3" stroke="#FFD700" strokeWidth="2" />
        <rect x="8" y="8" width="8" height="8" rx="2" stroke="#FFD700" strokeWidth="2" />
      </svg>
    ),
    description:
      "Bring your wildest marketing ideas to life. b Studio lets you create, remix, and launch content with a touch of AI magic—no tech skills needed.",
  },
  {
    title: "Marketing AI Toolkit",
    icon: (
      <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
        <path
          d="M12 3l2.09 6.26L21 9.27l-5 3.64L17.18 21 12 17.27 6.82 21 8 12.91l-5-3.64 6.91-1.01z"
          stroke="#FFD700"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    ),
    description:
      "Your creative Swiss Army knife: chat, write, design, edit, and organize—all powered by AI, all in one place. No more juggling apps or tabs.",
  },
  {
    title: "Knowledge & Context",
    icon: (
      <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
        <rect x="4" y="4" width="16" height="16" rx="3" stroke="#FFD700" strokeWidth="2" />
        <rect x="8" y="8" width="8" height="8" rx="2" stroke="#FFD700" strokeWidth="2" />
      </svg>
    ),
    description:
      "b learns your brand's voice and context, so every output feels like you—only faster, and with a dash of AI brilliance.",
  },
  {
    title: "Trust Foundation",
    icon: (
      <svg width="28" height="28" fill="none" viewBox="0 0 24 24">
        <path
          d="M12 2l7 4v6c0 5.25-3.5 10-7 10s-7-4.75-7-10V6l7-4z"
          stroke="#FFD700"
          strokeWidth="2"
          strokeLinejoin="round"
        />
      </svg>
    ),
    description:
      "Your ideas are safe here. b keeps your data private and secure, so you can create with confidence and focus on what matters—your next big idea.",
  },
] as const;















