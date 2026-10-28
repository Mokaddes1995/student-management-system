import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import text

from app.api.routes.students import router as students_router
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Student Management System")

    yield

    logger.info("Shutting down Student Management System")


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Student Management System",
    description="A REST API for managing students and academic records.",
    version="0.3.0",
    lifespan=lifespan,
)

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database schema is managed through Alembic migrations.
    yield


app = FastAPI(
    title="Student Management System",
    description="A REST API for managing students and academic records.",
    version="0.4.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(students_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Student Management System",
        "status": "running",
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "Request failed: request_id=%s method=%s path=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed",
        extra={
            "event": "request_completed",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )

    return response


app.include_router(students_router)


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from None

    return {
        "status": "healthy",
        "database": "connected",
    }
