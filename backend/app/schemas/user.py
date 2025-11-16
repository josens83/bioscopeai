from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


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


class UserResponse(BaseModel):
    """사용자 응답 스키마"""

    id: int = Field(..., description="사용자 ID", example=1)
    email: str = Field(..., description="이메일 주소", example="user@example.com")
    username: str = Field(..., description="사용자 이름", example="johndoe")
    full_name: Optional[str] = Field(None, description="전체 이름", example="홍길동")
    is_active: bool = Field(..., description="활성화 상태", example=True)
    created_at: datetime = Field(..., description="계정 생성일시", example="2024-01-01T00:00:00")

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
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""

    access_token: str = Field(..., description="액세스 토큰 (30분 유효)", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., description="리프레시 토큰 (7일 유효)", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", description="토큰 타입", example="bearer")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjQwOTk1MjAwfQ.xyz",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjQxNjAwMDAwfQ.abc",
                    "token_type": "bearer"
                }
            ]
        }
    }
