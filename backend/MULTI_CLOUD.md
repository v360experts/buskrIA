# Configuración Multi-Nube

Este proyecto soporta múltiples proveedores de nube para embeddings y vector search, permitiendo flexibilidad y portabilidad entre GCP, Azure y OpenAI.

## 🏗️ Arquitectura Multi-Nube

El sistema utiliza una arquitectura de abstracción que detecta automáticamente qué proveedor usar basado en las variables de entorno configuradas.

```
┌─────────────────────────────────────────┐
│         Aplicación FastAPI              │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐    ┌─────────▼─────────┐
│ Embedding      │    │ Vector Search     │
│ Service        │    │ Service           │
│ (Abstracción)  │    │ (Abstracción)     │
└───────┬────────┘    └─────────┬─────────┘
        │                       │
   ┌────┴────┐            ┌─────┴─────┐
   │         │            │           │
┌──▼──┐  ┌──▼──┐    ┌────▼───┐  ┌───▼────┐
│GCP  │  │OpenAI│    │ Vertex │  │ Azure  │
│Vertex│  │     │    │   AI   │  │   AI   │
│  AI  │  │     │    │ Search │  │ Search │
└──────┘  └─────┘    └────────┘  └────────┘
```

## 📋 Proveedores Soportados

### Embeddings

1. **Vertex AI (GCP)** - `text-embedding-004`
   - Dimensión: 768
   - Requiere: `GCP_PROJECT_ID`
   - Costo: ~$0.0001 por 1000 caracteres

2. **OpenAI** - `text-embedding-3-small` o `text-embedding-3-large`
   - Dimensión: 1536 (small) o 3072 (large)
   - Requiere: `OPENAI_API_KEY`
   - Costo: ~$0.02 por 1M tokens (small)

### Vector Search

1. **Vertex AI Vector Search (GCP)**
   - Requiere: `VECTOR_SEARCH_ENDPOINT_ID`, `VECTOR_SEARCH_DEPLOYED_INDEX_ID`
   - Costo: ~$0.10 por 1000 queries

2. **Azure AI Search**
   - Requiere: `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`
   - Costo: Depende del tier (Basic/Standard)

## 🔧 Configuración

### Opción 1: Todo en GCP

```env
# Embeddings
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Vector Search
VECTOR_SEARCH_ENDPOINT_ID=projects/.../indexEndpoints/...
VECTOR_SEARCH_DEPLOYED_INDEX_ID=your-deployed-index-id
```

**Ventajas:**
- Todo en un solo proveedor
- Integración nativa
- Menor latencia entre servicios

### Opción 2: Todo en Azure

```env
# Embeddings (usando OpenAI)
OPENAI_API_KEY=sk-your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Vector Search
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=products-index
```

**Ventajas:**
- Azure AI Search es robusto
- Puede usar OpenAI para embeddings
- Buena integración con otros servicios Azure

### Opción 3: Híbrido (Recomendado para flexibilidad)

```env
# Embeddings con OpenAI (más económico)
OPENAI_API_KEY=sk-your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Vector Search con Azure
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_API_KEY=your-api-key
AZURE_SEARCH_INDEX_NAME=products-index
```

**Ventajas:**
- Flexibilidad máxima
- Puedes cambiar proveedores fácilmente
- Optimización de costos

## 🚀 Inicio Rápido

### 1. Configurar Variables de Entorno

Copia `env.example` a `.env` y configura según tu proveedor:

```bash
cp env.example .env
# Edita .env con tus credenciales
```

### 2. Instalar Dependencias

**Para GCP:**
```bash
pip install google-cloud-aiplatform vertexai
```

**Para Azure:**
```bash
pip install azure-search-documents azure-identity
```

**Para OpenAI:**
```bash
pip install openai
```

**O instala todas:**
```bash
pip install -r requirements.txt
```

### 3. Verificar Configuración

El sistema mostrará qué proveedor está usando al iniciar:

```
🔵 Usando Vertex AI (GCP) para embeddings
🔵 Usando Vertex AI Vector Search (GCP)
```

O:

```
🟢 Usando OpenAI para embeddings
🟣 Usando Azure AI Search
```

## 📊 Comparación de Proveedores

### Embeddings

| Proveedor | Modelo | Dimensión | Costo/1M tokens | Latencia |
|-----------|--------|-----------|------------------|----------|
| Vertex AI | text-embedding-004 | 768 | ~$0.10 | Baja |
| OpenAI | text-embedding-3-small | 1536 | ~$0.20 | Media |
| OpenAI | text-embedding-3-large | 3072 | ~$1.30 | Media |

### Vector Search

| Proveedor | Queries/seg | Latencia | Costo/mes |
|-----------|-------------|----------|-----------|
| Vertex AI | 100+ | <100ms | Pay-per-use |
| Azure AI Search | 50-1000* | <200ms | Tier-based |

*Depende del tier

## 🔄 Migración entre Proveedores

### De GCP a Azure

1. Configurar Azure AI Search
2. Cambiar variables de entorno
3. Re-indexar productos (los embeddings son compatibles si usas la misma dimensión)

```bash
# Cambiar .env
# De:
VECTOR_SEARCH_ENDPOINT_ID=...
# A:
AZURE_SEARCH_ENDPOINT=https://...
AZURE_SEARCH_API_KEY=...
```

### De Vertex AI a OpenAI (embeddings)

1. Cambiar variables de entorno
2. Re-generar embeddings (dimensiones diferentes)

```bash
# Cambiar .env
# De:
GCP_PROJECT_ID=...
# A:
OPENAI_API_KEY=sk-...
```

**Nota:** Si cambias de proveedor de embeddings, necesitas re-indexar todos los productos porque las dimensiones pueden ser diferentes.

## 🧪 Testing Multi-Nube

### Test de Detección de Proveedor

```python
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService

# Verificar qué proveedor está activo
embedding_provider = EmbeddingService.get_provider()
print(f"Embedding provider: {type(embedding_provider).__name__}")

vector_provider = VectorSearchService.get_provider()
print(f"Vector Search provider: {type(vector_provider).__name__}")
```

### Test de Funcionalidad

```bash
# Ejecutar tests (detectan automáticamente el proveedor)
python -m tests.test_all
```

## 🔐 Seguridad

### GCP

```bash
# Usar Service Account
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# O usar Application Default Credentials
gcloud auth application-default login
```

### Azure

```bash
# Usar API Key (recomendado para desarrollo)
export AZURE_SEARCH_API_KEY=your-key

# O usar Managed Identity (producción)
# Configurar en Azure Portal
```

### OpenAI

```bash
# Usar API Key
export OPENAI_API_KEY=sk-your-key

# Rotar keys regularmente
# Usar diferentes keys por ambiente
```

## 💰 Optimización de Costos

### Estrategia 1: Embeddings con OpenAI + Vector Search con Azure

- OpenAI embeddings: ~$0.20/1M tokens
- Azure AI Search: Tier Basic desde $75/mes
- **Total estimado:** ~$100-200/mes para 1M búsquedas

### Estrategia 2: Todo con GCP

- Vertex AI embeddings: ~$0.10/1M tokens
- Vector Search: ~$0.10/1000 queries
- **Total estimado:** ~$150-250/mes para 1M búsquedas

### Estrategia 3: Cache Agresivo

- Cache embeddings: Reduce 80% de llamadas
- Cache resultados: Reduce 60% de queries
- **Ahorro:** 50-70% en costos

## 📝 Mejores Prácticas

1. **Usar variables de entorno** - Nunca hardcodear credenciales
2. **Cache de embeddings** - Reducir llamadas a APIs
3. **Batch processing** - Procesar múltiples embeddings juntos
4. **Monitoring** - Monitorear costos y latencia
5. **Fallback** - Implementar fallback entre proveedores
6. **Testing** - Probar con ambos proveedores antes de producción

## 🐛 Troubleshooting

### Error: "No se encontró proveedor configurado"

**Solución:** Verifica que tengas configurado al menos:
- Para embeddings: `GCP_PROJECT_ID` o `OPENAI_API_KEY`
- Para Vector Search: `VECTOR_SEARCH_ENDPOINT_ID` o `AZURE_SEARCH_ENDPOINT`

### Error: "Dimension mismatch"

**Solución:** Si cambias de proveedor de embeddings, necesitas re-indexar porque las dimensiones son diferentes:
- Vertex AI: 768
- OpenAI small: 1536
- OpenAI large: 3072

### Error: "Authentication failed"

**Solución:**
- GCP: Verifica `GOOGLE_APPLICATION_CREDENTIALS`
- Azure: Verifica `AZURE_SEARCH_API_KEY`
- OpenAI: Verifica `OPENAI_API_KEY`

## 📚 Recursos

- [Vertex AI Embeddings](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings)
- [Azure AI Search](https://learn.microsoft.com/azure/search/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Multi-Cloud Best Practices](https://cloud.google.com/architecture/multi-cloud)

