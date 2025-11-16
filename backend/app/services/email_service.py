"""
이메일 서비스
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
from app.core.config import settings
from app.core.logging import app_logger as logger
from pathlib import Path


# 이메일 설정
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER if hasattr(settings, 'SMTP_USER') else "",
    MAIL_PASSWORD=settings.SMTP_PASSWORD if hasattr(settings, 'SMTP_PASSWORD') else "",
    MAIL_FROM=settings.SMTP_FROM if hasattr(settings, 'SMTP_FROM') else "noreply@bioscopeai.com",
    MAIL_PORT=settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587,
    MAIL_SERVER=settings.SMTP_HOST if hasattr(settings, 'SMTP_HOST') else "smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fm = FastMail(conf)


async def send_email(
    email_to: List[EmailStr],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html
):
    """이메일 전송"""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=email_to,
            body=body,
            subtype=subtype,
        )

        await fm.send_message(message)
        logger.info(f"이메일 전송 성공: {email_to}")
        return True
    except Exception as e:
        logger.error(f"이메일 전송 실패: {e}")
        return False


async def send_password_reset_email(email: str, token: str):
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

    return await send_email(
        email_to=[email],
        subject="BioscopeAI - 비밀번호 재설정",
        body=body,
    )


async def send_verification_email(email: str, token: str):
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

    return await send_email(
        email_to=[email],
        subject="BioscopeAI - 이메일 인증",
        body=body,
    )


async def send_welcome_email(email: str, username: str):
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

    return await send_email(
        email_to=[email],
        subject="BioscopeAI에 오신 것을 환영합니다! 🎉",
        body=body,
    )
