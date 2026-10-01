"""
Observability and Prometheus metric collectors for tracking API latencies and Agent executions.
"""
import time
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import engine


class MetricsCollector:
    """Collects application health metrics and database connection status."""

    @staticmethod
    def check_database_connection(db: Session) -> Dict[str, Any]:
        start = time.time()
        try:
            db.execute(text("SELECT 1"))
            latency_ms = round((time.time() - start) * 1000.0, 2)
            return {"status": "connected", "latency_ms": latency_ms}
        except Exception as exc:
            return {"status": "disconnected", "error": str(exc)}


metrics_collector = MetricsCollector()
