"""
Script para cargar datos iniciales (seed) de productos
Incluye productos con diferentes valores de ranking para pruebas
"""
import asyncio
from app.database import get_database
from app.services.product_service import ProductService
from app.models.product import ProductCreate


# Productos iniciales tipo supermercado
# Variados en: margin_score, popularity, stock, is_sponsored para probar ranking
INITIAL_PRODUCTS = [
    # Productos patrocinados con alto margen y popularidad
    {
        "name": "Lechera Nestlé",
        "brand": "Nestlé",
        "category": "Lácteos",
        "description": "Leche condensada azucarada Lechera Nestlé 395g. Ideal para postres y repostería.",
        "price": 45.50,
        "stock": 150,  # Alto stock
        "image_url": "https://example.com/images/lechera-nestle.jpg",
        "margin_score": 0.35,  # Alto margen
        "popularity": 0.95,  # Muy popular
        "is_sponsored": True,  # Patrocinado
        "tags": ["leche", "condensada", "dulce", "postre", "reposteria"]
    },
    {
        "name": "Lechera La Lechera",
        "brand": "La Lechera",
        "category": "Lácteos",
        "description": "Leche condensada La Lechera 395g. Tradicional y deliciosa.",
        "price": 42.00,
        "stock": 200,  # Muy alto stock
        "image_url": "https://example.com/images/lechera-la-lechera.jpg",
        "margin_score": 0.32,  # Alto margen
        "popularity": 0.88,  # Muy popular
        "is_sponsored": True,  # Patrocinado
        "tags": ["leche", "condensada", "dulce", "tradicional"]
    },
    
    # Productos con alto margen pero no patrocinados
    {
        "name": "Nido Fortificada",
        "brand": "Nestlé",
        "category": "Lácteos",
        "description": "Leche en polvo Nido Fortificada 1.8kg. Rica en calcio y vitaminas.",
        "price": 189.90,
        "stock": 80,  # Stock medio
        "image_url": "https://example.com/images/nido-fortificada.jpg",
        "margin_score": 0.40,  # Muy alto margen
        "popularity": 0.85,  # Alta popularidad
        "is_sponsored": False,  # No patrocinado
        "tags": ["leche", "polvo", "fortificada", "nutritiva", "calcio"]
    },
    {
        "name": "Nido Crecimiento",
        "brand": "Nestlé",
        "category": "Lácteos",
        "description": "Leche en polvo Nido Crecimiento 1.2kg. Especial para niños en crecimiento.",
        "price": 165.00,
        "stock": 60,  # Stock medio-bajo
        "image_url": "https://example.com/images/nido-crecimiento.jpg",
        "margin_score": 0.38,  # Alto margen
        "popularity": 0.75,  # Popularidad media-alta
        "is_sponsored": False,
        "tags": ["leche", "polvo", "crecimiento", "niños", "nutritivo"]
    },
    
    # Productos con bajo margen pero alta popularidad
    {
        "name": "Leche Santa Clara Entera",
        "brand": "Santa Clara",
        "category": "Lácteos",
        "description": "Leche entera pasteurizada Santa Clara 1L. Fresca y natural.",
        "price": 28.50,
        "stock": 250,  # Muy alto stock
        "image_url": "https://example.com/images/santa-clara-entera.jpg",
        "margin_score": 0.15,  # Bajo margen (producto básico)
        "popularity": 0.90,  # Muy popular
        "is_sponsored": False,
        "tags": ["leche", "entera", "pasteurizada", "fresca", "natural"]
    },
    {
        "name": "Leche Santa Clara Deslactosada",
        "brand": "Santa Clara",
        "category": "Lácteos",
        "description": "Leche deslactosada Santa Clara 1L. Para personas con intolerancia a la lactosa.",
        "price": 32.00,
        "stock": 120,  # Stock medio-alto
        "image_url": "https://example.com/images/santa-clara-deslactosada.jpg",
        "margin_score": 0.18,  # Margen bajo
        "popularity": 0.70,  # Popularidad media
        "is_sponsored": False,
        "tags": ["leche", "deslactosada", "sin lactosa", "intolerancia"]
    },
    
    # Productos con margen medio y popularidad variada
    {
        "name": "Lechera Carnation",
        "brand": "Carnation",
        "category": "Lácteos",
        "description": "Leche evaporada Carnation 370g. Perfecta para cocinar.",
        "price": 38.50,
        "stock": 100,  # Stock medio
        "image_url": "https://example.com/images/lechera-carnation.jpg",
        "margin_score": 0.25,  # Margen medio
        "popularity": 0.65,  # Popularidad media
        "is_sponsored": False,
        "tags": ["leche", "evaporada", "cocina", "recetas"]
    },
    {
        "name": "Nido Kinder",
        "brand": "Nestlé",
        "category": "Lácteos",
        "description": "Leche en polvo Nido Kinder 800g. Especial para niños pequeños.",
        "price": 145.00,
        "stock": 45,  # Stock bajo
        "image_url": "https://example.com/images/nido-kinder.jpg",
        "margin_score": 0.30,  # Margen medio-alto
        "popularity": 0.60,  # Popularidad media-baja
        "is_sponsored": False,
        "tags": ["leche", "polvo", "kinder", "niños", "bebes"]
    },
    
    # Productos para probar casos extremos
    {
        "name": "Leche Alpura Entera",
        "brand": "Alpura",
        "category": "Lácteos",
        "description": "Leche entera Alpura 1L. Calidad premium.",
        "price": 35.00,
        "stock": 5,  # Stock muy bajo (últimas unidades)
        "image_url": "https://example.com/images/alpura-entera.jpg",
        "margin_score": 0.20,  # Margen bajo
        "popularity": 0.55,  # Popularidad baja
        "is_sponsored": False,
        "tags": ["leche", "entera", "alpura", "premium"]
    },
    {
        "name": "Leche Lala Light",
        "brand": "Lala",
        "category": "Lácteos",
        "description": "Leche light Lala 1L. Baja en grasa.",
        "price": 30.00,
        "stock": 300,  # Stock muy alto
        "image_url": "https://example.com/images/lala-light.jpg",
        "margin_score": 0.12,  # Margen muy bajo
        "popularity": 0.50,  # Popularidad baja
        "is_sponsored": False,
        "tags": ["leche", "light", "baja grasa", "dietetica"]
    },
    {
        "name": "Leche Svelty Deslactosada",
        "brand": "Svelty",
        "category": "Lácteos",
        "description": "Leche deslactosada Svelty 1L. Sin lactosa, rica en calcio.",
        "price": 34.50,
        "stock": 180,  # Stock alto
        "image_url": "https://example.com/images/svelty-deslactosada.jpg",
        "margin_score": 0.28,  # Margen medio
        "popularity": 0.80,  # Popularidad alta
        "is_sponsored": True,  # Patrocinado
        "tags": ["leche", "deslactosada", "svelty", "calcio"]
    },
    
    # Más productos para tener mejor dataset
    {
        "name": "Leche Ultra Pasteurizada Alpura",
        "brand": "Alpura",
        "category": "Lácteos",
        "description": "Leche ultra pasteurizada Alpura 1L. Larga duración.",
        "price": 33.00,
        "stock": 95,
        "image_url": "https://example.com/images/alpura-ultra.jpg",
        "margin_score": 0.22,
        "popularity": 0.68,
        "is_sponsored": False,
        "tags": ["leche", "ultra pasteurizada", "larga duracion"]
    },
    {
        "name": "Leche Entera Lala",
        "brand": "Lala",
        "category": "Lácteos",
        "description": "Leche entera Lala 1L. Fresca y nutritiva.",
        "price": 29.50,
        "stock": 220,
        "image_url": "https://example.com/images/lala-entera.jpg",
        "margin_score": 0.16,
        "popularity": 0.82,
        "is_sponsored": False,
        "tags": ["leche", "entera", "lala", "fresca"]
    },
]


async def seed_database():
    """Cargar productos iniciales en la base de datos"""
    db = get_database()
    product_service = ProductService(db)
    
    print("\n" + "="*70)
    print("🌱 INICIANDO CARGA DE DATOS (SEED)")
    print("="*70)
    print(f"\n📦 Total de productos a cargar: {len(INITIAL_PRODUCTS)}")
    print("\n⏳ Cargando productos...\n")
    
    created_count = 0
    failed_count = 0
    
    for i, product_data in enumerate(INITIAL_PRODUCTS, 1):
        try:
            print(f"[{i}/{len(INITIAL_PRODUCTS)}] Creando: {product_data['name']}...", end=" ")
            product = ProductCreate(**product_data)
            created_product = await product_service.create_product(product)
            created_count += 1
            print(f"✅")
            print(f"    💰 Precio: ${created_product.price}")
            print(f"    📊 Stock: {created_product.stock}")
            print(f"    ⭐ Popularidad: {created_product.popularity:.2f}")
            print(f"    💵 Margen: {created_product.margin_score:.2f}")
            print(f"    {'📢 PATROCINADO' if created_product.is_sponsored else '   No patrocinado'}")
            print()
        except Exception as e:
            failed_count += 1
            print(f"❌ ERROR")
            print(f"    Detalle: {str(e)}")
            print()
    
    print("="*70)
    print("📊 RESUMEN DE CARGA")
    print("="*70)
    print(f"✅ Productos creados exitosamente: {created_count}")
    if failed_count > 0:
        print(f"❌ Productos con error: {failed_count}")
    print(f"📦 Total procesado: {len(INITIAL_PRODUCTS)}")
    print()
    
    if created_count > 0:
        print("🎉 ¡Carga completada!")
        print("\n💡 Los productos incluyen diferentes valores de:")
        print("   - margin_score (0.12 - 0.40)")
        print("   - popularity (0.50 - 0.95)")
        print("   - stock (5 - 300)")
        print("   - is_sponsored (True/False)")
        print("\n   Esto te permitirá probar el sistema de ranking completo.")
    else:
        print("⚠️  No se pudo crear ningún producto. Revisa los errores arriba.")
    
    print()


if __name__ == "__main__":
    asyncio.run(seed_database())

