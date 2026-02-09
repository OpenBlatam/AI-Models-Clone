import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './pages/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
        './app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: 'hsl(258, 90%, 66%)',
                    glow: 'hsl(258, 90%, 56%)',
                    dark: 'hsl(258, 90%, 46%)',
                    light: 'hsl(258, 90%, 76%)',
                },
                secondary: {
                    DEFAULT: 'hsl(198, 93%, 60%)',
                    glow: 'hsl(198, 93%, 50%)',
                },
                accent: {
                    success: 'hsl(142, 76%, 55%)',
                    warning: 'hsl(45, 93%, 58%)',
                    error: 'hsl(0, 84%, 60%)',
                },
                background: {
                    DEFAULT: 'hsl(240, 10%, 6%)',
                    secondary: 'hsl(240, 10%, 10%)',
                },
                card: {
                    DEFAULT: 'hsl(240, 10%, 10%)',
                    hover: 'hsl(240, 10%, 14%)',
                },
                text: {
                    DEFAULT: 'hsl(0, 0%, 95%)',
                    muted: 'hsl(240, 5%, 65%)',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            animation: {
                'glow': 'glow 2s ease-in-out infinite alternate',
                'float': 'float 3s ease-in-out infinite',
                'pulse-slow': 'pulse 3s ease-in-out infinite',
                'shimmer': 'shimmer 2s linear infinite',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 20px hsl(258, 90%, 66%, 0.3)' },
                    '100%': { boxShadow: '0 0 40px hsl(258, 90%, 66%, 0.6)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                shimmer: {
                    '0%': { backgroundPosition: '-200% 0' },
                    '100%': { backgroundPosition: '200% 0' },
                },
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-primary': 'linear-gradient(135deg, hsl(258, 90%, 66%) 0%, hsl(198, 93%, 60%) 100%)',
                'shimmer': 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
            },
        },
    },
    plugins: [],
}

export default config
