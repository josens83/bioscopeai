from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PaperSearch(BaseModel):
    """논문 검색 스키마"""

    query: str = Field(..., min_length=1)
    max_results: int = Field(default=20, ge=1, le=100)
    sort: str = Field(default="relevance")


class PaperCreate(BaseModel):
    """논문 생성 스키마"""

    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    pubmed_id: Optional[str] = None
    pdf_url: Optional[str] = None
    full_text: Optional[str] = None
    keywords: Optional[List[str]] = None
    source: Optional[str] = None


class PaperResponse(BaseModel):
    """논문 응답 스키마"""

    id: int
    user_id: int
    title: str
    authors: Optional[str] = None
    abstract: Optional[str] = None
    publication_date: Optional[datetime] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    pubmed_id: Optional[str] = None
    pdf_url: Optional[str] = None
    keywords: Optional[List[str]] = None
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaperUpload(BaseModel):
    """논문 업로드 스키마"""

    title: Optional[str] = None
    authors: Optional[str] = None
