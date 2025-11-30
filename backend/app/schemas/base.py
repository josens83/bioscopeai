"""
공통 Pydantic 스키마 베이스 클래스

모든 스키마에서 공통으로 사용되는 필드와 설정
"""
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class TimestampMixin(BaseModel):
    """타임스탬프 필드 Mixin"""
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")


class BaseSchema(BaseModel):
    """모든 스키마의 베이스 클래스"""
    model_config = ConfigDict(
        from_attributes=True,  # ORM 모델로부터 생성 가능
        use_enum_values=True,  # Enum을 값으로 변환
        populate_by_name=True,  # alias 사용 가능
        str_strip_whitespace=True,  # 문자열 공백 제거
        json_schema_extra={
            "examples": []
        }
    )


class BaseDBSchema(BaseSchema, TimestampMixin):
    """데이터베이스 모델 기반 스키마 베이스"""
    id: int = Field(..., description="ID", gt=0)


class PaginationParams(BaseModel):
    """페이지네이션 파라미터"""
    page: int = Field(1, ge=1, description="페이지 번호 (1부터 시작)")
    size: int = Field(20, ge=1, le=100, description="페이지당 아이템 수 (최대 100)")

    @property
    def offset(self) -> int:
        """SQL OFFSET 계산"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """SQL LIMIT"""
        return self.size


class SortParams(BaseModel):
    """정렬 파라미터"""
    sort_by: str = Field("created_at", description="정렬 기준 필드")
    order: str = Field("desc", pattern="^(asc|desc)$", description="정렬 순서")

    @property
    def order_by_clause(self) -> str:
        """SQL ORDER BY 절 생성"""
        return f"{self.sort_by} {self.order.upper()}"


class FilterParams(BaseModel):
    """공통 필터 파라미터"""
    search: Optional[str] = Field(None, description="검색어", max_length=200)
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")
    is_active: Optional[bool] = Field(None, description="활성 상태 필터")
