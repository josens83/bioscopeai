"""
Papers Domain Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseDBSchema


class PaperSearch(BaseModel):
    """논문 검색 스키마"""

    query: str = Field(..., min_length=1, description="검색 쿼리")
    max_results: int = Field(default=20, ge=1, le=100, description="최대 결과 수")
    sort: str = Field(default="relevance", description="정렬 방식")


class PaperCreate(BaseModel):
    """논문 생성 스키마"""

    title: str = Field(..., description="논문 제목")
    authors: Optional[str] = Field(None, description="저자")
    abstract: Optional[str] = Field(None, description="초록")
    publication_date: Optional[datetime] = Field(None, description="발행일")
    journal: Optional[str] = Field(None, description="저널")
    doi: Optional[str] = Field(None, description="DOI")
    pubmed_id: Optional[str] = Field(None, description="PubMed ID")
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    full_text: Optional[str] = Field(None, description="전문")
    keywords: Optional[List[str]] = Field(None, description="키워드")
    source: Optional[str] = Field(None, description="출처")


class PaperResponse(BaseDBSchema):
    """논문 응답 스키마"""

    user_id: int = Field(..., description="사용자 ID")
    title: str = Field(..., description="논문 제목")
    authors: Optional[str] = Field(None, description="저자")
    abstract: Optional[str] = Field(None, description="초록")
    publication_date: Optional[datetime] = Field(None, description="발행일")
    journal: Optional[str] = Field(None, description="저널")
    doi: Optional[str] = Field(None, description="DOI")
    pubmed_id: Optional[str] = Field(None, description="PubMed ID")
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    keywords: Optional[List[str]] = Field(None, description="키워드")
    source: Optional[str] = Field(None, description="출처")

    model_config = {"from_attributes": True}


class PaperUpdate(BaseModel):
    """논문 업데이트 스키마"""

    title: Optional[str] = Field(None, description="논문 제목")
    authors: Optional[str] = Field(None, description="저자")
    abstract: Optional[str] = Field(None, description="초록")
    keywords: Optional[List[str]] = Field(None, description="키워드")
