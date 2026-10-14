"""
Vector Store Manager implementing token-based chunking, ChromaDB storage, and semantic search retrieval.
"""
import uuid
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.rag.embeddings import embedding_generator
from app.schemas.rag import DocumentChunkResponse
from app.core.logging import get_logger

import json
import os
from pathlib import Path
import numpy as np

logger = get_logger("app.rag.vector_store")


class VectorStoreManager:
    """Manages document chunking, vector indexing, and semantic similarity search with persistent storage."""

    def __init__(self):
        self._docs_in_memory: List[Dict[str, Any]] = []
        self._storage_path = Path(__file__).parent / "data" / "vector_store.json"
        self._load_from_disk()

    def _save_to_disk(self):
        """Save vectorized document chunks to disk for persistence across backend restarts."""
        try:
            os.makedirs(self._storage_path.parent, exist_ok=True)
            serializable_docs = []
            for doc in self._docs_in_memory:
                d = dict(doc)
                if isinstance(d.get("embedding"), np.ndarray):
                    d["embedding"] = d["embedding"].tolist()
                elif isinstance(d.get("embedding"), list):
                    d["embedding"] = [float(x) for x in d["embedding"]]
                serializable_docs.append(d)
            
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(serializable_docs, f, indent=2)
            logger.info("vector_store_persisted", path=str(self._storage_path), docs_count=len(serializable_docs))
        except Exception as e:
            logger.warning("vector_store_save_failed", error=str(e))

    def _load_from_disk(self):
        """Load persisted document chunks from disk and ensure embeddings are up to date."""
        if not self._storage_path.exists():
            return
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                raw_docs = json.load(f)
            loaded = []
            for doc in raw_docs:
                if "embedding" in doc and doc["embedding"]:
                    doc["embedding"] = np.array(doc["embedding"], dtype=np.float32)
                loaded.append(doc)
            self._docs_in_memory = loaded
            # Recompute semantic embeddings to guarantee high precision
            self.recompute_all_embeddings()
            logger.info("vector_store_loaded_from_disk", path=str(self._storage_path), docs_count=len(loaded))
        except Exception as e:
            logger.warning("vector_store_load_failed", error=str(e))

    def recompute_all_embeddings(self):
        """Re-generate semantic embeddings for all in-memory chunks and persist."""
        if not self._docs_in_memory:
            return
        chunks = [d["chunk"] for d in self._docs_in_memory]
        embeddings = embedding_generator.generate_embeddings(chunks)
        for doc, embed in zip(self._docs_in_memory, embeddings):
            doc["embedding"] = np.array(embed, dtype=np.float32)
        self._save_to_disk()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into chunks of specified word length while preserving newlines and structure.
        """
        if not text or not text.strip():
            return []

        words = text.split()
        if len(words) <= chunk_size:
            return [text.strip()]

        # For long documents, break into line-aware chunks preserving formatting
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        chunks = []
        current_chunk = []
        current_words = 0

        for line in lines:
            line_words = len(line.split())
            if current_words + line_words > chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = current_chunk[-max(1, overlap // 20):]
                current_words = sum(len(l.split()) for l in current_chunk)
            current_chunk.append(line)
            current_words += line_words

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks or [text.strip()]

    def ingest_document(
        self,
        title: str,
        category: str,
        content: str,
        hotel_id: Optional[int] = None,
        version: str = "1.0.0",
    ) -> List[str]:
        """
        Chunk, embed, and index a revenue strategy document or web page incrementally into vector store.
        If a document with the same title & hotel_id exists, update it incrementally without wiping other chunks.
        """
        target_hid = int(hotel_id) if hotel_id is not None else None

        # Incremental update: Remove previous chunks for the exact same document title & hotel_id
        self._docs_in_memory = [
            doc for doc in self._docs_in_memory
            if not (doc.get("title") == title and (int(doc["hotel_id"]) if doc.get("hotel_id") is not None else None) == target_hid)
        ]

        doc_id = f"doc_{uuid.uuid4().hex[:10]}"
        chunks = self.chunk_text(content, chunk_size=300, overlap=30)
        embeddings = embedding_generator.generate_embeddings(chunks)

        chunk_ids = []
        for idx, (chunk, embed) in enumerate(zip(chunks, embeddings)):
            cid = f"{doc_id}_c{idx}"
            chunk_ids.append(cid)
            self._docs_in_memory.append(
                {
                    "document_id": doc_id,
                    "chunk_id": cid,
                    "title": title,
                    "category": category,
                    "hotel_id": target_hid,
                    "version": version,
                    "chunk": chunk,
                    "embedding": np.array(embed, dtype=np.float32),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        self._save_to_disk()
        logger.info("document_ingested_incremental", title=title, hotel_id=target_hid, chunks_count=len(chunks))
        return chunk_ids

    def get_hotel_documents(self, hotel_id: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all indexed document chunks matching a specific hotel_id."""
        if not self._docs_in_memory:
            return []
        
        target_hid = int(hotel_id) if hotel_id is not None else None
        res = []
        for doc in self._docs_in_memory:
            doc_hid = int(doc["hotel_id"]) if doc.get("hotel_id") is not None else None
            if target_hid and doc_hid and doc_hid != target_hid:
                continue
            if category and doc.get("category") != category:
                continue
            res.append(doc)
        return res

    def search_similar(
        self, query: str, hotel_id: Optional[int] = None, top_k: int = 5
    ) -> List[DocumentChunkResponse]:
        """
        Execute hybrid semantic similarity and lexical relevance search over vectorized document chunks.
        """
        if not self._docs_in_memory:
            return []

        query_embed = np.array(embedding_generator.generate_embeddings([query])[0], dtype=np.float32)
        query_lower = query.lower()
        stop_words = {
            "what", "is", "the", "are", "do", "you", "have", "in", "for", "to",
            "of", "and", "a", "an", "this", "that", "these", "those", "how", "can",
            "me", "at", "by", "from", "on", "with", "about", "as", "offer", "offers",
            "tell", "show", "give", "please", "hotel"
        }
        query_words = [w for w in re.findall(r'[a-zA-Z0-9]+', query_lower) if w not in stop_words and len(w) >= 3]

        target_hid = int(hotel_id) if hotel_id is not None else None
        results = []

        for doc in self._docs_in_memory:
            doc_hid = int(doc["hotel_id"]) if doc.get("hotel_id") is not None else None
            if target_hid is not None and doc_hid is not None and doc_hid != target_hid:
                continue

            doc_embed = doc["embedding"]
            if isinstance(doc_embed, list):
                doc_embed = np.array(doc_embed, dtype=np.float32)

            # Cosine similarity
            cos_sim = float(np.dot(query_embed, doc_embed))
            cos_sim = max(0.0, min(1.0, cos_sim))

            # Lexical keyword & topic match
            doc_text = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('chunk', '')}".lower()
            keyword_score = 0.0
            if query_words:
                matched_kw = sum(1 for kw in query_words if kw in doc_text)
                keyword_score = matched_kw / len(query_words)

            # Concept boosts & penalties to guarantee appropriate topical match
            concept_boost = 0.0
            if any(k in query_lower for k in ["amenit", "facilit", "pool", "gym", "wifi", "parking", "service"]):
                if any(k in doc_text for k in ["amenit", "facilit", "pool", "gym", "wifi", "parking"]):
                    concept_boost = 0.35
                elif "holiday" in doc.get("category", "").lower() or "holiday" in doc.get("title", "").lower():
                    # Strongly penalize holiday documents when asking about hotel amenities
                    concept_boost = -0.50

            elif any(k in query_lower for k in ["room", "suite", "bed", "inventory", "category"]):
                if any(k in doc_text for k in ["room", "suite", "inventory", "deluxe", "superior"]):
                    concept_boost = 0.35

            elif any(k in query_lower for k in ["din", "restaurant", "food", "breakfast", "buffet"]):
                if any(k in doc_text for k in ["restaurant", "dining", "cuisine", "buffet", "food"]):
                    concept_boost = 0.35

            elif any(k in query_lower for k in ["competitor", "rate", "price", "rival", "benchmark"]):
                if any(k in doc_text for k in ["competitor", "rate", "benchmark", "median"]):
                    concept_boost = 0.35

            elif any(k in query_lower for k in ["holiday", "festival", "diwali", "pongal"]):
                if any(k in doc_text for k in ["holiday", "festival", "observance"]):
                    concept_boost = 0.35

            # Property-specific boost
            hotel_boost = 0.05 if (target_hid is not None and doc_hid == target_hid) else 0.0

            # Final hybrid score: normalized between 0.0 and 1.0
            final_score = (0.50 * cos_sim) + (0.35 * keyword_score) + concept_boost + hotel_boost
            final_score = max(0.0, min(0.99, final_score))

            # Filter out irrelevant documents
            if final_score >= 0.25:
                results.append((final_score, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:top_k]

        return [
            DocumentChunkResponse(
                document_id=doc["document_id"],
                title=doc["title"],
                category=doc.get("category", "General"),
                chunk=doc["chunk"],
                content=doc["chunk"],
                score=round(float(score), 4),
                similarity_score=round(float(score), 4),
                source=f"{doc['title']} (v{doc.get('version', '1.0.0')})",
            )
            for score, doc in top_results
        ]


vector_store_manager = VectorStoreManager()

