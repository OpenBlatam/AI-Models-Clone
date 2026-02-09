# 📊 Observability Pack

Configuraciones listas para Prometheus, Alertmanager y Grafana.

## 📂 Archivos

- `prometheus-rules.yml` – Alertas (latencia, errores, saturación)
- `alertmanager.yml` – Rutas de alertas (Slack, email)
- `grafana-dashboard.json` – Dashboard listo para importar

## 🚀 Uso Rápido

```bash
kubectl apply -n monitoring -f monitoring/prometheus-rules.yml
kubectl apply -n monitoring -f monitoring/alertmanager.yml
```

### Grafana Dashboard
1. Abrir Grafana (`http://localhost:3000`)
2. Import → Upload JSON file → seleccionar `grafana-dashboard.json`

## 🔔 Alertas Incluidas

| Alerta | Condición | Severidad |
|--------|-----------|-----------|
| `HighLatency` | p95 > 1s por 5m | warning |
| `HighErrorRate` | Error rate > 5% por 5m | critical |
| `HighCPU` | CPU > 80% por 10m | warning |
| `HPAThrottle` | Replica al máximo por 15m | warning |

## 🔧 Variables

- Actualiza `slack_api_url` en `alertmanager.yml`
- Ajusta thresholds según SLAs

## 🧪 Testing

```bash
kubectl -n monitoring port-forward svc/prometheus 9090:9090
kubectl -n monitoring port-forward svc/grafana 3000:3000
```

## ✅ Requisitos

- Prometheus Operator o kube-prometheus-stack
- Grafana 9+
- Alertmanager configurado

---

**Tip:** usa `helm upgrade --install monitoring prometheus-community/kube-prometheus-stack -f monitoring/values.yaml` y agrega estos archivos como `extraConfig`. 




