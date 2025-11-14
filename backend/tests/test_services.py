"""
Tests de integración para servicios principales
"""
import os
import sys
from bson import ObjectId
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from app.database import get_database
from app.services.product_service import ProductService
from app.services.search_service import SearchService
from app.services.related_service import RelatedService
from app.models.product import ProductCreate
import asyncio


def run_async(coro):
    """Helper para ejecutar funciones async"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def test_product_service():
    """Test del servicio de productos"""
    print("\n" + "="*60)
    print("🔍 TEST: Product Service")
    print("="*60)
    
    try:
        db = get_database()
        product_service = ProductService(db)
        
        # Crear producto de prueba
        print("⏳ Creando producto de prueba...")
        test_product = ProductCreate(
            name="Test Product Integration",
            brand="Test Brand",
            category="Test Category",
            description="Producto de prueba para tests de integración",
            price=99.99,
            stock=100,
            margin_score=0.25,
            popularity=0.5,
            is_sponsored=False,
            tags=["test", "integration"]
        )
        
        created = run_async(product_service.create_product(test_product))
        
        if not created:
            print("❌ ERROR: No se pudo crear el producto")
            return False, None
        
        print(f"✅ Producto creado! ID: {created.id}")
        print(f"   Nombre: {created.name}")
        print(f"   Precio: ${created.price}")
        
        # Leer producto
        print("\n⏳ Leyendo producto...")
        read_product = run_async(product_service.get_product(created.id))
        
        if not read_product:
            print("❌ ERROR: No se pudo leer el producto")
            return False, created.id
        
        if read_product.name != test_product.name:
            print("❌ ERROR: El nombre no coincide")
            return False, created.id
        
        print("✅ Producto leído correctamente")
        
        # Actualizar producto
        print("\n⏳ Actualizando producto...")
        from app.models.product import ProductUpdate
        update_data = ProductUpdate(price=149.99, stock=150)
        
        updated = run_async(product_service.update_product(created.id, update_data))
        
        if not updated:
            print("❌ ERROR: No se pudo actualizar el producto")
            return False, created.id
        
        if updated.price != 149.99:
            print("❌ ERROR: El precio no se actualizó correctamente")
            return False, created.id
        
        print("✅ Producto actualizado correctamente")
        print(f"   Nuevo precio: ${updated.price}")
        
        return True, created.id
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_search_service():
    """Test del servicio de búsqueda"""
    print("\n" + "="*60)
    print("🔍 TEST: Search Service")
    print("="*60)
    
    try:
        db = get_database()
        search_service = SearchService(db)
        
        # Realizar búsqueda
        query = "leche"
        print(f"⏳ Buscando: '{query}'...")
        
        results = run_async(search_service.search(
            query=query,
            limit=5
        ))
        
        if not results:
            print("❌ ERROR: No se obtuvieron resultados")
            return False
        
        products = results.get("products", [])
        total = results.get("total", 0)
        
        print(f"✅ Búsqueda completada!")
        print(f"   Productos encontrados: {total}")
        
        if len(products) > 0:
            print("\n📊 Primeros resultados:")
            for i, product in enumerate(products[:3], 1):
                print(f"   {i}. {product.name} - ${product.price}")
        else:
            print("⚠️  No se encontraron productos (puede ser normal si no hay datos)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_related_service():
    """Test del servicio de productos relacionados"""
    print("\n" + "="*60)
    print("🔍 TEST: Related Service")
    print("="*60)
    
    try:
        db = get_database()
        
        # Primero necesitamos un producto existente
        products_collection = db.products
        sample_product = products_collection.find_one()
        
        if not sample_product:
            print("⚠️  SKIP: No hay productos en la base de datos")
            print("   Ejecuta el seed primero: python -m app.seed")
            return None
        
        product_id = str(sample_product["_id"])
        print(f"📦 Producto base: {sample_product.get('name', 'N/A')}")
        print(f"   ID: {product_id}")
        
        related_service = RelatedService(db)
        
        print("⏳ Buscando productos relacionados...")
        related = run_async(related_service.get_related_products(product_id, limit=5))
        
        if not related:
            print("⚠️  No se encontraron productos relacionados")
            print("   (Esto puede ser normal si hay pocos productos)")
            return None
        
        print(f"✅ Encontrados {len(related)} productos relacionados")
        
        print("\n📊 Productos relacionados:")
        for i, product in enumerate(related[:3], 1):
            print(f"   {i}. {product.name} - ${product.price}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_product(product_id):
    """Limpiar producto de prueba"""
    if not product_id:
        return
    
    try:
        db = get_database()
        products_collection = db.products
        result = products_collection.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count > 0:
            print(f"\n🧹 Producto de prueba eliminado (ID: {product_id})")
    except Exception as e:
        print(f"\n⚠️  No se pudo eliminar el producto de prueba: {e}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE INTEGRACIÓN - SERVICIOS")
    print("="*60)
    
    results = []
    test_product_id = None
    
    try:
        # Test de producto
        product_result, test_product_id = test_product_service()
        results.append(("Product Service", product_result))
        
        # Test de búsqueda
        search_result = test_search_service()
        results.append(("Search Service", search_result))
        
        # Test de relacionados
        related_result = test_related_service()
        if related_result is not None:
            results.append(("Related Service", related_result))
        
    finally:
        # Limpiar producto de prueba
        if test_product_id:
            cleanup_test_product(test_product_id)
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    for test_name, result in results:
        if result is None:
            status = "⏭️  SKIP"
        elif result:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        print(f"{status} - {test_name}")
    
    executed_tests = [r for _, r in results if r is not None]
    all_passed = all(executed_tests) if executed_tests else False
    
    if all_passed:
        print("\n🎉 Todos los tests pasaron!")
    else:
        print("\n⚠️  Algunos tests fallaron")
    
    sys.exit(0 if all_passed else 1)

