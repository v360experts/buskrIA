# Mejoras y Optimizaciones - Infraestructura

Este documento lista mejoras recomendadas para hacer la infraestructura más robusta, escalable y costo-eficiente.

## 🚀 Escalabilidad

### 1. Auto-scaling para Cloud Run

**Problema actual:** Instancias fijas pueden no ser suficientes en picos.

**Solución:**
```bash
gcloud run services update supermarket-backend \
  --min-instances=1 \
  --max-instances=10 \
  --cpu-throttling \
  --concurrency=80 \
  --cpu=2 \
  --memory=2Gi
```

**Configuración recomendada:**
- Min instances: 1 (para mantener warm)
- Max instances: 10-20 (según tráfico)
- Concurrency: 80 requests por instancia
- CPU: 2 cores para mejor performance

### 2. Load Balancer con Múltiples Regiones

**Solución:**
```bash
# Crear servicios en múltiples regiones
gcloud run deploy supermarket-backend-us \
  --region=us-central1

gcloud run deploy supermarket-backend-eu \
  --region=europe-west1

# Configurar Load Balancer
gcloud compute backend-services create supermarket-backend-service \
  --global

# Agregar backends
gcloud compute backend-services add-backend supermarket-backend-service \
  --global \
  --network-endpoint-group=neg-us \
  --network-endpoint-group-region=us-central1
```

**Beneficios:**
- Menor latencia global
- Alta disponibilidad
- Distribución de carga

### 3. CDN para Assets Estáticos

**Solución:**
```bash
# Usar Cloud Storage + CDN
gsutil mb gs://supermarket-assets
gsutil -m rsync -r ./assets gs://supermarket-assets/
gsutil web set -m index.html -e 404.html gs://supermarket-assets/

# Configurar CDN
gcloud compute backend-buckets create supermarket-cdn \
  --gcs-bucket-name=supermarket-assets
```

## 💰 Optimización de Costos

### 4. Reserved Capacity para Vertex AI

**Problema actual:** Pay-per-use puede ser caro con alto tráfico.

**Solución:**
```bash
# Evaluar uso mensual
# Si > $500/mes, considerar committed use discounts
gcloud alpha ai commitments create \
  --region=us-central1 \
  --display-name="Vector Search Commitment" \
  --plan=ANNUAL \
  --resources=min-nodes=1,max-nodes=5
```

**Ahorro estimado:** 20-30% en costos de Vertex AI

### 5. Lifecycle Policies para Cloud Storage

**Solución:**
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365}
      }
    ]
  }
}
```

### 6. Scheduled Scaling

**Solución:**
```bash
# Reducir instancias en horas de bajo tráfico
gcloud scheduler jobs create http scale-down \
  --schedule="0 2 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT/services/supermarket-backend" \
  --http-method=PATCH \
  --headers="Authorization=Bearer $(gcloud auth print-access-token)" \
  --body='{"spec":{"template":{"spec":{"minInstances":1}}}}'
```

## 🔒 Seguridad

### 7. VPC para Aislamiento

**Solución:**
```bash
# Crear VPC
gcloud compute networks create supermarket-vpc \
  --subnet-mode=custom

# Crear subnets
gcloud compute networks subnets create backend-subnet \
  --network=supermarket-vpc \
  --range=10.0.1.0/24 \
  --region=us-central1

# Conectar Cloud Run a VPC
gcloud run services update supermarket-backend \
  --vpc-connector=supermarket-connector \
  --vpc-egress=private-ranges-only
```

### 8. Secret Manager para Credenciales

**Problema actual:** Credenciales en variables de entorno.

**Solución:**
```bash
# Crear secretos
echo -n "mongodb-connection-string" | gcloud secrets create mongodb-uri --data-file=-
echo -n "service-account-key" | gcloud secrets create gcp-credentials --data-file=-

# Usar en Cloud Run
gcloud run services update supermarket-backend \
  --update-secrets=MONGODB_URI=mongodb-uri:latest,GCP_CREDENTIALS=gcp-credentials:latest
```

**Beneficios:**
- Rotación automática
- Auditoría de acceso
- Encriptación en reposo

### 9. WAF (Web Application Firewall)

**Solución:**
```bash
# Configurar Cloud Armor
gcloud compute security-policies create supermarket-waf \
  --description="WAF for supermarket API"

# Reglas básicas
gcloud compute security-policies rules create 1000 \
  --security-policy=supermarket-waf \
  --expression="origin.region_code == 'RU'" \
  --action=deny-403

# Aplicar a Load Balancer
gcloud compute backend-services update supermarket-backend-service \
  --security-policy=supermarket-waf
```

### 10. DDoS Protection

**Solución:**
```bash
# Cloud Armor con rate limiting
gcloud compute security-policies rules create 2000 \
  --security-policy=supermarket-waf \
  --expression="true" \
  --action=rate-based-ban \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=300
```

## 📊 Monitoreo y Observabilidad

### 11. Cloud Monitoring Dashboard

**Solución:**
```bash
# Crear dashboard personalizado
gcloud monitoring dashboards create \
  --config-from-file=dashboard.json
```

**Métricas clave a monitorear:**
- Latencia de búsquedas (p50, p95, p99)
- Tasa de errores
- Uso de CPU/Memoria
- Costos de Vertex AI
- Throughput de requests

### 12. Alertas Proactivas

**Solución:**
```bash
# Alerta de alta latencia
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Search Latency" \
  --condition-threshold-value=2000 \
  --condition-threshold-duration=300s \
  --condition-aggregations=ALIGN_MEAN,ALIGNER_RATE,REDUCE_MEAN
```

**Alertas recomendadas:**
- Latencia > 2s por más de 5 minutos
- Error rate > 5%
- CPU > 80% por más de 10 minutos
- Costos diarios > umbral
- Vector Search errors

### 13. Distributed Tracing

**Solución:**
```python
# Agregar OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
processor = BatchSpanProcessor(CloudTraceSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# En los servicios
with tracer.start_as_current_span("search_products"):
    # código de búsqueda
    pass
```

## 🔄 Alta Disponibilidad

### 14. Multi-Region Deployment

**Solución:**
```bash
# Desplegar en múltiples regiones
REGIONS=("us-central1" "us-east1" "europe-west1")

for region in "${REGIONS[@]}"; do
  gcloud run deploy supermarket-backend-${region} \
    --region=${region} \
    --image=${IMAGE} \
    --platform=managed
done
```

### 15. Database Replication

**Solución:**
```bash
# MongoDB Atlas con replicas
# O Cloud SQL con read replicas
gcloud sql instances create supermarket-db-replica \
  --master-instance-name=supermarket-db \
  --tier=db-n1-standard-2 \
  --region=us-east1
```

### 16. Backup Automático

**Solución:**
```bash
# Cloud SQL automated backups
gcloud sql instances patch supermarket-db \
  --backup-start-time=02:00 \
  --enable-bin-log

# MongoDB backups
# Configurar en MongoDB Atlas o usar mongodump
0 2 * * * mongodump --uri="$MONGODB_URI" --out=/backups/$(date +\%Y-\%m-\%d)
```

## 🚦 CI/CD Mejorado

### 17. Pipeline de CI/CD Completo

**Solución:**
```yaml
# cloudbuild.yaml
steps:
  # Tests
  - name: 'python:3.10'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        python -m pytest tests/
        python -m tests.test_all
  
  # Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/backend:$SHORT_SHA', '.']
  
  # Security scan
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['container', 'images', 'scan', 'gcr.io/$PROJECT_ID/backend:$SHORT_SHA']
  
  # Deploy
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'supermarket-backend'
      - '--image=gcr.io/$PROJECT_ID/backend:$SHORT_SHA'
      - '--region=us-central1'
```

### 18. Blue-Green Deployment

**Solución:**
```bash
# Deploy a nueva versión sin downtime
gcloud run services update-traffic supermarket-backend \
  --to-revisions=backend-v2=10 \
  --region=us-central1

# Gradual rollout
for percent in 10 25 50 75 100; do
  gcloud run services update-traffic supermarket-backend \
    --to-revisions=backend-v2=$percent
  sleep 300  # Esperar 5 minutos entre incrementos
done
```

## 📈 Performance

### 19. Redis Cluster para Cache Distribuido

**Solución:**
```bash
# Crear Redis instance
gcloud redis instances create supermarket-cache \
  --size=1 \
  --region=us-central1 \
  --tier=standard \
  --redis-version=redis_6_x

# Conectar desde Cloud Run
gcloud run services update supermarket-backend \
  --add-vpc-connector=supermarket-connector \
  --vpc-egress=private-ranges-only
```

### 20. Connection Pooling Optimizado

**Solución:**
```python
# Configurar pools más grandes
MONGO_POOL_SIZE = 50
MONGO_MAX_IDLE_TIME = 45000

client = MongoClient(
    uri,
    maxPoolSize=MONGO_POOL_SIZE,
    minPoolSize=10,
    maxIdleTimeMS=MONGO_MAX_IDLE_TIME
)
```

## 🔍 Optimización de Vertex AI

### 21. Batch Processing para Embeddings

**Solución:**
```python
# Procesar embeddings en batch durante horas de bajo tráfico
def batch_update_embeddings():
    products = get_all_products()
    texts = [build_product_text(p) for p in products]
    
    # Generar embeddings en batch (más eficiente)
    embeddings = model.get_embeddings(texts)
    
    # Upsert en batch
    vectors = [{
        "id": p.id,
        "embedding": emb.values,
        "metadata": {...}
    } for p, emb in zip(products, embeddings)]
    
    vertex_ai.upsert_vectors(vectors)
```

### 22. Compresión de Embeddings

**Solución:**
```python
# Reducir dimensión de 768 a 512 usando PCA
from sklearn.decomposition import PCA
import numpy as np

pca = PCA(n_components=512)
# Entrenar con embeddings existentes
pca.fit(existing_embeddings)
# Comprimir nuevos embeddings
compressed = pca.transform(new_embeddings)
```

**Ahorro:** ~33% en almacenamiento y búsqueda

## 🎯 Prioridades de Implementación

### Alta Prioridad (Impacto inmediato)
1. ✅ Auto-scaling en Cloud Run
2. ✅ Secret Manager para credenciales
3. ✅ Monitoring dashboard
4. ✅ Alertas proactivas

### Media Prioridad (Mejora de calidad)
5. ✅ VPC para aislamiento
6. ✅ Backup automático
7. ✅ CI/CD pipeline
8. ✅ Redis para cache

### Baja Prioridad (Optimizaciones avanzadas)
9. ✅ Multi-region deployment
10. ✅ WAF y DDoS protection
11. ✅ Distributed tracing
12. ✅ Blue-green deployment

## 💡 Mejores Prácticas

### Costos
- Usar committed use discounts para Vertex AI
- Lifecycle policies para storage
- Scheduled scaling para reducir costos en horas bajas
- Monitorear costos diariamente

### Seguridad
- Rotar credenciales regularmente
- Usar Secret Manager
- Implementar WAF
- Auditar accesos regularmente

### Performance
- Cache agresivo (Redis)
- Connection pooling
- Batch processing cuando sea posible
- Monitorear latencia constantemente

### Disponibilidad
- Multi-region deployment
- Health checks robustos
- Circuit breakers
- Graceful degradation

## 📚 Recursos

- [GCP Best Practices](https://cloud.google.com/docs/enterprise/best-practices)
- [Cloud Run Optimization](https://cloud.google.com/run/docs/tips)
- [Vertex AI Cost Optimization](https://cloud.google.com/vertex-ai/pricing)
- [Security Best Practices](https://cloud.google.com/security/best-practices)

