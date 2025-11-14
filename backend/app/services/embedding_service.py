# -*- coding: utf-8 -*-
"""
Servicio abstracto para generación de embeddings
Soporta múltiples proveedores: Vertex AI (GCP) y OpenAI
"""
import os
from typing import List, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class EmbeddingProvider(ABC):
    """Interfaz abstracta para proveedores de embeddings"""
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Generar embedding para un texto"""
        pass
    
    @abstractmethod
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generar embeddings para múltiples textos en batch"""
        pass


class VertexAIEmbeddingProvider(EmbeddingProvider):
    """Proveedor de embeddings usando Vertex AI (GCP)"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID no está configurado")
        
        # Inicializar Vertex AI
        try:
            from google.cloud import aiplatform
            aiplatform.init(project=self.project_id, location=self.location)
        except ImportError:
            raise ImportError("vertexai no está instalado. Instala con: pip install vertexai")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generar embedding usando Vertex AI text-embedding-004"""
        try:
            from vertexai.preview.language_models import TextEmbeddingModel
            
            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings = model.get_embeddings([text])
            
            if embeddings and len(embeddings) > 0:
                return embeddings[0].values
            
            raise ValueError("Empty embedding returned from Vertex AI")
        except ImportError:
            raise ImportError("vertexai no está instalado")
        except Exception as e:
            raise ValueError(f"Error generando embedding con Vertex AI: {str(e)}")
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generar múltiples embeddings en batch"""
        try:
            from vertexai.preview.language_models import TextEmbeddingModel
            
            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings = model.get_embeddings(texts)
            
            return [emb.values for emb in embeddings if emb]
        except Exception as e:
            raise ValueError(f"Error generando embeddings batch con Vertex AI: {str(e)}")


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Proveedor de embeddings usando OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurado")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai no está instalado. Instala con: pip install openai")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generar embedding usando OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].embedding
            
            raise ValueError("Empty embedding returned from OpenAI")
        except Exception as e:
            raise ValueError(f"Error generando embedding con OpenAI: {str(e)}")
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generar múltiples embeddings en batch"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            return [item.embedding for item in response.data]
        except Exception as e:
            raise ValueError(f"Error generando embeddings batch con OpenAI: {str(e)}")


class EmbeddingService:
    """Servicio unificado para embeddings con detección automática de proveedor"""
    
    _instance: Optional[EmbeddingProvider] = None
    
    @classmethod
    def get_provider(cls) -> EmbeddingProvider:
        """Obtener el proveedor de embeddings configurado"""
        if cls._instance is not None:
            return cls._instance
        
        # Detectar proveedor basado en variables de entorno
        gcp_project = os.getenv("GCP_PROJECT_ID")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if gcp_project:
            print("🔵 Usando Vertex AI (GCP) para embeddings")
            cls._instance = VertexAIEmbeddingProvider()
        elif openai_key:
            print("🟢 Usando OpenAI para embeddings")
            cls._instance = OpenAIEmbeddingProvider()
        else:
            raise ValueError(
                "No se encontró proveedor de embeddings configurado. "
                "Configura GCP_PROJECT_ID o OPENAI_API_KEY"
            )
        
        return cls._instance
    
    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """Generar embedding usando el proveedor configurado"""
        provider = cls.get_provider()
        return provider.get_embedding(text)
    
    @classmethod
    def get_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        """Generar embeddings en batch"""
        provider = cls.get_provider()
        return provider.get_embeddings_batch(texts)
    
    @classmethod
    def get_embedding_dimension(cls) -> int:
        """Obtener la dimensión de los embeddings del proveedor actual"""
        provider = cls.get_provider()
        
        if isinstance(provider, VertexAIEmbeddingProvider):
            return 768  # text-embedding-004
        elif isinstance(provider, OpenAIEmbeddingProvider):
            model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            if "3-small" in model:
                return 1536
            elif "3-large" in model:
                return 3072
            else:
                return 1536  # Default
        else:
            return 768  # Default

