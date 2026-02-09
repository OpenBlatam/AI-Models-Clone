# AI Continuous Document Generator - Optimización de Rendimiento

## 1. Estrategias de Optimización General

### 1.1 Principios de Optimización
- **Medición Primero**: Identificar cuellos de botella reales
- **Optimización por Capas**: Frontend, Backend, Base de Datos, Red
- **Caching Inteligente**: Múltiples niveles de cache
- **Lazy Loading**: Carga diferida de recursos
- **Compresión**: Minimizar transferencia de datos
- **CDN**: Distribución global de contenido

### 1.2 Métricas Clave de Rendimiento
- **Core Web Vitals**: LCP, FID, CLS
- **Tiempo de Respuesta**: < 200ms para APIs
- **Throughput**: Requests por segundo
- **Uso de Memoria**: < 80% de capacidad
- **CPU**: < 70% de utilización
- **Latencia de Red**: < 100ms

## 2. Optimización del Frontend

### 2.1 Code Splitting y Lazy Loading
```typescript
// Lazy loading de componentes
const DocumentEditor = lazy(() => import('./components/DocumentEditor'));
const AIPanel = lazy(() => import('./components/AIPanel'));
const Templates = lazy(() => import('./components/Templates'));

// Lazy loading de rutas
const routes = [
  {
    path: '/documents/:id',
    component: lazy(() => import('./pages/DocumentPage'))
  },
  {
    path: '/templates',
    component: lazy(() => import('./pages/TemplatesPage'))
  }
];

// Lazy loading de librerías
const loadMonacoEditor = () => import('monaco-editor');
const loadChartJS = () => import('chart.js');
```

### 2.2 Optimización de Bundle
```javascript
// webpack.config.js
const path = require('path');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true
        }
      }
    },
    usedExports: true,
    sideEffects: false
  },
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false
    })
  ]
};
```

### 2.3 Memoización y Optimización de Re-renders
```typescript
// Memoización de componentes
const DocumentList = memo(({ documents, onSelect }) => {
  return (
    <div className="document-list">
      {documents.map(doc => (
        <DocumentItem
          key={doc.id}
          document={doc}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
});

// Memoización de callbacks
const DocumentEditor = ({ documentId }) => {
  const [content, setContent] = useState('');
  
  const handleContentChange = useCallback((newContent) => {
    setContent(newContent);
    // Debounce para evitar demasiadas actualizaciones
    debounce(updateDocument, 500)(documentId, newContent);
  }, [documentId]);

  const debouncedSave = useMemo(
    () => debounce(saveDocument, 1000),
    []
  );

  return (
    <RichTextEditor
      value={content}
      onChange={handleContentChange}
    />
  );
};

// Memoización de valores computados
const DocumentStats = ({ documents }) => {
  const stats = useMemo(() => {
    return {
      total: documents.length,
      published: documents.filter(d => d.status === 'published').length,
      drafts: documents.filter(d => d.status === 'draft').length,
      totalWords: documents.reduce((sum, doc) => sum + doc.wordCount, 0)
    };
  }, [documents]);

  return <StatsDisplay stats={stats} />;
};
```

### 2.4 Virtualización para Listas Grandes
```typescript
import { FixedSizeList as List } from 'react-window';

const VirtualizedDocumentList = ({ documents }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <DocumentItem document={documents[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={documents.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </List>
  );
};

// Virtualización horizontal para tabs
const VirtualizedTabs = ({ tabs }) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 });
  
  const visibleTabs = useMemo(() => {
    return tabs.slice(visibleRange.start, visibleRange.end);
  }, [tabs, visibleRange]);

  return (
    <div className="tabs-container">
      {visibleTabs.map(tab => (
        <Tab key={tab.id} tab={tab} />
      ))}
    </div>
  );
};
```

### 2.5 Optimización de Imágenes
```typescript
// Componente de imagen optimizada
const OptimizedImage = ({ src, alt, width, height, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className="image-container" style={{ width, height }}>
      {!isLoaded && !error && (
        <div className="image-placeholder">
          <Skeleton width={width} height={height} />
        </div>
      )}
      
      <img
        src={src}
        alt={alt}
        onLoad={() => setIsLoaded(true)}
        onError={() => setError(true)}
        style={{
          display: isLoaded ? 'block' : 'none',
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
        loading="lazy"
        {...props}
      />
    </div>
  );
};

// WebP con fallback
const WebPImage = ({ src, alt, ...props }) => {
  const [supportsWebP, setSupportsWebP] = useState(false);

  useEffect(() => {
    const webP = new Image();
    webP.onload = webP.onerror = () => {
      setSupportsWebP(webP.height === 2);
    };
    webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
  }, []);

  const imageSrc = supportsWebP ? src.replace(/\.(jpg|jpeg|png)$/, '.webp') : src;

  return <img src={imageSrc} alt={alt} {...props} />;
};
```

## 3. Optimización del Backend

### 3.1 Caching Estratégico
```javascript
// Redis caching con TTL
class CacheService {
  constructor(redis) {
    this.redis = redis;
    this.defaultTTL = 3600; // 1 hora
  }

  async get(key) {
    try {
      const cached = await this.redis.get(key);
      return cached ? JSON.parse(cached) : null;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }

  async set(key, value, ttl = this.defaultTTL) {
    try {
      await this.redis.setex(key, ttl, JSON.stringify(value));
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }

  async del(key) {
    try {
      await this.redis.del(key);
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }

  // Cache con invalidación inteligente
  async getOrSet(key, fetchFn, ttl = this.defaultTTL) {
    let cached = await this.get(key);
    
    if (cached) {
      return cached;
    }

    const fresh = await fetchFn();
    await this.set(key, fresh, ttl);
    return fresh;
  }
}

// Uso en controladores
const DocumentController = {
  async getDocument(req, res) {
    const { id } = req.params;
    const cacheKey = `document:${id}`;
    
    const document = await cacheService.getOrSet(
      cacheKey,
      () => Document.findById(id).populate('collaborators'),
      1800 // 30 minutos
    );
    
    res.json(document);
  },

  async updateDocument(req, res) {
    const { id } = req.params;
    const updates = req.body;
    
    const document = await Document.findByIdAndUpdate(id, updates, { new: true });
    
    // Invalidar cache
    await cacheService.del(`document:${id}`);
    await cacheService.del(`user:${req.user.id}:documents`);
    
    res.json(document);
  }
};
```

### 3.2 Optimización de Base de Datos
```javascript
// Índices optimizados
const DocumentSchema = new mongoose.Schema({
  title: { type: String, required: true, index: true },
  content: { type: String, required: true },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', index: true },
  status: { type: String, enum: ['draft', 'published', 'archived'], index: true },
  tags: [{ type: String, index: true }],
  createdAt: { type: Date, default: Date.now, index: true },
  updatedAt: { type: Date, default: Date.now, index: true }
});

// Índices compuestos
DocumentSchema.index({ userId: 1, status: 1, updatedAt: -1 });
DocumentSchema.index({ tags: 1, status: 1 });
DocumentSchema.index({ title: 'text', content: 'text' });

// Queries optimizadas
class DocumentService {
  // Paginación eficiente
  async getDocuments(userId, options = {}) {
    const {
      page = 1,
      limit = 20,
      status,
      tags,
      search,
      sortBy = 'updatedAt',
      sortOrder = 'desc'
    } = options;

    const query = { userId };
    
    if (status) query.status = status;
    if (tags && tags.length > 0) query.tags = { $in: tags };
    if (search) {
      query.$text = { $search: search };
    }

    const sort = { [sortBy]: sortOrder === 'desc' ? -1 : 1 };
    
    const [documents, total] = await Promise.all([
      Document.find(query)
        .select('title status tags createdAt updatedAt')
        .sort(sort)
        .skip((page - 1) * limit)
        .limit(limit)
        .lean(), // Usar lean() para mejor rendimiento
      Document.countDocuments(query)
    ]);

    return {
      documents,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    };
  }

  // Aggregation pipeline optimizada
  async getDocumentStats(userId) {
    const stats = await Document.aggregate([
      { $match: { userId: new mongoose.Types.ObjectId(userId) } },
      {
        $group: {
          _id: '$status',
          count: { $sum: 1 },
          totalWords: { $sum: { $strLenCP: '$content' } }
        }
      }
    ]);

    return stats.reduce((acc, stat) => {
      acc[stat._id] = {
        count: stat.count,
        totalWords: stat.totalWords
      };
      return acc;
    }, {});
  }
}
```

### 3.3 Connection Pooling
```javascript
// Configuración de pool de conexiones
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.DATABASE_URL, {
      maxPoolSize: 10, // Mantener hasta 10 conexiones
      serverSelectionTimeoutMS: 5000, // Mantener intentando por 5 segundos
      socketTimeoutMS: 45000, // Cerrar sockets después de 45 segundos
      bufferMaxEntries: 0, // Deshabilitar buffering
      bufferCommands: false, // Deshabilitar buffering de comandos
    });

    // Event listeners para monitoreo
    mongoose.connection.on('connected', () => {
      console.log('MongoDB connected');
    });

    mongoose.connection.on('error', (err) => {
      console.error('MongoDB connection error:', err);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('MongoDB disconnected');
    });

  } catch (error) {
    console.error('Database connection failed:', error);
    process.exit(1);
  }
};

// Pool de conexiones para Redis
const Redis = require('ioredis');

const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: process.env.REDIS_PORT,
  password: process.env.REDIS_PASSWORD,
  retryDelayOnFailover: 100,
  maxRetriesPerRequest: 3,
  lazyConnect: true,
  keepAlive: 30000,
  family: 4,
  db: 0,
  maxLoadingTimeout: 5000,
  enableReadyCheck: true,
  maxMemoryPolicy: 'allkeys-lru'
});
```

### 3.4 Compresión y Optimización de Respuestas
```javascript
// Middleware de compresión
const compression = require('compression');
const express = require('express');

const app = express();

app.use(compression({
  level: 6, // Nivel de compresión (1-9)
  threshold: 1024, // Comprimir solo archivos > 1KB
  filter: (req, res) => {
    if (req.headers['x-no-compression']) {
      return false;
    }
    return compression.filter(req, res);
  }
}));

// Optimización de respuestas JSON
app.use((req, res, next) => {
  const originalJson = res.json;
  
  res.json = function(data) {
    // Remover campos undefined
    const cleanData = JSON.parse(JSON.stringify(data));
    
    // Comprimir respuestas grandes
    if (JSON.stringify(cleanData).length > 10000) {
      res.setHeader('Content-Encoding', 'gzip');
    }
    
    return originalJson.call(this, cleanData);
  };
  
  next();
});

// Streaming para respuestas grandes
app.get('/api/documents/export', async (req, res) => {
  const { format, documentIds } = req.query;
  
  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Content-Disposition', `attachment; filename="documents.${format}"`);
  
  const stream = await generateExportStream(documentIds, format);
  stream.pipe(res);
});
```

## 4. Optimización de APIs de IA

### 4.1 Batching y Rate Limiting
```javascript
// Queue para requests de IA
const Queue = require('bull');
const aiQueue = new Queue('AI processing', process.env.REDIS_URL);

// Procesamiento en lotes
aiQueue.process('generate-content', 5, async (job) => {
  const { prompts, documentId } = job.data;
  
  // Procesar múltiples prompts en paralelo
  const results = await Promise.allSettled(
    prompts.map(prompt => generateAIContent(prompt))
  );
  
  return results.map((result, index) => ({
    prompt: prompts[index],
    content: result.status === 'fulfilled' ? result.value : null,
    error: result.status === 'rejected' ? result.reason : null
  }));
});

// Rate limiting inteligente
class AIRateLimiter {
  constructor() {
    this.requests = new Map();
    this.limits = {
      openai: { requests: 50, window: 60000 }, // 50 requests por minuto
      anthropic: { requests: 30, window: 60000 } // 30 requests por minuto
    };
  }

  async canMakeRequest(provider) {
    const now = Date.now();
    const limit = this.limits[provider];
    
    if (!this.requests.has(provider)) {
      this.requests.set(provider, []);
    }
    
    const requests = this.requests.get(provider);
    
    // Limpiar requests antiguos
    const validRequests = requests.filter(time => now - time < limit.window);
    this.requests.set(provider, validRequests);
    
    return validRequests.length < limit.requests;
  }

  async makeRequest(provider, requestFn) {
    if (!(await this.canMakeRequest(provider))) {
      throw new Error(`Rate limit exceeded for ${provider}`);
    }
    
    const now = Date.now();
    this.requests.get(provider).push(now);
    
    return requestFn();
  }
}
```

### 4.2 Caching de Respuestas de IA
```javascript
// Cache inteligente para respuestas de IA
class AICacheService {
  constructor(redis) {
    this.redis = redis;
    this.ttl = 86400; // 24 horas
  }

  generateCacheKey(prompt, model, options) {
    const hash = crypto
      .createHash('sha256')
      .update(JSON.stringify({ prompt, model, options }))
      .digest('hex');
    
    return `ai:${hash}`;
  }

  async getCachedResponse(prompt, model, options) {
    const key = this.generateCacheKey(prompt, model, options);
    return await this.redis.get(key);
  }

  async cacheResponse(prompt, model, options, response) {
    const key = this.generateCacheKey(prompt, model, options);
    await this.redis.setex(key, this.ttl, JSON.stringify(response));
  }

  async generateWithCache(prompt, model, options) {
    // Intentar obtener del cache
    const cached = await this.getCachedResponse(prompt, model, options);
    if (cached) {
      return JSON.parse(cached);
    }

    // Generar nueva respuesta
    const response = await this.generateAIResponse(prompt, model, options);
    
    // Cachear respuesta
    await this.cacheResponse(prompt, model, options, response);
    
    return response;
  }
}
```

### 4.3 Optimización de Prompts
```javascript
// Optimización de prompts para mejor rendimiento
class PromptOptimizer {
  constructor() {
    this.templates = new Map();
    this.loadTemplates();
  }

  loadTemplates() {
    this.templates.set('summary', {
      system: 'Eres un experto en resumir documentos. Genera resúmenes concisos y precisos.',
      user: 'Resume el siguiente texto en máximo 3 párrafos:\n\n{content}',
      maxTokens: 500
    });

    this.templates.set('improve', {
      system: 'Eres un editor profesional. Mejora la claridad y fluidez del texto.',
      user: 'Mejora el siguiente texto manteniendo el significado original:\n\n{content}',
      maxTokens: 1000
    });
  }

  optimizePrompt(type, content, options = {}) {
    const template = this.templates.get(type);
    if (!template) {
      throw new Error(`Template ${type} not found`);
    }

    const optimizedPrompt = template.user.replace('{content}', content);
    
    return {
      system: template.system,
      user: optimizedPrompt,
      maxTokens: options.maxTokens || template.maxTokens,
      temperature: options.temperature || 0.7
    };
  }

  // Compresión de contexto para prompts largos
  compressContext(content, maxLength = 4000) {
    if (content.length <= maxLength) {
      return content;
    }

    // Dividir en párrafos y mantener los más importantes
    const paragraphs = content.split('\n\n');
    const compressed = [];
    let currentLength = 0;

    for (const paragraph of paragraphs) {
      if (currentLength + paragraph.length <= maxLength) {
        compressed.push(paragraph);
        currentLength += paragraph.length;
      } else {
        break;
      }
    }

    return compressed.join('\n\n');
  }
}
```

## 5. Optimización de Red

### 5.1 HTTP/2 y Server Push
```javascript
// Configuración HTTP/2
const http2 = require('http2');
const fs = require('fs');

const server = http2.createSecureServer({
  key: fs.readFileSync('private-key.pem'),
  cert: fs.readFileSync('certificate.pem')
});

server.on('stream', (stream, headers) => {
  const path = headers[':path'];
  
  if (path === '/') {
    // Server push para recursos críticos
    stream.pushStream({ ':path': '/static/css/main.css' }, (err, pushStream) => {
      if (!err) {
        pushStream.respond({ ':status': 200, 'content-type': 'text/css' });
        pushStream.end(fs.readFileSync('static/css/main.css'));
      }
    });
    
    stream.pushStream({ ':path': '/static/js/main.js' }, (err, pushStream) => {
      if (!err) {
        pushStream.respond({ ':status': 200, 'content-type': 'application/javascript' });
        pushStream.end(fs.readFileSync('static/js/main.js'));
      }
    });
    
    stream.respond({ ':status': 200, 'content-type': 'text/html' });
    stream.end(fs.readFileSync('index.html'));
  }
});
```

### 5.2 CDN y Edge Caching
```javascript
// Configuración de CDN
const cdnConfig = {
  static: {
    domain: 'cdn.yourdomain.com',
    cacheControl: 'public, max-age=31536000', // 1 año
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS'
    }
  },
  api: {
    domain: 'api-cdn.yourdomain.com',
    cacheControl: 'public, max-age=300', // 5 minutos
    headers: {
      'Vary': 'Accept-Encoding, Authorization'
    }
  }
};

// Middleware para headers de CDN
app.use((req, res, next) => {
  if (req.path.startsWith('/static/')) {
    res.setHeader('Cache-Control', cdnConfig.static.cacheControl);
    Object.entries(cdnConfig.static.headers).forEach(([key, value]) => {
      res.setHeader(key, value);
    });
  } else if (req.path.startsWith('/api/')) {
    res.setHeader('Cache-Control', cdnConfig.api.cacheControl);
    Object.entries(cdnConfig.api.headers).forEach(([key, value]) => {
      res.setHeader(key, value);
    });
  }
  
  next();
});
```

### 5.3 Preloading y Prefetching
```typescript
// Preloading de recursos críticos
const ResourcePreloader = {
  preloadCriticalResources() {
    const criticalResources = [
      '/static/css/critical.css',
      '/static/js/critical.js',
      '/api/user/profile'
    ];

    criticalResources.forEach(resource => {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = resource;
      
      if (resource.endsWith('.css')) {
        link.as = 'style';
      } else if (resource.endsWith('.js')) {
        link.as = 'script';
      } else if (resource.startsWith('/api/')) {
        link.as = 'fetch';
        link.crossOrigin = 'anonymous';
      }
      
      document.head.appendChild(link);
    });
  },

  prefetchOnHover(element, resource) {
    let prefetched = false;
    
    element.addEventListener('mouseenter', () => {
      if (!prefetched) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = resource;
        document.head.appendChild(link);
        prefetched = true;
      }
    });
  }
};

// Prefetching inteligente basado en comportamiento del usuario
const IntelligentPrefetcher = {
  init() {
    this.trackUserBehavior();
    this.setupIntersectionObserver();
  },

  trackUserBehavior() {
    let mouseX = 0;
    let mouseY = 0;
    
    document.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    // Prefetch cuando el mouse se acerca a enlaces
    document.addEventListener('mouseover', (e) => {
      const link = e.target.closest('a[href]');
      if (link && this.isLikelyToClick(mouseX, mouseY, link)) {
        this.prefetch(link.href);
      }
    });
  },

  isLikelyToClick(x, y, element) {
    const rect = element.getBoundingClientRect();
    const distance = Math.sqrt(
      Math.pow(x - (rect.left + rect.width / 2), 2) +
      Math.pow(y - (rect.top + rect.height / 2), 2)
    );
    
    return distance < 100; // 100px de distancia
  },

  prefetch(url) {
    if (!this.prefetched.has(url)) {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = url;
      document.head.appendChild(link);
      this.prefetched.add(url);
    }
  }
};
```

## 6. Monitoreo y Métricas

### 6.1 Performance Monitoring
```javascript
// Performance monitoring con Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.init();
  }

  init() {
    getCLS(this.handleMetric.bind(this));
    getFID(this.handleMetric.bind(this));
    getFCP(this.handleMetric.bind(this));
    getLCP(this.handleMetric.bind(this));
    getTTFB(this.handleMetric.bind(this));
  }

  handleMetric(metric) {
    this.metrics.set(metric.name, metric);
    this.sendMetric(metric);
  }

  sendMetric(metric) {
    // Enviar a servicio de analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', metric.name, {
        value: Math.round(metric.value),
        event_category: 'Web Vitals',
        event_label: metric.id,
        non_interaction: true
      });
    }

    // Enviar a API personalizada
    fetch('/api/metrics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: metric.name,
        value: metric.value,
        id: metric.id,
        timestamp: Date.now()
      })
    });
  }
}

// Monitoreo de APIs
const apiMonitor = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    // Log métricas de API
    console.log(`${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
    
    // Enviar a sistema de métricas
    metricsCollector.recordAPICall({
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration,
      timestamp: Date.now()
    });
  });
  
  next();
};
```

### 6.2 Real User Monitoring (RUM)
```typescript
// RUM para monitoreo de usuarios reales
class RealUserMonitoring {
  private sessionId: string;
  private startTime: number;
  private errors: Error[] = [];

  constructor() {
    this.sessionId = this.generateSessionId();
    this.startTime = Date.now();
    this.init();
  }

  init() {
    this.trackPageLoad();
    this.trackUserInteractions();
    this.trackErrors();
    this.trackResourceTiming();
  }

  trackPageLoad() {
    window.addEventListener('load', () => {
      const loadTime = Date.now() - this.startTime;
      
      this.sendMetric({
        type: 'page_load',
        loadTime,
        url: window.location.href,
        userAgent: navigator.userAgent,
        connection: (navigator as any).connection?.effectiveType
      });
    });
  }

  trackUserInteractions() {
    let interactionCount = 0;
    
    ['click', 'scroll', 'keydown'].forEach(eventType => {
      document.addEventListener(eventType, () => {
        interactionCount++;
        
        if (interactionCount % 10 === 0) {
          this.sendMetric({
            type: 'user_interaction',
            eventType,
            count: interactionCount,
            timestamp: Date.now()
          });
        }
      });
    });
  }

  trackErrors() {
    window.addEventListener('error', (event) => {
      this.errors.push({
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        timestamp: Date.now()
      });

      this.sendMetric({
        type: 'error',
        error: {
          message: event.message,
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno
        }
      });
    });
  }

  trackResourceTiming() {
    if ('performance' in window && 'getEntriesByType' in performance) {
      const resources = performance.getEntriesByType('resource');
      
      resources.forEach(resource => {
        this.sendMetric({
          type: 'resource_timing',
          name: resource.name,
          duration: resource.duration,
          size: resource.transferSize,
          type: resource.initiatorType
        });
      });
    }
  }

  private sendMetric(metric: any) {
    fetch('/api/rum', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: this.sessionId,
        ...metric
      })
    });
  }

  private generateSessionId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
}
```

## 7. Optimización de Base de Datos

### 7.1 Query Optimization
```javascript
// Optimización de queries con explain
class QueryOptimizer {
  async analyzeQuery(query, options = {}) {
    const explain = await query.explain('executionStats');
    
    const analysis = {
      executionTime: explain.executionStats.executionTimeMillis,
      totalDocsExamined: explain.executionStats.totalDocsExamined,
      totalDocsReturned: explain.executionStats.totalDocsReturned,
      indexUsed: explain.executionStats.totalDocsExamined === explain.executionStats.totalDocsReturned,
      efficiency: explain.executionStats.totalDocsReturned / explain.executionStats.totalDocsExamined
    };

    if (analysis.efficiency < 0.1) {
      console.warn('Inefficient query detected:', analysis);
    }

    return analysis;
  }

  // Query builder optimizado
  buildOptimizedQuery(filters) {
    const query = {};
    const sort = {};
    const projection = {};

    // Aplicar filtros en orden de selectividad
    if (filters.userId) {
      query.userId = filters.userId; // Muy selectivo
    }
    
    if (filters.status) {
      query.status = filters.status; // Moderadamente selectivo
    }
    
    if (filters.tags && filters.tags.length > 0) {
      query.tags = { $in: filters.tags }; // Menos selectivo
    }
    
    if (filters.dateRange) {
      query.createdAt = {
        $gte: filters.dateRange.start,
        $lte: filters.dateRange.end
      };
    }

    // Ordenamiento optimizado
    if (filters.sortBy) {
      sort[filters.sortBy] = filters.sortOrder === 'desc' ? -1 : 1;
    } else {
      sort.updatedAt = -1; // Orden por defecto
    }

    // Proyección para reducir transferencia de datos
    if (filters.fields) {
      filters.fields.forEach(field => {
        projection[field] = 1;
      });
    }

    return { query, sort, projection };
  }
}
```

### 7.2 Database Connection Optimization
```javascript
// Pool de conexiones optimizado
const mongoose = require('mongoose');

const connectionOptions = {
  maxPoolSize: 10, // Máximo 10 conexiones
  minPoolSize: 2,  // Mínimo 2 conexiones
  maxIdleTimeMS: 30000, // Cerrar conexiones inactivas después de 30s
  serverSelectionTimeoutMS: 5000, // Timeout de selección de servidor
  socketTimeoutMS: 45000, // Timeout de socket
  bufferMaxEntries: 0, // Deshabilitar buffering
  bufferCommands: false, // Deshabilitar buffering de comandos
  retryWrites: true, // Reintentar escrituras
  retryReads: true,  // Reintentar lecturas
  readPreference: 'secondaryPreferred', // Preferir lecturas secundarias
  readConcern: { level: 'majority' }, // Leer solo datos confirmados
  writeConcern: { w: 'majority', j: true } // Escribir con confirmación
};

// Configuración de replica set para alta disponibilidad
const replicaSetOptions = {
  replicaSet: 'rs0',
  readPreference: 'secondaryPreferred',
  readConcern: { level: 'majority' },
  writeConcern: { w: 'majority', j: true }
};

// Monitoreo de conexiones
mongoose.connection.on('connected', () => {
  console.log('MongoDB connected');
  console.log(`Pool size: ${mongoose.connection.readyState}`);
});

mongoose.connection.on('error', (err) => {
  console.error('MongoDB connection error:', err);
});

mongoose.connection.on('disconnected', () => {
  console.log('MongoDB disconnected');
});

// Health check de base de datos
const dbHealthCheck = async () => {
  try {
    const start = Date.now();
    await mongoose.connection.db.admin().ping();
    const duration = Date.now() - start;
    
    return {
      status: 'healthy',
      responseTime: duration,
      poolSize: mongoose.connection.readyState
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error.message
    };
  }
};
```

Esta guía de optimización de rendimiento proporciona estrategias completas para mejorar el rendimiento del sistema de generación de documentos con IA en todas las capas de la aplicación.







