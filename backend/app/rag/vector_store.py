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
        """Load persisted document chunks from disk if available."""
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
            logger.info("vector_store_loaded_from_disk", path=str(self._storage_path), docs_count=len(loaded))
        except Exception as e:
            logger.warning("vector_store_load_failed", error=str(e))

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into character/word chunks of specified length with overlap.
        """
        words = text.split()
        if not words:
            return []

        chunks = []
        step = max(1, chunk_size - overlap)
        for i in range(0, len(words), step):
            chunk_words = words[i : i + chunk_size]
            chunks.append(" ".join(chunk_words))
        return chunks

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
                    "embedding": embed,
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
        self, query: str, hotel_id: Optional[int] = None, top_k: int = 3
    ) -> List[DocumentChunkResponse]:
        """
        Execute cosine similarity search over vectorized document chunks.
        """
        if not self._docs_in_memory:
            return []

        query_embed = embedding_generator.generate_embeddings([query])[0]
        results = []

        target_hid = int(hotel_id) if hotel_id is not None else None

        for doc in self._docs_in_memory:
            doc_hid = int(doc["hotel_id"]) if doc.get("hotel_id") is not None else None
            if target_hid and doc_hid and doc_hid != target_hid:
                continue

            doc_embed = doc["embedding"]
            if isinstance(doc_embed, list):
                doc_embed = np.array(doc_embed, dtype=np.float32)
            
            # Cosine similarity
            sim = float(np.dot(query_embed, doc_embed))
            results.append((sim, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:top_k]

        return [
            DocumentChunkResponse(
                document_id=doc["document_id"],
                title=doc["title"],
                category=doc["category"],
                chunk=doc["chunk"],
                score=round(float(sim), 4),
                source=f"{doc['title']} (v{doc['version']})",
            )
            for sim, doc in top_results
        ]


vector_store_manager = VectorStoreManager()

