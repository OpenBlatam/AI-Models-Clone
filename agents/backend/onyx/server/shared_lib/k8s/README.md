# ☸️ Kubernetes Deployment Guide

Manifiestos listos para desplegar `shared_lib` en Kubernetes con soporte para Istio, Linkerd, HPA y observabilidad.

## 📂 Archivos

- `deployment.yaml` – Deployment con readiness/liveness, PodDisruptionBudget, tolerations
- `service.yaml` – Service (ClusterIP) + annotations para mesh/proxy
- `ingress.yaml` – Ingress compatible con NGINX / AWS ALB
- `hpa.yaml` – Horizontal Pod Autoscaler (CPU + custom metrics)
- `istio-virtualservice.yaml` – Traffic management (canary, retries, timeouts)
- `linkerd-serviceprofile.yaml` – ServiceProfile para request-level metrics

## 🚀 Uso Rápido

```bash
kubectl apply -n music-analyzer -f k8s/deployment.yaml
kubectl apply -n music-analyzer -f k8s/service.yaml
kubectl apply -n music-analyzer -f k8s/ingress.yaml
kubectl apply -n music-analyzer -f k8s/hpa.yaml
```

### Istio (opcional)
```bash
kubectl apply -n music-analyzer -f k8s/istio-virtualservice.yaml
```

### Linkerd (opcional)
```bash
kubectl apply -n music-analyzer -f k8s/linkerd-serviceprofile.yaml
```

## 🔧 Variables Clave

| Variable | Ubicación | Descripción |
|----------|-----------|-------------|
| `SERVICE_NAME` | deployment.yaml | Nombre lógico del servicio |
| `IMAGE` | deployment.yaml | Imagen container (ECR/GCR) |
| `ENVIRONMENT` | deployment.yaml | `dev/staging/prod` |
| `TARGET_AVG_CPU` | hpa.yaml | CPU target para autoscaling |

## ✅ Requisitos

- Kubernetes ≥ 1.25
- Metrics Server (para HPA)
- (Opcional) Istio 1.20+ / Linkerd 2.14+
- (Opcional) NGINX Ingress Controller

## 🧪 Testing

```bash
kubectl -n music-analyzer rollout status deployment/music-analyzer
kubectl -n music-analyzer get hpa
kubectl -n music-analyzer describe virtualservice music-analyzer
```

## 📊 Observabilidad

- Listo para integrarse con Prometheus (`prometheus.io` annotations)
- Liveness + readiness probes adaptados a FastAPI (`/health`)
- Istio/Linkerd config incluye timeout, retries, circuit breakers

---

**Tip:** Usa `kustomize` o `helm` para parametrizar estos manifiestos.
{
  "cells": [],
  "metadata": {
    "language_info": {
      "name": "python"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}