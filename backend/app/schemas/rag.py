"""
Pydantic v2 schemas for RAG Knowledge Base document ingestion and semantic search.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(default="SOP", description="SOP, CONTRACT, POLICY, STRATEGY")
    hotel_id: Optional[int] = Field(None, description="Optional property ID filter")
    content: str = Field(..., min_length=10, description="Full text document content")
    version: str = Field(default="1.0.0", max_length=50)


class DocumentChunkResponse(BaseModel):
    document_id: str
    title: str
    category: str
    chunk: str
    score: float
    source: str


class SearchQueryRequest(BaseModel):
    query: str = Field(..., min_length=2)
    hotel_id: Optional[int] = None
    top_k: int = Field(default=3, ge=1, le=10)


class SearchQueryResponse(BaseModel):
    query: str
    results_count: int
    results: List[DocumentChunkResponse]


class ScrapeWebsiteRequest(BaseModel):
    url: str = Field(..., description="Official hotel website URL to crawl")
    hotel_id: Optional[int] = Field(None, description="Associated hotel ID")
    max_sublinks: int = Field(default=8, ge=1, le=20, description="Max sublinks to crawl")

