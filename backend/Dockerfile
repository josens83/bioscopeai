# ========================================
# Stage 1: Builder - 의존성 빌드 및 설치
# ========================================
FROM python:3.11-slim as builder

WORKDIR /app

# 시스템 의존성 설치 (빌드 도구)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ========================================
# Stage 2: Runtime - 실행 환경
# ========================================
FROM python:3.11-slim

WORKDIR /app

# 런타임 의존성만 설치 (빌드 도구 제외)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 빌더 스테이지에서 설치한 Python 패키지 복사
COPY --from=builder /root/.local /root/.local

# Python PATH 설정
ENV PATH=/root/.local/bin:$PATH

# 비루트 사용자 생성 (보안 강화)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads /app/logs && \
    chown -R appuser:appuser /app

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 비루트 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
