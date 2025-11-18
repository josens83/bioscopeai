"""
API 키 관리 엔드포인트

사용자가 프로그래밍 방식으로 API에 접근하기 위한 API 키를 관리
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.services.api_key_service import APIKeyService
from app.core.logging import app_logger as logger


router = APIRouter()


# Request/Response 스키마
class APIKeyCreate(BaseModel):
    """API 키 생성 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="키 이름 (예: Production Server)")
    description: Optional[str] = Field(None, max_length=500, description="키 설명")
    scopes: Optional[List[str]] = Field(None, description="권한 범위 (예: ['papers:read', 'analysis:write'])")
    rate_limit: Optional[int] = Field(None, gt=0, description="분당 요청 제한 (없으면 플랜 기본값 사용)")
    expires_days: Optional[int] = Field(None, gt=0, description="만료까지 일수 (없으면 무제한)")
    ip_whitelist: Optional[List[str]] = Field(None, description="허용 IP 리스트")


class APIKeyResponse(BaseModel):
    """API 키 응답 (목록 조회용 - 실제 키는 숨김)"""
    id: int
    name: str
    prefix: str  # 예: "bsa_abc123..."
    description: Optional[str]
    scopes: Optional[str]
    rate_limit: Optional[int]
    is_active: bool
    last_used_at: Optional[datetime]
    usage_count: int
    expires_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    """API 키 생성 응답 (실제 키 포함 - 한 번만 표시)"""
    api_key: str  # 실제 API 키 (bsa_...)
    key_info: APIKeyResponse
    warning: str = "이 API 키를 안전한 곳에 저장하세요. 다시 조회할 수 없습니다."


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    내 API 키 목록 조회

    생성한 모든 API 키 목록을 반환합니다 (실제 키 값은 숨김).
    """
    api_keys = await APIKeyService.get_user_api_keys(db, current_user.id)
    return api_keys


@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    새 API 키 생성

    **중요**: 생성된 API 키는 이 응답에서만 표시됩니다.
    안전한 곳에 저장하세요!

    **사용 방법**:
    ```
    curl -H "X-API-Key: bsa_your_key_here" https://api.bioscopeai.com/api/v1/papers
    ```

    **권한 범위(Scopes)**:
    - `papers:read`: 논문 조회
    - `papers:write`: 논문 업로드
    - `analysis:read`: 분석 결과 조회
    - `analysis:write`: 분석 실행
    - `*`: 모든 권한
    """
    # API 키 생성
    api_key_obj, raw_key = await APIKeyService.create_api_key(
        db=db,
        user=current_user,
        name=key_data.name,
        description=key_data.description,
        scopes=key_data.scopes,
        rate_limit=key_data.rate_limit,
        expires_days=key_data.expires_days,
        ip_whitelist=key_data.ip_whitelist,
    )

    logger.info(f"API 키 생성: user_id={current_user.id}, key_name={key_data.name}")

    return {
        "api_key": raw_key,
        "key_info": api_key_obj,
        "warning": "이 API 키를 안전한 곳에 저장하세요. 다시 조회할 수 없습니다."
    }


@router.delete("/{key_id}", status_code=status.HTTP_200_OK)
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    API 키 삭제

    지정한 API 키를 완전히 삭제합니다.
    """
    success = await APIKeyService.delete_api_key(db, key_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API 키를 찾을 수 없습니다"
        )

    logger.info(f"API 키 삭제: user_id={current_user.id}, key_id={key_id}")

    return {"message": "API 키가 삭제되었습니다"}


@router.post("/{key_id}/revoke", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    API 키 비활성화 (취소)

    API 키를 삭제하지 않고 비활성화합니다.
    나중에 다시 활성화할 수 없으므로, 영구적으로 막으려면 이 방법을 사용하세요.
    """
    success = await APIKeyService.revoke_api_key(db, key_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API 키를 찾을 수 없습니다"
        )

    logger.warning(f"API 키 취소: user_id={current_user.id}, key_id={key_id}")

    return {"message": "API 키가 취소되었습니다"}
