import axios from 'axios'
import { SearchRequest, SearchResponse, Product } from '@/types/product'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const searchProducts = async (
  request: SearchRequest
): Promise<SearchResponse> => {
  const response = await api.post<SearchResponse>('/search', request)
  return response.data
}

export const getProduct = async (productId: string): Promise<Product> => {
  const response = await api.get<Product>(`/products/${productId}`)
  return response.data
}

export const getRelatedProducts = async (
  productId: string,
  limit: number = 10
): Promise<Product[]> => {
  const response = await api.get<Product[]>(
    `/products/${productId}/related?limit=${limit}`
  )
  return response.data
}

