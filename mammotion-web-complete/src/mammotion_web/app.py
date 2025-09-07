from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .core.logging import setup_logging
from .routers import auth_router, devices_router, ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    setup_logging(settings)
    logging.getLogger(__name__).info("Mammotion Web starting up")
    yield
    # Shutdown
    logging.getLogger(__name__).info("Mammotion Web shutting down")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title="Mammotion Web", lifespan=lifespan)

    # Sessions
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="mammotion_session",
        https_only=False,  # For development
        same_site="lax",
    )

    # CORS (if configured)
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Static files (create directory if it doesn't exist)
    static_dir = settings.STATIC_DIR
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Routers
    app.include_router(auth_router.router)
    app.include_router(devices_router.router)
    app.include_router(ws_router.router)

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.get("/ready")
    async def ready():
        return {"ready": True}

    return app


app = create_app()
