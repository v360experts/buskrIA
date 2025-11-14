# Ejemplos de Salida de los Tests

## Test de MongoDB

```
======================================================================
🔍 TEST: Conexión a MongoDB
======================================================================
📋 URI: mongodb://localhost:27017
📋 Database: supermarket_db

⏳ Intentando conectar...
✅ Conexión exitosa a MongoDB!
📊 Versión MongoDB: 6.0.0
📁 Colecciones existentes: ['products', 'test_connection']

⏳ Probando escritura...
✅ Escritura exitosa! ID: 507f1f77bcf86cd799439011

⏳ Probando lectura...
✅ Lectura exitosa!

🧹 Documento de prueba eliminado

======================================================================
🔍 TEST: Colecciones de MongoDB
======================================================================
✅ Colección 'products' existe con 8 documentos

📦 Producto de ejemplo:
   ID: 507f1f77bcf86cd799439011
   Nombre: Lechera Nestlé
   Categoría: Lácteos
   Precio: $45.5

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================
✅ PASS - Conexión MongoDB
✅ PASS - Colecciones MongoDB

🎉 Todos los tests pasaron!
```

---

## Test de Vertex AI - Éxito

```
======================================================================
🔍 TEST: Credenciales de Vertex AI
======================================================================
📋 Project ID: mi-proyecto-gcp
📋 Location: us-central1
📋 Credentials: /path/to/service-account.json
✅ Archivo de credenciales encontrado

======================================================================
🔍 TEST: Generación de Embeddings
======================================================================
⏳ Inicializando servicio Vertex AI...

📝 Texto de prueba: 'leche condensada nestlé'
⏳ Generando embedding...

✅ Embedding generado exitosamente!
📊 Dimensión: 768
📊 Primeros 5 valores: [0.0234, -0.0156, 0.0892, 0.0045, -0.0321]
📊 Últimos 5 valores: [0.0123, -0.0089, 0.0456, -0.0234, 0.0567]
✅ Dimensión correcta (768 para text-embedding-004)
✅ Todos los valores son numéricos

======================================================================
🔍 TEST: Upsert de Vectores
======================================================================
⏳ Inicializando servicio Vertex AI...

📝 Texto de prueba: 'Producto de prueba para test'
⏳ Generando embedding...
✅ Embedding generado (dimensión: 768)

⏳ Insertando vector en el índice...
✅ Vector insertado exitosamente!
   (Nota: Puede tomar unos minutos para que esté disponible para búsqueda)

======================================================================
🔍 TEST: Vector Search
======================================================================
📋 Endpoint ID: projects/123456/locations/us-central1/indexEndpoints/789012
📋 Deployed Index ID: supermarket-index-deployment

⏳ Inicializando servicio Vertex AI...

📝 Query de prueba: 'leche en polvo'
⏳ Generando embedding de la query...
✅ Embedding generado (dimensión: 768)

⏳ Buscando vectores similares...
✅ Búsqueda exitosa! 5 resultados encontrados

📊 Resultados:
   1. ID: 507f1f77bcf86cd799439011
      Similitud: 0.9234
      Distancia: 0.0766
   2. ID: 507f1f77bcf86cd799439012
      Similitud: 0.8901
      Distancia: 0.1099
   3. ID: 507f1f77bcf86cd799439013
      Similitud: 0.8567
      Distancia: 0.1433

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================
✅ PASS - Credenciales
✅ PASS - Generación de Embeddings
✅ PASS - Upsert de Vectores
✅ PASS - Vector Search

🎉 Todos los tests pasaron!
```

---

## Test de Vertex AI - Con Errores

```
======================================================================
🔍 TEST: Credenciales de Vertex AI
======================================================================
📋 Project ID: NO CONFIGURADO
📋 Location: us-central1
📋 Credentials: NO CONFIGURADO
⚠️  ADVERTENCIA: GOOGLE_APPLICATION_CREDENTIALS no está configurado
   Intentando usar credenciales por defecto...

❌ ERROR: GCP_PROJECT_ID no está configurado

======================================================================
🔍 TEST: Generación de Embeddings
======================================================================
⏳ Inicializando servicio Vertex AI...

📝 Texto de prueba: 'leche condensada nestlé'
⏳ Generando embedding...

❌ ERROR: ValueError
   Detalle: Could not generate embedding for text: leche condensada nestlé. Error: 403 Permission denied

💡 Verifica que:
   - Las credenciales de GCP sean válidas
   - La API de Vertex AI esté activada
   - Tengas permisos para usar el modelo text-embedding-004

======================================================================
🔍 TEST: Upsert de Vectores
======================================================================
⚠️  SKIP: Vector Search no está configurado

======================================================================
🔍 TEST: Vector Search
======================================================================
📋 Endpoint ID: NO CONFIGURADO
📋 Deployed Index ID: NO CONFIGURADO
⚠️  SKIP: Vector Search no está configurado
   Configura VECTOR_SEARCH_ENDPOINT_ID y VECTOR_SEARCH_DEPLOYED_INDEX_ID

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================
❌ FAIL - Credenciales
❌ FAIL - Generación de Embeddings
⏭️  SKIP - Upsert de Vectores
⏭️  SKIP - Vector Search

⚠️  Algunos tests fallaron
```

---

## Test de Servicios - Éxito

```
======================================================================
🔍 TEST: Product Service
======================================================================
⏳ Creando producto de prueba...

✅ Producto creado! ID: 507f1f77bcf86cd799439011
   Nombre: Test Product Integration
   Precio: $99.99

⏳ Leyendo producto...
✅ Producto leído correctamente

⏳ Actualizando producto...
✅ Producto actualizado correctamente
   Nuevo precio: $149.99

======================================================================
🔍 TEST: Search Service
======================================================================
⏳ Buscando: 'leche'...

✅ Búsqueda completada!
   Productos encontrados: 5

📊 Primeros resultados:
   1. Lechera Nestlé - $45.5
   2. Nido Fortificada - $189.9
   3. Leche Santa Clara Entera - $28.5

======================================================================
🔍 TEST: Related Service
======================================================================
📦 Producto base: Lechera Nestlé
   ID: 507f1f77bcf86cd799439011

⏳ Buscando productos relacionados...
✅ Encontrados 4 productos relacionados

📊 Productos relacionados:
   1. Nido Fortificada - $189.9
   2. Leche Santa Clara Entera - $28.5
   3. Lechera La Lechera - $42.0

🧹 Producto de prueba eliminado (ID: 507f1f77bcf86cd799439011)

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================
✅ PASS - Product Service
✅ PASS - Search Service
✅ PASS - Related Service

🎉 Todos los tests pasaron!
```

---

## Test de Servicios - Con Errores

```
======================================================================
🔍 TEST: Product Service
======================================================================
⏳ Creando producto de prueba...

❌ ERROR: ConnectionFailure
   Detalle: [Errno 61] Connection refused

💡 Verifica que MongoDB esté corriendo

======================================================================
🔍 TEST: Search Service
======================================================================
⏳ Buscando: 'leche'...

❌ ERROR: ValueError
   Detalle: Vector Search endpoint not configured

💡 Configura VECTOR_SEARCH_ENDPOINT_ID

======================================================================
🔍 TEST: Related Service
======================================================================
⚠️  SKIP: No hay productos en la base de datos
   Ejecuta el seed primero: python -m app.seed

======================================================================
📊 RESUMEN DE RESULTADOS
======================================================================
❌ FAIL - Product Service
❌ FAIL - Search Service
⏭️  SKIP - Related Service

⚠️  Algunos tests fallaron
```

---

## Salida Completa de test_all.py

```
======================================================================
🧪 TESTS DE INTEGRACIÓN COMPLETOS
======================================================================

Este script ejecutará todos los tests de integración para verificar:
  - Conexión a MongoDB
  - Integración con Vertex AI (Embeddings)
  - Vector Search
  - Servicios principales

======================================================================
EJECUTANDO: MongoDB Connection
======================================================================

[Salida completa del test de MongoDB...]

======================================================================
EJECUTANDO: Vertex AI Integration
======================================================================

[Salida completa del test de Vertex AI...]

======================================================================
EJECUTANDO: Services Integration
======================================================================

[Salida completa del test de Servicios...]

======================================================================
📊 RESUMEN FINAL
======================================================================

✅ PASS - MongoDB Connection
✅ PASS - Vertex AI Integration
✅ PASS - Services Integration

Total: 3 | Pasados: 3 | Fallidos: 0

🎉 ¡Todos los tests pasaron exitosamente!
```

---

## Notas Importantes

### Estados de los Tests

- ✅ **PASS**: Test exitoso, todo funcionando correctamente
- ❌ **FAIL**: Test fallido, hay un problema que necesita atención
- ⏭️ **SKIP**: Test omitido (normal si el servicio no está configurado)

### Información Mostrada

Los tests muestran:
- **Configuración**: Variables de entorno y valores configurados
- **Proceso**: Qué está haciendo en cada paso
- **Resultados**: Datos obtenidos (IDs, dimensiones, valores, etc.)
- **Errores**: Mensajes detallados con sugerencias de solución
- **Resumen**: Estado final de cada test

### Errores Comunes y Soluciones

1. **MongoDB Connection refused**
   - Solución: Iniciar MongoDB o verificar `MONGODB_URI`

2. **GCP_PROJECT_ID no configurado**
   - Solución: Agregar a `.env`: `GCP_PROJECT_ID=tu-proyecto`

3. **Permission denied en Vertex AI**
   - Solución: Verificar credenciales y permisos del service account

4. **Vector Search no configurado**
   - Solución: Configurar índices en GCP o omitir estos tests

