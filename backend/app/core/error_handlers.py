"""
전역 에러 핸들러
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from app.core.exceptions import BioscopeAIException
from app.core.logging import app_logger as logger
import traceback


async def bioscopeai_exception_handler(request: Request, exc: BioscopeAIException) -> JSONResponse:
    """BioscopeAI 커스텀 예외 핸들러"""
    logger.warning(
        f"BioscopeAI Exception: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.__class__.__name__,
                "details": exc.details
            }
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """HTTP 예외 핸들러"""
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": "HTTPException"
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """입력 검증 예외 핸들러"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"Validation Error: {len(errors)} errors",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "입력값 검증에 실패했습니다.",
                "code": "ValidationError",
                "details": {"validation_errors": errors}
            }
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """데이터베이스 무결성 오류 핸들러"""
    logger.error(
        f"Database Integrity Error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    # 중복 키 오류 감지
    error_msg = str(exc.orig)
    if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": {
                    "message": "이미 존재하는 데이터입니다.",
                    "code": "DuplicateError"
                }
            }
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "message": "데이터베이스 오류가 발생했습니다.",
                "code": "DatabaseError"
            }
        }
    )


async def operational_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    """데이터베이스 연결 오류 핸들러"""
    logger.error(
        f"Database Operational Error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": {
                "message": "데이터베이스 연결에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "code": "DatabaseConnectionError"
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """일반 예외 핸들러 (모든 미처리 예외)"""
    logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )

    # 프로덕션 환경에서는 상세 오류를 노출하지 않음
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "code": "InternalServerError"
            }
        }
    )


def register_exception_handlers(app):
    """모든 예외 핸들러 등록"""
    app.add_exception_handler(BioscopeAIException, bioscopeai_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(OperationalError, operational_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
