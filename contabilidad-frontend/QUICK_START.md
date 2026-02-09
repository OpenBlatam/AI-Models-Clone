# Inicio Rápido

## Prerrequisitos

- Node.js 18+ instalado
- Backend API ejecutándose (por defecto en `http://localhost:8000`)

## Pasos para Iniciar

### 1. Instalar Dependencias

```bash
cd contabilidad-frontend
npm install
```

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo y ajusta la URL del backend:

```bash
cp .env.example .env.local
```

Edita `.env.local` y configura la URL de tu backend:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Iniciar el Servidor de Desarrollo

```bash
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## Uso

1. Abre `http://localhost:3000` en tu navegador
2. Selecciona un servicio del dashboard
3. Completa el formulario correspondiente
4. Observa el progreso de la tarea en el monitor lateral
5. El resultado aparecerá automáticamente cuando la tarea se complete

## Servicios Disponibles

- **Cálculo de Impuestos**: Calcula impuestos (ISR, IVA, IEPS) según régimen fiscal
- **Asesoría Fiscal**: Obtén respuestas personalizadas a tus preguntas fiscales
- **Guía Fiscal**: Guías detalladas sobre temas fiscales específicos
- **Trámites SAT**: Información sobre trámites del SAT
- **Ayuda con Declaraciones**: Asistencia para preparar declaraciones fiscales

## Solución de Problemas

### El frontend no se conecta al backend

1. Verifica que el backend esté ejecutándose
2. Verifica la URL en `.env.local`
3. Verifica que no haya problemas de CORS en el backend

### Errores de TypeScript

Ejecuta:

```bash
npm run build
```

Esto mostrará todos los errores de TypeScript.

### El polling no funciona

Verifica que:
- El backend esté respondiendo correctamente
- La URL del API esté correcta
- No haya errores en la consola del navegador














