from fastapi import APIRouter, Query
from typing import List, Optional, Dict
from app.services.graph_service import graph_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/product/{product_id}")
async def get_product(product_id: str) -> Optional[Dict]:
    """Get product details with graph relationships."""
    try:
        return graph_service.get_product_by_id(product_id)
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        return None


@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: int = Query(5, description="Number of similar products to return")
) -> List[Dict]:
    """Get similar products from the graph."""
    try:
        return graph_service.get_similar_products(product_id, limit)
    except Exception as e:
        logger.error(f"Error getting similar products: {e}")
        return []


@router.get("/category/{category}")
async def get_products_in_category(
    category: str,
    limit: int = Query(20, description="Number of products to return")
) -> List[str]:
    """Get products in a specific category."""
    try:
        return graph_service.get_products_by_category(category, limit)
    except Exception as e:
        logger.error(f"Error getting products by category: {e}")
        return []


@router.get("/brand/{brand}")
async def get_products_by_brand(
    brand: str,
    limit: int = Query(20, description="Number of products to return")
) -> List[str]:
    """Get products by a specific brand."""
    try:
        return graph_service.get_products_by_brand(brand, limit)
    except Exception as e:
        logger.error(f"Error getting products by brand: {e}")
        return []


@router.get("/categories")
async def get_all_categories() -> List[str]:
    """Get all categories sorted by product count."""
    try:
        return graph_service.get_all_categories()
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return []


@router.get("/brands")
async def get_all_brands() -> List[str]:
    """Get all brands sorted by product count."""
    try:
        return graph_service.get_all_brands()
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        return []


@router.get("/stats")
async def get_graph_stats() -> Dict:
    """Get graph statistics."""
    try:
        return graph_service.get_graph_stats()
    except Exception as e:
        logger.error(f"Error getting graph stats: {e}")
        return {}