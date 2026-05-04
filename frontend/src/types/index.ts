export interface Product {
  product_id: string;
  name: string;
  description: string;
  brand: string;
  category: string;
  price: number;
  image_path: string;
  rating?: number;
  reviews?: string[];
}

export interface SearchResult {
  products: Product[];
  scores: number[];
}

export interface QueryRequest {
  question: string;
  top_k: number;
}

export interface QueryResponse {
  answer: string;
  sources: Product[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Product[];
}

export interface RecommendationResult {
  products: Product[];
  message?: string;
}