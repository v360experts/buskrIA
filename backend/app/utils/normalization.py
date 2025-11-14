"""
Módulo de normalización de texto para búsquedas
"""
from unidecode import unidecode
from typing import Dict, List


# Diccionario de sinónimos
SYNONYMS: Dict[str, List[str]] = {
    "picanha": ["picaña", "picana", "picanha"],
    "picaña": ["picanha", "picana", "picaña"],
    "picana": ["picanha", "picaña", "picana"],
    "leche": ["lacteo", "lácteo"],
    "lacteo": ["leche", "lácteo"],
    "lácteo": ["leche", "lacteo"],
    "azucar": ["azúcar", "endulzante"],
    "azúcar": ["azucar", "endulzante"],
    "endulzante": ["azucar", "azúcar"],
    "aceite": ["grasa", "manteca"],
    "grasa": ["aceite", "manteca"],
    "manteca": ["aceite", "grasa"],
}


def normalize_text(text: str) -> str:
    """
    Normaliza texto: lowercase, sin acentos, sin caracteres especiales
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not text:
        return ""
    
    # Convertir a lowercase
    text = text.lower()
    
    # Remover acentos
    text = unidecode(text)
    
    # Remover caracteres especiales (mantener letras, números y espacios)
    text = "".join(c if c.isalnum() or c.isspace() else " " for c in text)
    
    # Normalizar espacios múltiples
    text = " ".join(text.split())
    
    return text.strip()


def apply_synonyms(text: str) -> List[str]:
    """
    Aplica sinónimos al texto y retorna lista de variantes
    
    Args:
        text: Texto a expandir
        
    Returns:
        Lista de variantes del texto con sinónimos aplicados
    """
    normalized = normalize_text(text)
    words = normalized.split()
    
    variants = [normalized]  # Incluir la versión original
    
    # Expandir cada palabra con sus sinónimos
    for word in words:
        if word in SYNONYMS:
            for synonym in SYNONYMS[word]:
                variant = normalized.replace(word, synonym)
                if variant not in variants:
                    variants.append(variant)
    
    return variants


def expand_query(query: str) -> List[str]:
    """
    Expande una query de búsqueda aplicando normalización y sinónimos
    
    Args:
        query: Query original
        
    Returns:
        Lista de queries expandidas
    """
    if not query:
        return [""]
    
    # Normalizar
    normalized = normalize_text(query)
    
    # Aplicar sinónimos
    variants = apply_synonyms(normalized)
    
    # Asegurar que la query original esté incluida
    if normalized not in variants:
        variants.insert(0, normalized)
    
    return variants


def get_search_terms(query: str) -> List[str]:
    """
    Obtiene términos de búsqueda expandidos de una query
    
    Args:
        query: Query de búsqueda
        
    Returns:
        Lista de términos normalizados y expandidos
    """
    expanded = expand_query(query)
    terms = set()
    
    for variant in expanded:
        terms.add(variant)
        # También agregar palabras individuales
        for word in variant.split():
            if len(word) > 2:  # Ignorar palabras muy cortas
                terms.add(word)
    
    return list(terms)

