# 🚀 Cómo Ejecutar - Guía Rápida

## ✅ Lo que ya está listo para ejecutar

### 1. Middleware Avanzado (FUNCIONA AHORA)

```python
# En cualquier proyecto FastAPI
from shared_lib.middleware import setup_advanced_middleware
from fastapi import FastAPI

app = FastAPI()
setup_advanced_middleware(app, service_name="mi_servicio")
```

### 2. Servicios con Docker Compose

```bash
# Iniciar todos los servicios
cd agents/backend/onyx/server/shared_lib
docker-compose up -d

# Ver servicios
docker-compose ps

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### 3. Ejemplo Completo

```bash
# Ejecutar servidor de ejemplo
cd agents/backend/onyx/server
python shared_lib/run_example.py

# O con uvicorn directamente
uvicorn shared_lib.run_example:app --host 0.0.0.0 --port 8000
```

## 📋 Comandos por Plataforma

### Windows (PowerShell)

```powershell
# 1. Iniciar servicios
cd agents\backend\onyx\server\shared_lib
.\start_services.ps1

# 2. Verificar
python shared_lib\setup.py

# 3. Ejecutar ejemplo
python shared_lib\run_example.py
```

### Linux/Mac

```bash
# 1. Iniciar servicios
cd agents/backend/onyx/server/shared_lib
chmod +x start_services.sh
./start_services.sh

# 2. Verificar
python shared_lib/setup.py

# 3. Ejecutar ejemplo
python shared_lib/run_example.py
```

## 🎯 Integración Rápida en Proyectos Existentes

### Paso 1: Agregar a main.py

```python
# Al inicio del archivo
from shared_lib.middleware import setup_advanced_middleware

# Después de crear app = FastAPI()
setup_advanced_middleware(app, service_name="nombre_del_servicio")
```

### Paso 2: Verificar que funciona

```bash
# Iniciar servicio
python main.py

# En otra terminal, probar
curl http://localhost:PORT/
# Deberías ver headers: X-Request-ID, X-Process-Time
```

## 🔍 Verificación Manual

### Test 1: Import

```python
python -c "from shared_lib.middleware import setup_advanced_middleware; print('✅ OK')"
```

### Test 2: FastAPI Setup

```python
from fastapi import FastAPI
from shared_lib.middleware import setup_advanced_middleware

app = FastAPI()
setup_advanced_middleware(app, service_name="test")
print("✅ Setup exitoso")
```

### Test 3: Servicios Docker

```bash
# Verificar Redis
docker exec shared-lib-redis redis-cli ping
# Debería responder: PONG

# Verificar RabbitMQ
curl http://localhost:15672/api/overview
# Debería retornar JSON

# Verificar Elasticsearch
curl http://localhost:9200/_cluster/health
# Debería retornar status
```

## 📊 Servicios Disponibles

| Servicio | Puerto | URL | Credenciales |
|----------|--------|-----|--------------|
| Redis | 6379 | - | - |
| RabbitMQ | 5672 | - | admin/admin |
| RabbitMQ Management | 15672 | http://localhost:15672 | admin/admin |
| Prometheus | 9090 | http://localhost:9090 | - |
| Grafana | 3000 | http://localhost:3000 | admin/admin |
| Elasticsearch | 9200 | http://localhost:9200 | - |
| Memcached | 11211 | - | - |

## 🎯 Ejemplo Completo de Uso

```python
# main.py
from fastapi import FastAPI
from shared_lib.middleware import setup_advanced_middleware

app = FastAPI(title="Mi Servicio")

# Configurar middleware (una línea)
setup_advanced_middleware(
    app,
    service_name="mi_servicio",
    enable_opentelemetry=True
)

@app.get("/")
async def root():
    return {"message": "Servicio con shared_lib"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Ejecutar:
```bash
python main.py
```

## ✅ Checklist de Ejecución

- [ ] Docker instalado y funcionando
- [ ] Servicios iniciados (`docker-compose up -d`)
- [ ] Dependencias instaladas (`pip install -r shared_lib/requirements.txt`)
- [ ] Import funciona (`from shared_lib.middleware import setup_advanced_middleware`)
- [ ] Servicio FastAPI iniciado
- [ ] Headers presentes en respuestas (X-Request-ID, etc.)
- [ ] Logs estructurados funcionando

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'shared_lib'"

**Solución**: Asegúrate de estar en el directorio correcto:
```bash
cd agents/backend/onyx/server/
python -c "from shared_lib import setup_advanced_middleware"
```

### "Docker no está instalado"

**Solución**: Instalar Docker Desktop desde https://www.docker.com/products/docker-desktop

### "Puerto ya en uso"

**Solución**: Cambiar puertos en `docker-compose.yml` o detener servicios que usan esos puertos

### "OpenTelemetry not available"

**Solución**: Es opcional, el middleware funciona sin él. Para habilitarlo:
```bash
pip install opentelemetry-api opentelemetry-sdk
```

---

**¡Listo para ejecutar!** 🚀




