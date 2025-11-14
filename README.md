# Buscador de Supermercado - La Comer Style

Sistema completo de búsqueda semántica de productos para supermercado con integración de Vertex AI, MongoDB y Next.js.

## Estructura del Proyecto

```
.
├── backend/          # FastAPI backend
├── frontend/         # Next.js 14 frontend
├── infrastructure/   # Scripts y documentación GCP
└── README.md
```

## Características

- 🔍 Búsqueda semántica con Vertex AI Embeddings
- 📊 Vector Search con filtros y ranking
- 🔄 Normalización de texto y sinónimos
- 📈 Sistema de ranking personalizado
- 🔗 Productos relacionados
- 📡 Integración con Pub/Sub para actualizaciones
- 🎨 Frontend moderno estilo supermercado

## Requisitos Previos

- Python 3.10+
- Node.js 18+
- MongoDB
- Cuenta de GCP con APIs activadas
- Credenciales de GCP configuradas

## Instalación

Ver documentación en cada directorio:
- `backend/README.md` - Setup del backend
- `frontend/README.md` - Setup del frontend
- `infrastructure/README.md` - Setup de GCP

## Inicio Rápido

1. Configurar variables de entorno (ver `.env.example`)
2. Crear índice de Vector Search en GCP
3. Ejecutar seed de productos
4. **Ejecutar tests de integración** para verificar conexiones:
   ```bash
   cd backend
   python -m tests.test_all
   ```
5. Iniciar backend y frontend

Ver `QUICKSTART.md` para instrucciones detalladas.

## Tests de Integración

Ejecuta los tests para verificar todas las conexiones:

```bash
cd backend
python -m tests.test_all
```

Ver ejemplos de salida en `backend/tests/EXAMPLE_OUTPUT.md`

## Mejoras y Optimizaciones

Cada directorio incluye un archivo `IMPROVEMENTS.md` con recomendaciones profesionales:

- **Backend**: Cache de embeddings, optimizaciones de performance, escalabilidad
- **Frontend**: Debounce, lazy loading, PWA, mejoras de UX
- **Infraestructura**: Auto-scaling, multi-region, optimización de costos, seguridad

Ver:
- `backend/IMPROVEMENTS.md` - Mejoras del backend
- `frontend/IMPROVEMENTS.md` - Mejoras del frontend
- `infrastructure/IMPROVEMENTS.md` - Mejoras de infraestructura

