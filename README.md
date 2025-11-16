# 🧬 BioscopeAI

<div align="center">

**AI 기반 생물의학 논문 분석 플랫폼**

RAG(검색증강생성) 기술로 논문을 검색하고, 분석하고, 비교하세요.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)

[빠른 시작](#-빠른-시작) • [기능](#-주요-기능) • [데모](#-데모-계정) • [문서](#-문서) • [기여](#-기여하기)

</div>

---

## 🌟 주요 기능

### 📚 논문 관리
- **PubMed 검색**: 최신 생물의학 논문 실시간 검색
- **PDF 업로드**: 논문 PDF 업로드 및 자동 텍스트 추출
- **메타데이터 관리**: 제목, 저자, 초록, DOI 등 자동 파싱
- **개인 라이브러리**: 논문 저장 및 관리

### 🤖 AI 분석
- **질의응답**: RAG 기반 논문 내용 질문답변
- **자동 요약**: GPT-4로 논문 핵심 내용 요약
- **비교 분석**: 최대 10개 논문 동시 비교
- **트렌드 분석**: 연구 키워드 및 트렌드 시각화

### 💳 구독 서비스
- **4가지 플랜**: Free, Basic ($9.99), Premium ($29.99), Enterprise ($99.99)
- **Stripe 결제**: 안전한 결제 시스템
- **유연한 구독**: 언제든 업그레이드/다운그레이드/취소 가능

### 🌐 멀티 플랫폼
- **웹 앱**: React + TypeScript 반응형 웹
- **모바일 앱**: React Native + Expo (iOS/Android)
- **REST API**: 완전한 API 제공

## 🏗️ 기술 스택

### Backend
```
FastAPI • Python 3.11 • PostgreSQL • Redis
LangChain • OpenAI GPT-4 • FAISS • BioBERT
Stripe • Alembic • SQLAlchemy • Pydantic
```

### Frontend
```
React 18 • TypeScript • Tailwind CSS
React Query • Zustand • Axios • React Router
React Markdown • Vite
```

### Mobile
```
React Native • Expo • TypeScript
React Navigation • React Query
expo-secure-store
```

### Infrastructure
```
Docker • Docker Compose • Nginx
GitHub Actions • Alembic
```

## 🚀 빠른 시작

### 사전 요구사항
- Docker & Docker Compose
- Git
- (선택) Node.js 18+ (로컬 개발용)

### 5분 안에 실행하기

```bash
# 1. 저장소 클론
git clone https://github.com/josens83/bioscopeai.git
cd bioscopeai

# 2. 환경 변수 설정
cp backend/.env.example backend/.env
# .env 파일을 열어 다음 값들을 입력하세요:
# - OPENAI_API_KEY (필수)
# - SECRET_KEY, JWT_SECRET_KEY (필수)
# - PUBMED_EMAIL (필수)
# - STRIPE_SECRET_KEY (선택)

# 3. Docker로 실행
docker-compose up -d

# 4. 데이터베이스 초기화
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/seed_data.py

# 5. 접속!
# 웹: http://localhost:3000
# API: http://localhost:8000/docs
```

자세한 내용은 [빠른 시작 가이드](./docs/QUICK_START.md)를 참고하세요.

## 🎮 데모 계정

로그인 없이 바로 체험하세요:

```
이메일: demo@bioscopeai.com
비밀번호: demo1234
```

또는 관리자 계정:

```
이메일: admin@bioscopeai.com
비밀번호: admin1234
```

## 📱 모바일 앱 실행

```bash
cd mobile
npm install
npm start
# Expo Go 앱으로 QR 코드 스캔
```

**주의**: `mobile/app.json`의 `apiUrl`을 실제 백엔드 주소로 변경하세요.

## 📊 프로젝트 구조

```
bioscopeai/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # REST API 엔드포인트
│   │   │   └── v1/      # API v1 (auth, papers, analysis, subscriptions)
│   │   ├── core/        # 핵심 설정 (config, security, database)
│   │   ├── models/      # SQLAlchemy 모델
│   │   ├── services/    # 비즈니스 로직 (PubMed, PDF, Stripe)
│   │   ├── rag/         # RAG 시스템 (embeddings, vectorstore, pipeline)
│   │   └── schemas/     # Pydantic 스키마
│   ├── alembic/         # 데이터베이스 마이그레이션
│   ├── scripts/         # 유틸리티 스크립트 (seed_data.py)
│   └── requirements.txt
├── frontend/            # React 웹 앱
│   ├── src/
│   │   ├── components/  # 재사용 컴포넌트
│   │   ├── pages/       # 페이지 (Dashboard, Papers, Analysis, Subscription)
│   │   ├── services/    # API 클라이언트
│   │   ├── hooks/       # React Query hooks
│   │   └── store/       # Zustand 상태관리
│   └── package.json
├── mobile/              # React Native 모바일 앱
│   ├── src/
│   │   ├── screens/     # 화면 (Login, Dashboard, Papers, Analysis, Profile)
│   │   ├── navigation/  # 네비게이션 (Stack + Bottom Tabs)
│   │   ├── services/    # API 클라이언트
│   │   └── store/       # 인증 상태관리
│   └── package.json
├── docs/                # 문서
│   ├── QUICK_START.md   # 빠른 시작 가이드
│   ├── SETUP.md         # 상세 설치 가이드
│   └── API.md           # API 문서
├── docker-compose.yml   # Docker Compose 설정
├── nginx.conf           # Nginx 리버스 프록시 설정
└── README.md
```

## 🔑 환경 변수

필수 환경 변수:

```env
# OpenAI API (필수)
OPENAI_API_KEY=sk-your-key-here

# 보안 (필수)
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 데이터베이스 (Docker 사용 시 기본값 사용)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/bioscopeai
REDIS_URL=redis://redis:6379/0

# PubMed (필수)
PUBMED_EMAIL=your-email@example.com
PUBMED_API_KEY=your-api-key  # 선택

# Stripe (유료 기능 사용 시)
STRIPE_SECRET_KEY=sk_test_your-key
STRIPE_PUBLISHABLE_KEY=pk_test_your-key
STRIPE_WEBHOOK_SECRET=whsec_your-secret
```

## 📚 문서

- **[빠른 시작 가이드](./docs/QUICK_START.md)**: 5분 안에 실행
- **[설치 가이드](./docs/SETUP.md)**: 상세한 설치 및 설정
- **[API 문서](./docs/API.md)**: 완전한 API 레퍼런스
- **[Swagger UI](http://localhost:8000/docs)**: 인터랙티브 API 문서
- **[ReDoc](http://localhost:8000/redoc)**: API 문서 (대안)

## 🧪 개발

### 로컬 개발 환경

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

#### Mobile
```bash
cd mobile
npm install
npm start
```

### 테스트

```bash
# Backend 테스트
cd backend
pytest

# Frontend 테스트
cd frontend
npm test
```

## 📦 배포

### Docker Compose (프로덕션)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Nginx 설정

프로덕션 환경에서는 Nginx를 리버스 프록시로 사용:
- Rate Limiting: API 10req/s, Auth 5req/m
- SSL/TLS 설정
- CORS 처리

자세한 내용은 `nginx.conf` 참고

## 🤝 기여하기

기여를 환영합니다! 다음 단계를 따라주세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들을 사용합니다:

- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [React](https://reactjs.org/)
- [OpenAI](https://openai.com/)
- [Stripe](https://stripe.com/)

## 📞 문의

- **Issues**: [GitHub Issues](https://github.com/josens83/bioscopeai/issues)
- **Email**: support@bioscopeai.com
- **Website**: [bioscopeai.com](https://bioscopeai.com)

## 🗺️ 로드맵

- [x] 논문 검색 및 관리
- [x] AI 질의응답 (RAG)
- [x] 논문 요약
- [x] 논문 비교 분석
- [x] 유료 구독 시스템
- [x] 웹 앱
- [x] 모바일 앱
- [ ] 논문 자동 분류
- [ ] 인용 네트워크 시각화
- [ ] 협업 기능
- [ ] 커스텀 AI 모델 학습
- [ ] 음성 질의응답

---

<div align="center">

**Made with ❤️ by BioscopeAI Team**

⭐ 이 프로젝트가 유용하다면 Star를 눌러주세요!

</div>
