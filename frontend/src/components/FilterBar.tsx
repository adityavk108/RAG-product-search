interface FilterBarProps {
  categories: string[];
  brands: string[];
  selectedCategory: string | null;
  selectedBrand: string | null;
  onCategoryChange: (category: string | null) => void;
  onBrandChange: (brand: string | null) => void;
}

export default function FilterBar({
  categories,
  brands,
  selectedCategory,
  selectedBrand,
  onCategoryChange,
  onBrandChange,
}: FilterBarProps) {
  return (
    <div className="flex flex-wrap gap-4">
      <select
        value={selectedCategory || ''}
        onChange={(e) => onCategoryChange(e.target.value || null)}
        className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">All Categories</option>
        {categories.map((cat) => (
          <option key={cat} value={cat}>{cat}</option>
        ))}
      </select>

      <select
        value={selectedBrand || ''}
        onChange={(e) => onBrandChange(e.target.value || null)}
        className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">All Brands</option>
        {brands.map((brand) => (
          <option key={brand} value={brand}>{brand}</option>
        ))}
      </select>

      {(selectedCategory || selectedBrand) && (
        <button
          onClick={() => {
            onCategoryChange(null);
            onBrandChange(null);
          }}
          className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
        >
          Clear filters
        </button>
      )}
    </div>
  );
}