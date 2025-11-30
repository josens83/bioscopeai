"""
표준 API 응답 형식

모든 API 엔드포인트에서 일관된 응답 형식을 사용
"""
from typing import Any, Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    표준 API 성공 응답

    Example:
        {
            "success": true,
            "data": {...},
            "message": "작업이 완료되었습니다",
            "timestamp": "2024-01-16T12:00:00Z"
        }
    """
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {"id": 1, "name": "Example"},
                "message": "작업이 완료되었습니다",
                "timestamp": "2024-01-16T12:00:00Z"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    페이지네이션 응답

    Example:
        {
            "success": true,
            "data": {
                "items": [...],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            },
            "message": null,
            "timestamp": "2024-01-16T12:00:00Z"
        }
    """
    success: bool = True
    data: "PaginationData[T]"
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationData(BaseModel, Generic[T]):
    """페이지네이션 데이터"""
    items: List[T]
    total: int = Field(..., description="전체 아이템 수")
    page: int = Field(..., description="현재 페이지 (1부터 시작)")
    size: int = Field(..., description="페이지당 아이템 수")
    pages: int = Field(..., description="전체 페이지 수")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> "PaginationData[T]":
        """페이지네이션 데이터 생성"""
        pages = (total + size - 1) // size if size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class ErrorResponse(BaseModel):
    """
    표준 API 에러 응답

    Example:
        {
            "success": false,
            "error": {
                "code": "ResourceNotFound",
                "message": "리소스를 찾을 수 없습니다",
                "details": {"resource_id": 123}
            },
            "timestamp": "2024-01-16T12:00:00Z"
        }
    """
    success: bool = False
    error: "ErrorDetail"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    code: str = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    details: Optional[dict] = Field(None, description="추가 정보")


# Helper functions
def success_response(
    data: Any = None,
    message: Optional[str] = None
) -> dict:
    """성공 응답 생성 헬퍼"""
    return APIResponse(
        success=True,
        data=data,
        message=message
    ).model_dump()


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    size: int,
    message: Optional[str] = None
) -> dict:
    """페이지네이션 응답 생성 헬퍼"""
    pagination_data = PaginationData.create(
        items=items,
        total=total,
        page=page,
        size=size
    )
    return PaginatedResponse(
        success=True,
        data=pagination_data,
        message=message
    ).model_dump()


def error_response(
    code: str,
    message: str,
    details: Optional[dict] = None
) -> dict:
    """에러 응답 생성 헬퍼"""
    return ErrorResponse(
        success=False,
        error=ErrorDetail(
            code=code,
            message=message,
            details=details
        )
    ).model_dump()
