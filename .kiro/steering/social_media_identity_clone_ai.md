---
inclusion: manual
---

# Social Media Identity Clone AI - Project Context

This steering file provides context for working with the Social Media Identity Clone AI project.

## Project Overview

Sistema de IA avanzado que clona la identidad de perfiles de redes sociales (TikTok, Instagram, YouTube) extrayendo todo el contenido, análisis de videos, posts y comentarios para crear un perfil de identidad completo y generar contenido auténtico basado en esa identidad clonada.

## Project Structure

```
social_media_identity_clone_ai/
├── core/              # Modelos y entidades base
├── services/          # Servicios principales (12 servicios)
├── connectors/        # Conectores a APIs (TikTok, Instagram, YouTube)
├── api/              # API REST (FastAPI)
├── ml_advanced/      # Sistema ML avanzado
├── middleware/       # Middleware (logging, security, rate limiting)
├── utils/           # Utilidades
├── db/              # Modelos de base de datos
├── tests/           # Tests
└── frontend/        # Frontend Next.js
```

## Key Services

- `ProfileExtractor`: Extrae perfiles de redes sociales
- `IdentityAnalyzer`: Analiza y construye identidad
- `ContentGenerator`: Genera contenido basado en identidad
- `VideoProcessor`: Procesa videos y transcripciones
- `StorageService`: Gestión de almacenamiento
- `VersioningService`: Control de versiones de identidades
- `WebhookService`: Webhooks para notificaciones
- `ExportService`: Exportación de datos
- `BatchService`: Procesamiento por lotes

## Code Style Guidelines

- Use type hints for all function parameters and return types
- Follow PEP 8 style guide
- Use async/await for I/O operations
- Inherit from `BaseService` or `BaseMLService` for services
- Use structured logging with `logger` from each module
- Handle errors using custom exceptions from `core.exceptions`
- Use Pydantic models for data validation

## Testing

- Tests located in `tests/` directory
- Use pytest for testing
- Test files should follow pattern `test_*.py`
- Use pytest-asyncio for async tests

## Documentation

- Main README: `README.md`
- API Documentation: `API_DOCUMENTATION.md`
- Architecture: `ARCHITECTURE.md`
- Deployment: `DEPLOYMENT.md`
- Security: `SECURITY.md`

## Common Tasks

### Adding a new connector:
1. Create file in `connectors/` directory
2. Implement connector class with retry and circuit breaker
3. Add to `ProfileExtractor` service
4. Add tests in `tests/`

### Adding a new service:
1. Create file in `services/` directory
2. Inherit from `BaseService` or `BaseMLService`
3. Implement required methods
4. Add to `__init__.py` exports
5. Add API routes if needed
6. Add tests

### Adding API endpoints:
1. Add route in `api/routes.py`
2. Use dependency injection for services
3. Add request/response models
4. Add error handling
5. Update `API_DOCUMENTATION.md`

## Important Notes

- The project uses FastAPI for the API
- Database models use SQLAlchemy
- ML services use PyTorch
- All async operations should use proper error handling
- Rate limiting and security middleware are configured
- The project supports multiple platforms: TikTok, Instagram, YouTube

