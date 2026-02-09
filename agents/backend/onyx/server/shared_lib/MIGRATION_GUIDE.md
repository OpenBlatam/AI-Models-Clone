# 📦 Guía de Migración - Shared Library

Guía para migrar utilidades avanzadas a la librería compartida.

## 🎯 Objetivo

Centralizar todas las utilidades avanzadas en `shared_lib/` para que puedan ser reutilizadas por todos los proyectos.

## 📋 Módulos a Migrar

### Desde `3d_prototype_ai/utils/` o `music_analyzer_ai/utils/advanced/`:

1. ✅ **middleware/advanced_middleware.py** → `shared_lib/middleware/advanced_middleware.py` (COMPLETADO)
2. ⏳ **oauth2_security.py** → `shared_lib/security/oauth2_security.py`
3. ⏳ **async_workers.py** → `shared_lib/workers/async_workers.py`
4. ⏳ **message_broker.py** → `shared_lib/messaging/message_broker.py`
5. ⏳ **serverless_optimizer.py** → `shared_lib/serverless/serverless_optimizer.py`
6. ⏳ **structured_logging.py** → `shared_lib/logging/structured_logging.py`
7. ⏳ **owasp_security.py** → `shared_lib/security_owasp/owasp_security.py`
8. ⏳ **database_adapters.py** → `shared_lib/database/database_adapters.py`
9. ⏳ **elasticsearch_client.py** → `shared_lib/search/elasticsearch_client.py`
10. ⏳ **memcached_client.py** → `shared_lib/cache/memcached_client.py`
11. ⏳ **kong_gateway.py** → `shared_lib/gateway/kong_gateway.py`
12. ⏳ **aws_api_gateway.py** → `shared_lib/gateway/aws_api_gateway.py`
13. ⏳ **service_mesh.py** → `shared_lib/service_mesh/service_mesh.py`
14. ⏳ **service_discovery.py** → `shared_lib/discovery/service_discovery.py`
15. ⏳ **inter_service_comm.py** → `shared_lib/inter_service/inter_service_comm.py`

## 🔧 Pasos de Migración

### Paso 1: Copiar Archivos

```bash
# Desde agents/backend/onyx/server/features/3d_prototype_ai/utils/

# Security
cp oauth2_security.py ../shared_lib/security/

# Workers
cp async_workers.py ../shared_lib/workers/

# Messaging
cp message_broker.py ../shared_lib/messaging/

# Serverless
cp serverless_optimizer.py ../shared_lib/serverless/

# Logging
cp structured_logging.py ../shared_lib/logging/

# OWASP Security
cp owasp_security.py ../shared_lib/security_owasp/

# Database
cp database_adapters.py ../shared_lib/database/

# Search
cp elasticsearch_client.py ../shared_lib/search/

# Cache
cp memcached_client.py ../shared_lib/cache/

# Gateway
cp kong_gateway.py ../shared_lib/gateway/
cp aws_api_gateway.py ../shared_lib/gateway/

# Service Mesh
cp service_mesh.py ../shared_lib/service_mesh/

# Discovery
cp service_discovery.py ../shared_lib/discovery/

# Inter-service
cp inter_service_comm.py ../shared_lib/inter_service/
```

### Paso 2: Crear __init__.py para cada módulo

Cada carpeta necesita un `__init__.py` que exporte las clases/funciones principales.

### Paso 3: Actualizar Imports en Proyectos

Cambiar de:
```python
from utils.advanced.advanced_middleware import setup_advanced_middleware
```

A:
```python
from shared_lib.middleware import setup_advanced_middleware
```

O:
```python
from shared_lib import setup_advanced_middleware
```

### Paso 4: Actualizar Nombres de Servicio

En los archivos migrados, cambiar nombres de servicio genéricos:
- `"3d_prototype_ai"` → `"blatam_service"` o usar parámetro
- `"music_analyzer_ai"` → `"blatam_service"` o usar parámetro

## ✅ Checklist de Migración

- [x] Estructura de carpetas creada
- [x] `__init__.py` principal creado
- [x] Middleware migrado
- [ ] Security (OAuth2) migrado
- [ ] Workers migrado
- [ ] Messaging migrado
- [ ] Serverless migrado
- [ ] Logging migrado
- [ ] OWASP Security migrado
- [ ] Database migrado
- [ ] Search migrado
- [ ] Cache migrado
- [ ] Gateway migrado
- [ ] Service Mesh migrado
- [ ] Discovery migrado
- [ ] Inter-service migrado
- [ ] Documentación actualizada
- [ ] Tests creados

## 🚀 Uso Después de Migración

```python
# Antes
from utils.advanced.advanced_middleware import setup_advanced_middleware

# Después
from shared_lib import setup_advanced_middleware
# o
from shared_lib.middleware import setup_advanced_middleware
```

## 📝 Notas

- Los archivos deben ser genéricos y no específicos de un proyecto
- Usar parámetros para nombres de servicio en lugar de hardcodear
- Mantener compatibilidad hacia atrás cuando sea posible
- Documentar cambios breaking

---

**Estado**: En progreso  
**Última actualización**: 2024




