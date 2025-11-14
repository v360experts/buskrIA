# Mejoras y Optimizaciones - Frontend

Este documento lista mejoras recomendadas para hacer el frontend más profesional, rápido y con mejor UX.

## ⚡ Optimizaciones de Performance

### 1. Cache de Búsquedas en el Cliente

**Problema actual:** Cada búsqueda hace una nueva petición, incluso para queries repetidas.

**Solución:**
```typescript
// services/cache.ts
const searchCache = new Map<string, { data: SearchResponse; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

export const getCachedSearch = (query: string): SearchResponse | null => {
  const cached = searchCache.get(query);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  return null;
};

export const setCachedSearch = (query: string, data: SearchResponse) => {
  searchCache.set(query, { data, timestamp: Date.now() });
};
```

**Uso:**
```typescript
const handleSearch = async (query: string) => {
  // Verificar cache primero
  const cached = getCachedSearch(query);
  if (cached) {
    setProducts(cached.products);
    return;
  }
  
  // Si no está en cache, hacer request
  const results = await searchProducts({ query });
  setCachedSearch(query, results);
  setProducts(results.products);
};
```

### 2. Debounce en la Búsqueda

**Problema actual:** Cada tecla presionada dispara una búsqueda.

**Solución:**
```typescript
import { useDebouncedCallback } from 'use-debounce';

const debouncedSearch = useDebouncedCallback(
  (query: string) => {
    handleSearch(query);
  },
  500 // Esperar 500ms después de que el usuario deje de escribir
);

// En el input
<input
  onChange={(e) => {
    setQuery(e.target.value);
    debouncedSearch(e.target.value);
  }}
/>
```

**Beneficios:**
- Reduce requests innecesarios
- Mejor experiencia de usuario
- Menor carga en el servidor

### 3. Virtual Scrolling para Listas Grandes

**Problema actual:** Renderizar 100+ productos puede ser lento.

**Solución:**
```typescript
import { useVirtualizer } from '@tanstack/react-virtual';

const parentRef = useRef<HTMLDivElement>(null);

const virtualizer = useVirtualizer({
  count: products.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 300, // Altura estimada de cada card
  overscan: 5,
});

// Renderizar solo los items visibles
{virtualizer.getVirtualItems().map((virtualItem) => (
  <ProductCard
    key={virtualItem.key}
    product={products[virtualItem.index]}
    style={{ height: virtualItem.size }}
  />
))}
```

### 4. Lazy Loading de Imágenes

**Problema actual:** Todas las imágenes se cargan inmediatamente.

**Solución:**
```typescript
import Image from 'next/image';

<ProductCard>
  <Image
    src={product.image_url}
    alt={product.name}
    loading="lazy"
    placeholder="blur"
    blurDataURL="data:image/jpeg;base64,..."
  />
</ProductCard>
```

### 5. Code Splitting y Lazy Loading de Componentes

**Solución:**
```typescript
import dynamic from 'next/dynamic';

const ProductGrid = dynamic(() => import('@/components/ProductGrid'), {
  loading: () => <ProductGridSkeleton />,
  ssr: false, // Si no necesitas SSR
});
```

## 🎨 Mejoras de UX

### 6. Búsqueda con Autocompletado

**Solución:**
```typescript
const [suggestions, setSuggestions] = useState<string[]>([]);

const fetchSuggestions = async (query: string) => {
  if (query.length < 2) return;
  
  const response = await fetch(`/api/suggestions?q=${query}`);
  const data = await response.json();
  setSuggestions(data.suggestions);
};

// Mostrar dropdown con sugerencias
{suggestions.length > 0 && (
  <div className="suggestions-dropdown">
    {suggestions.map((suggestion, i) => (
      <div key={i} onClick={() => handleSearch(suggestion)}>
        {suggestion}
      </div>
    ))}
  </div>
)}
```

### 7. Filtros Avanzados con UI Mejorada

**Solución:**
```typescript
const [filters, setFilters] = useState({
  category: '',
  brand: '',
  priceRange: [0, 1000],
  inStock: true,
});

// Componente de filtros
<FilterPanel>
  <CategoryFilter categories={categories} />
  <BrandFilter brands={brands} />
  <PriceRangeSlider min={0} max={1000} />
  <StockToggle />
</FilterPanel>
```

### 8. Indicadores de Carga Mejorados

**Solución:**
```typescript
// Skeleton más realista
const ProductCardSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-48 bg-gray-200 rounded" />
    <div className="mt-4 space-y-2">
      <div className="h-4 bg-gray-200 rounded w-3/4" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
    </div>
  </div>
);

// Progress bar para búsquedas largas
{loading && <ProgressBar progress={searchProgress} />}
```

### 9. Manejo de Errores con Retry

**Solución:**
```typescript
const [error, setError] = useState<Error | null>(null);
const [retryCount, setRetryCount] = useState(0);

const handleSearchWithRetry = async (query: string, retries = 3) => {
  try {
    const results = await searchProducts({ query });
    setError(null);
    setRetryCount(0);
    return results;
  } catch (err) {
    if (retries > 0) {
      setTimeout(() => {
        setRetryCount(retries - 1);
        handleSearchWithRetry(query, retries - 1);
      }, 1000 * (4 - retries)); // Backoff exponencial
    } else {
      setError(err as Error);
    }
  }
};

// UI de error con retry
{error && (
  <ErrorBanner
    message="Error al buscar productos"
    onRetry={() => handleSearchWithRetry(searchQuery)}
  />
)}
```

### 10. Optimistic Updates

**Solución:**
```typescript
// Al agregar a favoritos, mostrar inmediatamente
const handleAddToFavorites = (productId: string) => {
  // Actualizar UI inmediatamente
  setFavorites([...favorites, productId]);
  
  // Hacer request en background
  addToFavorites(productId).catch(() => {
    // Revertir si falla
    setFavorites(favorites.filter(id => id !== productId));
  });
};
```

## 🔍 Mejoras de Búsqueda

### 11. Búsqueda con Historial

**Solución:**
```typescript
const [searchHistory, setSearchHistory] = useState<string[]>([]);

useEffect(() => {
  const history = localStorage.getItem('searchHistory');
  if (history) {
    setSearchHistory(JSON.parse(history));
  }
}, []);

const saveToHistory = (query: string) => {
  const updated = [query, ...searchHistory.filter(q => q !== query)].slice(0, 10);
  setSearchHistory(updated);
  localStorage.setItem('searchHistory', JSON.stringify(updated));
};
```

### 12. Búsqueda por Voz

**Solución:**
```typescript
const [isListening, setIsListening] = useState(false);

const startVoiceSearch = () => {
  const recognition = new (window as any).webkitSpeechRecognition();
  recognition.lang = 'es-MX';
  recognition.onresult = (event: any) => {
    const query = event.results[0][0].transcript;
    handleSearch(query);
  };
  recognition.start();
  setIsListening(true);
};
```

### 13. Búsqueda con Corrección Ortográfica

**Solución:**
```typescript
// Detectar si hay pocos resultados y sugerir corrección
if (products.length < 3) {
  const corrected = await getSpellCheck(query);
  if (corrected !== query) {
    setDidYouMean(corrected);
  }
}

// Mostrar "¿Quisiste decir...?"
{didYouMean && (
  <div className="did-you-mean">
    ¿Quisiste decir <button onClick={() => handleSearch(didYouMean)}>{didYouMean}</button>?
  </div>
)}
```

## 📱 Responsive y Accesibilidad

### 14. Mejoras de Accesibilidad

**Solución:**
```typescript
// Agregar ARIA labels
<SearchBar
  aria-label="Buscar productos"
  aria-describedby="search-help"
/>

// Navegación por teclado
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    handleSearch(query);
  }
  if (e.key === 'Escape') {
    clearSearch();
  }
};

// Focus management
useEffect(() => {
  if (products.length > 0) {
    firstProductRef.current?.focus();
  }
}, [products]);
```

### 15. PWA (Progressive Web App)

**Solución:**
```typescript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
});

module.exports = withPWA({
  // config
});

// manifest.json
{
  "name": "Buscador de Supermercado",
  "short_name": "Supermarket",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#0ea5e9"
}
```

### 16. Modo Oscuro

**Solución:**
```typescript
const [theme, setTheme] = useState<'light' | 'dark'>('light');

useEffect(() => {
  const saved = localStorage.getItem('theme') as 'light' | 'dark';
  if (saved) setTheme(saved);
}, []);

// tailwind.config.js
module.exports = {
  darkMode: 'class',
  // ...
};

// Toggle
<button onClick={() => {
  const newTheme = theme === 'light' ? 'dark' : 'light';
  setTheme(newTheme);
  document.documentElement.classList.toggle('dark');
}}>
  {theme === 'light' ? '🌙' : '☀️'}
</button>
```

## 🎯 Analytics y Tracking

### 17. Tracking de Eventos

**Solución:**
```typescript
// utils/analytics.ts
export const trackEvent = (eventName: string, properties?: Record<string, any>) => {
  // Google Analytics
  if (typeof window !== 'undefined' && (window as any).gtag) {
    (window as any).gtag('event', eventName, properties);
  }
  
  // O tu propio sistema
  fetch('/api/analytics', {
    method: 'POST',
    body: JSON.stringify({ event: eventName, properties }),
  });
};

// Uso
trackEvent('search_performed', { query, results_count: products.length });
trackEvent('product_viewed', { product_id: product.id });
trackEvent('add_to_cart', { product_id: product.id });
```

### 18. Performance Monitoring

**Solución:**
```typescript
// Medir tiempo de búsqueda
const startTime = performance.now();
const results = await searchProducts({ query });
const duration = performance.now() - startTime;

trackEvent('search_performance', {
  query,
  duration_ms: duration,
  results_count: results.products.length,
});

// Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);
getFID(console.log);
getFCP(console.log);
getLCP(console.log);
getTTFB(console.log);
```

## 🔐 Seguridad

### 19. Sanitización de Input

**Solución:**
```typescript
import DOMPurify from 'isomorphic-dompurify';

const sanitizeInput = (input: string): string => {
  return DOMPurify.sanitize(input);
};

// Usar en búsquedas
const safeQuery = sanitizeInput(query);
```

### 20. Rate Limiting en el Cliente

**Solución:**
```typescript
let requestCount = 0;
let resetTime = Date.now();

const canMakeRequest = (): boolean => {
  const now = Date.now();
  if (now > resetTime) {
    requestCount = 0;
    resetTime = now + 60000; // Reset cada minuto
  }
  
  if (requestCount >= 10) { // Max 10 requests por minuto
    return false;
  }
  
  requestCount++;
  return true;
};
```

## 🧪 Testing

### 21. Tests Unitarios

**Solución:**
```typescript
// __tests__/SearchBar.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from '@/components/SearchBar';

test('calls onSearch when form is submitted', () => {
  const handleSearch = jest.fn();
  render(<SearchBar onSearch={handleSearch} />);
  
  const input = screen.getByPlaceholderText('Buscar productos...');
  fireEvent.change(input, { target: { value: 'leche' } });
  fireEvent.submit(input.closest('form')!);
  
  expect(handleSearch).toHaveBeenCalledWith('leche');
});
```

### 22. Tests E2E con Playwright

**Solución:**
```typescript
// e2e/search.spec.ts
import { test, expect } from '@playwright/test';

test('search for products', async ({ page }) => {
  await page.goto('/');
  await page.fill('input[placeholder*="Buscar"]', 'leche');
  await page.click('button[type="submit"]');
  await expect(page.locator('.product-card')).toHaveCount(20);
});
```

## 📦 Optimizaciones de Build

### 23. Bundle Analysis

**Solución:**
```bash
npm install --save-dev @next/bundle-analyzer
```

```typescript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // config
});
```

### 24. Image Optimization

**Solución:**
```typescript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};
```

## 🎯 Prioridades de Implementación

### Alta Prioridad (Impacto inmediato)
1. ✅ Debounce en búsqueda
2. ✅ Cache de búsquedas
3. ✅ Lazy loading de imágenes
4. ✅ Manejo de errores mejorado

### Media Prioridad (Mejora de UX)
5. ✅ Autocompletado
6. ✅ Filtros avanzados
7. ✅ Historial de búsqueda
8. ✅ Modo oscuro

### Baja Prioridad (Features avanzadas)
9. ✅ Búsqueda por voz
10. ✅ PWA
11. ✅ Virtual scrolling
12. ✅ Analytics completo

## 📚 Recursos

- [Next.js Optimization](https://nextjs.org/docs/app/building-your-application/optimizing)
- [React Performance](https://react.dev/learn/render-and-commit)
- [Web Vitals](https://web.dev/vitals/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

