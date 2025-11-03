import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import init_db
from app.routes import user_routes, auth_routes

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
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Starting Inquiro API in '{settings.ENVIRONMENT}' mode...")
    if settings.ENVIRONMENT == "dev":
        init_db()  # Auto-create tables only in dev
    logger.info("✅ Startup complete.")

    yield

    logger.info("🛑 Shutting down Inquiro API...")
    logger.info("👋 Shutdown complete.")


# ---------------------------------------------------------
# Initialize FastAPI
# ---------------------------------------------------------
app = FastAPI(
    title="Inquiro API",
    description="AI-powered research discovery backend for Inquiro.",
    version="0.1.0",
    lifespan=lifespan
)


# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
