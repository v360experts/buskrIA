# -*- coding: utf-8 -*-
"""
Servicio para productos relacionados
"""
from typing import List
from bson import ObjectId

from app.database import get_database
from app.models.product import Product
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService


class RelatedService:
    """Servicio para obtener productos relacionados"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.products
    
    async def get_related_products(
        self,
        product_id: str,
        limit: int = 10
    ) -> List[Product]:
        """
        Obtener productos relacionados usando embedding del producto
        
        Args:
            product_id: ID del producto
            limit: Número de productos relacionados a retornar
            
        Returns:
            Lista de productos relacionados
        """
        # Obtener producto
        product_doc = self.collection.find_one({"_id": ObjectId(product_id)})
        
        if not product_doc:
            return []
        
        # Construir texto para embedding
        text_parts = [
            product_doc.get("name", ""),
            product_doc.get("description", ""),
            product_doc.get("brand", ""),
            product_doc.get("category", "")
        ]
        text = " ".join(filter(None, text_parts))
        
        # Generar embedding del producto usando el servicio unificado
        product_embedding = EmbeddingService.get_embedding(text)
        
        # Buscar productos similares usando el servicio unificado
        vector_results = VectorSearchService.search_vectors(
            query_embedding=product_embedding,
            num_neighbors=limit + 1  # +1 porque el mismo producto aparecerá
        )
        
        # Filtrar el mismo producto y obtener IDs
        related_ids = []
        for result in vector_results:
            if result["id"] != product_id:
                related_ids.append(result["id"])
                if len(related_ids) >= limit:
                    break
        
        if not related_ids:
            return []
        
        # Obtener productos de MongoDB
        product_docs = list(
            self.collection.find({
                "_id": {"$in": [ObjectId(pid) for pid in related_ids]}
            })
        )
        
        # Convertir a modelos Product
        products = []
        for doc in product_docs:
            doc["_id"] = str(doc["_id"])
            product = Product(**doc)
            products.append(product)
        
        # TODO: Mezclar con co-view si existe (requiere tracking de co-views)
        # Por ahora, retornar productos ordenados por similitud
        
        return products

