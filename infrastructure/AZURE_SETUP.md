# Setup de Azure AI Search

Guía para configurar Azure AI Search como proveedor de Vector Search.

## Prerrequisitos

1. Cuenta de Azure activa
2. Azure CLI instalado
3. Permisos de administrador o colaborador

## Paso 1: Crear Azure AI Search Service

```bash
# Login a Azure
az login

# Crear resource group
az group create \
  --name supermarket-rg \
  --location eastus

# Crear Azure AI Search service
az search service create \
  --resource-group supermarket-rg \
  --name supermarket-search \
  --sku Basic \
  --location eastus
```

**SKUs disponibles:**
- `Free`: Para desarrollo (limitado)
- `Basic`: $75/mes, hasta 3 réplicas
- `Standard`: Desde $274/mes, escalable

## Paso 2: Crear Índice

### Opción A: Usando Azure Portal

1. Ve a tu servicio de Azure AI Search
2. Click en "Indexes" > "Create index"
3. Configura:
   - **Name**: `products-index`
   - **Key**: `id` (String, Key)
   - Agregar campos vectoriales

### Opción B: Usando API

```bash
# Obtener admin key
ADMIN_KEY=$(az search admin-key show \
  --resource-group supermarket-rg \
  --service-name supermarket-search \
  --query primaryKey -o tsv)

# Crear índice usando API
curl -X POST "https://supermarket-search.search.windows.net/indexes?api-version=2023-11-01" \
  -H "api-key: $ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d @index-definition.json
```

### Definición del Índice (index-definition.json)

```json
{
  "name": "products-index",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false
    },
    {
      "name": "contentVector",
      "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchProfile": "vector-profile"
    },
    {
      "name": "category",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "brand",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    }
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "vector-profile",
        "algorithm": "hnsw"
      }
    ],
    "algorithms": [
      {
        "name": "hnsw",
        "kind": "hnsw"
      }
    ]
  }
}
```

**Nota:** Ajusta `dimensions` según tu proveedor de embeddings:
- Vertex AI: 768
- OpenAI small: 1536
- OpenAI large: 3072

## Paso 3: Obtener Credenciales

```bash
# Obtener endpoint
ENDPOINT=$(az search service show \
  --resource-group supermarket-rg \
  --name supermarket-search \
  --query hostName -o tsv)

# Obtener admin key
ADMIN_KEY=$(az search admin-key show \
  --resource-group supermarket-rg \
  --service-name supermarket-search \
  --query primaryKey -o tsv)

# Obtener query key (para solo lectura)
QUERY_KEY=$(az search query-key list \
  --resource-group supermarket-rg \
  --service-name supermarket-search \
  --query "[0].key" -o tsv)
```

## Paso 4: Configurar Variables de Entorno

```env
# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://supermarket-search.search.windows.net
AZURE_SEARCH_API_KEY=your-admin-key-or-query-key
AZURE_SEARCH_INDEX_NAME=products-index
```

## Paso 5: Verificar Configuración

```bash
# Test de conexión
curl "https://supermarket-search.search.windows.net/indexes/products-index?api-version=2023-11-01" \
  -H "api-key: $ADMIN_KEY"
```

## Paso 6: Cargar Datos

El sistema cargará automáticamente los vectores cuando:
1. Creas un producto nuevo
2. Actualizas un producto existente
3. Ejecutas el seed

```bash
cd backend
python -m app.seed
```

## Configuración Avanzada

### Configurar CORS (si es necesario)

```bash
az search service update \
  --resource-group supermarket-rg \
  --name supermarket-search \
  --cors-allowed-origins "*"
```

### Configurar Autenticación con Managed Identity

```bash
# Crear Managed Identity
az identity create \
  --resource-group supermarket-rg \
  --name supermarket-identity

# Asignar permisos
az role assignment create \
  --assignee $(az identity show --resource-group supermarket-rg --name supermarket-identity --query principalId -o tsv) \
  --role "Search Service Contributor" \
  --scope /subscriptions/{subscription-id}/resourceGroups/supermarket-rg
```

## Monitoreo

### Ver métricas

```bash
# En Azure Portal
# Ve a tu servicio > Metrics
# Monitorea:
# - Search queries per second
# - Search latency
# - Throttled search queries
```

### Alertas

```bash
az monitor metrics alert create \
  --name "high-search-latency" \
  --resource-group supermarket-rg \
  --scopes /subscriptions/{subscription-id}/resourceGroups/supermarket-rg/providers/Microsoft.Search/searchServices/supermarket-search \
  --condition "avg SearchLatency > 200" \
  --window-size 5m
```

## Costos

### Estimación Mensual

- **Basic tier**: $75/mes base
- **Storage**: $0.25/GB/mes
- **Queries**: Incluidas en el tier

### Optimización

1. Usar tier apropiado para tu carga
2. Limpiar índices antiguos
3. Comprimir datos cuando sea posible

## Troubleshooting

### Error: "Index not found"

**Solución:** Verifica que el índice esté creado:
```bash
az search index show \
  --resource-group supermarket-rg \
  --service-name supermarket-search \
  --name products-index
```

### Error: "Authentication failed"

**Solución:** Verifica la API key:
```bash
# Regenerar key si es necesario
az search admin-key regenerate \
  --resource-group supermarket-rg \
  --service-name supermarket-search \
  --key-type primary
```

### Error: "Dimension mismatch"

**Solución:** Asegúrate de que la dimensión del índice coincida con tus embeddings:
- Verifica `dimensions` en la definición del índice
- Verifica qué proveedor de embeddings estás usando

## Recursos

- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Vector Search in Azure](https://learn.microsoft.com/azure/search/vector-search-overview)
- [Pricing](https://azure.microsoft.com/pricing/details/search/)

