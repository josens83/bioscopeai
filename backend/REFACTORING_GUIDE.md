# BioscopeAI 프로덕션 리팩토링 가이드

전체 코드베이스를 프로덕션급 SaaS 수준으로 리팩토링한 내용과 가이드라인

---

## 📋 목차

1. [리팩토링 개요](#리팩토링-개요)
2. [주요 개선사항](#주요-개선사항)
3. [새로 추가된 구조](#새로-추가된-구조)
4. [API 표준화 가이드](#api-표준화-가이드)
5. [네이밍 컨벤션](#네이밍-컨벤션)
6. [에러 핸들링 가이드](#에러-핸들링-가이드)
7. [마이그레이션 가이드](#마이그레이션-가이드)
8. [Before & After 비교](#before--after-비교)

---

## 리팩토링 개요

### 목표
- ✅ **일관된 API 응답 형식** 구축
- ✅ **재사용 가능한 컴포넌트** 분리
- ✅ **타입 안정성** 강화
- ✅ **유지보수성** 향상
- ✅ **테스트 용이성** 개선

### 원칙
1. **DRY (Don't Repeat Yourself)**: 중복 코드 제거
2. **SOLID**: 객체지향 설계 원칙 준수
3. **명확한 책임 분리**: 각 모듈의 역할 명확화
4. **일관성**: 전체 코드베이스에서 동일한 패턴 사용

---

## 주요 개선사항

### 1. 표준 API 응답 형식 (`app/schemas/responses.py`)

**Before:**
```python
# 각 엔드포인트마다 다른 응답 형식
@router.get("/users/{id}")
async def get_user(id: int):
    return {"id": 1, "name": "User"}  # 불일치

@router.get("/papers")
async def list_papers():
    return papers  # 메타데이터 없음
```

**After:**
```python
from app.schemas.responses import success_response, paginated_response

@router.get("/users/{id}")
async def get_user(id: int):
    return success_response(
        data={"id": 1, "name": "User"},
        message="사용자 조회 성공"
    )

@router.get("/papers")
async def list_papers(page: int = 1, size: int = 20):
    return paginated_response(
        items=papers,
        total=100,
        page=page,
        size=size
    )
```

**응답 구조:**
```json
{
  "success": true,
  "data": {...},
  "message": "작업이 완료되었습니다",
  "timestamp": "2024-01-16T12:00:00Z"
}
```

### 2. 공통 스키마 베이스 클래스 (`app/schemas/base.py`)

**Before:**
```python
# 각 스키마마다 중복된 설정
class UserSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaperSchema(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
```

**After:**
```python
from app.schemas.base import BaseDBSchema

class UserSchema(BaseDBSchema):
    # id, created_at, updated_at, Config 자동 상속
    name: str
    email: str

class PaperSchema(BaseDBSchema):
    title: str
    abstract: str
```

**제공되는 베이스 클래스:**
- `BaseSchema`: 기본 설정
- `BaseDBSchema`: DB 모델용 (id, timestamps 포함)
- `PaginationParams`: 페이지네이션 파라미터
- `SortParams`: 정렬 파라미터
- `FilterParams`: 공통 필터 파라미터

### 3. Constants 중앙화 (`app/constants/`)

**Before:**
```python
# 코드 곳곳에 하드코딩된 상수
page_size = 20
max_papers = 100
rate_limit = 60
```

**After:**
```python
from app.constants import DEFAULT_PAGE_SIZE, TIER_LIMITS
from app.constants.subscription import SubscriptionTier

page_size = DEFAULT_PAGE_SIZE
max_papers = TIER_LIMITS[SubscriptionTier.PREMIUM]["max_papers"]
```

**Constants 구조:**
```
app/constants/
├── __init__.py
├── api.py            # API 관련 (페이지네이션, rate limit)
├── subscription.py   # 구독 플랜, 제한, 가격
├── status.py         # 상태 Enum
└── messages.py       # 성공/에러 메시지
```

### 4. 유틸리티 함수 (`app/utils/`)

**Before:**
```python
# 중복된 날짜 처리 로직
now = datetime.utcnow()
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
```

**After:**
```python
from app.utils.datetime import get_current_utc, format_datetime

now = get_current_utc()
formatted = format_datetime(now)
```

**제공되는 유틸리티:**
- `datetime.py`: 날짜/시간 처리
- `validators.py`: 유효성 검증
- `formatters.py`: 포맷팅 (통화, 파일 크기 등)
- `pagination.py`: 페이지네이션 계산

---

## 새로 추가된 구조

### 디렉토리 구조

```
backend/app/
├── api/
│   ├── v1/
│   │   ├── endpoints/       # API 엔드포인트
│   │   └── router.py
│   └── deps.py              # 의존성
├── constants/               # ✨ NEW: 상수 및 Enum
│   ├── __init__.py
│   ├── api.py
│   ├── subscription.py
│   ├── status.py
│   └── messages.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── exceptions.py        # 커스텀 예외
│   └── error_handlers.py    # 에러 핸들러
├── models/                  # SQLAlchemy 모델
├── schemas/                 # Pydantic 스키마
│   ├── base.py             # ✨ NEW: 공통 베이스 클래스
│   ├── responses.py        # ✨ NEW: 표준 응답 형식
│   ├── user.py
│   └── ...
├── services/                # 비즈니스 로직
├── utils/                   # ✨ NEW: 유틸리티 함수
│   ├── __init__.py
│   ├── datetime.py
│   ├── validators.py
│   ├── formatters.py
│   └── pagination.py
└── main.py
```

---

## API 표준화 가이드

### 1. 성공 응답 (200 OK)

```python
from app.schemas.responses import success_response

@router.post("/users")
async def create_user(user_data: UserCreate):
    user = await create_user_in_db(user_data)
    return success_response(
        data=user,
        message="사용자가 생성되었습니다"
    )
```

### 2. 페이지네이션 응답

```python
from app.schemas.responses import paginated_response
from app.schemas.base import PaginationParams

@router.get("/papers")
async def list_papers(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # 데이터 조회
    papers = await get_papers(
        db,
        offset=pagination.offset,
        limit=pagination.limit
    )
    total = await count_papers(db)

    return paginated_response(
        items=papers,
        total=total,
        page=pagination.page,
        size=pagination.size
    )
```

### 3. 에러 응답

```python
from app.core.exceptions import ResourceNotFound
from app.constants.messages import ERROR_MESSAGES

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await find_user(user_id)
    if not user:
        raise ResourceNotFound("사용자", user_id)

    return success_response(data=user)
```

**자동 변환되는 에러 응답:**
```json
{
  "success": false,
  "error": {
    "code": "ResourceNotFound",
    "message": "사용자을(를) 찾을 수 없습니다.",
    "details": {
      "resource_type": "사용자",
      "resource_id": 123
    }
  },
  "timestamp": "2024-01-16T12:00:00Z"
}
```

---

## 네이밍 컨벤션

### 1. 파일명
- **소문자 + 언더스코어**: `user_service.py`, `api_key_service.py`
- **복수형 사용**: `constants/`, `utils/`, `schemas/`

### 2. 클래스명
- **PascalCase**: `UserService`, `APIKeyService`
- **의미 명확**: `PromotionCodeService` (X: `PromoService`)

### 3. 함수명
- **snake_case**: `create_user`, `validate_email`
- **동사 시작**: `get_`, `create_`, `update_`, `delete_`, `validate_`, `format_`
- **불린 반환**: `is_`, `has_`, `can_`

### 4. 변수명
- **snake_case**: `user_id`, `created_at`
- **의미 명확**: `max_papers` (X: `max_p`)

### 5. 상수
- **대문자 + 언더스코어**: `DEFAULT_PAGE_SIZE`, `MAX_FILE_SIZE`

---

## 에러 핸들링 가이드

### 1. 커스텀 예외 사용

```python
from app.core.exceptions import (
    UsageLimitExceeded,
    FeatureNotAvailable,
    ResourceNotFound,
    DuplicateResource
)

# ✅ GOOD
if usage.count >= limit:
    raise UsageLimitExceeded(
        usage_type="analyses",
        current=usage.count,
        limit=limit,
        plan=user.subscription.tier
    )

# ❌ BAD
if usage.count >= limit:
    raise HTTPException(status_code=429, detail="Limit exceeded")
```

### 2. 일관된 메시지 사용

```python
from app.constants.messages import SUCCESS_MESSAGES, ERROR_MESSAGES

# ✅ GOOD
return success_response(
    data=user,
    message=SUCCESS_MESSAGES["USER_UPDATED"]
)

# ❌ BAD
return {"message": "User updated successfully"}
```

### 3. 에러 로깅

```python
from app.core.logging import app_logger as logger

try:
    result = await external_api_call()
except Exception as e:
    logger.error(f"External API error: {e}", exc_info=True)
    raise ExternalServiceError("PubMed", str(e))
```

---

## 마이그레이션 가이드

### 기존 엔드포인트를 새 형식으로 마이그레이션

#### Step 1: Import 추가

```python
# Before
from fastapi import APIRouter, Depends

# After
from fastapi import APIRouter, Depends
from app.schemas.responses import success_response, paginated_response
from app.schemas.base import PaginationParams
from app.constants.messages import SUCCESS_MESSAGES
```

#### Step 2: 응답 형식 변경

```python
# Before
@router.get("/users")
async def list_users():
    users = await get_all_users()
    return users

# After
@router.get("/users")
async def list_users(
    pagination: PaginationParams = Depends()
):
    users = await get_users_paginated(
        offset=pagination.offset,
        limit=pagination.limit
    )
    total = await count_users()

    return paginated_response(
        items=users,
        total=total,
        page=pagination.page,
        size=pagination.size,
        message=SUCCESS_MESSAGES.get("OPERATION_SUCCESS")
    )
```

#### Step 3: 에러 처리 개선

```python
# Before
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await find_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# After
from app.core.exceptions import ResourceNotFound

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await find_user(user_id)
    if not user:
        raise ResourceNotFound("사용자", user_id)

    return success_response(data=user)
```

---

## Before & After 비교

### 1. API 엔드포인트

**Before:**
```python
@router.post("/login")
async def login(credentials: LoginRequest):
    user = authenticate(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
```

**After:**
```python
from app.schemas.responses import success_response
from app.core.exceptions import InvalidCredentials
from app.constants.messages import SUCCESS_MESSAGES

@router.post("/login")
async def login(credentials: LoginRequest):
    user = authenticate(credentials.email, credentials.password)
    if not user:
        raise InvalidCredentials()

    token = create_token(user.id)
    return success_response(
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": user
        },
        message=SUCCESS_MESSAGES["AUTH_LOGIN_SUCCESS"]
    )
```

### 2. 서비스 레이어

**Before:**
```python
class UserService:
    @staticmethod
    async def create_user(db, user_data):
        # 중복 체크
        existing = await db.execute(...)
        if existing.scalar_one_or_none():
            raise HTTPException(400, "Email exists")

        user = User(**user_data.dict())
        db.add(user)
        await db.commit()
        return user
```

**After:**
```python
from app.core.exceptions import DuplicateResource

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """사용자 생성"""
        # 중복 체크
        existing = await db.execute(...)
        if existing.scalar_one_or_none():
            raise DuplicateResource("사용자", "email", user_data.email)

        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(f"User created: {user.id}")
        return user
```

### 3. 스키마

**Before:**
```python
class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**After:**
```python
from app.schemas.base import BaseDBSchema

class UserResponse(BaseDBSchema):
    # id, created_at, updated_at, Config 자동 상속
    email: str
    full_name: Optional[str]
    role: str
```

---

## 체크리스트

새 엔드포인트 작성 시 확인 사항:

- [ ] 표준 응답 형식 사용 (`success_response`, `paginated_response`)
- [ ] 커스텀 예외 사용 (HTTPException 대신)
- [ ] Constants에서 메시지 가져오기
- [ ] 페이지네이션 파라미터 사용
- [ ] BaseDBSchema 상속
- [ ] 타입 힌팅 완전히 작성
- [ ] 로깅 추가
- [ ] Docstring 작성

---

## 추가 개선 계획

### Phase 2 (향후 작업)
- [ ] 모든 API 엔드포인트를 새 형식으로 마이그레이션
- [ ] Unit Test 추가
- [ ] Integration Test 추가
- [ ] API 문서 자동 생성 개선
- [ ] OpenAPI 스펙 완전 준수
- [ ] 성능 최적화 (N+1 쿼리 제거)
- [ ] 캐싱 전략 고도화

---

**작성일:** 2024-01-16
**버전:** 1.0.0
**마지막 업데이트:** 2024-01-16
**작성자:** Claude (AI Assistant)
