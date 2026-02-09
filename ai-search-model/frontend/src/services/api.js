import axios from 'axios';

// Configuración base de la API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Crear instancia de axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    // Agregar timestamp para evitar cache
    config.params = {
      ...config.params,
      _t: Date.now(),
    };
    
    // Log de requests en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Interceptor para responses
api.interceptors.response.use(
  (response) => {
    // Log de responses en desarrollo
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
    }
    
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error);
    
    // Manejo de errores específicos
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          throw new Error(data.detail || 'Solicitud inválida');
        case 401:
          throw new Error('No autorizado');
        case 403:
          throw new Error('Acceso denegado');
        case 404:
          throw new Error('Recurso no encontrado');
        case 429:
          throw new Error('Demasiadas solicitudes. Intenta más tarde');
        case 500:
          throw new Error('Error interno del servidor');
        case 503:
          throw new Error('Servicio no disponible');
        default:
          throw new Error(data.detail || `Error del servidor: ${status}`);
      }
    } else if (error.request) {
      // La solicitud se hizo pero no se recibió respuesta
      throw new Error('No se pudo conectar con el servidor');
    } else {
      // Algo más pasó
      throw new Error(error.message || 'Error desconocido');
    }
  }
);

// Servicios de la API
export const apiService = {
  // Health check
  async checkHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  // Búsqueda de documentos
  async searchDocuments(searchParams) {
    const response = await api.post('/search', searchParams);
    return response.data;
  },

  // Obtener documento por ID
  async getDocument(documentId) {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  // Listar documentos
  async listDocuments(params = {}) {
    const response = await api.get('/documents', { params });
    return response.data;
  },

  // Crear/Indexar documento
  async createDocument(documentData) {
    const response = await api.post('/documents', documentData);
    return response.data;
  },

  // Eliminar documento
  async deleteDocument(documentId) {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },

  // Obtener estadísticas
  async getStatistics() {
    const response = await api.get('/stats');
    return response.data;
  },

  // Subir archivo (para futuras implementaciones)
  async uploadFile(file, metadata = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Funciones de utilidad
export const apiUtils = {
  // Construir URL de búsqueda
  buildSearchUrl(query, options = {}) {
    const params = new URLSearchParams({
      q: query,
      ...options,
    });
    return `/search?${params.toString()}`;
  },

  // Formatear errores de API
  formatError(error) {
    if (error.response) {
      return error.response.data.detail || 'Error del servidor';
    }
    return error.message || 'Error desconocido';
  },

  // Verificar si es un error de red
  isNetworkError(error) {
    return !error.response && error.request;
  },

  // Verificar si es un error de timeout
  isTimeoutError(error) {
    return error.code === 'ECONNABORTED';
  },

  // Retry automático para requests fallidos
  async retryRequest(requestFn, maxRetries = 3, delay = 1000) {
    let lastError;
    
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;
        
        // No reintentar para errores 4xx (excepto 429)
        if (error.response && error.response.status >= 400 && error.response.status < 500 && error.response.status !== 429) {
          throw error;
        }
        
        // Esperar antes del siguiente intento
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
        }
      }
    }
    
    throw lastError;
  },
};

// Hooks personalizados para React Query
export const apiHooks = {
  // Hook para búsqueda
  useSearchQuery(query, options = {}) {
    return {
      queryKey: ['search', query, options],
      queryFn: () => apiService.searchDocuments({ query, ...options }),
      enabled: !!query && query.trim().length > 0,
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 10 * 60 * 1000, // 10 minutos
    };
  },

  // Hook para obtener documento
  useDocumentQuery(documentId) {
    return {
      queryKey: ['document', documentId],
      queryFn: () => apiService.getDocument(documentId),
      enabled: !!documentId,
    };
  },

  // Hook para listar documentos
  useDocumentsQuery(params = {}) {
    return {
      queryKey: ['documents', params],
      queryFn: () => apiService.listDocuments(params),
      staleTime: 2 * 60 * 1000, // 2 minutos
    };
  },

  // Hook para estadísticas
  useStatisticsQuery() {
    return {
      queryKey: ['statistics'],
      queryFn: () => apiService.getStatistics(),
      staleTime: 1 * 60 * 1000, // 1 minuto
    };
  },

  // Hook para health check
  useHealthQuery() {
    return {
      queryKey: ['health'],
      queryFn: () => apiService.checkHealth(),
      refetchInterval: 30 * 1000, // 30 segundos
      retry: 3,
    };
  },
};

// Configuración de la API
export const apiConfig = {
  // URLs base
  baseURL: API_BASE_URL,
  
  // Timeouts
  timeout: 30000,
  
  // Headers por defecto
  defaultHeaders: {
    'Content-Type': 'application/json',
  },
  
  // Configuración de retry
  retryConfig: {
    maxRetries: 3,
    baseDelay: 1000,
    maxDelay: 10000,
  },
  
  // Configuración de cache
  cacheConfig: {
    defaultStaleTime: 5 * 60 * 1000, // 5 minutos
    defaultCacheTime: 10 * 60 * 1000, // 10 minutos
  },
};

// Exportar por defecto
export default api;



























