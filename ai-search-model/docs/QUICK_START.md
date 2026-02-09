# 🚀 Guía de Inicio Rápido - AI Search Model

## ⚡ Instalación en 3 Pasos

### 1. **Instalación Automática (Recomendado)**

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### 2. **Iniciar el Sistema**
```bash
python start.py
```

### 3. **Acceder a la Aplicación**
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs

## 🎯 Uso Básico

### 1. **Ver Demostración**
```bash
python demo.py
```

### 2. **Indexar un Documento**
```bash
curl -X POST "http://localhost:8000/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Documento",
    "content": "Contenido del documento...",
    "document_type": "text"
  }'
```

### 3. **Buscar Documentos**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "inteligencia artificial",
    "search_type": "semantic",
    "limit": 10
  }'
```

## 🔍 Tipos de Búsqueda

| Tipo | Descripción | Cuándo Usar |
|------|-------------|-------------|
| **Semántica** | Busca por significado | Conceptos, ideas relacionadas |
| **Palabras Clave** | Busca términos exactos | Nombres, códigos, términos específicos |
| **Híbrida** | Combina ambos métodos | Búsquedas generales, mejor cobertura |

## 📊 Ejemplos de Búsqueda

### Búsqueda Semántica
```json
{
  "query": "machine learning",
  "search_type": "semantic"
}
```
**Encuentra**: "aprendizaje automático", "ML", "algoritmos de IA"

### Búsqueda por Palabras Clave
```json
{
  "query": "Python",
  "search_type": "keyword"
}
```
**Encuentra**: Solo documentos que contengan exactamente "Python"

### Búsqueda Híbrida
```json
{
  "query": "desarrollo web",
  "search_type": "hybrid"
}
```
**Encuentra**: Mejor balance entre precisión y cobertura

## 🛠️ Comandos Útiles

### Verificar Estado del Sistema
```bash
curl http://localhost:8000/health
```

### Ver Estadísticas
```bash
curl http://localhost:8000/stats
```

### Ejecutar Pruebas
```bash
python test_system.py
```

### Solo Backend
```bash
python start.py --backend-only
```

### Solo Frontend
```bash
python start.py --frontend-only
```

## 🔧 Configuración Rápida

### Variables Importantes en `.env`
```env
# Modelo de IA (cambiar para mejor calidad)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Límites de búsqueda
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100

# Pesos de búsqueda híbrida
SEMANTIC_WEIGHT=0.7
KEYWORD_WEIGHT=0.3
```

## 🚨 Solución de Problemas

### Error: "No se puede conectar con el servidor"
1. Verificar que el backend esté ejecutándose
2. Comprobar puerto 8000 disponible
3. Revisar logs en consola

### Error: "Dependencias faltantes"
```bash
# Reinstalar dependencias
pip install -r requirements.txt
cd frontend && npm install
```

### Error: "Memoria insuficiente"
1. Reducir `MAX_CONTENT_LENGTH` en `.env`
2. Usar modelo más pequeño
3. Procesar documentos en lotes más pequeños

## 📈 Optimización

### Para Mejor Rendimiento
- Usar SSD para almacenamiento
- Aumentar RAM disponible
- Usar modelo más pequeño para desarrollo

### Para Mejor Calidad
- Usar `sentence-transformers/all-mpnet-base-v2`
- Aumentar `SEMANTIC_WEIGHT` a 0.8
- Procesar documentos con más contexto

## 🎉 ¡Listo!

Tu sistema de búsqueda IA está funcionando. Explora la interfaz web y experimenta con diferentes tipos de búsqueda.

**Próximos pasos:**
1. Indexa tus propios documentos
2. Experimenta con diferentes consultas
3. Ajusta la configuración según tus necesidades
4. Revisa la documentación completa en `README.md`



























