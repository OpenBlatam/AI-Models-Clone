# AI Continuous Document Generator - Especificaciones de Seguridad

## 1. Arquitectura de Seguridad

### 1.1 Modelo de Seguridad por Capas
```
┌─────────────────────────────────────┐
│        Application Security         │
├─────────────────────────────────────┤
│        Network Security             │
├─────────────────────────────────────┤
│        Infrastructure Security      │
├─────────────────────────────────────┤
│        Data Security                │
└─────────────────────────────────────┘
```

### 1.2 Principios de Seguridad
- **Defensa en Profundidad**: Múltiples capas de seguridad
- **Principio de Menor Privilegio**: Acceso mínimo necesario
- **Seguridad por Diseño**: Seguridad integrada desde el inicio
- **Monitoreo Continuo**: Detección y respuesta en tiempo real
- **Cumplimiento Normativo**: GDPR, CCPA, SOC 2, ISO 27001

## 2. Autenticación y Autorización

### 2.1 Autenticación Multi-Factor
```javascript
// services/auth-service/src/middleware/mfa.js
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');

class MFAService {
  generateSecret(userId) {
    const secret = speakeasy.generateSecret({
      name: `Document Generator (${userId})`,
      issuer: 'Document Generator'
    });
    
    return {
      secret: secret.base32,
      qrCodeUrl: secret.otpauth_url
    };
  }

  verifyToken(secret, token) {
    return speakeasy.totp.verify({
      secret: secret,
      encoding: 'base32',
      token: token,
      window: 2 // Permite 2 períodos de tiempo de tolerancia
    });
  }

  generateQRCode(otpauthUrl) {
    return QRCode.toDataURL(otpauthUrl);
  }
}
```

### 2.2 JWT con Refresh Tokens
```javascript
// services/auth-service/src/utils/jwt.js
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

class JWTService {
  constructor() {
    this.accessTokenSecret = process.env.JWT_ACCESS_SECRET;
    this.refreshTokenSecret = process.env.JWT_REFRESH_SECRET;
    this.accessTokenExpiry = '15m';
    this.refreshTokenExpiry = '7d';
  }

  generateTokens(user) {
    const payload = {
      userId: user.id,
      email: user.email,
      role: user.role,
      permissions: user.permissions
    };

    const accessToken = jwt.sign(payload, this.accessTokenSecret, {
      expiresIn: this.accessTokenExpiry,
      issuer: 'document-generator',
      audience: 'document-generator-users'
    });

    const refreshToken = jwt.sign(
      { userId: user.id, tokenId: crypto.randomUUID() },
      this.refreshTokenSecret,
      {
        expiresIn: this.refreshTokenExpiry,
        issuer: 'document-generator',
        audience: 'document-generator-refresh'
      }
    );

    return { accessToken, refreshToken };
  }

  verifyAccessToken(token) {
    try {
      return jwt.verify(token, this.accessTokenSecret, {
        issuer: 'document-generator',
        audience: 'document-generator-users'
      });
    } catch (error) {
      throw new Error('Invalid access token');
    }
  }

  verifyRefreshToken(token) {
    try {
      return jwt.verify(token, this.refreshTokenSecret, {
        issuer: 'document-generator',
        audience: 'document-generator-refresh'
      });
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }
}
```

### 2.3 Sistema de Roles y Permisos
```javascript
// shared/models/Permission.js
const permissions = {
  // Document permissions
  'documents:create': 'Create new documents',
  'documents:read': 'Read documents',
  'documents:update': 'Update documents',
  'documents:delete': 'Delete documents',
  'documents:share': 'Share documents',
  
  // AI permissions
  'ai:generate': 'Generate content with AI',
  'ai:fine-tune': 'Fine-tune AI models',
  'ai:admin': 'Admin AI settings',
  
  // User management
  'users:read': 'View user information',
  'users:update': 'Update user information',
  'users:delete': 'Delete users',
  'users:invite': 'Invite new users',
  
  // Admin permissions
  'admin:system': 'System administration',
  'admin:security': 'Security administration',
  'admin:audit': 'View audit logs'
};

const roles = {
  'viewer': [
    'documents:read'
  ],
  'editor': [
    'documents:create',
    'documents:read',
    'documents:update',
    'ai:generate'
  ],
  'admin': [
    'documents:create',
    'documents:read',
    'documents:update',
    'documents:delete',
    'documents:share',
    'ai:generate',
    'users:read',
    'users:invite'
  ],
  'super-admin': Object.keys(permissions)
};

module.exports = { permissions, roles };
```

## 3. Seguridad de Datos

### 3.1 Encriptación de Datos
```javascript
// shared/security/encryption.js
const crypto = require('crypto');
const bcrypt = require('bcrypt');

class EncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.keyLength = 32;
    this.ivLength = 16;
    this.tagLength = 16;
    this.saltRounds = 12;
  }

  // Encriptación de datos sensibles
  encrypt(text, key) {
    const iv = crypto.randomBytes(this.ivLength);
    const cipher = crypto.createCipher(this.algorithm, key);
    cipher.setAAD(Buffer.from('document-generator', 'utf8'));
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const tag = cipher.getAuthTag();
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      tag: tag.toString('hex')
    };
  }

  decrypt(encryptedData, key) {
    const decipher = crypto.createDecipher(this.algorithm, key);
    decipher.setAAD(Buffer.from('document-generator', 'utf8'));
    decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));
    
    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  // Hash de contraseñas
  async hashPassword(password) {
    return await bcrypt.hash(password, this.saltRounds);
  }

  async verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
  }

  // Generación de claves
  generateKey() {
    return crypto.randomBytes(this.keyLength).toString('hex');
  }

  // Hash de documentos para integridad
  hashDocument(content) {
    return crypto.createHash('sha256').update(content).digest('hex');
  }
}
```

### 3.2 Protección de Documentos
```javascript
// services/document-service/src/security/DocumentSecurity.js
class DocumentSecurity {
  constructor() {
    this.encryptionService = new EncryptionService();
  }

  // Encriptar contenido de documentos sensibles
  async encryptDocumentContent(content, documentId) {
    const key = await this.getDocumentKey(documentId);
    return this.encryptionService.encrypt(content, key);
  }

  // Desencriptar contenido de documentos
  async decryptDocumentContent(encryptedContent, documentId) {
    const key = await this.getDocumentKey(documentId);
    return this.encryptionService.decrypt(encryptedContent, key);
  }

  // Verificar permisos de acceso
  async checkDocumentAccess(userId, documentId, action) {
    const document = await Document.findById(documentId);
    if (!document) {
      throw new Error('Document not found');
    }

    // Verificar si es el propietario
    if (document.userId === userId) {
      return true;
    }

    // Verificar colaboradores
    const collaboration = await DocumentCollaborator.findOne({
      documentId,
      userId
    });

    if (!collaboration) {
      throw new Error('Access denied');
    }

    // Verificar permisos específicos
    const rolePermissions = roles[collaboration.role];
    const requiredPermission = `documents:${action}`;
    
    return rolePermissions.includes(requiredPermission);
  }

  // Auditoría de acceso
  async logDocumentAccess(userId, documentId, action, ipAddress) {
    await AuditLog.create({
      userId,
      documentId,
      action,
      ipAddress,
      timestamp: new Date(),
      userAgent: req.headers['user-agent']
    });
  }
}
```

## 4. Seguridad de Red

### 4.1 Rate Limiting
```javascript
// shared/middleware/rateLimiting.js
const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const Redis = require('ioredis');

const redis = new Redis(process.env.REDIS_URL);

// Rate limiting general
const generalLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.call(...args),
  }),
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // máximo 100 requests por IP
  message: 'Too many requests from this IP',
  standardHeaders: true,
  legacyHeaders: false,
});

// Rate limiting para generación de IA
const aiLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.call(...args),
  }),
  windowMs: 60 * 1000, // 1 minuto
  max: 10, // máximo 10 requests de IA por minuto
  keyGenerator: (req) => req.user.id, // por usuario
  message: 'AI generation rate limit exceeded',
});

// Rate limiting para autenticación
const authLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args) => redis.call(...args),
  }),
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 5, // máximo 5 intentos de login
  skipSuccessfulRequests: true,
  message: 'Too many authentication attempts',
});

module.exports = { generalLimiter, aiLimiter, authLimiter };
```

### 4.2 CORS y Headers de Seguridad
```javascript
// shared/middleware/security.js
const helmet = require('helmet');
const cors = require('cors');

const securityMiddleware = [
  // Helmet para headers de seguridad
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        fontSrc: ["'self'", "https://fonts.gstatic.com"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", "wss:", "https:"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    }
  }),

  // CORS configuration
  cors({
    origin: function (origin, callback) {
      const allowedOrigins = process.env.ALLOWED_ORIGINS.split(',');
      if (!origin || allowedOrigins.includes(origin)) {
        callback(null, true);
      } else {
        callback(new Error('Not allowed by CORS'));
      }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
  })
];

module.exports = securityMiddleware;
```

## 5. Monitoreo y Detección de Amenazas

### 5.1 Sistema de Detección de Intrusiones
```javascript
// shared/security/ids.js
class IntrusionDetectionSystem {
  constructor() {
    this.suspiciousPatterns = [
      /union.*select/i,
      /script.*alert/i,
      /<script/i,
      /javascript:/i,
      /\.\.\//g,
      /eval\(/i,
      /exec\(/i
    ];
    
    this.failedAttempts = new Map();
    this.blockedIPs = new Set();
  }

  analyzeRequest(req, res, next) {
    const { ip, body, query, params } = req;
    
    // Verificar si la IP está bloqueada
    if (this.blockedIPs.has(ip)) {
      return res.status(403).json({ error: 'IP blocked' });
    }

    // Analizar patrones sospechosos
    const requestData = JSON.stringify({ body, query, params });
    
    for (const pattern of this.suspiciousPatterns) {
      if (pattern.test(requestData)) {
        this.logSuspiciousActivity(ip, 'Suspicious pattern detected', requestData);
        return res.status(400).json({ error: 'Invalid request' });
      }
    }

    // Verificar intentos fallidos
    this.checkFailedAttempts(ip);
    
    next();
  }

  logSuspiciousActivity(ip, reason, data) {
    console.warn(`Suspicious activity detected: ${ip} - ${reason}`);
    
    // Incrementar contador de intentos fallidos
    const attempts = this.failedAttempts.get(ip) || 0;
    this.failedAttempts.set(ip, attempts + 1);

    // Bloquear IP si hay demasiados intentos
    if (attempts >= 5) {
      this.blockedIPs.add(ip);
      console.error(`IP ${ip} blocked due to suspicious activity`);
    }

    // Log a base de datos para auditoría
    AuditLog.create({
      type: 'security_incident',
      ipAddress: ip,
      reason: reason,
      data: data,
      timestamp: new Date()
    });
  }

  checkFailedAttempts(ip) {
    const attempts = this.failedAttempts.get(ip) || 0;
    if (attempts > 0) {
      // Reducir contador con el tiempo
      setTimeout(() => {
        const currentAttempts = this.failedAttempts.get(ip) || 0;
        if (currentAttempts > 0) {
          this.failedAttempts.set(ip, currentAttempts - 1);
        }
      }, 60000); // 1 minuto
    }
  }
}
```

### 5.2 Logging de Seguridad
```javascript
// shared/logging/securityLogger.js
const winston = require('winston');

const securityLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'security' },
  transports: [
    new winston.transports.File({ 
      filename: 'security.log',
      level: 'warn'
    }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

class SecurityLogger {
  static logAuthentication(userId, success, ipAddress, userAgent) {
    const level = success ? 'info' : 'warn';
    securityLogger.log(level, 'Authentication attempt', {
      userId,
      success,
      ipAddress,
      userAgent,
      timestamp: new Date()
    });
  }

  static logAuthorization(userId, resource, action, success) {
    const level = success ? 'info' : 'warn';
    securityLogger.log(level, 'Authorization check', {
      userId,
      resource,
      action,
      success,
      timestamp: new Date()
    });
  }

  static logDataAccess(userId, documentId, action, ipAddress) {
    securityLogger.info('Data access', {
      userId,
      documentId,
      action,
      ipAddress,
      timestamp: new Date()
    });
  }

  static logSecurityIncident(type, details, severity = 'medium') {
    const level = severity === 'high' ? 'error' : 'warn';
    securityLogger.log(level, 'Security incident', {
      type,
      details,
      severity,
      timestamp: new Date()
    });
  }
}

module.exports = SecurityLogger;
```

## 6. Cumplimiento y Auditoría

### 6.1 Sistema de Auditoría
```javascript
// shared/models/AuditLog.js
const { DataTypes } = require('sequelize');

const AuditLog = {
  id: {
    type: DataTypes.UUID,
    primaryKey: true,
    defaultValue: DataTypes.UUIDV4
  },
  userId: {
    type: DataTypes.UUID,
    allowNull: true,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  action: {
    type: DataTypes.STRING,
    allowNull: false
  },
  resource: {
    type: DataTypes.STRING,
    allowNull: true
  },
  resourceId: {
    type: DataTypes.UUID,
    allowNull: true
  },
  ipAddress: {
    type: DataTypes.INET,
    allowNull: true
  },
  userAgent: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  details: {
    type: DataTypes.JSONB,
    allowNull: true
  },
  timestamp: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
};

// Middleware de auditoría
const auditMiddleware = (action, resource) => {
  return async (req, res, next) => {
    const originalSend = res.send;
    
    res.send = function(data) {
      // Log después de que la respuesta se envíe
      AuditLog.create({
        userId: req.user?.id,
        action: action,
        resource: resource,
        resourceId: req.params.id,
        ipAddress: req.ip,
        userAgent: req.headers['user-agent'],
        details: {
          method: req.method,
          url: req.url,
          statusCode: res.statusCode,
          responseSize: data?.length || 0
        }
      });
      
      originalSend.call(this, data);
    };
    
    next();
  };
};

module.exports = { AuditLog, auditMiddleware };
```

### 6.2 Cumplimiento GDPR
```javascript
// services/user-service/src/gdpr/GDPRService.js
class GDPRService {
  // Derecho al olvido
  async deleteUserData(userId) {
    const transaction = await sequelize.transaction();
    
    try {
      // Anonimizar datos de usuario
      await User.update({
        email: `deleted_${Date.now()}@deleted.com`,
        firstName: 'Deleted',
        lastName: 'User',
        passwordHash: null
      }, {
        where: { id: userId },
        transaction
      });

      // Eliminar documentos del usuario
      await Document.destroy({
        where: { userId },
        transaction
      });

      // Eliminar logs de auditoría (mantener por período legal)
      const cutoffDate = new Date();
      cutoffDate.setFullYear(cutoffDate.getFullYear() - 7); // 7 años
      
      await AuditLog.destroy({
        where: {
          userId,
          timestamp: { [Op.lt]: cutoffDate }
        },
        transaction
      });

      await transaction.commit();
    } catch (error) {
      await transaction.rollback();
      throw error;
    }
  }

  // Exportar datos del usuario
  async exportUserData(userId) {
    const user = await User.findByPk(userId);
    const documents = await Document.findAll({
      where: { userId }
    });
    const auditLogs = await AuditLog.findAll({
      where: { userId }
    });

    return {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt
      },
      documents: documents.map(doc => ({
        id: doc.id,
        title: doc.title,
        createdAt: doc.createdAt,
        updatedAt: doc.updatedAt
      })),
      auditLogs: auditLogs.map(log => ({
        action: log.action,
        resource: log.resource,
        timestamp: log.timestamp
      }))
    };
  }

  // Consentimiento de datos
  async updateConsent(userId, consentData) {
    await UserConsent.upsert({
      userId,
      marketing: consentData.marketing || false,
      analytics: consentData.analytics || false,
      personalization: consentData.personalization || false,
      updatedAt: new Date()
    });
  }
}
```

## 7. Configuración de Seguridad

### 7.1 Variables de Entorno Seguras
```bash
# .env.example
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/documents
REDIS_URL=redis://localhost:6379

# JWT Secrets (generar con: openssl rand -hex 32)
JWT_ACCESS_SECRET=your-access-secret-here
JWT_REFRESH_SECRET=your-refresh-secret-here

# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Security
ENCRYPTION_KEY=your-encryption-key-here
MFA_ISSUER=Document Generator

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Logging
LOG_LEVEL=info
SECURITY_LOG_LEVEL=warn
```

### 7.2 Configuración de Producción
```yaml
# k8s/security-config.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  jwt-access-secret: <base64-encoded-jwt-secret>
  jwt-refresh-secret: <base64-encoded-refresh-secret>
  encryption-key: <base64-encoded-encryption-key>
  openai-api-key: <base64-encoded-openai-key>
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: security-config
data:
  ALLOWED_ORIGINS: "https://yourdomain.com"
  RATE_LIMIT_WINDOW_MS: "900000"
  RATE_LIMIT_MAX_REQUESTS: "100"
  LOG_LEVEL: "info"
  SECURITY_LOG_LEVEL: "warn"
```

## 8. Testing de Seguridad

### 8.1 Tests de Seguridad
```javascript
// tests/security/security.test.js
const request = require('supertest');
const app = require('../../src/app');

describe('Security Tests', () => {
  describe('Authentication', () => {
    it('should reject requests without token', async () => {
      const response = await request(app)
        .get('/api/documents')
        .expect(401);
      
      expect(response.body.error).toBe('Token required');
    });

    it('should reject invalid tokens', async () => {
      const response = await request(app)
        .get('/api/documents')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401);
      
      expect(response.body.error).toBe('Invalid token');
    });
  });

  describe('Authorization', () => {
    it('should prevent access to other users documents', async () => {
      const user1Token = await getAuthToken('user1@test.com');
      const user2Token = await getAuthToken('user2@test.com');
      
      // Crear documento como user1
      const docResponse = await request(app)
        .post('/api/documents')
        .set('Authorization', `Bearer ${user1Token}`)
        .send({ title: 'User1 Document' });
      
      const documentId = docResponse.body.id;
      
      // Intentar acceder como user2
      const response = await request(app)
        .get(`/api/documents/${documentId}`)
        .set('Authorization', `Bearer ${user2Token}`)
        .expect(403);
      
      expect(response.body.error).toBe('Access denied');
    });
  });

  describe('Input Validation', () => {
    it('should prevent SQL injection', async () => {
      const token = await getAuthToken('test@test.com');
      
      const response = await request(app)
        .get('/api/documents')
        .set('Authorization', `Bearer ${token}`)
        .query({ search: "'; DROP TABLE documents; --" })
        .expect(400);
      
      expect(response.body.error).toBe('Invalid input');
    });

    it('should prevent XSS attacks', async () => {
      const token = await getAuthToken('test@test.com');
      
      const response = await request(app)
        .post('/api/documents')
        .set('Authorization', `Bearer ${token}`)
        .send({
          title: '<script>alert("xss")</script>',
          content: 'Test content'
        })
        .expect(400);
      
      expect(response.body.error).toBe('Invalid input');
    });
  });

  describe('Rate Limiting', () => {
    it('should enforce rate limits', async () => {
      const token = await getAuthToken('test@test.com');
      
      // Hacer muchas requests rápidamente
      const promises = Array(150).fill().map(() =>
        request(app)
          .get('/api/documents')
          .set('Authorization', `Bearer ${token}`)
      );
      
      const responses = await Promise.all(promises);
      const rateLimitedResponses = responses.filter(r => r.status === 429);
      
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });
});
```

Esta implementación de seguridad proporciona una base sólida para proteger el sistema de generación de documentos con IA, cumpliendo con estándares de seguridad modernos y regulaciones de privacidad.







