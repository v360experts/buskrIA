"""
Tests de integración para Vertex AI (Embeddings y Vector Search)
"""
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from app.services.vertex_ai_service import VertexAIService


def test_vertex_ai_credentials():
    """Test de credenciales de GCP"""
    print("\n" + "="*60)
    print("🔍 TEST: Credenciales de Vertex AI")
    print("="*60)
    
    try:
        project_id = os.getenv("GCP_PROJECT_ID")
        location = os.getenv("GCP_LOCATION", "us-central1")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        print(f"📋 Project ID: {project_id or 'NO CONFIGURADO'}")
        print(f"📋 Location: {location}")
        print(f"📋 Credentials: {credentials_path or 'NO CONFIGURADO'}")
        
        if not project_id:
            print("❌ ERROR: GCP_PROJECT_ID no está configurado")
            return False
        
        if not credentials_path:
            print("⚠️  ADVERTENCIA: GOOGLE_APPLICATION_CREDENTIALS no está configurado")
            print("   Intentando usar credenciales por defecto...")
        else:
            if not os.path.exists(credentials_path):
                print(f"❌ ERROR: Archivo de credenciales no existe: {credentials_path}")
                return False
            else:
                print(f"✅ Archivo de credenciales encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def test_vertex_ai_embedding():
    """Test de generación de embeddings"""
    print("\n" + "="*60)
    print("🔍 TEST: Generación de Embeddings")
    print("="*60)
    
    try:
        print("⏳ Inicializando servicio Vertex AI...")
        vertex_ai = VertexAIService()
        
        test_text = "leche condensada nestlé"
        print(f"\n📝 Texto de prueba: '{test_text}'")
        print("⏳ Generando embedding...")
        
        embedding = vertex_ai.get_embedding(test_text)
        
        if not embedding:
            print("❌ ERROR: No se generó el embedding")
            return False
        
        print(f"✅ Embedding generado exitosamente!")
        print(f"📊 Dimensión: {len(embedding)}")
        print(f"📊 Primeros 5 valores: {embedding[:5]}")
        print(f"📊 Últimos 5 valores: {embedding[-5:]}")
        
        # Validar que es un embedding válido
        if len(embedding) != 768:
            print(f"⚠️  ADVERTENCIA: Dimensión esperada 768, obtenida {len(embedding)}")
        else:
            print("✅ Dimensión correcta (768 para text-embedding-004)")
        
        # Validar que los valores son floats
        if all(isinstance(x, (int, float)) for x in embedding):
            print("✅ Todos los valores son numéricos")
        else:
            print("❌ ERROR: Algunos valores no son numéricos")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ ERROR: No se pudo importar Vertex AI SDK")
        print(f"   Detalle: {str(e)}")
        print("\n💡 Instala las dependencias: pip install vertexai")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        print("\n💡 Verifica que:")
        print("   - Las credenciales de GCP sean válidas")
        print("   - La API de Vertex AI esté activada")
        print("   - Tengas permisos para usar el modelo text-embedding-004")
        return False


def test_vertex_ai_vector_search():
    """Test de Vector Search"""
    print("\n" + "="*60)
    print("🔍 TEST: Vector Search")
    print("="*60)
    
    try:
        endpoint_id = os.getenv("VECTOR_SEARCH_ENDPOINT_ID")
        deployed_index_id = os.getenv("VECTOR_SEARCH_DEPLOYED_INDEX_ID")
        
        print(f"📋 Endpoint ID: {endpoint_id or 'NO CONFIGURADO'}")
        print(f"📋 Deployed Index ID: {deployed_index_id or 'NO CONFIGURADO'}")
        
        if not endpoint_id or not deployed_index_id:
            print("⚠️  SKIP: Vector Search no está configurado")
            print("   Configura VECTOR_SEARCH_ENDPOINT_ID y VECTOR_SEARCH_DEPLOYED_INDEX_ID")
            return None  # Skip, no es un error
        
        print("⏳ Inicializando servicio Vertex AI...")
        vertex_ai = VertexAIService()
        
        if not vertex_ai.endpoint:
            print("❌ ERROR: No se pudo inicializar el endpoint")
            return False
        
        # Generar embedding de prueba
        test_query = "leche en polvo"
        print(f"\n📝 Query de prueba: '{test_query}'")
        print("⏳ Generando embedding de la query...")
        
        query_embedding = vertex_ai.get_embedding(test_query)
        print(f"✅ Embedding generado (dimensión: {len(query_embedding)})")
        
        # Buscar vectores similares
        print("⏳ Buscando vectores similares...")
        results = vertex_ai.search_vectors(
            query_embedding=query_embedding,
            num_neighbors=5
        )
        
        if results is None:
            print("❌ ERROR: No se obtuvieron resultados")
            return False
        
        print(f"✅ Búsqueda exitosa! {len(results)} resultados encontrados")
        
        if len(results) > 0:
            print("\n📊 Resultados:")
            for i, result in enumerate(results[:3], 1):
                print(f"   {i}. ID: {result.get('id', 'N/A')}")
                print(f"      Similitud: {result.get('similarity', 0):.4f}")
                print(f"      Distancia: {result.get('distance', 0):.4f}")
        else:
            print("⚠️  No se encontraron resultados (el índice puede estar vacío)")
        
        return True
        
    except ValueError as e:
        if "not configured" in str(e):
            print("⚠️  SKIP: Vector Search no está configurado")
            return None
        print(f"❌ ERROR: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        print("\n💡 Verifica que:")
        print("   - El índice esté creado y desplegado")
        print("   - El endpoint esté activo")
        print("   - Tengas permisos para acceder al Vector Search")
        return False


def test_vertex_ai_upsert():
    """Test de upsert de vectores"""
    print("\n" + "="*60)
    print("🔍 TEST: Upsert de Vectores")
    print("="*60)
    
    try:
        endpoint_id = os.getenv("VECTOR_SEARCH_ENDPOINT_ID")
        
        if not endpoint_id:
            print("⚠️  SKIP: Vector Search no está configurado")
            return None
        
        print("⏳ Inicializando servicio Vertex AI...")
        vertex_ai = VertexAIService()
        
        # Generar embedding de prueba
        test_text = "Producto de prueba para test"
        print(f"\n📝 Texto de prueba: '{test_text}'")
        print("⏳ Generando embedding...")
        
        embedding = vertex_ai.get_embedding(test_text)
        print(f"✅ Embedding generado (dimensión: {len(embedding)})")
        
        # Preparar vector de prueba
        test_vector = {
            "id": "test-product-123",
            "embedding": embedding,
            "metadata": {
                "category": "test",
                "brand": "test-brand"
            }
        }
        
        print("⏳ Insertando vector en el índice...")
        result = vertex_ai.upsert_vectors([test_vector])
        
        if result:
            print("✅ Vector insertado exitosamente!")
            print("   (Nota: Puede tomar unos minutos para que esté disponible para búsqueda)")
        else:
            print("❌ ERROR: No se pudo insertar el vector")
            return False
        
        return True
        
    except ValueError as e:
        if "not configured" in str(e):
            print("⚠️  SKIP: Vector Search no está configurado")
            return None
        print(f"❌ ERROR: {str(e)}")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE INTEGRACIÓN - VERTEX AI")
    print("="*60)
    
    results = []
    
    results.append(("Credenciales", test_vertex_ai_credentials()))
    results.append(("Generación de Embeddings", test_vertex_ai_embedding()))
    
    upsert_result = test_vertex_ai_upsert()
    if upsert_result is not None:
        results.append(("Upsert de Vectores", upsert_result))
    
    search_result = test_vertex_ai_vector_search()
    if search_result is not None:
        results.append(("Vector Search", search_result))
    
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
    
    # Solo contar los tests que no fueron skipped
    executed_tests = [r for _, r in results if r is not None]
    all_passed = all(executed_tests) if executed_tests else False
    
    if all_passed:
        print("\n🎉 Todos los tests pasaron!")
    else:
        print("\n⚠️  Algunos tests fallaron")
    
    sys.exit(0 if all_passed else 1)

