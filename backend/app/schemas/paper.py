from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseDBSchema


class PaperSearch(BaseModel):
    """논문 검색 스키마"""

    query: str = Field(..., min_length=1, description="검색 쿼리", example="cancer treatment")
    max_results: int = Field(default=20, ge=1, le=100, description="최대 결과 수 (1-100)", example=20)
    sort: str = Field(default="relevance", description="정렬 방식", example="relevance")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "CRISPR gene editing",
                    "max_results": 10,
                    "sort": "relevance"
                }
            ]
        }
    }


class PaperCreate(BaseModel):
    """논문 생성 스키마"""

    title: str = Field(..., description="논문 제목", example="CRISPR-Cas9 Gene Editing in Human Cells")
    authors: Optional[str] = Field(None, description="저자", example="Smith J, Lee K, Park M")
    abstract: Optional[str] = Field(None, description="초록", example="This study demonstrates...")
    publication_date: Optional[datetime] = Field(None, description="발행일", example="2024-01-15T00:00:00")
    journal: Optional[str] = Field(None, description="저널", example="Nature Biotechnology")
    doi: Optional[str] = Field(None, description="DOI", example="10.1038/nbt.2024.001")
    pubmed_id: Optional[str] = Field(None, description="PubMed ID", example="38123456")
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    full_text: Optional[str] = Field(None, description="전문")
    keywords: Optional[List[str]] = Field(None, description="키워드", example=["CRISPR", "gene editing", "biotechnology"])
    source: Optional[str] = Field(None, description="출처", example="pubmed")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "CRISPR-Cas9 Gene Editing in Human Cells",
                    "authors": "Smith J, Lee K",
                    "abstract": "This study demonstrates the application of CRISPR-Cas9...",
                    "journal": "Nature Biotechnology",
                    "doi": "10.1038/nbt.2024.001",
                    "pubmed_id": "38123456",
                    "keywords": ["CRISPR", "gene editing"],
                    "source": "pubmed"
                }
            ]
        }
    }


class PaperResponse(BaseDBSchema):
    """논문 응답 스키마"""
    # id, created_at, updated_at 자동 상속

    user_id: int = Field(..., description="사용자 ID", example=1)
    title: str = Field(..., description="논문 제목", example="CRISPR-Cas9 Gene Editing in Human Cells")
    authors: Optional[str] = Field(None, description="저자", example="Smith J, Lee K")
    abstract: Optional[str] = Field(None, description="초록", example="This study demonstrates...")
    publication_date: Optional[datetime] = Field(None, description="발행일", example="2024-01-15T00:00:00")
    journal: Optional[str] = Field(None, description="저널", example="Nature Biotechnology")
    doi: Optional[str] = Field(None, description="DOI", example="10.1038/nbt.2024.001")
    pubmed_id: Optional[str] = Field(None, description="PubMed ID", example="38123456")
    pdf_url: Optional[str] = Field(None, description="PDF URL")
    keywords: Optional[List[str]] = Field(None, description="키워드", example=["CRISPR", "gene editing"])
    source: Optional[str] = Field(None, description="출처", example="pubmed")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "title": "CRISPR-Cas9 Gene Editing in Human Cells",
                    "authors": "Smith J, Lee K",
                    "abstract": "This study demonstrates the application...",
                    "journal": "Nature Biotechnology",
                    "doi": "10.1038/nbt.2024.001",
                    "pubmed_id": "38123456",
                    "keywords": ["CRISPR", "gene editing"],
                    "source": "pubmed",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ]
        }
    }


class PaperUpload(BaseModel):
    """논문 업로드 스키마"""

    title: Optional[str] = Field(None, description="논문 제목")
    authors: Optional[str] = Field(None, description="저자")
