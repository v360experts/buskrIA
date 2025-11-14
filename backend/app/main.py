from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from app.database import get_database
from app.services.product_service import ProductService
from app.services.search_service import SearchService
from app.services.related_service import RelatedService
from app.models.product import Product, ProductCreate, ProductUpdate

load_dotenv()

app = FastAPI(title="Supermarket Search API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = get_database()
product_service = ProductService(db)
search_service = SearchService(db)
related_service = RelatedService(db)


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 20


class SearchResponse(BaseModel):
    products: List[Product]
    total: int
    query: str


@app.get("/")
async def root():
    return {"message": "Supermarket Search API", "version": "1.0.0"}


@app.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    """Crear un nuevo producto"""
    try:
        created_product = await product_service.create_product(product)
        return created_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductUpdate):
    """Actualizar un producto existente"""
    try:
        updated_product = await product_service.update_product(product_id, product)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Obtener un producto por ID"""
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/search", response_model=SearchResponse)
async def search_products(request: SearchRequest):
    """Búsqueda semántica de productos"""
    try:
        results = await search_service.search(
            query=request.query,
            category=request.category,
            brand=request.brand,
            min_price=request.min_price,
            max_price=request.max_price,
            limit=request.limit
        )
        return SearchResponse(
            products=results["products"],
            total=results["total"],
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}/related", response_model=List[Product])
async def get_related_products(product_id: str, limit: int = 10):
    """Obtener productos relacionados"""
    try:
        related = await related_service.get_related_products(product_id, limit)
        return related
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", 8000)))

