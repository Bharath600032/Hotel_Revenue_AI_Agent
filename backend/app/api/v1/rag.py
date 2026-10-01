"""
RAG Knowledge Base REST API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.rag import (
    DocumentUploadRequest,
    SearchQueryRequest,
    SearchQueryResponse,
    ScrapeWebsiteRequest,
)
from app.rag.vector_store import vector_store_manager
from app.rag.website_scraper import website_scraper_service
from app.api.deps import get_current_user, require_roles, get_db
from sqlalchemy.orm import Session
from app.models.user import User

router = APIRouter(prefix="/rag", tags=["RAG Knowledge Base"])


@router.post("/documents/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    payload: DocumentUploadRequest,
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager"])),
):
    """Upload and vectorize a revenue strategy document or SOP policy."""
    chunk_ids = vector_store_manager.ingest_document(
        title=payload.title,
        category=payload.category,
        content=payload.content,
        hotel_id=payload.hotel_id,
        version=payload.version,
    )
    return {
        "status": "INGESTED",
        "title": payload.title,
        "category": payload.category,
        "chunks_created": len(chunk_ids),
        "chunk_ids": chunk_ids,
    }


@router.post("/documents/scrape-url", status_code=status.HTTP_201_CREATED)
async def scrape_website_url(
    payload: ScrapeWebsiteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager"])),
):
    """Crawl hotel website URL + sublinks, extract content, and store in vector database."""
    res = website_scraper_service.crawl_and_ingest_website(
        url=payload.url,
        hotel_id=payload.hotel_id,
        max_sublinks=payload.max_sublinks,
        db=db,
    )
    return {
        "status": "CRAWLED_AND_INDEXED",
        "target_url": res["target_url"],
        "pages_crawled_count": res["pages_crawled_count"],
        "total_chunks_indexed": res["total_chunks_indexed"],
        "discovered_room_types": res.get("discovered_room_types", []),
        "pages": res["pages"],
    }



@router.post("/search", response_model=SearchQueryResponse)
async def search_knowledge_base(
    payload: SearchQueryRequest,
    current_user: User = Depends(require_roles(["Administrator", "Revenue Manager", "Hotel Manager", "Analyst", "Read-only User"])),
):
    """Execute semantic vector similarity search over strategy documents and scraped website content."""
    results = vector_store_manager.search_similar(
        query=payload.query, hotel_id=payload.hotel_id, top_k=payload.top_k
    )
    return SearchQueryResponse(
        query=payload.query,
        results_count=len(results),
        results=results,
    )

