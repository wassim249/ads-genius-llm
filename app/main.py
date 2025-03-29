"""Main application file for the BERT model serving API."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app

from app.api.routes import router as api_router
from app.core.app_logging import setup_logging
from app.core.config import Settings, get_settings
from app.core.queue import get_queue, init_queue

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Lifespan for the application."""
    # Startup
    setup_logging()
    logger.info("Application starting up")
    settings = get_settings()
    init_queue(settings.MAX_PARALLEL_REQUESTS)
    logger.info(f"Initialized request queue with max {settings.MAX_PARALLEL_REQUESTS} parallel requests")
    yield
    # Shutdown
    logger.info("Application shutting down")


def create_application() -> FastAPI:
    """Create the FastAPI application."""
    settings = Settings()

    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production-ready BERT model serving API",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Setup CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add prometheus metrics
    metrics_app = make_asgi_app()
    application.mount("/metrics", metrics_app)

    # Mount static files
    application.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Include API router
    application.include_router(api_router, prefix="/api")

    # Add middleware to handle queue status
    @application.middleware("http")
    async def add_queue_headers(request, call_next):
        response = await call_next(request)
        queue = get_queue()
        response.headers["X-Queue-Size"] = str(queue.queue.qsize())
        response.headers["X-Active-Requests"] = str(queue.current_requests)
        return response

    # Serve index.html at root
    @application.get("/")
    async def root():
        return FileResponse("app/static/index.html")

    return application


app = create_application()
