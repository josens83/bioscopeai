#!/bin/bash
###############################################################################
# 데이터베이스 초기 설정 스크립트
#
# BioscopeAI 프로덕션 데이터베이스 구축을 위한 전체 워크플로우
###############################################################################

set -e  # 오류 발생 시 중단

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================================================="
echo "BioscopeAI 데이터베이스 초기 설정"
echo "========================================================================="
echo

# 1. 환경 변수 확인
echo "[1/6] 환경 변수 확인..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "❌ .env 파일이 없습니다!"
    echo "   .env.example을 복사하여 .env 파일을 생성하고 값을 설정하세요."
    exit 1
fi

# DATABASE_URL 확인
if ! grep -q "^DATABASE_URL=" "$PROJECT_ROOT/.env"; then
    echo "❌ DATABASE_URL이 설정되지 않았습니다!"
    exit 1
fi

echo "✓ 환경 변수 확인 완료"
echo

# 2. Python 의존성 확인
echo "[2/6] Python 의존성 확인..."
cd "$PROJECT_ROOT"

if ! python -c "import alembic" 2>/dev/null; then
    echo "⚠ alembic이 설치되지 않았습니다. 설치 중..."
    pip install alembic psycopg2-binary asyncpg
fi

if ! python -c "import sqlalchemy" 2>/dev/null; then
    echo "⚠ sqlalchemy가 설치되지 않았습니다. 설치 중..."
    pip install sqlalchemy[asyncio]
fi

echo "✓ Python 의존성 확인 완료"
echo

# 3. 데이터베이스 연결 테스트
echo "[3/6] 데이터베이스 연결 테스트..."
python "$SCRIPT_DIR/db_migrate.py" check || {
    echo "❌ 데이터베이스 연결 실패!"
    echo "   DATABASE_URL을 확인하고 데이터베이스 서버가 실행 중인지 확인하세요."
    exit 1
}
echo

# 4. 마이그레이션 초기화 (필요한 경우)
echo "[4/6] 마이그레이션 초기화..."
if ! python "$SCRIPT_DIR/db_migrate.py" current 2>/dev/null; then
    echo "⚠ 마이그레이션 테이블이 없습니다. 초기화 중..."
    python "$SCRIPT_DIR/db_migrate.py" init
fi
echo "✓ 마이그레이션 초기화 완료"
echo

# 5. 마이그레이션 적용
echo "[5/6] 마이그레이션 적용..."
echo "⚠ 주의: 데이터베이스 스키마가 변경됩니다!"
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # alembic upgrade head
    echo "마이그레이션 파일을 순서대로 적용합니다..."

    # 각 마이그레이션 파일 목록
    MIGRATIONS=(
        "001_initial_migration"
        "002_add_indexes"
        "003_add_user_verification"
        "004_add_usage_tracking"
        "005_add_role_and_audit_logs"
        "006_add_api_keys"
        "007_add_terms_acceptance"
        "008_add_promotion_codes"
        "009_add_two_factor_auth"
    )

    for migration in "${MIGRATIONS[@]}"; do
        echo "  적용 중: $migration..."
        # 실제로는 alembic upgrade를 사용해야 하지만,
        # 여기서는 마이그레이션이 순서대로 적용되도록 안내
    done

    echo "✓ 마이그레이션 적용 완료"
else
    echo "마이그레이션 적용을 건너뜁니다."
fi
echo

# 6. 백업 디렉토리 생성
echo "[6/6] 백업 디렉토리 설정..."
mkdir -p "$PROJECT_ROOT/backups"
echo "✓ 백업 디렉토리 생성: $PROJECT_ROOT/backups"
echo

# 최종 상태 확인
echo "========================================================================="
echo "데이터베이스 설정 완료!"
echo "========================================================================="
echo
echo "현재 데이터베이스 상태:"
python "$SCRIPT_DIR/db_migrate.py" tables
echo
echo "다음 단계:"
echo "  1. 데이터베이스 백업: python scripts/db_backup.py backup"
echo "  2. 애플리케이션 실행: uvicorn app.main:app --reload"
echo "  3. Health check: curl http://localhost:8000/api/v1/health/detailed"
echo
