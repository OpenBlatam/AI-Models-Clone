# 🚀 **SISTEMA DE GESTIÓN DE RECURSOS INTELIGENTE**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-red.svg)](https://pytorch.org/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-green.svg)](https://gradio.app/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema avanzado de gestión automática e inteligente de recursos del sistema con optimización predictiva, monitoreo en tiempo real y arquitectura modular escalable.

## 📋 **TABLA DE CONTENIDOS**

- [🚀 Características](#-características)
- [🏗️ Arquitectura](#️-arquitectura)
- [📦 Instalación](#-instalación)
- [🎮 Uso Rápido](#-uso-rápido)
- [🔧 Configuración](#-configuración)
- [🐳 Docker](#-docker)
- [🧪 Testing](#-testing)
- [📊 Monitoreo](#-monitoreo)
- [🔮 Roadmap](#-roadmap)
- [🤝 Contribución](#-contribución)
- [📄 Licencia](#-licencia)

---

## 🚀 **CARACTERÍSTICAS**

### **🧠 Inteligencia Artificial Avanzada**
- **Predicción de Recursos**: Análisis predictivo de uso de CPU, GPU y memoria
- **Optimización Automática**: 4 niveles de optimización basados en prioridades
- **Aprendizaje Continuo**: Sistema que mejora automáticamente con el tiempo
- **Gestión Inteligente**: Toma de decisiones automática basada en IA

### **📊 Monitoreo en Tiempo Real**
- **Métricas Avanzadas**: Uso actual, pico, promedio, tendencias y predicciones
- **Alertas Inteligentes**: Notificaciones proactivas antes de problemas
- **Visualización Interactiva**: Interfaz Gradio moderna y responsiva
- **Historial Completo**: Trazabilidad de todas las optimizaciones

### **⚡ Optimización Automática**
- **4 Niveles de Prioridad**:
  - 🆘 **Emergencia**: Limpieza forzada y optimización inmediata
  - ⚡ **Crítico**: Optimización agresiva con múltiples estrategias
  - 🛡️ **Alto**: Optimización preventiva y monitoreo intensivo
  - 🔧 **Bajo**: Mantenimiento rutinario y ajustes menores

### **🏗️ Arquitectura Modular**
- **Microservicios**: Componentes independientes y escalables
- **Plugin System**: Sistema de plugins dinámico y extensible
- **Event-Driven**: Arquitectura basada en eventos asíncronos
- **Distributed**: Soporte para sistemas distribuidos

---

## 🏗️ **ARQUITECTURA**

```
┌─────────────────────────────────────────────────────────────┐
│                    🎮 INTERFAZ GRADIO                       │
│                    (Puerto 7860)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              🧠 ORQUESTADOR INTELIGENTE                     │
│              IntelligentResourceOrchestrator                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              🔧 GESTORES DE RECURSOS                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ CPUMemoryManager│  │ GPUMemoryManager│  │ Otros...     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              📊 SISTEMA DE MÉTRICAS                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Recolección   │  │   Análisis      │  │  Predicción  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              🔄 COLA DE OPTIMIZACIÓN                        │
│              (Priorización Automática)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 **INSTALACIÓN**

### **Requisitos del Sistema**
- Python 3.9+
- CUDA 12.1+ (opcional, para GPU)
- Docker & Docker Compose (recomendado)
- 8GB+ RAM
- 4+ núcleos CPU

### **Instalación Rápida**

#### **1. Clonar Repositorio**
```bash
git clone https://github.com/intelligent-system/resource-manager.git
cd resource-manager
```

#### **2. Instalar Dependencias**

**Opción A: Instalación Completa**
```bash
pip install -r requirements_optimized.txt
```

**Opción B: Instalación Modular**
```bash
# Core + Desarrollo
pip install -e ".[dev]"

# Con soporte GPU
pip install -e ".[gpu]"

# Con monitoreo avanzado
pip install -e ".[monitoring]"

# Todo incluido
pip install -e ".[all]"
```

#### **3. Verificar Instalación**
```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import gradio; print(f'Gradio: {gradio.__version__}')"
python -c "import psutil; print('psutil: OK')"
```

---

## 🎮 **USO RÁPIDO**

### **1. Ejecutar Sistema Principal**
```bash
# Sistema completo con interfaz Gradio
python resource_manager_demo.py

# Solo sistema de gestión (sin interfaz)
python intelligent_resource_manager.py
```

### **2. Ejecutar Tests**
```bash
# Tests completos
python test_intelligent_resource_manager.py

# Tests con pytest
pytest test_intelligent_resource_manager.py -v

# Tests con cobertura
pytest test_intelligent_resource_manager.py --cov=. --cov-report=html
```

### **3. Configuración Personalizada**
```bash
# Editar configuración
nano resource_config.yaml

# Ejecutar con configuración personalizada
python intelligent_resource_manager.py --config custom_config.yaml
```

---

## 🔧 **CONFIGURACIÓN**

### **Archivo de Configuración (`resource_config.yaml`)**

```yaml
# Configuración de recursos
resources:
  cpu_memory:
    max_usage: 0.85          # Uso máximo permitido
    optimal_usage: 0.65      # Uso óptimo
    critical_threshold: 0.92 # Umbral crítico
    auto_optimize: true      # Optimización automática
    
  gpu:
    max_usage: 0.80
    optimal_usage: 0.60
    critical_threshold: 0.90
    auto_optimize: true

# Configuración de optimización
optimization:
  priority_levels:
    0: "emergency"      # Máxima prioridad
    1: "critical"       # Crítico
    2: "high"           # Alto
    3: "low"            # Bajo

# Configuración de monitoreo
monitoring:
  metrics_history_size: 100
  alert_thresholds:
    warning: 0.75
    critical: 0.90
    emergency: 0.95
```

### **Variables de Entorno**

```bash
# Configuración básica
export GRADIO_SERVER_NAME=0.0.0.0
export GRADIO_SERVER_PORT=7860
export MONITORING_ENABLED=true
export GPU_ENABLED=true

# Configuración avanzada
export REDIS_URL=redis://localhost:6379
export LOG_LEVEL=INFO
export PROFILING_ENABLED=false
```

---

## 🐳 **DOCKER**

### **Ejecución Rápida con Docker**

#### **1. Construir Imagen**
```bash
# Construir imagen de producción
docker build -t intelligent-resource-manager .

# Construir imagen de desarrollo
docker build --target development -t intelligent-resource-manager:dev .
```

#### **2. Ejecutar Contenedor**
```bash
# Ejecutar con GPU
docker run --gpus all -p 7860:7860 intelligent-resource-manager

# Ejecutar en modo desarrollo
docker run -it -p 7860:7860 -v $(pwd):/app intelligent-resource-manager:dev

# Ejecutar tests
docker run intelligent-resource-manager:test
```

### **Docker Compose Completo**

#### **1. Iniciar Sistema Completo**
```bash
# Sistema completo con monitoreo
docker-compose up -d

# Solo servicios principales
docker-compose up resource-manager-ui resource-manager-core redis

# Modo desarrollo
docker-compose --profile development up -d
```

#### **2. Servicios Disponibles**
- **🎮 UI Principal**: http://localhost:7860 (Gradio)
- **📊 Grafana**: http://localhost:3000 (admin/admin123)
- **📈 Prometheus**: http://localhost:9090
- **🌸 Flower**: http://localhost:5555 (Celery)
- **📚 Jupyter**: http://localhost:8888 (token: resource_manager_2024)

#### **3. Comandos Útiles**
```bash
# Ver logs
docker-compose logs -f resource-manager-ui

# Reiniciar servicio
docker-compose restart resource-manager-core

# Escalar workers
docker-compose up -d --scale celery-worker=3

# Limpiar todo
docker-compose down -v
```

---

## 🧪 **TESTING**

### **Ejecutar Tests**

```bash
# Tests unitarios
pytest test_intelligent_resource_manager.py -v

# Tests con cobertura
pytest test_intelligent_resource_manager.py --cov=. --cov-report=html

# Tests específicos
pytest test_intelligent_resource_manager.py::TestCPUMemoryManager -v

# Tests de integración
pytest test_intelligent_resource_manager.py::TestIntegration -v

# Tests de rendimiento
pytest test_intelligent_resource_manager.py -m "slow" -v
```

### **Cobertura de Tests**

```bash
# Generar reporte de cobertura
coverage run -m pytest test_intelligent_resource_manager.py
coverage report
coverage html  # Abrir htmlcov/index.html
```

### **Tests con Docker**

```bash
# Ejecutar tests en contenedor
docker-compose --profile testing up testing

# Tests con GPU
docker run --gpus all intelligent-resource-manager:test
```

---

## 📊 **MONITOREO**

### **Métricas Disponibles**

- **CPU**: Uso, frecuencia, temperatura
- **Memoria**: Uso, swap, fragmentación
- **GPU**: Uso, memoria, temperatura
- **Red**: Ancho de banda, latencia
- **Disco**: I/O, espacio, velocidad

### **Alertas Configurables**

- **Advertencia**: 75% de uso
- **Crítico**: 90% de uso
- **Emergencia**: 95% de uso

### **Dashboards**

- **Grafana**: Dashboards predefinidos para recursos
- **Prometheus**: Métricas históricas y alertas
- **Gradio**: Interfaz interactiva en tiempo real

---

## 🔮 **ROADMAP**

### **Versión 2.0 (Próximamente)**
- [ ] **Machine Learning Avanzado**: Predicciones más precisas
- [ ] **Auto-scaling**: Escalado automático de recursos
- [ ] **Integración Cloud**: AWS, GCP, Azure
- [ ] **Kubernetes**: Orquestación nativa de K8s

### **Versión 3.0 (Futuro)**
- [ ] **Edge Computing**: Optimización para dispositivos edge
- [ ] **Federated Learning**: Aprendizaje distribuido
- [ ] **Quantum Optimization**: Optimización cuántica
- [ ] **AI Agents**: Agentes autónomos de optimización

---

## 🤝 **CONTRIBUCIÓN**

### **Cómo Contribuir**

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. **Abre** un Pull Request

### **Estándares de Código**

```bash
# Formatear código
black intelligent_resource_manager.py
isort intelligent_resource_manager.py

# Verificar tipos
mypy intelligent_resource_manager.py

# Linting
flake8 intelligent_resource_manager.py

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### **Reportar Bugs**

- Usa el [Issue Tracker](https://github.com/intelligent-system/resource-manager/issues)
- Incluye logs y configuración
- Describe pasos para reproducir

---

## 📄 **LICENCIA**

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 🙏 **AGRADECIMIENTOS**

- **PyTorch Team** por el framework de deep learning
- **Gradio Team** por la interfaz interactiva
- **Hugging Face** por las librerías de transformers
- **NVIDIA** por el soporte CUDA
- **Docker Team** por la containerización

---

## 📞 **CONTACTO**

- **Email**: dev@intelligent-system.com
- **GitHub**: [@intelligent-system](https://github.com/intelligent-system)
- **Documentación**: [ReadTheDocs](https://intelligent-resource-manager.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/intelligent-system/resource-manager/issues)

---

**⭐ ¡No olvides dar una estrella al proyecto si te resulta útil! ⭐**
