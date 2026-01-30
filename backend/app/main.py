import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routes import (
    auth_routes,
    paper_routes,
    project_routes,
    search_routes,
    user_routes,
)
from app.workers.queues.conversion_queue import ConversionQueue

# ---------------------------------------------------------
# Configure Logging
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("inquiro")


# ---------------------------------------------------------
# Lifespan Event Handlers (Modern FastAPI)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    """Initialize and tear down application resources."""

    logger.info("🚀 Starting Inquiro API in '%s' mode...", settings.ENVIRONMENT)
    if settings.ENVIRONMENT == "dev":
        await init_db()  # Auto-create tables only in dev

    # Start PDF conversion workers
    queue = ConversionQueue.get_instance()
    await queue.start_workers()

    logger.info("✅ Startup complete.")

    yield

    logger.info("🛑 Shutting down Inquiro API...")

    # Stop conversion workers
    await queue.stop_workers()

    logger.info("👋 Shutdown complete.")


# ---------------------------------------------------------
# Initialize FastAPI
# ---------------------------------------------------------
app = FastAPI(
    title="Inquiro API",
    description="AI-powered research discovery backend for Inquiro.",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------
# Development-only CORS configuration
# ---------------------------------------------------------
if settings.ENVIRONMENT == "dev":
    logger.info("🌐 Enabling CORS for local development...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(search_routes.router)
app.include_router(project_routes.router)
app.include_router(paper_routes.router)
