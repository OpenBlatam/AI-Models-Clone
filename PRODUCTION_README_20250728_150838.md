# 🚀 Guía de Despliegue en Producción - Servicio SEO

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Configuración Inicial](#configuración-inicial)
3. [Despliegue con Docker](#despliegue-con-docker)
4. [Configuración de Seguridad](#configuración-de-seguridad)
5. [Monitoreo y Métricas](#monitoreo-y-métricas)
6. [Backup y Recuperación](#backup-y-recuperación)
7. [Escalabilidad](#escalabilidad)
8. [Troubleshooting](#troubleshooting)
9. [Mantenimiento](#mantenimiento)

## 🖥️ Requisitos del Sistema

### Requisitos Mínimos
- **CPU**: 4 cores
- **RAM**: 8GB
- **Almacenamiento**: 50GB SSD
- **Red**: 100 Mbps

### Requisitos Recomendados
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Almacenamiento**: 100GB+ SSD
- **Red**: 1 Gbps

### Software Requerido
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl
- openssl

## ⚙️ Configuración Inicial

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd seo-service
```

### 2. Configurar Variables de Entorno
```bash
# Copiar archivo de configuración
cp env.production .env

# Editar variables críticas
nano .env
```

**Variables Críticas a Configurar:**
```bash
# Seguridad
SECRET_KEY=your-super-secret-key-here
DOMAIN=your-domain.com

# APIs
OPENAI_API_KEY=your-openai-api-key
SENTRY_DSN=your-sentry-dsn

# Monitoreo
GRAFANA_PASSWORD=your-secure-password
```

### 3. Generar Certificados SSL
```bash
# Para desarrollo (autofirmados)
./deploy.sh

# Para producción (Let's Encrypt)
certbot certonly --standalone -d your-domain.com
```

## 🐳 Despliegue con Docker

### Despliegue Automático
```bash
# Desplegar todo el stack
./deploy.sh deploy

# Verificar estado
./deploy.sh status

# Ver logs
./deploy.sh logs seo-service
```

### Despliegue Manual
```bash
# Construir imágenes
docker-compose build --no-cache

# Levantar servicios
docker-compose up -d

# Verificar servicios
docker-compose ps
```

### Servicios Incluidos
- **seo-service**: API principal
- **redis**: Cache y rate limiting
- **prometheus**: Métricas
- **grafana**: Visualización
- **nginx**: Reverse proxy
- **elasticsearch**: Logs
- **kibana**: Visualización de logs
- **filebeat**: Recolección de logs

## 🔒 Configuración de Seguridad

### 1. Firewall
```bash
# Configurar UFW
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 2. SSL/TLS
```bash
# Configurar certificados en nginx.conf
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### 3. Headers de Seguridad
Los siguientes headers están configurados automáticamente:
- `X-Frame-Options: SAMEORIGIN`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy`

### 4. Rate Limiting
```nginx
# Configurado en nginx.conf
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

### 5. User Agents Maliciosos
```nginx
# Bloquear bots maliciosos
if ($http_user_agent ~* (curl|wget|scraper|bot|spider|crawler)) {
    return 403;
}
```

## 📊 Monitoreo y Métricas

### 1. Prometheus
- **URL**: http://localhost:9091
- **Configuración**: `prometheus.yml`
- **Métricas recolectadas**:
  - Request rate
  - Response time
  - Error rate
  - Cache hit/miss ratio
  - System resources

### 2. Grafana
- **URL**: http://localhost:3000
- **Usuario**: admin
- **Contraseña**: Configurada en `.env`
- **Dashboards incluidos**:
  - SEO Service Overview
  - Performance Metrics
  - Error Analysis
  - System Resources

### 3. Health Checks
```bash
# Verificar salud del sistema
curl http://localhost/health

# Verificar métricas
curl http://localhost/metrics

# Verificar estado
curl http://localhost/status
```

### 4. Logs
```bash
# Ver logs en tiempo real
docker-compose logs -f seo-service

# Ver logs de nginx
docker-compose logs -f nginx

# Ver logs en Kibana
# URL: http://localhost:5601
```

## 💾 Backup y Recuperación

### Backup Automático
```bash
# Crear backup manual
./deploy.sh backup

# Los backups se guardan en: backups/YYYYMMDD_HHMMSS/
```

### Backup Programado
```bash
# Agregar al crontab
0 2 * * * /path/to/seo-service/deploy.sh backup
```

### Recuperación
```bash
# Rollback a versión anterior
./deploy.sh rollback

# Restaurar backup específico
tar xzf backups/20240101_120000/redis-data.tar.gz
tar xzf backups/20240101_120000/logs.tar.gz
```

## 📈 Escalabilidad

### Escalado Horizontal
```bash
# Escalar servicio principal
docker-compose up -d --scale seo-service=3

# Escalar con load balancer
docker-compose up -d --scale seo-service=5
```

### Configuración de Load Balancer
```nginx
upstream seo_backend {
    server seo-service:8000 weight=1;
    server seo-service:8001 weight=1;
    server seo-service:8002 weight=1;
}
```

### Redis Cluster
```yaml
# Para alta disponibilidad
redis-cluster:
  image: redis:7-alpine
  command: redis-server --cluster-enabled yes
  ports:
    - "7000-7005:7000-7005"
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Servicio no inicia
```bash
# Verificar logs
docker-compose logs seo-service

# Verificar configuración
docker-compose config

# Verificar recursos
docker stats
```

#### 2. Errores de memoria
```bash
# Aumentar límites de memoria
docker-compose down
docker system prune -f
docker-compose up -d
```

#### 3. Problemas de red
```bash
# Verificar conectividad
docker-compose exec seo-service ping redis
docker-compose exec seo-service curl -f http://localhost:8000/health
```

#### 4. Problemas de SSL
```bash
# Verificar certificados
openssl x509 -in ssl/cert.pem -text -noout

# Regenerar certificados
./deploy.sh
```

### Comandos de Diagnóstico
```bash
# Estado general
./deploy.sh status

# Health check completo
./deploy.sh health

# Limpiar recursos
./deploy.sh cleanup

# Ver logs específicos
./deploy.sh logs seo-service
```

## 🛠️ Mantenimiento

### Actualizaciones
```bash
# Actualizar código
git pull origin main

# Reconstruir y desplegar
./deploy.sh deploy

# Verificar cambios
./deploy.sh health
```

### Limpieza Regular
```bash
# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +30 -delete

# Limpiar cache
docker-compose exec redis redis-cli FLUSHDB

# Limpiar Docker
docker system prune -f
```

### Monitoreo Continuo
```bash
# Script de monitoreo
#!/bin/bash
while true; do
    if ! curl -f http://localhost/health > /dev/null; then
        echo "Service down at $(date)" >> /var/log/seo-monitor.log
        ./deploy.sh deploy
    fi
    sleep 60
done
```

## 📞 Soporte

### Contactos
- **Desarrollador**: [Tu Email]
- **DevOps**: [DevOps Email]
- **Documentación**: [Wiki URL]

### Recursos Adicionales
- [Documentación de la API](./README.md)
- [Guía de Desarrollo](./DEVELOPMENT.md)
- [Changelog](./CHANGELOG.md)

### Logs de Auditoría
```bash
# Ver logs de auditoría
tail -f logs/audit.log

# Buscar errores críticos
grep -i "error\|critical" logs/*.log
```

---

## 🎯 Checklist de Despliegue

- [ ] Variables de entorno configuradas
- [ ] Certificados SSL generados
- [ ] Firewall configurado
- [ ] Servicios desplegados
- [ ] Health checks pasando
- [ ] Métricas funcionando
- [ ] Logs configurados
- [ ] Backup configurado
- [ ] Monitoreo activo
- [ ] Documentación actualizada

## 📈 Métricas de Rendimiento Esperadas

- **Response Time**: < 2s promedio
- **Throughput**: 100+ requests/segundo
- **Uptime**: 99.9%
- **Error Rate**: < 0.1%
- **Cache Hit Rate**: > 80%

---

**¡El servicio está listo para producción! 🚀** 