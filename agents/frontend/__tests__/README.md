# Tests

Este directorio contiene todos los tests del proyecto Music Analyzer AI.

## Estructura

```
__tests__/
├── components/
│   └── music/
│       ├── MusicSocial.test.tsx
│       ├── MusicTrendingNow.test.tsx
│       ├── MusicActivity.test.tsx
│       ├── MusicRadio.test.tsx
│       ├── MusicDiscoverWeekly.test.tsx
│       ├── MusicAchievements.test.tsx
│       └── MusicStreak.test.tsx
├── lib/
│   └── api/
│       └── music-api.test.ts
└── utils.test.ts
```

## Ejecutar Tests

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests en modo watch
npm run test:watch

# Ejecutar tests con coverage
npm run test:coverage
```

## Cobertura

Los tests cubren:
- Componentes de React (renderizado, interacciones, eventos)
- Servicios de API (llamadas HTTP, manejo de errores)
- Funciones utilitarias (formateo, validación)

## Mocks

Los siguientes módulos están mockeados:
- `next/navigation` - Router de Next.js
- `react-hot-toast` - Notificaciones
- `framer-motion` - Animaciones
- `axios` - Cliente HTTP
- APIs del navegador (Audio, IntersectionObserver, matchMedia)

## Escribir Nuevos Tests

### Componente de React

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from '@/components/MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('handles user interaction', () => {
    const handleClick = jest.fn();
    render(<MyComponent onClick={handleClick} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

### Servicio de API

```typescript
import axios from 'axios';
import { myApiService } from '@/lib/api/my-api';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('MyApiService', () => {
  it('should make API call', async () => {
    const mockResponse = { data: { success: true } };
    mockedAxios.get.mockResolvedValue(mockResponse);

    const result = await myApiService.getData();
    expect(result).toEqual({ success: true });
  });
});
```

## Mejores Prácticas

1. **Nombres descriptivos**: Usa nombres claros para tests y describe blocks
2. **Arrange-Act-Assert**: Organiza tus tests en estas tres secciones
3. **Un test, una aserción**: Cada test debe verificar una cosa
4. **Mocks apropiados**: Mockea dependencias externas, no el código que estás testeando
5. **Cobertura significativa**: Enfócate en lógica de negocio y casos edge

