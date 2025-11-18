"""
구독 관련 상수 및 Enum
"""
from enum import Enum
from typing import Dict


class SubscriptionTier(str, Enum):
    """구독 플랜 티어"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """구독 상태"""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"
    PAUSED = "paused"


# 플랜별 제한
TIER_LIMITS: Dict[SubscriptionTier, Dict[str, int]] = {
    SubscriptionTier.FREE: {
        "max_papers": 3,
        "max_analyses_per_month": 10,
        "max_comparison_papers": 2,
        "api_calls_per_month": 100,
    },
    SubscriptionTier.BASIC: {
        "max_papers": 20,
        "max_analyses_per_month": 100,
        "max_comparison_papers": 5,
        "api_calls_per_month": 1000,
    },
    SubscriptionTier.PREMIUM: {
        "max_papers": 100,
        "max_analyses_per_month": 1000,
        "max_comparison_papers": 10,
        "api_calls_per_month": 10000,
    },
    SubscriptionTier.ENTERPRISE: {
        "max_papers": -1,  # 무제한
        "max_analyses_per_month": -1,
        "max_comparison_papers": -1,
        "api_calls_per_month": -1,
    },
}


# 플랜별 가격 (USD)
TIER_PRICES: Dict[SubscriptionTier, float] = {
    SubscriptionTier.FREE: 0.0,
    SubscriptionTier.BASIC: 9.99,
    SubscriptionTier.PREMIUM: 29.99,
    SubscriptionTier.ENTERPRISE: 99.99,
}


# 플랜별 기능
TIER_FEATURES: Dict[SubscriptionTier, list] = {
    SubscriptionTier.FREE: [
        "기본 논문 분석",
        "제한된 논문 저장",
        "기본 비교 분석"
    ],
    SubscriptionTier.BASIC: [
        "고급 논문 분석",
        "더 많은 논문 저장",
        "향상된 비교 분석",
        "이메일 지원"
    ],
    SubscriptionTier.PREMIUM: [
        "무제한 논문 분석",
        "대량 논문 저장",
        "고급 비교 분석",
        "우선 지원",
        "API 액세스"
    ],
    SubscriptionTier.ENTERPRISE: [
        "모든 Premium 기능",
        "무제한 사용",
        "전담 지원",
        "커스텀 통합",
        "SLA 보장"
    ],
}
