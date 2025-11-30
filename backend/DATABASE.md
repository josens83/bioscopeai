# BioscopeAI 데이터베이스 관리 가이드

프로덕션 환경을 위한 데이터베이스 구축, 관리, 백업/복구 가이드

---

## 목차

1. [데이터베이스 아키텍처](#데이터베이스-아키텍처)
2. [초기 설정](#초기-설정)
3. [마이그레이션 관리](#마이그레이션-관리)
4. [백업 및 복구](#백업-및-복구)
5. [성능 최적화](#성능-최적화)
6. [모니터링](#모니터링)
7. [트러블슈팅](#트러블슈팅)

---

## 데이터베이스 아키텍처

### 스키마 개요

BioscopeAI는 다음과 같은 주요 테이블로 구성되어 있습니다:

#### 핵심 테이블
- **users** - 사용자 계정 (인증, 프로필)
- **subscriptions** - 구독 정보
- **subscription_plans** - 구독 플랜
- **papers** - 논문 정보
- **analyses** - 분석 결과
- **usages** - 사용량 추적

#### 보안 및 관리
- **two_factor_auth** - 2단계 인증
- **api_keys** - API 키 관리
- **audit_logs** - 감사 로그
- **terms_acceptances** - 약관 동의 기록
- **terms_versions** - 약관 버전 관리

#### 마케팅 및 결제
- **promotion_codes** - 프로모션 코드
- **promotion_code_usages** - 프로모션 사용 기록

### Connection Pool 설정

```python
# app/core/database.py
pool_size=10              # 기본 연결 수
max_overflow=20           # 추가 가능한 최대 연결 수
pool_timeout=30           # 연결 대기 시간 (초)
pool_recycle=3600         # 1시간마다 연결 재활용
pool_pre_ping=True        # 연결 사용 전 health check
```

**프로덕션 권장 설정:**
- 작은 서비스: `pool_size=10, max_overflow=20`
- 중형 서비스: `pool_size=20, max_overflow=40`
- 대형 서비스: `pool_size=50, max_overflow=100`

---

## 초기 설정

### 1. 환경 변수 설정

`.env` 파일에 데이터베이스 설정 추가:

```bash
# PostgreSQL (프로덕션 권장)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/bioscopeai

# Connection Pool 설정
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

### 2. 자동 설정 스크립트 실행

```bash
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
```

이 스크립트는 다음을 수행합니다:
1. 환경 변수 확인
2. Python 의존성 확인
3. 데이터베이스 연결 테스트
4. 마이그레이션 초기화
5. 마이그레이션 적용
6. 백업 디렉토리 생성

### 3. 수동 설정 (선택사항)

```bash
# 1. 데이터베이스 연결 확인
python scripts/db_migrate.py check

# 2. 마이그레이션 테이블 초기화
python scripts/db_migrate.py init

# 3. 현재 버전 확인
python scripts/db_migrate.py current

# 4. 테이블 목록 확인
python scripts/db_migrate.py tables

# 5. 인덱스 확인
python scripts/db_migrate.py indexes

# 6. 외래 키 확인
python scripts/db_migrate.py fkeys
```

---

## 마이그레이션 관리

### 마이그레이션 파일 목록

```
alembic/versions/
├── 001_initial_migration.py         # 기본 테이블 생성
├── 002_add_indexes.py                # 인덱스 추가
├── 003_add_user_verification.py     # 이메일 인증
├── 004_add_usage_tracking.py        # 사용량 추적
├── 005_add_role_and_audit_logs.py   # 역할 및 감사 로그
├── 006_add_api_keys.py               # API 키 관리
├── 007_add_terms_acceptance.py      # 약관 동의
├── 008_add_promotion_codes.py       # 프로모션 코드
└── 009_add_two_factor_auth.py       # 2단계 인증
```

### 마이그레이션 적용

```bash
# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade 005

# 한 단계 업그레이드
alembic upgrade +1

# 현재 버전 확인
alembic current

# 마이그레이션 히스토리
alembic history
```

### 마이그레이션 다운그레이드

```bash
# 한 단계 다운그레이드
alembic downgrade -1

# 특정 버전으로 다운그레이드
alembic downgrade 004

# 전체 초기화
alembic downgrade base
```

---

## 백업 및 복구

### 전체 백업

```bash
# 전체 데이터베이스 백업
python scripts/db_backup.py backup

# 백업 파일: backups/backup_YYYYMMDD_HHMMSS.sql
```

### 특정 테이블 백업

```bash
# 사용자 테이블만 백업
python scripts/db_backup.py backup --tables users two_factor_auth
```

### JSON 내보내기

```bash
# 모든 데이터를 JSON으로 내보내기
python scripts/db_backup.py export-json

# 출력: backups/data_export_YYYYMMDD_HHMMSS.json
```

### 백업 목록 조회

```bash
python scripts/db_backup.py list
```

### 복구

```bash
# 백업 파일로부터 복구
python scripts/db_backup.py restore backups/backup_20240116_120000.sql

# ⚠️ 주의: 기존 데이터가 삭제됩니다!
```

### 백업 자동화 (Cron)

```bash
# crontab -e
# 매일 오전 3시에 백업
0 3 * * * cd /path/to/backend && python scripts/db_backup.py backup

# 매주 일요일 오전 2시에 JSON 내보내기
0 2 * * 0 cd /path/to/backend && python scripts/db_backup.py export-json
```

---

## 성능 최적화

### 1. 인덱스 전략

현재 적용된 주요 인덱스:

```sql
-- 사용자 관련
CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_username ON users(username);

-- 구독 관련
CREATE INDEX ix_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX ix_subscriptions_status ON subscriptions(status);

-- 논문 및 분석
CREATE INDEX ix_papers_user_id ON papers(user_id);
CREATE INDEX ix_analyses_user_id ON analyses(user_id);
CREATE INDEX ix_analyses_paper_id ON analyses(paper_id);

-- API 키
CREATE INDEX ix_api_keys_key ON api_keys(key);
CREATE INDEX ix_api_keys_user_id ON api_keys(user_id);

-- 감사 로그
CREATE INDEX ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX ix_audit_logs_timestamp ON audit_logs(timestamp);
```

### 2. 쿼리 최적화

```sql
-- 느린 쿼리 확인 (PostgreSQL)
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 테이블 크기 확인
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. Connection Pool 모니터링

```python
# Health check 엔드포인트에서 확인
GET /api/v1/health/detailed

{
  "checks": {
    "database": {
      "pool_size": 10,
      "checked_in_connections": 8,
      "checked_out_connections": 2,
      "overflow_connections": 0,
      "total_connections": 10
    }
  }
}
```

### 4. VACUUM 및 ANALYZE (PostgreSQL)

```sql
-- 전체 VACUUM
VACUUM ANALYZE;

-- 특정 테이블 VACUUM
VACUUM ANALYZE users;

-- 자동 VACUUM 설정 확인
SHOW autovacuum;
```

---

## 모니터링

### Health Check 엔드포인트

```bash
# 기본 health check
curl http://localhost:8000/api/v1/health

# 상세 health check (DB, Redis, 시스템 리소스)
curl http://localhost:8000/api/v1/health/detailed

# Kubernetes readiness probe
curl http://localhost:8000/api/v1/health/ready

# Kubernetes liveness probe
curl http://localhost:8000/api/v1/health/live
```

### 데이터베이스 통계

```bash
# 스키마 전체 검증
python scripts/db_migrate.py check

# 테이블 목록
python scripts/db_migrate.py tables

# 인덱스 목록
python scripts/db_migrate.py indexes

# 외래 키 목록
python scripts/db_migrate.py fkeys
```

### 로그 모니터링

```python
# app/core/logging.py에서 설정된 로거 사용
from app.core.logging import app_logger as logger

# DB 연결 로그
logger.info("데이터베이스 연결 성공")

# DB 에러 로그
logger.error(f"데이터베이스 오류: {e}")
```

---

## 트러블슈팅

### 연결 풀 고갈

**증상:** `QueuePool limit of size X overflow Y reached, connection timed out`

**해결:**
```python
# config.py에서 pool 크기 증가
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
```

### 끊긴 연결 (Lost connection)

**증상:** `Lost connection to MySQL server during query`

**해결:**
- `pool_pre_ping=True` 설정 확인 (이미 적용됨)
- `pool_recycle` 값 조정 (현재 3600초)

### 마이그레이션 충돌

**증상:** `Multiple head revisions are present`

**해결:**
```bash
# 마이그레이션 히스토리 확인
alembic history

# 병합 마이그레이션 생성
alembic merge heads
```

### 데이터베이스 잠금 (Lock timeout)

**증상:** `Lock wait timeout exceeded`

**해결:**
```sql
-- 현재 실행 중인 쿼리 확인
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- 오래 실행 중인 쿼리 종료
SELECT pg_terminate_backend(pid);
```

### 디스크 공간 부족

**해결:**
```bash
# 백업 파일 정리
find backups/ -name "backup_*.sql" -mtime +30 -delete

# 로그 파일 정리
find logs/ -name "*.log" -mtime +7 -delete

# PostgreSQL VACUUM으로 공간 회수
VACUUM FULL;
```

---

## 프로덕션 체크리스트

배포 전 확인 사항:

- [ ] DATABASE_URL이 프로덕션 DB를 가리키는지 확인
- [ ] Connection pool 설정이 적절한지 확인
- [ ] 모든 마이그레이션이 적용되었는지 확인
- [ ] 인덱스가 제대로 생성되었는지 확인
- [ ] 백업 자동화 설정 (cron)
- [ ] Health check 엔드포인트 테스트
- [ ] DB 연결 모니터링 설정
- [ ] 느린 쿼리 로깅 활성화
- [ ] 자동 VACUUM 설정 확인
- [ ] DB 사용자 권한 최소화 (least privilege)
- [ ] SSL/TLS 연결 활성화 (프로덕션)
- [ ] 백업 복구 테스트 수행

---

## 추가 리소스

- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [Alembic 마이그레이션 가이드](https://alembic.sqlalchemy.org/)
- [FastAPI 데이터베이스 가이드](https://fastapi.tiangolo.com/tutorial/sql-databases/)

---

**작성일:** 2024-01-16
**버전:** 1.0.0
**마지막 업데이트:** 2024-01-16
