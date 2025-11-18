#!/usr/bin/env python
"""
데이터베이스 백업/복구 스크립트

Usage:
    python scripts/db_backup.py backup                    # 전체 백업
    python scripts/db_backup.py backup --tables users     # 특정 테이블만 백업
    python scripts/db_backup.py restore backup.sql        # 복구
    python scripts/db_backup.py list                      # 백업 목록
"""
import sys
import os
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.logging import app_logger as logger


BACKUP_DIR = Path(__file__).parent.parent / "backups"
BACKUP_DIR.mkdir(exist_ok=True)


def parse_database_url(url: str):
    """DATABASE_URL 파싱"""
    # asyncpg:// 또는 postgresql+asyncpg:// 형식 처리
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("asyncpg://", "postgresql://")

    parsed = urlparse(url)
    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/"),
        "username": parsed.username,
        "password": parsed.password,
    }


def backup_database(output_file: str = None, tables: list = None):
    """PostgreSQL 데이터베이스 백업 (pg_dump 사용)"""
    try:
        db_config = parse_database_url(settings.DATABASE_URL)

        # 백업 파일명 생성
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = BACKUP_DIR / f"backup_{timestamp}.sql"
        else:
            output_file = Path(output_file)

        # pg_dump 명령어 구성
        cmd = [
            "pg_dump",
            "-h", db_config["host"],
            "-p", str(db_config["port"]),
            "-U", db_config["username"],
            "-d", db_config["database"],
            "-F", "c",  # Custom format (압축)
            "-f", str(output_file),
            "--verbose",
        ]

        # 특정 테이블만 백업
        if tables:
            for table in tables:
                cmd.extend(["-t", table])

        # 환경 변수에 비밀번호 설정
        env = os.environ.copy()
        if db_config["password"]:
            env["PGPASSWORD"] = db_config["password"]

        # 백업 실행
        logger.info(f"백업 시작: {output_file}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"✓ 백업 완료: {output_file} ({file_size:.2f} MB)")
            return str(output_file)
        else:
            logger.error(f"✗ 백업 실패: {result.stderr}")
            return None

    except Exception as e:
        logger.error(f"백업 중 오류: {e}")
        return None


def restore_database(backup_file: str):
    """PostgreSQL 데이터베이스 복구 (pg_restore 사용)"""
    try:
        db_config = parse_database_url(settings.DATABASE_URL)

        if not Path(backup_file).exists():
            logger.error(f"백업 파일이 존재하지 않습니다: {backup_file}")
            return False

        # 복구 전 확인
        response = input(f"⚠ 주의: 기존 데이터가 삭제될 수 있습니다. 계속하시겠습니까? (yes/no): ")
        if response.lower() != "yes":
            logger.info("복구 취소됨")
            return False

        # pg_restore 명령어 구성
        cmd = [
            "pg_restore",
            "-h", db_config["host"],
            "-p", str(db_config["port"]),
            "-U", db_config["username"],
            "-d", db_config["database"],
            "--clean",  # 복구 전 기존 객체 삭제
            "--if-exists",  # 객체 없어도 에러 안남
            "--verbose",
            str(backup_file),
        ]

        # 환경 변수에 비밀번호 설정
        env = os.environ.copy()
        if db_config["password"]:
            env["PGPASSWORD"] = db_config["password"]

        # 복구 실행
        logger.info(f"복구 시작: {backup_file}")
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info("✓ 복구 완료")
            return True
        else:
            logger.warning(f"복구 완료 (일부 경고 발생): {result.stderr}")
            return True

    except Exception as e:
        logger.error(f"복구 중 오류: {e}")
        return False


def list_backups():
    """백업 파일 목록"""
    backups = sorted(BACKUP_DIR.glob("backup_*.sql"), reverse=True)

    if not backups:
        logger.info("백업 파일이 없습니다.")
        return

    logger.info(f"\n백업 파일 목록 ({len(backups)}개):")
    logger.info("="*70)
    for backup in backups:
        size = backup.stat().st_size / (1024 * 1024)  # MB
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        logger.info(f"  {backup.name:40s} {size:10.2f} MB  {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70)


async def export_data_to_json():
    """데이터베이스 데이터를 JSON으로 내보내기"""
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine
        import json

        engine = create_async_engine(settings.DATABASE_URL)

        # 모든 테이블 조회
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = 'public'
                AND tablename != 'alembic_version'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = BACKUP_DIR / f"data_export_{timestamp}.json"

        all_data = {}

        # 각 테이블 데이터 추출
        for table in tables:
            async with engine.connect() as conn:
                result = await conn.execute(text(f'SELECT * FROM "{table}"'))
                rows = result.fetchall()
                columns = result.keys()

                # 딕셔너리 리스트로 변환
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # datetime 객체를 문자열로 변환
                        if hasattr(value, 'isoformat'):
                            value = value.isoformat()
                        row_dict[col] = value
                    table_data.append(row_dict)

                all_data[table] = table_data
                logger.info(f"  {table}: {len(table_data)} rows")

        await engine.dispose()

        # JSON 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False, default=str)

        file_size = output_file.stat().st_size / (1024 * 1024)
        logger.info(f"\n✓ JSON 내보내기 완료: {output_file} ({file_size:.2f} MB)")
        return str(output_file)

    except Exception as e:
        logger.error(f"JSON 내보내기 실패: {e}")
        return None


def print_usage():
    """사용법 출력"""
    print(__doc__)


async def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "backup":
        # 테이블 지정 확인
        tables = None
        if "--tables" in sys.argv:
            idx = sys.argv.index("--tables")
            tables = sys.argv[idx + 1:]

        backup_database(tables=tables)

    elif command == "restore":
        if len(sys.argv) < 3:
            logger.error("백업 파일 경로를 지정하세요")
            print_usage()
            return
        restore_database(sys.argv[2])

    elif command == "list":
        list_backups()

    elif command == "export-json":
        await export_data_to_json()

    else:
        logger.error(f"알 수 없는 명령어: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
