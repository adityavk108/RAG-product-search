from pydantic import BaseModel
from typing import Optional, List


class ProductBase(BaseModel):
    product_id: str
    name: str
    description: str
    brand: str
    category: str
    price: float
    image_path: str
    rating: Optional[float] = None
    reviews: Optional[List[str]] = []


class ProductInDB(ProductBase):
    text_embedding: Optional[List[float]] = None
    image_embedding: Optional[List[float]] = None


class SearchResult(BaseModel):
    products: List[ProductBase]
    scores: List[float]


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[ProductBase]


class RecommendationResult(BaseModel):
    products: List[ProductBase]
    message: Optional[str] = None


class IngestResponse(BaseModel):
    status: str
    message: str
    products_loaded: int = 0
    categories: List[str] = []
    brands: List[str] = []