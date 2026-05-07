from fastapi import FastAPI

from api.router import api_router
from core.config import get_settings
from core.logging import configure_logging
from core.middleware import RequestIdMiddleware
from core.telemetry import configure_metrics
from db.session import init_db


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="FastAPI backend for Project Leviathan.",
)
app.add_middleware(RequestIdMiddleware)
app.include_router(api_router)
configure_metrics(app)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
