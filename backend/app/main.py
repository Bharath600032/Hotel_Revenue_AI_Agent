"""
Main FastAPI Application Entrypoint with structured logging, exception handlers, and security middleware.
"""
import warnings
warnings.filterwarnings("ignore", message=".*Python 3.8 is no longer supported.*")

import uuid
import time
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import HotelRevenueException
from app.core.security_headers import SecurityHeadersMiddleware
from app.api.v1.router import api_router
from contextlib import asynccontextmanager

# Initialize structured logging
setup_logging()
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Auto-seed database tables and Super Admin account on application startup."""
    from app.db.session import SessionLocal
    from app.db.init_db import init_db
    try:
        db = SessionLocal()
        init_db(db)
        db.close()
        logger.info("startup_init_db_completed")
    except Exception as e:
        logger.warning("startup_init_db_failed", error=str(e))
    yield


app = FastAPI(
    title="Hotel Autonomous Revenue AI Agent API",
    description="Enterprise AI-powered autonomous hotel revenue management platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Security Headers & CORS Middleware setup
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_and_logging(request: Request, call_next):
    """Inject request correlation ID and log request execution metrics."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.time()
    logger.info(
        "http_request_started",
        path=request.url.path,
        method=request.method,
        request_id=request_id,
    )

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    logger.info(
        "http_request_finished",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration_seconds=round(process_time, 4),
        request_id=request_id,
    )
    return response


# Global Exception Handlers
@app.exception_handler(HotelRevenueException)
async def hotel_revenue_exception_handler(request: Request, exc: HotelRevenueException):
    """Handle custom application exceptions cleanly."""
    logger.warning(
        "domain_exception",
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic request validation errors."""
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters provided.",
                "details": {"errors": exc.errors()},
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle unhandled server exceptions safely without leaking tracebacks."""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        exc_info=True,
        path=request.url.path,
        request_id=getattr(request.state, "request_id", None),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please contact system administrator.",
            },
        },
    )


# Include API v1 routes
app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Hotel Autonomous Revenue AI Agent Backend",
        "version": "1.0.0",
        "mode": settings.APP_MODE,
        "is_demo_mode": settings.is_demo_mode,
        "llm_provider": settings.LLM_PROVIDER,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
