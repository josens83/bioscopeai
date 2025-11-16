from fastapi import APIRouter
from app.api.v1.endpoints import auth, papers, analysis, subscriptions

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(papers.router, prefix="/papers", tags=["논문"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["분석"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["구독"])
