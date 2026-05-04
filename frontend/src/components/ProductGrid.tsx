import { Product } from '../types';
import ProductCard from './ProductCard';
import LoadingSpinner from './LoadingSpinner';

interface ProductGridProps {
  products: Product[];
  loading?: boolean;
  emptyMessage?: string;
}

export default function ProductGrid({ products, loading, emptyMessage = "No products found" }: ProductGridProps) {
  if (loading) {
    return <LoadingSpinner />;
  }

  if (!products.length) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400 text-lg">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.product_id}
          product={product}
        />
      ))}
    </div>
  );
}