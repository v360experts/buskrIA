# Guía de Inicio Rápido

Esta guía te ayudará a poner en marcha el sistema de búsqueda de supermercado.

## Prerrequisitos

1. **Python 3.10+** instalado
2. **Node.js 18+** instalado
3. **MongoDB** corriendo (local o remoto)
4. **Cuenta de GCP** con proyecto configurado
5. **Credenciales de GCP** (service account JSON)

## Paso 1: Configurar Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

### Variables de entorno necesarias:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=supermarket_db
GCP_PROJECT_ID=tu-proyecto-id
GCP_LOCATION=us-central1
VECTOR_SEARCH_INDEX_ID=tu-index-id
VECTOR_SEARCH_ENDPOINT_ID=tu-endpoint-id
VECTOR_SEARCH_DEPLOYED_INDEX_ID=tu-deployed-index-id
PUBSUB_TOPIC_PRODUCT_UPDATES=product-updates
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## Paso 2: Configurar GCP

Sigue las instrucciones en `infrastructure/README.md` para:

1. Activar APIs necesarias
2. Crear índice de Vector Search
3. Crear endpoint y desplegar índice
4. Configurar Pub/Sub

O ejecuta el script de setup básico:

```bash
cd infrastructure
./setup.sh TU_PROJECT_ID us-central1
```

## Paso 3: Cargar Datos Iniciales

```bash
cd backend
python -m app.seed
```

Esto cargará **14 productos** de ejemplo con valores variados de:
- `margin_score` (0.12 - 0.40)
- `popularity` (0.50 - 0.95)
- `stock` (5 - 300)
- `is_sponsored` (True/False)

Perfecto para probar el sistema de ranking completo.

### Ver Estadísticas

```bash
python -m app.seed_stats
```

Muestra estadísticas detalladas de los productos cargados.

## Paso 4: Iniciar Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

El API estará disponible en `http://localhost:8000`

## Paso 5: Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local
# Editar .env.local con la URL del API
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Paso 6: Iniciar Frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

## Verificación

### Opción 1: Tests de Integración (Recomendado)

Ejecuta los tests de integración para verificar todas las conexiones:

```bash
cd backend
python -m tests.test_all
```

O usa el script:

```bash
cd backend
./run_tests.sh
```

Esto verificará:
- ✅ Conexión a MongoDB
- ✅ Generación de embeddings con Vertex AI
- ✅ Vector Search (si está configurado)
- ✅ Servicios principales

### Opción 2: Verificación Manual

1. Abre `http://localhost:3000`
2. Busca "leche" o "nido"
3. Deberías ver productos relacionados

## Endpoints del API

- `GET /` - Información del API
- `POST /products` - Crear producto
- `PUT /products/{id}` - Actualizar producto
- `GET /products/{id}` - Obtener producto
- `POST /search` - Búsqueda semántica
- `GET /products/{id}/related` - Productos relacionados
- `GET /health` - Health check

## Ejemplo de Búsqueda

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "leche condensada",
    "limit": 10
  }'
```

## Troubleshooting

### Error: "Vector Search endpoint not configured"
- Verifica que `VECTOR_SEARCH_ENDPOINT_ID` esté configurado
- Asegúrate de que el índice esté desplegado

### Error: "Could not generate embedding"
- Verifica credenciales de GCP
- Verifica que la API de Vertex AI esté activada
- Verifica que `GOOGLE_APPLICATION_CREDENTIALS` apunte al archivo correcto

### Error: "MongoDB connection failed"
- Verifica que MongoDB esté corriendo
- Verifica `MONGODB_URI` en `.env`

### Frontend no encuentra el API
- Verifica `NEXT_PUBLIC_API_URL` en `.env.local`
- Asegúrate de que el backend esté corriendo

## Próximos Pasos

1. Personalizar productos en `backend/app/seed.py`
2. Ajustar sinónimos en `backend/app/utils/normalization.py`
3. Personalizar ranking en `backend/app/utils/ranking.py`
4. Desplegar en producción siguiendo `infrastructure/README.md`

