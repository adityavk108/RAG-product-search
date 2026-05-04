# RAG-product-search

RAG-product-search is a production-grade Multi-Modal Graph RAG system designed for e-commerce product discovery. The system combines three powerful search paradigms - semantic vector search, knowledge graph traversal, and large language model generation - into a unified platform that enables intelligent product search, visual similarity matching, and natural language Q&A for online shopping.

Traditional e-commerce search relies on keyword matching, which fails when users don't know the exact product names or when they describe needs in natural language. This project addresses that gap by embedding products into a semantic vector space where similar items cluster together, regardless of keyword overlap. A Neo4j knowledge graph adds structural understanding of brand-category-product relationships, enabling graph traversal for related recommendations. Finally, Gemini LLM generates human-readable answers by grounding responses in the retrieved product context, transforming raw search results into conversational assistance.

The system targets developers building e-commerce platforms, students learning modern AI architectures, and teams evaluating RAG implementations for production use. It demonstrates how multiple AI components - sentence transformers for text, CLIP for images, Neo4j for relationships, and Gemini for generation - can be orchestrated into a cohesive application. With 280 products across 25 categories, the dataset is large enough to showcase real search behavior while remaining manageable for local development.

Technically, the system processes product data through an ingestion pipeline that generates 384-dimensional text embeddings using Sentence Transformers, stores them in a FAISS vector index for sub-millisecond similarity search, and creates Neo4j nodes with category/brand relationships. The API layer accepts text queries or image uploads, performs hybrid retrieval combining vector similarity with graph expansion, and optionally passes the results to Gemini for natural language response generation. The React frontend provides a dark-mode interface for search, filtering, and chat-based interaction.

---

## Architecture

The system follows a three-tier architecture: data layer at the bottom, intelligence engines in the middle, and API/presentation at the top. The data layer consists of a CSV file containing 280 products with associated images stored in the filesystem, a FAISS vector index for semantic search, and a Neo4j graph database for relationship queries. The intelligence layer includes an embedding service that generates 384-dimensional vectors using Sentence Transformers (all-MiniLM-L6-v2), a graph service that manages Neo4j nodes and relationships, and an LLM service that interfaces with Google's Gemini model. The API layer, built on FastAPI, exposes endpoints for search, recommendations, graph queries, and RAG-powered Q&A.

### Vector Search Engine

The vector search engine converts product text descriptions into dense vector embeddings using Sentence Transformers. Each product's name, description, brand, and category are concatenated into a single text string, then encoded into a 384-dimensional vector with L2-normalization. These embeddings are stored in a FAISS IndexFlatIP index, which performs inner product search equivalent to cosine similarity on normalized vectors. During search, a query is embedded using the same model, then the index returns the top-k most similar products in sub-millisecond time. The embedding service supports batch processing for efficient ingestion of all 280 products in approximately 30 seconds, and results are cached to disk to avoid recomputation on restart.

### Knowledge Graph

The knowledge graph, built on Neo4j 5.14, models products as nodes with three primary relationship types. Every product node connects to a Category node via an IN_CATEGORY relationship, enabling queries like "find all phones" by traversing from the Category node. Products connect to Brand nodes via BRANDED_BY relationships, allowing brand-centric queries such as "find all Apple products." Finally, SIMILAR_TO relationships link products that share categories and similar price ranges, providing the foundation for the recommendation engine. The graph service exposes endpoints to query individual products, list all categories and brands, retrieve products by category, and compute graph statistics including node counts and relationship distributions.

### RAG Pipeline

The Retrieval-Augmented Generation pipeline combines vector search, graph expansion, and LLM generation into a single Q&A flow. When a user submits a natural language query, the system first embeds the query and retrieves the top-10 most similar products from FAISS. Simultaneously, it queries the Neo4j graph to find products in the same categories and brands as the top results. This dual retrieval produces a set of 15-20 candidate products. The system then formats these products into a context string with names, prices, descriptions, and ratings. This context, along with a system prompt defining the assistant's behavior, is sent to Gemini 2.0 Flash Lite, which generates a natural language response grounded in the retrieved products. If no API key is configured, the system gracefully degrades to returning only the raw search results without LLM generation.

### Data Flow

A typical search request flows through the system as follows. The frontend sends a POST request with a query string to the /search endpoint. FastAPI invokes the search service, which calls the embedding service to convert the query into a 384-dimensional vector. The vector is passed to the FAISS index, which returns the top-k product IDs with similarity scores. These IDs are used to fetch full product details from the CSV data. Simultaneously, the graph service may be called to retrieve category or brand neighbors for expansion. The final result is sorted by relevance and returned to the frontend as a JSON array of product objects.

---

## Key Features

**Multi-Modal Semantic Search** - The search engine performs vector-based similarity matching using 384-dimensional embeddings from Sentence Transformers. Unlike keyword search, this approach finds products that are semantically similar to the query, even when they use different terminology. For example, searching for "wireless earbuds" will return Bluetooth headphones and TWS earphones even if those exact words don't appear in the product names.

**Image-Based Product Search** - The system supports uploading product images to find visually similar items using OpenAI's CLIP model. When an image is submitted, CLIP generates a 512-dimensional embedding that is compared against the image embedding database. This enables reverse image search for products, such as finding all similar-looking shoes from a photo. If CLIP fails to load, the system gracefully falls back to text-only search.

**Knowledge Graph Relationships** - Neo4j maintains structured relationships between products, categories, and brands. This enables graph-based queries like finding all products in a category, all products from a brand, or products related through similarity relationships. The graph also supports path queries to find products that are two or three hops away through category-brand-product chains.

**RAG-Powered Q&A** - The /query endpoint accepts natural language questions and generates answers using Gemini. The system retrieves relevant products as context, formats them into a prompt, and uses Gemini to generate a conversational response. This transforms the search experience from a list of results into an interactive shopping assistant that can explain product differences, suggest alternatives, and answer specific questions about specifications.

**Recommendation Engine** - The /recommendations endpoint generates similar product suggestions by combining vector similarity with graph-based expansion. For a given product ID, it finds similar products from the vector index, then expands the results by including products in the same category or from the same brand. This hybrid approach provides more diverse and contextually relevant recommendations than pure similarity search.

**Production-Grade Architecture** - The system is containerized with Docker Compose, includes health checks for all services, implements CORS for frontend access, and uses async FastAPI endpoints for concurrent request handling. The backend creates necessary cache directories on startup, handles missing API keys gracefully, and logs startup and runtime information for debugging.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI, Python 3.11, Uvicorn |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Vector Store | FAISS (CPU-optimized) |
| Text Embeddings | Sentence Transformers (all-MiniLM-L6-v2, 384-dim) |
| Image Embeddings | OpenAI CLIP (512-dim) |
| Knowledge Graph | Neo4j 5.14 |
| LLM | Google Gemini 2.0 Flash Lite |
| Containerization | Docker, Docker Compose |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic product search with text query |
| `/search/image` | POST | Image-based product similarity search |
| `/recommendations/{id}` | GET | Get similar products for a given product ID |
| `/query` | POST | RAG-powered natural language Q&A |
| `/graph/product/{id}` | GET | Get product with its graph relationships |
| `/graph/categories` | GET | List all product categories |
| `/graph/brands` | GET | List all product brands |
| `/graph/stats` | GET | Graph statistics (node and relationship counts) |
| `/ingest` | POST | Load products into vector store and Neo4j graph |

---

## Quick Start

1. **Configure API Key**
   ```bash
   cp backend/.env.example backend/.env
   # Add your GEMINI_API_KEY to backend/.env
   ```

2. **Start Services**
   ```bash
   docker compose up -d
   ```

3. **Access Application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Neo4j Browser: http://localhost:7474 (neo4j/password)

---

## Project Structure

```
RAG-product-search/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI endpoints (search, query, graph, recommendations)
│   │   ├── services/        # Business logic (embedding, vector, graph, LLM)
│   │   ├── models/          # Pydantic data models
│   │   └── utils/           # CSV and image data loaders
│   ├── data/
│   │   ├── products.csv     # 280 products across 25+ categories
│   │   └── images/          # 280 product images
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React UI components (ProductCard, SearchBar, etc.)
│   │   ├── pages/           # App pages (Home, Results, Q&A)
│   │   ├── hooks/           # Custom React hooks (useSearch, useQuery)
│   │   └── services/        # API client for backend communication
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Service orchestration (Neo4j, backend, frontend)
└── README.md
```

---

## Data Schema

**Product Model:**
- product_id: string (format: P001 to P280)
- name: string (product name)
- description: string (product features and details)
- brand: string (manufacturer name)
- category: string (product category from 25+ options)
- price: float (price in Indian Rupees)
- image_file: string (filename in p001.jpg format)
- rating: float (1.0 to 5.0 scale)
- reviews: string array (semicolon-separated customer reviews)

**Product Categories:** Phones, Laptops, Headphones, Cameras, Shoes, Tablets, Smart Home, Gaming Consoles, Gaming Accessories, Fitness Equipment, Kitchen Appliances, Beauty & Personal Care, Baby Products, Pet Supplies, Automotive, Electronics Accessories, Furniture, Sports Equipment, Books & Media, Office Supplies, Wearables, Speakers, Watches, Sunglasses, Clothing

---

## Environment Variables

```bash
# Required
GEMINI_API_KEY=your-google-api-key  # Get from Google AI Studio (https://aistudio.google.com/app/apikey)

# Optional (defaults work for local development)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

## Docker Services

| Service | Container | Ports | Health Check |
|---------|-----------|-------|--------------|
| neo4j | ecommerce-neo4j | 7474, 7687 | 30s interval, wget to 7474 |
| backend | ecommerce-backend | 8000 | HTTP GET /health |
| frontend | ecommerce-frontend | 3000 | nginx wget to port 80 |

---

## Development Notes

- The system uses CPU-only PyTorch to reduce Docker image size (GPU version adds ~2GB)
- CLIP image embeddings gracefully degrade to zero-vectors if the model fails to load, allowing text search to continue
- Neo4j APOC plugin is enabled for advanced graph procedures
- Frontend communicates with backend via localhost:8000 (Docker port mapping) rather than Docker DNS for browser compatibility
- The embedding cache in backend/cache/embeddings/ persists between restarts to speed up subsequent launches