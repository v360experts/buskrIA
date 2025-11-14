# -*- coding: utf-8 -*-
"""
Servicio para integración con Vertex AI Embeddings y Vector Search
"""
import os
from typing import List, Dict, Optional, Any
from google.cloud import aiplatform
from google.cloud.aiplatform import matching_engine
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class VertexAIService:
    """Servicio para interactuar con Vertex AI"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "us-central1")
        self.index_id = os.getenv("VECTOR_SEARCH_INDEX_ID")
        self.endpoint_id = os.getenv("VECTOR_SEARCH_ENDPOINT_ID")
        self.deployed_index_id = os.getenv("VECTOR_SEARCH_DEPLOYED_INDEX_ID")
        
        # Inicializar Vertex AI
        aiplatform.init(project=self.project_id, location=self.location)
        
        # Inicializar endpoint
        self.endpoint = None
        if self.endpoint_id:
            self.endpoint = MatchingEngineIndexEndpoint(
                index_endpoint_name=self.endpoint_id,
                project=self.project_id,
                location=self.location
            )
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Obtiene el embedding de un texto usando text-embedding-004
        
        Args:
            text: Texto a convertir en embedding
            
        Returns:
            Lista de floats representando el embedding
        """
        try:
            # Usar Vertex AI SDK para embeddings
            from vertexai.preview.language_models import TextEmbeddingModel
            
            model = TextEmbeddingModel.from_pretrained("text-embedding-004")
            embeddings = model.get_embeddings([text])
            
            if embeddings and len(embeddings) > 0:
                return embeddings[0].values
            
            raise ValueError("Empty embedding returned")
        except ImportError:
            # Fallback: usar REST API directamente
            from google.cloud import aiplatform_v1
            import base64
            import json
            
            client = aiplatform_v1.PredictionServiceClient()
            
            # Construir el nombre del endpoint
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/text-embedding-004"
            
            # Preparar instancia
            instance = {"content": text}
            
            # Crear request
            request = aiplatform_v1.PredictRequest(
                name=endpoint,
                instances=[instance]
            )
            
            # Hacer predicción
            response = client.predict(request=request)
            
            # Extraer embedding
            if response.predictions and len(response.predictions) > 0:
                prediction = response.predictions[0]
                # El formato puede variar, intentar diferentes estructuras
                if "embeddings" in prediction:
                    if "values" in prediction["embeddings"]:
                        return prediction["embeddings"]["values"]
                elif "values" in prediction:
                    return prediction["values"]
            
            raise ValueError(f"Could not extract embedding from response")
        except Exception as e:
            raise ValueError(f"Could not generate embedding for text: {text}. Error: {e}")
    
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]]
    ) -> bool:
        """
        Inserta o actualiza vectores en el índice
        
        Args:
            vectors: Lista de diccionarios con:
                - id: ID del vector
                - embedding: Lista de floats
                - metadata: Diccionario con metadata
                
        Returns:
            True si fue exitoso
        """
        if not self.endpoint:
            raise ValueError("Vector Search endpoint not configured")
        
        try:
            # Preparar datos para upsert
            datapoints = []
            for vector in vectors:
                datapoint = matching_engine.matching_engine_index_endpoint.Datapoint(
                    datapoint_id=vector["id"],
                    feature_vector=vector["embedding"],
                    restricts=vector.get("metadata", {})
                )
                datapoints.append(datapoint)
            
            # Realizar upsert
            self.endpoint.upsert_datapoints(datapoints=datapoints)
            
            return True
        except Exception as e:
            print(f"Error upserting vectors: {e}")
            raise
    
    def search_vectors(
        self,
        query_embedding: List[float],
        num_neighbors: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Busca vectores similares
        
        Args:
            query_embedding: Embedding de la query
            num_neighbors: Número de vecinos a retornar
            filters: Filtros a aplicar (category, brand, etc.)
            
        Returns:
            Lista de resultados con id, distance y metadata
        """
        if not self.endpoint:
            raise ValueError("Vector Search endpoint not configured")
        
        try:
            # Preparar filtros
            restricts = []
            if filters:
                for key, value in filters.items():
                    restricts.append(
                        matching_engine.matching_engine_index_endpoint.Namespace(
                            name=key,
                            allow_tokens=[str(value)]
                        )
                    )
            
            # Realizar búsqueda
            results = self.endpoint.find_neighbors(
                deployed_index_id=self.deployed_index_id,
                queries=[query_embedding],
                num_neighbors=num_neighbors,
                restricts=restricts if restricts else None
            )
            
            # Procesar resultados
            search_results = []
            if results and len(results) > 0:
                for neighbor in results[0]:
                    search_results.append({
                        "id": neighbor.id,
                        "distance": neighbor.distance,
                        "similarity": 1.0 - neighbor.distance  # Convertir distancia a similitud
                    })
            
            return search_results
        except Exception as e:
            print(f"Error searching vectors: {e}")
            raise

