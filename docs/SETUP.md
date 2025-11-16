# BioscopeAI 설치 가이드

## 개발 환경 설정

### 1. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
```

`.env` 파일을 편집하여 필요한 값들을 입력:
- OpenAI API 키
- Stripe 키
- PubMed 이메일 및 API 키
- 데이터베이스 URL
- JWT Secret Key

### 2. Docker로 실행

```bash
docker-compose up -d
```

서비스 접속:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. 로컬 개발 환경

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 구독 플랜 초기 데이터

데이터베이스에 구독 플랜을 추가해야 합니다:

```sql
INSERT INTO subscription_plans (name, tier, price, max_papers, max_analyses_per_month, max_comparison_papers, is_active)
VALUES
('Free', 'free', 0, 10, 20, 2, true),
('Basic', 'basic', 9.99, 50, 100, 5, true),
('Premium', 'premium', 29.99, 200, 500, 10, true),
('Enterprise', 'enterprise', 99.99, 1000, 2000, 10, true);
```

## API 사용 예시

### 1. 회원가입

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. 로그인

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 3. 논문 검색

```bash
curl -X POST http://localhost:8000/api/v1/papers/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "cancer immunotherapy",
    "max_results": 10
  }'
```

## 문제 해결

### 포트 충돌
기본 포트(3000, 8000, 5432, 6379)가 이미 사용 중이면 `docker-compose.yml`에서 변경하세요.

### 데이터베이스 마이그레이션
```bash
docker-compose exec backend alembic upgrade head
```

### 로그 확인
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```
