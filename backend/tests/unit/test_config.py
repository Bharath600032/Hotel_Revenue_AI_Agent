"""
Unit tests for application core settings and config loading.
"""
import pytest
from app.core.config import Settings


def test_default_settings_load():
    """Verify settings defaults and property helpers."""
    cfg = Settings(APP_MODE="DEMO")
    assert cfg.APP_MODE == "DEMO"
    assert cfg.is_demo_mode is True
    assert cfg.MAX_DAILY_PRICE_CHANGE_PCT == 0.20
    assert cfg.APPROVAL_THRESHOLD_PCT == 0.10
    assert "sqlite" in cfg.get_sqlalchemy_database_url


def test_production_mode_database_url():
    """Verify database URL generation for production mode settings."""
    cfg = Settings(
        APP_MODE="PRODUCTION",
        DATABASE_URL=None,
        DB_SERVER="db.hotel.internal",
        DB_NAME="ProdHotelDB",
        DB_USER="revenue_admin",
    )
    db_url = cfg.get_sqlalchemy_database_url
    assert "mssql+pyodbc://" in db_url
    assert "revenue_admin@" in db_url
    assert "ProdHotelDB" in db_url
