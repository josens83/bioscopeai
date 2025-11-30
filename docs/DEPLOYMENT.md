# BioscopeAI 배포 가이드

이 문서는 BioscopeAI를 프로덕션 환경에 배포하는 방법을 설명합니다.

## 📋 목차

1. [사전 준비](#사전-준비)
2. [Docker Compose 배포](#docker-compose-배포)
3. [AWS 배포](#aws-배포)
4. [GCP 배포](#gcp-배포)
5. [Azure 배포](#azure-배포)
6. [보안 체크리스트](#보안-체크리스트)

## 사전 준비

### 필수 항목

- [ ] 도메인 이름 확보
- [ ] SSL/TLS 인증서 (Let's Encrypt 권장)
- [ ] OpenAI API 키
- [ ] Stripe 프로덕션 키 (결제 기능 사용 시)
- [ ] SMTP 서버 설정 (Gmail 또는 SendGrid 권장) - 결제 이메일 발송에 필수
- [ ] PubMed API 이메일 등록
- [ ] 데이터베이스 백업 전략 수립
- [ ] Sentry 계정 (선택사항, 에러 추적용)

### 환경 변수 설정

`.env.prod.example` 파일을 복사하여 `.env.prod` 생성:

```bash
cp .env.prod.example .env.prod
# 실제 프로덕션 값으로 수정
vim .env.prod
```

**중요**: 모든 SECRET_KEY는 최소 32자 이상의 강력한 랜덤 문자열로 설정하세요.

### 시스템 주요 기능

BioscopeAI는 다음 프로덕션 기능을 포함합니다:

#### 📊 사용량 추적 및 제한
- 플랜별 월간 사용량 자동 추적 (논문 분석, RAG 쿼리, API 호출)
- 사용량 한도 도달 시 자동 차단 및 업그레이드 안내
- 실시간 사용량 조회 API

#### 💳 Stripe 결제 통합
- Basic ($19.99/월), Pro ($99.99/월) 구독 플랜
- 자동 결제 처리 및 웹훅 이벤트 처리
- 결제 실패 시 자동 이메일 알림
- 환불 처리 자동화

#### 📧 자동 이메일 알림
- 결제 영수증 발송
- 결제 실패 알림
- 구독 취소 확인
- 웰컴 이메일 (선택사항)

#### 🛡️ 보안 및 에러 처리
- 전역 예외 핸들러로 일관된 에러 응답
- Sentry 통합으로 실시간 에러 추적
- 환경 설정 자동 검증 (시작 시)
- Rate limiting 및 보안 헤더 적용

#### 📈 관리자 대시보드
- 비즈니스 메트릭 (MRR, ARPU, DAU/MAU, 전환율, 이탈률)
- 사용량 분석 (총 사용량, 평균 사용량, 파워 유저)
- 사용자 통계

## Docker Compose 배포

가장 간단한 배포 방법입니다.

### 1. 서버 준비

```bash
# Ubuntu 22.04 기준
sudo apt update
sudo apt install -y docker.io docker-compose git

# Docker 권한 설정
sudo usermod -aG docker $USER
newgrp docker
```

### 2. 프로젝트 클론

```bash
git clone https://github.com/josens83/bioscopeai.git
cd bioscopeai
```

### 3. 환경 변수 설정

```bash
cp .env.prod.example .env.prod
# 프로덕션 값으로 수정
nano .env.prod
```

### 4. SSL 인증서 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt install certbot

# SSL 인증서 발급
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 인증서 복사
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
```

### 5. Nginx 설정 수정

```bash
# nginx.prod.conf에서 도메인 변경
sed -i 's/yourdomain.com/실제도메인.com/g' nginx.prod.conf
```

### 6. 배포

```bash
# 프로덕션 모드로 실행
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. 데이터베이스 초기화

```bash
# 마이그레이션 실행
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 초기 데이터 생성 (플랜, 데모 계정, 관리자 계정)
docker-compose -f docker-compose.prod.yml exec backend python -m scripts.seed_data
```

초기 데이터에는 다음이 포함됩니다:
- **플랜 제한**: Free, Basic, Pro 플랜별 사용량 제한
- **구독 플랜**: Stripe 연동을 위한 플랜 데이터 (stripe_price_id는 나중에 업데이트 필요)
- **데모 계정**: `demo@bioscopeai.com / demo1234`
- **관리자 계정**: `admin@bioscopeai.com / admin1234` (⚠️ 프로덕션에서 반드시 비밀번호 변경)

### 8. Stripe 설정

```bash
# Stripe 대시보드에서 Product 생성
# 1. https://dashboard.stripe.com/products 접속
# 2. "Add Product" 클릭
# 3. Basic Plan - $19.99/month
# 4. Pro Plan - $99.99/month
# 5. 각 플랜의 Price ID 복사

# 데이터베이스의 stripe_price_id 업데이트
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres bioscopeai <<EOF
UPDATE subscription_plans SET stripe_price_id = 'price_xxx' WHERE tier = 'basic';
UPDATE subscription_plans SET stripe_price_id = 'price_yyy' WHERE tier = 'pro';
EOF

# Stripe 웹훅 설정
# 1. https://dashboard.stripe.com/webhooks 접속
# 2. "Add endpoint" 클릭
# 3. URL: https://yourdomain.com/api/v1/subscriptions/webhook
# 4. Events to send:
#    - invoice.payment_succeeded
#    - invoice.payment_failed
#    - customer.subscription.created
#    - customer.subscription.updated
#    - customer.subscription.deleted
#    - charge.refunded
# 5. Webhook Secret 복사하여 .env.prod의 STRIPE_WEBHOOK_SECRET에 설정
```

### 9. SMTP 이메일 설정 검증

결제 영수증, 결제 실패, 구독 취소 등의 이메일이 자동으로 발송됩니다.

```bash
# 테스트 이메일 발송 (Python 셸에서)
docker-compose -f docker-compose.prod.yml exec backend python
>>> from app.services.email_service import send_email
>>> import asyncio
>>> asyncio.run(send_email("test@example.com", "Test Email", "This is a test"))
```

**Gmail 앱 비밀번호 생성 방법:**
1. Google 계정 관리 > 보안
2. 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 16자리 비밀번호를 SMTP_PASSWORD에 설정

### 10. Sentry 에러 추적 설정 (선택사항)

```bash
# 1. https://sentry.io 가입
# 2. 새 프로젝트 생성 (Python/FastAPI)
# 3. DSN 복사
# 4. .env.prod에 SENTRY_DSN 설정
# 5. 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 11. 접속 확인

```
https://yourdomain.com
https://yourdomain.com/docs  # API 문서
https://yourdomain.com/api/v1/health  # Health check
```

**데모 계정으로 로그인:**
- 이메일: demo@bioscopeai.com
- 비밀번호: demo1234

**관리자 대시보드:**
- 이메일: admin@bioscopeai.com
- 비밀번호: admin1234 (⚠️ 즉시 변경하세요)

## AWS 배포

### AWS ECS (Elastic Container Service) 사용

#### 1. ECR에 이미지 푸시

```bash
# AWS CLI 설치 및 설정
aws configure

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 빌드 및 푸시
docker build -t bioscopeai-backend ./backend
docker tag bioscopeai-backend:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/bioscopeai-backend:latest
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/bioscopeai-backend:latest

# 프론트엔드도 동일하게
docker build -t bioscopeai-frontend ./frontend
docker tag bioscopeai-frontend:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/bioscopeai-frontend:latest
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/bioscopeai-frontend:latest
```

#### 2. RDS PostgreSQL 생성

```bash
# AWS 콘솔에서:
# - RDS > Create Database
# - PostgreSQL 15 선택
# - 프로덕션 템플릿 사용
# - db.t3.medium 이상 권장
# - Multi-AZ 배포 활성화 (고가용성)
# - 백업 자동화 설정
```

#### 3. ElastiCache Redis 생성

```bash
# AWS 콘솔에서:
# - ElastiCache > Create Redis cluster
# - cache.t3.micro 시작 (필요시 확장)
# - 클러스터 모드 비활성화
```

#### 4. ECS 클러스터 생성

```bash
# Fargate 사용 권장
aws ecs create-cluster --cluster-name bioscopeai-cluster
```

#### 5. Task Definition 생성

`ecs-task-definition.json` 파일 생성 후:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

#### 6. ALB (Application Load Balancer) 설정

```bash
# AWS 콘솔에서:
# - EC2 > Load Balancers > Create ALB
# - HTTPS 리스너 추가
# - SSL 인증서 연결 (AWS Certificate Manager 사용)
# - Target Groups 설정
```

#### 7. ECS 서비스 생성

```bash
aws ecs create-service \
  --cluster bioscopeai-cluster \
  --service-name bioscopeai-service \
  --task-definition bioscopeai-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --load-balancers targetGroupArn=YOUR_TARGET_GROUP_ARN,containerName=backend,containerPort=8000
```

### 비용 최적화 팁

- Fargate Spot 사용으로 최대 70% 절감
- Reserved Instances 구매
- Auto Scaling 설정
- CloudWatch 모니터링으로 리소스 최적화

## GCP 배포

### Cloud Run 사용 (서버리스)

#### 1. Google Cloud 설정

```bash
# gcloud CLI 설치
curl https://sdk.cloud.google.com | bash
gcloud init

# 프로젝트 설정
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Artifact Registry에 이미지 푸시

```bash
# Artifact Registry 활성화
gcloud services enable artifactregistry.googleapis.com

# Repository 생성
gcloud artifacts repositories create bioscopeai \
  --repository-format=docker \
  --location=asia-northeast1

# 이미지 빌드 및 푸시
gcloud builds submit --tag asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/bioscopeai/backend ./backend
gcloud builds submit --tag asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/bioscopeai/frontend ./frontend
```

#### 3. Cloud SQL (PostgreSQL) 생성

```bash
gcloud sql instances create bioscopeai-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=asia-northeast1

# 데이터베이스 생성
gcloud sql databases create bioscopeai --instance=bioscopeai-db
```

#### 4. Memorystore (Redis) 생성

```bash
gcloud redis instances create bioscopeai-redis \
  --size=1 \
  --region=asia-northeast1 \
  --redis-version=redis_7_0
```

#### 5. Cloud Run 배포

```bash
# Backend 배포
gcloud run deploy bioscopeai-backend \
  --image asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/bioscopeai/backend \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql+asyncpg://...,REDIS_URL=redis://... \
  --max-instances 10 \
  --memory 512Mi

# Frontend 배포
gcloud run deploy bioscopeai-frontend \
  --image asia-northeast1-docker.pkg.dev/YOUR_PROJECT_ID/bioscopeai/frontend \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

#### 6. Cloud Load Balancer 설정

```bash
# 커스텀 도메인 매핑
gcloud run domain-mappings create --service bioscopeai-frontend --domain yourdomain.com
```

## Azure 배포

### Azure Container Instances 사용

#### 1. Azure CLI 설정

```bash
# Azure CLI 설치
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 로그인
az login
```

#### 2. Container Registry 생성

```bash
# ACR 생성
az acr create --resource-group bioscopeai-rg --name bioscopeaiacr --sku Basic

# 로그인
az acr login --name bioscopeaiacr

# 이미지 푸시
docker tag bioscopeai-backend bioscopeaiacr.azurecr.io/backend:latest
docker push bioscopeaiacr.azurecr.io/backend:latest
```

#### 3. Azure Database for PostgreSQL 생성

```bash
az postgres server create \
  --resource-group bioscopeai-rg \
  --name bioscopeai-db \
  --location koreacentral \
  --admin-user adminuser \
  --admin-password YourPassword123! \
  --sku-name B_Gen5_1 \
  --version 15
```

#### 4. Azure Cache for Redis 생성

```bash
az redis create \
  --location koreacentral \
  --name bioscopeai-redis \
  --resource-group bioscopeai-rg \
  --sku Basic \
  --vm-size c0
```

#### 5. Container Instances 배포

```bash
az container create \
  --resource-group bioscopeai-rg \
  --name bioscopeai-backend \
  --image bioscopeaiacr.azurecr.io/backend:latest \
  --cpu 1 \
  --memory 1 \
  --registry-login-server bioscopeaiacr.azurecr.io \
  --registry-username $(az acr credential show --name bioscopeaiacr --query username -o tsv) \
  --registry-password $(az acr credential show --name bioscopeaiacr --query passwords[0].value -o tsv) \
  --dns-name-label bioscopeai-api \
  --ports 8000 \
  --environment-variables DATABASE_URL=... REDIS_URL=...
```

## 보안 체크리스트

### 배포 전 확인사항

- [ ] 모든 SECRET_KEY를 강력한 랜덤 값으로 변경
- [ ] 데이터베이스 비밀번호 변경
- [ ] CORS 설정에서 프로덕션 도메인만 허용
- [ ] DEBUG 모드 비활성화
- [ ] HTTPS 활성화 (HTTP는 HTTPS로 리다이렉트)
- [ ] 방화벽 규칙 설정 (필요한 포트만 개방)
- [ ] 데이터베이스 접근을 애플리케이션 서버로만 제한
- [ ] Rate limiting 활성화 확인
- [ ] 로그 모니터링 설정
- [ ] 백업 자동화 설정
- [ ] 환경 변수를 코드에 하드코딩하지 않음
- [ ] Stripe Webhook Secret 설정
- [ ] HSTS 헤더 활성화
- [ ] SQL Injection 방지 확인
- [ ] XSS 방지 확인

### 모니터링 설정

```bash
# Docker 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend

# 에러 로그 모니터링
tail -f backend/logs/error.log

# 시스템 리소스 모니터링
docker stats
```

### 백업 전략

#### 데이터베이스 백업

```bash
# 자동 백업 스크립트
#!/bin/bash
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres bioscopeai | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

#### Cron 작업 설정

```bash
# 매일 새벽 3시 백업
0 3 * * * /path/to/backup-script.sh
```

## 트러블슈팅

### 일반적인 문제

**문제: 데이터베이스 연결 실패**
```bash
# 연결 확인
docker-compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import engine; print('Connected!')"
```

**문제: Out of Memory**
```bash
# 메모리 사용량 확인
docker stats

# 메모리 제한 설정 (docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 512M
```

**문제: SSL 인증서 만료**
```bash
# Let's Encrypt 자동 갱신
sudo certbot renew
```

## 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [AWS ECS 문서](https://docs.aws.amazon.com/ecs/)
- [GCP Cloud Run 문서](https://cloud.google.com/run/docs)
- [Azure Container Instances 문서](https://docs.microsoft.com/azure/container-instances/)

## 지원

배포 관련 문제가 있으시면:
- GitHub Issues: https://github.com/josens83/bioscopeai/issues
- Email: support@bioscopeai.com
