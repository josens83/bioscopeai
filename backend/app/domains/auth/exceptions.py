"""
Auth Domain Exceptions
"""
from fastapi import HTTPException, status


class AuthException(HTTPException):
    """인증 관련 기본 예외"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InvalidCredentialsException(AuthException):
    """잘못된 인증 정보"""
    def __init__(self):
        super().__init__(detail="이메일 또는 비밀번호가 올바르지 않습니다")


class UserNotFoundException(HTTPException):
    """사용자를 찾을 수 없음"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )


class EmailAlreadyExistsException(HTTPException):
    """이메일 중복"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )


class UsernameAlreadyExistsException(HTTPException):
    """사용자명 중복"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다"
        )


class InvalidTokenException(AuthException):
    """유효하지 않은 토큰"""
    def __init__(self):
        super().__init__(detail="유효하지 않은 토큰입니다")


class TokenExpiredException(AuthException):
    """만료된 토큰"""
    def __init__(self):
        super().__init__(detail="만료된 토큰입니다")


class EmailNotVerifiedException(HTTPException):
    """이메일 미인증"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이메일 인증이 필요합니다"
        )


class InactiveUserException(HTTPException):
    """비활성 사용자"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다"
        )
