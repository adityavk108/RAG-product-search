import { Product } from '../types';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden hover:border-indigo-500 hover:shadow-lg hover:shadow-indigo-500/20 transition-all group">
      <div className="h-16 bg-slate-700 flex items-center justify-center border-b border-slate-600">
        <h3 className="text-lg font-bold text-slate-100 text-center px-2 truncate">
          {product.name}
        </h3>
      </div>
      <div className="p-4">
        <p className="text-sm text-slate-400 mb-2">{product.brand} · {product.category}</p>
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-indigo-400">{formatPrice(product.price)}</span>
          {product.rating && (
            <div className="flex items-center gap-1">
              <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span className="text-sm text-slate-300">{product.rating}</span>
            </div>
          )}
        </div>
        {product.description && (
          <p className="text-xs text-slate-500 mt-2 line-clamp-2">{product.description}</p>
        )}
      </div>
    </div>
  );
}