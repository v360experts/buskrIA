'use client'

import { Product } from '@/types/product'

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
    }).format(price)
  }

  const getStockStatus = (stock: number) => {
    if (stock === 0) {
      return { text: 'Agotado', color: 'text-red-600 bg-red-50' }
    }
    if (stock < 10) {
      return { text: 'Últimas unidades', color: 'text-orange-600 bg-orange-50' }
    }
    return { text: 'Disponible', color: 'text-green-600 bg-green-50' }
  }

  const stockStatus = getStockStatus(product.stock)

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden flex flex-col">
      {/* Image */}
      <div className="relative w-full h-48 bg-gray-100">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              // Fallback a placeholder si la imagen falla
              e.currentTarget.style.display = 'none';
              e.currentTarget.nextElementSibling?.classList.remove('hidden');
            }}
          />
        ) : null}
        <div className={`w-full h-full flex items-center justify-center text-gray-400 ${product.image_url ? 'hidden' : ''}`}>
          <svg
            className="w-16 h-16"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
        {product.is_sponsored && (
          <div className="absolute top-2 right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded">
            PATROCINADO
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col">
        {/* Brand */}
        {product.brand && (
          <p className="text-xs text-gray-500 mb-1">{product.brand}</p>
        )}

        {/* Name */}
        <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>

        {/* Category */}
        <p className="text-xs text-gray-400 mb-3">{product.category}</p>

        {/* Price */}
        <div className="mt-auto">
          <p className="text-xl font-bold text-primary-600 mb-2">
            {formatPrice(product.price)}
          </p>

          {/* Stock Status */}
          <div
            className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${stockStatus.color}`}
          >
            {stockStatus.text}
          </div>
        </div>
      </div>
    </div>
  )
}

