from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import search, query, ingest, graph, recommendations
from app.config import settings
from app.utils.data_loader import get_csv_path
from app.services.llm_service import llm_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services
    print("Starting up E-Commerce RAG API...")
    
    # Create cache directories
    settings.cache_dir.mkdir(exist_ok=True)
    settings.embedding_cache_dir.mkdir(exist_ok=True)
    
    # Initialize LLM service
    print("Initializing LLM service...")
    if settings.gemini_api_key:
        llm_service.api_key = settings.gemini_api_key
        llm_service.initialize()
        print("LLM service initialized with Gemini API")
    else:
        print("Warning: GEMINI_API_KEY not set, LLM features disabled")
    
    # Verify CSV exists
    csv_path = get_csv_path()
    if csv_path.exists():
        print(f"Products CSV found at: {csv_path}")
    else:
        print(f"Warning: Products CSV not found at: {csv_path}")
    
    yield
    
    # Shutdown: Clean up resources
    print("Shutting down E-Commerce RAG API...")
    if llm_service and llm_service.is_initialized:
        print("LLM service closed")


app = FastAPI(
    title="E-Commerce Multi-Modal RAG API",
    version="1.0.0",
    description="Multi-modal product search and Q&A system with knowledge graph",
    lifespan=lifespan
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(query.router)
app.include_router(graph.router)
app.include_router(recommendations.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "E-Commerce RAG API",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "message": "Welcome to E-Commerce Multi-Modal RAG API",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "ingest": "/ingest",
            "search": "/search",
            "search_image": "/search/image",
            "query": "/query",
            "recommendations": "/recommendations/{product_id}",
            "graph_product": "/graph/product/{id}",
            "graph_similar": "/graph/similar/{id}",
            "graph_category": "/graph/category/{name}",
            "graph_brand": "/graph/brand/{name}",
            "graph_categories": "/graph/categories",
            "graph_brands": "/graph/brands",
            "graph_stats": "/graph/stats"
        }
    }