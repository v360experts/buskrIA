# Backend - FastAPI Supermarket Search

Backend del sistema de búsqueda semántica de productos.

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

## Configuración

### Variables de Entorno Requeridas

- `MONGODB_URI`: URI de conexión a MongoDB
- `MONGODB_DB_NAME`: Nombre de la base de datos
- `GCP_PROJECT_ID`: ID del proyecto de GCP
- `GCP_LOCATION`: Región de GCP (ej: us-central1)
- `VECTOR_SEARCH_INDEX_ID`: ID del índice de Vector Search
- `VECTOR_SEARCH_ENDPOINT_ID`: ID del endpoint de Vector Search
- `VECTOR_SEARCH_DEPLOYED_INDEX_ID`: ID del índice desplegado
- `GOOGLE_APPLICATION_CREDENTIALS`: Ruta al archivo JSON de credenciales

## Ejecución

### Desarrollo Local

```bash
uvicorn app.main:app --reload --port 8000
```

### Con Docker

```bash
docker build -t supermarket-backend .
docker run -p 8000:8080 --env-file .env supermarket-backend
```

## Endpoints

- `POST /products` - Crear producto
- `PUT /products/{id}` - Actualizar producto
- `GET /products/{id}` - Obtener producto
- `POST /search` - Búsqueda semántica
- `GET /products/{id}/related` - Productos relacionados
- `GET /health` - Health check

## Seed de Datos

Para cargar productos iniciales con datos variados para probar el ranking:

```bash
python -m app.seed
```

El seed carga **14 productos** con diferentes valores de:
- **margin_score**: 0.12 - 0.40 (bajo a alto)
- **popularity**: 0.50 - 0.95 (bajo a muy alto)
- **stock**: 5 - 300 (muy bajo a muy alto)
- **is_sponsored**: True/False (algunos patrocinados)

Esto permite probar el sistema de ranking completo que combina:
- Similarity (similitud semántica)
- Sponsored (productos patrocinados)
- Margin Score (margen de ganancia)
- Stock (disponibilidad)
- Popularity (popularidad)

### Ver Estadísticas de Productos

Después de cargar los datos, puedes ver estadísticas:

```bash
python -m app.seed_stats
```

Muestra:
- Total de productos
- Rango de margin_score, popularity, stock
- Productos patrocinados vs no patrocinados
- Top productos por popularidad y margen

## Ejemplo de Búsqueda y Ranking

### Consulta de Ejemplo

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "leche condensada",
    "limit": 5
  }'
```

### Resultados y Explicación del Ranking

Supongamos que la búsqueda retorna estos productos en orden:

#### 1. Lechera Nestlé (Posición #1)
```
Precio: $45.50
Stock: 150
Popularidad: 0.95
Margen: 0.35
Patrocinado: ✅ SÍ
Similitud semántica: 0.92
```

**Cálculo del Score de Ranking:**
```
Score = (similarity × 0.4) + (sponsored × 0.2) + (margin × 0.15) + (stock × 0.15) + (popularity × 0.1)
Score = (0.92 × 0.4) + (1.0 × 0.2) + (0.35 × 0.15) + (0.85 × 0.15) + (0.95 × 0.1)
Score = 0.368 + 0.200 + 0.053 + 0.128 + 0.095
Score = 0.844
```

**¿Por qué está primero?**
- ✅ Alta similitud semántica (0.92)
- ✅ Patrocinado (boost de 0.2)
- ✅ Alto margen (0.35)
- ✅ Alta popularidad (0.95)
- ✅ Buen stock (150 unidades)

#### 2. Lechera La Lechera (Posición #2)
```
Precio: $42.00
Stock: 200
Popularidad: 0.88
Margen: 0.32
Patrocinado: ✅ SÍ
Similitud semántica: 0.89
```

**Cálculo del Score:**
```
Score = (0.89 × 0.4) + (1.0 × 0.2) + (0.32 × 0.15) + (0.90 × 0.15) + (0.88 × 0.1)
Score = 0.356 + 0.200 + 0.048 + 0.135 + 0.088
Score = 0.827
```

**¿Por qué está segundo?**
- ✅ Patrocinado (mismo boost que #1)
- ✅ Muy alto stock (200 unidades)
- ⚠️ Similitud ligeramente menor (0.89 vs 0.92)
- ⚠️ Margen ligeramente menor (0.32 vs 0.35)

#### 3. Nido Fortificada (Posición #3)
```
Precio: $189.90
Stock: 80
Popularidad: 0.85
Margen: 0.40
Patrocinado: ❌ NO
Similitud semántica: 0.75
```

**Cálculo del Score:**
```
Score = (0.75 × 0.4) + (0.0 × 0.2) + (0.40 × 0.15) + (0.65 × 0.15) + (0.85 × 0.1)
Score = 0.300 + 0.000 + 0.060 + 0.098 + 0.085
Score = 0.543
```

**¿Por qué está tercero?**
- ✅ Muy alto margen (0.40 - el más alto)
- ✅ Buena popularidad (0.85)
- ❌ NO patrocinado (pierde 0.2 puntos)
- ⚠️ Similitud menor (0.75) - es "leche en polvo", no "condensada"
- ⚠️ Stock medio (80 unidades)

#### 4. Leche Santa Clara Entera (Posición #4)
```
Precio: $28.50
Stock: 250
Popularidad: 0.90
Margen: 0.15
Patrocinado: ❌ NO
Similitud semántica: 0.65
```

**Cálculo del Score:**
```
Score = (0.65 × 0.4) + (0.0 × 0.2) + (0.15 × 0.15) + (0.95 × 0.15) + (0.90 × 0.1)
Score = 0.260 + 0.000 + 0.023 + 0.143 + 0.090
Score = 0.516
```

**¿Por qué está cuarto?**
- ✅ Muy alto stock (250 unidades)
- ✅ Alta popularidad (0.90)
- ❌ Bajo margen (0.15)
- ❌ NO patrocinado
- ⚠️ Baja similitud (0.65) - es "entera", no "condensada"

#### 5. Lechera Carnation (Posición #5)
```
Precio: $38.50
Stock: 100
Popularidad: 0.65
Margen: 0.25
Patrocinado: ❌ NO
Similitud semántica: 0.70
```

**Cálculo del Score:**
```
Score = (0.70 × 0.4) + (0.0 × 0.2) + (0.25 × 0.15) + (0.70 × 0.15) + (0.65 × 0.1)
Score = 0.280 + 0.000 + 0.038 + 0.105 + 0.065
Score = 0.488
```

**¿Por qué está quinto?**
- ⚠️ Similitud media (0.70)
- ❌ NO patrocinado
- ⚠️ Margen medio (0.25)
- ⚠️ Popularidad baja (0.65)
- ⚠️ Stock medio (100 unidades)

### Pesos del Sistema de Ranking

El sistema combina 5 factores con estos pesos:

| Factor | Peso | Descripción |
|--------|------|-------------|
| **Similarity** | 40% | Similitud semántica de la búsqueda (0-1) |
| **Sponsored** | 20% | Boost si el producto está patrocinado (0 o 1) |
| **Margin Score** | 15% | Margen de ganancia del producto (0-1) |
| **Stock** | 15% | Disponibilidad (normalizado logarítmicamente) |
| **Popularity** | 10% | Popularidad histórica del producto (0-1) |

### Cómo Subir un Producto en el Ranking

Para mejorar la posición de un producto, puedes modificar:

#### 1. **Aumentar Similitud Semántica (40% del score)**
- Mejorar la descripción del producto
- Agregar sinónimos en los tags
- Usar términos que los usuarios buscan

**Ejemplo:**
```json
{
  "name": "Leche Condensada Premium",
  "description": "Leche condensada azucarada ideal para postres y repostería. También conocida como lechera.",
  "tags": ["leche", "condensada", "lechera", "dulce", "postre", "reposteria"]
}
```

#### 2. **Hacer el Producto Patrocinado (20% del score)**
```json
{
  "is_sponsored": true
}
```
Esto agrega **0.2 puntos** directamente al score final.

#### 3. **Aumentar el Margin Score (15% del score)**
```json
{
  "margin_score": 0.40  // Aumentar de 0.25 a 0.40
}
```
Cada 0.1 de aumento agrega **0.015 puntos** al score.

#### 4. **Aumentar el Stock (15% del score)**
```json
{
  "stock": 200  // Aumentar de 100 a 200
}
```
El stock se normaliza logarítmicamente:
- Stock 5 → score ~0.15
- Stock 100 → score ~0.70
- Stock 300 → score ~1.0

#### 5. **Aumentar la Popularidad (10% del score)**
```json
{
  "popularity": 0.90  // Aumentar de 0.65 a 0.90
}
```
Cada 0.1 de aumento agrega **0.01 puntos** al score.

### Ejemplo Práctico: Subir "Lechera Carnation" al Top 3

**Estado actual:**
- Score: 0.488 (posición #5)
- Similarity: 0.70
- Sponsored: false
- Margin: 0.25
- Stock: 100
- Popularity: 0.65

**Cambios propuestos:**

1. **Hacer patrocinado** (+0.2 puntos)
2. **Aumentar margen a 0.35** (+0.015 puntos)
3. **Aumentar popularidad a 0.80** (+0.015 puntos)
4. **Mejorar descripción para aumentar similitud a 0.85** (+0.06 puntos)

**Nuevo score:**
```
Score = (0.85 × 0.4) + (1.0 × 0.2) + (0.35 × 0.15) + (0.70 × 0.15) + (0.80 × 0.1)
Score = 0.340 + 0.200 + 0.053 + 0.105 + 0.080
Score = 0.778
```

**Resultado:** Subiría de posición #5 a posición #2 o #3, compitiendo con los productos patrocinados.

### Endpoint para Actualizar Producto

```bash
curl -X PUT http://localhost:8000/products/{product_id} \
  -H "Content-Type: application/json" \
  -d '{
    "is_sponsored": true,
    "margin_score": 0.35,
    "popularity": 0.80,
    "description": "Leche evaporada Carnation 370g. Perfecta para cocinar. También conocida como leche condensada para cocina."
  }'
```

## Estructura

```
app/
├── main.py              # Aplicación FastAPI principal
├── database.py          # Conexión a MongoDB
├── models/              # Modelos Pydantic
│   └── product.py
├── services/            # Servicios de negocio
│   ├── product_service.py
│   ├── search_service.py
│   ├── related_service.py
│   ├── vertex_ai_service.py
│   └── pubsub_service.py
└── utils/               # Utilidades
    ├── normalization.py
    └── ranking.py
```

