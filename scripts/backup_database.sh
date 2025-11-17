#!/bin/bash
# =============================================================================
# BioscopeAI 데이터베이스 자동 백업 스크립트
# =============================================================================
# 사용법:
#   ./scripts/backup_database.sh
#
# Cron 설정 예시 (매일 새벽 3시):
#   0 3 * * * /path/to/bioscopeai/scripts/backup_database.sh >> /var/log/bioscopeai-backup.log 2>&1
# =============================================================================

set -e  # 오류 발생 시 즉시 종료

# =============================================================================
# 설정
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_ROOT/backups}"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=${KEEP_DAYS:-7}  # 백업 보관 기간 (일)
KEEP_WEEKS=${KEEP_WEEKS:-4}  # 주간 백업 보관 기간 (주)
KEEP_MONTHS=${KEEP_MONTHS:-6}  # 월간 백업 보관 기간 (월)

# Docker Compose 파일 경로
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_ROOT/docker-compose.prod.yml}"

# S3 백업 설정 (선택사항)
S3_BUCKET="${S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# =============================================================================
# 색상 출력
# =============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# =============================================================================
# 백업 디렉토리 생성
# =============================================================================
create_backup_dirs() {
    log_info "백업 디렉토리 생성 중..."
    mkdir -p "$BACKUP_DIR/daily"
    mkdir -p "$BACKUP_DIR/weekly"
    mkdir -p "$BACKUP_DIR/monthly"
    log_info "백업 디렉토리 생성 완료: $BACKUP_DIR"
}

# =============================================================================
# 데이터베이스 백업
# =============================================================================
backup_database() {
    local backup_type=$1  # daily, weekly, monthly
    local backup_file="$BACKUP_DIR/$backup_type/bioscopeai_${backup_type}_${DATE}.sql.gz"

    log_info "데이터베이스 백업 시작 ($backup_type)..."

    # Docker Compose를 사용한 pg_dump
    if [ -f "$COMPOSE_FILE" ]; then
        log_info "Docker Compose를 사용하여 백업 중..."

        if docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres -d bioscopeai | gzip > "$backup_file"; then
            local file_size=$(du -h "$backup_file" | cut -f1)
            log_info "백업 완료: $backup_file (크기: $file_size)"
            return 0
        else
            log_error "백업 실패"
            return 1
        fi
    else
        log_error "Docker Compose 파일을 찾을 수 없습니다: $COMPOSE_FILE"
        return 1
    fi
}

# =============================================================================
# S3 업로드 (선택사항)
# =============================================================================
upload_to_s3() {
    local backup_file=$1
    local backup_type=$2

    if [ -z "$S3_BUCKET" ]; then
        log_warn "S3_BUCKET이 설정되지 않았습니다. S3 업로드를 건너뜁니다."
        return 0
    fi

    log_info "S3에 백업 업로드 중..."

    if command -v aws &> /dev/null; then
        local s3_path="s3://$S3_BUCKET/bioscopeai-backups/$backup_type/$(basename $backup_file)"

        if aws s3 cp "$backup_file" "$s3_path" --region "$AWS_REGION"; then
            log_info "S3 업로드 완료: $s3_path"
            return 0
        else
            log_error "S3 업로드 실패"
            return 1
        fi
    else
        log_warn "AWS CLI가 설치되지 않았습니다. S3 업로드를 건너뜁니다."
        return 0
    fi
}

# =============================================================================
# 오래된 백업 정리
# =============================================================================
cleanup_old_backups() {
    log_info "오래된 백업 파일 정리 중..."

    # Daily 백업: KEEP_DAYS일 이상 된 파일 삭제
    if [ -d "$BACKUP_DIR/daily" ]; then
        log_info "일일 백업 정리 (${KEEP_DAYS}일 이상 된 파일)..."
        find "$BACKUP_DIR/daily" -name "*.sql.gz" -type f -mtime +$KEEP_DAYS -delete
        local daily_count=$(find "$BACKUP_DIR/daily" -name "*.sql.gz" -type f | wc -l)
        log_info "남은 일일 백업 파일: $daily_count개"
    fi

    # Weekly 백업: KEEP_WEEKS주 이상 된 파일 삭제
    if [ -d "$BACKUP_DIR/weekly" ]; then
        local weeks_in_days=$((KEEP_WEEKS * 7))
        log_info "주간 백업 정리 (${KEEP_WEEKS}주 이상 된 파일)..."
        find "$BACKUP_DIR/weekly" -name "*.sql.gz" -type f -mtime +$weeks_in_days -delete
        local weekly_count=$(find "$BACKUP_DIR/weekly" -name "*.sql.gz" -type f | wc -l)
        log_info "남은 주간 백업 파일: $weekly_count개"
    fi

    # Monthly 백업: KEEP_MONTHS개월 이상 된 파일 삭제
    if [ -d "$BACKUP_DIR/monthly" ]; then
        local months_in_days=$((KEEP_MONTHS * 30))
        log_info "월간 백업 정리 (${KEEP_MONTHS}개월 이상 된 파일)..."
        find "$BACKUP_DIR/monthly" -name "*.sql.gz" -type f -mtime +$months_in_days -delete
        local monthly_count=$(find "$BACKUP_DIR/monthly" -name "*.sql.gz" -type f | wc -l)
        log_info "남은 월간 백업 파일: $monthly_count개"
    fi
}

# =============================================================================
# 백업 검증
# =============================================================================
verify_backup() {
    local backup_file=$1

    log_info "백업 파일 검증 중..."

    # 파일 존재 확인
    if [ ! -f "$backup_file" ]; then
        log_error "백업 파일이 존재하지 않습니다: $backup_file"
        return 1
    fi

    # 파일 크기 확인 (최소 1KB)
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    if [ "$file_size" -lt 1024 ]; then
        log_error "백업 파일 크기가 너무 작습니다: $file_size bytes"
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
# 백업 알림 (선택사항)
# =============================================================================
send_notification() {
    local status=$1
    local message=$2

    # Slack 웹훅 (선택사항)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local emoji=":white_check_mark:"
        local color="good"

        if [ "$status" != "success" ]; then
            emoji=":x:"
            color="danger"
        fi

        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"$emoji BioscopeAI Backup\", \"attachments\": [{\"color\": \"$color\", \"text\": \"$message\"}]}" \
            > /dev/null 2>&1
    fi
}

# =============================================================================
# 메인 함수
# =============================================================================
main() {
    log_info "=========================================="
    log_info "BioscopeAI 데이터베이스 백업 시작"
    log_info "=========================================="
    log_info "백업 시간: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "백업 디렉토리: $BACKUP_DIR"

    # 백업 디렉토리 생성
    create_backup_dirs

    # 백업 타입 결정
    local day_of_week=$(date +%u)  # 1-7 (월요일=1, 일요일=7)
    local day_of_month=$(date +%d)
    local backup_type="daily"

    if [ "$day_of_month" = "01" ]; then
        backup_type="monthly"
        log_info "월간 백업 수행"
    elif [ "$day_of_week" = "7" ]; then
        backup_type="weekly"
        log_info "주간 백업 수행"
    else
        log_info "일일 백업 수행"
    fi

    # 데이터베이스 백업
    if backup_database "$backup_type"; then
        local backup_file="$BACKUP_DIR/$backup_type/bioscopeai_${backup_type}_${DATE}.sql.gz"

        # 백업 검증
        if verify_backup "$backup_file"; then
            # S3 업로드 (설정된 경우)
            upload_to_s3 "$backup_file" "$backup_type"

            # 오래된 백업 정리
            cleanup_old_backups

            log_info "=========================================="
            log_info "백업 완료!"
            log_info "=========================================="

            send_notification "success" "백업 완료: $backup_file"
            exit 0
        else
            log_error "백업 검증 실패"
            send_notification "error" "백업 검증 실패"
            exit 1
        fi
    else
        log_error "백업 실패"
        send_notification "error" "백업 실패"
        exit 1
    fi
}

# 스크립트 실행
main "$@"
