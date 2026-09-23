from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.redis_client import close_redis
from app.worker import start_worker, stop_worker

from app.routers import auth
from app.routers import users
from app.routers import rooms

from app.websocket.chat import router as websocket_router


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # --------------------------------------------------------
    # STARTUP
    # --------------------------------------------------------

    print("Starting application...")

    # Initialize database
    await init_db()

    print("Database initialized.")

    # Start Redis worker
    worker_task = await start_worker()

    print("Redis worker started.")

    try:

        yield

    finally:

        # ----------------------------------------------------
        # SHUTDOWN
        # ----------------------------------------------------

        print("Shutting down application...")

        # Stop Redis worker
        await stop_worker(worker_task)

        # Close Redis connection
        await close_redis()

        print("Application shutdown complete.")


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Real-Time Messaging System",
    version="1.0.0",
    description=(
        "A real-time messaging system built with "
        "FastAPI, WebSockets, Redis Streams, "
        "PostgreSQL and JWT authentication."
    ),
    lifespan=lifespan,
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    auth.router
)

app.include_router(
    users.router
)

app.include_router(
    rooms.router
)


# ============================================================
# WEBSOCKET ROUTER
# ============================================================

app.include_router(
    websocket_router
)


# ============================================================
# FRONTEND
# ============================================================

if not FRONTEND_DIR.exists():

    raise RuntimeError(
        f"Frontend directory not found: {FRONTEND_DIR}"
    )


if not (FRONTEND_DIR / "index.html").exists():

    raise RuntimeError(
        f"Frontend index.html not found: "
        f"{FRONTEND_DIR / 'index.html'}"
    )


app.mount(
    "/",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True,
    ),
    name="frontend",
)