# Estructura del Proyecto

```
Buskda_IA/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # Aplicación FastAPI principal
│   │   ├── database.py        # Conexión a MongoDB
│   │   ├── seed.py            # Script de carga inicial
│   │   ├── models/            # Modelos Pydantic
│   │   │   ├── __init__.py
│   │   │   └── product.py     # Modelo de Producto
│   │   ├── services/          # Servicios de negocio
│   │   │   ├── __init__.py
│   │   │   ├── product_service.py      # CRUD de productos
│   │   │   ├── search_service.py       # Búsqueda semántica
│   │   │   ├── related_service.py      # Productos relacionados
│   │   │   ├── vertex_ai_service.py     # Integración Vertex AI
│   │   │   ├── pubsub_service.py        # Publicación en Pub/Sub
│   │   │   └── pubsub_subscriber.py     # Subscriber de Pub/Sub
│   │   └── utils/              # Utilidades
│   │       ├── __init__.py
│   │       ├── normalization.py        # Normalización de texto
│   │       └── ranking.py              # Sistema de ranking
│   ├── Dockerfile             # Docker para Cloud Run
│   ├── requirements.txt       # Dependencias Python
│   ├── env.example            # Ejemplo de variables de entorno
│   └── README.md              # Documentación del backend
│
├── frontend/                   # Frontend Next.js 14
│   ├── app/
│   │   ├── layout.tsx         # Layout principal
│   │   ├── page.tsx           # Página principal
│   │   └── globals.css        # Estilos globales
│   ├── components/            # Componentes React
│   │   ├── SearchBar.tsx      # Barra de búsqueda
│   │   ├── ProductGrid.tsx    # Grid de productos
│   │   ├── ProductCard.tsx    # Tarjeta de producto
│   │   ├── ProductCardSkeleton.tsx  # Skeleton de carga
│   │   └── StoreSelector.tsx  # Selector de sucursal
│   ├── services/
│   │   └── api.ts             # Cliente API
│   ├── types/
│   │   └── product.ts         # Tipos TypeScript
│   ├── package.json           # Dependencias Node
│   ├── tsconfig.json          # Configuración TypeScript
│   ├── tailwind.config.js     # Configuración Tailwind
│   ├── next.config.js         # Configuración Next.js
│   ├── env.example            # Ejemplo de variables de entorno
│   └── README.md              # Documentación del frontend
│
├── infrastructure/             # Infraestructura GCP
│   ├── README.md              # Guía de setup de GCP
│   ├── setup.sh               # Script de setup básico
│   ├── index-metadata.json    # Metadata del índice Vector Search
│   └── pubsub-subscriber/     # Subscriber de Pub/Sub
│       ├── Dockerfile
│       └── requirements.txt
│
├── README.md                   # README principal
├── QUICKSTART.md              # Guía de inicio rápido
├── PROJECT_STRUCTURE.md       # Este archivo
└── .gitignore                 # Archivos ignorados por Git
```

## Descripción de Componentes

### Backend

- **FastAPI**: Framework web moderno y rápido
- **MongoDB**: Base de datos NoSQL para productos
- **Vertex AI**: Embeddings y Vector Search
- **Pub/Sub**: Mensajería asíncrona para actualizaciones

### Frontend

- **Next.js 14**: Framework React con App Router
- **Tailwind CSS**: Estilos utility-first
- **TypeScript**: Tipado estático
- **Axios**: Cliente HTTP

### Infraestructura

- **Cloud Run**: Contenedores serverless
- **Vertex AI Vector Search**: Búsqueda por similitud
- **Pub/Sub**: Mensajería asíncrona
- **Artifact Registry**: Repositorio de imágenes Docker

## Flujo de Datos

1. **Creación de Producto**:
   - POST /products → MongoDB
   - Generar embedding → Vertex AI
   - Indexar vector → Vector Search
   - Publicar evento → Pub/Sub

2. **Búsqueda**:
   - POST /search → Generar embedding de query
   - Buscar en Vector Search
   - Obtener productos de MongoDB
   - Aplicar ranking
   - Retornar resultados

3. **Productos Relacionados**:
   - GET /products/{id}/related
   - Usar embedding del producto como query
   - Buscar productos similares

4. **Actualización Asíncrona**:
   - Pub/Sub recibe evento
   - Subscriber actualiza embedding
   - Vector Search se actualiza

