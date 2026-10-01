"""
Unit tests for RAG Knowledge Base text chunking, vector indexing, and semantic search retrieval.
"""
import pytest
from app.rag.vector_store import vector_store_manager
from app.rag.ingestion import ingestion_service


def test_text_chunking():
    text = "Word " * 1000  # 1000 words
    chunks = vector_store_manager.chunk_text(text, chunk_size=300, overlap=30)
    assert len(chunks) >= 3


def test_ingest_and_search_rag_documents():
    # Seed default SOPs
    ingestion_service.seed_default_strategy_documents()

    # Search for occupancy strategy
    results = vector_store_manager.search_similar(
        query="What should we do when occupancy exceeds 85%?", top_k=2
    )

    assert len(results) >= 1
    assert "Revenue Management SOP" in results[0].source
    assert results[0].score > 0.0
