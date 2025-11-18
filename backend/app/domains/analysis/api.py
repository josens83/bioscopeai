"""
Analysis Domain API Router
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.auth.dependencies import get_db, get_current_user
from app.domains.auth.models import User
from app.core.rate_limiting import limiter, RateLimits
from .service import AnalysisService
from .schemas import QuestionRequest, ComparisonRequest, AnalysisResponse

router = APIRouter()


@router.post("/qa", response_model=AnalysisResponse)
@limiter.limit(RateLimits.API_WRITE)
async def question_answer(
    request: Request,
    qa_request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """RAG 기반 질의응답"""
    return await AnalysisService.question_answer(
        db, current_user.id, qa_request.question, qa_request.paper_id, qa_request.k
    )


@router.post("/summary/{paper_id}", response_model=AnalysisResponse)
@limiter.limit(RateLimits.API_HEAVY)
async def summarize_paper(
    request: Request,
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문 요약"""
    return await AnalysisService.summarize_paper(db, current_user.id, paper_id)


@router.post("/compare", response_model=AnalysisResponse)
@limiter.limit(RateLimits.API_HEAVY)
async def compare_papers(
    request: Request,
    comparison: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문 비교"""
    return await AnalysisService.compare_papers(db, current_user.id, comparison.paper_ids)
