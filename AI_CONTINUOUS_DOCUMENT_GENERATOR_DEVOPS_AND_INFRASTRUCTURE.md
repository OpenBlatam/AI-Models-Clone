# AI Continuous Document Generator - DevOps e Infraestructura

## 1. Arquitectura de Infraestructura

### 1.1 Arquitectura Cloud-Native
```yaml
# kubernetes/infrastructure.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: document-generator
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: document-generator
data:
  NODE_ENV: "production"
  API_VERSION: "v1"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: document-generator
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  REDIS_URL: <base64-encoded>
  JWT_SECRET: <base64-encoded>
  OPENAI_API_KEY: <base64-encoded>
```

### 1.2 Microservicios Architecture
```typescript
// infrastructure/microservices.ts
interface MicroserviceConfig {
  name: string;
  port: number;
  replicas: number;
  resources: ResourceRequirements;
  healthCheck: HealthCheck;
  dependencies: string[];
}

const microservices: MicroserviceConfig[] = [
  {
    name: 'api-gateway',
    port: 3000,
    replicas: 3,
    resources: {
      requests: { cpu: '500m', memory: '1Gi' },
      limits: { cpu: '1000m', memory: '2Gi' }
    },
    healthCheck: {
      path: '/health',
      port: 3000,
      interval: 30
    },
    dependencies: []
  },
  {
    name: 'document-service',
    port: 3001,
    replicas: 5,
    resources: {
      requests: { cpu: '1000m', memory: '2Gi' },
      limits: { cpu: '2000m', memory: '4Gi' }
    },
    healthCheck: {
      path: '/health',
      port: 3001,
      interval: 30
    },
    dependencies: ['postgresql', 'redis']
  },
  {
    name: 'ai-service',
    port: 3002,
    replicas: 3,
    resources: {
      requests: { cpu: '2000m', memory: '4Gi' },
      limits: { cpu: '4000m', memory: '8Gi' }
    },
    healthCheck: {
      path: '/health',
      port: 3002,
      interval: 30
    },
    dependencies: ['redis', 'openai-api']
  },
  {
    name: 'collaboration-service',
    port: 3003,
    replicas: 3,
    resources: {
      requests: { cpu: '500m', memory: '1Gi' },
      limits: { cpu: '1000m', memory: '2Gi' }
    },
    healthCheck: {
      path: '/health',
      port: 3003,
      interval: 30
    },
    dependencies: ['redis', 'websocket']
  }
];
```

## 2. CI/CD Pipeline

### 2.1 GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linting
      run: npm run lint
    
    - name: Run type checking
      run: npm run type-check
    
    - name: Run unit tests
      run: npm run test:unit
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
    
    - name: Run integration tests
      run: npm run test:integration
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
    
    - name: Run E2E tests
      run: npm run test:e2e
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
    
    - name: Generate coverage report
      run: npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security audit
      run: npm audit --audit-level moderate
    
    - name: Run Snyk security scan
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/api-gateway api-gateway=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        kubectl set image deployment/document-service document-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        kubectl set image deployment/ai-service ai-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
        kubectl set image deployment/collaboration-service collaboration-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    
    - name: Wait for deployment
      run: |
        kubectl rollout status deployment/api-gateway
        kubectl rollout status deployment/document-service
        kubectl rollout status deployment/ai-service
        kubectl rollout status deployment/collaboration-service
    
    - name: Run smoke tests
      run: |
        kubectl run smoke-test --image=curlimages/curl --rm -i --restart=Never -- \
          curl -f http://api-gateway:3000/health
```

### 2.2 Docker Configuration
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

## 3. Monitoreo y Observabilidad

### 3.1 Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'document-service'
    static_configs:
      - targets: ['document-service:3001']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'ai-service'
    static_configs:
      - targets: ['ai-service:3002']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'collaboration-service'
    static_configs:
      - targets: ['collaboration-service:3003']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

### 3.2 Grafana Dashboards
```json
{
  "dashboard": {
    "id": null,
    "title": "Document Generator - System Overview",
    "tags": ["document-generator", "system"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{service}} - {{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec",
            "min": 0
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
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
            "label": "Response Time (s)",
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
            "legendFormat": "5xx Errors"
          },
          {
            "expr": "rate(http_requests_total{status=~\"4..\"}[5m])",
            "legendFormat": "4xx Errors"
          }
        ],
        "yAxes": [
          {
            "label": "Errors/sec",
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
            "legendFormat": "{{pod}}"
          }
        ],
        "yAxes": [
          {
            "label": "CPU %",
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
            "legendFormat": "{{pod}}"
          }
        ],
        "yAxes": [
          {
            "label": "Memory %",
            "min": 0,
            "max": 100
          }
        ]
      }
    ]
  }
}
```

### 3.3 Application Metrics
```typescript
// src/middleware/metrics.ts
import { register, Counter, Histogram, Gauge } from 'prom-client';

// Custom metrics
const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'endpoint', 'status', 'service']
});

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'endpoint', 'service'],
  buckets: [0.1, 0.3, 0.5, 0.7, 1, 3, 5, 7, 10]
});

const activeConnections = new Gauge({
  name: 'websocket_connections_active',
  help: 'Number of active WebSocket connections',
  labelNames: ['service']
});

const documentGenerationTime = new Histogram({
  name: 'document_generation_duration_seconds',
  help: 'Time taken to generate documents',
  labelNames: ['template', 'ai_provider'],
  buckets: [1, 2, 5, 10, 30, 60, 120]
});

const aiRequestsTotal = new Counter({
  name: 'ai_requests_total',
  help: 'Total number of AI requests',
  labelNames: ['provider', 'model', 'status']
});

// Middleware to collect metrics
export const metricsMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    
    httpRequestsTotal
      .labels(req.method, req.route?.path || req.path, res.statusCode.toString(), 'api-gateway')
      .inc();
    
    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, 'api-gateway')
      .observe(duration);
  });
  
  next();
};

// Metrics endpoint
export const metricsEndpoint = (req: Request, res: Response) => {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
};
```

## 4. Logging y Tracing

### 4.1 Structured Logging
```typescript
// src/utils/logger.ts
import winston from 'winston';
import { v4 as uuidv4 } from 'uuid';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'document-generator',
    version: process.env.SERVICE_VERSION || '1.0.0'
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error'
    }),
    new winston.transports.File({
      filename: 'logs/combined.log'
    })
  ]
});

export class Logger {
  private requestId: string;
  private userId?: string;
  private sessionId?: string;

  constructor(requestId?: string, userId?: string, sessionId?: string) {
    this.requestId = requestId || uuidv4();
    this.userId = userId;
    this.sessionId = sessionId;
  }

  info(message: string, meta?: any) {
    logger.info(message, {
      requestId: this.requestId,
      userId: this.userId,
      sessionId: this.sessionId,
      ...meta
    });
  }

  error(message: string, error?: Error, meta?: any) {
    logger.error(message, {
      requestId: this.requestId,
      userId: this.userId,
      sessionId: this.sessionId,
      error: error?.stack,
      ...meta
    });
  }

  warn(message: string, meta?: any) {
    logger.warn(message, {
      requestId: this.requestId,
      userId: this.userId,
      sessionId: this.sessionId,
      ...meta
    });
  }

  debug(message: string, meta?: any) {
    logger.debug(message, {
      requestId: this.requestId,
      userId: this.userId,
      sessionId: this.sessionId,
      ...meta
    });
  }
}
```

### 4.2 Distributed Tracing
```typescript
// src/utils/tracing.ts
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import { NodeTracerProvider } from '@opentelemetry/sdk-node';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const tracerProvider = new NodeTracerProvider({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'document-generator',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0'
  })
});

const jaegerExporter = new JaegerExporter({
  endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces'
});

tracerProvider.addSpanProcessor(new BatchSpanProcessor(jaegerExporter));
tracerProvider.register();

const tracer = trace.getTracer('document-generator');

export class TracingService {
  static async traceFunction<T>(
    name: string,
    fn: () => Promise<T>,
    attributes?: Record<string, any>
  ): Promise<T> {
    const span = tracer.startSpan(name, {
      attributes: {
        'function.name': name,
        ...attributes
      }
    });

    try {
      const result = await context.with(trace.setSpan(context.active(), span), fn);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  }

  static createSpan(name: string, attributes?: Record<string, any>) {
    return tracer.startSpan(name, {
      attributes: {
        'span.name': name,
        ...attributes
      }
    });
  }
}
```

## 5. Auto-scaling y Load Balancing

### 5.1 Horizontal Pod Autoscaler
```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: document-generator
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-service-hpa
  namespace: document-generator
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 85
  - type: Pods
    pods:
      metric:
        name: ai_requests_per_second
      target:
        type: AverageValue
        averageValue: "50"
```

### 5.2 Load Balancer Configuration
```yaml
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: document-generator-ingress
  namespace: document-generator
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/rate-limit-connections: "10"
    nginx.ingress.kubernetes.io/rate-limit-requests: "100"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.documentgenerator.com
    - app.documentgenerator.com
    secretName: document-generator-tls
  rules:
  - host: api.documentgenerator.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 3000
  - host: app.documentgenerator.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

## 6. Backup y Disaster Recovery

### 6.1 Database Backup Strategy
```bash
#!/bin/bash
# scripts/backup-database.sh

# Configuration
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-document_generator}
DB_USER=${DB_USER:-postgres}
BACKUP_DIR=${BACKUP_DIR:-/backups}
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

# Create database backup
echo "Creating database backup..."
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
echo "Compressing backup..."
gzip $BACKUP_FILE

# Upload to S3
echo "Uploading to S3..."
aws s3 cp "$BACKUP_FILE.gz" s3://document-generator-backups/database/

# Clean up old local backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully!"
```

### 6.2 Disaster Recovery Plan
```yaml
# kubernetes/disaster-recovery.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: disaster-recovery-config
  namespace: document-generator
data:
  recovery-plan.yaml: |
    phases:
      - name: "Assessment"
        duration: "5 minutes"
        tasks:
          - "Assess system health"
          - "Identify affected services"
          - "Estimate recovery time"
      
      - name: "Immediate Response"
        duration: "15 minutes"
        tasks:
          - "Activate backup systems"
          - "Redirect traffic to backup region"
          - "Notify stakeholders"
      
      - name: "Data Recovery"
        duration: "30 minutes"
        tasks:
          - "Restore database from backup"
          - "Restore file storage"
          - "Verify data integrity"
      
      - name: "Service Recovery"
        duration: "20 minutes"
        tasks:
          - "Deploy services to backup region"
          - "Update DNS records"
          - "Verify service health"
      
      - name: "Validation"
        duration: "10 minutes"
        tasks:
          - "Run smoke tests"
          - "Verify user access"
          - "Monitor system metrics"
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: disaster-recovery-test
  namespace: document-generator
spec:
  schedule: "0 2 * * 0"  # Every Sunday at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: dr-test
            image: document-generator/dr-test:latest
            env:
            - name: BACKUP_REGION
              value: "us-west-2"
            - name: PRIMARY_REGION
              value: "us-east-1"
          restartPolicy: OnFailure
```

## 7. Security y Compliance

### 7.1 Network Policies
```yaml
# kubernetes/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: document-generator-network-policy
  namespace: document-generator
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: document-generator
    - podSelector:
        matchLabels:
          app: api-gateway
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: document-generator
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to: []
    ports:
    - protocol: TCP
      port: 443
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-network-policy
  namespace: document-generator
spec:
  podSelector:
    matchLabels:
      app: postgresql
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: document-service
    - podSelector:
        matchLabels:
          app: ai-service
    ports:
    - protocol: TCP
      port: 5432
```

### 7.2 Pod Security Policies
```yaml
# kubernetes/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: document-generator-psp
  namespace: document-generator
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

Esta infraestructura DevOps proporciona una base sólida, escalable y segura para el AI Continuous Document Generator, con capacidades avanzadas de monitoreo, auto-scaling, backup y disaster recovery.




