from fastapi import APIRouter
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.sources import router as sources_router
from backend.app.api.v1.fleet import router as fleet_router
from backend.app.api.v1.events import router as events_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.ws import router as ws_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(sources_router)
api_v1_router.include_router(fleet_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(ws_router)
