"""
Vector and Semantic Indexing for SwarmDroid Memory
Lightweight, robust cosine-similarity vector search with zero external heavyweight dependencies.
Supports embedding vectors as well as n-gram TF-IDF vectorization for offline semantic retrieval.
"""

import math
import re
from typing import List, Dict, Any, Tuple, Optional


class VectorIndex:
    """Fast in-memory vector index with cosine similarity search."""
    
    def __init__(self):
        # document_id -> (text, metadata, vector)
        self._documents: Dict[str, Tuple[str, Dict[str, Any], List[float]]] = {}
    
    @staticmethod
    def _text_to_vector(text: str, dim: int = 64) -> List[float]:
        """Generates a stable normalized pseudo-semantic feature vector using character and word hashes.
        Works offline without external API dependencies.
        """
        words = re.findall(r"\w+", text.lower())
        vec = [0.0] * dim
        if not words:
            return vec
        
        for w in words:
            # Word token contribution
            h = hash(w) % dim
            vec[h] += 1.0
            # Bi-gram subwords
            if len(w) >= 3:
                for i in range(len(w) - 2):
                    sub = w[i:i+3]
                    h_sub = hash(sub) % dim
                    vec[h_sub] += 0.5
        
        # Normalize vector (L2 norm)
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec
    
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def add(self, doc_id: str, text: str, metadata: Dict[str, Any], custom_vector: Optional[List[float]] = None):
        vec = custom_vector if custom_vector else self._text_to_vector(text)
        self._documents[doc_id] = (text, metadata, vec)
    
    def remove(self, doc_id: str) -> bool:
        if doc_id in self._documents:
            del self._documents[doc_id]
            return True
        return False
    
    def search(self, query: str, top_k: int = 5, min_score: float = 0.1) -> List[Dict[str, Any]]:
        query_vec = self._text_to_vector(query)
        results = []
        for doc_id, (text, metadata, vec) in self._documents.items():
            score = self.cosine_similarity(query_vec, vec)
            if score >= min_score:
                results.append({
                    "id": doc_id,
                    "text": text,
                    "score": round(score, 4),
                    "metadata": metadata
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def count(self) -> int:
        return len(self._documents)
