# 🚀 Guía de Ejecución - Shared Library

Guía completa para ejecutar y probar la librería compartida.

## 📋 Contenido

1. [Verificación](#verificación)
2. [Iniciar Servicios](#iniciar-servicios)
3. [Ejecutar Ejemplo](#ejecutar-ejemplo)
4. [Tests](#tests)
5. [Integración en Proyectos](#integración-en-proyectos)

---

## 1. Verificación

### Verificar Instalación

```bash
# Desde agents/backend/onyx/server/
python shared_lib/setup.py
```

O:

```bash
cd shared_lib
python setup.py
```

### Verificar Imports

```python
python -c "from shared_lib.middleware import setup_advanced_middleware; print('✅ OK')"
```

### Ejecutar Tests

```bash
python shared_lib/run_tests.py
```

---

## 2. Iniciar Servicios

### Opción A: Script Automático (Linux/Mac)

```bash
chmod +x shared_lib/start_services.sh
./shared_lib/start_services.sh
```

### Opción B: Script PowerShell (Windows)

```powershell
.\shared_lib\start_services.ps1
```

### Opción C: Docker Compose Manual

```bash
cd shared_lib
docker-compose up -d
```

### Servicios Iniciados

- **Redis**: `localhost:6379`
- **RabbitMQ**: `localhost:5672`
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Elasticsearch**: `localhost:9200`
- **Memcached**: `localhost:11211`

### Verificar Servicios

```bash
# Redis
redis-cli ping

# RabbitMQ
curl http://localhost:15672/api/overview

# Elasticsearch
curl http://localhost:9200/_cluster/health

# Prometheus
curl http://localhost:9090/-/healthy
```

### Detener Servicios

```bash
cd shared_lib
docker-compose down
```

---

## 3. Ejecutar Ejemplo

### Ejemplo Completo

```bash
# Desde agents/backend/onyx/server/
python shared_lib/run_example.py
```

O:

```bash
cd shared_lib
python run_example.py
```

### Acceder al Servidor

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### Probar Endpoints

```bash
# Root
curl http://localhost:8000/

# Health
curl http://localhost:8000/health

# Test endpoint
curl http://localhost:8000/test/123

# Async task (si workers disponibles)
curl -X POST http://localhost:8000/async-task \
  -H "Content-Type: application/json" \
  -d '{"data": "test"}'

# Publish event (si message broker disponible)
curl -X POST http://localhost:8000/publish-event \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```

---

## 4. Tests

### Tests Automáticos

```bash
python shared_lib/run_tests.py
```

### Tests Manuales

```python
# test_imports.py
from shared_lib.middleware import setup_advanced_middleware
from fastapi import FastAPI

app = FastAPI()
setup_advanced_middleware(app, service_name="test")
print("✅ Test pasado")
```

---

## 5. Integración en Proyectos

### En main.py de cualquier proyecto

```python
from fastapi import FastAPI
from shared_lib.middleware import setup_advanced_middleware

app = FastAPI(title="Mi Servicio")

# Una línea para configurar todo
setup_advanced_middleware(
    app,
    service_name="mi_servicio",
    enable_opentelemetry=True
)

# Tu código aquí...
```

### Verificar que Funciona

```bash
# Iniciar tu servicio
python main.py

# Verificar logs estructurados
# Deberías ver logs JSON con request_id, timing, etc.

# Verificar headers
curl -I http://localhost:PORT/
# Deberías ver X-Request-ID, X-Process-Time, security headers
```

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'shared_lib'"

**Solución**: Asegúrate de estar en el directorio correcto:
```bash
cd agents/backend/onyx/server/
python -c "from shared_lib import setup_advanced_middleware"
```

### Error: "OpenTelemetry not available"

**Solución**: Instalar dependencias:
```bash
pip install -r shared_lib/requirements.txt
```

### Error: "Redis connection failed"

**Solución**: Iniciar servicios:
```bash
cd shared_lib
docker-compose up -d redis
```

### Error: "RabbitMQ connection failed"

**Solución**: Iniciar RabbitMQ:
```bash
cd shared_lib
docker-compose up -d rabbitmq
```

---

## 📊 Monitoreo

### Prometheus

- URL: http://localhost:9090
- Ver métricas de servicios FastAPI

### Grafana

- URL: http://localhost:3000
- Login: admin/admin
- Configurar datasource: Prometheus (http://prometheus:9090)

### Logs Estructurados

Los logs se generan en formato JSON. Verificar en consola o configurar exportación a:
- ELK Stack
- CloudWatch
- Archivo JSON

---

## ✅ Checklist de Ejecución

- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Servicios iniciados (`docker-compose up -d`)
- [ ] Tests pasando (`python run_tests.py`)
- [ ] Ejemplo funcionando (`python run_example.py`)
- [ ] Integrado en proyecto
- [ ] Logs estructurados funcionando
- [ ] Headers de seguridad presentes
- [ ] OpenTelemetry configurado (opcional)

---

## 🎯 Comandos Rápidos

```bash
# Todo en uno
cd agents/backend/onyx/server/shared_lib
docker-compose up -d && python run_tests.py && python run_example.py
```

---

**Última actualización**: 2024




