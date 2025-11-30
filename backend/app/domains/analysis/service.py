"""
Analysis Domain Service
"""
import time
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.usage_service import UsageService
from .models import Analysis, AnalysisType
from .rag import rag_pipeline, vectorstore_service


class AnalysisService:
    """분석 서비스"""

    @staticmethod
    async def question_answer(db: AsyncSession, user_id: int, question: str, paper_id: int = None, k: int = 5) -> Analysis:
        """RAG 기반 질의응답"""
        await UsageService.check_and_increment(db, user_id, "rag_query")
        
        start = time.time()
        result = await rag_pipeline.answer_question(question, paper_id, k)
        processing_time = int((time.time() - start) * 1000)

        analysis = Analysis(
            user_id=user_id,
            paper_id=paper_id,
            analysis_type=AnalysisType.QA,
            query=question,
            result=result,
            processing_time=processing_time
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis

    @staticmethod
    async def summarize_paper(db: AsyncSession, user_id: int, paper_id: int) -> Analysis:
        """논문 요약"""
        await UsageService.check_and_increment(db, user_id, "summary")
        
        from app.domains.papers.models import Paper
        result = await db.execute(select(Paper).where(Paper.id == paper_id))
        paper = result.scalar_one_or_none()
        
        if not paper:
            raise ValueError("Paper not found")
            
        start = time.time()
        summary_result = await rag_pipeline.summarize_paper(paper.full_text or paper.abstract, paper.title)
        processing_time = int((time.time() - start) * 1000)

        analysis = Analysis(
            user_id=user_id,
            paper_id=paper_id,
            analysis_type=AnalysisType.SUMMARY,
            result=summary_result,
            processing_time=processing_time
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis

    @staticmethod
    async def compare_papers(db: AsyncSession, user_id: int, paper_ids: List[int]) -> Analysis:
        """논문 비교"""
        await UsageService.check_and_increment(db, user_id, "comparison")
        
        from app.domains.papers.models import Paper
        result = await db.execute(select(Paper).where(Paper.id.in_(paper_ids)))
        papers = result.scalars().all()
        
        paper_data = [{"title": p.title, "abstract": p.abstract} for p in papers]
        
        start = time.time()
        comparison_result = await rag_pipeline.compare_papers(paper_data)
        processing_time = int((time.time() - start) * 1000)

        analysis = Analysis(
            user_id=user_id,
            analysis_type=AnalysisType.COMPARISON,
            compared_paper_ids=paper_ids,
            result=comparison_result,
            processing_time=processing_time
        )
        
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis
