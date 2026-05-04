import { useState } from 'react';
import { searchProducts, searchByImage } from '../services/api';

export function useSearch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (query: string, topK: number = 10) => {
    setLoading(true);
    setError(null);
    try {
      const results = await searchProducts(query, topK);
      return results;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const searchImage = async (file: File, topK: number = 10) => {
    setLoading(true);
    setError(null);
    try {
      const results = await searchByImage(file, topK);
      return results;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Image search failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { search, searchImage, loading, error };
}