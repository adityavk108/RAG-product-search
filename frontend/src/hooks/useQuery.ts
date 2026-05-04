import { useState } from 'react';
import { queryProducts } from '../services/api';

export function useQuery() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async (question: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await queryProducts(question, 5);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { ask, loading, error };
}