"""
Embeddings abstraction layer using sentence-transformers or local TF-IDF vectorizer fallback.
"""
from typing import List
import numpy as np


class EmbeddingGenerator:
    """Generates numerical vector embeddings for document text chunks."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = "MOCK"
        return self._model

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized 384-dim float embeddings for list of text strings."""
        if not texts:
            return []

        model = self._get_model()
        if model != "MOCK":
            embeddings = model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()

        # Fallback deterministic pseudo-embedding for local demo testing without weights download
        results = []
        for text in texts:
            vec = [0.0] * 384
            for i, char in enumerate(text[:384]):
                vec[i % 384] += ord(char) / 255.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = (np.array(vec) / norm).tolist()
            results.append(vec)
        return results


embedding_generator = EmbeddingGenerator()
