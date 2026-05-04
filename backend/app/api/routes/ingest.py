from fastapi import APIRouter
from app.models.product import IngestResponse
from app.utils.data_loader import load_products_from_csv, get_csv_path, get_images_dir
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.graph_service import graph_service
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
async def ingest_products() -> IngestResponse:
    """
    Ingest products from CSV, generate embeddings, build knowledge graph.
    """
    try:
        # Load products from CSV
        csv_path = get_csv_path()
        images_dir = get_images_dir()
        
        logger.info(f"Loading products from {csv_path}")
        products = load_products_from_csv(str(csv_path))
        logger.info(f"Loaded {len(products)} products from CSV")

        # Initialize embedding models
        logger.info("Initializing embedding models...")
        embedding_service.initialize()

        # Clear existing vector store
        vector_store.clear()

        # Add products to vector store (generates embeddings)
        logger.info("Generating embeddings and adding to vector store...")
        vector_store.add_products(products)

        # Save embeddings to cache
        cache_dir = "/app/cache/embeddings"
        os.makedirs(cache_dir, exist_ok=True)
        vector_store.save_index(cache_dir)
        logger.info(f"Saved embeddings to {cache_dir}")

        # Build knowledge graph
        logger.info("Building knowledge graph in Neo4j...")
        try:
            graph_service.connect()
            graph_service.build_graph_from_products(products)
            logger.info("Knowledge graph built successfully")
        except Exception as e:
            logger.warning(f"Failed to build knowledge graph: {e}")

        # Extract categories and brands
        categories = list(set(p.category for p in products))
        brands = list(set(p.brand for p in products))
        categories.sort()
        brands.sort()

        logger.info(f"Ingestion complete: {len(products)} products, {len(categories)} categories, {len(brands)} brands")

        return IngestResponse(
            status="success",
            message=f"Successfully ingested {len(products)} products with embeddings",
            products_loaded=len(products),
            categories=categories,
            brands=brands
        )

    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return IngestResponse(
            status="error",
            message=f"Ingestion failed: {str(e)}",
            products_loaded=0,
            categories=[],
            brands=[]
        )