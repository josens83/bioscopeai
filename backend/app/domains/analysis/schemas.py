"""
Analysis Domain Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from app.models.analysis import AnalysisType
from app.schemas.base import BaseDBSchema


class AnalysisCreate(BaseModel):
    analysis_type: AnalysisType = Field(..., description="분석 유형")
    paper_id: Optional[int] = Field(None, description="논문 ID")
    query: Optional[str] = Field(None, description="질문")
    compared_paper_ids: Optional[List[int]] = Field(None, description="비교 논문 IDs")


class AnalysisResponse(BaseDBSchema):
    user_id: int
    paper_id: Optional[int]
    analysis_type: AnalysisType
    query: Optional[str]
    result: Any
    compared_paper_ids: Optional[List[int]]
    processing_time: Optional[int]
    tokens_used: Optional[int]

    model_config = {"from_attributes": True}


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
    paper_id: Optional[int] = None
    k: int = Field(default=5, ge=1, le=20)


class ComparisonRequest(BaseModel):
    paper_ids: List[int] = Field(..., min_items=2, max_items=10)
