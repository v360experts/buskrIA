#!/bin/bash

# Script de setup rápido para infraestructura GCP
# Uso: ./setup.sh PROJECT_ID REGION

set -e

PROJECT_ID=${1:-""}
REGION=${2:-"us-central1"}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID requerido"
    echo "Uso: ./setup.sh PROJECT_ID [REGION]"
    exit 1
fi

echo "🚀 Configurando infraestructura GCP..."
echo "Proyecto: $PROJECT_ID"
echo "Región: $REGION"

# Configurar proyecto
gcloud config set project $PROJECT_ID

# Activar APIs
echo "📦 Activando APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Crear Service Account
echo "👤 Creando Service Account..."
gcloud iam service-accounts create supermarket-service \
  --display-name="Supermarket Service Account" \
  --project=$PROJECT_ID || echo "Service account ya existe"

# Asignar roles
echo "🔐 Asignando roles..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user" || true

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher" || true

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:supermarket-service@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber" || true

# Crear Pub/Sub topic
echo "📡 Creando tópico de Pub/Sub..."
gcloud pubsub topics create product-updates \
  --project=$PROJECT_ID || echo "Tópico ya existe"

# Crear Artifact Registry
echo "📦 Creando Artifact Registry..."
gcloud artifacts repositories create supermarket-repo \
  --repository-format=docker \
  --location=$REGION \
  --project=$PROJECT_ID || echo "Repositorio ya existe"

echo "✅ Setup básico completado!"
echo ""
echo "Próximos pasos:"
echo "1. Crear índice de Vector Search (ver infrastructure/README.md)"
echo "2. Crear endpoint y desplegar índice"
echo "3. Configurar variables de entorno"
echo "4. Desplegar servicios en Cloud Run"

