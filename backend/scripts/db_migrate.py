#!/usr/bin/env python
"""
데이터베이스 마이그레이션 관리 스크립트

Usage:
    python scripts/db_migrate.py upgrade        # 최신 버전으로 업그레이드
    python scripts/db_migrate.py downgrade -1   # 한 단계 다운그레이드
    python scripts/db_migrate.py current        # 현재 버전 확인
    python scripts/db_migrate.py history        # 마이그레이션 이력
    python scripts/db_migrate.py check          # 스키마 검증
"""
import sys
import os
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.logging import app_logger as logger


async def check_database_connection():
    """데이터베이스 연결 확인"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        logger.info("✓ 데이터베이스 연결 성공")
        return True
    except Exception as e:
        logger.error(f"✗ 데이터베이스 연결 실패: {e}")
        return False


async def check_migration_table():
    """alembic_version 테이블 존재 확인"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'alembic_version'
                )
            """))
            exists = result.scalar()
        await engine.dispose()

        if exists:
            logger.info("✓ 마이그레이션 테이블 존재")
        else:
            logger.warning("⚠ 마이그레이션 테이블 없음 - 초기화 필요")
        return exists
    except Exception as e:
        logger.error(f"✗ 마이그레이션 테이블 확인 실패: {e}")
        return False


async def get_current_version():
    """현재 마이그레이션 버전 확인"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
        await engine.dispose()

        if version:
            logger.info(f"현재 마이그레이션 버전: {version}")
        else:
            logger.warning("마이그레이션 버전 정보 없음")
        return version
    except Exception as e:
        logger.error(f"버전 확인 실패: {e}")
        return None


async def list_all_tables():
    """모든 테이블 목록 조회"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            # PostgreSQL 쿼리 (다른 DB는 수정 필요)
            result = await conn.execute(text("""
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = [row[0] for row in result.fetchall()]
        await engine.dispose()

        logger.info(f"\n현재 테이블 목록 ({len(tables)}개):")
        for table in tables:
            logger.info(f"  - {table}")
        return tables
    except Exception as e:
        logger.error(f"테이블 목록 조회 실패: {e}")
        return []


async def check_table_indexes():
    """테이블 인덱스 확인"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))
            indexes = result.fetchall()
        await engine.dispose()

        logger.info(f"\n인덱스 목록 ({len(indexes)}개):")
        current_table = None
        for table, index_name, index_def in indexes:
            if table != current_table:
                logger.info(f"\n[{table}]")
                current_table = table
            logger.info(f"  - {index_name}")

        return indexes
    except Exception as e:
        logger.error(f"인덱스 확인 실패: {e}")
        return []


async def check_foreign_keys():
    """외래 키 제약조건 확인"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    rc.delete_rule
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
                JOIN information_schema.referential_constraints AS rc
                  ON rc.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public'
                ORDER BY tc.table_name
            """))
            fks = result.fetchall()
        await engine.dispose()

        logger.info(f"\n외래 키 목록 ({len(fks)}개):")
        for table, column, ref_table, ref_column, delete_rule in fks:
            logger.info(f"  {table}.{column} -> {ref_table}.{ref_column} (ON DELETE {delete_rule})")

        return fks
    except Exception as e:
        logger.error(f"외래 키 확인 실패: {e}")
        return []


async def validate_schema():
    """스키마 전체 검증"""
    logger.info("\n" + "="*60)
    logger.info("데이터베이스 스키마 검증")
    logger.info("="*60)

    # 1. 연결 확인
    if not await check_database_connection():
        return False

    # 2. 마이그레이션 테이블 확인
    await check_migration_table()

    # 3. 현재 버전 확인
    await get_current_version()

    # 4. 테이블 목록
    tables = await list_all_tables()

    # 5. 인덱스 확인
    await check_table_indexes()

    # 6. 외래 키 확인
    await check_foreign_keys()

    logger.info("\n" + "="*60)
    logger.info("검증 완료")
    logger.info("="*60)

    return True


async def create_migration_table():
    """alembic_version 테이블 생성"""
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            """))
        await engine.dispose()
        logger.info("✓ alembic_version 테이블 생성 완료")
        return True
    except Exception as e:
        logger.error(f"✗ 테이블 생성 실패: {e}")
        return False


def print_usage():
    """사용법 출력"""
    print(__doc__)


async def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "check":
        await validate_schema()
    elif command == "current":
        await get_current_version()
    elif command == "tables":
        await list_all_tables()
    elif command == "indexes":
        await check_table_indexes()
    elif command == "fkeys":
        await check_foreign_keys()
    elif command == "init":
        await create_migration_table()
    else:
        print(f"알 수 없는 명령어: {command}")
        print_usage()


if __name__ == "__main__":
    asyncio.run(main())
