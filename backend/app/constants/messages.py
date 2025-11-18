"""
메시지 상수
"""

# 성공 메시지
SUCCESS_MESSAGES = {
    # 인증
    "AUTH_LOGIN_SUCCESS": "로그인에 성공했습니다.",
    "AUTH_LOGOUT_SUCCESS": "로그아웃되었습니다.",
    "AUTH_REGISTER_SUCCESS": "회원가입이 완료되었습니다. 이메일을 확인해주세요.",
    "AUTH_EMAIL_VERIFIED": "이메일 인증이 완료되었습니다.",
    "AUTH_PASSWORD_RESET_REQUESTED": "비밀번호 재설정 이메일을 발송했습니다.",
    "AUTH_PASSWORD_CHANGED": "비밀번호가 변경되었습니다.",

    # 사용자
    "USER_UPDATED": "사용자 정보가 업데이트되었습니다.",
    "USER_DELETED": "사용자가 삭제되었습니다.",

    # 구독
    "SUBSCRIPTION_CREATED": "구독이 생성되었습니다.",
    "SUBSCRIPTION_UPDATED": "구독이 업데이트되었습니다.",
    "SUBSCRIPTION_CANCELLED": "구독이 취소되었습니다.",

    # 논문
    "PAPER_UPLOADED": "논문이 업로드되었습니다.",
    "PAPER_DELETED": "논문이 삭제되었습니다.",

    # 분석
    "ANALYSIS_STARTED": "분석을 시작했습니다.",
    "ANALYSIS_COMPLETED": "분석이 완료되었습니다.",

    # API 키
    "API_KEY_CREATED": "API 키가 생성되었습니다.",
    "API_KEY_DELETED": "API 키가 삭제되었습니다.",

    # 2FA
    "2FA_ENABLED": "2단계 인증이 활성화되었습니다.",
    "2FA_DISABLED": "2단계 인증이 비활성화되었습니다.",

    # 프로모션
    "PROMOTION_APPLIED": "프로모션 코드가 적용되었습니다.",
    "PROMOTION_CREATED": "프로모션 코드가 생성되었습니다.",

    # 일반
    "OPERATION_SUCCESS": "작업이 성공적으로 완료되었습니다.",
}


# 에러 메시지
ERROR_MESSAGES = {
    # 인증
    "AUTH_INVALID_CREDENTIALS": "이메일 또는 비밀번호가 올바르지 않습니다.",
    "AUTH_EMAIL_NOT_VERIFIED": "이메일 인증이 필요합니다.",
    "AUTH_ACCOUNT_DISABLED": "비활성화된 계정입니다.",
    "AUTH_TOKEN_EXPIRED": "인증 토큰이 만료되었습니다.",
    "AUTH_TOKEN_INVALID": "유효하지 않은 인증 토큰입니다.",

    # 사용자
    "USER_NOT_FOUND": "사용자를 찾을 수 없습니다.",
    "USER_EMAIL_EXISTS": "이미 사용 중인 이메일입니다.",
    "USER_USERNAME_EXISTS": "이미 사용 중인 사용자명입니다.",

    # 구독
    "SUBSCRIPTION_NOT_FOUND": "구독 정보를 찾을 수 없습니다.",
    "SUBSCRIPTION_ALREADY_EXISTS": "이미 활성 구독이 있습니다.",
    "SUBSCRIPTION_PAYMENT_FAILED": "결제에 실패했습니다.",

    # 사용량
    "USAGE_LIMIT_EXCEEDED": "사용량 한도를 초과했습니다.",
    "FEATURE_NOT_AVAILABLE": "현재 플랜에서 사용할 수 없는 기능입니다.",

    # 논문
    "PAPER_NOT_FOUND": "논문을 찾을 수 없습니다.",
    "PAPER_UPLOAD_FAILED": "논문 업로드에 실패했습니다.",
    "PAPER_INVALID_FORMAT": "지원하지 않는 파일 형식입니다.",

    # 분석
    "ANALYSIS_NOT_FOUND": "분석 결과를 찾을 수 없습니다.",
    "ANALYSIS_FAILED": "분석에 실패했습니다.",

    # API 키
    "API_KEY_NOT_FOUND": "API 키를 찾을 수 없습니다.",
    "API_KEY_INVALID": "유효하지 않은 API 키입니다.",
    "API_KEY_EXPIRED": "만료된 API 키입니다.",

    # 프로모션
    "PROMOTION_NOT_FOUND": "프로모션 코드를 찾을 수 없습니다.",
    "PROMOTION_INVALID": "유효하지 않은 프로모션 코드입니다.",
    "PROMOTION_EXPIRED": "만료된 프로모션 코드입니다.",
    "PROMOTION_LIMIT_EXCEEDED": "프로모션 코드 사용 횟수를 초과했습니다.",

    # 일반
    "RESOURCE_NOT_FOUND": "리소스를 찾을 수 없습니다.",
    "PERMISSION_DENIED": "권한이 없습니다.",
    "VALIDATION_ERROR": "입력값 검증에 실패했습니다.",
    "INTERNAL_SERVER_ERROR": "서버 내부 오류가 발생했습니다.",
    "DATABASE_ERROR": "데이터베이스 오류가 발생했습니다.",
    "EXTERNAL_SERVICE_ERROR": "외부 서비스 연결에 실패했습니다.",
}
