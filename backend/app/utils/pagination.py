"""
페이지네이션 유틸리티
"""
from typing import TypeVar, List, Dict, Any
from math import ceil

T = TypeVar('T')


def calculate_pagination(
    total: int,
    page: int,
    size: int
) -> Dict[str, Any]:
    """
    페이지네이션 메타데이터 계산

    Args:
        total: 전체 아이템 수
        page: 현재 페이지 (1부터 시작)
        size: 페이지당 아이템 수

    Returns:
        {
            "total": 전체 아이템 수,
            "page": 현재 페이지,
            "size": 페이지당 아이템 수,
            "pages": 전체 페이지 수,
            "has_prev": 이전 페이지 존재 여부,
            "has_next": 다음 페이지 존재 여부,
            "prev_page": 이전 페이지 번호,
            "next_page": 다음 페이지 번호
        }
    """
    pages = ceil(total / size) if size > 0 else 0
    has_prev = page > 1
    has_next = page < pages

    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else None,
        "next_page": page + 1 if has_next else None,
    }


def get_pagination_metadata(
    items: List[T],
    total: int,
    page: int,
    size: int
) -> Dict[str, Any]:
    """
    페이지네이션된 응답에 메타데이터 추가

    Returns:
        {
            "items": [...],
            "pagination": {...}
        }
    """
    pagination = calculate_pagination(total, page, size)

    return {
        "items": items,
        "pagination": pagination
    }


def get_offset_limit(page: int, size: int) -> tuple[int, int]:
    """
    페이지 번호를 SQL OFFSET/LIMIT으로 변환

    Args:
        page: 페이지 번호 (1부터 시작)
        size: 페이지당 아이템 수

    Returns:
        (offset, limit)

    Examples:
        get_offset_limit(1, 20) -> (0, 20)
        get_offset_limit(2, 20) -> (20, 20)
        get_offset_limit(3, 20) -> (40, 20)
    """
    offset = (page - 1) * size
    limit = size
    return offset, limit
