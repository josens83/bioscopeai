"""
Email Service - 이메일 전송 인프라
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
from app.core.config import settings
from app.core.logging import app_logger as logger


class EmailService:
    """이메일 전송 서비스"""

    def __init__(self):
        """이메일 설정 초기화"""
        self.conf = ConnectionConfig(
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
        self.fm = FastMail(self.conf)

    async def send_email(
        self,
        email_to: List[EmailStr],
        subject: str,
        body: str,
        subtype: MessageType = MessageType.html
    ) -> bool:
        """이메일 전송"""
        try:
            message = MessageSchema(
                subject=subject,
                recipients=email_to,
                body=body,
                subtype=subtype,
            )

            await self.fm.send_message(message)
            logger.info(f"이메일 전송 성공: {email_to}")
            return True
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
            return False


# 싱글톤 인스턴스
email_service = EmailService()
