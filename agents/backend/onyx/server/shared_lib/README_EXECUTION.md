# ⚡ Ejecución Rápida - Shared Library

## 🚀 Inicio Rápido (3 Pasos)

### 1. Iniciar Servicios

```bash
cd agents/backend/onyx/server/shared_lib
docker-compose up -d
```

### 2. Verificar Instalación

```bash
python quick_test.py
```

### 3. Usar en tu Proyecto

```python
from shared_lib.middleware import setup_advanced_middleware

app = FastAPI()
setup_advanced_middleware(app, service_name="mi_servicio")
```

## ✅ Eso es todo!

La librería ya está funcionando. Ver `HOW_TO_RUN.md` para más detalles.




