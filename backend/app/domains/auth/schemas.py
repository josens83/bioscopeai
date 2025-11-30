"""
Auth Domain Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.schemas.base import BaseDBSchema


class UserCreate(BaseModel):
    """사용자 생성 스키마"""

    email: EmailStr = Field(..., description="사용자 이메일 주소", example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, description="사용자 이름 (3-50자)", example="johndoe")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)", example="SecurePass123!")
    full_name: Optional[str] = Field(None, description="전체 이름", example="홍길동")


class UserLogin(BaseModel):
    """로그인 스키마"""

    email: EmailStr = Field(..., description="사용자 이메일 주소", example="demo@bioscopeai.com")
    password: str = Field(..., description="비밀번호", example="demo1234")


class UserResponse(BaseDBSchema):
    """사용자 응답 스키마"""

    email: str = Field(..., description="이메일 주소")
    username: str = Field(..., description="사용자 이름")
    full_name: Optional[str] = Field(None, description="전체 이름")
    is_active: bool = Field(..., description="활성화 상태")
    is_verified: bool = Field(default=False, description="이메일 인증 여부")
    role: str = Field(..., description="사용자 역할")

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""

    access_token: str = Field(..., description="액세스 토큰 (30분 유효)")
    refresh_token: str = Field(..., description="리프레시 토큰 (7일 유효)")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user: UserResponse = Field(..., description="사용자 정보")


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""

    email: EmailStr = Field(..., description="비밀번호를 재설정할 계정의 이메일 주소")


class PasswordReset(BaseModel):
    """비밀번호 재설정 스키마"""

    token: str = Field(..., description="이메일로 받은 재설정 토큰")
    new_password: str = Field(..., min_length=8, description="새 비밀번호 (최소 8자)")


class EmailVerification(BaseModel):
    """이메일 인증 스키마"""

    token: str = Field(..., description="이메일로 받은 인증 토큰")


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 스키마"""

    email: Optional[EmailStr] = Field(None, description="새 이메일 주소")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="새 사용자 이름")
    full_name: Optional[str] = Field(None, description="새 전체 이름")


class PasswordChange(BaseModel):
    """비밀번호 변경 스키마"""

    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., min_length=8, description="새 비밀번호 (최소 8자)")
