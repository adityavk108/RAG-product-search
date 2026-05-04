import faiss
import numpy as np
import json
import os
from typing import List, Tuple, Dict
from app.models.product import ProductBase, ProductInDB
from app.services.embedding_service import embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for text and image embeddings."""

    def __init__(self):
        self.text_index = None
        self.image_index = None
        self.product_ids: List[str] = []
        self.product_data: Dict[str, ProductInDB] = {}
        self.text_idx_to_product: Dict[int, str] = {}
        self.image_idx_to_product: Dict[int, str] = {}
        self.text_dim = 384
        self.image_dim = 512

    def add_products(self, products: List[ProductBase]):
        """Add products to the vector store."""
        if not products:
            return

        logger.info(f"Adding {len(products)} products to vector store...")
        
        # Create FAISS indexes if not exists
        if self.text_index is None:
            self.text_index = faiss.IndexFlatIP(self.text_dim)
            logger.info(f"Created text index (dim={self.text_dim})")
        
        if self.image_index is None:
            self.image_index = faiss.IndexFlatIP(self.image_dim)
            logger.info(f"Created image index (dim={self.image_dim})")

        # Generate embeddings and add to indexes
        text_embeddings = []
        image_embeddings = []
        
        for i, product in enumerate(products):
            if (i + 1) % 10 == 0:
                logger.info(f"Processing product {i+1}/{len(products)}")
            
            # Generate text embedding
            text = f"Name: {product.name}. Description: {product.description}. Brand: {product.brand}, Category: {product.category}"
            text_emb = embedding_service.get_text_embedding(text)
            text_embeddings.append(text_emb)
            
            # Generate image embedding
            image_emb = embedding_service.get_image_embedding(product.image_path)
            image_embeddings.append(image_emb)
            
            # Store product data
            product_in_db = ProductInDB(
                product_id=product.product_id,
                name=product.name,
                description=product.description,
                brand=product.brand,
                category=product.category,
                price=product.price,
                image_path=product.image_path,
                rating=product.rating,
                reviews=product.reviews,
                text_embedding=text_emb,
                image_embedding=image_emb
            )
            self.product_data[product.product_id] = product_in_db
            self.product_ids.append(product.product_id)

        # Add to FAISS indexes
        text_embeddings_np = np.array(text_embeddings, dtype=np.float32)
        image_embeddings_np = np.array(image_embeddings, dtype=np.float32)

        self.text_index.add(text_embeddings_np)
        self.image_index.add(image_embeddings_np)

        # Update mappings
        for i, pid in enumerate(self.product_ids):
            self.text_idx_to_product[i] = pid
            self.image_idx_to_product[i] = pid

        logger.info(f"Added {len(products)} products. Text index size: {self.text_index.ntotal}, Image index size: {self.image_index.ntotal}")

    def search_text(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        """Search by text query."""
        if self.text_index is None or self.text_index.ntotal == 0:
            logger.warning("Text index is empty")
            return []

        query_embedding = embedding_service.get_query_embedding(query)
        query_np = np.array([query_embedding], dtype=np.float32)

        scores, indices = self.text_index.search(query_np, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.product_ids):
                pid = self.product_ids[idx]
                results.append((pid, float(score)))

        return results

    def search_image(self, image_path: str, top_k: int) -> List[Tuple[str, float]]:
        """Search by image."""
        if self.image_index is None or self.image_index.ntotal == 0:
            logger.warning("Image index is empty")
            return []

        image_embedding = embedding_service.get_image_embedding(image_path)
        query_np = np.array([image_embedding], dtype=np.float32)

        scores, indices = self.image_index.search(query_np, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.product_ids):
                pid = self.product_ids[idx]
                results.append((pid, float(score)))

        return results

    def hybrid_search(self, query: str, image_path: str, top_k: int, alpha: float = 0.5) -> List[Tuple[str, float]]:
        """Combine text and image search."""
        text_results = self.search_text(query, top_k * 2) if query else []
        image_results = self.search_image(image_path, top_k * 2) if image_path else []

        # Merge and re-rank results
        combined_scores = {}
        
        for pid, score in text_results:
            combined_scores[pid] = combined_scores.get(pid, 0) + alpha * score
        
        for pid, score in image_results:
            combined_scores[pid] = combined_scores.get(pid, 0) + (1 - alpha) * score

        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def get_products_by_ids(self, product_ids: List[str]) -> List[ProductBase]:
        """Retrieve full product data by IDs."""
        products = []
        for pid in product_ids:
            if pid in self.product_data:
                products.append(self.product_data[pid])
        return products

    def save_index(self, save_dir: str):
        """Save index to disk."""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        if self.text_index is not None:
            faiss.write_index(self.text_index, os.path.join(save_dir, "text_index.faiss"))
            logger.info(f"Saved text index to {save_dir}/text_index.faiss")
        
        if self.image_index is not None:
            faiss.write_index(self.image_index, os.path.join(save_dir, "image_index.faiss"))
            logger.info(f"Saved image index to {save_dir}/image_index.faiss")

        # Save mappings
        with open(os.path.join(save_dir, "product_mappings.json"), "w") as f:
            json.dump({
                "product_ids": self.product_ids,
                "text_idx_to_product": self.text_idx_to_product,
                "image_idx_to_product": self.image_idx_to_product
            }, f)
        
        # Save product data (without embeddings to save space)
        product_data_simple = {
            pid: {
                "product_id": p.product_id,
                "name": p.name,
                "description": p.description,
                "brand": p.brand,
                "category": p.category,
                "price": p.price,
                "image_path": p.image_path,
                "rating": p.rating,
                "reviews": p.reviews
            }
            for pid, p in self.product_data.items()
        }
        with open(os.path.join(save_dir, "product_data.json"), "w") as f:
            json.dump(product_data_simple, f)
        
        logger.info(f"Saved all index files to {save_dir}")

    def load_index(self, load_dir: str):
        """Load index from disk."""
        text_index_path = os.path.join(load_dir, "text_index.faiss")
        image_index_path = os.path.join(load_dir, "image_index.faiss")
        mappings_path = os.path.join(load_dir, "product_mappings.json")
        product_data_path = os.path.join(load_dir, "product_data.json")

        if os.path.exists(text_index_path):
            self.text_index = faiss.read_index(text_index_path)
            logger.info(f"Loaded text index with {self.text_index.ntotal} vectors")

        if os.path.exists(image_index_path):
            self.image_index = faiss.read_index(image_index_path)
            logger.info(f"Loaded image index with {self.image_index.ntotal} vectors")

        if os.path.exists(mappings_path):
            with open(mappings_path, "r") as f:
                mappings = json.load(f)
                self.product_ids = mappings.get("product_ids", [])
                self.text_idx_to_product = mappings.get("text_idx_to_product", {})
                self.image_idx_to_product = mappings.get("image_idx_to_product", {})

        if os.path.exists(product_data_path):
            with open(product_data_path, "r") as f:
                product_data_simple = json.load(f)
                for pid, data in product_data_simple.items():
                    self.product_data[pid] = ProductInDB(**data)

        logger.info(f"Loaded {len(self.product_ids)} products from index")

    def clear(self):
        """Clear all indexes and data."""
        self.text_index = None
        self.image_index = None
        self.product_ids = []
        self.product_data = {}
        self.text_idx_to_product = {}
        self.image_idx_to_product = {}
        logger.info("Cleared vector store")


vector_store = VectorStore()