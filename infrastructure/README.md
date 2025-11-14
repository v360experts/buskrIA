# Infraestructura GCP - Setup Guide

Guía completa para configurar la infraestructura en Google Cloud Platform.

## Requisitos Previos

1. Cuenta de GCP activa
2. `gcloud` CLI instalado y configurado
3. Permisos de administrador o editor en el proyecto

## Paso 1: Activar APIs Necesarias

```bash
# Configurar proyecto
export PROJECT_ID="tu-proyecto-id"
gcloud config set project $PROJECT_ID

# Activar APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## Paso 2: Crear Índice de Vector Search

### 2.1 Crear el Índice

```bash
# Configurar variables
export INDEX_ID="supermarket-products-index"
export REGION="us-central1"
export DIMENSIONS=768  # text-embedding-004 tiene 768 dimensiones

# Crear índice
gcloud ai indexes create \
  --display-name="Supermarket Products Index" \
  --metadata-file=index-metadata.json \
  --region=$REGION \
  --project=$PROJECT_ID
```

### 2.2 Archivo index-metadata.json

Crear `index-metadata.json`:

```json
{
  "contentsDeltaUri": "gs://tu-bucket/index/contents",
  "config": {
    "dimensions": 768,
    "approximateNeighborsCount": 10,
    "distanceMeasureType": "DOT_PRODUCT_DISTANCE",
    "algorithmConfig": {
      "treeAhConfig": {
        "leafNodeEmbeddingCount": 500,
        "leafNodesToSearchPercent": 10
      }
    }
  }
}
```

### 2.3 Crear Endpoint

```bash
gcloud ai index-endpoints create \
  --display-name="Supermarket Search Endpoint" \
  --region=$REGION \
  --project=$PROJECT_ID
```

### 2.4 Desplegar Índice en el Endpoint

```bash
# Obtener IDs
export INDEX_ID=$(gcloud ai indexes list --region=$REGION --format="value(name)" --filter="displayName:Supermarket Products Index" | head -1)
export ENDPOINT_ID=$(gcloud ai index-endpoints list --region=$REGION --format="value(name)" --filter="displayName:Supermarket Search Endpoint" | head -1)

# Desplegar
gcloud ai index-endpoints deploy-index $ENDPOINT_ID \
  --deployed-index-id="supermarket-index-deployment" \
  --index=$INDEX_ID \
  --display-name="Supermarket Index Deployment" \
  --min-replica-count=1 \
  --max-replica-count=1 \
  --region=$REGION \
  --project=$PROJECT_ID
```

## Paso 3: Configurar Pub/Sub

### 3.1 Crear Tópico

```bash
gcloud pubsub topics create product-updates \
  --project=$PROJECT_ID
```

### 3.2 Crear Suscripción

```bash
gcloud pubsub subscriptions create product-updates-subscription \
  --topic=product-updates \
  --project=$PROJECT_ID
```

## Paso 4: Crear Service Account

```bash
# Crear service account
gcloud iam service-accounts create supermarket-service \
  --display-name="Supermarket Service Account" \
  --project=$PROJECT_ID

# Asignar roles necesarios
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

# Crear y descargar key
gcloud iam service-accounts keys create service-account-key.json \
  --iam-account=supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com \
  --project=$PROJECT_ID
```

## Paso 5: Desplegar Backend en Cloud Run

### 5.1 Build y Push de Imagen

```bash
# Configurar Artifact Registry
gcloud artifacts repositories create supermarket-repo \
  --repository-format=docker \
  --location=$REGION \
  --project=$PROJECT_ID

# Configurar Docker
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build y push
cd backend
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/supermarket-repo/backend:latest
```

### 5.2 Desplegar Cloud Run

```bash
gcloud run deploy supermarket-backend \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/supermarket-repo/backend:latest \
  --platform managed \
  --region $REGION \
  --service-account supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com \
  --set-env-vars="MONGODB_URI=tu-mongodb-uri,MONGODB_DB_NAME=supermarket_db,GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION},VECTOR_SEARCH_INDEX_ID=${INDEX_ID},VECTOR_SEARCH_ENDPOINT_ID=${ENDPOINT_ID},VECTOR_SEARCH_DEPLOYED_INDEX_ID=supermarket-index-deployment,PUBSUB_TOPIC_PRODUCT_UPDATES=product-updates" \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10
```

## Paso 6: Desplegar Subscriber de Pub/Sub

### 6.1 Crear Cloud Run Service para Subscriber

Crear `infrastructure/pubsub-subscriber/main.py`:

```python
from flask import Flask, request
import json
import os
from google.cloud import pubsub_v1
from app.services.product_service import ProductService
from app.database import get_database

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_message():
    envelope = request.get_json()
    
    if not envelope:
        return 'Bad Request: no Pub/Sub message received', 400
    
    pubsub_message = envelope.get('message', {})
    data = json.loads(base64.b64decode(pubsub_message.get('data', '')).decode('utf-8'))
    
    product_id = data.get('product_id')
    event_type = data.get('event_type')
    
    # Procesar actualización
    db = get_database()
    product_service = ProductService(db)
    
    if event_type in ['created', 'updated']:
        product = await product_service.get_product(product_id)
        if product:
            await product_service._update_product_embedding(product_id, product.dict())
    
    return 'OK', 200
```

### 6.2 Desplegar Subscriber

```bash
cd infrastructure/pubsub-subscriber
gcloud builds submit --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/supermarket-repo/subscriber:latest

gcloud run deploy product-updates-subscriber \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/supermarket-repo/subscriber:latest \
  --platform managed \
  --region $REGION \
  --service-account supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com \
  --no-allow-unauthenticated \
  --memory=1Gi \
  --cpu=1
```

### 6.3 Crear Push Subscription

```bash
gcloud pubsub subscriptions create product-updates-push \
  --topic=product-updates \
  --push-endpoint=https://product-updates-subscriber-XXXXX-uc.a.run.app/ \
  --project=$PROJECT_ID
```

## Paso 7: Variables de Entorno

Actualizar `.env` del backend con:

```env
MONGODB_URI=tu-mongodb-uri
MONGODB_DB_NAME=supermarket_db
GCP_PROJECT_ID=tu-proyecto-id
GCP_LOCATION=us-central1
VECTOR_SEARCH_INDEX_ID=el-id-del-indice
VECTOR_SEARCH_ENDPOINT_ID=el-id-del-endpoint
VECTOR_SEARCH_DEPLOYED_INDEX_ID=supermarket-index-deployment
PUBSUB_TOPIC_PRODUCT_UPDATES=product-updates
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## Verificación

### Verificar Índice

```bash
gcloud ai indexes list --region=$REGION
```

### Verificar Endpoint

```bash
gcloud ai index-endpoints list --region=$REGION
```

### Verificar Pub/Sub

```bash
gcloud pubsub topics list
gcloud pubsub subscriptions list
```

### Verificar Cloud Run

```bash
gcloud run services list --region=$REGION
```

## Costos Estimados

- Vertex AI Vector Search: ~$0.10 por 1000 queries
- Vertex AI Embeddings: ~$0.0001 por 1000 caracteres
- Cloud Run: Pay per use
- Pub/Sub: Primeros 10GB/mes gratis

## Troubleshooting

### Error: Index not found
- Verificar que el índice esté creado y desplegado
- Verificar permisos del service account

### Error: Authentication failed
- Verificar que `GOOGLE_APPLICATION_CREDENTIALS` esté configurado
- Verificar que el service account tenga los roles correctos

### Error: Vector Search timeout
- Aumentar timeout en Cloud Run
- Verificar que el índice esté correctamente desplegado

