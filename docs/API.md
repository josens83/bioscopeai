# API 문서

## 기본 정보

- **Base URL**: `http://localhost:8000/api/v1`
- **인증**: Bearer Token (JWT)
- **Content-Type**: `application/json`

## 인증 (Authentication)

### 회원가입

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name"
}
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "created_at": "2025-11-16T00:00:00Z"
}
```

### 로그인

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## 논문 (Papers)

### PubMed 검색

```http
POST /papers/search
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "query": "cancer immunotherapy",
  "max_results": 20,
  "sort": "relevance"
}
```

### 논문 목록 조회

```http
GET /papers
Authorization: Bearer {access_token}
```

### 논문 저장

```http
POST /papers
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Paper Title",
  "authors": "Author1, Author2",
  "abstract": "Abstract text...",
  "pubmed_id": "12345678",
  "doi": "10.1234/example"
}
```

### PDF 업로드

```http
POST /papers/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [PDF file]
title: "Paper Title" (optional)
authors: "Author Names" (optional)
```

### 논문 삭제

```http
DELETE /papers/{paper_id}
Authorization: Bearer {access_token}
```

## AI 분석 (Analysis)

### 질의응답

```http
POST /analysis/question
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "question": "What is the main finding?",
  "paper_id": 1,
  "k": 5
}
```

**Response**:
```json
{
  "analysis_id": 123,
  "answer": "The main finding is...",
  "sources": [
    {
      "paper_id": 1,
      "text": "Relevant excerpt...",
      "score": 0.95
    }
  ],
  "confidence": 0.89
}
```

### 논문 요약

```http
POST /analysis/summarize/{paper_id}
Authorization: Bearer {access_token}
```

**Response**:
```json
{
  "analysis_id": 124,
  "summary": "This paper investigates..."
}
```

### 논문 비교

```http
POST /analysis/compare
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "paper_ids": [1, 2, 3]
}
```

**Response**:
```json
{
  "analysis_id": 125,
  "comparison": "| Aspect | Paper 1 | Paper 2 | Paper 3 |\n|..."
}
```

### 분석 기록 조회

```http
GET /analysis?analysis_type=qa&skip=0&limit=20
Authorization: Bearer {access_token}
```

## 구독 (Subscriptions)

### 구독 플랜 목록

```http
GET /subscriptions/plans
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Free",
    "tier": "free",
    "price": 0.0,
    "max_papers": 10,
    "max_analyses_per_month": 20,
    "max_comparison_papers": 2
  },
  {
    "id": 2,
    "name": "Basic",
    "tier": "basic",
    "price": 9.99,
    "max_papers": 50,
    "max_analyses_per_month": 100,
    "max_comparison_papers": 5
  }
]
```

### 내 구독 조회

```http
GET /subscriptions/my
Authorization: Bearer {access_token}
```

### 구독 생성

```http
POST /subscriptions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "tier": "basic",
  "payment_method_id": "pm_xxx"
}
```

### 구독 취소

```http
POST /subscriptions/cancel
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "at_period_end": true
}
```

## 에러 응답

모든 에러는 다음 형식으로 반환됩니다:

```json
{
  "detail": "Error message here"
}
```

### HTTP 상태 코드

- `200 OK`: 성공
- `201 Created`: 생성 성공
- `204 No Content`: 삭제 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 필요
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `500 Internal Server Error`: 서버 오류

## Rate Limiting

- **일반 API**: 10 requests/second
- **인증 API**: 5 requests/minute

Rate limit 초과 시:
```json
{
  "detail": "Too many requests. Please try again later."
}
```

## Webhook (Stripe)

```http
POST /subscriptions/webhook
Content-Type: application/json
Stripe-Signature: {signature}

{
  "type": "customer.subscription.updated",
  "data": {...}
}
```

## 전체 API 문서

서버 실행 후 다음 URL에서 인터랙티브 API 문서를 확인하세요:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
