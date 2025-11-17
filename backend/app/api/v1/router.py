from fastapi import APIRouter
from app.api.v1.endpoints import auth, papers, analysis, subscriptions, health, admin, usage

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(papers.router, prefix="/papers", tags=["papers"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscription"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
