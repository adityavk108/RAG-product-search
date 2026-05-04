# RAG-product-search

A production-grade Multi-Modal Graph RAG system for e-commerce product search. Combines semantic vector search, knowledge graphs, and LLM-powered Q&A into one platform.

---

## What It Does

- Searches products by meaning, not just keywords ("wireless earbuds" finds Bluetooth headphones)
- Finds similar products from images (upload a shoe photo, get similar styles)
- Recommends related products using category/brand relationships from Neo4j
- Answers questions in natural language ("which iPhone has the best camera?")
- Shows products in dark-mode React UI with category/price filters

---

## Architecture

**Data Layer:**
- 280 products in CSV with 280 product images
- FAISS vector index (384-dim text embeddings via Sentence Transformers)
- Neo4j graph (products connected to categories and brands)

**Intelligence Layer:**
- all-MiniLM-L6-v2 model for text embeddings (384 dimensions)
- OpenAI CLIP for image similarity (512 dimensions)
- Neo4j with APOC for graph queries and path finding
- Gemini 2.0 Flash Lite for generating conversational responses

**API Layer:**
- FastAPI with async endpoints and CORS middleware
- React 18 + TypeScript + Tailwind CSS frontend
- Docker Compose with health checks for all services

---

## Architectural Details

### Vector Search Pipeline
- Each product's text (name + description + brand + category) is concatenated and embedded using Sentence Transformers into a 384-dimensional vector
- Vectors are L2-normalized to enable cosine similarity via inner product
- FAISS IndexFlatIP index stores all vectors for O(1) similarity search
- Query embedding uses the same model, then index returns top-k IDs with similarity scores
- Embeddings are cached to disk in `backend/cache/embeddings/` to avoid recomputation on restart
- Batch processing embeds all 280 products in ~30 seconds during `/ingest`

### Knowledge Graph Schema
- Node types: Product, Category, Brand
- Relationship types:
  - `(:Product)-[:IN_CATEGORY]->(:Category)` - connects product to its category
  - `(:Product)-[:BRANDED_BY]->(:Brand)` - connects product to its brand
  - `(:Product)-[:SIMILAR_TO]->(:Product)` - connects similar products (same category, similar price)
- Graph service creates nodes and relationships during `/ingest`
- Queries support: single product lookup, category traversal, brand filtering, similarity paths

### RAG Q&A Pipeline
1. User sends natural language question to `/query`
2. Query is embedded using Sentence Transformers (same as search)
3. FAISS returns top-10 most similar products
4. Graph expands results: fetch products in same categories and brands
5. Combined product context is formatted into a prompt with name, price, description, rating
6. System prompt instructs Gemini to use only the provided context, cite specific products, format prices in INR
7. Gemini generates response. If no API key, returns raw search results instead

### Request Flow
- **Search**: POST `/search` -> embed query -> FAISS lookup -> return products with scores
- **Image Search**: POST `/search/image` -> embed image via CLIP -> FAISS lookup -> return similar products
- **Recommendations**: GET `/recommendations/{id}` -> find similar from vector index + add graph neighbors
- **Graph Query**: GET `/graph/product/{id}` -> Neo4j MATCH query -> return product with relationships
- **Q&A**: POST `/query` -> embed -> retrieve -> format context -> call Gemini -> return answer

---

## Key Features

- **Semantic Search**: Vector similarity finds products even when keywords don't match. Searching "running shoes" returns Nike React and ASICS Gel-Kayano even if the word "running" isn't in every name.

- **Image Search**: Upload product photos to find visually similar items using CLIP embeddings. Works even for products with no text description.

- **Knowledge Graph**: Neo4j stores category and brand relationships. Query "all Apple phones" traverses from Product to Category nodes through IN_CATEGORY edges.

- **RAG Q&A**: Gemini generates natural language answers by grounding responses in retrieved product context. Says "based on the products I found..." before answering.

- **Recommendations**: Hybrid retrieval combines vector similarity with graph expansion. Finds similar products from the vector index, then adds products from the same category.

- **Production Ready**: One `docker compose up` starts all services with health checks. Backend waits for Neo4j to be healthy before accepting requests.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI, Python 3.11, Uvicorn |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Vector Search | FAISS (CPU), Sentence Transformers |
| Image Embeddings | OpenAI CLIP |
| Knowledge Graph | Neo4j 5.14 with APOC |
| LLM | Google Gemini 2.0 Flash Lite |
| Container | Docker Compose |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic text search |
| `/search/image` | POST | Image-based similarity search |
| `/recommendations/{id}` | GET | Get similar products for a given product |
| `/query` | POST | Ask questions in natural language |
| `/graph/product/{id}` | GET | Get product with its category/brand relationships |
| `/graph/categories` | GET | List all product categories |
| `/graph/brands` | GET | List all brands |
| `/graph/stats` | GET | Graph node and relationship counts |
| `/ingest` | POST | Load all products to vector store and Neo4j |
| `/health` | GET | Backend health status |

---

## Quick Start

1. Run `quickstart.bat` (requires Docker Desktop)
2. Open http://localhost:3000 for the frontend
3. Open http://localhost:8000/docs for API documentation
4. Open http://localhost:7474 to explore the Neo4j graph (login: neo4j/password)

---

## Project Structure

```
RAG-product-search/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # 5 route modules
│   │   ├── services/         # embedding, vector, graph, LLM
│   │   ├── models/           # Pydantic schemas
│   │   └── utils/            # CSV and image loaders
│   ├── data/
│   │   ├── products.csv      # 280 products
│   │   └── images/           # 280 images (p001.jpg to p280.jpg)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # ProductCard, SearchBar, Navbar
│   │   ├── pages/            # Home, Results, Q&A
│   │   ├── hooks/            # useSearch, useQuery
│   │   └── services/         # API client
│   └── package.json
├── docker-compose.yml        # 3 services: neo4j, backend, frontend
└── README.md
```

---

## Data

**Products:** 280 items across 25+ categories

- Electronics: Phones, Laptops, Headphones, Cameras, Tablets, Wearables, Speakers
- Computing: Gaming Consoles, Gaming Accessories, Office Supplies
- Lifestyle: Shoes, Clothing, Watches, Sunglasses
- Home: Smart Home, Kitchen Appliances, Furniture
- Sports: Fitness Equipment, Sports Equipment
- Other: Baby Products, Pet Supplies, Automotive, Books & Media

**Product Fields:** product_id, name, description, brand, category, price (INR), image_file, rating (1-5), reviews

---

## Setup

1. Copy `backend/.env.example` to `backend/.env`
2. Add your `GEMINI_API_KEY` from Google AI Studio
3. Run `quickstart.bat`
4. access the UI at localhost:3000
