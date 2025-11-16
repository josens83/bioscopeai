# BioscopeAI - 생물의학 논문 분석 플랫폼

RAG(검색증강생성) 기술을 활용한 AI 기반 생물의학 논문 분석 및 비교 플랫폼입니다.

## 주요 기능

- 📚 **논문 검색 및 분석**: PubMed API 연동으로 최신 논문 검색
- 🤖 **AI 챗봇**: 논문 내용에 대한 질의응답
- 📊 **비교 분석**: 최대 10개 논문 동시 비교
- 📈 **트렌드 분석**: 연구 트렌드 시각화
- 💳 **유료 서비스**: Stripe 기반 구독 모델
- 🔒 **보안**: JWT 기반 인증 및 권한 관리

## 기술 스택

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL (데이터베이스)
- Redis (캐싱)
- LangChain (RAG 파이프라인)
- FAISS (벡터 검색)
- BioBERT/PubMedBERT (임베딩)

### Frontend
- React 18 + TypeScript
- Tailwind CSS
- React Query
- Zustand (상태 관리)

### Mobile
- React Native
- Expo

### DevOps
- Docker & Docker Compose
- Nginx
- GitHub Actions (CI/CD)

## 프로젝트 구조

```
bioscopeai/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 엔드포인트
│   │   ├── core/        # 설정, 보안
│   │   ├── models/      # 데이터베이스 모델
│   │   ├── services/    # 비즈니스 로직
│   │   └── rag/         # RAG 시스템
│   ├── tests/
│   └── requirements.txt
├── frontend/            # React 웹 앱
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── hooks/
│   └── package.json
├── mobile/              # React Native 모바일 앱
│   ├── src/
│   └── package.json
├── docs/                # 문서
└── docker-compose.yml
```

## 시작하기

### 환경 변수 설정

```bash
cp backend/.env.example backend/.env
# .env 파일에 필요한 값 입력
```

### Docker로 실행

```bash
docker-compose up -d
```

### 개별 실행

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API 문서

서버 실행 후 다음 URL에서 API 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 라이선스

MIT License

## 개발자

BioscopeAI Team
