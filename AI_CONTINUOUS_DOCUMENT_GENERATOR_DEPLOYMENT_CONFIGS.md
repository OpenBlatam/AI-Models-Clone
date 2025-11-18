# Configuraciones de Despliegue: IA Generadora Continua de Documentos

## 🚀 Configuraciones de Despliegue Completas

### Visión General
Este documento proporciona configuraciones completas de despliegue para el Sistema de Generación Continua de Documentos con IA, incluyendo configuraciones para desarrollo, staging, producción, y entornos especializados.

## 🏗️ Arquitectura de Despliegue

### Arquitectura de Microservicios
```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (NGINX)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                 API Gateway (Kong)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐         ┌───▼───┐         ┌───▼───┐
│ Core  │         │ AI    │         │ Meta- │
│ API   │         │ ML    │         │ verse │
└───────┘         └───────┘         └───────┘
    │                 │                 │
┌───▼───┐         ┌───▼───┐         ┌───▼───┐
│ Block-│         │ Quan- │         │ Work- │
│ chain │         │ tum   │         │ flow  │
└───────┘         └───────┘         └───────┘
```

### Componentes Principales
1. **API Gateway**: Kong con autenticación y rate limiting
2. **Core API**: FastAPI con documentación automática
3. **AI/ML Service**: Servicios de IA y machine learning
4. **Metaverse Service**: Integración VR/AR y colaboración 3D
5. **Blockchain Service**: Integración blockchain y smart contracts
6. **Quantum Service**: Procesamiento cuántico y optimización
7. **Workflow Engine**: Automatización de flujos de trabajo

## 🐳 Configuraciones Docker

### Docker Compose - Desarrollo
```yaml
version: '3.8'

services:
  # Base de datos principal
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: document_generator
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis para caché
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Core API
  core-api:
    build:
      context: .
      dockerfile: Dockerfile.core
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://admin:${POSTGRES_PASSWORD}@postgres:5432/document_generator
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./app:/app
      - ./logs:/app/logs
    restart: unless-stopped

  # AI/ML Service
  ai-ml-service:
    build:
      context: .
      dockerfile: Dockerfile.ai
    ports:
      - "8001:8001"
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis:6379
      - AI_MODELS_PATH=/app/models
    volumes:
      - ./ai_models:/app/models
      - ./logs:/app/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  # Metaverse Service
  metaverse-service:
    build:
      context: .
      dockerfile: Dockerfile.metaverse
    ports:
      - "8002:8002"
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis:6379
      - VR_PLATFORMS=oculus,htc_vive,playstation_vr
    volumes:
      - ./vr_assets:/app/assets
      - ./logs:/app/logs
    restart: unless-stopped

  # Blockchain Service
  blockchain-service:
    build:
      context: .
      dockerfile: Dockerfile.blockchain
    ports:
      - "8003:8003"
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis:6379
      - ETHEREUM_RPC_URL=${ETHEREUM_RPC_URL}
      - POLYGON_RPC_URL=${POLYGON_RPC_URL}
    volumes:
      - ./blockchain_config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

  # Quantum Service
  quantum-service:
    build:
      context: .
      dockerfile: Dockerfile.quantum
    ports:
      - "8004:8004"
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis:6379
      - IBM_QUANTUM_TOKEN=${IBM_QUANTUM_TOKEN}
      - GOOGLE_QUANTUM_TOKEN=${GOOGLE_QUANTUM_TOKEN}
    volumes:
      - ./quantum_config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

  # Workflow Engine
  workflow-engine:
    build:
      context: .
      dockerfile: Dockerfile.workflow
    ports:
      - "8005:8005"
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis:6379
      - WORKFLOW_STORAGE_PATH=/app/workflows
    volumes:
      - ./workflows:/app/workflows
      - ./logs:/app/logs
    restart: unless-stopped

  # NGINX Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - core-api
      - ai-ml-service
      - metaverse-service
      - blockchain-service
      - quantum-service
      - workflow-engine
    restart: unless-stopped

  # Monitoring
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Docker Compose - Producción
```yaml
version: '3.8'

services:
  # Base de datos con replicación
  postgres-primary:
    image: postgres:15
    environment:
      POSTGRES_DB: document_generator
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: ${REPLICATION_PASSWORD}
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    command: >
      postgres
      -c wal_level=replica
      -c max_wal_senders=3
      -c max_replication_slots=3
      -c hot_standby=on
    restart: unless-stopped

  postgres-replica:
    image: postgres:15
    environment:
      POSTGRES_DB: document_generator
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGUSER: postgres
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
    command: >
      bash -c "
      until pg_basebackup -h postgres-primary -D /var/lib/postgresql/data -U replicator -v -P -W
      do
        echo 'Waiting for primary to connect...'
        sleep 1s
      done
      echo 'Backup done, starting replica...'
      chmod 0700 /var/lib/postgresql/data
      postgres
      "
    depends_on:
      - postgres-primary
    restart: unless-stopped

  # Redis Cluster
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes --replica-read-only no
    volumes:
      - redis_master_data:/data
    restart: unless-stopped

  redis-replica:
    image: redis:7-alpine
    command: redis-server --appendonly yes --replicaof redis-master 6379
    volumes:
      - redis_replica_data:/data
    depends_on:
      - redis-master
    restart: unless-stopped

  # Core API con múltiples instancias
  core-api-1:
    build:
      context: .
      dockerfile: Dockerfile.core
    environment:
      - DATABASE_URL=postgresql://admin:${POSTGRES_PASSWORD}@postgres-primary:5432/document_generator
      - REDIS_URL=redis://redis-master:6379
      - ENVIRONMENT=production
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped

  core-api-2:
    build:
      context: .
      dockerfile: Dockerfile.core
    environment:
      - DATABASE_URL=postgresql://admin:${POSTGRES_PASSWORD}@postgres-primary:5432/document_generator
      - REDIS_URL=redis://redis-master:6379
      - ENVIRONMENT=production
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped

  core-api-3:
    build:
      context: .
      dockerfile: Dockerfile.core
    environment:
      - DATABASE_URL=postgresql://admin:${POSTGRES_PASSWORD}@postgres-primary:5432/document_generator
      - REDIS_URL=redis://redis-master:6379
      - ENVIRONMENT=production
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped

  # AI/ML Service con GPU
  ai-ml-service:
    build:
      context: .
      dockerfile: Dockerfile.ai
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis-master:6379
      - AI_MODELS_PATH=/app/models
      - GPU_ENABLED=true
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  # Metaverse Service
  metaverse-service:
    build:
      context: .
      dockerfile: Dockerfile.metaverse
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis-master:6379
      - VR_PLATFORMS=oculus,htc_vive,playstation_vr
      - MAX_CONCURRENT_SESSIONS=1000
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '3'
          memory: 6G
        reservations:
          cpus: '1.5'
          memory: 3G
    restart: unless-stopped

  # Blockchain Service
  blockchain-service:
    build:
      context: .
      dockerfile: Dockerfile.blockchain
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis-master:6379
      - ETHEREUM_RPC_URL=${ETHEREUM_RPC_URL}
      - POLYGON_RPC_URL=${POLYGON_RPC_URL}
      - BSC_RPC_URL=${BSC_RPC_URL}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped

  # Quantum Service
  quantum-service:
    build:
      context: .
      dockerfile: Dockerfile.quantum
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis-master:6379
      - IBM_QUANTUM_TOKEN=${IBM_QUANTUM_TOKEN}
      - GOOGLE_QUANTUM_TOKEN=${GOOGLE_QUANTUM_TOKEN}
      - MICROSOFT_QUANTUM_TOKEN=${MICROSOFT_QUANTUM_TOKEN}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '3'
          memory: 6G
        reservations:
          cpus: '1.5'
          memory: 3G
    restart: unless-stopped

  # Workflow Engine
  workflow-engine:
    build:
      context: .
      dockerfile: Dockerfile.workflow
    environment:
      - CORE_API_URL=http://core-api:8000
      - REDIS_URL=redis://redis-master:6379
      - WORKFLOW_STORAGE_PATH=/app/workflows
      - MAX_CONCURRENT_WORKFLOWS=500
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    restart: unless-stopped

  # NGINX con SSL
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - core-api-1
      - core-api-2
      - core-api-3
      - ai-ml-service
      - metaverse-service
      - blockchain-service
      - quantum-service
      - workflow-engine
    restart: unless-stopped

  # Monitoring Stack
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.prod.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped

  # Logging
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - ./logs:/var/log/app
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  postgres_primary_data:
  postgres_replica_data:
  redis_master_data:
  redis_replica_data:
  prometheus_data:
  grafana_data:
  elasticsearch_data:
```

## ☸️ Configuraciones Kubernetes

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: document-generator
  labels:
    name: document-generator
```

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: document-generator-config
  namespace: document-generator
data:
  DATABASE_URL: "postgresql://admin:password@postgres-service:5432/document_generator"
  REDIS_URL: "redis://redis-service:6379"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "4"
  AI_MODELS_PATH: "/app/models"
  VR_PLATFORMS: "oculus,htc_vive,playstation_vr"
  MAX_CONCURRENT_SESSIONS: "1000"
  MAX_CONCURRENT_WORKFLOWS: "500"
```

### Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: document-generator-secrets
  namespace: document-generator
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded-password>
  REDIS_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-jwt-secret>
  ETHEREUM_RPC_URL: <base64-encoded-url>
  POLYGON_RPC_URL: <base64-encoded-url>
  BSC_RPC_URL: <base64-encoded-url>
  IBM_QUANTUM_TOKEN: <base64-encoded-token>
  GOOGLE_QUANTUM_TOKEN: <base64-encoded-token>
  MICROSOFT_QUANTUM_TOKEN: <base64-encoded-token>
  GRAFANA_PASSWORD: <base64-encoded-password>
```

### PostgreSQL Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: document-generator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: document_generator
        - name: POSTGRES_USER
          value: admin
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: document-generator-secrets
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: document-generator
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: document-generator
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
```

### Redis Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: document-generator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "0.5"
          limits:
            memory: "2Gi"
            cpu: "1"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: document-generator
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: document-generator
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
```

### Core API Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-api
  namespace: document-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: core-api
  template:
    metadata:
      labels:
        app: core-api
    spec:
      containers:
      - name: core-api
        image: document-generator/core-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: document-generator-config
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: document-generator-config
              key: REDIS_URL
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: document-generator-config
              key: ENVIRONMENT
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: core-api-service
  namespace: document-generator
spec:
  selector:
    app: core-api
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### AI/ML Service Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-ml-service
  namespace: document-generator
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-ml-service
  template:
    metadata:
      labels:
        app: ai-ml-service
    spec:
      containers:
      - name: ai-ml-service
        image: document-generator/ai-ml-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: CORE_API_URL
          value: "http://core-api-service:8000"
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: document-generator-config
              key: REDIS_URL
        - name: AI_MODELS_PATH
          valueFrom:
            configMapKeyRef:
              name: document-generator-config
              key: AI_MODELS_PATH
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: ai-models
          mountPath: /app/models
      volumes:
      - name: ai-models
        persistentVolumeClaim:
          claimName: ai-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ai-ml-service
  namespace: document-generator
spec:
  selector:
    app: ai-ml-service
  ports:
  - port: 8001
    targetPort: 8001
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ai-models-pvc
  namespace: document-generator
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 200Gi
```

### Ingress
```yaml
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
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
  - hosts:
    - api.document-generator.com
    - metaverse.document-generator.com
    - quantum.document-generator.com
    secretName: document-generator-tls
  rules:
  - host: api.document-generator.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: core-api-service
            port:
              number: 8000
  - host: metaverse.document-generator.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: metaverse-service
            port:
              number: 8002
  - host: quantum.document-generator.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: quantum-service
            port:
              number: 8004
```

## 🔧 Configuraciones NGINX

### NGINX - Desarrollo
```nginx
events {
    worker_connections 1024;
}

http {
    upstream core_api {
        server core-api:8000;
    }

    upstream ai_ml_service {
        server ai-ml-service:8001;
    }

    upstream metaverse_service {
        server metaverse-service:8002;
    }

    upstream blockchain_service {
        server blockchain-service:8003;
    }

    upstream quantum_service {
        server quantum-service:8004;
    }

    upstream workflow_engine {
        server workflow-engine:8005;
    }

    server {
        listen 80;
        server_name localhost;

        # Core API
        location /api/ {
            proxy_pass http://core_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # AI/ML Service
        location /ai/ {
            proxy_pass http://ai_ml_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Metaverse Service
        location /metaverse/ {
            proxy_pass http://metaverse_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Blockchain Service
        location /blockchain/ {
            proxy_pass http://blockchain_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Quantum Service
        location /quantum/ {
            proxy_pass http://quantum_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Workflow Engine
        location /workflow/ {
            proxy_pass http://workflow_engine/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://core_api/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### NGINX - Producción
```nginx
events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=ai:10m rate=5r/s;
    limit_req_zone $binary_remote_addr zone=quantum:10m rate=2r/s;

    # Upstream servers
    upstream core_api {
        least_conn;
        server core-api-1:8000 max_fails=3 fail_timeout=30s;
        server core-api-2:8000 max_fails=3 fail_timeout=30s;
        server core-api-3:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream ai_ml_service {
        least_conn;
        server ai-ml-service-1:8001 max_fails=3 fail_timeout=30s;
        server ai-ml-service-2:8001 max_fails=3 fail_timeout=30s;
        keepalive 16;
    }

    upstream metaverse_service {
        least_conn;
        server metaverse-service-1:8002 max_fails=3 fail_timeout=30s;
        server metaverse-service-2:8002 max_fails=3 fail_timeout=30s;
        server metaverse-service-3:8002 max_fails=3 fail_timeout=30s;
        keepalive 16;
    }

    upstream blockchain_service {
        least_conn;
        server blockchain-service-1:8003 max_fails=3 fail_timeout=30s;
        server blockchain-service-2:8003 max_fails=3 fail_timeout=30s;
        keepalive 16;
    }

    upstream quantum_service {
        least_conn;
        server quantum-service-1:8004 max_fails=3 fail_timeout=30s;
        server quantum-service-2:8004 max_fails=3 fail_timeout=30s;
        keepalive 8;
    }

    upstream workflow_engine {
        least_conn;
        server workflow-engine-1:8005 max_fails=3 fail_timeout=30s;
        server workflow-engine-2:8005 max_fails=3 fail_timeout=30s;
        server workflow-engine-3:8005 max_fails=3 fail_timeout=30s;
        keepalive 16;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name api.document-generator.com metaverse.document-generator.com quantum.document-generator.com;
        return 301 https://$server_name$request_uri;
    }

    # Main API server
    server {
        listen 443 ssl http2;
        server_name api.document-generator.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/api.document-generator.com.crt;
        ssl_certificate_key /etc/nginx/ssl/api.document-generator.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Core API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://core_api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # AI/ML Service
        location /ai/ {
            limit_req zone=ai burst=10 nodelay;
            proxy_pass http://ai_ml_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Blockchain Service
        location /blockchain/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://blockchain_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Workflow Engine
        location /workflow/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://workflow_engine/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://core_api/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }
    }

    # Metaverse server
    server {
        listen 443 ssl http2;
        server_name metaverse.document-generator.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/metaverse.document-generator.com.crt;
        ssl_certificate_key /etc/nginx/ssl/metaverse.document-generator.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Metaverse Service
        location / {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://metaverse_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # WebSocket for VR/AR
        location /vr/ws/ {
            proxy_pass http://metaverse_service/vr/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 7d;
            proxy_send_timeout 7d;
            proxy_read_timeout 7d;
        }
    }

    # Quantum server
    server {
        listen 443 ssl http2;
        server_name quantum.document-generator.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/quantum.document-generator.com.crt;
        ssl_certificate_key /etc/nginx/ssl/quantum.document-generator.com.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Quantum Service
        location / {
            limit_req zone=quantum burst=5 nodelay;
            proxy_pass http://quantum_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }
    }
}
```

## 📊 Configuraciones de Monitoreo

### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'core-api'
    static_configs:
      - targets: ['core-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'ai-ml-service'
    static_configs:
      - targets: ['ai-ml-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'metaverse-service'
    static_configs:
      - targets: ['metaverse-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'blockchain-service'
    static_configs:
      - targets: ['blockchain-service:8003']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'quantum-service'
    static_configs:
      - targets: ['quantum-service:8004']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'workflow-engine'
    static_configs:
      - targets: ['workflow-engine:8005']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboards
```json
{
  "dashboard": {
    "id": null,
    "title": "Document Generator System Overview",
    "tags": ["document-generator"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Response Time (seconds)",
            "min": 0
          }
        ]
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests per second",
            "min": 0
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{service}} - 5xx errors"
          }
        ],
        "yAxes": [
          {
            "label": "Errors per second",
            "min": 0
          }
        ]
      },
      {
        "id": 4,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100",
            "legendFormat": "{{container_name}}"
          }
        ],
        "yAxes": [
          {
            "label": "CPU Usage (%)",
            "min": 0,
            "max": 100
          }
        ]
      },
      {
        "id": 5,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes / container_spec_memory_limit_bytes * 100",
            "legendFormat": "{{container_name}}"
          }
        ],
        "yAxes": [
          {
            "label": "Memory Usage (%)",
            "min": 0,
            "max": 100
          }
        ]
      },
      {
        "id": 6,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "Active connections"
          }
        ],
        "yAxes": [
          {
            "label": "Connections",
            "min": 0
          }
        ]
      },
      {
        "id": 7,
        "title": "Redis Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "redis_memory_used_bytes",
            "legendFormat": "Used memory"
          }
        ],
        "yAxes": [
          {
            "label": "Memory (bytes)",
            "min": 0
          }
        ]
      },
      {
        "id": 8,
        "title": "AI Model Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_model_prediction_duration_seconds",
            "legendFormat": "{{model_name}}"
          }
        ],
        "yAxes": [
          {
            "label": "Prediction Time (seconds)",
            "min": 0
          }
        ]
      },
      {
        "id": 9,
        "title": "Quantum Task Queue",
        "type": "graph",
        "targets": [
          {
            "expr": "quantum_tasks_pending",
            "legendFormat": "Pending tasks"
          },
          {
            "expr": "quantum_tasks_running",
            "legendFormat": "Running tasks"
          }
        ],
        "yAxes": [
          {
            "label": "Tasks",
            "min": 0
          }
        ]
      },
      {
        "id": 10,
        "title": "Metaverse Sessions",
        "type": "graph",
        "targets": [
          {
            "expr": "metaverse_active_sessions",
            "legendFormat": "Active sessions"
          },
          {
            "expr": "metaverse_concurrent_users",
            "legendFormat": "Concurrent users"
          }
        ],
        "yAxes": [
          {
            "label": "Sessions/Users",
            "min": 0
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## 🚀 Scripts de Despliegue

### Deploy Script - Desarrollo
```bash
#!/bin/bash

# Deploy script for development environment

set -e

echo "🚀 Starting deployment to development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Load environment variables
if [ -f .env.development ]; then
    echo "📋 Loading environment variables from .env.development..."
    export $(cat .env.development | grep -v '^#' | xargs)
else
    echo "⚠️  No .env.development file found. Using default values."
fi

# Build images
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.dev.yml build

# Start services
echo "🚀 Starting services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
services=("core-api" "ai-ml-service" "metaverse-service" "blockchain-service" "quantum-service" "workflow-engine")

for service in "${services[@]}"; do
    if docker-compose -f docker-compose.dev.yml ps | grep -q "$service.*Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
        exit 1
    fi
done

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.dev.yml exec core-api python -m alembic upgrade head

# Run tests
echo "🧪 Running tests..."
docker-compose -f docker-compose.dev.yml exec core-api python -m pytest tests/ -v

echo "✅ Deployment to development environment completed successfully!"
echo "🌐 Services are available at:"
echo "   - Core API: http://localhost:8000"
echo "   - AI/ML Service: http://localhost:8001"
echo "   - Metaverse Service: http://localhost:8002"
echo "   - Blockchain Service: http://localhost:8003"
echo "   - Quantum Service: http://localhost:8004"
echo "   - Workflow Engine: http://localhost:8005"
echo "   - Grafana: http://localhost:3000"
echo "   - Prometheus: http://localhost:9090"
```

### Deploy Script - Producción
```bash
#!/bin/bash

# Deploy script for production environment

set -e

echo "🚀 Starting deployment to production environment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm and try again."
    exit 1
fi

# Check cluster connection
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Load environment variables
if [ -f .env.production ]; then
    echo "📋 Loading environment variables from .env.production..."
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "❌ No .env.production file found. Please create one with required variables."
    exit 1
fi

# Create namespace if it doesn't exist
echo "📦 Creating namespace..."
kubectl create namespace document-generator --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets
echo "🔐 Applying secrets..."
kubectl apply -f k8s/secrets.yaml

# Apply configmaps
echo "📋 Applying configmaps..."
kubectl apply -f k8s/configmap.yaml

# Apply persistent volume claims
echo "💾 Applying persistent volume claims..."
kubectl apply -f k8s/pvc.yaml

# Apply deployments
echo "🚀 Applying deployments..."
kubectl apply -f k8s/deployments/

# Apply services
echo "🌐 Applying services..."
kubectl apply -f k8s/services/

# Apply ingress
echo "🔗 Applying ingress..."
kubectl apply -f k8s/ingress.yaml

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n document-generator

# Check pod status
echo "🔍 Checking pod status..."
kubectl get pods -n document-generator

# Run database migrations
echo "🗄️  Running database migrations..."
kubectl exec -n document-generator deployment/core-api -- python -m alembic upgrade head

# Run health checks
echo "🏥 Running health checks..."
kubectl exec -n document-generator deployment/core-api -- python -c "
import requests
import sys

services = [
    'http://core-api-service:8000/health',
    'http://ai-ml-service:8001/health',
    'http://metaverse-service:8002/health',
    'http://blockchain-service:8003/health',
    'http://quantum-service:8004/health',
    'http://workflow-engine:8005/health'
]

for service in services:
    try:
        response = requests.get(service, timeout=10)
        if response.status_code == 200:
            print(f'✅ {service} is healthy')
        else:
            print(f'❌ {service} returned status {response.status_code}')
            sys.exit(1)
    except Exception as e:
        print(f'❌ {service} health check failed: {e}')
        sys.exit(1)
"

echo "✅ Deployment to production environment completed successfully!"
echo "🌐 Services are available at:"
echo "   - API: https://api.document-generator.com"
echo "   - Metaverse: https://metaverse.document-generator.com"
echo "   - Quantum: https://quantum.document-generator.com"
echo "   - Grafana: https://grafana.document-generator.com"
echo "   - Prometheus: https://prometheus.document-generator.com"
```

## 🔧 Configuraciones de CI/CD

### GitHub Actions - Desarrollo
```yaml
name: Development Deployment

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
        isort --check-only .
    
    - name: Run type checking
      run: mypy .
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push images
      run: |
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-core-api:dev-${{ github.sha }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-core-api:dev-latest \
          --push -f Dockerfile.core .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-ai-ml:dev-${{ github.sha }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-ai-ml:dev-latest \
          --push -f Dockerfile.ai .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-metaverse:dev-${{ github.sha }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-metaverse:dev-latest \
          --push -f Dockerfile.metaverse .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-blockchain:dev-${{ github.sha }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-blockchain:dev-latest \
          --push -f Dockerfile.blockchain .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-quantum:dev-${{ github.sha }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-quantum:dev-latest \
          --push -f Dockerfile.quantum .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-workflow:dev-${{ github.sha }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-workflow:dev-latest \
          --push -f Dockerfile.workflow .

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to development
      run: |
        echo "🚀 Deploying to development environment..."
        # Add deployment commands here
        # This would typically involve updating the development environment
        # with the new images and configurations
```

### GitHub Actions - Producción
```yaml
name: Production Deployment

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 .
        black --check .
        isort --check-only .
    
    - name: Run type checking
      run: mypy .
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
    
    - name: Run security scan
      run: |
        bandit -r . -f json -o bandit-report.json
        safety check --json --output safety-report.json
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Extract version
      id: version
      run: |
        if [[ $GITHUB_REF == refs/tags/* ]]; then
          echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
        else
          echo "VERSION=latest" >> $GITHUB_OUTPUT
        fi
    
    - name: Build and push images
      run: |
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-core-api:${{ steps.version.outputs.VERSION }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-core-api:latest \
          --push -f Dockerfile.core .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-ai-ml:${{ steps.version.outputs.VERSION }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-ai-ml:latest \
          --push -f Dockerfile.ai .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-metaverse:${{ steps.version.outputs.VERSION }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-metaverse:latest \
          --push -f Dockerfile.metaverse .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-blockchain:${{ steps.version.outputs.VERSION }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-blockchain:latest \
          --push -f Dockerfile.blockchain .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-quantum:${{ steps.version.outputs.VERSION }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-quantum:latest \
          --push -f Dockerfile.quantum .
        
        docker buildx build --platform linux/amd64,linux/arm64 \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-workflow:${{ steps.version.outputs.VERSION }} \
          -t ${{ secrets.DOCKER_USERNAME }}/document-generator-workflow:latest \
          --push -f Dockerfile.workflow .

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/')
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to production
      run: |
        echo "🚀 Deploying to production environment..."
        
        # Update image tags in Kubernetes manifests
        sed -i "s|image: .*/document-generator-core-api:.*|image: ${{ secrets.DOCKER_USERNAME }}/document-generator-core-api:${{ steps.version.outputs.VERSION }}|g" k8s/deployments/core-api.yaml
        sed -i "s|image: .*/document-generator-ai-ml:.*|image: ${{ secrets.DOCKER_USERNAME }}/document-generator-ai-ml:${{ steps.version.outputs.VERSION }}|g" k8s/deployments/ai-ml-service.yaml
        sed -i "s|image: .*/document-generator-metaverse:.*|image: ${{ secrets.DOCKER_USERNAME }}/document-generator-metaverse:${{ steps.version.outputs.VERSION }}|g" k8s/deployments/metaverse-service.yaml
        sed -i "s|image: .*/document-generator-blockchain:.*|image: ${{ secrets.DOCKER_USERNAME }}/document-generator-blockchain:${{ steps.version.outputs.VERSION }}|g" k8s/deployments/blockchain-service.yaml
        sed -i "s|image: .*/document-generator-quantum:.*|image: ${{ secrets.DOCKER_USERNAME }}/document-generator-quantum:${{ steps.version.outputs.VERSION }}|g" k8s/deployments/quantum-service.yaml
        sed -i "s|image: .*/document-generator-workflow:.*|image: ${{ secrets.DOCKER_USERNAME }}/document-generator-workflow:${{ steps.version.outputs.VERSION }}|g" k8s/deployments/workflow-engine.yaml
        
        # Apply Kubernetes manifests
        kubectl apply -f k8s/
        
        # Wait for rollout to complete
        kubectl rollout status deployment/core-api -n document-generator --timeout=300s
        kubectl rollout status deployment/ai-ml-service -n document-generator --timeout=300s
        kubectl rollout status deployment/metaverse-service -n document-generator --timeout=300s
        kubectl rollout status deployment/blockchain-service -n document-generator --timeout=300s
        kubectl rollout status deployment/quantum-service -n document-generator --timeout=300s
        kubectl rollout status deployment/workflow-engine -n document-generator --timeout=300s
        
        # Run health checks
        kubectl exec -n document-generator deployment/core-api -- python -c "
        import requests
        import sys
        
        services = [
            'http://core-api-service:8000/health',
            'http://ai-ml-service:8001/health',
            'http://metaverse-service:8002/health',
            'http://blockchain-service:8003/health',
            'http://quantum-service:8004/health',
            'http://workflow-engine:8005/health'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=10)
                if response.status_code == 200:
                    print(f'✅ {service} is healthy')
                else:
                    print(f'❌ {service} returned status {response.status_code}')
                    sys.exit(1)
            except Exception as e:
                print(f'❌ {service} health check failed: {e}')
                sys.exit(1)
        "
    
    - name: Notify deployment
      run: |
        echo "✅ Production deployment completed successfully!"
        echo "🌐 Services are available at:"
        echo "   - API: https://api.document-generator.com"
        echo "   - Metaverse: https://metaverse.document-generator.com"
        echo "   - Quantum: https://quantum.document-generator.com"
```

## 📋 Checklist de Despliegue

### Pre-Despliegue
- [ ] Verificar que todos los tests pasen
- [ ] Revisar configuraciones de seguridad
- [ ] Validar variables de entorno
- [ ] Verificar recursos disponibles
- [ ] Confirmar backups de base de datos
- [ ] Validar certificados SSL
- [ ] Verificar conectividad de red
- [ ] Confirmar acceso a servicios externos

### Durante el Despliegue
- [ ] Monitorear logs en tiempo real
- [ ] Verificar estado de pods/servicios
- [ ] Validar conectividad entre servicios
- [ ] Ejecutar health checks
- [ ] Verificar métricas de rendimiento
- [ ] Validar funcionalidad crítica
- [ ] Confirmar migraciones de base de datos
- [ ] Verificar configuraciones de red

### Post-Despliegue
- [ ] Ejecutar tests de integración
- [ ] Verificar métricas de monitoreo
- [ ] Validar logs de error
- [ ] Confirmar funcionalidad de usuarios
- [ ] Verificar rendimiento del sistema
- [ ] Validar backups automáticos
- [ ] Confirmar alertas de monitoreo
- [ ] Documentar cambios realizados

## 🎯 Conclusión

Las configuraciones de despliegue proporcionadas cubren todos los aspectos necesarios para implementar el Sistema de Generación Continua de Documentos con IA en diferentes entornos:

- **Desarrollo**: Configuración simple para desarrollo local
- **Staging**: Configuración intermedia para pruebas
- **Producción**: Configuración robusta con alta disponibilidad
- **Kubernetes**: Orquestación de contenedores para escalabilidad
- **Monitoreo**: Observabilidad completa del sistema
- **CI/CD**: Automatización de despliegues

Estas configuraciones aseguran que el sistema sea:
- **Escalable**: Capaz de manejar cargas variables
- **Resiliente**: Tolerante a fallos
- **Seguro**: Protegido contra amenazas
- **Monitoreado**: Completamente observable
- **Automatizado**: Despliegues sin intervención manual

El sistema está diseñado para ser desplegado en cualquier infraestructura moderna, desde entornos de desarrollo local hasta clusters de Kubernetes en la nube, proporcionando flexibilidad y adaptabilidad a diferentes necesidades organizacionales.