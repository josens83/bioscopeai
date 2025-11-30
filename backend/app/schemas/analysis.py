from pydantic import BaseModel, Field
from typing import Optional, List, Any
from app.models.analysis import AnalysisType
from app.schemas.base import BaseDBSchema


class AnalysisCreate(BaseModel):
    """분석 생성 스키마"""

    analysis_type: AnalysisType = Field(..., description="분석 유형", example="summary")
    paper_id: Optional[int] = Field(None, description="논문 ID (선택사항)", example=1)
    query: Optional[str] = Field(None, description="질문 쿼리 (Q&A 타입)", example="What are the main findings?")
    compared_paper_ids: Optional[List[int]] = Field(None, description="비교할 논문 ID 목록 (비교 타입)", example=[1, 2, 3])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "analysis_type": "summary",
                    "paper_id": 1
                },
                {
                    "analysis_type": "qa",
                    "paper_id": 1,
                    "query": "What are the key findings of this study?"
                },
                {
                    "analysis_type": "comparison",
                    "compared_paper_ids": [1, 2, 3]
                }
            ]
        }
    }


class AnalysisResponse(BaseDBSchema):
    """분석 응답 스키마"""
    # id, created_at, updated_at 자동 상속

    user_id: int = Field(..., description="사용자 ID", example=1)
    paper_id: Optional[int] = Field(None, description="논문 ID", example=1)
    analysis_type: AnalysisType = Field(..., description="분석 유형", example="summary")
    query: Optional[str] = Field(None, description="질문 쿼리", example="What are the main findings?")
    result: Any = Field(..., description="분석 결과")
    compared_paper_ids: Optional[List[int]] = Field(None, description="비교한 논문 ID 목록", example=[1, 2, 3])
    processing_time: Optional[int] = Field(None, description="처리 시간 (밀리초)", example=2500)
    tokens_used: Optional[int] = Field(None, description="사용된 토큰 수", example=1500)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "paper_id": 1,
                    "analysis_type": "summary",
                    "query": None,
                    "result": {
                        "summary": "This study demonstrates...",
                        "key_points": ["Point 1", "Point 2"]
                    },
                    "compared_paper_ids": None,
                    "processing_time": 2500,
                    "tokens_used": 1500,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ]
        }
    }


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
