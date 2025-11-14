"""
Tests de integración para MongoDB
"""
import os
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()


def test_mongodb_connection():
    """Test de conexión a MongoDB"""
    print("\n" + "="*60)
    print("🔍 TEST: Conexión a MongoDB")
    print("="*60)
    
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "supermarket_db")
        
        print(f"📋 URI: {mongodb_uri}")
        print(f"📋 Database: {db_name}")
        print("\n⏳ Intentando conectar...")
        
        # Intentar conexión con timeout corto
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Forzar conexión
        client.admin.command('ping')
        
        print("✅ Conexión exitosa a MongoDB!")
        
        # Obtener información del servidor
        server_info = client.server_info()
        print(f"📊 Versión MongoDB: {server_info.get('version', 'N/A')}")
        
        # Verificar base de datos
        db = client[db_name]
        collections = db.list_collection_names()
        print(f"📁 Colecciones existentes: {collections if collections else 'Ninguna'}")
        
        # Test de escritura
        print("\n⏳ Probando escritura...")
        test_collection = db.test_connection
        test_doc = {"test": "connection", "timestamp": "now"}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Escritura exitosa! ID: {result.inserted_id}")
        
        # Test de lectura
        print("⏳ Probando lectura...")
        found = test_collection.find_one({"_id": result.inserted_id})
        if found:
            print("✅ Lectura exitosa!")
        else:
            print("❌ Error: No se pudo leer el documento insertado")
            return False
        
        # Limpiar
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Documento de prueba eliminado")
        
        client.close()
        return True
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ ERROR: Timeout al conectar a MongoDB")
        print(f"   Detalle: {str(e)}")
        print("\n💡 Verifica que:")
        print("   - MongoDB esté corriendo")
        print("   - MONGODB_URI sea correcta")
        print("   - No haya problemas de red/firewall")
        return False
        
    except ConnectionFailure as e:
        print(f"❌ ERROR: Fallo de conexión a MongoDB")
        print(f"   Detalle: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR inesperado: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        return False


def test_mongodb_collections():
    """Test de colecciones de MongoDB"""
    print("\n" + "="*60)
    print("🔍 TEST: Colecciones de MongoDB")
    print("="*60)
    
    try:
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "supermarket_db")
        
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # Verificar colección de productos
        if "products" in db.list_collection_names():
            products_count = db.products.count_documents({})
            print(f"✅ Colección 'products' existe con {products_count} documentos")
            
            if products_count > 0:
                # Mostrar un producto de ejemplo
                sample = db.products.find_one()
                print(f"\n📦 Producto de ejemplo:")
                print(f"   ID: {sample.get('_id')}")
                print(f"   Nombre: {sample.get('name', 'N/A')}")
                print(f"   Categoría: {sample.get('category', 'N/A')}")
                print(f"   Precio: ${sample.get('price', 0)}")
        else:
            print("⚠️  Colección 'products' no existe (esto es normal si no has ejecutado el seed)")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE INTEGRACIÓN - MONGODB")
    print("="*60)
    
    results = []
    
    results.append(("Conexión MongoDB", test_mongodb_connection()))
    results.append(("Colecciones MongoDB", test_mongodb_collections()))
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 Todos los tests pasaron!")
    else:
        print("\n⚠️  Algunos tests fallaron")
    
    sys.exit(0 if all_passed else 1)

