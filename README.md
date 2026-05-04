# RAG-product-search

A production-ready Multi-Modal Graph RAG system for e-commerce product search and recommendation. Combines vector similarity search, knowledge graph relationships, and LLM-powered Q&A to deliver intelligent shopping assistance.

---

## System Architecture

```
                    +------------------+
                    |   Frontend       |
                    | (React + Vite)   |
                    +--------+---------+
                             |
                    +--------v---------+
                    |    Backend API   |
                    | (FastAPI/Python) |
                    +--------+---------+
                             |
         +-----------------+-----------------+
         |                 |                 |
+--------v-------+  +------v------+  +-------v-------+
| Vector Store  |  | Knowledge   |  | LLM Service    |
| (FAISS)       |  | Graph       |  | (Gemini)       |
| 384-dim text  |  | (Neo4j)     |  | gemini-2.0-flash|
+--------+-------+  +------+------+  +---------------+
         |                 |
+--------v-------+  +------v------+      +--------+------+
| Data Layer     |  | Products    |      | Embeddings    |
| CSV + Images   |  | (280 items) |      | Sentence-     |
+----------------+  +-------------+      | Transformers  |
                                        +---------------+
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend API | FastAPI, Python 3.11, Uvicorn |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Vector Store | FAISS (CPU-optimized) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2, 384-dim) |
| Image Embeddings | OpenAI CLIP (512-dim) |
| Knowledge Graph | Neo4j 5.14 |
| LLM | Google Gemini 2.0 Flash Lite |
| Containerization | Docker, Docker Compose |
| Database | Neo4j, CSV (280 products) |

---

## Key Features

1. **Multi-Modal Semantic Search** - Text and image-based product similarity using hybrid vector embeddings

2. **Knowledge Graph** - Neo4j-powered product relationships (category, brand, similar products)

3. **RAG Q&A** - Gemini LLM generates natural language answers from retrieved product context

4. **Recommendation Engine** - Hybrid retrieval combining vector similarity + graph expansion

5. **Production Architecture** - Dockerized services with health checks, CORS, async processing

6. **Dark Mode UI** - React + Tailwind interface with search, filters, and chat Q&A

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/search` | POST | Semantic product search |
| `/search/image` | POST | Image-based product search |
| `/recommendations/{id}` | GET | Similar products |
| `/query` | POST | RAG-powered Q&A |
| `/graph/product/{id}` | GET | Product relationships |
| `/graph/categories` | GET | All categories |
| `/graph/stats` | GET | Graph statistics |
| `/ingest` | POST | Load products to vector store + graph |

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
│   │   ├── api/routes/     # FastAPI endpoints
│   │   ├── services/       # Business logic
│   │   ├── models/         # Pydantic schemas
│   │   └── utils/          # Data loaders
│   ├── data/
│   │   ├── products.csv    # 280 products
│   │   └── images/         # Product images
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # App pages
│   │   ├── hooks/          # Custom hooks
│   │   └── services/       # API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Data Schema

**Product Model:**
```
product_id: string (P001-P280)
name: string
description: string
brand: string
category: string (25+ categories)
price: float (INR)
image_file: string (p001.jpg format)
rating: float (1.0-5.0)
reviews: string[] (semicolon-separated)
```

**Categories:** Phones, Laptops, Headphones, Cameras, Shoes, Tablets, Smart Home, Gaming Consoles, Gaming Accessories, Fitness Equipment, Kitchen Appliances, Beauty & Personal Care, Baby Products, Pet Supplies, Automotive, Electronics Accessories, Furniture, Sports Equipment, Books & Media, Office Supplies, Wearables, Speakers, Watches, Sunglasses, Clothing

---

## Architectural Details

**Vector Search Pipeline:**
- Text embeddings via Sentence Transformers (384-dim, normalized)
- FAISS IndexFlatIP for cosine similarity
- Batch processing for 280 products (~30 seconds)
- Cache persists to `backend/cache/embeddings/`

**Knowledge Graph Schema:**
- Nodes: Product, Category, Brand
- Relationships: `(:Product)-[:IN_CATEGORY]->(:Category)`
- Relationships: `(:Product)-[:BRANDED_BY]->(:Brand)`
- Relationships: `(:Product)-[:SIMILAR_TO]->(:Product)`

**RAG Pipeline:**
- Query embedding -> FAISS search (top-k)
- Graph expansion: fetch category/brand neighbors
- Context assembled from retrieved products
- Gemini 2.0 Flash Lite generates response

---

## Environment Variables

```bash
# Required
GEMINI_API_KEY=your-google-api-key  # Get from Google AI Studio

# Optional (defaults in docker-compose.yml)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

## Docker Services

| Service | Port | Health Check |
|---------|------|--------------|
| neo4j | 7474, 7687 | 30s interval |
| backend | 8000 | /health |
| frontend | 3000 | nginx health |

---

## Development Notes

- CPU-only PyTorch for smaller Docker images
- CLIP model gracefully falls back to placeholders if loading fails
- Neo4j APOC plugin enabled for advanced queries
- Frontend uses localhost:8000 (not Docker internal hostname)

---

## License

MIT License