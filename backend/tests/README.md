# Tests de Integración

Tests para verificar la conectividad y funcionamiento de todos los servicios.

## Ejemplos de Salida

Ver `EXAMPLE_OUTPUT.md` para ver ejemplos completos de salida de todos los tests, incluyendo:
- ✅ Casos exitosos
- ❌ Casos con errores
- ⏭️ Tests omitidos

## Ejecutar Todos los Tests

```bash
# Desde el directorio backend
python -m tests.test_all
```

O directamente:

```bash
cd backend
python tests/test_all.py
```

## Ejecutar Tests Individuales

### Test de MongoDB

```bash
python tests/test_mongodb.py
```

Verifica:
- ✅ Conexión a MongoDB
- ✅ Escritura y lectura
- ✅ Colecciones existentes

### Test de Vertex AI

```bash
python tests/test_vertex_ai.py
```

Verifica:
- ✅ Credenciales de GCP
- ✅ Generación de embeddings
- ✅ Upsert de vectores
- ✅ Búsqueda en Vector Search

### Test de Servicios

```bash
python tests/test_services.py
```

Verifica:
- ✅ Product Service (CRUD)
- ✅ Search Service (búsqueda semántica)
- ✅ Related Service (productos relacionados)

## Requisitos

Antes de ejecutar los tests, asegúrate de tener:

1. **Variables de entorno configuradas** (`.env`):
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB_NAME=supermarket_db
   GCP_PROJECT_ID=tu-proyecto-id
   GCP_LOCATION=us-central1
   VECTOR_SEARCH_ENDPOINT_ID=tu-endpoint-id
   VECTOR_SEARCH_DEPLOYED_INDEX_ID=tu-deployed-index-id
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```

2. **MongoDB corriendo** (local o remoto)

3. **Credenciales de GCP** configuradas

4. **APIs de GCP activadas**:
   - Vertex AI API
   - Vector Search configurado (opcional para algunos tests)

## Interpretación de Resultados

- ✅ **PASS**: Test exitoso
- ❌ **FAIL**: Test fallido (revisa el mensaje de error)
- ⏭️ **SKIP**: Test omitido (normal si no está configurado, ej: Vector Search)

## Troubleshooting

### Error: "MongoDB connection failed"
- Verifica que MongoDB esté corriendo
- Revisa `MONGODB_URI` en `.env`

### Error: "Could not generate embedding"
- Verifica credenciales de GCP
- Asegúrate de que la API de Vertex AI esté activada
- Verifica que `GOOGLE_APPLICATION_CREDENTIALS` apunte al archivo correcto

### Error: "Vector Search endpoint not configured"
- Esto es normal si no has configurado Vector Search aún
- Los tests de Vector Search se omitirán automáticamente

### Error: "No module named 'app'"
- Ejecuta los tests desde el directorio `backend/`
- O usa: `python -m tests.test_mongodb`

