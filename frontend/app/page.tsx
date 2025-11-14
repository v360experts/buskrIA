'use client'

import { useState } from 'react'
import SearchBar from '@/components/SearchBar'
import ProductGrid from '@/components/ProductGrid'
import StoreSelector from '@/components/StoreSelector'
import { Product } from '@/types/product'
import { searchProducts } from '@/services/api'

export default function Home() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStore, setSelectedStore] = useState('store-1')

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setProducts([])
      return
    }

    setLoading(true)
    setSearchQuery(query)

    try {
      const results = await searchProducts({
        query,
        limit: 20,
      })
      setProducts(results.products || [])
    } catch (error) {
      console.error('Error searching products:', error)
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Buscador de Supermercado
            </h1>
            <StoreSelector
              selectedStore={selectedStore}
              onStoreChange={setSelectedStore}
            />
          </div>
          <SearchBar onSearch={handleSearch} />
        </div>
      </header>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {searchQuery && (
          <div className="mb-4">
            <p className="text-sm text-gray-600">
              {loading
                ? 'Buscando...'
                : products.length > 0
                ? `${products.length} productos encontrados para "${searchQuery}"`
                : `No se encontraron productos para "${searchQuery}"`}
            </p>
          </div>
        )}

        <ProductGrid products={products} loading={loading} />
      </div>
    </main>
  )
}

