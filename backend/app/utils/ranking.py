"""
Módulo de ranking para ordenar resultados de búsqueda
"""
from typing import List, Dict
from app.models.product import Product


def calculate_ranking_score(product: Product, similarity_score: float = 0.0) -> float:
    """
    Calcula el score de ranking combinando múltiples factores
    
    Args:
        product: Producto a rankear
        similarity_score: Score de similitud semántica (0-1)
        
    Returns:
        Score final de ranking
    """
    # Pesos para cada factor
    WEIGHT_SIMILARITY = 0.4
    WEIGHT_SPONSORED = 0.2
    WEIGHT_MARGIN = 0.15
    WEIGHT_STOCK = 0.15
    WEIGHT_POPULARITY = 0.1
    
    # Score de similitud (ya viene normalizado)
    similarity = similarity_score
    
    # Score de patrocinado (boost si está patrocinado)
    sponsored = 1.0 if product.is_sponsored else 0.0
    
    # Score de margen (normalizado 0-1)
    margin = product.margin_score
    
    # Score de stock (normalizado: más stock = mejor)
    # Usar función logarítmica para suavizar
    import math
    stock_score = min(1.0, math.log(product.stock + 1) / math.log(100)) if product.stock > 0 else 0.0
    
    # Score de popularidad (ya viene normalizado 0-1)
    popularity = product.popularity
    
    # Calcular score final
    final_score = (
        similarity * WEIGHT_SIMILARITY +
        sponsored * WEIGHT_SPONSORED +
        margin * WEIGHT_MARGIN +
        stock_score * WEIGHT_STOCK +
        popularity * WEIGHT_POPULARITY
    )
    
    return final_score


def rank_products(
    products: List[Product],
    similarity_scores: Dict[str, float]
) -> List[Product]:
    """
    Reordena productos según el score de ranking
    
    Args:
        products: Lista de productos
        similarity_scores: Diccionario de product_id -> similarity_score
        
    Returns:
        Lista de productos ordenada por ranking
    """
    # Calcular scores para cada producto
    scored_products = []
    
    for product in products:
        similarity = similarity_scores.get(product.id, 0.0)
        ranking_score = calculate_ranking_score(product, similarity)
        
        scored_products.append({
            "product": product,
            "ranking_score": ranking_score,
            "similarity": similarity
        })
    
    # Ordenar por ranking score (descendente)
    scored_products.sort(key=lambda x: x["ranking_score"], reverse=True)
    
    # Retornar solo los productos ordenados
    return [item["product"] for item in scored_products]

