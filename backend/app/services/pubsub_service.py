"""
Servicio para integración con Google Cloud Pub/Sub
"""
import os
import json
from typing import Dict, any
from google.cloud import pubsub_v1
from dotenv import load_dotenv

load_dotenv()


class PubSubService:
    """Servicio para publicar eventos en Pub/Sub"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.topic_name = os.getenv("PUBSUB_TOPIC_PRODUCT_UPDATES", "product-updates")
        
        self.publisher = None
        if self.project_id:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
    
    async def publish_product_update(
        self,
        product_id: str,
        event_type: str,
        metadata: Dict[str, any] = None
    ):
        """
        Publicar evento de actualización de producto
        
        Args:
            product_id: ID del producto
            event_type: Tipo de evento (created, updated, deleted)
            metadata: Metadata adicional
        """
        if not self.publisher:
            print("Pub/Sub not configured, skipping event publication")
            return
        
        try:
            message_data = {
                "product_id": product_id,
                "event_type": event_type,
                "metadata": metadata or {}
            }
            
            message_bytes = json.dumps(message_data).encode("utf-8")
            
            future = self.publisher.publish(self.topic_path, message_bytes)
            message_id = future.result()
            
            print(f"Published message {message_id} for product {product_id}")
        except Exception as e:
            print(f"Error publishing message: {e}")
            # No fallar la operación si falla Pub/Sub

