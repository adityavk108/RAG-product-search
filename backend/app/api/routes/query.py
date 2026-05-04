from fastapi import APIRouter, Query
from typing import Optional
from app.models.product import QueryRequest, QueryResponse, ProductBase
from app.services.vector_store import vector_store
from app.services.graph_service import graph_service
from app.services.llm_service import llm_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


def hybrid_retrieval(question: str, top_k: int = 10, include_graph: bool = True) -> list:
    """Perform hybrid retrieval combining vector search and graph expansion."""
    search_k = top_k * 2
    results = vector_store.search_text(question, search_k)
    
    product_ids = [pid for pid, score in results]
    vector_scores = {pid: score for pid, score in results}

    expanded_ids = set(product_ids)
    graph_scores = {}

    if include_graph and product_ids:
        try:
            for pid in product_ids[:5]:
                similar = graph_service.get_similar_products(pid, limit=3)
                for sim in similar:
                    if sim.get('product_id'):
                        expanded_ids.add(sim['product_id'])
                        graph_scores[sim['product_id']] = sim.get('score', 0.5)
        except Exception as e:
            logger.warning(f"Graph expansion failed: {e}")

    final_ids = list(expanded_ids)
    final_scores = []
    
    for pid in final_ids:
        vector_score = vector_scores.get(pid, 0.0)
        graph_score = graph_scores.get(pid, 0.0)
        if include_graph and graph_score > 0:
            combined = 0.7 * vector_score + 0.3 * graph_score
        else:
            combined = vector_score
        final_scores.append((pid, combined))

    sorted_pairs = sorted(final_scores, key=lambda x: x[1], reverse=True)
    return sorted_pairs[:top_k]


@router.post("", response_model=QueryResponse)
async def query_products(request: QueryRequest) -> QueryResponse:
    """
    RAG-based question answering about products.
    """
    try:
        question = request.question
        top_k = request.top_k
        
        if len(question) > 1000:
            question = question[:1000]
        
        top_k = max(1, min(20, top_k))
        
        logger.info(f"Processing query: {question}")
        
        retrieved = hybrid_retrieval(question, top_k=top_k, include_graph=True)
        
        product_ids = [pid for pid, _ in retrieved]
        context_products = vector_store.get_products_by_ids(product_ids)
        
        if not context_products:
            return QueryResponse(
                answer="No products match your query. Please try a different search term.",
                sources=[]
            )
        
        answer = llm_service.generate_response(question, context_products)
        
        return QueryResponse(
            answer=answer,
            sources=context_products[:5]
        )
        
    except Exception as e:
        logger.error(f"Error in query: {e}")
        return QueryResponse(
            answer=f"Error processing your request: {str(e)}",
            sources=[]
        )


@router.get("/similar/{product_id}")
async def get_similar_via_query(
    product_id: str,
    limit: int = Query(5, ge=1, le=20)
) -> dict:
    """Get similar products using hybrid retrieval."""
    try:
        product = vector_store.product_data.get(product_id)
        if not product:
            return {"products": [], "message": "Product not found"}
        
        question = f"products similar to {product.name}"
        retrieved = hybrid_retrieval(question, top_k=limit, include_graph=True)
        
        product_ids = [pid for pid, _ in retrieved if pid != product_id]
        products = vector_store.get_products_by_ids(product_ids)
        
        return {"products": products}
        
    except Exception as e:
        logger.error(f"Error getting similar products: {e}")
        return {"products": [], "message": str(e)}