from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.models.analysis import Analysis, AnalysisType
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, QuestionRequest, ComparisonRequest
from app.rag.rag_pipeline import rag_pipeline
import time

router = APIRouter()


@router.post("/question", response_model=dict)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문에 대한 질문"""
    start_time = time.time()

    # paper_id가 제공된 경우 권한 확인
    if request.paper_id:
        result = await db.execute(
            select(Paper).where(
                Paper.id == request.paper_id,
                Paper.user_id == current_user.id
            )
        )
        paper = result.scalar_one_or_none()
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="논문을 찾을 수 없습니다",
            )

    # RAG 파이프라인으로 답변 생성
    result = await rag_pipeline.answer_question(
        question=request.question,
        paper_id=request.paper_id,
        k=request.k,
    )

    processing_time = int(time.time() - start_time)

    # 분석 기록 저장
    analysis = Analysis(
        user_id=current_user.id,
        paper_id=request.paper_id,
        analysis_type=AnalysisType.QA,
        query=request.question,
        result=result,
        processing_time=processing_time,
    )

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        **result,
    }


@router.post("/summarize/{paper_id}", response_model=dict)
async def summarize_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문 요약"""
    # 논문 조회
    result = await db.execute(
        select(Paper).where(
            Paper.id == paper_id,
            Paper.user_id == current_user.id
        )
    )
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="논문을 찾을 수 없습니다",
        )

    if not paper.full_text and not paper.abstract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="요약할 내용이 없습니다",
        )

    start_time = time.time()

    # 요약 생성
    text_to_summarize = paper.full_text or paper.abstract
    summary_result = await rag_pipeline.summarize_paper(
        paper_text=text_to_summarize,
        paper_title=paper.title,
    )

    processing_time = int(time.time() - start_time)

    # 분석 기록 저장
    analysis = Analysis(
        user_id=current_user.id,
        paper_id=paper_id,
        analysis_type=AnalysisType.SUMMARY,
        result=summary_result,
        processing_time=processing_time,
    )

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        **summary_result,
    }


@router.post("/compare", response_model=dict)
async def compare_papers(
    request: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """여러 논문 비교"""
    # 논문 조회
    result = await db.execute(
        select(Paper).where(
            Paper.id.in_(request.paper_ids),
            Paper.user_id == current_user.id
        )
    )
    papers = result.scalars().all()

    if len(papers) != len(request.paper_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="일부 논문을 찾을 수 없습니다",
        )

    if len(papers) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="최소 2개 이상의 논문이 필요합니다",
        )

    start_time = time.time()

    # 비교 분석
    paper_data = [
        {
            "title": p.title,
            "abstract": p.abstract or "",
            "authors": p.authors or "",
        }
        for p in papers
    ]

    comparison_result = await rag_pipeline.compare_papers(paper_data)

    processing_time = int(time.time() - start_time)

    # 분석 기록 저장
    analysis = Analysis(
        user_id=current_user.id,
        analysis_type=AnalysisType.COMPARISON,
        result=comparison_result,
        compared_paper_ids=request.paper_ids,
        processing_time=processing_time,
    )

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return {
        "analysis_id": analysis.id,
        **comparison_result,
    }


@router.get("/", response_model=List[AnalysisResponse])
async def list_analyses(
    skip: int = 0,
    limit: int = 20,
    analysis_type: AnalysisType = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """분석 기록 조회"""
    query = select(Analysis).where(Analysis.user_id == current_user.id)

    if analysis_type:
        query = query.where(Analysis.analysis_type == analysis_type)

    query = query.offset(skip).limit(limit).order_by(Analysis.created_at.desc())

    result = await db.execute(query)
    analyses = result.scalars().all()

    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """분석 상세 조회"""
    result = await db.execute(
        select(Analysis).where(
            Analysis.id == analysis_id,
            Analysis.user_id == current_user.id
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="분석 기록을 찾을 수 없습니다",
        )

    return analysis
