# BioscopeAI - 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1. 사전 요구사항

- Docker & Docker Compose
- Git

### 2. 프로젝트 클론

```bash
git clone https://github.com/josens83/bioscopeai.git
cd bioscopeai
```

### 3. 환경 변수 설정

```bash
cp backend/.env.example backend/.env
```

`.env` 파일을 열어 다음 필수 값들을 입력하세요:

```env
# 필수: OpenAI API 키
OPENAI_API_KEY=sk-your-key-here

# 필수: JWT Secret (랜덤 문자열)
SECRET_KEY=your-random-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# 필수: PubMed 이메일
PUBMED_EMAIL=your-email@example.com

# 선택: Stripe 키 (결제 기능 사용 시)
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret
```

### 4. Docker로 실행

```bash
docker-compose up -d
```

### 5. 데이터베이스 초기화

```bash
# 백엔드 컨테이너 접속
docker-compose exec backend bash

# 마이그레이션 실행
alembic upgrade head

# 초기 데이터 생성
python scripts/seed_data.py

# 컨테이너 나가기
exit
```

### 6. 접속하기

- **웹 앱**: http://localhost:3000
- **API 문서**: http://localhost:8000/docs
- **Backend**: http://localhost:8000

### 7. 데모 계정으로 로그인

```
이메일: demo@bioscopeai.com
비밀번호: demo1234
```

또는

```
이메일: admin@bioscopeai.com
비밀번호: admin1234
```

## 📱 모바일 앱 실행

```bash
cd mobile
npm install
npm start
```

Expo Go 앱으로 QR 코드를 스캔하세요.

**중요**: `mobile/app.json`의 `apiUrl`을 실제 백엔드 주소로 변경하세요.

## 🧪 주요 기능 테스트

### 1. 논문 검색
1. "논문" 탭 클릭
2. "PubMed 검색" 탭 선택
3. 검색어 입력 (예: "cancer immunotherapy")
4. 검색 결과를 내 라이브러리에 저장

### 2. AI 분석
1. "분석" 탭 클릭
2. "질의응답" 탭에서 질문 입력
3. AI의 답변 확인

### 3. 논문 비교
1. "분석" 탭 > "논문 비교"
2. 2개 이상 논문 선택
3. 비교 분석 실행

## 🛠️ 문제 해결

### 포트가 이미 사용 중인 경우

`docker-compose.yml`에서 포트 번호를 변경하세요:

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # 3000 → 3001로 변경
```

### 데이터베이스 연결 오류

```bash
docker-compose down
docker-compose up -d db
# 10초 대기
docker-compose up -d
```

### 로그 확인

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📚 다음 단계

- [전체 설치 가이드](./SETUP.md)
- [API 문서](http://localhost:8000/docs)
- [구독 플랜 설정](#)
- [프로덕션 배포 가이드](#)

## 💬 도움이 필요하신가요?

- GitHub Issues: https://github.com/josens83/bioscopeai/issues
- 이메일: support@bioscopeai.com
