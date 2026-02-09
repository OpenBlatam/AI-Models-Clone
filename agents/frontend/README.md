# Blatam Academy Frontend

Frontend Next.js con TypeScript para las plataformas Music Analyzer AI y Robot Movement AI.

## 🚀 Características

- **Next.js 14** con App Router
- **TypeScript** para type safety
- **Tailwind CSS** para estilos
- **React Query** para manejo de estado y caché
- **Integración completa** con ambos backends
- **UI moderna y responsive**

## 📦 Instalación

```bash
# Instalar dependencias
npm install

# O con yarn
yarn install
```

## ⚙️ Configuración

Crea un archivo `.env.local` basado en `.env.local.example`:

```env
NEXT_PUBLIC_MUSIC_API_URL=http://localhost:8010
NEXT_PUBLIC_ROBOT_API_URL=http://localhost:8010
```

## 🏃 Desarrollo

```bash
# Iniciar servidor de desarrollo
npm run dev

# Build para producción
npm run build

# Iniciar servidor de producción
npm start

# Type checking
npm run type-check

# Linting
npm run lint
```

El servidor estará disponible en `http://localhost:3000`

## 📁 Estructura del Proyecto

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx          # Layout principal
│   ├── page.tsx             # Página de inicio
│   ├── music/              # Páginas de Music Analyzer
│   └── robot/              # Páginas de Robot Movement
├── components/             # Componentes React
│   ├── music/              # Componentes de Music Analyzer
│   └── robot/              # Componentes de Robot Movement
├── lib/                    # Utilidades y servicios
│   ├── api/                # Servicios API
│   └── utils.ts            # Utilidades generales
└── public/                 # Archivos estáticos
```

## 🎵 Music Analyzer AI

Funcionalidades:
- Búsqueda de canciones
- Análisis musical completo
- Coaching personalizado
- Recomendaciones inteligentes
- Dashboard de analytics

## 🤖 Robot Movement AI

Funcionalidades:
- Control mediante chat
- Monitoreo de estado en tiempo real
- Controles de movimiento
- Métricas y analytics

## 🛠️ Tecnologías

- **Next.js 14**: Framework React
- **TypeScript**: Type safety
- **Tailwind CSS**: Estilos
- **React Query**: Data fetching
- **Axios**: HTTP client
- **Lucide React**: Iconos
- **React Hot Toast**: Notificaciones
- **Framer Motion**: Animaciones

## 📝 Scripts Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build de producción
- `npm start` - Servidor de producción
- `npm run lint` - Linter
- `npm run type-check` - Verificación de tipos

## 🔗 Enlaces

- Music Analyzer API: `/music`
- Robot Movement API: `/robot`
- Página principal: `/`

## 📄 Licencia

Parte de Blatam Academy

