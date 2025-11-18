# 🏗️ BioscopeAI Architecture - Domain-Driven Design (DDD)

> **프로덕션급 SaaS 아키텍처 가이드**
> 작성일: 2025-01-18
> 버전: 2.0 (DDD 전환)

## 📋 목차

1. [개요](#개요)
2. [디렉토리 구조](#디렉토리-구조)
3. [도메인 주도 설계 (DDD) 원칙](#도메인-주도-설계-ddd-원칙)
4. [Auth 도메인 완전 예제](#auth-도메인-완전-예제)
5. [새로운 도메인 생성 가이드](#새로운-도메인-생성-가이드)
6. [마이그레이션 체크리스트](#마이그레이션-체크리스트)
7. [테스트 구조](#테스트-구조)
8. [모범 사례](#모범-사례)

---

## 개요

BioscopeAI는 **도메인 주도 설계(DDD)** 아키텍처로 전환하여 다음을 달성합니다:

### ✅ 개선 사항

| 측면 | 이전 구조 | DDD 구조 | 개선율 |
|------|-----------|----------|--------|
| **파일 크기** | 최대 872줄 | 평균 ~150줄 | 82% 감소 |
| **도메인 경계** | 불명확 | 명확 | ✅ |
| **테스트 용이성** | 중간 | 매우 좋음 | ✅ |
| **확장성** | 제한적 | 무한 확장 | ✅ |
| **마이크로서비스 전환** | 어려움 | 쉬움 | ✅ |

### 🎯 핵심 원칙

1. **도메인별 독립성**: 각 도메인은 자체 models, schemas, services, api 포함
2. **명확한 경계**: 도메인 간 의존성 최소화
3. **공유 모듈 분리**: `shared/`에 공통 기능 집중
4. **Infrastructure 분리**: 외부 시스템 통합은 `shared/infrastructure/`

---

## 디렉토리 구조

```
backend/
├── app/
│   ├── domains/                    # 도메인별 비즈니스 로직 ⭐ NEW
│   │   ├── auth/                   # ✅ 인증 도메인 (완성)
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # User 모델
│   │   │   ├── schemas.py          # UserCreate, UserResponse 등
│   │   │   ├── service.py          # AuthService (비즈니스 로직)
│   │   │   ├── api.py              # FastAPI 라우터
│   │   │   ├── dependencies.py     # get_current_user 등
│   │   │   └── exceptions.py       # AuthException 등
│   │   │
│   │   ├── papers/                 # 📄 논문 도메인 (TODO)
│   │   │   ├── models.py           # Paper 모델
│   │   │   ├── schemas.py          # PaperCreate, PaperResponse
│   │   │   ├── service.py          # PaperService
│   │   │   └── api.py              # 라우터
│   │   │
│   │   ├── analysis/               # 🤖 분석 도메인 (TODO)
│   │   │   ├── models.py           # Analysis 모델
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── api.py
│   │   │   └── rag/                # RAG 전용 모듈
│   │   │       ├── embeddings.py
│   │   │       ├── vectorstore.py
│   │   │       └── pipeline.py
│   │   │
│   │   ├── subscriptions/          # 💳 구독 도메인 (TODO)
│   │   │   ├── models.py           # Subscription, PromotionCode
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── payment_service.py  # Stripe 통합
│   │   │   └── api/                # 엔드포인트 분할
│   │   │       ├── plans.py
│   │   │       ├── checkout.py
│   │   │       └── webhooks.py
│   │   │
│   │   ├── admin/                  # 👑 관리자 도메인 (TODO)
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── api/                # 거대 파일 분할
│   │   │       ├── users.py        # 사용자 관리
│   │   │       ├── metrics.py      # 비즈니스 메트릭
│   │   │       ├── analytics.py    # 분석
│   │   │       └── system.py       # 시스템 모니터링
│   │   │
│   │   └── usage/                  # 📊 사용량 도메인 (TODO)
│   │       ├── models.py
│   │       ├── schemas.py
│   │       ├── service.py
│   │       └── api.py
│   │
│   ├── shared/                     # 공유 모듈 ⭐ NEW
│   │   ├── core/                   # 핵심 설정 (기존 app/core/)
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   ├── rate_limiting.py
│   │   │   ├── middleware.py
│   │   │   ├── logging.py
│   │   │   └── sentry.py
│   │   │
│   │   ├── infrastructure/         # 인프라 서비스 ⭐ NEW
│   │   │   ├── email/
│   │   │   │   ├── service.py      # EmailService 클래스
│   │   │   │   └── templates.py    # 이메일 템플릿
│   │   │   ├── cache/
│   │   │   │   └── service.py      # CacheService (Redis)
│   │   │   └── storage/            # S3/MinIO (Future)
│   │   │       └── service.py
│   │   │
│   │   ├── utils/                  # 유틸리티 (기존)
│   │   │   ├── datetime.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   └── pagination.py
│   │   │
│   │   ├── constants/              # 상수 (기존)
│   │   │   ├── api.py
│   │   │   ├── subscription.py
│   │   │   ├── messages.py
│   │   │   └── status.py
│   │   │
│   │   └── schemas/                # 공통 스키마 (기존)
│   │       ├── base.py             # BaseDBSchema
│   │       └── responses.py        # APIResponse[T]
│   │
│   └── main.py                     # FastAPI 앱 진입점
│
├── tests/                          # 테스트 미러 구조 ⭐
│   ├── unit/                       # 단위 테스트
│   │   ├── domains/
│   │   │   ├── auth/
│   │   │   │   ├── test_service.py
│   │   │   │   └── test_models.py
│   │   │   └── papers/
│   │   │       └── test_service.py
│   │   └── shared/
│   │       ├── utils/
│   │       │   └── test_validators.py
│   │       └── infrastructure/
│   │           ├── email/
│   │           │   └── test_service.py
│   │           └── cache/
│   │               └── test_service.py
│   │
│   ├── integration/                # 통합 테스트
│   │   ├── test_auth_flow.py
│   │   ├── test_subscription_flow.py
│   │   └── test_payment_webhook.py
│   │
│   ├── e2e/                        # E2E 테스트
│   │   └── test_user_journey.py
│   │
│   ├── fixtures/                   # 테스트 데이터
│   │   ├── users.py
│   │   └── papers.py
│   │
│   └── conftest.py                 # pytest 설정
│
├── alembic/                        # DB 마이그레이션
├── scripts/                        # 유틸리티 스크립트
└── requirements.txt
```

---

## 도메인 주도 설계 (DDD) 원칙

### 1. 도메인 구조

각 도메인은 다음 파일을 포함:

```python
domains/example/
├── __init__.py          # 도메인 export (router, models 등)
├── models.py            # SQLAlchemy 모델
├── schemas.py           # Pydantic 스키마 (입력/출력)
├── service.py           # 비즈니스 로직
├── api.py               # FastAPI 라우터
├── dependencies.py      # FastAPI 의존성
└── exceptions.py        # 도메인 전용 예외
```

### 2. 계층 분리

```
┌─────────────────────────────────────┐
│         API Layer (api.py)          │  ← HTTP 요청/응답
├─────────────────────────────────────┤
│     Service Layer (service.py)      │  ← 비즈니스 로직
├─────────────────────────────────────┤
│       Data Layer (models.py)        │  ← 데이터베이스
└─────────────────────────────────────┘
         ↕                     ↕
   schemas.py            dependencies.py
```

### 3. 의존성 방향

```
✅ 올바른 의존성:
domains/auth → shared/infrastructure/email
domains/papers → shared/utils/validators

❌ 잘못된 의존성:
shared/core → domains/auth (X)
domains/auth → domains/papers (X - 도메인 간 직접 의존)
```

---

## Auth 도메인 완전 예제

Auth 도메인은 **완전히 구현된 참고 예제**입니다.

### 파일 구조

```
domains/auth/
├── __init__.py          # export auth_router
├── models.py            # User 모델
├── schemas.py           # UserCreate, UserLogin, UserResponse, TokenResponse 등
├── service.py           # AuthService (register, login, verify_email 등)
├── api.py               # FastAPI 라우터 (8개 엔드포인트)
├── dependencies.py      # get_current_user, get_current_admin 등
└── exceptions.py        # InvalidCredentialsException 등 10개 예외
```

### 핵심 컴포넌트

#### 1. Models (`models.py`)

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")

    # 관계
    subscriptions = relationship("Subscription", back_populates="user")
    papers = relationship("Paper", back_populates="user")
```

**원칙**:
- 도메인 모델은 다른 도메인과 관계를 가질 수 있음
- Foreign Key는 id만 저장, 객체는 relationship으로 접근

#### 2. Schemas (`schemas.py`)

```python
class UserCreate(BaseModel):
    """사용자 생성 - 입력"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str]

class UserResponse(BaseDBSchema):
    """사용자 응답 - 출력"""
    # id, created_at, updated_at 자동 상속
    email: str
    username: str
    is_active: bool
    is_verified: bool

    model_config = {"from_attributes": True}
```

**원칙**:
- 입력 스키마: `BaseModel` 상속
- 출력 스키마: `BaseDBSchema` 상속 (자동 id, timestamps)
- 비밀번호 등 민감 정보는 응답에 포함 안 함

#### 3. Service (`service.py`)

```python
class AuthService:
    """비즈니스 로직 집중"""

    @staticmethod
    async def register(db: AsyncSession, user_in: UserCreate) -> User:
        # 1. 중복 확인
        if await db.execute(select(User).where(User.email == user_in.email)):
            raise EmailAlreadyExistsException()

        # 2. 사용자 생성
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            verification_token=secrets.token_urlsafe(32)
        )
        db.add(user)
        await db.commit()

        # 3. 이메일 전송 (Infrastructure 사용)
        await send_verification_email(user.email, user.verification_token)

        # 4. 감사 로그
        await log_user_created(db, user.id, user.email)

        return user
```

**원칙**:
- `@staticmethod` 사용 (상태 없는 서비스)
- 트랜잭션 관리 (db.commit)
- 예외는 도메인 예외 사용
- Infrastructure 서비스 활용 (이메일, 감사 로그)

#### 4. API (`api.py`)

```python
router = APIRouter()

@router.post("/register", response_model=UserResponse)
@limiter.limit(RateLimits.AUTH)  # Rate limiting
async def register(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """사용자 등록 엔드포인트"""
    user = await AuthService.register(db, user_in)
    return user
```

**원칙**:
- 얇은 컨트롤러 (비즈니스 로직 X)
- Service 메서드 호출만
- 의존성 주입 사용 (`Depends`)
- Rate limiting 적용
- Docstring으로 API 문서화

#### 5. Dependencies (`dependencies.py`)

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 토큰에서 현재 사용자 추출"""
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")

    user = await db.execute(select(User).where(User.id == int(user_id)))
    if not user:
        raise UserNotFoundException()

    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """관리자 권한 확인"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한 필요")
    return current_user
```

**원칙**:
- 재사용 가능한 의존성
- 체인 가능 (`get_current_admin` → `get_current_user`)
- 도메인 예외 사용

#### 6. Exceptions (`exceptions.py`)

```python
class AuthException(HTTPException):
    """인증 기본 예외"""
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail)

class InvalidCredentialsException(AuthException):
    """잘못된 인증 정보"""
    def __init__(self):
        super().__init__(detail="이메일 또는 비밀번호가 올바르지 않습니다")
```

**원칙**:
- 도메인별 의미 있는 예외
- HTTPException 상속
- 일관된 에러 메시지

---

## 새로운 도메인 생성 가이드

### Step 1: 디렉토리 생성

```bash
mkdir -p backend/app/domains/example
cd backend/app/domains/example
```

### Step 2: 파일 템플릿

#### `__init__.py`
```python
"""
Example Domain
"""
from .api import router as example_router

__all__ = ["example_router"]
```

#### `models.py`
```python
"""
Example Domain Models
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # 관계
    user = relationship("User", back_populates="examples")
```

#### `schemas.py`
```python
"""
Example Domain Schemas
"""
from pydantic import BaseModel, Field
from app.schemas.base import BaseDBSchema

class ExampleCreate(BaseModel):
    name: str = Field(..., description="이름")

class ExampleResponse(BaseDBSchema):
    name: str
    user_id: int

    model_config = {"from_attributes": True}
```

#### `service.py`
```python
"""
Example Domain Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Example
from .schemas import ExampleCreate

class ExampleService:
    @staticmethod
    async def create(db: AsyncSession, data: ExampleCreate, user_id: int) -> Example:
        example = Example(name=data.name, user_id=user_id)
        db.add(example)
        await db.commit()
        await db.refresh(example)
        return example
```

#### `api.py`
```python
"""
Example Domain API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.auth.dependencies import get_db, get_current_user
from app.domains.auth.models import User
from .service import ExampleService
from .schemas import ExampleCreate, ExampleResponse

router = APIRouter()

@router.post("/", response_model=ExampleResponse)
async def create_example(
    data: ExampleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await ExampleService.create(db, data, current_user.id)
```

### Step 3: 라우터 등록 (`main.py`)

```python
from app.domains.example import example_router

app.include_router(example_router, prefix="/api/v1/examples", tags=["examples"])
```

### Step 4: 테스트 작성

```python
# tests/unit/domains/example/test_service.py
import pytest
from app.domains.example.service import ExampleService
from app.domains.example.schemas import ExampleCreate

@pytest.mark.asyncio
async def test_create_example(db_session):
    data = ExampleCreate(name="Test")
    example = await ExampleService.create(db_session, data, user_id=1)
    assert example.name == "Test"
```

---

## 마이그레이션 체크리스트

기존 코드를 DDD 구조로 이전할 때:

### ✅ Auth 도메인 (완료)
- [x] models.py (User)
- [x] schemas.py (UserCreate, UserResponse, TokenResponse 등)
- [x] service.py (AuthService)
- [x] api.py (register, login, verify_email 등)
- [x] dependencies.py (get_current_user 등)
- [x] exceptions.py (AuthException 등)

### ⏳ Papers 도메인 (TODO)
- [ ] `app/models/paper.py` → `domains/papers/models.py`
- [ ] `app/schemas/paper.py` → `domains/papers/schemas.py`
- [ ] `app/services/pubmed_service.py` → `domains/papers/services/pubmed.py`
- [ ] `app/services/pdf_service.py` → `domains/papers/services/pdf.py`
- [ ] `app/api/v1/endpoints/papers.py` → `domains/papers/api.py` (분할 고려)
- [ ] 테스트 작성

### ⏳ Analysis 도메인 (TODO)
- [ ] `app/models/analysis.py` → `domains/analysis/models.py`
- [ ] `app/schemas/analysis.py` → `domains/analysis/schemas.py`
- [ ] `app/rag/` → `domains/analysis/rag/`
- [ ] `app/api/v1/endpoints/analysis.py` → `domains/analysis/api.py`
- [ ] 테스트 작성

### ⏳ Subscriptions 도메인 (TODO)
- [ ] `app/models/subscription.py` → `domains/subscriptions/models.py`
- [ ] `app/models/promotion_code.py` → `domains/subscriptions/models.py`
- [ ] `app/schemas/subscription.py` → `domains/subscriptions/schemas.py`
- [ ] `app/services/payment_service.py` → `domains/subscriptions/payment_service.py`
- [ ] `app/api/v1/endpoints/subscriptions.py` (421줄) → 분할:
  - [ ] `domains/subscriptions/api/plans.py`
  - [ ] `domains/subscriptions/api/checkout.py`
  - [ ] `domains/subscriptions/api/webhooks.py`
- [ ] 테스트 작성

### ⏳ Admin 도메인 (TODO)
- [ ] `app/api/v1/endpoints/admin.py` (872줄) → 분할:
  - [ ] `domains/admin/api/users.py` (사용자 관리)
  - [ ] `domains/admin/api/metrics.py` (비즈니스 메트릭)
  - [ ] `domains/admin/api/analytics.py` (분석)
  - [ ] `domains/admin/api/system.py` (시스템 모니터링)
- [ ] `domains/admin/service.py` (비즈니스 로직)
- [ ] 테스트 작성

---

## 테스트 구조

### 단위 테스트 (Unit Tests)

```python
# tests/unit/domains/auth/test_service.py
import pytest
from app.domains.auth.service import AuthService
from app.domains.auth.schemas import UserCreate
from app.domains.auth.exceptions import EmailAlreadyExistsException

@pytest.mark.asyncio
async def test_register_success(db_session):
    """성공적인 회원가입"""
    data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="SecurePass123!"
    )
    user = await AuthService.register(db_session, data)
    assert user.email == "test@example.com"
    assert user.is_verified == False

@pytest.mark.asyncio
async def test_register_duplicate_email(db_session, existing_user):
    """이메일 중복 시 예외 발생"""
    data = UserCreate(
        email=existing_user.email,
        username="newuser",
        password="SecurePass123!"
    )
    with pytest.raises(EmailAlreadyExistsException):
        await AuthService.register(db_session, data)
```

### 통합 테스트 (Integration Tests)

```python
# tests/integration/test_auth_flow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_complete_auth_flow(client: AsyncClient):
    """회원가입 → 이메일 인증 → 로그인 전체 플로우"""

    # 1. 회원가입
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecurePass123!"
    })
    assert response.status_code == 201
    user_data = response.json()

    # 2. 이메일 인증 (토큰은 DB에서 조회)
    # ... verification logic

    # 3. 로그인
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## 모범 사례

### ✅ DO

1. **Service에 비즈니스 로직 집중**
   ```python
   # ✅ GOOD
   class PaperService:
       @staticmethod
       async def create_paper(db, data, user_id):
           # 검증
           # DB 저장
           # 이메일 발송
           # 감사 로그
           return paper
   ```

2. **API는 얇게 유지**
   ```python
   # ✅ GOOD
   @router.post("/papers")
   async def create_paper(data: PaperCreate, db=Depends(get_db), user=Depends(get_current_user)):
       return await PaperService.create_paper(db, data, user.id)
   ```

3. **도메인 예외 사용**
   ```python
   # ✅ GOOD
   class PaperNotFoundException(HTTPException):
       def __init__(self):
           super().__init__(status_code=404, detail="논문을 찾을 수 없습니다")
   ```

4. **Infrastructure 서비스 활용**
   ```python
   # ✅ GOOD
   from app.shared.infrastructure.email.templates import send_welcome_email
   await send_welcome_email(user.email, user.username)
   ```

### ❌ DON'T

1. **API에 비즈니스 로직 작성**
   ```python
   # ❌ BAD
   @router.post("/papers")
   async def create_paper(data: PaperCreate, db=Depends(get_db)):
       # 비즈니스 로직이 API에 있음
       if await db.execute(select(Paper).where(...)):
           raise HTTPException(...)
       paper = Paper(...)
       db.add(paper)
       await db.commit()
       ...
   ```

2. **도메인 간 직접 의존**
   ```python
   # ❌ BAD
   from app.domains.papers.service import PaperService  # X

   class AuthService:
       async def register(self, ...):
           await PaperService.do_something()  # 도메인 간 직접 호출
   ```

3. **중복 코드 작성**
   ```python
   # ❌ BAD - 공통 유틸리티 사용
   from app.shared.utils.validators import validate_email
   ```

---

## 다음 단계

1. **Auth 도메인 참고하여 Papers 도메인 이전**
2. **Analysis 도메인 이전 (RAG 포함)**
3. **Subscriptions 도메인 이전 및 거대 파일 분할**
4. **Admin 도메인 이전 및 거대 파일 분할**
5. **단위/통합 테스트 작성**
6. **레거시 구조 제거** (`app/api/v1/endpoints/`, `app/services/` 등)

---

## 참고 자료

- [Auth 도메인 구현](./app/domains/auth/)
- [Shared Infrastructure](./app/shared/infrastructure/)
- [REFACTORING_GUIDE.md](./REFACTORING_GUIDE.md)
- [DATABASE.md](./DATABASE.md)

**작성자**: BioscopeAI Team
**최종 수정**: 2025-01-18
