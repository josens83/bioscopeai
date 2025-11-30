from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseDBSchema


class UserCreate(BaseModel):
    """사용자 생성 스키마"""

    email: EmailStr = Field(..., description="사용자 이메일 주소", example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, description="사용자 이름 (3-50자)", example="johndoe")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)", example="SecurePass123!")
    full_name: Optional[str] = Field(None, description="전체 이름", example="홍길동")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "johndoe",
                    "password": "SecurePass123!",
                    "full_name": "홍길동"
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """로그인 스키마"""

    email: EmailStr = Field(..., description="사용자 이메일 주소", example="demo@bioscopeai.com")
    password: str = Field(..., description="비밀번호", example="demo1234")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "demo@bioscopeai.com",
                    "password": "demo1234"
                }
            ]
        }
    }


class UserResponse(BaseDBSchema):
    """사용자 응답 스키마"""
    # id, created_at, updated_at 자동 상속

    email: str = Field(..., description="이메일 주소", example="user@example.com")
    username: str = Field(..., description="사용자 이름", example="johndoe")
    full_name: Optional[str] = Field(None, description="전체 이름", example="홍길동")
    is_active: bool = Field(..., description="활성화 상태", example=True)
    is_verified: bool = Field(default=False, description="이메일 인증 여부", example=False)
    role: str = Field(..., description="사용자 역할", example="user")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "email": "demo@bioscopeai.com",
                    "username": "demouser",
                    "full_name": "데모 사용자",
                    "is_active": True,
                    "is_verified": True,
                    "role": "user",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""

    access_token: str = Field(..., description="액세스 토큰 (30분 유효)", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="리프레시 토큰 (7일 유효)", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", description="토큰 타입", example="bearer")
    user: UserResponse = Field(..., description="사용자 정보")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjQwOTk1MjAwfQ.xyz",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjQxNjAwMDAwfQ.abc",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "email": "demo@bioscopeai.com",
                        "username": "demouser",
                        "full_name": "데모 사용자",
                        "is_active": True,
                        "is_verified": True,
                        "role": "user",
                        "created_at": "2024-01-01T00:00:00"
                    }
                }
            ]
        }
    }


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""

    email: EmailStr = Field(..., description="비밀번호를 재설정할 계정의 이메일 주소", example="user@example.com")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@bioscopeai.com"
                }
            ]
        }
    }


class PasswordReset(BaseModel):
    """비밀번호 재설정 스키마"""

    token: str = Field(..., description="이메일로 받은 재설정 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    new_password: str = Field(..., min_length=8, description="새 비밀번호 (최소 8자)", example="NewSecurePass123!")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIn0...",
                    "new_password": "MyNewPassword456!"
                }
            ]
        }
    }


class EmailVerification(BaseModel):
    """이메일 인증 스키마"""

    token: str = Field(..., description="이메일로 받은 인증 토큰", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIn0..."
                }
            ]
        }
    }


class UserUpdate(BaseModel):
    """사용자 정보 업데이트 스키마"""

    email: Optional[EmailStr] = Field(None, description="새 이메일 주소", example="newemail@example.com")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="새 사용자 이름", example="newusername")
    full_name: Optional[str] = Field(None, description="새 전체 이름", example="김철수")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "newemail@bioscopeai.com",
                    "username": "newusername",
                    "full_name": "김철수"
                }
            ]
        }
    }


class PasswordChange(BaseModel):
    """비밀번호 변경 스키마"""

    current_password: str = Field(..., description="현재 비밀번호", example="CurrentPass123!")
    new_password: str = Field(..., min_length=8, description="새 비밀번호 (최소 8자)", example="NewSecurePass456!")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "current_password": "OldPassword123!",
                    "new_password": "NewPassword456!"
                }
            ]
        }
    }
