# BioscopeAI API Documentation

## Overview

BioscopeAI는 AI 기반 생물의학 논문 분석 플랫폼입니다. 이 문서는 API 사용법과 엔드포인트에 대한 상세 정보를 제공합니다.

## Base URL

| 환경 | URL |
|------|-----|
| 로컬 개발 | `http://localhost:8000` |
| 스테이징 | `https://staging.bioscopeai.com` |
| 프로덕션 | `https://api.bioscopeai.com` |

## Authentication

### JWT Bearer Token

대부분의 API 엔드포인트는 JWT 토큰 인증이 필요합니다.

```bash
# 1. 로그인하여 토큰 획득
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'

# 응답:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "user": {...}
# }

# 2. API 요청 시 Authorization 헤더에 토큰 포함
curl -X GET "http://localhost:8000/api/v1/papers" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### API Key (개발자용)

개발자 설정에서 API 키를 생성하여 사용할 수 있습니다.

```bash
curl -X GET "http://localhost:8000/api/v1/papers" \
  -H "X-API-Key: your-api-key-here"
```

## Rate Limiting

API 요청은 Rate Limiting이 적용됩니다:

| 엔드포인트 | 제한 |
|------------|------|
| 일반 API | 10 req/min |
| 인증 API | 5-10 req/min |
| AI 분석 | 플랜별 월간 한도 |

Rate Limit 정보는 응답 헤더에 포함됩니다:
- `X-RateLimit-Limit`: 최대 요청 수
- `X-RateLimit-Remaining`: 남은 요청 수
- `X-RateLimit-Reset`: 리셋 시간 (Unix timestamp)

## Error Responses

모든 에러는 일관된 형식으로 반환됩니다:

```json
{
  "error": {
    "message": "에러 메시지",
    "code": "ErrorCode",
    "details": { "추가 정보": "..." }
  }
}
```

### 일반적인 에러 코드

| HTTP 코드 | 에러 코드 | 설명 |
|-----------|-----------|------|
| 400 | `ValidationError` | 입력값 검증 실패 |
| 401 | `Unauthorized` | 인증 필요 또는 토큰 만료 |
| 403 | `Forbidden` | 권한 없음 |
| 404 | `NotFound` | 리소스를 찾을 수 없음 |
| 409 | `DuplicateError` | 중복 데이터 |
| 429 | `RateLimitExceeded` | 요청 한도 초과 |
| 500 | `InternalServerError` | 서버 내부 오류 |

---

## API Endpoints

### Health Check

#### GET /api/v1/health
시스템 상태 확인

```bash
curl http://localhost:8000/api/v1/health
```

응답:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

---

### Authentication (인증)

#### POST /api/v1/auth/register
회원가입

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "full_name": "홍길동"
  }'
```

#### POST /api/v1/auth/login
로그인

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

#### POST /api/v1/auth/verify-email
이메일 인증

#### POST /api/v1/auth/password-reset/request
비밀번호 재설정 요청

#### POST /api/v1/auth/password-reset/confirm
비밀번호 재설정 확인

#### GET /api/v1/auth/me
현재 사용자 정보 조회

---

### Papers (논문)

#### GET /api/v1/papers
저장된 논문 목록 조회

```bash
curl "http://localhost:8000/api/v1/papers?page=1&size=20" \
  -H "Authorization: Bearer <token>"
```

쿼리 파라미터:
- `page`: 페이지 번호 (기본값: 1)
- `size`: 페이지 크기 (기본값: 20, 최대: 100)
- `search`: 검색어 (제목, 초록에서 검색)
- `sort_by`: 정렬 필드 (`created_at`, `publication_date`, `title`)
- `order`: 정렬 순서 (`asc`, `desc`)

#### POST /api/v1/papers
새 논문 저장

```bash
curl -X POST "http://localhost:8000/api/v1/papers" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "논문 제목",
    "authors": "저자1, 저자2",
    "abstract": "초록 내용...",
    "journal": "Nature",
    "publication_date": "2024-01-15",
    "doi": "10.1234/example"
  }'
```

#### GET /api/v1/papers/{paper_id}
특정 논문 조회

#### PUT /api/v1/papers/{paper_id}
논문 정보 수정

#### DELETE /api/v1/papers/{paper_id}
논문 삭제

#### GET /api/v1/papers/search/pubmed
PubMed 검색

```bash
curl "http://localhost:8000/api/v1/papers/search/pubmed?query=cancer+treatment&max_results=10" \
  -H "Authorization: Bearer <token>"
```

#### POST /api/v1/papers/{paper_id}/save-from-pubmed
PubMed 검색 결과를 내 논문으로 저장

#### POST /api/v1/papers/upload-pdf
PDF 업로드

```bash
curl -X POST "http://localhost:8000/api/v1/papers/upload-pdf" \
  -H "Authorization: Bearer <token>" \
  -F "file=@paper.pdf"
```

---

### Analysis (AI 분석)

#### POST /api/v1/analysis/qa
논문에 대한 Q&A

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/qa" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": 1,
    "question": "이 논문의 주요 발견은 무엇인가요?"
  }'
```

응답:
```json
{
  "answer": "이 논문의 주요 발견은...",
  "sources": [
    {"page": 3, "text": "관련 텍스트..."},
    {"page": 7, "text": "관련 텍스트..."}
  ],
  "confidence": 0.92
}
```

#### POST /api/v1/analysis/summarize
논문 요약

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/summarize" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_id": 1,
    "style": "brief"  // "brief", "detailed", "bullet_points"
  }'
```

#### POST /api/v1/analysis/compare
논문 비교

```bash
curl -X POST "http://localhost:8000/api/v1/analysis/compare" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "paper_ids": [1, 2, 3]
  }'
```

#### GET /api/v1/analysis/history
분석 이력 조회

---

### Subscription (구독)

#### GET /api/v1/subscriptions/plans
사용 가능한 플랜 목록

```bash
curl "http://localhost:8000/api/v1/subscriptions/plans"
```

응답:
```json
{
  "plans": [
    {
      "id": 1,
      "tier": "free",
      "name": "Free",
      "price": 0,
      "max_papers": 10,
      "max_analyses_per_month": 5
    },
    {
      "id": 2,
      "tier": "basic",
      "name": "Basic",
      "price": 9.99,
      "max_papers": 100,
      "max_analyses_per_month": 50
    }
  ]
}
```

#### GET /api/v1/subscriptions/my
내 구독 정보

#### POST /api/v1/subscriptions/checkout
구독 결제 시작 (Stripe Checkout)

```bash
curl -X POST "http://localhost:8000/api/v1/subscriptions/checkout" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "basic"
  }'
```

#### POST /api/v1/subscriptions/cancel
구독 취소

---

### Usage (사용량)

#### GET /api/v1/usage/my
내 사용량 조회

```bash
curl "http://localhost:8000/api/v1/usage/my" \
  -H "Authorization: Bearer <token>"
```

응답:
```json
{
  "plan": "basic",
  "papers": {
    "used": 45,
    "limit": 100
  },
  "analyses": {
    "used": 23,
    "limit": 50,
    "reset_at": "2024-02-01T00:00:00Z"
  }
}
```

#### GET /api/v1/usage/features
기능 접근 권한 확인

---

### Admin (관리자)

> 관리자 권한이 필요합니다.

#### GET /api/v1/admin/users
사용자 목록

#### GET /api/v1/admin/analytics
비즈니스 분석

#### GET /api/v1/admin/metrics
시스템 메트릭

---

## Webhooks

### Stripe Webhook

Stripe 결제 이벤트를 처리합니다.

```
POST /api/v1/subscriptions/webhook
```

Stripe Dashboard에서 웹훅 엔드포인트를 설정하고, `STRIPE_WEBHOOK_SECRET` 환경 변수를 설정하세요.

---

## SDK & Libraries

### Python

```python
import requests

class BioscopeAI:
    def __init__(self, api_url, token=None):
        self.api_url = api_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def login(self, email, password):
        response = requests.post(
            f"{self.api_url}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        self.headers["Authorization"] = f"Bearer {self.token}"
        return data

    def get_papers(self, page=1, size=20):
        response = requests.get(
            f"{self.api_url}/api/v1/papers",
            params={"page": page, "size": size},
            headers=self.headers
        )
        return response.json()

    def analyze(self, paper_id, question):
        response = requests.post(
            f"{self.api_url}/api/v1/analysis/qa",
            json={"paper_id": paper_id, "question": question},
            headers=self.headers
        )
        return response.json()


# 사용 예
client = BioscopeAI("http://localhost:8000")
client.login("user@example.com", "password")
papers = client.get_papers()
answer = client.analyze(1, "이 논문의 주요 발견은?")
```

### JavaScript/TypeScript

```typescript
class BioscopeAI {
  private apiUrl: string;
  private token: string | null = null;

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.apiUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  private get headers() {
    return {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
    };
  }

  async getPapers(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    const response = await fetch(`${this.apiUrl}/api/v1/papers?${params}`, {
      headers: this.headers,
    });
    return response.json();
  }

  async analyze(paperId: number, question: string) {
    const response = await fetch(`${this.apiUrl}/api/v1/analysis/qa`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ paper_id: paperId, question }),
    });
    return response.json();
  }
}

// 사용 예
const client = new BioscopeAI('http://localhost:8000');
await client.login('user@example.com', 'password');
const papers = await client.getPapers();
const answer = await client.analyze(1, '이 논문의 주요 발견은?');
```

---

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Support

문의사항이 있으시면 다음 채널을 이용해주세요:

- GitHub Issues: https://github.com/josens83/bioscopeai/issues
- Email: support@bioscopeai.com
