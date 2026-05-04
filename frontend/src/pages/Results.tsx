import { useState, useEffect } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import ProductGrid from '../components/ProductGrid';
import FilterBar from '../components/FilterBar';
import LoadingSpinner from '../components/LoadingSpinner';
import { useSearch } from '../hooks/useSearch';
import { Product } from '../types';

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const { search, loading } = useSearch();
  const [products, setProducts] = useState<Product[]>(location.state?.products || []);
  const [hasSearched, setHasSearched] = useState(!!location.state?.products);

  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null);

  useEffect(() => {
    if (query && !hasSearched) {
      handleSearch(query);
    }
  }, [query]);

  const handleSearch = async (searchQuery: string) => {
    setHasSearched(true);
    navigate(`/results?q=${encodeURIComponent(searchQuery)}`, { replace: true, state: {} });
    try {
      const results = await search(searchQuery, 20);
      setProducts(results.products);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const filteredProducts = products.filter(product => {
    if (selectedCategory && product.category !== selectedCategory) return false;
    if (selectedBrand && product.brand !== selectedBrand) return false;
    return true;
  });

  const categories = [...new Set(products.map(p => p.category))];
  const brands = [...new Set(products.map(p => p.brand))];

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="sticky top-16 z-40 bg-slate-900/95 backdrop-blur-sm border-b border-slate-700 py-4">
        <div className="max-w-7xl mx-auto px-4">
          <SearchBar onSearch={handleSearch} initialValue={query} />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="mb-6">
          <FilterBar
            categories={categories}
            brands={brands}
            selectedCategory={selectedCategory}
            selectedBrand={selectedBrand}
            onCategoryChange={setSelectedCategory}
            onBrandChange={setSelectedBrand}
          />
        </div>

        {loading ? (
          <LoadingSpinner />
        ) : hasSearched ? (
          <>
            <p className="text-slate-400 mb-4">
              {filteredProducts.length} {filteredProducts.length === 1 ? 'result' : 'results'}
              {query && ` for "${query}"`}
            </p>
            <ProductGrid
              products={filteredProducts}
              emptyMessage="No products match your search"
            />
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-400 text-lg">Enter a search term to find products</p>
          </div>
        )}
      </div>
    </div>
  );
}