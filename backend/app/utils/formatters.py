"""
포맷팅 유틸리티
"""
from typing import Optional


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    통화 포맷

    Examples:
        format_currency(1234.56) -> "$1,234.56"
        format_currency(1234.56, "KRW") -> "₩1,235"
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "KRW":
        return f"₩{int(amount):,}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 사람이 읽기 쉬운 형식으로 변환

    Examples:
        format_file_size(1024) -> "1.0 KB"
        format_file_size(1048576) -> "1.0 MB"
        format_file_size(1073741824) -> "1.0 GB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    텍스트를 지정된 길이로 자르기

    Examples:
        truncate_text("This is a long text", 10) -> "This is a..."
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    퍼센트 포맷

    Examples:
        format_percentage(0.1234) -> "12.34%"
        format_percentage(0.5, 1) -> "50.0%"
    """
    return f"{value * 100:.{decimals}f}%"


def format_number(number: int) -> str:
    """
    숫자를 천 단위 구분자로 포맷

    Examples:
        format_number(1234567) -> "1,234,567"
    """
    return f"{number:,}"


def slugify(text: str) -> str:
    """
    텍스트를 URL-safe slug로 변환

    Examples:
        slugify("Hello World!") -> "hello-world"
        slugify("한글 테스트") -> "한글-테스트"
    """
    import re
    # 소문자 변환
    text = text.lower()
    # 특수문자를 하이픈으로 변환
    text = re.sub(r'[^\w\s-]', '', text)
    # 공백을 하이픈으로 변환
    text = re.sub(r'[\s_]+', '-', text)
    # 연속된 하이픈 제거
    text = re.sub(r'-+', '-', text)
    # 앞뒤 하이픈 제거
    return text.strip('-')


def mask_email(email: str) -> str:
    """
    이메일 마스킹 (개인정보 보호)

    Examples:
        mask_email("user@example.com") -> "us**@example.com"
    """
    if '@' not in email:
        return email

    local, domain = email.split('@', 1)

    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0:2] + '*' * (len(local) - 2)

    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    전화번호 마스킹

    Examples:
        mask_phone("010-1234-5678") -> "010-****-5678"
    """
    import re
    # 숫자만 추출
    digits = re.sub(r'\D', '', phone)

    if len(digits) == 11:  # 휴대폰
        return f"{digits[0:3]}-****-{digits[7:]}"
    elif len(digits) == 10:  # 일반 전화
        return f"{digits[0:3]}-***-{digits[6:]}"
    else:
        return phone
