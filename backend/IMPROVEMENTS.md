# Mejoras y Optimizaciones - Backend

Este documento lista mejoras recomendadas para hacer el backend más profesional, escalable y eficiente.

## 🚀 Optimizaciones de Performance

### 1. Cache de Embeddings

**Problema actual:** Cada búsqueda genera embeddings desde cero, incluso para queries repetidas.

**Solución:**
```python
# Implementar Redis para cache de embeddings
from redis import Redis
import hashlib
import json

redis_client = Redis(host='localhost', port=6379, db=0)

def get_cached_embedding(text: str) -> Optional[List[float]]:
    """Obtener embedding del cache si existe"""
    cache_key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

def cache_embedding(text: str, embedding: List[float], ttl: int = 86400):
    """Guardar embedding en cache (24 horas por defecto)"""
    cache_key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
    redis_client.setex(cache_key, ttl, json.dumps(embedding))
```

**Beneficios:**
- Reduce llamadas a Vertex AI (ahorro de costos)
- Respuestas más rápidas para queries comunes
- Menor latencia en búsquedas repetidas

**Implementación:**
1. Agregar `redis==5.0.1` a `requirements.txt`
2. Modificar `vertex_ai_service.py` para usar cache
3. Configurar Redis en variables de entorno

### 2. Cache de Resultados de Búsqueda

**Problema actual:** Mismas búsquedas se procesan completamente cada vez.

**Solución:**
```python
def get_cached_search(query: str, filters: dict) -> Optional[dict]:
    """Cache de resultados de búsqueda"""
    cache_key = f"search:{hashlib.md5(f'{query}{json.dumps(filters)}'.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None
```

**TTL recomendado:**
- Búsquedas populares: 1 hora
- Búsquedas generales: 15 minutos
- Búsquedas con filtros: 5 minutos

### 3. Batch Processing de Embeddings

**Problema actual:** Embeddings se generan uno por uno.

**Solución:**
```python
def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generar múltiples embeddings en una sola llamada"""
    model = TextEmbeddingModel.from_pretrained("text-embedding-004")
    embeddings = model.get_embeddings(texts)  # Batch processing
    return [emb.values for emb in embeddings]
```

**Beneficios:**
- Reduce latencia en seed masivo
- Más eficiente para actualizaciones en lote
- Menor costo por embedding

### 4. Connection Pooling para MongoDB

**Problema actual:** Conexiones se crean sin pooling.

**Solución:**
```python
from pymongo import MongoClient
from pymongo.pool import PoolOptions

client = MongoClient(
    mongodb_uri,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=45000,
    waitQueueTimeoutMS=10000
)
```

**Beneficios:**
- Mejor manejo de concurrencia
- Reutilización de conexiones
- Menor overhead

## 📊 Optimizaciones de Base de Datos

### 5. Índices en MongoDB

**Problema actual:** Búsquedas por ID sin índices optimizados.

**Solución:**
```python
# Crear índices al inicializar
db.products.create_index([("normalized_name", "text")])
db.products.create_index([("category", 1)])
db.products.create_index([("brand", 1)])
db.products.create_index([("price", 1)])
db.products.create_index([("stock", -1)])
db.products.create_index([("popularity", -1)])
db.products.create_index([("is_sponsored", 1), ("popularity", -1)])
```

**Beneficios:**
- Búsquedas más rápidas
- Mejor rendimiento en filtros
- Optimización de queries complejas

### 6. Paginación Eficiente

**Problema actual:** Se retornan todos los resultados sin paginación.

**Solución:**
```python
class SearchRequest(BaseModel):
    query: str
    page: int = 1
    page_size: int = 20
    # ... otros campos

# En search_service.py
skip = (page - 1) * page_size
products = products[skip:skip + page_size]

return {
    "products": products,
    "total": total,
    "page": page,
    "page_size": page_size,
    "total_pages": (total + page_size - 1) // page_size
}
```

### 7. Agregación Pipeline para Estadísticas

**Problema actual:** Estadísticas se calculan en Python.

**Solución:**
```python
def get_product_stats():
    """Obtener estadísticas usando aggregation pipeline"""
    pipeline = [
        {
            "$group": {
                "_id": None,
                "avg_price": {"$avg": "$price"},
                "avg_stock": {"$avg": "$stock"},
                "total_products": {"$sum": 1},
                "sponsored_count": {
                    "$sum": {"$cond": ["$is_sponsored", 1, 0]}
                }
            }
        }
    ]
    return list(db.products.aggregate(pipeline))
```

## 🔒 Seguridad y Validación

### 8. Rate Limiting

**Problema actual:** Sin límites de requests.

**Solución:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/search")
@limiter.limit("10/minute")  # 10 búsquedas por minuto
async def search_products(request: Request, ...):
    # ...
```

### 9. Validación de Input Más Estricta

**Mejoras:**
```python
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    min_price: Optional[float] = Field(None, ge=0, le=100000)
    max_price: Optional[float] = Field(None, ge=0, le=100000)
    
    @validator('max_price')
    def max_price_greater_than_min(cls, v, values):
        if v and values.get('min_price') and v < values['min_price']:
            raise ValueError('max_price must be greater than min_price')
```

### 10. Logging y Monitoreo

**Solución:**
```python
import logging
from pythonjsonlogger import jsonlogger

# Configurar logging estructurado
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# En los servicios
logger.info("search_performed", extra={
    "query": query,
    "results_count": len(results),
    "response_time_ms": response_time
})
```

## 🔄 Mejoras de Arquitectura

### 11. Background Tasks para Actualizaciones

**Problema actual:** Actualizaciones de embeddings bloquean requests.

**Solución:**
```python
from fastapi import BackgroundTasks

@app.put("/products/{product_id}")
async def update_product(
    product_id: str,
    product: ProductUpdate,
    background_tasks: BackgroundTasks
):
    # Actualizar en MongoDB inmediatamente
    updated = await product_service.update_product(product_id, product)
    
    # Actualizar embedding en background
    background_tasks.add_task(
        product_service._update_product_embedding_async,
        product_id
    )
    
    return updated
```

### 12. Circuit Breaker para Vertex AI

**Problema actual:** Si Vertex AI falla, todo falla.

**Solución:**
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def get_embedding_with_circuit_breaker(text: str):
    """Embedding con circuit breaker"""
    return vertex_ai.get_embedding(text)
```

### 13. Retry Logic con Exponential Backoff

**Solución:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def get_embedding_with_retry(text: str):
    """Embedding con retry automático"""
    return vertex_ai.get_embedding(text)
```

## 📈 Escalabilidad

### 14. Async/Await Consistente

**Problema actual:** Mezcla de sync y async.

**Solución:**
- Convertir todas las operaciones de MongoDB a async usando `motor`
- Usar `async def` consistentemente
- Usar `asyncio.gather()` para operaciones paralelas

### 15. Message Queue para Procesamiento Asíncrono

**Solución:**
```python
# Usar Celery o RQ para tareas pesadas
from celery import Celery

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def update_product_embedding_task(product_id: str):
    # Procesar en background
    pass
```

### 16. Health Checks Mejorados

**Solución:**
```python
@app.get("/health")
async def health_check():
    """Health check completo"""
    checks = {
        "status": "healthy",
        "mongodb": await check_mongodb(),
        "vertex_ai": await check_vertex_ai(),
        "redis": await check_redis(),
        "vector_search": await check_vector_search()
    }
    
    if all(v for k, v in checks.items() if k != "status"):
        return checks
    else:
        raise HTTPException(status_code=503, detail=checks)
```

## 🧪 Testing

### 17. Tests Unitarios Completos

**Faltante:**
- Tests para cada servicio
- Tests de edge cases
- Tests de performance
- Mock de servicios externos

### 18. Integration Tests con Docker Compose

**Solución:**
```yaml
# docker-compose.test.yml
version: '3.8'
services:
  mongodb:
    image: mongo:6
  redis:
    image: redis:7
```

## 💰 Optimización de Costos

### 19. Compresión de Embeddings

**Solución:**
```python
import numpy as np
from sklearn.decomposition import PCA

# Reducir dimensión de 768 a 512 (opcional)
pca = PCA(n_components=512)
compressed_embeddings = pca.fit_transform(embeddings)
```

### 20. Lazy Loading de Embeddings

**Solución:**
- Solo generar embeddings cuando se necesiten
- Cachear embeddings de productos populares
- Generar embeddings en batch durante horas de bajo tráfico

## 📝 Documentación

### 21. OpenAPI/Swagger Mejorado

**Solución:**
```python
app = FastAPI(
    title="Supermarket Search API",
    description="API completa con ejemplos",
    version="2.0.0",
    openapi_tags=[
        {"name": "products", "description": "Gestión de productos"},
        {"name": "search", "description": "Búsqueda semántica"},
    ]
)
```

### 22. Ejemplos en la Documentación

**Agregar:**
- Ejemplos de requests/responses
- Casos de uso comunes
- Códigos de error y soluciones

## 🎯 Prioridades de Implementación

### Alta Prioridad (Impacto inmediato)
1. ✅ Cache de embeddings (Redis)
2. ✅ Índices en MongoDB
3. ✅ Rate limiting
4. ✅ Logging estructurado

### Media Prioridad (Mejora de calidad)
5. ✅ Paginación
6. ✅ Background tasks
7. ✅ Health checks mejorados
8. ✅ Validación estricta

### Baja Prioridad (Optimizaciones avanzadas)
9. ✅ Circuit breaker
10. ✅ Batch processing
11. ✅ Compresión de embeddings
12. ✅ Message queue

## 📚 Recursos

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [MongoDB Performance](https://www.mongodb.com/docs/manual/administration/analyzing-mongodb-performance/)
- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)
- [Vertex AI Optimization](https://cloud.google.com/vertex-ai/docs)

