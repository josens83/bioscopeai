#!/bin/bash
# =============================================================================
# BioscopeAI 데이터베이스 복원 스크립트
# =============================================================================
# 사용법:
#   ./scripts/restore_database.sh <backup_file>
#
# 예시:
#   ./scripts/restore_database.sh backups/daily/bioscopeai_daily_20250117_030000.sql.gz
#   ./scripts/restore_database.sh s3://mybucket/bioscopeai-backups/daily/backup.sql.gz
# =============================================================================

set -e  # 오류 발생 시 즉시 종료

# =============================================================================
# 색상 출력
# =============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# =============================================================================
# 설정
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_ROOT/docker-compose.prod.yml}"
TEMP_DIR="/tmp/bioscopeai-restore-$$"

# =============================================================================
# 사용법 출력
# =============================================================================
usage() {
    cat <<EOF
사용법: $0 <backup_file>

백업 파일 복원

옵션:
  <backup_file>    복원할 백업 파일 경로 (.sql.gz 파일)
                   로컬 파일 또는 S3 경로 (s3://...)

예시:
  $0 backups/daily/bioscopeai_daily_20250117_030000.sql.gz
  $0 s3://mybucket/bioscopeai-backups/daily/backup.sql.gz

환경변수:
  COMPOSE_FILE     Docker Compose 파일 경로 (기본값: docker-compose.prod.yml)
  AWS_REGION       AWS 리전 (S3 사용 시, 기본값: us-east-1)

EOF
    exit 1
}

# =============================================================================
# 인자 확인
# =============================================================================
if [ $# -eq 0 ]; then
    log_error "백업 파일 경로가 필요합니다"
    usage
fi

BACKUP_FILE="$1"

# =============================================================================
# S3에서 다운로드 (필요한 경우)
# =============================================================================
download_from_s3() {
    local s3_path=$1
    local local_path=$2

    log_info "S3에서 백업 다운로드 중..."

    if command -v aws &> /dev/null; then
        if aws s3 cp "$s3_path" "$local_path" --region "${AWS_REGION:-us-east-1}"; then
            log_info "S3 다운로드 완료"
            return 0
        else
            log_error "S3 다운로드 실패"
            return 1
        fi
    else
        log_error "AWS CLI가 설치되지 않았습니다"
        return 1
    fi
}

# =============================================================================
# 백업 파일 준비
# =============================================================================
prepare_backup_file() {
    mkdir -p "$TEMP_DIR"

    # S3 경로인 경우
    if [[ "$BACKUP_FILE" == s3://* ]]; then
        local local_file="$TEMP_DIR/backup.sql.gz"
        if download_from_s3 "$BACKUP_FILE" "$local_file"; then
            echo "$local_file"
            return 0
        else
            return 1
        fi
    # 로컬 파일인 경우
    elif [ -f "$BACKUP_FILE" ]; then
        echo "$BACKUP_FILE"
        return 0
    else
        log_error "백업 파일을 찾을 수 없습니다: $BACKUP_FILE"
        return 1
    fi
}

# =============================================================================
# 백업 파일 검증
# =============================================================================
verify_backup_file() {
    local backup_file=$1

    log_info "백업 파일 검증 중..."

    # 파일 존재 확인
    if [ ! -f "$backup_file" ]; then
        log_error "백업 파일이 존재하지 않습니다: $backup_file"
        return 1
    fi

    # gzip 파일 무결성 확인
    if gzip -t "$backup_file" 2>/dev/null; then
        log_info "백업 파일 검증 성공"
        return 0
    else
        log_error "백업 파일이 손상되었습니다"
        return 1
    fi
}

# =============================================================================
# 사용자 확인
# =============================================================================
confirm_restore() {
    log_warn "=============================================="
    log_warn "경고: 데이터베이스 복원 작업"
    log_warn "=============================================="
    log_warn "이 작업은 현재 데이터베이스의 모든 데이터를 삭제하고"
    log_warn "백업 파일로 덮어씁니다."
    log_warn ""
    log_warn "백업 파일: $BACKUP_FILE"
    log_warn ""

    read -p "정말로 복원하시겠습니까? (yes/no): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log_info "복원 작업이 취소되었습니다"
        exit 0
    fi
}

# =============================================================================
# 데이터베이스 복원
# =============================================================================
restore_database() {
    local backup_file=$1

    log_info "데이터베이스 복원 시작..."

    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose 파일을 찾을 수 없습니다: $COMPOSE_FILE"
        return 1
    fi

    # 데이터베이스 연결 종료
    log_step "1/4: 기존 데이터베이스 연결 종료 중..."
    docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d postgres -c \
        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'bioscopeai' AND pid <> pg_backend_pid();" \
        > /dev/null 2>&1 || true

    # 데이터베이스 삭제 및 재생성
    log_step "2/4: 데이터베이스 재생성 중..."
    docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d postgres <<EOF
DROP DATABASE IF EXISTS bioscopeai;
CREATE DATABASE bioscopeai;
\q
EOF

    # 백업 복원
    log_step "3/4: 백업 데이터 복원 중..."
    if gunzip -c "$backup_file" | docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d bioscopeai > /dev/null; then
        log_info "백업 복원 완료"
    else
        log_error "백업 복원 실패"
        return 1
    fi

    # 권한 확인
    log_step "4/4: 데이터베이스 권한 확인 중..."
    docker-compose -f "$COMPOSE_FILE" exec -T db psql -U postgres -d bioscopeai -c \
        "GRANT ALL PRIVILEGES ON DATABASE bioscopeai TO postgres;" \
        > /dev/null 2>&1 || true

    log_info "데이터베이스 복원 완료!"
    return 0
}

# =============================================================================
# 정리
# =============================================================================
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        log_info "임시 파일 정리 중..."
        rm -rf "$TEMP_DIR"
    fi
}

trap cleanup EXIT

# =============================================================================
# 메인 함수
# =============================================================================
main() {
    log_info "=========================================="
    log_info "BioscopeAI 데이터베이스 복원"
    log_info "=========================================="
    log_info "복원 시간: $(date '+%Y-%m-%d %H:%M:%S')"

    # 사용자 확인
    confirm_restore

    # 백업 파일 준비
    log_info "백업 파일 준비 중..."
    local backup_file
    if backup_file=$(prepare_backup_file); then
        log_info "백업 파일: $backup_file"
    else
        log_error "백업 파일 준비 실패"
        exit 1
    fi

    # 백업 파일 검증
    if ! verify_backup_file "$backup_file"; then
        log_error "백업 파일 검증 실패"
        exit 1
    fi

    # 데이터베이스 복원
    if restore_database "$backup_file"; then
        log_info "=========================================="
        log_info "복원 완료!"
        log_info "=========================================="
        log_info "애플리케이션을 재시작하여 변경사항을 적용하세요:"
        log_info "  docker-compose -f $COMPOSE_FILE restart backend"
        exit 0
    else
        log_error "복원 실패"
        exit 1
    fi
}

# 스크립트 실행
main "$@"
