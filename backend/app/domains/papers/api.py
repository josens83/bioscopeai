"""
Papers Domain API Router
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.auth.dependencies import get_db, get_current_user
from app.domains.auth.models import User
from app.core.rate_limiting import limiter, RateLimits
from .service import PaperService
from .schemas import PaperSearch, PaperCreate, PaperResponse, PaperUpdate
from .exceptions import InvalidPDFException

router = APIRouter()


@router.post("/search", response_model=List[dict])
@limiter.limit(RateLimits.API_READ)
async def search_papers(
    request: Request,
    search: PaperSearch,
    current_user: User = Depends(get_current_user),
):
    """
    PubMed에서 논문 검색

    - 캐싱 지원 (1시간)
    - 최대 100개 결과
    - 정렬: relevance, date
    """
    return await PaperService.search_pubmed(
        query=search.query,
        max_results=search.max_results,
        sort=search.sort,
    )


@router.post("/", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.API_WRITE)
async def create_paper(
    request: Request,
    paper_in: PaperCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    논문 저장 (PubMed 또는 수동 입력)

    - 사용량 추적
    - DOI 중복 확인
    - 벡터 스토어 자동 추가 (full_text 있는 경우)
    """
    return await PaperService.create_paper(db, paper_in, current_user.id)


@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.API_WRITE)
async def upload_paper(
    request: Request,
    file: UploadFile = File(...),
    title: str = None,
    authors: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PDF 업로드

    - 사용량 추적
    - PDF 텍스트 자동 추출
    - 메타데이터 자동 추출
    - 벡터 스토어 자동 추가
    """
    # 파일 형식 확인
    if not file.filename.endswith(".pdf"):
        raise InvalidPDFException()

    file_content = await file.read()
    return await PaperService.upload_pdf(
        db, current_user.id, file_content, file.filename, title, authors
    )


@router.get("/", response_model=List[PaperResponse])
@limiter.limit(RateLimits.API_READ)
async def get_papers(
    request: Request,
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    내 논문 목록 조회

    - 최신순 정렬
    - 페이지네이션 지원
    """
    return await PaperService.get_papers(db, current_user.id, skip, limit)


@router.get("/{paper_id}", response_model=PaperResponse)
@limiter.limit(RateLimits.API_READ)
async def get_paper(
    request: Request,
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    논문 상세 조회

    - 본인 소유 논문만 조회 가능
    """
    return await PaperService.get_paper(db, paper_id, current_user.id)


@router.patch("/{paper_id}", response_model=PaperResponse)
@limiter.limit(RateLimits.API_WRITE)
async def update_paper(
    request: Request,
    paper_id: int,
    paper_update: PaperUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    논문 정보 업데이트

    - 제목, 저자, 초록, 키워드 수정 가능
    """
    return await PaperService.update_paper(db, paper_id, current_user.id, paper_update)


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(RateLimits.API_WRITE)
async def delete_paper(
    request: Request,
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    논문 삭제

    - PDF 파일도 함께 삭제
    - 관련 분석 결과도 삭제 (CASCADE)
    """
    await PaperService.delete_paper(db, paper_id, current_user.id)
