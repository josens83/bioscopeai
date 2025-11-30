"""
상태 관련 Enum
"""
from enum import Enum


class UserRole(str, Enum):
    """사용자 역할"""
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class ResourceStatus(str, Enum):
    """리소스 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AnalysisStatus(str, Enum):
    """분석 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """결제 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class EmailVerificationStatus(str, Enum):
    """이메일 인증 상태"""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    EXPIRED = "expired"
