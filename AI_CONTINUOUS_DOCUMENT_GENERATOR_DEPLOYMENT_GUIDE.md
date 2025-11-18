# AI Continuous Document Generator - Guía de Despliegue

## 1. Requisitos Previos

### 1.1 Herramientas Necesarias
- **Docker**: Versión 20.10 o superior
- **Docker Compose**: Versión 2.0 o superior
- **Kubernetes**: Versión 1.24 o superior (para producción)
- **kubectl**: Para gestión de Kubernetes
- **Helm**: Versión 3.0 o superior (opcional)
- **Git**: Para clonar el repositorio

### 1.2 Servicios Externos
- **Base de Datos**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Almacenamiento**: AWS S3, Google Cloud Storage, o Azure Blob
- **APIs de IA**: OpenAI, Anthropic, o modelos locales
- **Dominio**: Para producción (opcional)

## 2. Configuración del Entorno

### 2.1 Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/documents
REDIS_URL=redis://localhost:6379

# JWT Secrets (generar con: openssl rand -hex 32)
JWT_ACCESS_SECRET=your-access-secret-here
JWT_REFRESH_SECRET=your-refresh-secret-here

# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Almacenamiento
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1

# Configuración de la aplicación
NODE_ENV=production
PORT=3000
API_BASE_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Logging
LOG_LEVEL=info
SECURITY_LOG_LEVEL=warn

# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### 2.2 Generar Claves de Seguridad
```bash
# Generar JWT secrets
openssl rand -hex 32  # Para JWT_ACCESS_SECRET
openssl rand -hex 32  # Para JWT_REFRESH_SECRET

# Generar clave de encriptación
openssl rand -hex 32  # Para ENCRYPTION_KEY
```

## 3. Despliegue Local con Docker

### 3.1 Estructura del Proyecto
```
document-generator/
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env
├── .env.example
├── api-gateway/
│   ├── Dockerfile
│   └── src/
├── services/
│   ├── document-service/
│   ├── ai-service/
│   ├── auth-service/
│   └── user-service/
├── frontend/
│   ├── Dockerfile
│   └── src/
└── k8s/
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    └── deployments/
```

### 3.2 Docker Compose para Desarrollo
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Base de datos
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: documents
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # API Gateway
  api-gateway:
    build: ./api-gateway
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/documents
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./api-gateway:/app
      - /app/node_modules

  # Document Service
  document-service:
    build: ./services/document-service
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/documents
    depends_on:
      - postgres
    volumes:
      - ./services/document-service:/app
      - /app/node_modules

  # AI Service
  ai-service:
    build: ./services/ai-service
    environment:
      - NODE_ENV=development
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./services/ai-service:/app
      - /app/node_modules

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3001:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:3000
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
  redis_data:
```

### 3.3 Comandos de Despliegue Local
```bash
# Clonar el repositorio
git clone https://github.com/your-org/document-generator.git
cd document-generator

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Construir y ejecutar
docker-compose up --build

# En modo detached
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar servicios
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

## 4. Despliegue en Producción

### 4.1 Docker Compose para Producción
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api-gateway
      - frontend

  # API Gateway
  api-gateway:
    build: 
      context: ./api-gateway
      dockerfile: Dockerfile.prod
    environment:
      - NODE_ENV=production
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Document Service
  document-service:
    build: 
      context: ./services/document-service
      dockerfile: Dockerfile.prod
    environment:
      - NODE_ENV=production
    depends_on:
      - postgres
    restart: unless-stopped

  # AI Service
  ai-service:
    build: 
      context: ./services/ai-service
      dockerfile: Dockerfile.prod
    environment:
      - NODE_ENV=production
    restart: unless-stopped

  # Frontend
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NODE_ENV=production
    restart: unless-stopped

  # Base de datos (usar servicio gestionado en producción)
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: documents
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Redis (usar servicio gestionado en producción)
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 4.2 Dockerfile de Producción
```dockerfile
# api-gateway/Dockerfile.prod
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:18-alpine AS production

WORKDIR /app

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

USER nodejs

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### 4.3 Configuración de Nginx
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api-gateway:3000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # API routes
        location /api/ {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 5. Despliegue en Kubernetes

### 5.1 Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: document-generator
  labels:
    name: document-generator
```

### 5.2 ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: document-generator
data:
  NODE_ENV: "production"
  API_BASE_URL: "https://api.yourdomain.com"
  FRONTEND_URL: "https://yourdomain.com"
  ALLOWED_ORIGINS: "https://yourdomain.com,https://www.yourdomain.com"
  RATE_LIMIT_WINDOW_MS: "900000"
  RATE_LIMIT_MAX_REQUESTS: "100"
  LOG_LEVEL: "info"
  SECURITY_LOG_LEVEL: "warn"
```

### 5.3 Secrets
```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: document-generator
type: Opaque
data:
  # Base64 encoded values
  DATABASE_URL: <base64-encoded-database-url>
  REDIS_URL: <base64-encoded-redis-url>
  JWT_ACCESS_SECRET: <base64-encoded-jwt-secret>
  JWT_REFRESH_SECRET: <base64-encoded-refresh-secret>
  OPENAI_API_KEY: <base64-encoded-openai-key>
  ANTHROPIC_API_KEY: <base64-encoded-anthropic-key>
  AWS_ACCESS_KEY_ID: <base64-encoded-aws-key>
  AWS_SECRET_ACCESS_KEY: <base64-encoded-aws-secret>
  AWS_S3_BUCKET: <base64-encoded-bucket-name>
```

### 5.4 Deployment de API Gateway
```yaml
# k8s/deployments/api-gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: document-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: your-registry/document-generator-api:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: NODE_ENV
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: REDIS_URL
        - name: JWT_ACCESS_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: JWT_ACCESS_SECRET
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway-service
  namespace: document-generator
spec:
  selector:
    app: api-gateway
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
```

### 5.5 Ingress
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: document-generator-ingress
  namespace: document-generator
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: document-generator-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: api-gateway-service
            port:
              number: 80
  - host: www.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

### 5.6 Comandos de Despliegue en Kubernetes
```bash
# Aplicar configuración
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Desplegar servicios
kubectl apply -f k8s/deployments/

# Verificar despliegue
kubectl get pods -n document-generator
kubectl get services -n document-generator
kubectl get ingress -n document-generator

# Ver logs
kubectl logs -f deployment/api-gateway -n document-generator

# Escalar servicios
kubectl scale deployment api-gateway --replicas=5 -n document-generator
```

## 6. CI/CD Pipeline

### 6.1 GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Run linting
      run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t your-registry/document-generator-api:${{ github.sha }} ./api-gateway
        docker build -t your-registry/document-generator-frontend:${{ github.sha }} ./frontend
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push your-registry/document-generator-api:${{ github.sha }}
        docker push your-registry/document-generator-frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.24.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to Kubernetes
      run: |
        # Update image tags
        sed -i "s|:latest|:${{ github.sha }}|g" k8s/deployments/*.yaml
        
        # Apply configurations
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/deployments/
        kubectl apply -f k8s/ingress.yaml
        
        # Wait for rollout
        kubectl rollout status deployment/api-gateway -n document-generator
        kubectl rollout status deployment/frontend -n document-generator
```

### 6.2 Scripts de Despliegue
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Variables
ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}
NAMESPACE="document-generator-${ENVIRONMENT}"

echo "Deploying to ${ENVIRONMENT} environment with version ${VERSION}"

# Build and push images
docker build -t your-registry/document-generator-api:${VERSION} ./api-gateway
docker build -t your-registry/document-generator-frontend:${VERSION} ./frontend

docker push your-registry/document-generator-api:${VERSION}
docker push your-registry/document-generator-frontend:${VERSION}

# Update Kubernetes manifests
sed -i "s|:latest|:${VERSION}|g" k8s/deployments/*.yaml
sed -i "s|namespace: document-generator|namespace: ${NAMESPACE}|g" k8s/deployments/*.yaml

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/ingress.yaml

# Wait for rollout
kubectl rollout status deployment/api-gateway -n ${NAMESPACE}
kubectl rollout status deployment/frontend -n ${NAMESPACE}

echo "Deployment completed successfully!"
```

## 7. Monitoreo y Logging

### 7.1 Health Checks
```javascript
// api-gateway/src/health.js
const express = require('express');
const router = express.Router();

router.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    services: {}
  };

  try {
    // Check database
    await sequelize.authenticate();
    health.services.database = 'healthy';
  } catch (error) {
    health.services.database = 'unhealthy';
    health.status = 'unhealthy';
  }

  try {
    // Check Redis
    await redis.ping();
    health.services.redis = 'healthy';
  } catch (error) {
    health.services.redis = 'unhealthy';
    health.status = 'unhealthy';
  }

  const statusCode = health.status === 'healthy' ? 200 : 503;
  res.status(statusCode).json(health);
});

router.get('/ready', async (req, res) => {
  // Check if service is ready to accept traffic
  res.status(200).json({ status: 'ready' });
});

module.exports = router;
```

### 7.2 Prometheus Metrics
```javascript
// shared/monitoring/metrics.js
const prometheus = require('prom-client');

// Create a Registry
const register = new prometheus.Registry();

// Add default metrics
prometheus.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

const httpRequestTotal = new prometheus.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const aiGenerationDuration = new prometheus.Histogram({
  name: 'ai_generation_duration_seconds',
  help: 'Duration of AI content generation',
  labelNames: ['model', 'template'],
  buckets: [1, 2, 5, 10, 30, 60]
});

register.registerMetric(httpRequestDuration);
register.registerMetric(httpRequestTotal);
register.registerMetric(aiGenerationDuration);

module.exports = { register, httpRequestDuration, httpRequestTotal, aiGenerationDuration };
```

## 8. Backup y Recuperación

### 8.1 Backup de Base de Datos
```bash
#!/bin/bash
# scripts/backup-db.sh

# Variables
DB_HOST="your-db-host"
DB_NAME="documents"
DB_USER="postgres"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/documents_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/documents_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/documents_$DATE.sql.gz s3://your-backup-bucket/database/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "documents_*.sql.gz" -mtime +30 -delete

echo "Backup completed: documents_$DATE.sql.gz"
```

### 8.2 Restauración de Base de Datos
```bash
#!/bin/bash
# scripts/restore-db.sh

BACKUP_FILE=$1
DB_HOST="your-db-host"
DB_NAME="documents"
DB_USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file>"
    exit 1
fi

# Download from S3 if needed
if [[ $BACKUP_FILE == s3://* ]]; then
    aws s3 cp $BACKUP_FILE /tmp/backup.sql.gz
    BACKUP_FILE="/tmp/backup.sql.gz"
fi

# Restore database
gunzip -c $BACKUP_FILE | psql -h $DB_HOST -U $DB_USER -d $DB_NAME

echo "Database restored from $BACKUP_FILE"
```

## 9. Troubleshooting

### 9.1 Problemas Comunes

#### Error de Conexión a Base de Datos
```bash
# Verificar conectividad
kubectl exec -it deployment/api-gateway -n document-generator -- nc -zv postgres 5432

# Verificar logs
kubectl logs deployment/api-gateway -n document-generator | grep -i database
```

#### Error de Memoria
```bash
# Verificar uso de memoria
kubectl top pods -n document-generator

# Aumentar límites de memoria
kubectl patch deployment api-gateway -n document-generator -p '{"spec":{"template":{"spec":{"containers":[{"name":"api-gateway","resources":{"limits":{"memory":"1Gi"}}}]}}}}'
```

#### Error de Rate Limiting
```bash
# Verificar configuración de Redis
kubectl exec -it deployment/redis -n document-generator -- redis-cli info

# Limpiar rate limits
kubectl exec -it deployment/redis -n document-generator -- redis-cli flushdb
```

### 9.2 Comandos de Diagnóstico
```bash
# Ver estado de todos los pods
kubectl get pods -n document-generator -o wide

# Ver logs de todos los servicios
kubectl logs -l app=api-gateway -n document-generator --tail=100

# Ver eventos del namespace
kubectl get events -n document-generator --sort-by='.lastTimestamp'

# Verificar recursos
kubectl describe deployment api-gateway -n document-generator

# Verificar servicios
kubectl get svc -n document-generator

# Verificar ingress
kubectl describe ingress document-generator-ingress -n document-generator
```

Esta guía de despliegue proporciona instrucciones completas para desplegar el sistema de generación de documentos con IA en diferentes entornos, desde desarrollo local hasta producción en Kubernetes.







