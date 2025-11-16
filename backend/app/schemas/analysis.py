from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from app.models.analysis import AnalysisType


class AnalysisCreate(BaseModel):
    """분석 생성 스키마"""

    analysis_type: AnalysisType
    paper_id: Optional[int] = None
    query: Optional[str] = None
    compared_paper_ids: Optional[List[int]] = None


class AnalysisResponse(BaseModel):
    """분석 응답 스키마"""

    id: int
    user_id: int
    paper_id: Optional[int] = None
    analysis_type: AnalysisType
    query: Optional[str] = None
    result: Any
    compared_paper_ids: Optional[List[int]] = None
    processing_time: Optional[int] = None
    tokens_used: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionRequest(BaseModel):
    """질문 요청 스키마"""

    question: str = Field(..., min_length=1)
    paper_id: Optional[int] = None
    k: int = Field(default=5, ge=1, le=20)


class ComparisonRequest(BaseModel):
    """비교 분석 요청 스키마"""

    paper_ids: List[int] = Field(..., min_items=2, max_items=10)
