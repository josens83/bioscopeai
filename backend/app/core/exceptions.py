"""
커스텀 예외 클래스
"""
from typing import Any, Dict, Optional


class BioscopeAIException(Exception):
    """Base exception for BioscopeAI"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class UsageLimitExceeded(BioscopeAIException):
    """사용량 제한 초과"""

    def __init__(
        self,
        usage_type: str,
        current: int,
        limit: int,
        plan: str
    ):
        message = f"{usage_type} 월별 사용량 한도를 초과했습니다."
        details = {
            "usage_type": usage_type,
            "current": current,
            "limit": limit,
            "plan": plan,
            "upgrade_required": True
        }
        super().__init__(message=message, status_code=429, details=details)


class FeatureNotAvailable(BioscopeAIException):
    """기능 사용 불가 (플랜 제한)"""

    def __init__(self, feature: str, required_plan: str, current_plan: str):
        message = f"'{feature}' 기능은 {required_plan} 플랜 이상에서 사용 가능합니다."
        details = {
            "feature": feature,
            "required_plan": required_plan,
            "current_plan": current_plan,
            "upgrade_required": True
        }
        super().__init__(message=message, status_code=403, details=details)


class InvalidCredentials(BioscopeAIException):
    """잘못된 인증 정보"""

    def __init__(self, message: str = "이메일 또는 비밀번호가 올바르지 않습니다"):
        super().__init__(message=message, status_code=401)


class EmailNotVerified(BioscopeAIException):
    """이메일 미인증"""

    def __init__(self):
        message = "이메일 인증이 필요합니다. 이메일을 확인해주세요."
        details = {"action_required": "email_verification"}
        super().__init__(message=message, status_code=403, details=details)


class ResourceNotFound(BioscopeAIException):
    """리소스를 찾을 수 없음"""

    def __init__(self, resource_type: str, resource_id: Any):
        message = f"{resource_type}을(를) 찾을 수 없습니다."
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        super().__init__(message=message, status_code=404, details=details)


class DuplicateResource(BioscopeAIException):
    """중복 리소스"""

    def __init__(self, resource_type: str, field: str, value: Any):
        message = f"이미 존재하는 {resource_type}입니다."
        details = {
            "resource_type": resource_type,
            "field": field,
            "value": value
        }
        super().__init__(message=message, status_code=409, details=details)


class PaymentRequired(BioscopeAIException):
    """결제 필요"""

    def __init__(self, message: str = "이 기능을 사용하려면 유료 플랜이 필요합니다."):
        details = {"upgrade_required": True}
        super().__init__(message=message, status_code=402, details=details)


class ExternalServiceError(BioscopeAIException):
    """외부 서비스 오류"""

    def __init__(self, service: str, error_message: str):
        message = f"{service} 서비스에 일시적인 문제가 발생했습니다."
        details = {
            "service": service,
            "error": error_message
        }
        super().__init__(message=message, status_code=503, details=details)


class ValidationError(BioscopeAIException):
    """입력 검증 오류"""

    def __init__(self, field: str, message: str):
        details = {"field": field, "validation_error": message}
        super().__init__(message=message, status_code=422, details=details)


class RateLimitExceeded(BioscopeAIException):
    """Rate Limit 초과"""

    def __init__(self, retry_after: int):
        message = "요청 횟수 제한을 초과했습니다. 잠시 후 다시 시도해주세요."
        details = {"retry_after": retry_after}
        super().__init__(message=message, status_code=429, details=details)
