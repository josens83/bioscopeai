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

    question: str = Field(..., min_length=1, description="질문", example="What are the main findings of this study?")
    paper_id: Optional[int] = Field(None, description="특정 논문 ID (선택사항)", example=1)
    k: int = Field(default=5, ge=1, le=20, description="검색할 문서 청크 수", example=5)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What are the key applications of CRISPR technology?",
                    "paper_id": 1,
                    "k": 5
                }
            ]
        }
    }


class ComparisonRequest(BaseModel):
    """비교 분석 요청 스키마"""

    paper_ids: List[int] = Field(..., min_items=2, max_items=10, description="비교할 논문 ID 리스트 (2-10개)", example=[1, 2, 3])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "paper_ids": [1, 2, 3]
                }
            ]
        }
    }
