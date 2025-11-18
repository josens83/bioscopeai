"""
Papers Domain Service - 비즈니스 로직
"""
import time
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.services.usage_service import UsageService
from .models import Paper
from .schemas import PaperCreate, PaperUpdate
from .services.pubmed import pubmed_service
from .services.pdf import pdf_service
from .exceptions import PaperNotFoundException, DuplicatePaperException, PDFProcessingException


class PaperService:
    """논문 서비스 - 논문 생성, 조회, 업데이트, 삭제"""

    @staticmethod
    async def search_pubmed(query: str, max_results: int = 20, sort: str = "relevance") -> List[dict]:
        """PubMed 검색"""
        return await pubmed_service.search_papers(query, max_results, sort)

    @staticmethod
    async def create_paper(db: AsyncSession, paper_in: PaperCreate, user_id: int) -> Paper:
        """논문 생성 (수동 또는 PubMed)"""
        # 사용량 확인 및 증가
        await UsageService.check_and_increment(db, user_id, "paper")

        # DOI 중복 확인
        if paper_in.doi:
            result = await db.execute(select(Paper).where(Paper.doi == paper_in.doi))
            if result.scalar_one_or_none():
                raise DuplicatePaperException(doi=paper_in.doi)

        # 논문 생성
        paper = Paper(
            user_id=user_id,
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

        # 벡터 스토어 추가는 Analysis 도메인에서 처리
        return paper

    @staticmethod
    async def upload_pdf(
        db: AsyncSession,
        user_id: int,
        file_content: bytes,
        filename: str,
        title: Optional[str] = None,
        authors: Optional[str] = None
    ) -> Paper:
        """PDF 업로드"""
        # 사용량 확인 및 증가
        await UsageService.check_and_increment(db, user_id, "paper")

        # 파일 저장
        unique_filename = f"{user_id}_{int(time.time())}_{filename}"
        file_path = pdf_service.save_uploaded_file(file_content, unique_filename)

        # 텍스트 추출
        full_text = pdf_service.extract_text_from_pdf(file_path)
        if not full_text:
            raise PDFProcessingException("PDF에서 텍스트를 추출할 수 없습니다")

        # 메타데이터 추출
        metadata = pdf_service.extract_metadata(file_path)

        # 논문 생성
        paper = Paper(
            user_id=user_id,
            title=title or metadata.get("title") or filename,
            authors=authors or metadata.get("author"),
            full_text=full_text,
            pdf_path=file_path,
            source="upload",
        )

        db.add(paper)
        await db.commit()
        await db.refresh(paper)

        return paper

    @staticmethod
    async def get_paper(db: AsyncSession, paper_id: int, user_id: int) -> Paper:
        """논문 조회 (본인 소유 확인)"""
        result = await db.execute(
            select(Paper).where(and_(Paper.id == paper_id, Paper.user_id == user_id))
        )
        paper = result.scalar_one_or_none()

        if not paper:
            raise PaperNotFoundException(paper_id=paper_id)

        return paper

    @staticmethod
    async def get_papers(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Paper]:
        """사용자의 논문 목록 조회"""
        result = await db.execute(
            select(Paper)
            .where(Paper.user_id == user_id)
            .order_by(Paper.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_paper(
        db: AsyncSession,
        paper_id: int,
        user_id: int,
        paper_update: PaperUpdate
    ) -> Paper:
        """논문 업데이트"""
        paper = await PaperService.get_paper(db, paper_id, user_id)

        # 업데이트
        update_data = paper_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(paper, field, value)

        await db.commit()
        await db.refresh(paper)

        return paper

    @staticmethod
    async def delete_paper(db: AsyncSession, paper_id: int, user_id: int):
        """논문 삭제"""
        paper = await PaperService.get_paper(db, paper_id, user_id)

        # PDF 파일 삭제
        if paper.pdf_path:
            pdf_service.delete_file(paper.pdf_path)

        await db.delete(paper)
        await db.commit()

    @staticmethod
    async def count_user_papers(db: AsyncSession, user_id: int) -> int:
        """사용자의 총 논문 수"""
        result = await db.execute(
            select(Paper).where(Paper.user_id == user_id)
        )
        return len(result.scalars().all())
