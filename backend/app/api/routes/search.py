from fastapi import APIRouter, UploadFile, File, Query
from typing import Optional, List
from app.models.product import SearchResult
from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.services.graph_service import graph_service
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search_products(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(10, description="Number of results to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    include_graph: bool = Query(True, description="Include graph-based similar products")
) -> SearchResult:
    """
    Text-based product search with optional graph enhancement.
    """
    try:
        search_k = top_k * 2 if include_graph else top_k
        results = vector_store.search_text(q, search_k)
        
        product_ids = [pid for pid, score in results]
        vector_scores = {pid: score for pid, score in results}

        filtered_ids = product_ids
        graph_scores = {}

        if include_graph and product_ids:
            try:
                expanded_ids = set(product_ids)
                for pid in product_ids[:5]:
                    similar = graph_service.get_similar_products(pid, limit=3)
                    for sim in similar:
                        if sim.get('product_id'):
                            expanded_ids.add(sim['product_id'])
                            graph_scores[sim['product_id']] = sim.get('score', 0.5)

                filtered_ids = list(expanded_ids)
            except Exception as e:
                logger.warning(f"Graph expansion failed: {e}")

        if category:
            try:
                category_products = set(graph_service.get_products_by_category(category, limit=100))
                filtered_ids = [pid for pid in filtered_ids if pid in category_products]
            except Exception as e:
                logger.warning(f"Category filter failed: {e}")

        if brand:
            try:
                brand_products = set(graph_service.get_products_by_brand(brand, limit=100))
                filtered_ids = [pid for pid in filtered_ids if pid in brand_products]
            except Exception as e:
                logger.warning(f"Brand filter failed: {e}")

        final_ids = filtered_ids[:top_k]
        final_scores = []
        
        for pid in final_ids:
            vector_score = vector_scores.get(pid, 0.0)
            graph_score = graph_scores.get(pid, 0.0)
            if include_graph and graph_score > 0:
                combined = 0.7 * vector_score + 0.3 * graph_score
            else:
                combined = vector_score
            final_scores.append(combined)

        sorted_pairs = sorted(zip(final_ids, final_scores), key=lambda x: x[1], reverse=True)
        final_ids = [pid for pid, _ in sorted_pairs]
        final_scores = [score for _, score in sorted_pairs]

        products = vector_store.get_products_by_ids(final_ids)
        
        return SearchResult(products=products, scores=final_scores)
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return SearchResult(products=[], scores=[])


@router.post("/image")
async def search_by_image(
    image: UploadFile = File(..., description="Product image"),
    top_k: int = Query(10, description="Number of results to return"),
    include_graph: bool = Query(True, description="Include graph-based similar products")
) -> SearchResult:
    """
    Image-based product search.
    """
    try:
        contents = await image.read()
        img = Image.open(io.BytesIO(contents))
        
        image_embedding = embedding_service.get_image_embedding_from_pil(img)
        
        import numpy as np
        query_np = np.array([image_embedding], dtype=np.float32)
        
        if vector_store.image_index is None or vector_store.image_index.ntotal == 0:
            logger.warning("Image index is empty")
            return SearchResult(products=[], scores=[])
        
        scores, indices = vector_store.image_index.search(query_np, top_k * 2)
        
        product_ids = []
        vector_scores = {}
        
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(vector_store.product_ids):
                pid = vector_store.product_ids[idx]
                product_ids.append(pid)
                vector_scores[pid] = float(score)
        
        graph_scores = {}
        if include_graph and product_ids:
            try:
                expanded_ids = set(product_ids)
                for pid in product_ids[:5]:
                    similar = graph_service.get_similar_products(pid, limit=3)
                    for sim in similar:
                        if sim.get('product_id'):
                            expanded_ids.add(sim['product_id'])
                            graph_scores[sim['product_id']] = sim.get('score', 0.5)
                product_ids = list(expanded_ids)
            except Exception as e:
                logger.warning(f"Graph expansion failed: {e}")
        
        final_ids = product_ids[:top_k]
        final_scores = []
        
        for pid in final_ids:
            vec_score = vector_scores.get(pid, 0.0)
            gr_score = graph_scores.get(pid, 0.0)
            if include_graph and gr_score > 0:
                combined = 0.7 * vec_score + 0.3 * gr_score
            else:
                combined = vec_score
            final_scores.append(combined)
        
        sorted_pairs = sorted(zip(final_ids, final_scores), key=lambda x: x[1], reverse=True)
        final_ids = [pid for pid, _ in sorted_pairs]
        final_scores = [score for _, score in sorted_pairs]
        
        products = vector_store.get_products_by_ids(final_ids)
        
        return SearchResult(products=products, scores=final_scores)
        
    except Exception as e:
        logger.error(f"Error in image search: {e}")
        return SearchResult(products=[], scores=[])