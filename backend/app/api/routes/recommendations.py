from fastapi import APIRouter, Query
from typing import List
from app.models.product import ProductBase, RecommendationResult
from app.services.graph_service import graph_service
from app.services.vector_store import vector_store
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{product_id}", response_model=RecommendationResult)
async def get_recommendations(
    product_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations")
) -> RecommendationResult:
    """
    Get similar product recommendations based on the given product.
    Uses Neo4j graph to find similar products.
    """
    try:
        similar_products = graph_service.get_similar_products(product_id, limit)
        
        if not similar_products:
            product = vector_store.product_data.get(product_id)
            if product:
                return RecommendationResult(
                    products=[],
                    message="No similar products found in the knowledge graph."
                )
            return RecommendationResult(
                products=[],
                message="Product not found."
            )
        
        product_ids = [sim.get('product_id') for sim in similar_products if sim.get('product_id')]
        products = vector_store.get_products_by_ids(product_ids)
        
        return RecommendationResult(products=products)
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return RecommendationResult(
            products=[],
            message=f"Error: {str(e)}"
        )


@router.get("/category/{category}", response_model=RecommendationResult)
async def get_category_recommendations(
    category: str,
    limit: int = Query(10, ge=1, le=50, description="Number of products to return")
) -> RecommendationResult:
    """
    Get products in a specific category.
    """
    try:
        product_ids = graph_service.get_products_by_category(category, limit)
        
        if not product_ids:
            return RecommendationResult(
                products=[],
                message=f"No products found in category: {category}"
            )
        
        products = vector_store.get_products_by_ids(product_ids)
        
        return RecommendationResult(products=products)
        
    except Exception as e:
        logger.error(f"Error getting category recommendations: {e}")
        return RecommendationResult(
            products=[],
            message=f"Error: {str(e)}"
        )


@router.get("/brand/{brand}", response_model=RecommendationResult)
async def get_brand_recommendations(
    brand: str,
    limit: int = Query(10, ge=1, le=50, description="Number of products to return")
) -> RecommendationResult:
    """
    Get products from a specific brand.
    """
    try:
        product_ids = graph_service.get_products_by_brand(brand, limit)
        
        if not product_ids:
            return RecommendationResult(
                products=[],
                message=f"No products found for brand: {brand}"
            )
        
        products = vector_store.get_products_by_ids(product_ids)
        
        return RecommendationResult(products=products)
        
    except Exception as e:
        logger.error(f"Error getting brand recommendations: {e}")
        return RecommendationResult(
            products=[],
            message=f"Error: {str(e)}"
        )