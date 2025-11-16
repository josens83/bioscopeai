from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AnalysisType(str, enum.Enum):
    """분석 타입"""

    SUMMARY = "summary"  # 논문 요약
    COMPARISON = "comparison"  # 논문 비교
    QA = "qa"  # 질의응답
    TREND = "trend"  # 트렌드 분석


class Analysis(Base):
    """분석 결과 모델"""

    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=True)

    # 분석 정보
    analysis_type = Column(Enum(AnalysisType), nullable=False)
    query = Column(Text, nullable=True)  # 사용자 질문 (QA의 경우)
    result = Column(JSON, nullable=False)  # 분석 결과 (JSON 형태)

    # 비교 분석의 경우 여러 논문 ID
    compared_paper_ids = Column(JSON, nullable=True)  # [1, 2, 3, ...]

    # 메타 정보
    processing_time = Column(Integer, nullable=True)  # 처리 시간 (초)
    tokens_used = Column(Integer, nullable=True)  # 사용된 토큰 수
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 관계
    user = relationship("User", back_populates="analyses")
    paper = relationship("Paper", back_populates="analyses")
