from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.paper import Paper
from app.schemas.paper import PaperSearch, PaperCreate, PaperResponse, PaperUpload
from app.services.pubmed_service import PubMedService
from app.services.pdf_service import pdf_service
from app.services.cache_service import cache
from app.services.usage_service import UsageService
from app.rag.vectorstore import vectorstore_service
from app.rag.rag_pipeline import rag_pipeline
import time

router = APIRouter()


@router.post("/search", response_model=List[dict])
async def search_papers(
    search: PaperSearch,
    current_user: User = Depends(get_current_user),
):
    """PubMed에서 논문 검색 (캐싱 지원)"""
    pubmed_service = PubMedService(cache=cache)
    papers = await pubmed_service.search_papers(
        query=search.query,
        max_results=search.max_results,
        sort=search.sort,
    )
    return papers


@router.post("/", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def create_paper(
    paper_in: PaperCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문 저장 (PubMed 또는 수동, 사용량 추적)"""
    # 사용량 확인 및 증가
    await UsageService.check_and_increment(db, current_user.id, "paper")

    # 논문 생성
    paper = Paper(
        user_id=current_user.id,
        title=paper_in.title,
        authors=paper_in.authors,
        abstract=paper_in.abstract,
        publication_date=paper_in.publication_date,
        journal=paper_in.journal,
        doi=paper_in.doi,
        pubmed_id=paper_in.pubmed_id,
        pdf_url=paper_in.pdf_url,
        full_text=paper_in.full_text,
        keywords=paper_in.keywords,
        source=paper_in.source or "manual",
    )

    db.add(paper)
    await db.commit()
    await db.refresh(paper)

    # 벡터 스토어에 추가 (full_text가 있는 경우)
    if paper.full_text:
        chunks = rag_pipeline.split_text(paper.full_text)
        metadata = [
            {"paper_id": paper.id, "title": paper.title, "chunk_index": i}
            for i in range(len(chunks))
        ]
        vectorstore_service.add_documents(chunks, metadata)

    return paper


@router.post("/upload", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def upload_paper(
    file: UploadFile = File(...),
    title: str = None,
    authors: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """PDF 업로드 (사용량 추적)"""
    # 사용량 확인 및 증가
    await UsageService.check_and_increment(db, current_user.id, "paper")

    # 파일 형식 확인
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF 파일만 업로드 가능합니다",
        )

    # 파일 저장
    file_content = await file.read()
    filename = f"{current_user.id}_{int(time.time())}_{file.filename}"
    file_path = pdf_service.save_uploaded_file(file_content, filename)

    # 텍스트 추출
    full_text = pdf_service.extract_text_from_pdf(file_path)
    if not full_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF에서 텍스트를 추출할 수 없습니다",
        )

    # 메타데이터 추출
    metadata = pdf_service.extract_metadata(file_path)

    # 논문 생성
    paper = Paper(
        user_id=current_user.id,
        title=title or metadata.get("title", file.filename),
        authors=authors or metadata.get("author", ""),
        full_text=full_text,
        pdf_path=file_path,
        source="upload",
    )

    db.add(paper)
    await db.commit()
    await db.refresh(paper)

    # 벡터 스토어에 추가
    chunks = rag_pipeline.split_text(full_text)
    chunk_metadata = [
        {"paper_id": paper.id, "title": paper.title, "chunk_index": i}
        for i in range(len(chunks))
    ]
    vectorstore_service.add_documents(chunks, chunk_metadata)

    return paper


@router.get("/", response_model=List[PaperResponse])
async def list_papers(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """사용자의 논문 목록"""
    result = await db.execute(
        select(Paper)
        .where(Paper.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Paper.created_at.desc())
    )
    papers = result.scalars().all()
    return papers


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문 상세 조회"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="논문을 찾을 수 없습니다",
        )

    return paper


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(
    paper_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """논문 삭제"""
    result = await db.execute(
        select(Paper).where(Paper.id == paper_id, Paper.user_id == current_user.id)
    )
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="논문을 찾을 수 없습니다",
        )

    # 파일 삭제
    if paper.pdf_path:
        pdf_service.delete_file(paper.pdf_path)

    # 벡터 스토어에서 삭제
    vectorstore_service.delete_by_paper_id(paper_id)

    # DB에서 삭제
    await db.delete(paper)
    await db.commit()
