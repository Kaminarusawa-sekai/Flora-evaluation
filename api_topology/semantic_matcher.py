"""Semantic matching using embeddings."""

from typing import Dict, Any, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class SemanticMatcher:
    """Semantic field matching using embeddings."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        if not EMBEDDINGS_AVAILABLE:
            self.model = None
            return
        self.model = SentenceTransformer(model_name)
        self._cache = {}

    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get embedding for text with caching."""
        if not self.model:
            return None
        if text not in self._cache:
            self._cache[text] = self.model.encode(text, convert_to_numpy=True)
        return self._cache[text]

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        if not self.model:
            return 0.0

        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        if emb1 is None or emb2 is None:
            return 0.0

        # Cosine similarity
        dot_product = np.dot(emb1, emb2)
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def is_available(self) -> bool:
        """Check if semantic matching is available."""
        return self.model is not None
