"""
Script para mostrar estadísticas de los productos en la base de datos
"""
import sys
import os
from bson import ObjectId

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_database
from dotenv import load_dotenv

load_dotenv()


def show_stats():
    """Mostrar estadísticas de productos"""
    try:
        db = get_database()
        collection = db.products
        
        total = collection.count_documents({})
        
        if total == 0:
            print("⚠️  No hay productos en la base de datos")
            print("   Ejecuta el seed primero: python -m app.seed")
            return
        
        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS DE PRODUCTOS")
        print("="*70)
        print(f"\n📦 Total de productos: {total}")
        
        # Estadísticas de campos de ranking
        products = list(collection.find({}))
        
        # Margin Score
        margin_scores = [p.get("margin_score", 0) for p in products]
        print(f"\n💵 Margin Score:")
        print(f"   Min: {min(margin_scores):.2f}")
        print(f"   Max: {max(margin_scores):.2f}")
        print(f"   Promedio: {sum(margin_scores)/len(margin_scores):.2f}")
        
        # Popularity
        popularities = [p.get("popularity", 0) for p in products]
        print(f"\n⭐ Popularity:")
        print(f"   Min: {min(popularities):.2f}")
        print(f"   Max: {max(popularities):.2f}")
        print(f"   Promedio: {sum(popularities)/len(popularities):.2f}")
        
        # Stock
        stocks = [p.get("stock", 0) for p in products]
        print(f"\n📦 Stock:")
        print(f"   Min: {min(stocks)}")
        print(f"   Max: {max(stocks)}")
        print(f"   Promedio: {sum(stocks)/len(stocks):.0f}")
        print(f"   Productos con stock bajo (<10): {sum(1 for s in stocks if s < 10)}")
        print(f"   Productos con stock alto (>100): {sum(1 for s in stocks if s > 100)}")
        
        # Sponsored
        sponsored_count = sum(1 for p in products if p.get("is_sponsored", False))
        print(f"\n📢 Patrocinados:")
        print(f"   Total: {sponsored_count}")
        print(f"   No patrocinados: {total - sponsored_count}")
        
        # Categorías
        categories = {}
        for p in products:
            cat = p.get("category", "Sin categoría")
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📁 Categorías:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count}")
        
        # Top productos por popularidad
        print(f"\n🏆 Top 5 productos por popularidad:")
        top_popular = sorted(products, key=lambda x: x.get("popularity", 0), reverse=True)[:5]
        for i, p in enumerate(top_popular, 1):
            print(f"   {i}. {p.get('name', 'N/A')} - Popularidad: {p.get('popularity', 0):.2f}")
        
        # Top productos por margen
        print(f"\n💰 Top 5 productos por margen:")
        top_margin = sorted(products, key=lambda x: x.get("margin_score", 0), reverse=True)[:5]
        for i, p in enumerate(top_margin, 1):
            print(f"   {i}. {p.get('name', 'N/A')} - Margen: {p.get('margin_score', 0):.2f}")
        
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    show_stats()

