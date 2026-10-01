"""
Strategy Document Ingestion Service for seeding standard hotel revenue policy contracts and SOPs.
"""
from typing import List
from app.rag.vector_store import vector_store_manager


class DocumentIngestionService:
    def seed_default_strategy_documents(self) -> None:
        """Seed initial hotel revenue SOPs and policy guidelines into vector store."""
        sop_doc = (
            "HOTEL REVENUE MANAGEMENT STANDARD OPERATING PROCEDURE (SOP)\n"
            "1. Occupancy Threshold Pricing: When forecast occupancy for a future stay date exceeds 85%, "
            "the revenue manager should implement dynamic rate increases of 15% to 25% over base price.\n"
            "2. Pickup Pace Monitoring: If 3-day pickup pace exceeds 10 rooms, trigger an immediate price review.\n"
            "3. Competitor Parity: Maintain room rate within -10% to +15% of the local 4-star competitor median.\n"
            "4. Min Rate Floor: Under no circumstances should any published room rate drop below ₹1,000 per night."
        )

        cancellation_doc = (
            "STANDARD CANCELLATION & REFUND POLICY CONTRACT\n"
            "1. Free Cancellation: Reservations cancelled up to 24 hours prior to standard check-in (14:00) "
            "are eligible for a 100% full refund.\n"
            "2. Late Cancellations: Cancellations within 24 hours of arrival incur a 1-night room charge penalty.\n"
            "3. No-Show Policy: No-shows will be charged 100% of the total reservation booking amount."
        )

        vector_store_manager.ingest_document(
            title="Revenue Management SOP",
            category="SOP",
            content=sop_doc,
            version="1.0.0",
        )
        vector_store_manager.ingest_document(
            title="Cancellation & Refund Policy",
            category="POLICY",
            content=cancellation_doc,
            version="1.0.0",
        )


ingestion_service = DocumentIngestionService()
