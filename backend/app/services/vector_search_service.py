"""
Servicio abstracto para Vector Search
Soporta múltiples proveedores: Vertex AI Vector Search (GCP) y Azure AI Search
"""
import os
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class VectorSearchProvider(ABC):
    """Interfaz abstracta para proveedores de vector search"""
    
    @abstractmethod
    def upsert_vectors(self, vectors: List[Dict[str, any]]) -> bool:
        """Insertar o actualizar vectores en el índice"""
        pass
    
    @abstractmethod
    def search_vectors(
        self,
        query_embedding: List[float],
        num_neighbors: int = 20,
        filters: Optional[Dict[str, any]] = None
    ) -> List[Dict]:
        """Buscar vectores similares"""
        pass
    
    @abstractmethod
    def delete_vector(self, vector_id: str) -> bool:
        """Eliminar un vector del índice"""
        pass


class VertexAIVectorSearchProvider(VectorSearchProvider):
    """Proveedor usando Vertex AI Vector Search (GCP)"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        self.index_id = os.getenv("VECTOR_SEARCH_INDEX_ID")
        self.endpoint_id = os.getenv("VECTOR_SEARCH_ENDPOINT_ID")
        self.deployed_index_id = os.getenv("VECTOR_SEARCH_DEPLOYED_INDEX_ID")
        
        if not all([self.project_id, self.endpoint_id, self.deployed_index_id]):
            raise ValueError(
                "Vertex AI Vector Search no está completamente configurado. "
                "Requiere: GCP_PROJECT_ID, VECTOR_SEARCH_ENDPOINT_ID, VECTOR_SEARCH_DEPLOYED_INDEX_ID"
            )
        
        try:
            from google.cloud import aiplatform
            from google.cloud.aiplatform import matching_engine
            from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
            
            aiplatform.init(project=self.project_id, location=self.location)
            
            self.endpoint = MatchingEngineIndexEndpoint(
                index_endpoint_name=self.endpoint_id,
                project=self.project_id,
                location=self.location
            )
        except ImportError:
            raise ImportError("google-cloud-aiplatform no está instalado")
        except Exception as e:
            raise ValueError(f"Error inicializando Vertex AI Vector Search: {str(e)}")
    
    def upsert_vectors(self, vectors: List[Dict[str, any]]) -> bool:
        """Insertar o actualizar vectores en Vertex AI Vector Search"""
        try:
            from google.cloud.aiplatform import matching_engine
            
            datapoints = []
            for vector in vectors:
                datapoint = matching_engine.matching_engine_index_endpoint.Datapoint(
                    datapoint_id=vector["id"],
                    feature_vector=vector["embedding"],
                    restricts=vector.get("metadata", {})
                )
                datapoints.append(datapoint)
            
            self.endpoint.upsert_datapoints(datapoints=datapoints)
            return True
        except Exception as e:
            raise ValueError(f"Error upserting vectors en Vertex AI: {str(e)}")
    
    def search_vectors(
        self,
        query_embedding: List[float],
        num_neighbors: int = 20,
        filters: Optional[Dict[str, any]] = None
    ) -> List[Dict]:
        """Buscar vectores similares en Vertex AI Vector Search"""
        try:
            from google.cloud.aiplatform import matching_engine
            
            restricts = []
            if filters:
                for key, value in filters.items():
                    restricts.append(
                        matching_engine.matching_engine_index_endpoint.Namespace(
                            name=key,
                            allow_tokens=[str(value)]
                        )
                    )
            
            results = self.endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=num_neighbors,
                restricts=restricts if restricts else None
            )
            
            search_results = []
            if results and len(results) > 0:
                for neighbor in results[0]:
                    search_results.append({
                        "id": neighbor.id,
                        "distance": neighbor.distance,
                        "similarity": 1.0 - neighbor.distance
                    })
            
            return search_results
        except Exception as e:
            raise ValueError(f"Error searching vectors en Vertex AI: {str(e)}")
    
    def delete_vector(self, vector_id: str) -> bool:
        """Eliminar vector de Vertex AI Vector Search"""
        try:
            self.endpoint.remove_datapoints(datapoint_ids=[vector_id])
            return True
        except Exception as e:
            raise ValueError(f"Error deleting vector en Vertex AI: {str(e)}")


class AzureAISearchProvider(VectorSearchProvider):
    """Proveedor usando Azure AI Search"""
    
    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "products-index")
        
        if not all([self.endpoint, self.api_key]):
            raise ValueError(
                "Azure AI Search no está completamente configurado. "
                "Requiere: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY"
            )
        
        try:
            from azure.search.documents import SearchClient
            from azure.core.credentials import AzureKeyCredential
            
            self.client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.api_key)
            )
        except ImportError:
            raise ImportError(
                "azure-search-documents no está instalado. "
                "Instala con: pip install azure-search-documents"
            )
        except Exception as e:
            raise ValueError(f"Error inicializando Azure AI Search: {str(e)}")
    
    def upsert_vectors(self, vectors: List[Dict[str, any]]) -> bool:
        """Insertar o actualizar vectores en Azure AI Search"""
        try:
            documents = []
            for vector in vectors:
                doc = {
                    "id": vector["id"],
                    "contentVector": vector["embedding"],
                }
                
                # Agregar metadata
                metadata = vector.get("metadata", {})
                for key, value in metadata.items():
                    doc[key] = value
                
                documents.append(doc)
            
            # Upsert documents
            result = self.client.upload_documents(documents=documents)
            
            # Verificar que no haya errores
            failed = [r for r in result if not r.succeeded]
            if failed:
                raise ValueError(f"Error upserting {len(failed)} documentos en Azure AI Search")
            
            return True
        except Exception as e:
            raise ValueError(f"Error upserting vectors en Azure AI Search: {str(e)}")
    
    def search_vectors(
        self,
        query_embedding: List[float],
        num_neighbors: int = 20,
        filters: Optional[Dict[str, any]] = None
    ) -> List[Dict]:
        """Buscar vectores similares en Azure AI Search"""
        try:
            # Construir filtro OData
            filter_str = None
            if filters:
                filter_parts = [f"{k} eq '{v}'" for k, v in filters.items()]
                filter_str = " and ".join(filter_parts)
            
            # Realizar búsqueda vectorial
            results = self.client.search(
                search_text="*",  # Búsqueda vectorial, texto no necesario
                vector_queries=[{
                    "kind": "vector",
                    "vector": query_embedding,
                    "k_nearest_neighbors": num_neighbors,
                    "fields": "contentVector"
                }],
                filter=filter_str,
                top=num_neighbors,
                select=["id"]
            )
            
            search_results = []
            for result in results:
                # Azure AI Search retorna score, convertirlo a similarity
                score = result.get("@search.score", 0.0)
                similarity = score / 100.0 if score > 1 else score  # Normalizar si es necesario
                
                search_results.append({
                    "id": result.get("id"),
                    "distance": 1.0 - similarity,
                    "similarity": similarity
                })
            
            return search_results
        except Exception as e:
            raise ValueError(f"Error searching vectors en Azure AI Search: {str(e)}")
    
    def delete_vector(self, vector_id: str) -> bool:
        """Eliminar vector de Azure AI Search"""
        try:
            result = self.client.delete_documents(documents=[{"id": vector_id}])
            return all(r.succeeded for r in result)
        except Exception as e:
            raise ValueError(f"Error deleting vector en Azure AI Search: {str(e)}")


class VectorSearchService:
    """Servicio unificado para Vector Search con detección automática de proveedor"""
    
    _instance: Optional[VectorSearchProvider] = None
    
    @classmethod
    def get_provider(cls) -> VectorSearchProvider:
        """Obtener el proveedor de vector search configurado"""
        if cls._instance is not None:
            return cls._instance
        
        # Detectar proveedor basado en variables de entorno
        gcp_endpoint = os.getenv("VECTOR_SEARCH_ENDPOINT_ID")
        azure_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        
        if gcp_endpoint:
            print("🔵 Usando Vertex AI Vector Search (GCP)")
            cls._instance = VertexAIVectorSearchProvider()
        elif azure_endpoint:
            print("🟣 Usando Azure AI Search")
            cls._instance = AzureAISearchProvider()
        else:
            raise ValueError(
                "No se encontró proveedor de Vector Search configurado. "
                "Configura VECTOR_SEARCH_ENDPOINT_ID (GCP) o AZURE_SEARCH_ENDPOINT (Azure)"
            )
        
        return cls._instance
    
    @classmethod
    def upsert_vectors(cls, vectors: List[Dict[str, any]]) -> bool:
        """Insertar o actualizar vectores"""
        provider = cls.get_provider()
        return provider.upsert_vectors(vectors)
    
    @classmethod
    def search_vectors(
        cls,
        query_embedding: List[float],
        num_neighbors: int = 20,
        filters: Optional[Dict[str, any]] = None
    ) -> List[Dict]:
        """Buscar vectores similares"""
        provider = cls.get_provider()
        return provider.search_vectors(query_embedding, num_neighbors, filters)
    
    @classmethod
    def delete_vector(cls, vector_id: str) -> bool:
        """Eliminar un vector"""
        provider = cls.get_provider()
        return provider.delete_vector(vector_id)

