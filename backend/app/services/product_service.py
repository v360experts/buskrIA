"""
Servicio para gestión de productos
"""
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.database import get_database
from app.models.product import Product, ProductCreate, ProductUpdate
from app.utils.normalization import normalize_text
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService
from app.services.pubsub_service import PubSubService


class ProductService:
    """Servicio para operaciones CRUD de productos"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.products
        self.pubsub = PubSubService()
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Crear un nuevo producto"""
        # Normalizar nombre
        normalized_name = normalize_text(product_data.name)
        
        # Crear documento
        product_doc = {
            "name": product_data.name,
            "normalized_name": normalized_name,
            "brand": product_data.brand,
            "category": product_data.category,
            "description": product_data.description,
            "price": product_data.price,
            "stock": product_data.stock,
            "image_url": product_data.image_url,
            "margin_score": product_data.margin_score,
            "popularity": product_data.popularity,
            "is_sponsored": product_data.is_sponsored,
            "tags": product_data.tags,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insertar en MongoDB
        result = self.collection.insert_one(product_doc)
        product_id = str(result.inserted_id)
        
        # Generar embedding y actualizar en Vector Search
        await self._update_product_embedding(product_id, product_doc)
        
        # Publicar evento en Pub/Sub
        await self.pubsub.publish_product_update(product_id, "created")
        
        # Retornar producto creado
        return await self.get_product(product_id)
    
    async def update_product(
        self,
        product_id: str,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """Actualizar un producto existente"""
        # Construir update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if product_data.name is not None:
            update_doc["name"] = product_data.name
            update_doc["normalized_name"] = normalize_text(product_data.name)
        
        if product_data.brand is not None:
            update_doc["brand"] = product_data.brand
        
        if product_data.category is not None:
            update_doc["category"] = product_data.category
        
        if product_data.description is not None:
            update_doc["description"] = product_data.description
        
        if product_data.price is not None:
            update_doc["price"] = product_data.price
        
        if product_data.stock is not None:
            update_doc["stock"] = product_data.stock
        
        if product_data.image_url is not None:
            update_doc["image_url"] = product_data.image_url
        
        if product_data.margin_score is not None:
            update_doc["margin_score"] = product_data.margin_score
        
        if product_data.popularity is not None:
            update_doc["popularity"] = product_data.popularity
        
        if product_data.is_sponsored is not None:
            update_doc["is_sponsored"] = product_data.is_sponsored
        
        if product_data.tags is not None:
            update_doc["tags"] = product_data.tags
        
        # Actualizar en MongoDB
        result = self.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            return None
        
        # Obtener producto actualizado
        product_doc = self.collection.find_one({"_id": ObjectId(product_id)})
        
        # Actualizar embedding si cambió nombre o descripción
        if product_data.name is not None or product_data.description is not None:
            await self._update_product_embedding(product_id, product_doc)
        
        # Publicar evento en Pub/Sub
        await self.pubsub.publish_product_update(product_id, "updated")
        
        return await self.get_product(product_id)
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Obtener un producto por ID"""
        product_doc = self.collection.find_one({"_id": ObjectId(product_id)})
        
        if not product_doc:
            return None
        
        product_doc["_id"] = str(product_doc["_id"])
        return Product(**product_doc)
    
    async def _update_product_embedding(self, product_id: str, product_doc: dict):
        """Actualizar embedding del producto en Vector Search"""
        try:
            # Construir texto para embedding
            text_parts = [
                product_doc.get("name", ""),
                product_doc.get("description", ""),
                product_doc.get("brand", ""),
                product_doc.get("category", "")
            ]
            text = " ".join(filter(None, text_parts))
            
            # Generar embedding usando el servicio unificado
            embedding = EmbeddingService.get_embedding(text)
            
            # Preparar metadata
            metadata = {
                "category": product_doc.get("category", ""),
                "brand": product_doc.get("brand", ""),
            }
            
            # Upsert en Vector Search usando el servicio unificado
            VectorSearchService.upsert_vectors([{
                "id": product_id,
                "embedding": embedding,
                "metadata": metadata
            }])
        except Exception as e:
            print(f"Error updating embedding for product {product_id}: {e}")
            # No fallar la operación si falla el embedding

