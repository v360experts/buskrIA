"""
Cloud Run subscriber para actualizar embeddings cuando hay cambios en productos
"""
import os
import json
import base64
import asyncio
from flask import Flask, request
from app.database import get_database
from app.services.product_service import ProductService
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def run_async(coro):
    """Helper para ejecutar funciones async desde Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route('/', methods=['POST'])
def handle_message():
    """Maneja mensajes de Pub/Sub"""
    try:
        envelope = request.get_json()
        
        if not envelope:
            return 'Bad Request: no Pub/Sub message received', 400
        
        # Decodificar mensaje de Pub/Sub
        pubsub_message = envelope.get('message', {})
        
        if 'data' not in pubsub_message:
            return 'Bad Request: no data in message', 400
        
        # Decodificar datos
        data_str = base64.b64decode(pubsub_message['data']).decode('utf-8')
        data = json.loads(data_str)
        
        product_id = data.get('product_id')
        event_type = data.get('event_type')
        
        if not product_id:
            return 'Bad Request: no product_id in message', 400
        
        # Procesar actualización
        db = get_database()
        product_service = ProductService(db)
        
        if event_type in ['created', 'updated']:
            # Obtener producto (async)
            product = run_async(product_service.get_product(product_id))
            
            if product:
                # Construir documento para actualizar embedding
                product_doc = {
                    "name": product.name,
                    "description": product.description or "",
                    "brand": product.brand or "",
                    "category": product.category,
                }
                
                # Actualizar embedding (async)
                run_async(product_service._update_product_embedding(product_id, product_doc))
                print(f"Updated embedding for product {product_id}")
            else:
                print(f"Product {product_id} not found")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        return f'Internal Server Error: {str(e)}', 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

