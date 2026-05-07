from fastapi import APIRouter

from api.routes.admin import router as admin_router
from api.routes.floats import router as floats_router
from api.routes.health import router as health_router
from api.routes.query import router as query_router
from api.webhooks import router as webhook_router


api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(webhook_router)
api_router.include_router(floats_router)
api_router.include_router(query_router)
api_router.include_router(admin_router)
