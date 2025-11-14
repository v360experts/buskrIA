# -*- coding: utf-8 -*-
"""
Servicio de búsqueda semántica
"""
from typing import List, Dict, Optional, Any
from bson import ObjectId

from app.database import get_database
from app.models.product import Product
from app.utils.normalization import normalize_text, expand_query
from app.utils.ranking import rank_products
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService


class SearchService:
    """Servicio para búsqueda semántica de productos"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.products
    
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Realizar búsqueda semántica de productos
        
        Args:
            query: Query de búsqueda
            category: Filtro por categoría
            brand: Filtro por marca
            min_price: Precio mínimo
            max_price: Precio máximo
            limit: Límite de resultados
            
        Returns:
            Diccionario con productos y total
        """
        # Normalizar query
        normalized_query = normalize_text(query)
        
        # Generar embedding de la query usando el servicio unificado
        query_embedding = EmbeddingService.get_embedding(normalized_query)
        
        # Preparar filtros
        filters = {}
        if category:
            filters["category"] = normalize_text(category)
        if brand:
            filters["brand"] = normalize_text(brand)
        
        # Buscar en Vector Search usando el servicio unificado
        vector_results = VectorSearchService.search_vectors(
            query_embedding=query_embedding,
            num_neighbors=limit * 2,  # Buscar más para aplicar filtros
            filters=filters if filters else None
        )
        
        # Obtener IDs de productos
        product_ids = [result["id"] for result in vector_results]
        similarity_scores = {
            result["id"]: result["similarity"]
            for result in vector_results
        }
        
        # Construir query de MongoDB
        mongo_query = {"_id": {"$in": [ObjectId(pid) for pid in product_ids]}}
        
        # Aplicar filtros adicionales
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            mongo_query["price"] = price_filter
        
        # Obtener productos de MongoDB
        product_docs = list(self.collection.find(mongo_query))
        
        # Convertir a modelos Product
        products = []
        for doc in product_docs:
            doc["_id"] = str(doc["_id"])
            product = Product(**doc)
            products.append(product)
        
        # Aplicar ranking
        ranked_products = rank_products(products, similarity_scores)
        
        # Limitar resultados
        limited_products = ranked_products[:limit]
        
        return {
            "products": limited_products,
            "total": len(limited_products)
        }

