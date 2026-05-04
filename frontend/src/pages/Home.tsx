import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import ImageUpload from '../components/ImageUpload';
import { searchByImage } from '../services/api';

export default function Home() {
  const navigate = useNavigate();

  const handleSearch = async (query: string) => {
    navigate(`/results?q=${encodeURIComponent(query)}`);
  };

  const handleImageSearch = async (file: File) => {
    try {
      const results = await searchByImage(file, 10);
      navigate('/results', { state: { products: results.products, scores: results.scores, imageSearch: true } });
    } catch (error) {
      console.error('Image search failed:', error);
    }
  };

  const popularSearches = ['phones', 'laptops', 'headphones', 'shoes', 'watches'];

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col">
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-100 mb-4">
            Smart Product Search
          </h1>
          <p className="text-lg text-slate-400 max-w-xl mx-auto">
            Find products with text or image search, powered by AI and knowledge graphs
          </p>
        </div>

        <div className="w-full max-w-2xl mb-8">
          <SearchBar onSearch={handleSearch} placeholder="Search for products..." />
        </div>

        <div className="w-full max-w-md mb-12">
          <p className="text-sm text-slate-500 mb-3 text-center">Or search by image</p>
          <ImageUpload onImageSelect={handleImageSearch} />
        </div>

        <div className="text-center">
          <p className="text-sm text-slate-500 mb-3">Popular searches</p>
          <div className="flex flex-wrap justify-center gap-2">
            {popularSearches.map((term) => (
              <button
                key={term}
                onClick={() => handleSearch(term)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-full text-sm text-slate-300 hover:text-slate-100 transition-colors capitalize"
              >
                {term}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 border-t border-slate-700 py-12 px-4">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div className="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-100 mb-2">Multi-Modal Search</h3>
            <p className="text-sm text-slate-400">Search by text or image to find products</p>
          </div>
          <div>
            <div className="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-100 mb-2">AI-Powered Q&A</h3>
            <p className="text-sm text-slate-400">Ask questions and get intelligent answers</p>
          </div>
          <div>
            <div className="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <h3 className="font-semibold text-slate-100 mb-2">Smart Recommendations</h3>
            <p className="text-sm text-slate-400">Get similar products from knowledge graph</p>
          </div>
        </div>
      </div>
    </div>
  );
}