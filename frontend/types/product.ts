export interface Product {
  id: string
  name: string
  normalized_name: string
  brand?: string
  category: string
  description?: string
  price: number
  stock: number
  image_url?: string
  margin_score: number
  popularity: number
  is_sponsored: boolean
  tags: string[]
  created_at?: string
  updated_at?: string
}

export interface SearchRequest {
  query: string
  category?: string
  brand?: string
  min_price?: number
  max_price?: number
  limit?: number
}

export interface SearchResponse {
  products: Product[]
  total: number
  query: string
}

