# Shopping Engine AI Frontend

A modern Next.js 15.3 Turbopack TypeScript frontend for the Shopping Engine AI backend.

## Features

- **Product Analysis**: Upload product images for AI-powered identification
- **Purchase Options**: Find where to buy with price estimates
- **Smart Recommendations**: Get alternatives, upgrades, and accessories
- **Price Comparison**: Compare prices across multiple vendors
- **Product Details**: Access comprehensive specifications

## Tech Stack

- **Framework**: Next.js 15.3 with Turbopack
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.4
- **Animations**: Framer Motion
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn or pnpm

### Installation

1. Navigate to the project directory:
```bash
cd agents/frontend/shopping-engine
```

2. Rename tsconfig.txt to tsconfig.json:
```bash
mv tsconfig.txt tsconfig.json
```

3. Create package.json:
```json
{
  "name": "shopping-engine-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "15.3.2",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "lucide-react": "^0.468.0",
    "framer-motion": "^11.15.0",
    "@tanstack/react-query": "^5.62.0",
    "@tanstack/react-query-devtools": "^5.62.0",
    "zustand": "^5.0.2",
    "react-hot-toast": "^2.4.1",
    "react-dropzone": "^14.3.5",
    "clsx": "^2.1.1",
    "date-fns": "^4.1.0",
    "zod": "^3.24.1"
  },
  "devDependencies": {
    "@types/node": "^22.10.2",
    "@types/react": "^19.0.1",
    "@types/react-dom": "^19.0.2",
    "typescript": "^5.7.2",
    "tailwindcss": "^3.4.17",
    "postcss": "^8.4.49",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.17.0",
    "eslint-config-next": "15.3.2",
    "prettier": "^3.4.2",
    "prettier-plugin-tailwindcss": "^0.6.9"
  }
}
```

4. Install dependencies:
```bash
npm install
```

5. Configure environment variables:
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8060" > .env.local
```

6. Run the development server:
```bash
npm run dev
```

7. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
shopping-engine/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── analyze/            # Product analysis page
│   ├── purchase/           # Purchase options page
│   ├── recommendations/    # Recommendations page
│   ├── compare/            # Price comparison page
│   └── details/            # Product details page
├── src/
│   ├── api/                # API client
│   ├── components/
│   │   ├── features/       # Feature-specific components
│   │   ├── layout/         # Layout components
│   │   └── ui/             # Reusable UI components
│   ├── hooks/              # Custom React hooks
│   └── types/              # TypeScript types
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## API Integration

The frontend connects to the Shopping Engine AI backend at `http://localhost:8060` by default. Make sure the backend is running before using the frontend.

### Starting the Backend

```bash
cd agents/backend/onyx/server/features/shopping_engine_ai
python -m uvicorn api.shopping_engine_api:app --host 0.0.0.0 --port 8060
```

## Design System

The frontend uses a premium dark theme with:
- Primary: Purple (`hsl(258, 90%, 66%)`)
- Secondary: Cyan (`hsl(198, 93%, 60%)`)
- Background: Dark slate (`hsl(240, 10%, 6%)`)

## License

MIT
