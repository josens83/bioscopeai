"""
유효성 검증 유틸리티
"""
import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """이메일 형식 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    비밀번호 강도 검증

    요구사항:
    - 최소 8자
    - 최소 1개의 대문자
    - 최소 1개의 소문자
    - 최소 1개의 숫자
    - 최소 1개의 특수문자

    Returns:
        (유효 여부, 에러 메시지)
    """
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."

    if not re.search(r'[A-Z]', password):
        return False, "비밀번호에 최소 1개의 대문자가 포함되어야 합니다."

    if not re.search(r'[a-z]', password):
        return False, "비밀번호에 최소 1개의 소문자가 포함되어야 합니다."

    if not re.search(r'\d', password):
        return False, "비밀번호에 최소 1개의 숫자가 포함되어야 합니다."

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호에 최소 1개의 특수문자가 포함되어야 합니다."

    return True, None


def validate_url(url: str) -> bool:
    """URL 형식 검증"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_html(text: str) -> str:
    """HTML 태그 제거 (XSS 방지)"""
    # 간단한 HTML 태그 제거
    clean_text = re.sub(r'<[^>]+>', '', text)
    # 스크립트 태그 완전 제거
    clean_text = re.sub(r'<script[^>]*>.*?</script>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
    return clean_text


def validate_phone_number(phone: str) -> bool:
    """한국 전화번호 형식 검증"""
    # 010-1234-5678 또는 01012345678
    pattern = r'^(01[016789])[-\s]?(\d{3,4})[-\s]?(\d{4})$'
    return bool(re.match(pattern, phone))


def validate_korean_business_number(number: str) -> bool:
    """사업자등록번호 검증 (10자리)"""
    # 숫자만 추출
    digits = re.sub(r'\D', '', number)

    if len(digits) != 10:
        return False

    # 체크섬 검증
    checksum_weights = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    checksum = 0

    for i in range(9):
        checksum += int(digits[i]) * checksum_weights[i]

    checksum += (int(digits[8]) * 5) // 10
    checksum = (10 - (checksum % 10)) % 10

    return checksum == int(digits[9])


def is_safe_filename(filename: str) -> bool:
    """
    안전한 파일명인지 검증

    - 경로 탐색 문자 없음 (../, /)
    - NULL 바이트 없음
    - 제어 문자 없음
    """
    # 경로 탐색 방지
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # NULL 바이트 방지
    if '\x00' in filename:
        return False

    # 제어 문자 방지
    if any(ord(c) < 32 for c in filename):
        return False

    return True
