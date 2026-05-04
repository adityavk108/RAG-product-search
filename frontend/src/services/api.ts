import { SearchResult, QueryResponse, RecommendationResult } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const searchProducts = async (query: string, topK: number = 10): Promise<SearchResult> => {
  const response = await fetch(
    `${API_BASE}/search?q=${encodeURIComponent(query)}&top_k=${topK}`
  );
  if (!response.ok) throw new Error('Search failed');
  return response.json();
};

export const searchByImage = async (imageFile: File, topK: number = 10): Promise<SearchResult> => {
  const formData = new FormData();
  formData.append('image', imageFile);
  const response = await fetch(
    `${API_BASE}/search/image?top_k=${topK}`,
    { method: 'POST', body: formData }
  );
  if (!response.ok) throw new Error('Image search failed');
  return response.json();
};

export const queryProducts = async (question: string, topK: number = 5): Promise<QueryResponse> => {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, top_k: topK })
  });
  if (!response.ok) throw new Error('Query failed');
  return response.json();
};

export const getRecommendations = async (productId: string, limit: number = 5): Promise<RecommendationResult> => {
  const response = await fetch(`${API_BASE}/recommendations/${productId}?limit=${limit}`);
  if (!response.ok) throw new Error('Recommendations failed');
  return response.json();
};

export const getCategoryProducts = async (category: string, limit: number = 10): Promise<RecommendationResult> => {
  const response = await fetch(`${API_BASE}/recommendations/category/${encodeURIComponent(category)}?limit=${limit}`);
  if (!response.ok) throw new Error('Category products failed');
  return response.json();
};

export const getBrandProducts = async (brand: string, limit: number = 10): Promise<RecommendationResult> => {
  const response = await fetch(`${API_BASE}/recommendations/brand/${encodeURIComponent(brand)}?limit=${limit}`);
  if (!response.ok) throw new Error('Brand products failed');
  return response.json();
};

export const ingestProducts = async (): Promise<{ status: string; message: string }> => {
  const response = await fetch(`${API_BASE}/ingest`, { method: 'POST' });
  if (!response.ok) throw new Error('Ingest failed');
  return response.json();
};

export const getGraphStats = async (): Promise<{
  product_count: number;
  category_count: number;
  brand_count: number;
}> => {
  const response = await fetch(`${API_BASE}/graph/stats`);
  if (!response.ok) throw new Error('Graph stats failed');
  return response.json();
};