"""
Tests de integración para verificar detección y funcionamiento multi-nube
"""
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService


def test_provider_detection():
    """Test de detección automática de proveedores"""
    print("\n" + "="*60)
    print("🔍 TEST: Detección de Proveedores Multi-Nube")
    print("="*60)
    
    # Detectar proveedor de embeddings
    gcp_project = os.getenv("GCP_PROJECT_ID")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"\n📋 Variables de entorno:")
    print(f"   GCP_PROJECT_ID: {'✅ Configurado' if gcp_project else '❌ No configurado'}")
    print(f"   OPENAI_API_KEY: {'✅ Configurado' if openai_key else '❌ No configurado'}")
    
    try:
        embedding_provider = EmbeddingService.get_provider()
        provider_name = type(embedding_provider).__name__
        print(f"\n✅ Proveedor de Embeddings detectado: {provider_name}")
        
        if "VertexAI" in provider_name:
            print("   🔵 Usando Vertex AI (GCP)")
        elif "OpenAI" in provider_name:
            print("   🟢 Usando OpenAI")
    except ValueError as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
    
    # Detectar proveedor de vector search
    gcp_endpoint = os.getenv("VECTOR_SEARCH_ENDPOINT_ID")
    azure_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    
    print(f"\n📋 Variables de Vector Search:")
    print(f"   VECTOR_SEARCH_ENDPOINT_ID: {'✅ Configurado' if gcp_endpoint else '❌ No configurado'}")
    print(f"   AZURE_SEARCH_ENDPOINT: {'✅ Configurado' if azure_endpoint else '❌ No configurado'}")
    
    try:
        vector_provider = VectorSearchService.get_provider()
        provider_name = type(vector_provider).__name__
        print(f"\n✅ Proveedor de Vector Search detectado: {provider_name}")
        
        if "VertexAI" in provider_name:
            print("   🔵 Usando Vertex AI Vector Search (GCP)")
        elif "Azure" in provider_name:
            print("   🟣 Usando Azure AI Search")
    except ValueError as e:
        print(f"\n⚠️  Vector Search no configurado: {str(e)}")
        print("   Esto es normal si solo estás probando embeddings")
        return None
    
    return True


def test_embedding_dimension():
    """Test de dimensión de embeddings"""
    print("\n" + "="*60)
    print("🔍 TEST: Dimensión de Embeddings")
    print("="*60)
    
    try:
        dimension = EmbeddingService.get_embedding_dimension()
        print(f"\n📊 Dimensión de embeddings: {dimension}")
        
        # Validar dimensión según proveedor
        embedding_provider = EmbeddingService.get_provider()
        provider_name = type(embedding_provider).__name__
        
        if "VertexAI" in provider_name:
            expected = 768
            if dimension == expected:
                print(f"✅ Dimensión correcta para Vertex AI ({expected})")
            else:
                print(f"⚠️  Dimensión inesperada. Esperada: {expected}, Obtenida: {dimension}")
        elif "OpenAI" in provider_name:
            model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            if "small" in model:
                expected = 1536
            elif "large" in model:
                expected = 3072
            else:
                expected = 1536
            
            if dimension == expected:
                print(f"✅ Dimensión correcta para OpenAI {model} ({expected})")
            else:
                print(f"⚠️  Dimensión inesperada. Esperada: {expected}, Obtenida: {dimension}")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def test_embedding_generation():
    """Test de generación de embeddings"""
    print("\n" + "="*60)
    print("🔍 TEST: Generación de Embeddings")
    print("="*60)
    
    try:
        test_text = "leche condensada para postres"
        print(f"\n📝 Texto de prueba: '{test_text}'")
        print("⏳ Generando embedding...")
        
        embedding = EmbeddingService.get_embedding(test_text)
        
        if not embedding:
            print("❌ ERROR: No se generó el embedding")
            return False
        
        dimension = EmbeddingService.get_embedding_dimension()
        
        print(f"✅ Embedding generado exitosamente!")
        print(f"📊 Dimensión: {len(embedding)} (esperada: {dimension})")
        print(f"📊 Primeros 5 valores: {embedding[:5]}")
        
        if len(embedding) == dimension:
            print("✅ Dimensión correcta")
        else:
            print(f"⚠️  Dimensión no coincide. Esperada: {dimension}, Obtenida: {len(embedding)}")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        return False


def test_batch_embeddings():
    """Test de generación de embeddings en batch"""
    print("\n" + "="*60)
    print("🔍 TEST: Embeddings en Batch")
    print("="*60)
    
    try:
        texts = [
            "leche condensada",
            "leche en polvo",
            "leche entera"
        ]
        
        print(f"\n📝 Textos de prueba: {len(texts)} textos")
        print("⏳ Generando embeddings en batch...")
        
        embeddings = EmbeddingService.get_embeddings_batch(texts)
        
        if not embeddings or len(embeddings) != len(texts):
            print(f"❌ ERROR: Se esperaban {len(texts)} embeddings, se obtuvieron {len(embeddings) if embeddings else 0}")
            return False
        
        print(f"✅ {len(embeddings)} embeddings generados exitosamente!")
        
        dimension = EmbeddingService.get_embedding_dimension()
        for i, emb in enumerate(embeddings):
            if len(emb) != dimension:
                print(f"⚠️  Embedding {i+1} tiene dimensión incorrecta: {len(emb)} (esperada: {dimension})")
                return False
        
        print("✅ Todas las dimensiones son correctas")
        return True
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   Detalle: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTS DE INTEGRACIÓN - MULTI-NUBE")
    print("="*60)
    
    results = []
    
    results.append(("Detección de Proveedores", test_provider_detection()))
    results.append(("Dimensión de Embeddings", test_embedding_dimension()))
    results.append(("Generación de Embeddings", test_embedding_generation()))
    results.append(("Embeddings en Batch", test_batch_embeddings()))
    
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

