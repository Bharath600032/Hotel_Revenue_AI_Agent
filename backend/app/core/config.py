"""
Core application configuration management using Pydantic Settings.
Supports dual DEMO and PRODUCTION operating modes.
"""
import os
from typing import List, Literal, Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # App Mode
    APP_MODE: Literal["DEMO", "PRODUCTION"] = Field(
        default="DEMO", description="Operating mode: DEMO or PRODUCTION"
    )

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server bind host")
    PORT: int = Field(default=8000, description="Server bind port")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Security & Auth
    SECRET_KEY: SecretStr = Field(
        default=SecretStr("super-secret-jwt-token-key-change-in-production-32bytes!"),
        description="JWT signing secret key",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=43200, description="Access token lifetime in minutes (30 days)"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token lifetime in days"
    )

    # Database Configuration
    DB_DRIVER: str = Field(
        default="ODBC Driver 18 for SQL Server", description="pyodbc DB driver"
    )
    DB_SERVER: str = Field(default="localhost", description="SQL Server host")
    DB_PORT: int = Field(default=1433, description="SQL Server port")
    DB_NAME: str = Field(default="HotelRevenueDB", description="Database name")
    DB_USER: str = Field(default="sa", description="Database username")
    DB_PASSWORD: SecretStr = Field(
        default=SecretStr("YourPassword123!"), description="Database password"
    )
    DATABASE_URL: Optional[str] = Field(
        default="sqlite:///./data/hotel_revenue_demo.db",
        description="SQLAlchemy database connection string override",
    )

    # Redis Cache (Optional for DEMO)
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_PASSWORD: Optional[SecretStr] = Field(
        default=None, description="Redis password"
    )

    # AI Provider Settings
    LLM_PROVIDER: Literal["claude", "gemini", "openai", "mock"] = Field(
        default="gemini", description="Selected LLM provider abstraction"
    )
    ANTHROPIC_API_KEY: Optional[SecretStr] = Field(default=None)
    GEMINI_API_KEY: Optional[SecretStr] = Field(default=None)
    OPENAI_API_KEY: Optional[SecretStr] = Field(default=None)

    # Vector DB (RAG) Settings
    CHROMA_DB_DIR: str = Field(
        default="./data/chroma_db", description="ChromaDB persistence folder"
    )
    EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2", description="SentenceTransformers embedding model"
    )

    # Business & Pricing Guardrail Defaults
    MAX_DAILY_PRICE_CHANGE_PCT: float = Field(
        default=0.20, description="Max daily price adjustment limit (+/- 20%)"
    )
    MAX_WEEKLY_PRICE_CHANGE_PCT: float = Field(
        default=0.35, description="Max weekly price adjustment limit (+/- 35%)"
    )
    APPROVAL_THRESHOLD_PCT: float = Field(
        default=0.10, description="Rate changes > 10% require human approval"
    )
    DEFAULT_MIN_RATE_FLOOR: float = Field(
        default=1000.0, description="Global minimum rate floor"
    )
    DEFAULT_MAX_RATE_CEILING: float = Field(
        default=50000.0, description="Global maximum rate ceiling"
    )

    # CORS Origins
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        description="Allowed CORS origin URIs",
    )

    @property
    def is_demo_mode(self) -> bool:
        """Check if application is running in DEMO mode."""
        return self.APP_MODE == "DEMO"

    @property
    def get_sqlalchemy_database_url(self) -> str:
        """
        Generate database connection URL for SQLAlchemy.
        Falls back to SQLite for DEMO mode if DATABASE_URL is set or SQL Server parameters are missing.
        Ensures relative SQLite paths resolve to absolute project root location.
        """
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("sqlite:///./"):
                # Anchor relative sqlite DB path to project root
                from pathlib import Path
                root_dir = Path(__file__).resolve().parent.parent.parent
                data_dir = root_dir / "data"
                data_dir.mkdir(parents=True, exist_ok=True)
                db_filename = self.DATABASE_URL.split("./")[-1]
                abs_db_path = (root_dir / db_filename).as_posix()
                return f"sqlite:///{abs_db_path}"
            return self.DATABASE_URL

        # SQL Server URL construction
        driver_encoded = self.DB_DRIVER.replace(" ", "+")
        password_val = self.DB_PASSWORD.get_secret_value() if self.DB_PASSWORD else ""
        return (
            f"mssql+pyodbc://{self.DB_USER}:{password_val}@"
            f"{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?"
            f"driver={driver_encoded}&Encrypt=no&TrustServerCertificate=yes"
        )


settings = Settings()

