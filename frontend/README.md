# Frontend - Next.js 14 Supermarket Search

Frontend del sistema de búsqueda semántica de productos.

## Instalación

1. Instalar dependencias:
```bash
npm install
# o
yarn install
```

2. Configurar variables de entorno:
```bash
cp .env.example .env.local
# Editar .env.local con la URL del API
```

## Desarrollo

Ejecutar servidor de desarrollo:

```bash
npm run dev
# o
yarn dev
```

Abrir [http://localhost:3000](http://localhost:3000) en el navegador.

## Build

Crear build de producción:

```bash
npm run build
npm start
```

## Características

- 🔍 Búsqueda en tiempo real
- 🎨 UI moderna estilo supermercado
- ⚡ Skeletons de carga
- 📱 Diseño responsive
- 🏪 Selector de sucursal
- 💰 Visualización de precios
- 📦 Estado de disponibilidad

## Estructura

```
app/
├── layout.tsx          # Layout principal
├── page.tsx            # Página principal
└── globals.css         # Estilos globales

components/
├── SearchBar.tsx       # Barra de búsqueda
├── ProductGrid.tsx     # Grid de productos
├── ProductCard.tsx     # Tarjeta de producto
├── ProductCardSkeleton.tsx  # Skeleton de carga
└── StoreSelector.tsx   # Selector de sucursal

services/
└── api.ts              # Cliente API

types/
└── product.ts          # Tipos TypeScript
```

