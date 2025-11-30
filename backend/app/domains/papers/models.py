"""
Papers Domain Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Paper(Base):
    """논문 모델"""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # 논문 메타데이터
    title = Column(String, nullable=False, index=True)
    authors = Column(Text, nullable=True)
    abstract = Column(Text, nullable=True)
    publication_date = Column(DateTime(timezone=True), nullable=True)
    journal = Column(String, nullable=True)
    doi = Column(String, nullable=True, unique=True, index=True)
    pubmed_id = Column(String, nullable=True, unique=True, index=True)

    # 파일 정보
    pdf_url = Column(String, nullable=True)
    pdf_path = Column(String, nullable=True)

    # 추출된 텍스트 및 임베딩
    full_text = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)

    # 메타 정보
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계
    user = relationship("User", back_populates="papers")
    analyses = relationship("Analysis", back_populates="paper")
