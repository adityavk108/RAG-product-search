import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <span className="text-xl font-bold text-slate-100">E-Commerce RAG</span>
          </Link>
          <div className="flex items-center space-x-4">
            <Link
              to="/"
              className="px-3 py-2 rounded-md text-sm font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-700 transition-colors"
            >
              Search
            </Link>
            <Link
              to="/qa"
              className="px-3 py-2 rounded-md text-sm font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-700 transition-colors"
            >
              Q&A
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}