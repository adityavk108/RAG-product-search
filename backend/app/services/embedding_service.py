import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text and image embeddings."""

    def __init__(self):
        self.text_model = None
        self.clip_model = None
        self.clip_processor = None
        self.device = "cpu"
        self.text_model_loaded = False
        self.clip_model_loaded = False
        self.clip_init_failed = False

    def initialize(self):
        """Initialize embedding models."""
        # Load text model
        if not self.text_model_loaded:
            logger.info("Loading text embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
            self.text_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("Text model loaded. Dimension: 384")
            self.text_model_loaded = True
        
        # Load CLIP model only if not already tried and failed
        if not self.clip_model_loaded and not self.clip_init_failed:
            logger.info("Loading CLIP image model...")
            try:
                self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-b-32")
                self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-b-32")
                self.clip_model.to(self.device)
                logger.info("CLIP model loaded. Dimension: 512")
                self.clip_model_loaded = True
            except Exception as e:
                logger.warning(f"Could not load CLIP model: {e}")
                logger.info("Using placeholder for image embeddings")
                self.clip_init_failed = True

    def get_text_embedding(self, text: str) -> List[float]:
        """Generate 384-dim text embedding."""
        if self.text_model is None:
            self.initialize()
        
        embedding = self.text_model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def get_image_embedding(self, image_path: str) -> List[float]:
        """Generate 512-dim image embedding."""
        if self.clip_model is None and not self.clip_init_failed:
            self.initialize()
        
        # Return placeholder if CLIP failed to load
        if self.clip_init_failed or self.clip_model is None:
            logger.warning(f"CLIP not available, using placeholder for image: {image_path}")
            return [0.0] * 512
        
        try:
            if not os.path.exists(image_path):
                logger.warning(f"Image file not found: {image_path}, using placeholder")
                return [0.0] * 512
            
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            inputs = self.clip_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            embedding = image_features[0].cpu().numpy()
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Failed to load image {image_path}: {e}")
            return [0.0] * 512

    def get_image_embedding_from_pil(self, image: Image.Image) -> List[float]:
        """Generate embedding from PIL Image."""
        if self.clip_model is None and not self.clip_init_failed:
            self.initialize()
        
        if self.clip_init_failed or self.clip_model is None:
            return [0.0] * 512
        
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            inputs = self.clip_processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
            
            embedding = image_features[0].cpu().numpy()
            embedding = embedding / np.linalg.norm(embedding)
            return embedding.tolist()
        except Exception as e:
            logger.warning(f"Failed to process PIL image: {e}")
            return [0.0] * 512

    def get_query_embedding(self, query: str) -> List[float]:
        """Generate query embedding for search."""
        return self.get_text_embedding(query)

    def process_text_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Process multiple texts efficiently."""
        if self.text_model is None:
            self.initialize()
        
        embeddings = self.text_model.encode(
            texts, 
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def process_image_batch(self, image_paths: List[str], batch_size: int = 16) -> List[List[float]]:
        """Process multiple images."""
        embeddings = []
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i+batch_size]
            batch_embeddings = [self.get_image_embedding(p) for p in batch_paths]
            embeddings.extend(batch_embeddings)
        return embeddings


embedding_service = EmbeddingService()