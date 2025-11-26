# ========================================
# Stage 1: Build - 프로덕션 빌드
# ========================================
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 파일 복사
COPY package*.json ./

# 의존성 설치 (개발 의존성 포함 - 빌드에 필요)
RUN npm ci

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정 (빌드 시점)
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# 프로덕션 빌드
RUN npm run build


# ========================================
# Stage 2: Production - Nginx 서빙
# ========================================
FROM nginx:alpine AS production

# Nginx 설정 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 빌드된 정적 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html

# 비루트 사용자로 실행 (보안 강화)
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup && \
    chown -R appuser:appgroup /var/cache/nginx && \
    chown -R appuser:appgroup /var/log/nginx && \
    chown -R appuser:appgroup /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R appuser:appgroup /var/run/nginx.pid

USER appuser

# 포트 노출
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
