"""
날짜/시간 유틸리티
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


def get_current_utc() -> datetime:
    """현재 UTC 시간 반환"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """datetime을 문자열로 포맷"""
    return dt.strftime(fmt)


def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """문자열을 datetime으로 파싱"""
    return datetime.strptime(dt_str, fmt)


def add_days(dt: datetime, days: int) -> datetime:
    """날짜에 일수 추가"""
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """날짜에 시간 추가"""
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """날짜에 분 추가"""
    return dt + timedelta(minutes=minutes)


def is_expired(dt: Optional[datetime]) -> bool:
    """날짜가 만료되었는지 확인"""
    if not dt:
        return True
    return datetime.utcnow() > dt.replace(tzinfo=None)


def time_until(dt: datetime) -> timedelta:
    """주어진 날짜까지 남은 시간"""
    now = datetime.utcnow().replace(tzinfo=None)
    target = dt.replace(tzinfo=None)
    return target - now


def human_readable_time_diff(dt: datetime) -> str:
    """
    사람이 읽기 쉬운 시간 차이 표현

    Examples:
        "방금 전"
        "5분 전"
        "2시간 전"
        "3일 전"
    """
    now = datetime.utcnow().replace(tzinfo=None)
    target = dt.replace(tzinfo=None)
    diff = now - target

    seconds = diff.total_seconds()

    if seconds < 60:
        return "방금 전"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}분 전"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}시간 전"
    elif seconds < 2592000:  # 30 days
        days = int(seconds / 86400)
        return f"{days}일 전"
    else:
        months = int(seconds / 2592000)
        return f"{months}개월 전"
