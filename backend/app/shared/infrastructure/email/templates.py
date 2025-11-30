"""
Email Templates - 이메일 템플릿
"""
from app.core.config import settings
from .service import email_service


async def send_password_reset_email(email: str, token: str) -> bool:
    """비밀번호 재설정 이메일 전송"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">🔐 비밀번호 재설정</h2>
            <p>안녕하세요,</p>
            <p>BioscopeAI 계정의 비밀번호 재설정을 요청하셨습니다.</p>
            <p>아래 버튼을 클릭하여 비밀번호를 재설정하세요:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}"
                   style="background-color: #4CAF50; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    비밀번호 재설정
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">
                또는 다음 링크를 복사하여 브라우저에 붙여넣으세요:<br>
                <a href="{reset_url}">{reset_url}</a>
            </p>
            <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                이 링크는 1시간 동안 유효합니다.<br>
                요청하지 않으신 경우 이 이메일을 무시하세요.
            </p>
        </body>
    </html>
    """

    return await email_service.send_email(
        email_to=[email],
        subject="BioscopeAI - 비밀번호 재설정",
        body=body,
    )


async def send_verification_email(email: str, token: str) -> bool:
    """이메일 인증 메일 전송"""
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">✉️ 이메일 인증</h2>
            <p>안녕하세요,</p>
            <p>BioscopeAI에 가입해 주셔서 감사합니다!</p>
            <p>아래 버튼을 클릭하여 이메일 주소를 인증해주세요:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verify_url}"
                   style="background-color: #2196F3; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    이메일 인증하기
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">
                또는 다음 링크를 복사하여 브라우저에 붙여넣으세요:<br>
                <a href="{verify_url}">{verify_url}</a>
            </p>
            <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">
                이메일을 인증하지 않으면 일부 기능이 제한될 수 있습니다.
            </p>
        </body>
    </html>
    """

    return await email_service.send_email(
        email_to=[email],
        subject="BioscopeAI - 이메일 인증",
        body=body,
    )


async def send_welcome_email(email: str, username: str) -> bool:
    """환영 이메일 전송"""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">🎉 환영합니다, {username}님!</h2>
            <p>BioscopeAI에 가입해 주셔서 감사합니다.</p>
            <h3 style="color: #555;">주요 기능:</h3>
            <ul style="line-height: 1.8;">
                <li>📄 PubMed 논문 검색 및 저장</li>
                <li>🤖 AI 기반 논문 분석 (Q&A, 요약)</li>
                <li>📊 여러 논문 비교 분석</li>
                <li>💎 프리미엄 플랜으로 더 많은 기능 이용</li>
            </ul>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}"
                   style="background-color: #FF9800; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    시작하기
                </a>
            </div>
            <p style="color: #666; font-size: 14px;">
                문의사항이 있으시면 언제든지 support@bioscopeai.com으로 연락주세요.
            </p>
        </body>
    </html>
    """

    return await email_service.send_email(
        email_to=[email],
        subject="BioscopeAI에 오신 것을 환영합니다! 🎉",
        body=body,
    )


async def send_payment_receipt_email(
    email: str,
    username: str,
    plan_name: str,
    amount: float,
    currency: str,
    transaction_id: str
) -> bool:
    """결제 영수증 이메일 전송"""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">🧾 결제 영수증</h2>
            <p>안녕하세요, {username}님!</p>
            <p>BioscopeAI 플랜 결제가 성공적으로 완료되었습니다.</p>

            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #555;">결제 상세</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;"><strong>플랜</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd; text-align: right;">{plan_name.upper()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;"><strong>금액</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd; text-align: right;">{currency.upper()} {amount:.2f}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd;"><strong>거래 ID</strong></td>
                        <td style="padding: 8px 0; border-bottom: 1px solid #ddd; text-align: right; font-family: monospace; font-size: 12px;">{transaction_id}</td>
                    </tr>
                </table>
            </div>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/dashboard"
                   style="background-color: #4CAF50; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    대시보드로 이동
                </a>
            </div>

            <p style="color: #666; font-size: 14px;">
                문의사항이 있으시면 support@bioscopeai.com으로 연락주세요.
            </p>
        </body>
    </html>
    """

    return await email_service.send_email(
        email_to=[email],
        subject=f"BioscopeAI - {plan_name.upper()} 플랜 결제 영수증",
        body=body,
    )


async def send_payment_failed_email(email: str, username: str, reason: str) -> bool:
    """결제 실패 알림 이메일 전송"""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #d32f2f;">❌ 결제 실패</h2>
            <p>안녕하세요, {username}님</p>
            <p>BioscopeAI 플랜 결제가 실패했습니다.</p>

            <div style="background-color: #ffebee; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #d32f2f;">
                <strong>실패 사유:</strong><br>
                {reason}
            </div>

            <p>다음 사항을 확인해주세요:</p>
            <ul style="line-height: 1.8;">
                <li>카드 정보가 올바른지 확인</li>
                <li>카드 잔액이 충분한지 확인</li>
                <li>카드 유효기간이 만료되지 않았는지 확인</li>
            </ul>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/subscriptions"
                   style="background-color: #2196F3; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    다시 시도하기
                </a>
            </div>
        </body>
    </html>
    """

    return await email_service.send_email(
        email_to=[email],
        subject="BioscopeAI - 결제 실패",
        body=body,
    )


async def send_subscription_cancelled_email(email: str, username: str, plan_name: str) -> bool:
    """구독 취소 알림 이메일 전송"""
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">👋 구독 취소 확인</h2>
            <p>안녕하세요, {username}님</p>
            <p>BioscopeAI {plan_name.upper()} 플랜 구독이 취소되었습니다.</p>

            <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                현재 결제 기간이 끝날 때까지는 계속 사용하실 수 있습니다.
            </div>

            <p>다시 돌아오시면 언제든지 환영합니다!</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/subscriptions"
                   style="background-color: #4CAF50; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    구독 재개하기
                </a>
            </div>
        </body>
    </html>
    """

    return await email_service.send_email(
        email_to=[email],
        subject="BioscopeAI - 구독 취소 확인",
        body=body,
    )
