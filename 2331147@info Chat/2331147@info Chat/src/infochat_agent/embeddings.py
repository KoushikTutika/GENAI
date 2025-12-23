"""Embedding functionality using sentence-transformers"""

import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from .config import config

class EmbeddingModel:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.embedding_model
        self.model = SentenceTransformer(self.model_name)
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into embeddings"""
        return self.model.encode(texts, show_progress_bar=True)
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text"""
        return self.model.encode([text])[0]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()